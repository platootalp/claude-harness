# KB 插件设计 — 自动化个人知识库

## 概述

一个全新插件（`kb`），将 `analysis` 和 `wiki` 的能力合并为 ETL 管道架构，构建自动化个人知识库，以代码库理解为核心。

**ETL 管道：**

```
Extract（代码库分析）→ Transform（结构化知识）→ Load/Present（站点 + 图谱）
```

- **Extract**：扫描代码库，按多个维度产出深度分析文档
- **Transform**：将原始分析转化为结构化、交叉引用的 wiki 页面
- **Load/Present**：通过可搜索的 Astro 站点 + 知识图谱可视化呈现所有内容

## 设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 架构 | ETL 管道 | 阶段通过文件系统解耦；支持一键自动化和细粒度控制 |
| 核心方向 | 代码库理解 | Extract 专为代码分析优化；其他来源是未来扩展 |
| Extract 阶段 | 两阶段：结构梳理 → 深度分析 | 结构地图指导深度提取；没有"概览"模式——所有产出都是深度文档 |
| 提取维度 | 5 个正交维度 | topology、api、data-model、flows、concepts——每个维度是单一职责 skill |
| 身份 | 新插件 | 不是 analysis 或 wiki 的升级版；全新架构 |
| 运行模式 | 双模式 | Claude Code 插件（斜杠命令 + agent）+ 独立运行（Astro 站点） |
| 展示层 | 复用 + 增强 Astro 站点 | 三个视图：Raw 文档、Wiki 页面、知识图谱 |

---

## 阶段 1：Extract

### 两阶段设计

**阶段 1 — 结构梳理**（`scan` skill）

扫描代码库，产出结构地图（`_map.md`），作为阶段 2 的路线图。这不是给用户看的文档，而是给后续提取 skill 用的分析指引。

产出：`data/raw/<project>/_map.md`

结构地图内容：
- 模块清单（路径、一句话职责、主要语言/框架、文件数量、对外接口数量）
- 依赖关系图（模块间 import/call 边，带方向）
- 架构分层（哪些模块属于哪层，层间依赖规则，违规情况）
- 入口识别（main、router、config、index 文件——新读者应该先看什么）
- 复杂度指标（按文件数量、依赖扇出、耦合度排名的模块列表）

**阶段 2 — 深度分析**（5 个维度 skill）

每个 skill 读取 `_map.md` 确定分析范围，然后逐模块/逐流程/逐实体产出深度分析文档。没有概览模式——所有产出都是深入的。

| Skill | 维度 | 分析内容 | 产出目录 |
|-------|------|---------|---------|
| `extract-topology` | topology | 模块内部结构、职责边界、上下游交互方式 | `data/raw/<project>/topology/` |
| `extract-api` | api | 完整 API 契约、参数、返回值、错误处理、调用示例 | `data/raw/<project>/api/` |
| `extract-data-model` | data-model | 实体 schema、关系、约束、状态机、访问模式 | `data/raw/<project>/data-model/` |
| `extract-flows` | flows | 业务流程与功能层次：识别核心业务场景，提取每个场景的端到端流程、功能分解、层次关系、触发条件、异常分支 | `data/raw/<project>/flows/` |
| `extract-concepts` | concepts | 领域概念定义、代码映射、概念间关系 | `data/raw/<project>/concepts/` |

**路由 skill**：`extract`——分发到具体维度 skill；支持 `--all` 全量提取。

### 产出目录结构

```
data/raw/<project>/
├── _map.md                              # 结构地图（阶段 1 产出）
├── topology/
│   ├── _index.md                        # 带 frontmatter 的索引
│   └── modules/
│       ├── <module-a>.md               # 每个模块一份深度文档
│       └── <module-b>.md
├── api/
│   ├── _index.md
│   ├── http/
│   │   ├── <resource-a>.md
│   │   └── <resource-b>.md
│   ├── cli/
│   │   └── <command-group>.md
│   └── events/
│       └── <event-type>.md
├── data-model/
│   ├── _index.md
│   ├── entities/
│   │   └── <entity>.md
│   └── state-machines/
│       └── <state-entity>.md
├── flows/
│   ├── _index.md
│   ├── <flow-a>.md                   # 端到端业务流程
│   ├── <flow-b>.md
│   └── <flow-c>.md                   # 每个流程包含功能分解和层次关系
└── concepts/
    ├── _index.md
    ├── terms.md
    └── <domain>.md
```

文件数量随代码库规模自然增长。模板定义每个维度必须包含的章节，不限制文件数量。

### Frontmatter

只有 `_index.md` 携带 frontmatter。子文件从父级继承上下文。

```yaml
---
project: claude-harness
dimension: topology
date: 2026-05-24
status: unprocessed
tags: [plugins, marketplace]
---
```

| 字段 | 用途 |
|------|------|
| `project` | 标识这份分析属于哪个项目 |
| `dimension` | 提取维度；Transform 根据此字段路由到对应的 wiki 页面类型 |
| `date` | 提取时间戳；用于过期检测和日志 |
| `status` | `unprocessed` / `processed`；Transform 扫描 unprocessed 的文档并在消费后标记为 processed |
| `tags` | 语义标签，用于分类和查询 |

### 现有 Analysis Skill 映射

| 现有 skill | 新 skill | 变化 |
|-----------|---------|------|
| `codebase-analysis` | `extract`（路由） | 重命名，管道感知 |
| `codebase-to-docs` | 拆分为 `extract-topology` + `extract-flows` | 双轴（架构 + 流程）拆为两个独立 skill |
| `system-architecture-analysis` | 合入 `extract-topology` | C4 模型成为 topology 的子模板 |
| `source-functional-analysis` | `extract-flows` | 重命名，聚焦业务流程与功能层次分析 |
| `deep-functional-analysis` | `extract-topology`（深度模块分析） | 作为 topology 的逐模块深度分析 |
| （无） | `extract-api` | 新增 |
| （无） | `extract-data-model` | 新增 |
| （无） | `extract-concepts` | 新增 |

---

## 阶段 2：Transform

### Skill 设计

| Skill | 职责 |
|-------|------|
| `transform` | 路由：分发到 ingest 或 cross-ref |
| `ingest` | 单维度/单文档转化：raw → wiki 页面 |
| `cross-ref` | 跨文档关联：补充交叉引用 + 生成 synthesis 页面 |
| `lint` | 知识库健康检查 |
| `query` | 知识库查询与综合 |

### 转化映射

| Extract 维度 | Wiki 页面类型 | 理由 |
|-------------|--------------|------|
| topology/modules/* | entity | 每个模块是一个实体 |
| api/* | entity | 每个接口组是一个实体 |
| data-model/entities/* | entity | 每个数据实体是一个实体 |
| flows/* | concept | 每个流程是一个概念（跨实体的行为模式） |
| concepts/* | concept | 每个领域概念是一个概念 |
| 跨维度综合 | synthesis | 发现跨维度关联时自动生成 |

### 交叉引用发现规则

`cross-ref` 通过以下信号发现 wiki 页面之间的关系：

1. **名称重叠**：实体或概念互相引用对方名称（如 entity 页面 "auth-module" 在 concept 页面 "login-flow" 中被提及）
2. **共享代码路径**：两个页面引用了相同的源文件或函数
3. **父子关系**：实体是其他实体的子组件（如 API 组属于某个模块）
4. **流程参与**：一个概念（流程）涉及多个实体——每个实体获得反向引用

当两个或以上页面共享至少一个信号时，`cross-ref` 创建双向链接；如果关系跨越维度，则生成一个 synthesis 页面总结这个横切关注点。

### Transform 执行流程

1. 扫描 `data/raw/<project>/` 下所有 `_index.md`，找到 `status: unprocessed`
2. 按维度读取所有深度分析文档
3. 对每份文档：确定目标 wiki 页面类型，按模板生成页面（entity 页面：职责、接口、依赖、内部结构、代码证据；concept 页面：定义、参与实体、生命周期、边界条件；synthesis 页面：横切关注点、相关实体/概念、影响），写入 `data/wiki/`，添加与已有 wiki 页面的交叉引用
4. 扫描所有新页面，发现跨维度关联，生成 synthesis 页面
5. 更新 `data/wiki/index.md`、`data/wiki/overview.md`、`data/wiki/log.md`
6. 将已处理的 `_index.md` 的 `status` 改为 `processed`

### Wiki 数据结构

```
data/wiki/
├── index.md                    # 内容目录
├── overview.md                 # 跨项目综合概览
├── log.md                      # 活动日志
├── projects/
│   └── <project>/
│       ├── overview.md         # 项目级概览
│       ├── entities/           # 实体页面
│       │   ├── <module>.md
│       │   ├── <api-group>.md
│       │   └── <data-entity>.md
│       ├── concepts/           # 概念页面
│       │   ├── <flow>.md
│       │   └── <domain-concept>.md
│       └── syntheses/          # 综合页面
│           └── <cross-dimension>.md
└── cross-project/              # 跨项目综合
    └── <synthesis>.md
```

相比现有 wiki 的关键变化：增加了 `projects/` 层级，因为知识库可能包含多个项目的分析结果。

---

## 阶段 3：Load/Present

### 整体架构

站点基于 Astro 6 + React 18 + Tailwind 3，从 analysis 现有站点增强而来。核心变化：

1. 内容源从单一 `docs/` 目录扩展为 `data/raw/` + `data/wiki/` 两个内容集合
2. 页面路由从单层 `/docs/[slug]` 扩展为多项目、多视图的路由体系
3. 新增知识图谱可视化（力导向图）
4. 新增项目切换、维度筛选等交互组件

### 内容集合

两个 Astro content collection，分别加载 raw 和 wiki 内容：

**`raw` 集合**：加载 `data/raw/<project>/` 下所有 markdown（排除 `_map.md`）

```typescript
// content.config.ts
const raw = defineCollection({
  loader: glob({ pattern: '**/*.md', base: RAW_ROOT }),
  schema: z.object({
    project: z.string(),
    dimension: z.enum(['topology', 'api', 'data-model', 'flows', 'concepts']),
    date: z.string(),
    status: z.enum(['unprocessed', 'processed']),
    tags: z.array(z.string()).optional(),
  }),
});
```

**`wiki` 集合**：加载 `data/wiki/projects/<project>/` 下所有 markdown

```typescript
const wiki = defineCollection({
  loader: glob({ pattern: '**/*.md', base: WIKI_ROOT }),
  schema: z.object({
    page_type: z.enum(['entity', 'concept', 'synthesis']),
    dimension: z.enum(['topology', 'api', 'data-model', 'flows', 'concepts']).optional(),
    project: z.string(),
    tags: z.array(z.string()).optional(),
    sources: z.array(z.string()).optional(),  // 指向 raw 文档的路径
    date: z.string(),
    last_updated: z.string(),
  }),
});
```

**图谱数据**：`build-graph` skill 产出的 `data/graph.json`，在构建时复制到 `public/graph.json`，运行时由 `KnowledgeGraph.tsx` 加载。

```typescript
// graph.json 结构
{
  nodes: Array<{
    id: string;           // wiki 页面路径
    label: string;        // 页面标题
    type: 'entity' | 'concept' | 'synthesis';
    dimension?: string;   // 来自哪个 extract 维度
    project: string;
    summary: string;      // 一句话摘要，用于悬浮卡片
  }>;
  edges: Array<{
    source: string;       // 节点 id
    target: string;       // 节点 id
    signal: 'name-overlap' | 'shared-code' | 'parent-child' | 'flow-participation';
  }>;
}
```

### 路由体系

```
/                                   → 全局首页（项目卡片列表）
/projects/[project]                 → 项目首页（三视图入口 + 统计）
/projects/[project]/raw             → Raw 视图总览
/projects/[project]/raw/[...slug]   → Raw 文档详情
/projects/[project]/wiki            → Wiki 视图总览
/projects/[project]/wiki/[...slug]  → Wiki 页面详情
/projects/[project]/graph           → 知识图谱
/search                             → 全局搜索
/sitemap.xml                        → 站点地图
/404                                → 404 页
```

### 全局首页

**页面**：`/src/pages/index.astro`

**布局**：不使用 DocLayout，使用独立的 `HomeLayout.astro`（无侧边栏，全宽内容区）

**内容结构**：

```
┌──────────────────────────────────────────────────────┐
│  TopNav（项目切换器 + 搜索 + 主题切换）                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  KB — 自动化个人知识库                                │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │ claude-    │  │ another-   │  │ third-     │    │
│  │ harness    │  │ project    │  │ project    │    │
│  │            │  │            │  │            │    │
│  │ 23 raw     │  │ 15 raw    │  │ 8 raw      │    │
│  │ 15 wiki    │  │ 10 wiki   │  │ 6 wiki     │    │
│  │ 5 dims     │  │ 5 dims    │  │ 3 dims     │    │
│  │            │  │            │  │            │    │
│  │ 最近更新:  │  │ 最近更新:  │  │ 最近更新:  │    │
│  │ 2026-05-24│  │ 2026-05-20│  │ 2026-05-15│    │
│  │            │  │            │  │            │    │
│  │ [进入]     │  │ [进入]     │  │ [进入]     │    │
│  └────────────┘  └────────────┘  └────────────┘    │
│                                                      │
│  最近活动                                            │
│  • claude-harness: topology 提取完成 — 05-24         │
│  • claude-harness: api 提取完成 — 05-24              │
│  • another-project: 全量转化完成 — 05-20             │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**数据来源**：
- 项目列表：扫描 `data/raw/` 下的子目录
- 每个项目的统计：从 `raw` 和 `wiki` 集合中按 `project` 字段过滤计数
- 最近活动：从 `data/wiki/log.md` 解析最近 N 条记录

### 项目首页

**页面**：`/src/pages/projects/[project]/index.astro`

**布局**：`DocLayout.astro`（侧边栏显示项目导航树）

**内容结构**：

```
┌──────────────────────────────────────────────────────┐
│  TopNav（面包屑: KB / claude-harness）                │
├──────────┬───────────────────────────────────────────┤
│ Sidebar  │                                           │
│          │  claude-harness                            │
│ ▸ Raw    │                                           │
│ ▸ Wiki   │  ┌──────────┬──────────┬──────────┐      │
│ ▸ Graph  │  │ Raw Docs │  Wiki    │  Graph   │      │
│          │  │          │  Pages   │          │      │
│          │  │ 23 docs  │  15 pages│  45 nodes│      │
│          │  │ 5 dims   │  3 types │  67 edges│      │
│          │  │          │          │          │      │
│          │  │ [浏览]   │  [浏览]  │  [探索]  │      │
│          │  └──────────┴──────────┴──────────┘      │
│          │                                           │
│          │  维度覆盖                                  │
│          │  ┌─────────────────────────────────┐      │
│          │  │ topology ████████████ 6 docs    │      │
│          │  │ api       ██████████   5 docs   │      │
│          │  │ data-model ██████     4 docs    │      │
│          │  │ flows     ████████████ 5 docs   │      │
│          │  │ concepts  ████        3 docs    │      │
│          │  └─────────────────────────────────┘      │
│          │                                           │
│          │  最近活动                                  │
│          │  • topology 提取完成 — 2026-05-24          │
│          │  • api 提取完成 — 2026-05-24               │
│          │  • wiki 转化完成 — 2026-05-24              │
│          └───────────────────────────────────────────┘
```

**侧边栏**：项目级导航树，固定三组：Raw、Wiki、Graph，点击进入对应视图。

### Raw 视图

#### 总览页

**页面**：`/src/pages/projects/[project]/raw/index.astro`

**布局**：`DocLayout.astro`

**内容结构**：

```
┌──────────┬───────────────────────────────────────────┐
│ Sidebar  │  Raw 文档 — claude-harness                  │
│          │                                           │
│ ▾ Raw    │  ┌─ topology ──────────────────────┐      │
│   ▸ topo │  │ 6 docs · 最近更新 2026-05-24     │      │
│   ▸ api  │  │                                  │      │
│   ▸ data │  │  • modules/spec-workflow.md      │      │
│   ▸ flows│  │  • modules/analysis.md           │      │
│   ▸ conc │  │  • modules/coding.md             │      │
│ ▸ Wiki   │  │  • modules/office.md             │      │
│ ▸ Graph  │  │  • modules/interview.md          │      │
│          │  │  • modules/wiki.md               │      │
│          │  └──────────────────────────────────┘      │
│          │                                           │
│          │  ┌─ api ────────────────────────────┐      │
│          │  │ 5 docs · 最近更新 2026-05-24      │      │
│          │  │                                  │      │
│          │  │  • http/commands.md              │      │
│          │  │  • http/skills.md                │      │
│          │  │  • cli/kb.md                     │      │
│          │  │  ...                              │      │
│          │  └──────────────────────────────────┘      │
│          │                                           │
│          │  ┌─ data-model ─────────────────────┐      │
│          │  │ 4 docs                            │      │
│          │  └──────────────────────────────────┘      │
│          │                                           │
│          │  ┌─ flows ───────────────────────────┐      │
│          │  │ 5 docs                            │      │
│          │  └──────────────────────────────────┘      │
│          │                                           │
│          │  ┌─ concepts ─────────────────────────┐    │
│          │  │ 3 docs                            │      │
│          │  └──────────────────────────────────┘      │
└──────────┴───────────────────────────────────────────┘
```

**侧边栏**：按维度分组，每个维度下展开文件列表。维度名可点击折叠/展开。

**数据来源**：从 `raw` 集合中按 `project` 过滤，按 `dimension` 分组。

#### 详情页

**页面**：`/src/pages/projects/[project]/raw/[...slug].astro`

**布局**：`DocLayout.astro`

**内容结构**：

```
┌──────────┬───────────────────────────────────────────┐
│ Sidebar  │  ┌─ 面包屑 ──────────────────────────┐    │
│          │  │ Raw / topology / spec-workflow      │    │
│          │  └────────────────────────────────────┘    │
│ ▾ Raw    │                                           │
│   ▾ topo │  # spec-workflow 模块拓扑                 │
│     ▪ spe│                                           │
│     ▪ ana│  （markdown 正文，包含 Mermaid 图、代码块、│
│     ▪ cod│   callout、表格等，由 rehype 插件处理）    │
│   ▸ api  │                                           │
│   ▸ data │  ┌─ 来源信息 ─────────────────────────┐    │
│   ▸ flows│  │ 项目: claude-harness                 │    │
│   ▸ conc │  │ 维度: topology                      │    │
│   ▸ Wiki │  │ 提取时间: 2026-05-24                 │    │
│   ▸ Graph│  │ 对应 Wiki: [spec-workflow 实体] →    │    │
│          │  └────────────────────────────────────┘    │
│          │                                           │
│          │  ← 上一篇          下一篇 →                │
└──────────┴───────────────────────────────────────────┘
```

**关键组件**：
- `RawDocMeta.astro`：渲染来源信息卡片（项目、维度、时间、对应 wiki 链接）
- 复用 `TableOfContents.tsx`（右侧目录）
- 复用 `Pagination.astro`（同维度内的前后导航）
- 复用 `ReadingProgress.tsx`

**对应 wiki 链接**：从 `wiki` 集合中查找 `sources` 字段包含当前 raw 路径的页面，渲染为链接。

### Wiki 视图

#### 总览页

**页面**：`/src/pages/projects/[project]/wiki/index.astro`

**布局**：`DocLayout.astro`

**内容结构**：

```
┌──────────┬───────────────────────────────────────────┐
│ Sidebar  │  Wiki 页面 — claude-harness                 │
│          │                                           │
│ ▸ Raw    │  ┌─ entities (10) ───────────────────┐     │
│ ▾ Wiki   │  │                                  │     │
│   ▸ enti │  │  模块实体                          │     │
│   ▸ conc │  │  • spec-workflow                  │     │
│   ▸ synt │  │  • analysis                       │     │
│   ▸ Graph│  │  • coding                          │     │
│          │  │  ...                               │     │
│          │  │                                  │     │
│          │  │  接口实体                          │     │
│          │  │  • http-commands                  │     │
│          │  │  • http-skills                    │     │
│          │  │  ...                               │     │
│          │  │                                  │     │
│          │  │  数据实体                          │     │
│          │  │  • plugin-config                  │     │
│          │  │  • skill-manifest                 │     │
│          │  └──────────────────────────────────┘     │
│          │                                           │
│          │  ┌─ concepts (3) ────────────────────┐     │
│          │  │  • 插件生命周期流程                  │     │
│          │  │  • 知识摄入流程                     │     │
│          │  │  • 文档生成流程                     │     │
│          │  └──────────────────────────────────┘     │
│          │                                           │
│          │  ┌─ syntheses (2) ───────────────────┐     │
│          │  │  • 插件-技能交叉分析                 │     │
│          │  │  • 数据模型-流程关联                 │     │
│          │  └──────────────────────────────────┘     │
└──────────┴───────────────────────────────────────────┘
```

**侧边栏**：按页面类型分组（entity/concept/synthesis），entity 下再按来源维度细分（模块实体、接口实体、数据实体）。

#### 详情页

**页面**：`/src/pages/projects/[project]/wiki/[...slug].astro`

**布局**：`DocLayout.astro`

**内容结构**：

```
┌──────────┬───────────────────────────────────────────┐
│ Sidebar  │  ┌─ 面包屑 ──────────────────────────┐    │
│          │  │ Wiki / entities / spec-workflow     │    │
│          │  └────────────────────────────────────┘    │
│ ▸ Raw    │                                           │
│ ▾ Wiki   │  # spec-workflow                          │
│   ▾ enti │                                           │
│     ▪ spe│  （wiki 正文，包含交叉引用链接）            │
│     ▪ ana│                                           │
│   ▸ conc │  ┌─ 交叉引用 ─────────────────────────┐    │
│   ▸ synt │  │ → analysis 模块（entity）            │    │
│   ▸ Graph│  │ → 插件生命周期流程（concept）         │    │
│          │  │ → plugin-config 数据模型（entity）    │    │
│          │  └────────────────────────────────────┘    │
│          │                                           │
│          │  ┌─ 来源追溯 ─────────────────────────┐    │
│          │  │ ← topology/modules/spec-workflow.md  │    │
│          │  └────────────────────────────────────┘    │
│          │                                           │
│          │  ← 上一篇          下一篇 →                │
└──────────┴───────────────────────────────────────────┘
```

**关键组件**：
- `CrossReferences.astro`：渲染该页面的所有交叉引用链接，按引用目标类型分组（entity/concept/synthesis），每个链接显示目标页面标题和类型标签
- `SourceTraceability.astro`：渲染来源追溯，链接回对应的 raw 文档（从 frontmatter `sources` 字段获取）
- 复用 `TableOfContents.tsx`、`Pagination.astro`、`ReadingProgress.tsx`

### 图谱视图

**页面**：`/src/pages/projects/[project]/graph.astro`

**布局**：`DocLayout.astro`（侧边栏收起为 icon-rail 模式，最大化图谱画布）

**内容结构**：

```
┌──────────┬───────────────────────────────────────────┐
│ Sidebar  │  ┌─ GraphControls ────────────────────┐   │
│ (icon    │  │ 着色: [维度▼]  筛选: [全部▼]       │   │
│  rail)   │  │ 布局: [收缩] [展开] [重置]         │   │
│          │  │ 搜索: [________]                    │   │
│          │  └────────────────────────────────────┘   │
│          │                                           │
│          │  ┌─ KnowledgeGraph ────────────────────┐   │
│          │  │                                   │   │
│          │  │       (力导向图)                    │   │
│          │  │                                   │   │
│          │  │    ○ spec-workflow                │   │
│          │  │   / \                             │   │
│          │  │  ○   ○ analysis  coding           │   │
│          │  │  |    |  \                         │   │
│          │  │  ○   ○   ○                       │   │
│          │  │                                   │   │
│          │  │  节点颜色:                         │   │
│          │  │  ■ topology  ■ api  ■ data-model  │   │
│          │  │  ■ flows     ■ concepts           │   │
│          │  │                                   │   │
│          │  └───────────────────────────────────┘   │
│          │                                           │
│          │  ┌─ NodeCard（悬浮） ──────────────────┐   │
│          │  │ spec-workflow                       │   │
│          │  │ 类型: entity · 维度: topology       │   │
│          │  │ 10 个技能，7 个规则，8 个命令       │   │
│          │  │ [查看 Wiki 页面] [查看 Raw 文档]    │   │
│          │  └────────────────────────────────────┘   │
└──────────┴───────────────────────────────────────────┘
```

**关键组件**：

**`KnowledgeGraph.tsx`**（React 客户端组件）：
- 使用 d3-force 实现力导向布局（forceLink + forceManyBody + forceCenter）
- 从 `public/graph.json` 加载节点和边数据
- 节点渲染为圆形，大小按连接度缩放（度越大圆越大）
- 边渲染为曲线，颜色取源节点颜色，透明度 0.3
- 拖拽交互：拖拽节点固定位置，双击释放
- 缩放/平移：d3-zoom 控制画布
- 悬浮交互：鼠标悬浮显示 `NodeCard`
- 点击交互：单击节点聚焦（高亮该节点及其邻居，淡化其余），双击跳转到 wiki 详情页
- 主题感知：监听 `html` 的 `dark` class 变化，调整标签颜色和背景

**`GraphControls.tsx`**（React 客户端组件）：
- 着色模式选择器：按维度 / 按类型 / 按项目
- 筛选器：多选维度、类型、项目（控制哪些节点显示）
- 布局控制：收缩（只显示 entity）、展开（显示全部）、重置（重新计算布局）
- 搜索框：输入节点名称，匹配的节点高亮脉冲动画
- 统计信息：当前可见节点数 / 总节点数，当前可见边数 / 总边数

**`NodeCard.tsx`**（React 客户端组件）：
- 悬浮卡片，显示节点摘要信息
- 内容：标题、类型标签、维度标签、一句话摘要
- 操作：[查看 Wiki 页面]（跳转到 wiki 详情页）、[查看 Raw 文档]（跳转到 raw 详情页）
- 定位：跟随鼠标，偏移 (15, 15) 避免遮挡

### 新增组件清单

| 组件 | 类型 | 文件 | 职责 |
|------|------|------|------|
| `HomeLayout.astro` | Astro 服务端 | `layouts/HomeLayout.astro` | 全局首页布局（无侧边栏，全宽） |
| `ProjectCard.astro` | Astro 服务端 | `components/ProjectCard.astro` | 项目卡片（首页用） |
| `ViewCard.astro` | Astro 服务端 | `components/ViewCard.astro` | 视图入口卡片（项目首页用） |
| `DimensionBar.astro` | Astro 服务端 | `components/DimensionBar.astro` | 维度覆盖条形图（项目首页用） |
| `RawDocMeta.astro` | Astro 服务端 | `components/RawDocMeta.astro` | Raw 文档来源信息卡片 |
| `CrossReferences.astro` | Astro 服务端 | `components/CrossReferences.astro` | 交叉引用列表（wiki 详情页用） |
| `SourceTraceability.astro` | Astro 服务端 | `components/SourceTraceability.astro` | 来源追溯链接（wiki 详情页用） |
| `KnowledgeGraph.tsx` | React 客户端 | `components/KnowledgeGraph.tsx` | 力导向知识图谱 |
| `GraphControls.tsx` | React 客户端 | `components/GraphControls.tsx` | 图谱控制面板 |
| `NodeCard.tsx` | React 客户端 | `components/NodeCard.tsx` | 节点悬浮摘要卡片 |
| `ProjectSwitcher.astro` | Astro 服务端 | `components/ProjectSwitcher.astro` | TopNav 中的项目切换下拉菜单 |

### 复用现有组件

| 组件 | 复用方式 |
|------|---------|
| `DocLayout.astro` | 所有非首页页面使用 |
| `TopNav.astro` | 增加 ProjectSwitcher 插槽 |
| `Sidebar.astro` | 根据当前视图（raw/wiki/graph）动态构建导航树 |
| `SearchModal.tsx` | 扩展搜索范围覆盖 raw + wiki 集合 |
| `SearchTrigger.tsx` | 不变 |
| `TableOfContents.tsx` | raw 和 wiki 详情页使用 |
| `Pagination.astro` | raw 和 wiki 详情页使用 |
| `ReadingProgress.tsx` | raw 和 wiki 详情页使用 |
| `ThemeToggle.tsx` | 不变 |
| `KeyboardShortcuts.astro` | 不变 |
| `mermaid-block.ts` | raw 详情页使用（raw 文档包含 Mermaid 图表） |

### 搜索增强

现有搜索只覆盖 `docs` 集合。增强后覆盖 `raw` + `wiki` 两个集合：

```typescript
// build-search-index.mjs 增强
const rawDocs = await loadCollection('raw');
const wikiDocs = await loadCollection('wiki');

const index = [...rawDocs.map(d => ({
  title: d.title,
  description: d.description || '',
  content: stripMarkdown(d.body),
  section: `raw/${d.dimension}`,
  href: `/projects/${d.project}/raw/${d.slug}`,
  type: 'raw',
})), ...wikiDocs.map(d => ({
  title: d.title,
  description: d.description || '',
  content: stripMarkdown(d.body),
  section: `wiki/${d.page_type}`,
  href: `/projects/${d.project}/wiki/${d.slug}`,
  type: 'wiki',
}))];
```

搜索结果增加类型标签（raw/wiki）和维度/页面类型标签，帮助用户区分结果来源。

### 站点完整目录结构

```
site/
├── astro.config.mjs
├── site.config.ts
├── tailwind.config.mjs
├── tsconfig.json
├── package.json
├── scripts/
│   └── build-search-index.mjs           # 增强：覆盖 raw + wiki
├── public/
│   ├── favicon.svg
│   ├── robots.txt
│   ├── search-index.json                # 构建时生成
│   └── graph.json                       # 构建时从 data/ 复制
├── src/
│   ├── content.config.ts                # 两个集合：raw + wiki
│   ├── layouts/
│   │   ├── DocLayout.astro              # 复用
│   │   └── HomeLayout.astro             # 新增：全局首页布局
│   ├── pages/
│   │   ├── index.astro                  # 全局首页
│   │   ├── projects/
│   │   │   └── [project]/
│   │   │       ├── index.astro          # 项目首页
│   │   │       ├── raw/
│   │   │       │   ├── index.astro      # Raw 总览
│   │   │       │   └── [...slug].astro  # Raw 详情
│   │   │       ├── wiki/
│   │   │       │   ├── index.astro      # Wiki 总览
│   │   │       │   └── [...slug].astro  # Wiki 详情
│   │   │       └── graph.astro          # 知识图谱
│   │   ├── search.astro                 # 全局搜索
│   │   ├── sitemap.xml.astro
│   │   └── 404.astro
│   ├── components/
│   │   ├── TopNav.astro                 # 增强：+ ProjectSwitcher
│   │   ├── Sidebar.astro                # 增强：动态导航树
│   │   ├── SearchModal.tsx              # 增强：raw + wiki 搜索
│   │   ├── HomeLayout.astro             # 新增
│   │   ├── ProjectCard.astro            # 新增
│   │   ├── ViewCard.astro               # 新增
│   │   ├── DimensionBar.astro           # 新增
│   │   ├── RawDocMeta.astro             # 新增
│   │   ├── CrossReferences.astro        # 新增
│   │   ├── SourceTraceability.astro     # 新增
│   │   ├── KnowledgeGraph.tsx           # 新增
│   │   ├── GraphControls.tsx            # 新增
│   │   ├── NodeCard.tsx                 # 新增
│   │   ├── ProjectSwitcher.astro        # 新增
│   │   ├── Pagination.astro             # 复用
│   │   ├── TableOfContents.tsx          # 复用
│   │   ├── ReadingProgress.tsx          # 复用
│   │   ├── ThemeToggle.tsx              # 复用
│   │   ├── SearchTrigger.tsx            # 复用
│   │   ├── KeyboardShortcuts.astro      # 复用
│   │   ├── Breadcrumb.astro             # 复用
│   │   └── mermaid-block.ts             # 复用
│   ├── lib/
│   │   ├── rehype-callout.ts            # 复用
│   │   └── remark-mermaid.mjs           # 复用
│   └── styles/
│       └── global.css                   # 增强：图谱样式、卡片样式
```

### Load Skills

| Skill | 职责 |
|-------|------|
| `serve` | 构建 Astro 站点 + 启动预览服务器 |
| `build-search-index` | 从 wiki + raw 内容构建 Fuse.js 搜索索引 |
| `build-graph` | 从 wiki 页面提取交叉引用，构建图谱数据（JSON）供力导向图消费 |

这些 skill 由 `/kb serve` 自动串联调用，用户不直接使用。

### 双模式运行

- **插件模式**：用户通过 `/kb` 命令和 agent 在 Claude Code 中交互
- **独立模式**：直接 `npm run dev` 或 `npm run build`；消费 `data/wiki/` + `data/raw/` 中的已有内容，不需要 Claude Code

---

## 管道命令

| 命令 | 管道阶段 | 说明 |
|------|---------|------|
| `/kb` | scan → extract-all → ingest → cross-ref → serve | 一键全量管道 |
| `/kb scan` | scan | 只做结构梳理 |
| `/kb extract [dimension]` | scan + extract-* | 提取指定维度（topology/api/data-model/flows/concepts）；不指定则全量 |
| `/kb transform [dimension]` | ingest + cross-ref | 转化指定维度的 raw 为 wiki；不指定则全量 |
| `/kb query <question>` | query | 查询知识库 |
| `/kb lint` | lint | 知识库健康检查 |
| `/kb serve` | serve | 构建 + 启动站点 |

## Agents

| Agent | 职责 | 模型 |
|-------|------|------|
| `kb-agent` | 主路由：解析 `/kb` 命令参数，分发到 skill | sonnet |
| `extract-agent` | 多维度并行提取：读 `_map.md`，并发调用 extract skill | sonnet |
| `transform-agent` | 批量转化：扫描 unprocessed 的 raw，逐个 ingest，最后 cross-ref | sonnet |

## 插件目录结构

```
plugins/kb/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── extract/
│   │   └── SKILL.md                         # Extract 路由
│   ├── scan/
│   │   └── SKILL.md                         # 阶段 1：结构梳理
│   ├── extract-topology/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── topology.md                  # topology 文档必含章节
│   ├── extract-api/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── api.md
│   ├── extract-data-model/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── data-model.md
│   ├── extract-flows/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── flows.md                  # 必含章节：业务场景、功能分解、层次关系、流程路径、异常分支
│   ├── extract-concepts/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── concepts.md
│   ├── transform/
│   │   └── SKILL.md                         # Transform 路由
│   ├── ingest/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       ├── entity.md                    # 实体页面模板
│   │       ├── concept.md                   # 概念页面模板
│   │       └── synthesis.md                 # 综合页面模板
│   ├── cross-ref/
│   │   └── SKILL.md
│   ├── lint/
│   │   └── SKILL.md
│   ├── query/
│   │   └── SKILL.md
│   ├── serve/
│   │   └── SKILL.md
│   ├── build-search-index/
│   │   └── SKILL.md
│   └── build-graph/
│       └── SKILL.md
├── agents/
│   ├── kb-agent.md
│   ├── extract-agent.md
│   └── transform-agent.md
├── commands/
│   └── kb.md                                # /kb 命令
├── data/
│   ├── config.json                          # {"dataDir": "data"}
│   ├── raw/                                 # Extract 产出（gitignore）
│   └── wiki/                                # Transform 产出（gitignore）
├── site/                                    # Astro 站点（从 analysis 增强）
├── .gitignore
└── CHANGELOG.md
```

## 路线图

### 阶段 1：核心管道

- `scan` + 5 个 extract skill + 模板
- `ingest` + `cross-ref` + wiki 页面模板
- `serve` + Astro 站点（raw/wiki/图谱三视图）
- `/kb` 命令 + 3 个 agent
- 验证：对 `claude-harness` 本身做端到端分析

### 阶段 2：扩展来源

- 远程仓库摄入（clone + scan）
- URL 摄入
- 文件摄入（PDF、docx 等）
- 非代码库 raw → wiki 转化

### 阶段 3：智能化

- 增量提取（只重新分析变更文件）
- 变更影响分析（`extract-impact`）
- 设计决策提取（`extract-decisions`）
- git hook 自动更新
- 知识图谱社区发现

### 阶段 4：生态集成

- 导出 PDF/DOCX（office 插件集成）
- 多项目跨综合
- 团队共享（图谱作为 JSON，提交到仓库）
- API 文档托管