# KB 插件实现计划 — Extract 阶段

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 KB 插件的 Extract 阶段——结构梳理 + 5 维度深度分析 + 路由命令 + agent，产出的 raw 文档可被 Transform 阶段消费。

**Architecture:** 两阶段 Extract：scan skill 产出结构地图（`_map.md`），5 个维度 skill 读取地图后逐模块/逐流程深度提取。所有产出写入 `data/raw/<project>/`，通过 frontmatter 的 `status` 字段与 Transform 阶段解耦。`/kb` 命令和 3 个 agent 作为管道入口。

**Tech Stack:** Claude Code plugin（markdown skills/agents/commands），Astro 6 + React 18 + Tailwind 3（站点骨架）

**依赖的设计文档：** `docs/superpowers/specs/2026-05-24-kb-plugin-design.md`

---

## 文件结构

### 新建文件

```
plugins/kb/
├── .claude-plugin/plugin.json
├── .gitignore
├── CHANGELOG.md
├── CLAUDE.md
├── data/
│   └── config.json
├── skills/
│   ├── extract/SKILL.md
│   ├── scan/SKILL.md
│   ├── extract-topology/
│   │   ├── SKILL.md
│   │   └── templates/topology.md
│   ├── extract-api/
│   │   ├── SKILL.md
│   │   └── templates/api.md
│   ├── extract-data-model/
│   │   ├── SKILL.md
│   │   └── templates/data-model.md
│   ├── extract-flows/
│   │   ├── SKILL.md
│   │   └── templates/flows.md
│   └── extract-concepts/
│       ├── SKILL.md
│       └── templates/concepts.md
├── agents/
│   ├── kb-agent.md
│   ├── extract-agent.md
│   └── transform-agent.md
└── commands/
    └── kb.md
```

### 修改文件

```
.claude-plugin/marketplace.json          # 注册 kb 插件
CLAUDE.md                                # 更新插件列表
```

---

## Task 1: 插件骨架

**Files:**
- Create: `plugins/kb/.claude-plugin/plugin.json`
- Create: `plugins/kb/.gitignore`
- Create: `plugins/kb/CHANGELOG.md`
- Create: `plugins/kb/data/config.json`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: 创建 plugin.json**

```json
{
  "name": "kb",
  "version": "0.1.0",
  "description": "自动化个人知识库 — 代码库深度分析、结构化知识转化、交互式展示",
  "author": { "name": "platootalp" },
  "license": "MIT"
}
```

- [ ] **Step 2: 创建 .gitignore**

```
data/raw/
data/wiki/
site/node_modules/
site/dist/
site/.astro/
```

- [ ] **Step 3: 创建 CHANGELOG.md**

```markdown
# Changelog

## [Unreleased]

### Added
- 初始插件骨架
```

- [ ] **Step 4: 创建 data/config.json**

```json
{"dataDir": "data"}
```

- [ ] **Step 5: 在 marketplace.json 中注册 kb 插件**

在 `plugins` 数组中添加：

```json
{
  "name": "kb",
  "source": "./plugins/kb",
  "description": "自动化个人知识库 — 代码库深度分析、结构化知识转化、交互式展示"
}
```

- [ ] **Step 6: 提交**

```bash
git add plugins/kb/ .claude-plugin/marketplace.json
git commit -m "feat(kb): 初始插件骨架"
```

---

## Task 2: scan skill

**Files:**
- Create: `plugins/kb/skills/scan/SKILL.md`

- [ ] **Step 1: 编写 scan SKILL.md**

```markdown
---
name: scan
description: 当需要理解代码库结构、规划深度分析范围、或为 extract 维度技能提供输入时使用。产出模块清单、依赖关系、架构分层、入口识别、复杂度指标的结构地图。
---

# Scan — 代码库结构梳理

扫描目标代码库，产出结构地图 `_map.md`，作为深度分析的路线图。

<HARD-GATE>
`_map.md` 不存在时，所有 extract 维度技能（extract-topology、extract-api 等）无法执行。scan 是 Extract 管道的起点，必须先完成。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--target <path>` | 否 | 当前工作目录 | 目标代码库路径 |
| `--project <name>` | 否 | 路径最后一层目录名 | 项目名称，决定输出目录 |

## 输出

写入 `data/raw/<project>/_map.md`，作为后续 extract 技能的输入。

## 反模式

| 想法 | 问题 |
|------|------|
| "我直接开始 extract-topology，不需要先 scan" | 没有 `_map.md`，extract 技能不知道有哪些模块、依赖关系如何，会遗漏或重复分析 |
| "scan 结果不够详细，我来补充代码片段" | `_map.md` 是路线图，不是文档。细节由 extract 技能深入，scan 只负责结构 |
| "这个代码库太小了，不需要 scan" | 小代码库的 scan 很快。跳过 scan 会导致 extract 技能缺少输入，反而更慢 |
| "scan 结果看起来有误，我来手动修改 `_map.md`" | 可以修正，但应记录修正原因。下次 scan 会覆盖，所以根因可能是 scan 的识别逻辑不足 |

## 执行流程

1. 扫描目标路径，识别目录结构和文件类型分布
2. 识别模块/包/插件：按目录粒度划分，每个包含独立职责的目录为一个模块
3. 对每个模块：
   a. 读取目录内容，识别主要语言和框架
   b. 统计文件数量
   c. 识别对外接口（HTTP 端点、CLI 命令、事件、SDK 导出）
   d. 写一句话职责描述
4. 构建依赖关系图：分析模块间的 import/require 引用关系
5. 识别架构分层：根据目录命名和依赖方向推断分层（如 api/service/data/model）
6. 识别入口文件：main、index、router、config 等
7. 计算复杂度指标：按文件数量、依赖扇出、耦合度排名
8. 将所有结果写入 `_map.md`

## `_map.md` 格式

```markdown
# <project> 结构地图

> 扫描时间：YYYY-MM-DD HH:MM
> 目标路径：<path>

## 模块清单

| 模块 | 路径 | 职责 | 语言/框架 | 文件数 | 对外接口数 |
|------|------|------|-----------|--------|-----------|
| ... | ... | ... | ... | ... | ... |

## 依赖关系

（Mermaid 依赖关系图）

## 架构分层

| 层 | 模块 | 依赖规则 |
|----|------|---------|
| ... | ... | ... |

## 入口文件

| 文件 | 类型 | 说明 |
|------|------|------|
| ... | ... | ... |

## 复杂度排名

| 排名 | 模块 | 文件数 | 依赖扇出 | 耦合度 |
|------|------|--------|---------|--------|
| ... | ... | ... | ... | ... |
```

## 关键原则

- **路线图，非文档：** `_map.md` 是给 extract 技能用的分析指引，不是给用户看的文档
- **模块划分粒度：** 一个目录如果包含独立职责（有自己的 skills/agents/commands），就是一个模块
- **只分析直接依赖：** 不传递推导，A→B→C 只记录 A→B 和 B→C
- **分层是推断：** 架构分层基于命名和依赖方向推断，可能需要人工修正
```

- [ ] **Step 2: 提交**

```bash
git add plugins/kb/skills/scan/
git commit -m "feat(kb): 添加 scan skill — 代码库结构梳理"
```

---

## Task 3: extract-topology skill + 模板

**Files:**
- Create: `plugins/kb/skills/extract-topology/SKILL.md`
- Create: `plugins/kb/skills/extract-topology/templates/topology.md`

- [ ] **Step 1: 编写 topology 模板**

```markdown
# 模块拓扑分析模板

每份模块拓扑文档必须包含以下章节：

## 必含章节

### 1. 模块概述
- 一段话描述模块的职责和存在理由
- 在整个系统中的位置（属于哪层，服务谁）

### 2. 内部结构
- 子目录/子模块组成
- 每个子部分的职责
- Mermaid 组件图

### 3. 职责边界
- 这个模块负责什么（明确列出）
- 这个模块不负责什么（明确列出，避免职责扩散误解）

### 4. 上游交互
- 依赖哪些模块/服务，通过什么接口
- Mermaid 依赖关系图（仅上游）

### 5. 下游交互
- 被哪些模块/服务依赖，提供什么接口
- Mermaid 被依赖关系图（仅下游）

### 6. 关键设计决策
- 模块内部的架构选择（为什么这样组织）
- 与其他模块的交互方式选择

### 7. 代码证据
- 关键文件的路径和作用
- 入口文件、配置文件、核心逻辑文件

## 质量要求

- 每个模块至少 1 个 Mermaid 图
- 职责边界必须同时列出"负责"和"不负责"
- 代码证据必须包含实际文件路径
```

- [ ] **Step 2: 编写 extract-topology SKILL.md**

```markdown
---
name: extract-topology
description: 当需要理解模块内部结构、职责边界、上下游交互方式、或关键设计决策时使用。读取结构地图，逐模块产出深度拓扑分析文档。
---

# Extract Topology — 模块拓扑深度分析

读取结构地图，逐模块产出深度拓扑分析文档。

<HARD-GATE>
`data/raw/<project>/_map.md` 必须存在（由 scan 技能产出）。如果没有，先调用 scan 技能。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--target <path>` | 是 | - | 目标代码库路径 |
| `--project <name>` | 是 | - | 项目名称 |
| `--module <name>` | 否 | 全量 | 只分析指定模块 |

## 前置条件

- `data/raw/<project>/_map.md` 必须存在

## 输出

- `data/raw/<project>/topology/_index.md`（带 frontmatter 的索引）
- `data/raw/<project>/topology/modules/<module>.md`（每个模块一份深度文档）

## 反模式

| 想法 | 问题 |
|------|------|
| "我已经很熟悉这个模块了，不需要读代码" | 直觉会遗漏内部结构变化和隐性依赖，必须从代码证据出发 |
| "把所有模块写在一个大文件里" | 每个模块一份文档，保证独立性和可读性 |
| "职责边界只写负责什么就够了" | 只写"负责"会导致职责扩散——读者会假设你没写的你也管。必须同时写"不负责" |
| "Mermaid 图可有可无" | 拓扑分析的核心价值是可视化关系。没有图 = 没有拓扑分析 |

## 执行流程

1. 读取 `_map.md`，获取模块清单和依赖关系
2. 如果指定了 `--module`，只分析该模块；否则分析所有模块
3. 对每个模块：
   a. 读取模块目录下的所有文件
   b. 分析内部结构（子目录、子模块、文件组织）
   c. 确定职责边界（负责什么、不负责什么）
   d. 分析上游依赖（依赖谁、通过什么接口）
   e. 分析下游依赖（被谁依赖、提供什么接口）
   f. 识别关键设计决策
   g. 收集代码证据（关键文件路径和作用）
   h. 按 `templates/topology.md` 模板生成深度文档
   i. 写入 `topology/modules/<module>.md`
4. 生成 `topology/_index.md`（模块清单 + 依赖总图 + frontmatter）

## `_index.md` frontmatter

```yaml
---
project: <project>
dimension: topology
date: YYYY-MM-DD
status: unprocessed
tags: [...]
---
```

## 模板

遵循 `templates/topology.md` 定义的必含章节和质量要求。

## 关键原则

- **从代码出发，不从记忆出发：** 每个结论必须有代码路径佐证
- **职责边界是对称的：** "负责"和"不负责"同样重要，缺一不可
- **一个模块一个文件：** 保证文档独立性和 Transform 阶段的可处理性
```

- [ ] **Step 3: 提交**

```bash
git add plugins/kb/skills/extract-topology/
git commit -m "feat(kb): 添加 extract-topology skill + 模板"
```

---

## Task 4: extract-api skill + 模板

**Files:**
- Create: `plugins/kb/skills/extract-api/SKILL.md`
- Create: `plugins/kb/skills/extract-api/templates/api.md`

- [ ] **Step 1: 编写 api 模板**

```markdown
# API 接口分析模板

每份接口文档必须包含以下章节：

## 必含章节

### 1. 接口概述
- 接口类型（HTTP/CLI/事件/SDK）
- 所属模块
- 一段话描述这组接口的用途

### 2. 接口清单
- 每个接口的端点/命令/事件名
- HTTP 方法（如适用）
- 认证要求

### 3. 接口详情
对每个接口：
- 参数（名称、类型、必填、默认值、说明）
- 返回值（字段、类型、说明）
- 错误码/错误响应
- 调用示例（实际代码或 curl）

### 4. 接口间关系
- 同组接口的调用顺序依赖
- 与其他接口组的关联
- Mermaid 序列图（如涉及多步交互）

### 5. 版本与兼容
- 接口版本（如有）
- 破坏性变更历史（如有）
- 废弃接口（如有）

## 质量要求

- 每个接口必须有参数和返回值
- HTTP 接口必须有调用示例
- 涉及多步交互必须有 Mermaid 序列图
```

- [ ] **Step 2: 编写 extract-api SKILL.md**

```markdown
---
name: extract-api
description: 当需要理解代码库暴露的所有接口契约、参数细节、调用方式、或接口间关系时使用。从路由定义和 handler 代码中提取完整的 API 分析文档。
---

# Extract API — API 接口深度分析

读取结构地图，识别并提取所有对外暴露的接口。

<HARD-GATE>
`data/raw/<project>/_map.md` 必须存在。如果没有，先调用 scan 技能。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--target <path>` | 是 | - | 目标代码库路径 |
| `--project <name>` | 是 | - | 项目名称 |

## 前置条件

- `data/raw/<project>/_map.md` 必须存在

## 输出

- `data/raw/<project>/api/_index.md`
- `data/raw/<project>/api/http/<resource>.md`（HTTP 接口组）
- `data/raw/<project>/api/cli/<command-group>.md`（CLI 命令组）
- `data/raw/<project>/api/events/<event-type>.md`（事件接口）

## 反模式

| 想法 | 问题 |
|------|------|
| "只提取 HTTP 接口就够了" | CLI 命令、事件、SDK 导出同样是接口，遗漏它们会导致知识库不完整 |
| "参数和返回值从类型定义抄就行" | 类型定义不含业务含义。必须结合 handler 代码理解参数的实际用途和约束 |
| "调用示例用伪代码" | 伪代码无法验证。必须用实际的 curl 命令或代码片段，确保可执行 |
| "接口之间没有关系就不用画图" | 即使没有顺序依赖，也有数据依赖和共享资源。序列图揭示隐含关系 |

## 执行流程

1. 读取 `_map.md`，获取模块清单和对外接口数量
2. 扫描代码库，识别所有接口定义：
   - HTTP：路由定义、handler 函数、OpenAPI spec
   - CLI：命令定义、参数解析
   - 事件：事件发布/订阅定义
   - SDK：export 的公共接口
3. 按接口类型分组，每组按资源/命令组/事件类型组织
4. 对每组接口，按 `templates/api.md` 模板生成深度文档
5. 生成 `api/_index.md`

## 接口识别策略

- **HTTP：** 搜索路由注册模式（app.get/post、router.use、@Controller 等）
- **CLI：** 搜索命令定义模式（commander、yargs、argparse 等）
- **事件：** 搜索事件发布/订阅模式（emit/on、publish/subscribe 等）
- **SDK：** 搜索 export 语句和公共 API 声明

## 关键原则

- **契约完整性：** 参数、返回值、错误码三者缺一不可，否则无法作为接口参考
- **可验证的示例：** 调用示例必须可执行，不是伪代码
- **按类型分组：** HTTP/CLI/事件/SDK 的文档结构不同，不能混在一起
```

- [ ] **Step 3: 提交**

```bash
git add plugins/kb/skills/extract-api/
git commit -m "feat(kb): 添加 extract-api skill + 模板"
```

---

## Task 5: extract-data-model skill + 模板

**Files:**
- Create: `plugins/kb/skills/extract-data-model/SKILL.md`
- Create: `plugins/kb/skills/extract-data-model/templates/data-model.md`

- [ ] **Step 1: 编写 data-model 模板**

```markdown
# 数据模型分析模板

每份数据模型文档必须包含以下章节：

## 必含章节

### 1. 实体概述
- 实体名称和用途
- 在业务中的角色

### 2. Schema 定义
- 字段名称、类型、约束（必填/唯一/默认值）
- 嵌套结构（如有）
- 实际 schema 代码片段

### 3. 实体关系
- 与其他实体的关系（一对一/一对多/多对多）
- 外键/引用字段
- Mermaid ER 图

### 4. 状态机
- 实体的生命周期状态（如有）
- 状态转换条件和触发事件
- Mermaid 状态图

### 5. 访问模式
- 主要的读写模式（CRUD 操作分布）
- 高频查询场景
- 缓存策略（如有）

### 6. 约束与验证
- 业务约束（唯一性、范围、格式）
- 验证规则
- 跨字段约束

## 质量要求

- 每个实体至少 1 个 Mermaid 图（ER 图或状态图）
- Schema 必须包含实际代码片段
- 关系必须标注基数（1:1, 1:N, M:N）
```

- [ ] **Step 2: 编写 extract-data-model SKILL.md**

```markdown
---
name: extract-data-model
description: 当需要理解数据实体定义、实体间关系、约束规则、或状态机转换时使用。从数据库 schema、ORM 定义、类型声明中提取完整的数据模型分析文档。
---

# Extract Data Model — 数据模型深度分析

读取结构地图，识别并提取所有数据实体和模型定义。

<HARD-GATE>
`data/raw/<project>/_map.md` 必须存在。如果没有，先调用 scan 技能。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--target <path>` | 是 | - | 目标代码库路径 |
| `--project <name>` | 是 | - | 项目名称 |

## 前置条件

- `data/raw/<project>/_map.md` 必须存在

## 输出

- `data/raw/<project>/data-model/_index.md`
- `data/raw/<project>/data-model/entities/<entity>.md`
- `data/raw/<project>/data-model/state-machines/<state-entity>.md`（有状态实体单独文件）

## 反模式

| 想法 | 问题 |
|------|------|
| "只提取数据库表结构就够了" | ORM 定义、Zod schema、TypeScript 类型都是数据模型的一部分，遗漏它们会导致模型不完整 |
| "状态机可以省略" | 有状态实体是系统最容易出 bug 的地方，状态机文档是数据模型分析的高价值产出 |
| "ER 图和状态图选一个就行" | ER 图描述实体间关系，状态图描述单实体的生命周期，两者回答不同问题 |
| "字段注释从代码复制就行" | 代码注释往往过时或不完整。必须结合业务逻辑重新理解字段含义 |

## 执行流程

1. 读取 `_map.md`，确定分析范围
2. 扫描代码库，识别数据模型定义：
   - 数据库 schema（SQL DDL、ORM model、migration）
   - 配置 schema（JSON schema、Zod、Yup、Joi）
   - TypeScript/Python 类型定义
3. 对每个核心实体，按 `templates/data-model.md` 模板生成深度文档
4. 有复杂状态机的实体，额外产出状态机文档
5. 生成 `data-model/_index.md`（含 ER 总图）

## 模型识别策略

- **SQL：** 搜索 CREATE TABLE、migration 文件
- **ORM：** 搜索 model/Entity 定义（TypeORM、SQLAlchemy、Prisma 等）
- **Schema：** 搜索 Zod/Yup/Joi/JSON schema 定义
- **Type：** 搜索 interface/type/class 定义（排除纯行为接口）

## 关键原则

- **多源交叉验证：** 同一个实体可能同时有 SQL DDL 和 ORM 定义，两者必须一致
- **关系必须标基数：** "用户-订单" 不是关系，"1:N 用户-订单" 才是
- **状态机是重点：** 有状态实体的转换条件必须精确，模糊的状态机比没有更危险
```

- [ ] **Step 3: 提交**

```bash
git add plugins/kb/skills/extract-data-model/
git commit -m "feat(kb): 添加 extract-data-model skill + 模板"
```

---

## Task 6: extract-flows skill + 模板

**Files:**
- Create: `plugins/kb/skills/extract-flows/SKILL.md`
- Create: `plugins/kb/skills/extract-flows/templates/flows.md`

- [ ] **Step 1: 编写 flows 模板**

```markdown
# 业务流程分析模板

每份业务流程文档必须包含以下章节：

## 必含章节

### 1. 业务场景
- 场景名称和描述
- 触发条件（谁在什么情况下发起）
- 业务目标（这个流程要达成什么）

### 2. 功能分解
- 流程由哪些子功能组成
- 子功能之间的层次关系（组合/依赖/顺序）
- Mermaid 功能分解图（树形或层次图）

### 3. 正常流程
- 端到端的完整路径（步骤 1 → 2 → 3 → ...）
- 每步涉及的模块和函数
- Mermaid 序列图

### 4. 异常分支
- 每个可能出错的步骤
- 错误类型和处理方式
- 恢复策略（重试/回滚/降级）
- Mermaid 流程图（含异常分支）

### 5. 性能特征
- 关键路径上的耗时瓶颈
- 并发/串行点
- 数据量敏感点

### 6. 代码证据
- 流程入口函数
- 关键步骤的实现文件
- 错误处理的实现文件

## 质量要求

- 每个流程至少 2 个 Mermaid 图（序列图 + 流程图）
- 功能分解必须体现层次关系，不能是扁平列表
- 异常分支必须覆盖每个可能出错的步骤
- 代码证据必须包含实际文件路径
```

- [ ] **Step 2: 编写 extract-flows SKILL.md**

```markdown
---
name: extract-flows
description: 当需要理解业务场景的端到端流程、功能层次、触发条件、或异常处理策略时使用。从入口文件追踪调用链，提取完整的业务流程分析文档。
---

# Extract Flows — 业务流程与功能层次深度分析

读取结构地图，识别核心业务场景，逐场景产出深度流程分析文档。

<HARD-GATE>
`data/raw/<project>/_map.md` 必须存在。如果没有，先调用 scan 技能。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--target <path>` | 是 | - | 目标代码库路径 |
| `--project <name>` | 是 | - | 项目名称 |
| `--flow <name>` | 否 | 全量 | 只分析指定流程 |

## 前置条件

- `data/raw/<project>/_map.md` 必须存在

## 输出

- `data/raw/<project>/flows/_index.md`
- `data/raw/<project>/flows/<flow>.md`

## 反模式

| 想法 | 问题 |
|------|------|
| "只画正常流程就行，异常大家都知道" | 异常分支是流程最容易出问题的地方，也是新手最需要了解的地方 |
| "功能分解用扁平列表就够了" | 扁平列表看不出组合关系和依赖顺序，层次图才能揭示结构 |
| "性能特征以后再补" | 流程分析的价值在于端到端视角，性能瓶颈是这个视角的独特产出 |
| "从函数名推断流程就够了" | 函数名只反映实现视角。必须从入口追踪调用链，还原业务视角的完整路径 |

## 执行流程

1. 读取 `_map.md`，获取模块清单和入口文件
2. 识别核心业务场景：
   - 从入口文件追踪调用链，识别端到端流程
   - 从模块职责描述推断业务场景
   - 从 API 端点推断业务操作
3. 对每个业务场景：
   a. 追踪端到端调用链
   b. 分解为子功能，建立层次关系
   c. 提取正常流程路径
   d. 识别每个步骤的异常可能和处理方式
   e. 分析性能特征
   f. 收集代码证据
   g. 按 `templates/flows.md` 模板生成深度文档
4. 生成 `flows/_index.md`

## 业务场景识别策略

- **入口驱动：** 从 main/router/handler 追踪调用链
- **API 驱动：** 每个 API 端点对应一个业务操作
- **事件驱动：** 事件发布/订阅对应异步流程
- **配置驱动：** 配置变更触发的流程

## 关键原则

- **从业务视角追踪：** 函数名是实现视角，调用链的起点才是业务入口
- **异常与正常同等重要：** 每个可能出错的步骤都必须有异常分支文档
- **层次优于扁平：** 功能分解图揭示组合关系，扁平列表做不到
- **两个图是底线：** 序列图描述时序，流程图描述分支，缺一个都是不完整的流程分析
```

- [ ] **Step 3: 提交**

```bash
git add plugins/kb/skills/extract-flows/
git commit -m "feat(kb): 添加 extract-flows skill + 模板 — 业务流程与功能层次分析"
```

---

## Task 7: extract-concepts skill + 模板

**Files:**
- Create: `plugins/kb/skills/extract-concepts/SKILL.md`
- Create: `plugins/kb/skills/extract-concepts/templates/concepts.md`

- [ ] **Step 1: 编写 concepts 模板**

```markdown
# 领域概念分析模板

每份概念文档必须包含以下章节：

## 必含章节

### 1. 概念定义
- 概念名称
- 一段话精确定义（不是模糊描述）
- 与日常概念的类比（帮助理解）

### 2. 代码映射
- 这个概念在代码中如何体现
- 对应的类/接口/类型/枚举
- 对应的文件路径

### 3. 概念间关系
- 与其他概念的关系（泛化/组合/依赖/冲突）
- Mermaid 概念关系图

### 4. 使用场景
- 这个概念在哪些业务流程中出现
- 在哪些模块中被使用

### 5. 边界条件
- 这个概念不适用于什么情况
- 与其他概念的边界在哪里

## 质量要求

- 概念定义必须精确，不能是同义反复
- 代码映射必须包含实际文件路径和代码结构
- 概念间关系必须标注关系类型
```

- [ ] **Step 2: 编写 extract-concepts SKILL.md**

```markdown
---
name: extract-concepts
description: 当需要理解代码库的业务领域概念、术语定义、概念间关系、或概念到代码的映射时使用。从命名、类型、枚举、文档中提取领域概念分析文档。
---

# Extract Concepts — 领域概念深度分析

读取结构地图，识别并提取业务领域概念。

<HARD-GATE>
`data/raw/<project>/_map.md` 必须存在。如果没有，先调用 scan 技能。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--target <path>` | 是 | - | 目标代码库路径 |
| `--project <name>` | 是 | - | 项目名称 |

## 前置条件

- `data/raw/<project>/_map.md` 必须存在

## 输出

- `data/raw/<project>/concepts/_index.md`
- `data/raw/<project>/concepts/terms.md`（术语表）
- `data/raw/<project>/concepts/<domain>.md`（每个业务领域一份）

## 反模式

| 想法 | 问题 |
|------|------|
| "概念定义用一句话概括就够了" | "订单就是订单"不是定义。必须精确到能让新人理解概念的含义和边界 |
| "代码映射可以省略" | 没有代码映射的概念文档是纯理论，无法帮助开发者定位实现 |
| "概念间关系不重要" | 关系图是理解领域模型的关键。孤立的定义无法揭示泛化、冲突、依赖 |
| "从 README 复制概念定义就行" | README 的定义往往面向用户，不是面向开发者。必须从代码中验证 |

## 执行流程

1. 读取 `_map.md`，获取模块清单
2. 识别领域概念：
   - 从模块职责描述提取业务术语
   - 从类型/接口名称提取概念
   - 从配置/枚举提取业务分类
   - 从注释/文档提取概念定义
3. 去重和合并：相同概念的不同表述合并
4. 建立概念间关系：泛化、组合、依赖、冲突
5. 生成术语表（所有概念的精确定义）
6. 按业务领域分组，每组按 `templates/concepts.md` 模板生成深度文档
7. 生成 `concepts/_index.md`（含概念关系总图）

## 概念识别策略

- **从命名提取：** 类名、接口名、枚举值、配置键名中的业务术语
- **从文档提取：** README、注释中的概念定义
- **从代码结构提取：** 设计模式、架构风格隐含的概念

## 关键原则

- **定义必须精确：** "X 是管理 Y 的组件" 不是定义，"X 负责 Y 的创建、验证和持久化，但不负责 Y 的路由和展示" 才是
- **代码映射是锚点：** 概念必须能追溯到代码中的具体结构，否则是空中楼阁
- **关系类型必须标注：** "A 和 B 有关系" 没有信息量，"A 组合 B" 或 "A 依赖 B" 才有
```

- [ ] **Step 3: 提交**

```bash
git add plugins/kb/skills/extract-concepts/
git commit -m "feat(kb): 添加 extract-concepts skill + 模板"
```

---

## Task 8: extract 路由 skill

**Files:**
- Create: `plugins/kb/skills/extract/SKILL.md`

- [ ] **Step 1: 编写 extract SKILL.md**

```markdown
---
name: extract
description: 当需要对代码库进行多维度深度分析时使用。路由到具体维度的提取技能，或一键全量提取。scan 的自然后续步骤。
---

# Extract — 提取路由

解析用户意图，分发到具体的维度提取技能。

<HARD-GATE>
如果 `_map.md` 不存在，必须先调用 scan 技能。extract 不负责 scan——它只路由到维度提取技能。
</HARD-GATE>

## 用法

| 命令 | 行为 |
|------|------|
| `extract --target <path> --project <name>` | 全量提取（5 个维度） |
| `extract --target <path> --project <name> --dimension topology` | 只提取拓扑 |
| `extract --target <path> --project <name> --dimension api` | 只提取接口 |
| `extract --target <path> --project <name> --dimension data-model` | 只提取数据模型 |
| `extract --target <path> --project <name> --dimension flows` | 只提取业务流程 |
| `extract --target <path> --project <name> --dimension concepts` | 只提取领域概念 |

## 反模式

| 想法 | 问题 |
|------|------|
| "我直接调用 extract-topology，不需要 extract 路由" | 可以，但 extract 路由帮你处理 scan 前置检查和多维度并发编排 |
| "全量提取太慢了，先做两个维度" | 合理。用 `--dimension` 参数选择需要的维度，后续可以增量补充 |

## 执行流程

1. 如果 `_map.md` 不存在，先调用 `scan` 技能
2. 根据 `--dimension` 参数决定调用哪些技能：
   - `topology` → `extract-topology`
   - `api` → `extract-api`
   - `data-model` → `extract-data-model`
   - `flows` → `extract-flows`
   - `concepts` → `extract-concepts`
   - 不指定 → 全部 5 个
3. 逐个调用对应技能（或并发调用，如果 extract-agent 可用）
4. 汇总结果，报告每个维度的产出文件数量

## 关键原则

- **路由，非实现：** extract 不做提取工作，只做分发和编排
- **前置检查：** scan 是所有维度提取的前提，extract 必须确保它已完成
- **增量友好：** 支持按维度提取，允许分步完成全量分析
```

- [ ] **Step 2: 提交**

```bash
git add plugins/kb/skills/extract/
git commit -m "feat(kb): 添加 extract 路由 skill"
```

---

## Task 9: /kb 命令 + 3 个 agent

**Files:**
- Create: `plugins/kb/commands/kb.md`
- Create: `plugins/kb/agents/kb-agent.md`
- Create: `plugins/kb/agents/extract-agent.md`
- Create: `plugins/kb/agents/transform-agent.md`

- [ ] **Step 1: 编写 /kb 命令**

```markdown
---
name: kb
description: 自动化个人知识库 — 一键 ETL 管道或分步执行
---

# /kb 命令

## 用法

| 子命令 | 行为 |
|--------|------|
| `/kb` | 一键全量管道：scan → extract-all → ingest → cross-ref → serve |
| `/kb scan` | 只做结构梳理 |
| `/kb extract [dimension]` | 提取指定维度（topology/api/data-model/flows/concepts）；不指定则全量 |
| `/kb transform [dimension]` | 转化指定维度的 raw 为 wiki；不指定则全量 |
| `/kb query <question>` | 查询知识库 |
| `/kb lint` | 知识库健康检查 |
| `/kb serve` | 构建 + 启动站点 |

## 执行

调用 `kb-agent`，由 agent 解析参数并分发到对应技能。
```

- [ ] **Step 2: 编写 kb-agent**

```markdown
---
name: kb-agent
model: sonnet
tools: Read, Glob, Grep, Bash, Skill, Write, Edit
---

# KB Agent — 主路由

解析 `/kb` 命令参数，分发到对应技能或子 agent。

## 路由逻辑

| 子命令 | 分发目标 |
|--------|---------|
| （无） | 全量管道：scan → extract-agent → transform-agent → serve |
| `scan` | scan 技能 |
| `extract` | extract-agent |
| `transform` | transform-agent |
| `query` | query 技能 |
| `lint` | lint 技能 |
| `serve` | serve 技能 |

## 全量管道执行

1. 调用 `scan` 技能，产出 `_map.md`
2. 派遣 `extract-agent`，并发提取 5 个维度
3. 派遣 `transform-agent`，全量转化 + 交叉引用
4. 调用 `serve` 技能，构建站点
5. 报告结果：每个阶段的产出数量和耗时
```

- [ ] **Step 3: 编写 extract-agent**

```markdown
---
name: extract-agent
model: sonnet
tools: Read, Glob, Grep, Bash, Skill, Write
---

# Extract Agent — 多维度并行提取

读取 `_map.md`，并发调用多个 extract 技能。

## 执行流程

1. 读取 `data/raw/<project>/_map.md`
2. 确定要提取的维度（由 `--dimension` 参数或默认全量决定）
3. 并发调用对应技能：
   - `extract-topology`
   - `extract-api`
   - `extract-data-model`
   - `extract-flows`
   - `extract-concepts`
4. 等待所有技能完成
5. 汇总结果：每个维度的产出文件数量
```

- [ ] **Step 4: 编写 transform-agent**

```markdown
---
name: transform-agent
model: sonnet
tools: Read, Glob, Grep, Bash, Skill, Write, Edit
---

# Transform Agent — 批量转化

扫描 unprocessed 的 raw 文档，逐个 ingest，最后 cross-ref。

## 执行流程

1. 扫描 `data/raw/<project>/` 下所有 `_index.md`，找到 `status: unprocessed`
2. 对每个 unprocessed 维度，调用 `ingest` 技能
3. 所有维度转化完成后，调用 `cross-ref` 技能
4. 更新 `data/wiki/index.md`、`data/wiki/overview.md`、`data/wiki/log.md`
5. 将已处理的 `_index.md` 标记为 `status: processed`
6. 汇总结果：转化的 wiki 页面数量、交叉引用数量、synthesis 页面数量
```

- [ ] **Step 5: 提交**

```bash
git add plugins/kb/commands/ plugins/kb/agents/
git commit -m "feat(kb): 添加 /kb 命令 + 3 个 agent"
```

---

## Task 10: 更新 CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 在插件列表中添加 kb**

在 CLAUDE.md 的插件表格中添加一行：

```markdown
| **kb** | Skills: scan, extract (路由), extract-topology, extract-api, extract-data-model, extract-flows, extract-concepts. Agents: kb-agent, extract-agent, transform-agent. 命令: /kb. ETL 管道：代码库深度分析 → 结构化知识转化 → 交互式展示 |
```

- [ ] **Step 2: 在安装命令中添加 kb**

在 Installing Plugins 部分添加：

```bash
/plugin install kb
```

- [ ] **Step 3: 提交**

```bash
git add CLAUDE.md
git commit -m "docs: 在 CLAUDE.md 中注册 kb 插件"
```

---

## Task 11: 端到端验证

**Files:** 无新文件，验证已有产出

- [ ] **Step 1: 对 claude-harness 自身运行 scan**

```bash
claude --plugin-dir ./plugins/kb
# 然后执行 /kb scan --target . --project claude-harness
```

预期：`data/raw/claude-harness/_map.md` 生成，包含模块清单、依赖图、分层、入口、复杂度。

- [ ] **Step 2: 对 claude-harness 运行 extract-topology**

```bash
# 执行 /kb extract topology
```

预期：`data/raw/claude-harness/topology/` 下生成每个模块的深度文档。

- [ ] **Step 3: 检查产出格式**

验证：
- `_index.md` 包含正确的 frontmatter（project, dimension, date, status: unprocessed, tags）
- 子文件包含模板定义的必含章节
- Mermaid 图表语法正确
- 文件路径引用准确

- [ ] **Step 4: 提交验证结果**

```bash
git add -A
git commit -m "feat(kb): 端到端验证 — 对 claude-harness 运行 scan + extract-topology"
```
