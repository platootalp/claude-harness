# KB 插件实现计划 — Transform 阶段

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 KB 插件的 Transform 阶段——将 Extract 产出的 raw 文档转化为结构化的 wiki 页面，建立交叉引用，生成 synthesis 页面，维护索引。

**Architecture:** Transform 分三个技能：ingest（单文档转化 raw → wiki）、cross-ref（跨文档关联 + synthesis 生成）、transform（路由）。所有 wiki 页面写入 `data/wiki/projects/<project>/`，通过 frontmatter 的 `sources` 字段追溯到 raw 文档。沿用 wiki 现有的模板体系和命名规范，扩展 projects 层级。

**Tech Stack:** Claude Code plugin（markdown skills/agents），wiki 模板体系（raw-source、page-source、page-entity、page-concept、page-synthesis、page-overview、index-entry、log-entry 共 8 个模板）

**依赖的设计文档：** `docs/superpowers/specs/2026-05-24-kb-plugin-design.md`

**前置条件：** Extract 阶段已完成（`data/raw/<project>/` 下存在 `_map.md` 和维度目录）

---

## 文件结构

### 新建文件

```
plugins/kb/skills/
├── transform/SKILL.md
├── ingest/
│   ├── SKILL.md
│   └── templates/
│       ├── entity.md
│       ├── concept.md
│       └── synthesis.md
└── cross-ref/SKILL.md
```

### 修改文件

```
plugins/kb/data/wiki/index.md       # 增量更新
plugins/kb/data/wiki/overview.md    # 增量更新
plugins/kb/data/wiki/log.md         # 追加记录
```

---

## Task 1: ingest 技能 — entity 模板

**Files:**
- Create: `plugins/kb/skills/ingest/templates/entity.md`

- [ ] **Step 1: 编写 entity 模板**

基于 wiki 现有的 `page-entity.md` 模板，适配 KB 的 projects 层级和多维度来源：

```markdown
---
tags: [{从 raw frontmatter 继承}]
date: {从 raw frontmatter 继承}
last_updated: {从 raw frontmatter 继承}
sources:
  - {raw 文档相对路径，如 topology/modules/spec-workflow.md}
status: stable
page_type: entity
dimension: {topology | api | data-model}  # entity 只来自这三个维度
project: {项目名}
---

# {实体名称}

## 摘要

（100-150 字，概括实体的职责、在系统中的位置、核心特征）

## 关键领域

### 概述
（定义：这个实体是什么。示例：一个典型使用场景。边界：什么情况不属于这个实体）

### {领域 1 — 从 raw 文档中提取的核心职责域}
（定义 + 示例 + 边界条件，150-300 字）

### {领域 2}
（同上）

### {领域 N}
（同上，领域数量取决于 raw 文档的复杂度）

## 依赖关系

### 上游
- 依赖哪些实体，通过什么接口

### 下游
- 被哪些实体依赖，提供什么接口

## 内部结构
（子组件组成，如果实体有内部模块）

## 代码证据
- `{关键文件路径}` — {作用说明}
- `{入口文件路径}` — {作用说明}

## 另见
- [{关联实体名}](../entities/{name}.md) — {关系说明}
- [{关联概念名}](../concepts/{name}.md) — {关系说明}
- ← 来源：[{raw 文档名}](../../raw/{dimension}/modules/{name}.md)

<!-- 质量检查：
- 摘要在 100-150 字之间
- 每个关键领域有定义+示例+边界
- 另见至少 2 个链接
- 代码证据包含实际文件路径
-->
```

- [ ] **Step 2: 提交**

```bash
git add plugins/kb/skills/ingest/templates/entity.md
git commit -m "feat(kb): 添加 entity wiki 页面模板"
```

---

## Task 2: ingest 技能 — concept 模板

**Files:**
- Create: `plugins/kb/skills/ingest/templates/concept.md`

- [ ] **Step 1: 编写 concept 模板**

基于 wiki 现有的 `page-concept.md` 模板，适配 KB 的 flows/concepts 维度：

```markdown
---
tags: [{从 raw frontmatter 继承}]
date: {从 raw frontmatter 继承}
last_updated: {从 raw frontmatter 继承}
sources:
  - {raw 文档相对路径}
status: stable
page_type: concept
dimension: {flows | concepts}  # concept 只来自这两个维度
project: {项目名}
---

# {概念名称}

## 摘要

（100-150 字，概括概念的定义、参与实体、核心行为）

## 核心思想

（200-400 字，详细阐述这个概念是什么、为什么存在、如何运作）

## 参与实体

- [{实体名}](../entities/{name}.md) — {这个实体在概念中的角色}

## 应用场景

### 场景 1：{典型应用}
（描述在什么情况下这个概念被触发，如何执行）

### 场景 2：{另一应用}
（同上，至少 2 个场景）

## 权衡

| 优势 | 劣势 |
|------|------|
| {优势 1} | {劣势 1} |
| {优势 2} | {劣势 2} |

局限：{这个概念不适用于什么情况}
替代方案：{如果不用这个概念，还有什么选择}

## 生命周期

（概念从触发到完成的完整过程，如果适用）

## 边界条件

- {什么情况下这个概念不成立}
- {与其他概念的冲突点}

## 另见
- [{关联概念名}](../concepts/{name}.md) — {关系说明}
- [{关联实体名}](../entities/{name}.md) — {关系说明}
- ← 来源：[{raw 文档名}](../../raw/{dimension}/{name}.md)

<!-- 质量检查：
- 摘要在 100-150 字之间
- 核心思想在 200-400 字之间
- 参与实体至少 1 个（链接到 entity 页面）
- 应用场景至少 2 个
- 另见至少 2 个链接
-->
```

- [ ] **Step 2: 提交**

```bash
git add plugins/kb/skills/ingest/templates/concept.md
git commit -m "feat(kb): 添加 concept wiki 页面模板"
```

---

## Task 3: ingest 技能 — synthesis 模板

**Files:**
- Create: `plugins/kb/skills/ingest/templates/synthesis.md`

- [ ] **Step 1: 编写 synthesis 模板**

基于 wiki 现有的 `page-synthesis.md` 模板，适配 KB 的跨维度综合：

```markdown
---
tags: [{从关联页面继承}]
date: {生成日期}
last_updated: {生成日期}
sources:
  - {参与综合的 raw 文档路径 1}
  - {参与综合的 raw 文档路径 2}
status: stable
page_type: synthesis
synthesis_type: {comparison | analysis | connection}
project: {项目名}
---

# {综合标题}

## 摘要

（100-150 字，概括这个横切关注点涉及哪些实体/概念，核心发现是什么）

## 分析

{synthesis_type=comparison 时：对比表格 + 关键差异分析}
{synthesis_type=analysis 时：深层原因分析 + 证据链}
{synthesis_type=connection 时：关联链路说明 + 影响范围}

## 相关实体

- [{实体名}](../entities/{name}.md) — {在这个横切关注点中的角色}

## 相关概念

- [{概念名}](../concepts/{name}.md) — {在这个横切关注点中的角色}

## 影响

建议：{基于分析给出的行动建议}
疑问：{需要进一步调查的问题}

## 另见
- [{关联页面}](../{type-dir}/{name}.md) — {关系说明}

<!-- 质量检查：
- 摘要在 100-150 字之间
- 分析结构匹配 synthesis_type
- 至少涉及 2 个不同维度的实体/概念
- 另见至少 2 个链接
-->
```

- [ ] **Step 2: 提交**

```bash
git add plugins/kb/skills/ingest/templates/synthesis.md
git commit -m "feat(kb): 添加 synthesis wiki 页面模板"
```

---

## Task 4: ingest 技能

**Files:**
- Create: `plugins/kb/skills/ingest/SKILL.md`

- [ ] **Step 1: 编写 ingest SKILL.md**

```markdown
---
name: ingest
description: 当需要将 Extract 产出的 raw 分析文档转化为结构化 wiki 页面时使用。单维度/单文档转化，按转化映射决定目标页面类型。
---

# Ingest — Raw → Wiki 页面转化

读取 raw 文档，按转化映射生成对应类型的 wiki 页面。

<HARD-GATE>
至少一个维度的 `_index.md` 状态为 `unprocessed`，且 `data/raw/<project>/_map.md` 存在。如果所有维度已 processed，ingest 无事可做。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--project <name>` | 是 | - | 项目名称 |
| `--dimension <name>` | 否 | 所有 unprocessed | 只转化指定维度 |

## 输出

- `data/wiki/projects/<project>/entities/<name>.md`
- `data/wiki/projects/<project>/concepts/<name>.md`
- 更新 `data/wiki/projects/<project>/overview.md`
- 追加 `data/wiki/log.md`

## 转化映射

| raw 来源 | wiki 页面类型 | 模板 |
|----------|-------------|------|
| topology/modules/*.md | entity | templates/entity.md |
| api/**/*.md | entity | templates/entity.md |
| data-model/entities/*.md | entity | templates/entity.md |
| flows/*.md | concept | templates/concept.md |
| concepts/*.md | concept | templates/concept.md |

## 反模式

| 想法 | 问题 |
|------|------|
| "raw 文档已经很好了，直接复制到 wiki 就行" | raw 是分析产出，wiki 是知识产出。两者受众和目的不同——raw 给 extract 技能用，wiki 给人用 |
| "我先转化所有维度，再处理交叉引用" | 正确。cross-ref 是独立的技能，ingest 只负责单文档转化 |
| "如果一个 raw 文档映射到多个 wiki 页面怎么办" | 不会。转化映射是一对一的，每个 raw 文档只生成一个 wiki 页面 |
| "wiki frontmatter 的 sources 可以省略" | sources 是 raw → wiki 的追溯锚点。没有它，用户无法从 wiki 页面回到原始分析 |
| "交叉引用应该在 ingest 阶段就做好" | 错。ingest 只添加与**已有** wiki 页面的交叉引用。跨维度 synthesis 由 cross-ref 技能负责 |

## 执行流程

1. 读取 `data/config.json`，解析 dataDir
2. 扫描 `data/raw/<project>/` 下所有 `_index.md`，找到 `status: unprocessed`
3. 如果指定了 `--dimension`，只处理该维度；否则处理所有 unprocessed 维度
4. 对每个 unprocessed 维度的 raw 文档：
   a. 确定目标 wiki 页面类型（查转化映射表）
   b. 读取 raw 文档全部内容
   c. 读取对应模板，按模板的必含章节和质量要求生成 wiki 页面
   d. 从 raw frontmatter 继承 tags、date
   e. 设置 wiki frontmatter：page_type、dimension、project、sources（指向 raw 路径）
   f. 写入 `data/wiki/projects/<project>/{entities|concepts}/<name>.md`
   g. 添加与已有 wiki 页面的交叉引用链接（写入"另见"章节）
5. 更新 `data/wiki/projects/<project>/overview.md`：
   - Domains 章节按维度更新覆盖描述
   - Recent Activity 追加本次操作记录
6. 将已处理的 `_index.md` 标记为 `status: processed`

## 交叉引用生成（ingest 阶段）

在 ingest 阶段，为每个新 wiki 页面添加与**已有** wiki 页面的交叉引用：

1. 扫描新页面中提到的实体/概念名称
2. 在已有 wiki 页面中查找同名实体/概念
3. 在双方的"另见"章节添加互相链接

注意：跨维度的 synthesis 页面不在 ingest 阶段生成，由 cross-ref 技能负责。

## Frontmatter 规范

所有 wiki 页面使用以下 frontmatter 字段：

| 字段 | 必填 | 说明 |
|------|------|------|
| tags | 是 | 从 raw 继承 |
| date | 是 | 从 raw 继承 |
| last_updated | 是 | 初始等于 date，后续每次编辑更新 |
| sources | 是 | 指向 raw 文档的相对路径数组 |
| status | 是 | draft / stable / needs-update |
| page_type | 是 | entity / concept / synthesis |
| dimension | 是 | topology / api / data-model / flows / concepts |
| project | 是 | 项目名 |

## 命名规范

- 文件名：kebab-case
- 同一实体/概念只对应一个 wiki 页面
- 被替代的旧页面标记 `needs-update`，不删除
- 路径格式：`data/wiki/projects/<project>/{entities|concepts}/<name>.md`

## 关键原则

- **一对一转化：** 每个 raw 文档生成一个 wiki 页面，不拆分不合并
- **追溯锚点：** sources 字段是不可省略的，它连接 raw 和 wiki
- **增量交叉引用：** ingest 只处理与已有页面的引用，不生成 synthesis
- **幂等性：** 重复运行 ingest 不会重复生成已 processed 的维度
```

- [ ] **Step 2: 提交**

```bash
git add plugins/kb/skills/ingest/
git commit -m "feat(kb): 添加 ingest skill + wiki 页面模板"
```

---

## Task 5: cross-ref 技能

**Files:**
- Create: `plugins/kb/skills/cross-ref/SKILL.md`

- [ ] **Step 1: 编写 cross-ref SKILL.md**

```markdown
---
name: cross-ref
description: 当需要发现 wiki 页面间跨维度关联、补充交叉引用、或生成综合分析页面时使用。扫描已有 wiki 页面，通过四种信号发现关系。
---

# Cross-Ref — 跨文档关联与综合

扫描 wiki 页面，通过四种信号发现跨维度关联，补充交叉引用，生成 synthesis 页面。

<HARD-GATE>
至少有两个不同维度的 wiki 页面存在。如果只有一个维度，无法产生跨维度关联，cross-ref 无事可做。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--project <name>` | 是 | - | 项目名称 |

## 前置条件

- `data/wiki/projects/<project>/` 下存在 wiki 页面
- 至少有两个不同维度的 wiki 页面

## 输出

- 更新 wiki 页面的"另见"章节（添加跨维度链接）
- `data/wiki/projects/<project>/syntheses/<name>.md`（新增 synthesis 页面）

## 关联发现规则

cross-ref 通过以下四种信号发现 wiki 页面之间的关系：

1. **名称重叠：** 实体或概念互相引用对方名称（如 entity "auth-module" 在 concept "login-flow" 中被提及）
2. **共享代码路径：** 两个页面的 sources 字段引用了相同的 raw 文档
3. **父子关系：** 实体是其他实体的子组件（如 API 组属于某个模块）
4. **流程参与：** 一个概念（流程）涉及多个 entity——每个 entity 获得反向引用

## 反模式

| 想法 | 问题 |
|------|------|
| "两个页面有链接就够了，不需要 synthesis" | 如果只有 2 个页面的双向引用，确实不需要 synthesis。但 3+ 页面的关联链是横切关注点，值得单独分析 |
| "synthesis 只是重复已有页面的内容" | synthesis 的价值在于**跨维度视角**——揭示单维度分析看不到的模式和冲突 |
| "四种信号都要匹配才能创建关联" | 不需要。共享至少一个信号且跨维度即可 |
| "同维度内的关联也要生成 synthesis" | 不需要。同维度内的关联只需在"另见"中添加链接，不需要单独的 synthesis 页面 |

## 执行流程

1. 读取 `data/wiki/projects/<project>/` 下所有 wiki 页面
2. 对每对页面，检查四种信号是否匹配
3. 如果两个页面共享至少一个信号，且**跨越维度**（dimension 不同）：
   a. 在双方的"另见"章节添加互相链接
   b. 判断是否需要生成 synthesis 页面：
      - 关系涉及 3 个以上页面的关联链 → 生成 synthesis
      - 简单的双向引用（只有 2 个页面） → 只添加交叉引用，不生成 synthesis
4. 对每个需要生成 synthesis 的关联组：
   a. 确定横切关注点的主题（如"认证链路" = auth-module(entity) + login-flow(concept)）
   b. 确定关联涉及的维度和页面列表
   c. 按 `ingest/templates/synthesis.md` 模板生成 synthesis 页面
   d. synthesis 的 sources 设为关联页面列表
   e. 写入 `data/wiki/projects/<project>/syntheses/<name>.md`
5. 更新 `data/wiki/projects/<project>/overview.md`（Active Questions + Recent Activity）
6. 追加 `data/wiki/log.md`

## 父子关系推断

推断实体间父子关系的策略：

- 如果 entity A 的"内部结构"章节包含了 entity B 的名称 → B 是 A 的子组件
- 如果 api 组的维度是 api，但名称中包含某个 topology-module 的前缀 → 该 api 组属于该模块
- 如果 data-model 实体的名称中包含某个 topology-module 的前缀 → 该数据实体属于该模块

## Synthesis 页面命名

- 格式：`{维度1}-{维度2}-{关注点}.md`
- 示例：`topology-flows-auth-chain.md`
- kebab-case

## 关键原则

- **跨维度是门槛：** 同维度内的关联只用"另见"链接，不生成 synthesis
- **3+ 页面才 synthesis：** 简单的双向引用不值得单独页面，3+ 页面的关联链才是横切关注点
- **四种信号互斥又互补：** 任何一个信号匹配即可创建关联，多个信号匹配则关联更强
- **synthesis 有独特价值：** 不是重复内容，而是提供跨维度视角
```

- [ ] **Step 2: 提交**

```bash
git add plugins/kb/skills/cross-ref/
git commit -m "feat(kb): 添加 cross-ref skill — 跨文档关联与综合"
```

---

## Task 6: transform 路由技能

**Files:**
- Create: `plugins/kb/skills/transform/SKILL.md`

- [ ] **Step 1: 编写 transform SKILL.md**

```markdown
---
name: transform
description: 当需要将 raw 文档批量转化为 wiki 页面、发现跨维度关联、或一键全量转化时使用。分发到 ingest 或 cross-ref，支持增量或全量。
---

# Transform — 转化路由

解析用户意图，分发到 ingest 或 cross-ref 技能。

<HARD-GATE>
如果没有任何 unprocessed 的 raw 文档且不是 `--cross-ref-only` 模式，transform 无事可做。告知用户所有维度已 processed。
</HARD-GATE>

## 用法

| 命令 | 行为 |
|------|------|
| `transform --project <name>` | 全量转化：先 ingest 所有 unprocessed 维度，再 cross-ref |
| `transform --project <name> --dimension <name>` | 只转化指定维度 |
| `transform --project <name> --cross-ref-only` | 只运行交叉引用发现 |

## 反模式

| 想法 | 问题 |
|------|------|
| "我直接调用 ingest，不需要 transform 路由" | 可以，但 transform 帮你处理 ingest + cross-ref 的编排，确保两者都执行 |
| "transform 应该也负责 query 和 lint" | 不。query 和 lint 是独立的技能，不在 Transform 阶段内 |

## 执行流程

1. 如果不是 `--cross-ref-only`，调用 `ingest` 技能：
   - 传入 `--project` 和可选的 `--dimension`
   - 等待 ingest 完成
2. 调用 `cross-ref` 技能：
   - 传入 `--project`
   - 等待 cross-ref 完成
3. 汇总结果：报告转化的 wiki 页面数量、新增交叉引用数量、新增 synthesis 页面数量

## 关键原则

- **路由，非实现：** transform 不做转化工作，只做分发和编排
- **先 ingest 后 cross-ref：** 顺序不可颠倒，cross-ref 依赖 wiki 页面存在
- **增量友好：** 支持按维度转化，允许分步完成全量转化
```

- [ ] **Step 2: 提交**

```bash
git add plugins/kb/skills/transform/
git commit -m "feat(kb): 添加 transform 路由 skill"
```

---

## Task 7: wiki 数据目录初始化

**Files:**
- Create: `plugins/kb/data/wiki/index.md`
- Create: `plugins/kb/data/wiki/overview.md`
- Create: `plugins/kb/data/wiki/log.md`
- Create: `plugins/kb/data/wiki/projects/.gitkeep`

- [ ] **Step 1: 创建 index.md**

```markdown
---
tags: [index]
date: 2026-05-24
status: stable
page_type: index
---

# 知识库目录

## 实体
（暂无）

## 概念
（暂无）

## 综合
（暂无）
```

- [ ] **Step 2: 创建 overview.md**

```markdown
---
tags: [overview]
date: 2026-05-24
last_updated: 2026-05-24
status: stable
page_type: overview
---

# 知识库概览

## 摘要

KB 知识库目前尚未包含任何项目的分析结果。使用 `/kb` 命令开始提取。

## 领域
（暂无项目）

## 活跃问题
- 如何将新项目加入知识库？

## 最近活动
- 2026-05-24 — 知识库初始化

## 另见
（暂无）
```

- [ ] **Step 3: 创建 log.md**

```markdown
# 知识库活动日志

## [2026-05-24] 初始化 | KB 知识库
```

- [ ] **Step 4: 创建 projects/.gitkeep**

```bash
mkdir -p plugins/kb/data/wiki/projects
touch plugins/kb/data/wiki/projects/.gitkeep
```

- [ ] **Step 5: 提交**

```bash
git add plugins/kb/data/wiki/
git commit -m "feat(kb): 初始化 wiki 数据目录"
```

---

## Task 8: 端到端验证

**前置条件：** Extract 阶段已产出 raw 文档（`data/raw/claude-harness/` 下有维度目录）

- [ ] **Step 1: 对 claude-harness 运行 ingest**

```bash
claude --plugin-dir ./plugins/kb
# 执行 /kb transform --project claude-harness --dimension topology
```

预期：
- `data/wiki/projects/claude-harness/entities/` 下生成 entity 页面
- 页面包含模板定义的必含章节
- frontmatter 字段完整（tags、date、sources、status、page_type、dimension、project）
- "另见"章节包含与已有页面的交叉引用

- [ ] **Step 2: 对 claude-harness 运行 cross-ref**

```bash
# 执行 /kb transform --project claude-harness --cross-ref-only
```

预期：
- 跨维度的 wiki 页面间新增交叉引用
- 如果存在 3+ 页面关联链，生成 synthesis 页面
- overview.md 更新
- log.md 追加记录

- [ ] **Step 3: 检查产出质量**

验证：
- entity 页面：摘要 100-150 字，关键领域有定义+示例+边界，代码证据包含实际路径
- concept 页面：摘要 100-150 字，核心思想 200-400 字，参与实体有链接
- synthesis 页面：涉及至少 2 个不同维度，分析结构匹配 synthesis_type
- 交叉引用：双向链接正确，路径使用相对路径格式

- [ ] **Step 4: 提交验证结果**

```bash
git add -A
git commit -m "feat(kb): Transform 阶段端到端验证 — 对 claude-harness 运行 ingest + cross-ref"
```