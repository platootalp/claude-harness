# kb 输出路径 + 文档质量 修复实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 kb 插件两个 bug：1) 输出目录落在目标项目而非插件 data 目录；2) 文档质量低（覆盖率不足、深度不够、图表少、格式不完整）

**Architecture:** Bug 1 通过在 `/kb` command 中计算插件 data 绝对路径并传递给子代理解决。Bug 2 通过将子代理粒度从维度级改为模块级、强化质量约束（图示/对比/量化/验收）解决。模板内联到 skill 中消除双源问题。

**Tech Stack:** Claude Code plugin skill/agent/command (markdown), 无代码变更

---

## 文件结构

| 操作 | 文件 | 职责 |
|------|------|------|
| Modify | `commands/kb.md` | 路径计算 + 模块级派发逻辑 |
| Modify | `agents/extract-agent.md` | 改为单模块提取 |
| Modify | `agents/transform-agent.md` | 适配模块级产出路径 |
| Modify | `skills/scan/SKILL.md` | 路径变量 + 质量约束 |
| Modify | `skills/extract-topology/SKILL.md` | 路径变量 + 质量约束 + 验收标准 + 内联模板 |
| Modify | `skills/extract-api/SKILL.md` | 同上 |
| Modify | `skills/extract-data-model/SKILL.md` | 同上 |
| Modify | `skills/extract-flows/SKILL.md` | 同上 |
| Modify | `skills/extract-concepts/SKILL.md` | 同上 |
| Modify | `skills/ingest/SKILL.md` | 路径变量 + 深化转化指导 |
| Modify | `skills/cross-ref/SKILL.md` | 路径变量 |
| Modify | `skills/build-search-index/SKILL.md` | 路径变量 |
| Modify | `skills/build-graph/SKILL.md` | 路径变量 |
| Modify | `.claude-plugin/plugin.json` | 版本号 0.5.0 → 0.6.0 |
| Modify | `CHANGELOG.md` | 新增 [Unreleased] 条目 |
| Delete | `skills/extract-topology/templates/topology.md` | 内联到 skill |
| Delete | `skills/extract-api/templates/api.md` | 内联到 skill |
| Delete | `skills/extract-data-model/templates/data-model.md` | 内联到 skill |
| Delete | `skills/extract-flows/templates/flows.md` | 内联到 skill |
| Delete | `skills/extract-concepts/templates/concepts.md` | 内联到 skill |

ingest 的 templates/（entity.md, concept.md, synthesis.md）保留，因为 ingest 模板是 wiki 页面结构模板，与 extract 的分析模板性质不同。

---

## Task 1: `/kb` command — 路径计算 + 模块级派发

**Files:**
- Modify: `plugins/kb/commands/kb.md`

这是最关键的改动——`/kb` command 是整个管道的编排者，需要：1) 计算插件 data 绝对路径；2) 改为模块级派发。

- [ ] **Step 1: 修改 `/kb` command 的 Step 1 SCAN**

在 Step 1 之前增加路径计算逻辑，修改 Step 1 传入路径：

将 Step 1 的描述从：
```
- 扫描代码库结构，产出模块清单、依赖关系、架构分层、入口识别、复杂度指标
- 输出: `data/raw/<project>/_map.md`
```
改为：
```
- 扫描代码库结构，产出模块清单、依赖关系、架构分层、入口识别、复杂度指标
- 输出: `{KB_DATA_ROOT}/raw/<project>/_map.md`
```

在 Step 1 之前增加路径计算段落：
```markdown
## 路径约定

所有数据写入路径基于 `KB_DATA_ROOT`，计算规则：

1. 读取本 command 文件所在目录，向上两级即为插件根目录（`commands/` → plugin root）
2. `KB_DATA_ROOT = <plugin-root>/data/`
3. 所有子代理 prompt 中，将 `data/raw/` 替换为 `{KB_DATA_ROOT}/raw/`，`data/wiki/` 替换为 `{KB_DATA_ROOT}/wiki/`
4. 在派发子代理时，将 `KB_DATA_ROOT` 的绝对路径作为参数传入 prompt

**示例：** 插件安装在 `/Users/x/.claude/plugins/cache/harness-marketplace/kb/0.6.0/`，则 `KB_DATA_ROOT = /Users/x/.claude/plugins/cache/harness-marketplace/kb/0.6.0/data/`
```

- [ ] **Step 2: 修改 Step 2 EXTRACT 为模块级派发**

将 Step 2 从"5 个维度级子代理"改为"维度×模块矩阵的模块级子代理"：

```markdown
## Step 2/6: EXTRACT

**按模块并行派发 extract 子代理。**

1. 读取 `{KB_DATA_ROOT}/raw/<project>/_map.md`，解析模块清单
2. 对每个维度 × 每个模块，派发一个子代理（最多同时 10 个并行）
3. 每个子代理 prompt 模板:
```
你是 extract 模块子代理。

项目: {project}
维度: {dimension}
模块: {module}
数据根目录: {KB_DATA_ROOT}
目标代码库: {target_path}

执行流程:
1. 读取 {KB_DATA_ROOT}/raw/{project}/_map.md
2. 读取目标模块的源代码文件
3. 调用 kb:extract-{dimension} skill（仅分析 {module} 模块）
4. 验证产出: {KB_DATA_ROOT}/raw/{project}/{dimension}/modules/{module}.md 存在且内容满足验收标准
5. 报告: 维度 / 模块 / 状态 / 产出行数 / 验收通过项
```

5 个维度: topology, api, data-model, flows, concepts
模块列表: 从 _map.md 的模块清单表格提取

等待所有子代理完成后，汇总结果。对每个维度生成 `_index.md`（汇总该维度所有模块的产出）。
```

- [ ] **Step 3: 修改 Step 4 TRANSFORM 适配模块级产出**

Step 4 的子代理 prompt 中路径全部替换为 `{KB_DATA_ROOT}` 前缀。transform-agent 的派发逻辑不变（仍按维度派发），但路径引用更新。

- [ ] **Step 4: 修改 Step 5/6 LOAD 和 SERVE 路径引用**

Step 5 中 `public/search-index.json` 等路径改为基于 `site/` 目录的绝对路径（`{KB_DATA_ROOT}/../site/public/`）。

- [ ] **Step 5: Commit**

```bash
git add plugins/kb/commands/kb.md
git commit -m "fix(kb): compute KB_DATA_ROOT absolute path + module-level dispatch in /kb command"
```

---

## Task 2: extract-agent — 改为单模块提取

**Files:**
- Modify: `plugins/kb/agents/extract-agent.md`

- [ ] **Step 1: 修改 extract-agent 参数和执行流程**

将 extract-agent 从"处理一个维度的全部模块"改为"处理一个维度的一个模块"：

```markdown
---
name: extract-agent
model: sonnet
tools: Read, Glob, Grep, Bash, Skill, Write
---

# Extract Agent — 单模块提取

执行指定维度的单个模块知识提取，产出 raw 文档。

## 输入参数

- `--project`: 项目名称（必需）
- `--dimension`: 提取维度（必需），取值: topology | api | data-model | flows | concepts
- `--module`: 模块名称（必需），取自 _map.md 模块清单
- `--kb-data-root`: 数据根目录绝对路径（必需）

## 执行流程

1. 读取 `{kb-data-root}/raw/<project>/_map.md`（硬前置：必须存在）
2. 根据 dimension 参数调用对应技能，传入 `--module` 参数限定分析范围：
   - topology → `kb:extract-topology`
   - api → `kb:extract-api`
   - data-model → `kb:extract-data-model`
   - flows → `kb:extract-flows`
   - concepts → `kb:extract-concepts`
3. 验证产出：确认 `{kb-data-root}/raw/<project>/<dimension>/modules/<module>.md` 存在且行数 ≥ 50
4. 报告结果

## 报告格式

```
维度: <dimension>
模块: <module>
状态: DONE | DONE_WITH_CONCERNS | BLOCKED
产出: <module>.md (<行数> 行)
验收: <通过项>/<总项>
问题: <如有>
```
```

- [ ] **Step 2: Commit**

```bash
git add plugins/kb/agents/extract-agent.md
git commit -m "fix(kb): change extract-agent to single-module extraction"
```

---

## Task 3: transform-agent — 适配路径变量

**Files:**
- Modify: `plugins/kb/agents/transform-agent.md`

- [ ] **Step 1: 修改 transform-agent 路径引用**

增加 `--kb-data-root` 参数，所有路径引用改为基于该参数：

```markdown
---
name: transform-agent
model: sonnet
tools: Read, Glob, Grep, Bash, Skill, Write, Edit
---

# Transform Agent — 单维度转化

执行指定维度的 ingest 转化，将 raw 文档转为 wiki 页面。

## 输入参数

- `--project`: 项目名称（必需）
- `--dimension`: 转化维度（必需），对应 raw 目录下的维度名
- `--kb-data-root`: 数据根目录绝对路径（必需）

## 执行流程

1. 读取 `{kb-data-root}/raw/<project>/<dimension>/_index.md`，确认 `status: unprocessed`
2. 调用 `kb:ingest` 技能处理该维度
3. 确认 `kb:ingest` 技能已产出 wiki 页面（entity/concept/synthesis）
4. 更新 `_index.md` status 为 `processed`
5. 报告结果

## 报告格式

```
维度: <dimension>
状态: DONE | DONE_WITH_CONCERNS | BLOCKED
产出: N 个 entity 页面 + M 个 concept 页面 + K 个 synthesis 页面
问题: <如有>
```
```

- [ ] **Step 2: Commit**

```bash
git add plugins/kb/agents/transform-agent.md
git commit -m "fix(kb): add kb-data-root parameter to transform-agent"
```

---

## Task 4: scan skill — 路径变量 + 质量约束

**Files:**
- Modify: `plugins/kb/skills/scan/SKILL.md`

- [ ] **Step 1: 修改 scan skill**

修改要点：
1. 增加 `--kb-data-root` 参数
2. 输出路径改为 `{KB_DATA_ROOT}/raw/<project>/_map.md`
3. 增加质量约束：模块职责描述必须 ≥ 10 字（非一句话空泛描述）、依赖关系必须覆盖 _map.md 中 90%+ 的模块间 import

具体修改——将输出部分从：
```
写入 `data/raw/<project>/_map.md`
```
改为：
```
写入 `{KB_DATA_ROOT}/raw/<project>/_map.md`
```

将执行流程第 8 步从：
```
8. **写入 `_map.md`**，按下方格式输出到 `data/raw/<project>/_map.md`
```
改为：
```
8. **写入 `_map.md`**，按下方格式输出到 `{KB_DATA_ROOT}/raw/<project>/_map.md`
9. **质量自检**：确认模块清单覆盖率 ≥ 90%（非空目录均应出现）、依赖关系覆盖 _map.md 中 90%+ 的模块间 import、每个模块职责描述 ≥ 10 字
```

- [ ] **Step 2: Commit**

```bash
git add plugins/kb/skills/scan/SKILL.md
git commit -m "fix(kb): add KB_DATA_ROOT path + quality constraints to scan skill"
```

---

## Task 5: extract-topology skill — 路径 + 质量约束 + 验收 + 内联模板

**Files:**
- Modify: `plugins/kb/skills/extract-topology/SKILL.md`
- Delete: `plugins/kb/skills/extract-topology/templates/topology.md`

- [ ] **Step 1: 重写 extract-topology SKILL.md**

修改要点：
1. 增加 `--kb-data-root` 参数，输出路径改为 `{KB_DATA_ROOT}/raw/<project>/topology/`
2. 内联模板必含章节（删除 templates/topology.md 引用，将内容直接写入 skill）
3. 增加质量约束：每模块 ≥ 3 张 Mermaid 图、≥ 1 张对比表格、设计决策有量化说明、关键结论有边界条件
4. 增加验收标准勾选框

关键新增内容（追加到 skill 末尾）：

```markdown
## 质量约束

- 每个模块文档至少 **3 张 Mermaid 图**（组件图 + 依赖图 + 至少一张序列图/状态图/流程图）
- 每个模块文档至少 **1 张对比表格**（与其他模块对比/与替代方案对比），对比必须有维度列和结论列
- 设计决策必须有**量化说明**（具体数字或明确取舍理由），禁止"更好"、"更快"等模糊表述
- 关键结论必须说明**边界条件**（"何时不成立"或"残留风险"）
- 职责边界必须同时列出"负责"和"不负责"，各 ≥ 3 条
- 代码证据必须包含实际文件路径和行号范围

## 验收标准

交付前逐项勾选，P0 未满足必须补充：

### P0 — 必含章节
- [ ] 模块概述（职责 + 系统位置）
- [ ] 内部结构（子组件 + Mermaid 组件图）
- [ ] 职责边界（负责 + 不负责，各 ≥ 3 条）
- [ ] 上游依赖（表格 + Mermaid 图）
- [ ] 下游依赖（表格 + Mermaid 图）
- [ ] 关键设计决策（≥ 3 条，有量化说明）
- [ ] 代码证据（实际路径 + 行号）

### P1 — 深度
- [ ] ≥ 3 张 Mermaid 图
- [ ] ≥ 1 张对比表格（有维度 + 有结论）
- [ ] 关键结论有边界条件
- [ ] 设计决策有量化说明
```

- [ ] **Step 2: 删除 templates/topology.md**

```bash
rm plugins/kb/skills/extract-topology/templates/topology.md && rmdir plugins/kb/skills/extract-topology/templates
```

- [ ] **Step 3: Commit**

```bash
git add plugins/kb/skills/extract-topology/ && git commit -m "fix(kb): add KB_DATA_ROOT + quality constraints + acceptance criteria + inline template to extract-topology"
```

---

## Task 6: extract-api skill — 路径 + 质量约束 + 验收 + 内联模板

**Files:**
- Modify: `plugins/kb/skills/extract-api/SKILL.md`
- Delete: `plugins/kb/skills/extract-api/templates/api.md`

- [ ] **Step 1: 重写 extract-api SKILL.md**

同 Task 5 的模式：增加 `--kb-data-root`、内联模板、增加质量约束和验收标准。

API 维度的质量约束：
- 每个模块文档至少 **3 张 Mermaid 图**（序列图 + 调用流程图 + 至少一张状态图/流程图）
- 每个接口至少 **1 个调用示例**（curl 命令或代码片段，可执行非伪代码）
- 错误码必须包含**触发条件**
- 每个模块文档至少 **1 张对比表格**

验收标准 P0：
- [ ] 接口概述（定位 + 协议类型 + 认证方式）
- [ ] 接口清单（表格：方法 | 路径/名称 | 用途 | 认证）
- [ ] 接口详情（参数表 + 响应表 + 错误码表 + 示例）
- [ ] 调用模式（Mermaid 序列图）

验收标准 P1：
- [ ] ≥ 3 张 Mermaid 图
- [ ] 每个接口有调用示例
- [ ] ≥ 1 张对比表格

- [ ] **Step 2: 删除 templates/api.md**

```bash
rm plugins/kb/skills/extract-api/templates/api.md && rmdir plugins/kb/skills/extract-api/templates
```

- [ ] **Step 3: Commit**

```bash
git add plugins/kb/skills/extract-api/ && git commit -m "fix(kb): add KB_DATA_ROOT + quality constraints + acceptance criteria + inline template to extract-api"
```

---

## Task 7: extract-data-model skill — 路径 + 质量约束 + 验收 + 内联模板

**Files:**
- Modify: `plugins/kb/skills/extract-data-model/SKILL.md`
- Delete: `plugins/kb/skills/extract-data-model/templates/data-model.md`

- [ ] **Step 1: 重写 extract-data-model SKILL.md**

同上模式。数据模型维度的质量约束：
- 每个模块文档至少 **2 张 Mermaid 图**（ER 图 + 关系图）
- 字段定义必须包含**约束信息**（非空/唯一/默认值）
- 关系必须标注**级联规则**
- 每个模块文档至少 **1 张对比表格**

验收标准 P0：
- [ ] 模型概述（设计哲学 + ER 图）
- [ ] 实体清单（表格）
- [ ] 实体详情（字段表含约束 + 索引定义）
- [ ] 关系详情（级联规则 + Mermaid 图）

验收标准 P1：
- [ ] ≥ 2 张 Mermaid 图
- [ ] 字段含约束信息
- [ ] 关系含级联规则
- [ ] ≥ 1 张对比表格

- [ ] **Step 2: 删除 templates/data-model.md**

```bash
rm plugins/kb/skills/extract-data-model/templates/data-model.md && rmdir plugins/kb/skills/extract-data-model/templates
```

- [ ] **Step 3: Commit**

```bash
git add plugins/kb/skills/extract-data-model/ && git commit -m "fix(kb): add KB_DATA_ROOT + quality constraints + acceptance criteria + inline template to extract-data-model"
```

---

## Task 8: extract-flows skill — 路径 + 质量约束 + 验收 + 内联模板

**Files:**
- Modify: `plugins/kb/skills/extract-flows/SKILL.md`
- Delete: `plugins/kb/skills/extract-flows/templates/flows.md`

- [ ] **Step 1: 重写 extract-flows SKILL.md**

同上模式。流程维度的质量约束：
- 每个模块文档至少 **3 张 Mermaid 图**（流程图 + 序列图 + 状态图）
- 必须包含**异常路径**（每个流程至少 1 个异常路径）
- 状态机必须覆盖**所有转换**
- 每个模块文档至少 **1 张对比表格**

验收标准 P0：
- [ ] 流程概述（触发条件 + 参与者 + 分类）
- [ ] 流程清单（表格：流程名 | 类型 | 触发方式 | 关键性）
- [ ] 流程详情（Mermaid 图 + 异常路径 + 后置状态）
- [ ] 状态机（转换表 + Mermaid 状态图）

验收标准 P1：
- [ ] ≥ 3 张 Mermaid 图
- [ ] 异常路径覆盖
- [ ] ≥ 1 张对比表格

- [ ] **Step 2: 删除 templates/flows.md**

```bash
rm plugins/kb/skills/extract-flows/templates/flows.md && rmdir plugins/kb/skills/extract-flows/templates
```

- [ ] **Step 3: Commit**

```bash
git add plugins/kb/skills/extract-flows/ && git commit -m "fix(kb): add KB_DATA_ROOT + quality constraints + acceptance criteria + inline template to extract-flows"
```

---

## Task 9: extract-concepts skill — 路径 + 质量约束 + 验收 + 内联模板

**Files:**
- Modify: `plugins/kb/skills/extract-concepts/SKILL.md`
- Delete: `plugins/kb/skills/extract-concepts/templates/concepts.md`

- [ ] **Step 1: 重写 extract-concepts SKILL.md**

同上模式。概念维度的质量约束：
- 每个模块文档至少 **2 张 Mermaid 图**（概念关系图 + 概念层次图）
- 术语表必须**表格形式**（术语 | 英文对照 | 定义 | 首次出现位置）
- 每个核心概念必须有**代码路径**
- 每个模块文档至少 **1 张对比表格**

验收标准 P0：
- [ ] 术语表（表格形式，按字母排序）
- [ ] 核心概念（定义 + 角色 + 代码路径 + Mermaid 图）
- [ ] 概念层次（Mermaid 层次图）
- [ ] 命名规范（模式 + 约定 + 缩写表）

验收标准 P1：
- [ ] ≥ 2 张 Mermaid 图
- [ ] 术语表为表格形式
- [ ] ≥ 1 张对比表格

- [ ] **Step 2: 删除 templates/concepts.md**

```bash
rm plugins/kb/skills/extract-concepts/templates/concepts.md && rmdir plugins/kb/skills/extract-concepts/templates
```

- [ ] **Step 3: Commit**

```bash
git add plugins/kb/skills/extract-concepts/ && git commit -m "fix(kb): add KB_DATA_ROOT + quality constraints + acceptance criteria + inline template to extract-concepts"
```

---

## Task 10: ingest skill — 路径变量 + 深化转化指导

**Files:**
- Modify: `plugins/kb/skills/ingest/SKILL.md`

- [ ] **Step 1: 修改 ingest skill**

修改要点：
1. 增加 `--kb-data-root` 参数，路径改为 `{KB_DATA_ROOT}/raw/` 和 `{KB_DATA_ROOT}/wiki/`
2. 深化转化指导：明确 ingest 不是格式转换，而是从 raw 文档中**提取和重组**信息以匹配模板结构

将执行流程第 3 步从：
```
3. **对每个维度执行：**
   - a. 读取 `_index.md` 和所有模块文档
   - b. 识别实体 → 用 entity 模板生成页面
   - c. 识别概念 → 用 concept 模板生成页面
   - d. 跨模块综合 → 用 synthesis 模板生成页面
   - e. 写入 `data/wiki/<project>/`
   - f. 更新 `_index.md` 状态为 `processed`
```
改为：
```
3. **对每个维度执行：**
   - a. 读取 `_index.md` 和所有模块文档
   - b. **实体识别与重组**：每个模块即为一个实体。从 raw 文档中提取信息，按 entity 模板结构重组（不是复制，是提取关键字段、补充约束和代码映射、生成 Mermaid 结构图）
   - c. **概念识别与重组**：从 raw 文档中提取领域术语和核心概念，按 concept 模板结构重组（补充原理、实现示例、演进历史）
   - d. **跨模块综合**：识别跨模块/跨维度主题，按 synthesis 模板生成综合分析页面（必须包含全景图、深度分析、交叉引用、洞察）
   - e. 写入 `{KB_DATA_ROOT}/wiki/<project>/`
   - f. 更新 `_index.md` 状态为 `processed`
   - g. **质量自检**：每个 entity 页面行数 ≥ 80、每个 synthesis 页面行数 ≥ 60、每个页面至少 1 张 Mermaid 图
```

- [ ] **Step 2: Commit**

```bash
git add plugins/kb/skills/ingest/SKILL.md
git commit -m "fix(kb): add KB_DATA_ROOT + deepen ingest transformation guidance"
```

---

## Task 11: cross-ref + build-search-index + build-graph — 路径变量

**Files:**
- Modify: `plugins/kb/skills/cross-ref/SKILL.md`
- Modify: `plugins/kb/skills/build-search-index/SKILL.md`
- Modify: `plugins/kb/skills/build-graph/SKILL.md`

- [ ] **Step 1: 修改 cross-ref skill 路径引用**

增加 `--kb-data-root` 参数，将 `data/wiki/<project>/` 改为 `{KB_DATA_ROOT}/wiki/<project>/`。

- [ ] **Step 2: 修改 build-search-index skill 路径引用**

增加 `--kb-data-root` 参数，说明数据读取路径基于 `{KB_DATA_ROOT}/raw/` 和 `{KB_DATA_ROOT}/wiki/`（通过 site/ 的符号链接访问）。

- [ ] **Step 3: 修改 build-graph skill 路径引用**

同上。

- [ ] **Step 4: Commit**

```bash
git add plugins/kb/skills/cross-ref/SKILL.md plugins/kb/skills/build-search-index/SKILL.md plugins/kb/skills/build-graph/SKILL.md
git commit -m "fix(kb): add KB_DATA_ROOT path to cross-ref, build-search-index, build-graph skills"
```

---

## Task 12: 版本号 + CHANGELOG

**Files:**
- Modify: `plugins/kb/.claude-plugin/plugin.json`
- Modify: `plugins/kb/CHANGELOG.md`

- [ ] **Step 1: 更新版本号 0.5.0 → 0.6.0**

将 `plugin.json` 中 `version` 从 `"0.5.0"` 改为 `"0.6.0"`。

- [ ] **Step 2: 更新 CHANGELOG.md**

在 `CHANGELOG.md` 顶部增加 `[Unreleased]` 条目（或如果已有则追加），记录本次修复：

```markdown
## [0.6.0] - 2026-05-25

### Fixed

- **输出目录错误**：所有 skill/agent/command 的数据路径改为基于 `KB_DATA_ROOT` 绝对路径，不再依赖 CWD
- **子代理粒度过粗**：extract-agent 从维度级改为模块级，每个子代理只处理一个模块，覆盖率从 5-10% 提升到 100%
- **文档质量不足**：增加质量约束（Mermaid 图 ≥ 3/模块、对比表格、量化权衡、边界条件）和验收标准勾选框
- **模板双源问题**：extract-* skill 的模板必含章节内联到 skill 中，删除 templates/ 子目录

### Changed

- `/kb` command 增加 `KB_DATA_ROOT` 路径计算逻辑
- extract-agent 改为单模块提取（新增 `--module` 和 `--kb-data-root` 参数）
- transform-agent 增加 `--kb-data-root` 参数
- ingest skill 深化转化指导（重组而非复制）
```

- [ ] **Step 3: Commit**

```bash
git add plugins/kb/.claude-plugin/plugin.json plugins/kb/CHANGELOG.md
git commit -m "chore(kb): bump version to 0.6.0 + changelog for output path and quality fixes"
```
