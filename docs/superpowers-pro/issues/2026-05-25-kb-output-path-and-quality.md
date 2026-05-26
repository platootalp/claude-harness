# Issue: kb 插件输出目录错误且文档质量低

## 根因

### Bug 1: 输出目录落在目标项目根目录而非插件 data 目录

**根因描述：** 所有 extract-* skill 和 ingest skill 中的路径（如 `data/raw/<project>/_map.md`、`data/wiki/<project>/`）都是**裸相对路径**，没有指定相对于哪个根目录。当 Claude Code agent 执行 Write 操作时，使用的是**当前工作目录（CWD）**作为基准——而 CWD 在用户对 OpenHarness 项目调用 `/kb` 时是 `/Users/lijunyi/road/OpenHarness/`，不是插件所在目录 `/Users/lijunyi/road/claude-harness/plugins/kb/`。

这不是某个单一文件的 bug，而是**架构层面缺失**：整个 kb 插件没有定义"数据根目录"变量，所有 15 个 skill、2 个 agent、1 个 command 中全部使用硬编码的相对路径字符串 `data/raw/` 和 `data/wiki/`，隐式依赖 CWD 恰好等于插件目录。

**数据流追踪：**
1. 用户在 `/Users/lijunyi/road/OpenHarness/` 目录下执行 `/kb`
2. CWD = `/Users/lijunyi/road/OpenHarness/`
3. `scan` skill 写入 `data/raw/<project>/_map.md` → Write 工具解析为 `{CWD}/data/raw/<project>/_map.md` → 实际写入 `/Users/lijunyi/road/OpenHarness/data/raw/<project>/_map.md`
4. 期望路径应为 `/Users/lijunyi/road/claude-harness/plugins/kb/data/raw/<project>/_map.md`
5. 所有下游 skill（extract-*、ingest、cross-ref）同样受影响

**影响文件清单（路径引用不完整的全部文件）：**

| 文件类型 | 文件 | 引用路径 |
|---------|------|----------|
| Command | `commands/kb.md` (L54,58,74-77,85,132,138-142) | `data/raw/<project>/`, `data/wiki/<project>/` |
| Agent | `agents/extract-agent.md` (L18,25) | `data/raw/<project>/_map.md`, `data/raw/<project>/<dimension>/` |
| Agent | `agents/transform-agent.md` (L18,21) | `data/raw/<project>/<dimension>/_index.md`, wiki pages |
| Skill | `skills/scan/SKILL.md` (L23,47) | `data/raw/<project>/_map.md` |
| Skill | `skills/extract-topology/SKILL.md` (L24-29,52,54) | `data/raw/<project>/topology/` |
| Skill | `skills/extract-api/SKILL.md` (L28-29) | `data/raw/<project>/api/` |
| Skill | `skills/extract-data-model/SKILL.md` (L28-29) | `data/raw/<project>/data-model/` |
| Skill | `skills/extract-flows/SKILL.md` (L28-29) | `data/raw/<project>/flows/` |
| Skill | `skills/extract-concepts/SKILL.md` (L28-29) | `data/raw/<project>/concepts/` |
| Skill | `skills/ingest/SKILL.md` (L40,47-48) | `data/raw/<project>/`, `data/wiki/<project>/` |
| Skill | `skills/cross-ref/SKILL.md` (L24,37) | `data/wiki/<project>/`, `overview.md` |
| Skill | `skills/build-search-index/SKILL.md` (L18) | `public/search-index.json` |
| Skill | `skills/build-graph/SKILL.md` (L18) | `public/graph.json` |

### Bug 2: 文档质量低——覆盖不全、深度不够、图表不足、格式错误

**根因描述：** 文档质量问题有 3 个独立的根因：

**2a. 模块覆盖严重不全（80% 的模块缺失）**

_map.md_ 列出约 40 个模块（cli, config, manager, runtime, api, auth, autopilot, bridge, channels, commands, coordinator, engine, hooks, keybindings, mcp, memory, permissions, plugins, prompts, runner, sandbox, skills, state, swarm, tools, ui, ohmo, frontend, autopilot-dashboard 等），但实际提取的模块极少：

| 维度 | _map.md 模块数 | 实际提取模块数 | 覆盖率 |
|------|---------------|---------------|--------|
| topology | ~40 | 4 (api, plugins, swarm, ui) | 10% |
| api | ~40 | 2 (api, swarm) | 5% |
| data-model | ~40 | 2 (api, swarm) | 5% |
| flows | ~40 | 2 (engine, plugins) | 5% |
| concepts | ~40 | 1 (core) | 2.5% |

**根因：** extract-* skill 的执行流程中写道"对每个模块"逐一分析，但没有显式的**遍历约束**或**完整性检查**。Claude Code agent 在子代理模式下受到上下文窗口和 token 预算限制，倾向于跳过大量模块以节省时间。Skill 没有声明"必须覆盖 _map.md 中的全部模块"，也没有提供分批处理策略。

**2b. 文档深度不够（不满足模板必含章节）**

对比模板要求和实际产出：

| 模板必含章节 | 实际产出情况 |
|------------|-------------|
| topology: 上游依赖 Mermaid 图 | 缺失（只有依赖表，没有单独的上游图） |
| topology: 下游依赖 Mermaid 图 | 缺失 |
| flows: 流程概述（触发条件/参与者/分类） | 部分缺失 |
| flows: 流程清单表格 | 缺失 |
| flows: 超时与重试 | 缺失（只有简单提及） |
| flows: 并发与一致性 | 缺失 |
| data-model: 模型概述（设计哲学） | 缺失 |
| data-model: 索引定义 | 缺失 |
| data-model: 数据生命周期 | 缺失 |
| data-model: 迁移历史 | 缺失 |
| concepts: 术语表（表格形式） | 缺失（用了列表而非表格） |
| concepts: 概念层次图 | 缺失 |
| concepts: 概念演进 | 缺失 |

**根因：** Skill 文件中引用模板（如"遵循 `templates/topology.md` 定义的必含章节和质量要求"），但 agent 未必会在执行时再次加载模板文件，因为 skill 已通过 Skill 工具加载到上下文中。模板被引用但**未内联**，agent 可能不知道模板的具体要求。此外，skill 中没有**自检机制**要求 agent 在写完文档后逐项核对模板必含章节。

**2c. Wiki 页面与 raw 文档几乎相同（ingest 转化过于浅层）**

对比 raw extract 和 wiki 页面内容，ingest 转化几乎只是"复制 + 加 frontmatter + 加交叉引用链接"，没有做：
- 结构重组（从模块视角转为实体/概念/综合视角）
- 补充模板要求的缺失章节（如 entity 模板的约束、代码映射；synthesis 模板的洞察）
- 深度分析和推理

**根因：** `ingest` skill (L40-48) 的执行流程过于模糊——"识别实体 → 用 entity 模板生成页面"、"识别概念 → 用 concept 模板生成页面"、"跨模块综合 → 用 synthesis 模板生成页面"——但没有定义**识别标准**和**生成深度**。Agent 倾向于做最小工作量的转化。

## 影响范围

- **所有使用 kb 插件的用户**：生成的文档目录在目标项目而非插件目录，与 site/ 的符号链接不一致，导致站点无法读取数据
- **所有维度的文档质量**：80%+ 的模块未被提取，已提取的模块深度不足
- **站点展示**：数据不在正确位置，site/ 的 symlinks 指向插件自己的 data/，与实际输出位置脱节

## 复现条件

1. 在任意项目目录（非 claude-harness/plugins/kb/）下启动 Claude Code
2. 执行 `/kb` 命令扫描该项目
3. 观察 data/ 目录出现在当前项目根目录下，而非 `plugins/kb/data/`
4. 检查生成的文档：模块覆盖率极低、缺少模板要求的章节、Mermaid 图不足

## 修复假设

### 假设 H1: 输出路径问题——引入 KB_DATA_ROOT 变量

在所有 skill/agent/command 中引入一个数据根目录变量（如 `KB_DATA_ROOT`），使其指向插件自身的 data/ 目录（`<plugin-root>/data/`），而非 CWD 相对路径。

**方案：**
- 在 `/kb` command 中定义 `KB_DATA_ROOT` 的计算逻辑：基于 skill 文件的 `__dirname` 或插件 manifest 的路径推算
- 所有 skill/agent 中将 `data/raw/` 替换为 `{KB_DATA_ROOT}/raw/`，`data/wiki/` 替换为 `{KB_DATA_ROOT}/wiki/`
- 由于 Claude Code skill 没有运行时变量机制，需要将路径计算逻辑写入 `/kb` command，并让 command 将绝对路径传递给子代理

### 假设 H2: 文档质量低——执行粒度过粗 + 质量约束缺失

当前 extract-agent 一次处理一个维度的**全部模块**（~40 个），token 预算不足时 agent 大量跳过模块、每个模块只写最浅层的内容。deep-functional-analysis skill 的产出之所以充实，是因为它**聚焦单一主题**，agent 有充足上下文做深度分析。

kb 的方法论（模板驱动、维度提取）是正确的，不需要改成问题驱动。但执行策略需要调整：

**H2a. 子代理粒度从"维度级"改为"模块级"**

- 当前：一个 extract-agent 处理一个维度的全部模块 → 覆盖率 5-10%
- 改为：一个 extract-agent 处理一个维度**的一个模块** → 覆盖率 100%，每模块深度足够
- `/kb` command 的 Step 2 EXTRACT 派发策略从"5 个维度级子代理"改为"维度×模块矩阵的并行子代理"
- 每个子代理只需读取目标模块的代码 + `_map.md` 中该模块的条目，上下文开销大幅减少

**H2b. 强化质量约束（不改方法论，加硬约束）**

- 每个 extract-* skill 增加**图示硬约束**：每个模块文档至少 3 张 Mermaid 图（当前只要求 1 张）
- 每个模块文档增加**对比约束**：至少 1 个对比表格（与其他模块对比/与替代方案对比），对比必须有维度和结论
- 每个模块文档增加**量化约束**：设计决策必须有具体数字或明确说明，禁止模糊表述
- 每个模块文档增加**边界条件约束**：关键结论说明"何时不成立"或"残留风险"
- 这些约束写在 skill 的执行流程中（不是模板引用），agent 执行时必须遵循

**H2c. 增加验收标准**

- 每个 extract-* skill 末尾增加验收勾选框（P0/P1 分级），agent 完成后逐项自检
- P0 未满足必须补充，不能跳过
- 验收标准与 deep-functional-analysis 的勾选框机制类似，但适配各维度的模板要求

## 风险

1. **路径变量传递风险**：Claude Code 的 skill/agent 系统没有运行时变量机制，子代理的 prompt 中需要硬编码绝对路径。如果插件安装路径变化（用户搬家、重装），路径可能失效。替代方案：使用环境变量或让用户配置路径。
2. **子代理数量爆炸风险**：改为模块级派发后，40 模块 × 5 维度 = 200 个子代理，远超当前 5 个。需要限制并行数量（如每轮最多 10 个），且子代理模型建议用 sonnet 而非 opus 以控制成本。
3. **模板维护风险**：强化质量约束写在 skill 中，需与 templates/ 下的模板文件保持一致。建议：删除 templates/ 子目录，将必含章节和质量要求直接内联到 skill 的执行流程中（消除双源问题）。
4. **ingest 转化一致性风险**：模块级提取后每个模块文档风格独立，ingest 转化时需要统一风格和交叉引用。cross-ref skill 需要适配模块级产出。