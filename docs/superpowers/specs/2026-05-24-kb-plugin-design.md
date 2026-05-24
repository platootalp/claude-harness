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
| `extract-flows` | flows | 端到端路径、分支、异常处理、性能特征 | `data/raw/<project>/flows/` |
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
│   ├── <flow-a>.md
│   └── <flow-b>.md
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
| `source-functional-analysis` | `extract-flows` | 重命名，产出格式对齐 |
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

### 三个视图

站点呈现同一个知识库的三个视角，各有用途。

**Raw 视图** — 浏览 Extract 的深度分析文档

- 入口页：按维度分组（topology、api、data-model、flows、concepts），每组显示文档数量
- 详情页：渲染 raw markdown，保留 Mermaid 图表、代码块、callout
- 侧边栏：按维度树形导航
- 用途：查看特定模块的分析细节、代码证据、技术机制

**Wiki 视图** — 浏览 Transform 的结构化知识页面

- 入口页：按页面类型分组（entity、concept、synthesis），每组显示页面数量
- 详情页：渲染 wiki 页面，带交叉引用链接和来源追溯（链接回 raw 文档）
- 侧边栏：按页面类型树形导航
- 用途：快速查找、跟随交叉引用探索关联知识

**图谱视图** — 交互式知识图谱

- 力导向图：节点 = wiki 页面（entity/concept/synthesis），边 = 交叉引用关系
- 点击节点：弹出摘要卡片，可跳转到 wiki 详情页
- 着色模式：按维度（来自哪个 Extract 维度）、按类型（entity/concept/synthesis）、按项目
- 筛选：按维度、类型、项目筛选节点
- 布局控制：收缩/展开、聚焦节点邻居
- 用途：发现未知关联、一眼看清知识结构

### 站点结构

```
site/
├── src/
│   ├── pages/
│   │   ├── index.astro                    # 首页：项目卡片列表
│   │   ├── projects/
│   │   │   └── [project]/
│   │   │       ├── index.astro            # 项目首页：三个视图入口
│   │   │       ├── raw/
│   │   │       │   ├── index.astro        # Raw 文档总览：按维度分组
│   │   │       │   └── [...slug].astro    # Raw 文档详情页
│   │   │       ├── wiki/
│   │   │       │   ├── index.astro        # Wiki 总览：按页面类型分组
│   │   │       │   └── [...slug].astro    # Wiki 页面详情页
│   │   │       └── graph.astro            # 知识图谱：力导向图
│   │   └── search.astro                   # 全局搜索
│   ├── components/
│   │   ├── ProjectSwitcher.astro          # 项目切换器
│   │   ├── DimensionFilter.astro          # 维度筛选器（raw 视图）
│   │   ├── PageTypeFilter.astro           # 页面类型筛选器（wiki 视图）
│   │   ├── KnowledgeGraph.tsx             # 力导向图组件
│   │   ├── GraphControls.tsx              # 图谱控制面板
│   │   └── ...                            # 复用现有组件
│   └── ...
```

### 项目首页

```
┌─────────────────────────────────────────────┐
│  claude-harness                              │
├─────────────┬──────────────┬────────────────┤
│  Raw Docs   │  Wiki Pages  │  Knowledge     │
│  23 docs    │  15 pages    │  Graph         │
│  5 dims     │  3 types     │  45 nodes      │
│             │              │  67 edges       │
│  [Browse]   │  [Browse]    │  [Explore]     │
├─────────────┴──────────────┴────────────────┤
│  Recent Activity                            │
│  • topology extracted — 2026-05-24          │
│  • api extracted — 2026-05-24               │
│  • wiki transformed — 2026-05-24            │
└─────────────────────────────────────────────┘
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
- **独立模式**：直接 `npm run dev` 或 `npm run build`；消费 `data/wiki/` 中的已有内容，不需要 Claude Code

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
│   │       └── flows.md
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