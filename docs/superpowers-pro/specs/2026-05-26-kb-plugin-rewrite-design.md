# KB 插件深度重写设计文档

> 日期：2026-05-26
> 状态：设计阶段
> 核心问题：Extract 阶段 prompt 过浅 + 维度固定一刀切 + 全链路质量不达标

---

## 1. 设计目标

1. **画像驱动**：先扫描仓库特征，再决定生成什么文档——不同仓库产出不同文档集
2. **深度提取**：每份文档有专属深度模板，产出架构决策级分析，而非结构罗列
3. **三层产出**：raw（原始提取）→ wiki（整合文档）→ graph（知识图谱），站点三视图展示
4. **可校验可增量**：每阶段输入/输出有明确 schema，支持单阶段重跑

---

## 2. 整体架构

### 2.1 五阶段管道

```
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: SCAN                                              │
│  输入: 仓库根目录                                            │
│  输出: repo-profile.json                                     │
│  职责: 结构扫描 + 框架识别 + 能力检测 → 仓库画像              │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 2: PLAN                                              │
│  输入: repo-profile.json                                     │
│  输出: doc-plan.json                                         │
│  职责: 画像驱动 → 决定生成哪些文档 + 每份文档的提取参数        │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 3: EXTRACT                                           │
│  输入: doc-plan.json + 仓库源码                              │
│  输出: raw/<doc-type>.md                                     │
│  职责: 按文档类型派生子代理，深度模板驱动提取                  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 4: TRANSFORM                                         │
│  输入: raw/ + repo-profile.json + doc-plan.json              │
│  输出: wiki/<编号文档>.md + graph.json                       │
│  职责: 交叉引用 + 一致性校验 + 术语归一 + 文档编排             │
│        raw 碎片 → wiki 连贯知识文档                           │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 5: LOAD                                              │
│  输入: raw/ + wiki/ + graph.json                             │
│  输出: search-index + graph 数据 → 站点可消费                 │
│  职责: 构建搜索索引 + 图谱数据转换 → 供站点三视图展示          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 数据流向

```
                    ┌──── raw/ ────┐
                    │              │
SCAN → PLAN → EXTRACT              TRANSFORM → LOAD → 站点
                    │              │     ↑
                    └──────────────┘     │
                                         │
              raw/ ──────────────────────┘
              wiki/ ─────────────────────┘
              graph.json ───────────────┘

站点三视图:
  - Raw View: 展示 raw/ 原始提取文档
  - Wiki View: 展示 wiki/ 整合文档
  - Graph View: 展示 graph.json 知识图谱
```

### 2.3 与现有架构的对比

| 维度 | 现有 | 重写后 |
|------|------|--------|
| 维度划分 | 固定 5 维（topology/api/data-model/flows/concepts） | 画像驱动，动态文档集 |
| Scan 输出 | 文件列表 + 语言统计 | repo-profile.json（仓库画像） |
| 中间编排 | 无（直接跑所有 extract） | doc-plan.json（文档规划） |
| Extract 产出 | 自由格式 Markdown | 深度模板驱动的结构化 Markdown |
| Transform | 仅 cross-ref 关联 | 交叉引用 + 一致性校验 + 术语归一 + 文档编排 |
| 站点数据源 | raw + wiki + graph | raw + wiki + graph（保持三视图） |

---

## 3. Stage 1: SCAN — 仓库画像

### 3.1 职责

扫描仓库，产出结构化画像。**只观察，不决策**——决策留给 PLAN 阶段。

### 3.2 扫描内容

| 扫描维度 | 检测项 | 检测方法 |
|----------|--------|----------|
| 技术栈 | 主要语言、框架、运行时 | 文件扩展名统计 + package.json/pom.xml/pyproject.toml 解析 |
| 仓库类型 | backend/frontend/sdk/platform/agent/tool | 框架特征 + 目录结构 + 入口模式 |
| 代码组织 | 分层架构 / DDD / Clean Arch / 模块化单体 / Monorepo | 目录模式匹配 + 层间依赖检测 |
| 能力特征 | has_api / has_db / has_queue / has_auth / has_plugin_system / has_agent_runtime / has_workflow / has_frontend / has_scheduler / has_ai | 特征文件 + 目录 + 依赖包检测 |
| 复杂度 | 模块数量 / 包深度 / 入口数量 / 调用链长度 / 外部依赖数量 | 文件统计 + import 分析 |
| 关键资产 | API 入口 / 数据模型 / 配置文件 / 部署描述 | 路径模式匹配 |

### 3.3 仓库类型识别规则

| repo_type | 识别特征 | 优先级 |
|-----------|----------|--------|
| `agentic_platform` | 存在 Agent/Tool/Prompt/Workflow/MCP 目录或文件，且有多模块结构 | 最高（优先匹配） |
| `platform_system` | 多模块 + 权限体系 + 插件机制 + 配置中心 | 高 |
| `backend_service` | Controller + Service + Repository 分层，或 Spring Boot / Express / FastAPI | 中 |
| `frontend_app` | React/Vue/Svelte + Router + Store + Components | 中 |
| `sdk_library` | export API + util/client/builder 包，无 HTTP 入口 | 中 |
| `tool_script` | CLI 入口 + shell/python 脚本 + cron/自动化特征 | 最低 |

**识别顺序**：agentic_platform → platform_system → backend_service / frontend_app → sdk_library → tool_script。高优先级匹配后不再向下检查。

**类型组合**：一个仓库可能有多种特征。repo_type 取最高优先级匹配，能力特征全部保留在 capabilities 数组中。例如 Claude Code 插件项目：

```json
{
  "repo_type": "agentic_platform",
  "capabilities": ["has_api", "has_plugin_system", "has_agent_runtime", "has_workflow", "has_frontend"]
}
```

### 3.4 repo-profile.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["repo_name", "repo_type", "primary_language", "frameworks", "architecture_style", "complexity_level", "capabilities", "entry_points", "modules"],
  "properties": {
    "repo_name": { "type": "string" },
    "repo_type": {
      "type": "string",
      "enum": ["agentic_platform", "platform_system", "backend_service", "frontend_app", "sdk_library", "tool_script"]
    },
    "primary_language": { "type": "string" },
    "frameworks": {
      "type": "array",
      "items": { "type": "string" }
    },
    "architecture_style": {
      "type": "string",
      "enum": ["layered", "ddd", "clean_architecture", "modular_monolith", "monorepo", "flat"]
    },
    "complexity_level": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    },
    "entry_points": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "type": { "type": "string", "enum": ["http", "cli", "cron", "event", "rpc", "agent"] },
          "description": { "type": "string" }
        }
      }
    },
    "modules": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "path": { "type": "string" },
          "responsibility": { "type": "string" },
          "key_files": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "capabilities": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "has_api", "has_database", "has_message_queue", "has_scheduler",
          "has_frontend", "has_auth", "has_plugin_system", "has_workflow_engine",
          "has_ai_capability", "has_agent_runtime", "has_context_management",
          "has_tool_system", "has_memory_system", "has_rag"
        ]
      }
    },
    "storage": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["relational_db", "nosql_db", "cache", "file_storage", "search_engine", "queue"] },
          "technology": { "type": "string" },
          "purpose": { "type": "string" }
        }
      }
    },
    "build_tools": { "type": "array", "items": { "type": "string" } },
    "deployment_type": {
      "type": "string",
      "enum": ["containerized", "serverless", "bare_metal", "static", "cli_tool"]
    }
  }
}
```

---

## 4. Stage 2: PLAN — 文档规划

### 4.1 职责

基于仓库画像，决定生成哪些文档、每份文档的提取参数、文档间编排顺序。

### 4.2 文档类型体系

#### 4.2.1 通用文档（所有仓库必须生成）

| ID | 文档名 | 编号 | 说明 |
|----|--------|------|------|
| `overview` | 项目总览 | 01 | 项目目标、核心能力、技术栈、阅读路径 |
| `structure` | 仓库结构 | 02 | 目录树、模块职责、入口文件、依赖边界 |
| `risk` | 风险与技术债 | 11 | 高复杂度模块、强耦合、技术债、改造建议 |
| `glossary` | 术语表 | 12 | 业务术语、技术术语、缩写、同义词映射 |

#### 4.2.2 条件文档（根据能力特征动态生成）

| ID | 文档名 | 编号 | 生成条件 |
|----|--------|------|----------|
| `architecture` | 架构设计 | 03 | modules > 3 OR 存在分层结构 OR 存在多服务调用 |
| `domain` | 领域与业务 | 04 | 存在 DDD 特征 OR 存在复杂业务状态 OR 存在多个聚合 |
| `flows` | 核心流程 | 05 | 存在复杂调用链 OR 存在工作流 OR 存在任务执行链 |
| `api` | 接口设计 | 06 | has_api |
| `data` | 数据设计 | 07 | has_database OR has_cache OR has_file_storage |
| `config` | 配置与运行 | 08 | 存在配置文件 OR 环境变量 OR docker-compose |
| `deployment` | 部署与运维 | 09 | 存在 Docker/K8S OR CI/CD OR Helm |
| `testing` | 测试与质量 | 10 | 存在测试目录 OR CI 测试 OR Mock 框架 |

#### 4.2.3 Agent/Platform 专用文档

| ID | 文档名 | 编号 | 生成条件 |
|----|--------|------|----------|
| `agent_system` | Agent 架构 | 03a | has_agent_runtime |
| `tool_system` | Tool 体系 | 04a | has_tool_system |
| `plugin_system` | 插件系统 | 05a | has_plugin_system |
| `context_system` | 上下文系统 | 06a | has_context_management |
| `workflow_system` | 工作流系统 | 07a | has_workflow_engine |
| `workspace` | Workspace 架构 | 02a | is_monorepo（architecture_style = monorepo） |

**编号规则**：通用文档固定编号（01-12），专用文档用字母后缀（02a, 03a...），在 wiki 编排时按逻辑顺序插入。

### 4.3 文档规划决策树

```
repo-profile.json
    │
    ├─ 必出: overview, structure, risk, glossary
    │
    ├─ 通用条件文档:
    │   ├─ modules > 3 → architecture
    │   ├─ has_domain_features → domain
    │   ├─ has_complex_flows → flows
    │   ├─ has_api → api
    │   ├─ has_database OR has_cache → data
    │   ├─ has_config → config
    │   ├─ has_deployment → deployment
    │   └─ has_tests → testing
    │
    └─ Agent/Platform 专用文档:
        ├─ is_monorepo → workspace
        ├─ has_agent_runtime → agent_system
        ├─ has_tool_system → tool_system
        ├─ has_plugin_system → plugin_system
        ├─ has_context_management → context_system
        └─ has_workflow_engine → workflow_system
```

**互斥规则**：
- `agent_system` 与 `architecture` 互斥：若 has_agent_runtime，用 agent_system 替代 architecture
- `tool_system` 与 `domain` 可共存但有优先级：has_tool_system 时 tool_system 优先
- `workspace` 与 `structure` 共存：workspace 是 structure 的扩展，编号紧接其后

### 4.4 doc-plan.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["profile_ref", "documents"],
  "properties": {
    "profile_ref": { "type": "string", "description": "repo-profile.json 的路径" },
    "documents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "title", "number", "reason"],
        "properties": {
          "id": { "type": "string", "description": "文档类型 ID，如 overview, architecture, agent_system" },
          "title": { "type": "string" },
          "number": { "type": "string", "description": "编排编号，如 01, 02a, 03" },
          "reason": { "type": "string", "description": "为什么生成这份文档" },
          "scope_hint": { "type": "string", "description": "提取时的范围提示，如 '重点分析 agent 调度循环和 tool routing'" },
          "depends_on": {
            "type": "array",
            "items": { "type": "string" },
            "description": "依赖的其他文档 ID（用于提取顺序编排）"
          }
        }
      }
    },
    "extraction_order": {
      "type": "array",
      "items": { "type": "string" },
      "description": "文档提取顺序（考虑依赖关系）"
    }
  }
}
```

### 4.5 doc-plan 示例

**Claude Code 插件项目（agentic_platform）**：

```json
{
  "profile_ref": "repo-profile.json",
  "documents": [
    { "id": "overview", "title": "项目总览", "number": "01", "reason": "通用必出" },
    { "id": "structure", "title": "仓库结构", "number": "02", "reason": "通用必出" },
    { "id": "workspace", "title": "Workspace 架构", "number": "02a", "reason": "is_monorepo", "scope_hint": "重点分析 plugins/ 和 skills/ 的组织边界" },
    { "id": "agent_system", "title": "Agent 架构", "number": "03a", "reason": "has_agent_runtime", "scope_hint": "分析 agent 调度循环、子代理派发、上下文管理", "depends_on": ["overview", "structure"] },
    { "id": "tool_system", "title": "Tool 体系", "number": "04a", "reason": "has_tool_system", "scope_hint": "分析 tool 注册、路由、权限、shell/file/web tools", "depends_on": ["agent_system"] },
    { "id": "plugin_system", "title": "插件系统", "number": "05a", "reason": "has_plugin_system", "scope_hint": "分析 skills/agents/hooks/commands/MCP 的生命周期和交互", "depends_on": ["agent_system"] },
    { "id": "context_system", "title": "上下文系统", "number": "06a", "reason": "has_context_management", "scope_hint": "分析 CLAUDE.md 层级、memory、prompt 注入、语义检索", "depends_on": ["agent_system"] },
    { "id": "workflow_system", "title": "工作流系统", "number": "07a", "reason": "has_workflow_engine", "scope_hint": "分析 skill 编排、检查点、条件分支", "depends_on": ["plugin_system"] },
    { "id": "risk", "title": "风险与技术债", "number": "11", "reason": "通用必出", "depends_on": ["agent_system", "tool_system", "plugin_system"] },
    { "id": "glossary", "title": "术语表", "number": "12", "reason": "通用必出" }
  ],
  "extraction_order": ["overview", "structure", "workspace", "agent_system", "tool_system", "plugin_system", "context_system", "workflow_system", "risk", "glossary"]
}
```

**Spring Boot 后端服务**：

```json
{
  "profile_ref": "repo-profile.json",
  "documents": [
    { "id": "overview", "title": "项目总览", "number": "01", "reason": "通用必出" },
    { "id": "structure", "title": "仓库结构", "number": "02", "reason": "通用必出" },
    { "id": "architecture", "title": "架构设计", "number": "03", "reason": "modules > 3 + 分层结构", "scope_hint": "重点分析 Controller-Service-Repository 分层和模块间依赖", "depends_on": ["overview", "structure"] },
    { "id": "domain", "title": "领域与业务", "number": "04", "reason": "存在 DDD 特征 + 复杂业务状态", "depends_on": ["architecture"] },
    { "id": "flows", "title": "核心流程", "number": "05", "reason": "存在复杂调用链", "depends_on": ["architecture", "domain"] },
    { "id": "api", "title": "接口设计", "number": "06", "reason": "has_api", "depends_on": ["architecture"] },
    { "id": "data", "title": "数据设计", "number": "07", "reason": "has_database", "depends_on": ["domain"] },
    { "id": "config", "title": "配置与运行", "number": "08", "reason": "存在 application.yml", "depends_on": ["overview"] },
    { "id": "risk", "title": "风险与技术债", "number": "11", "reason": "通用必出", "depends_on": ["architecture", "domain", "flows"] },
    { "id": "glossary", "title": "术语表", "number": "12", "reason": "通用必出" }
  ],
  "extraction_order": ["overview", "structure", "config", "architecture", "domain", "flows", "api", "data", "risk", "glossary"]
}
```

---

## 5. Stage 3: EXTRACT — 深度提取

### 5.1 职责

根据 doc-plan.json，按文档类型派生子代理，每个子代理使用对应的深度模板提取 raw 文档。

### 5.2 提取策略

**核心改进：从"浅层结构罗列"到"深度分析"**

当前 extract-* 技能的问题：prompt 只告诉 agent "分析什么"（如"分析文件依赖关系"），没告诉 agent"怎么分析"、"分析到什么深度"、"输出什么结构"。

重写后的每个文档类型模板包含：
1. **分析框架**：告诉 agent 用什么视角分析，分几个步骤
2. **深度锚点**：每个分析维度必须回答的核心问题（不是可选的，是必须回答的）
3. **输出结构**：严格的 Markdown 章节骨架 + 每节的必填项
4. **质量约束**：禁止罗列、要求解释设计意图、要求标注置信度

### 5.3 统一文档模板骨架

所有文档类型的 raw 产出必须遵循：

```markdown
# {文档标题}

> 置信度：{high/medium/low}
> 分析范围：{列出分析的关键文件/目录}

## 1. 文档目的

{一段话：这份文档回答什么问题，对谁有用}

## 2. 核心结论

{3-5 条关键发现，每条一句话}

## 3. 详细分析

{按文档类型的具体模板填充}

## 4. 典型场景

{至少 2 个具体场景，说明系统在真实使用中的行为}

## 5. 风险与限制

{当前设计的风险点、已知限制、待确认项}

## 6. 相关文档

{链接到其他相关 raw 文档}
```

### 5.4 各文档类型的深度模板

#### 5.4.1 overview — 项目总览

**分析框架**：

```
Step 1: 项目识别
  - 读取 README / package.json / pom.xml → 项目名称、目标、所属业务
  - 识别主要语言和框架

Step 2: 核心能力提取
  - 扫描入口文件 → 列出系统对外提供的核心能力
  - 每个能力必须说明：解决了什么问题、如何使用、关键实现文件

Step 3: 技术栈梳理
  - 依赖文件 → 列出核心依赖及用途
  - 区分框架依赖 / 工具依赖 / 业务依赖

Step 4: 阅读路径推荐
  - 根据仓库类型推荐文档阅读顺序
```

**深度锚点（必须回答）**：

| 锚点 | 问题 | 禁止 |
|------|------|------|
| 项目定位 | 这个项目为什么存在？解决什么痛点？ | 禁止只写"XX管理系统" |
| 核心能力 | 系统的 3-5 个核心能力是什么？每个能力解决什么场景？ | 禁止罗列功能列表 |
| 技术选型理由 | 为什么选这个框架/语言？有什么权衡？ | 禁止只写"使用 React" |
| 启动方式 | 本地如何启动？需要什么前置条件？ | 禁止只写 `npm start` |

**输出结构**：

```markdown
# 项目总览

## 1. 文档目的
## 2. 核心结论
## 3. 项目定位
### 3.1 解决的问题
### 3.2 核心能力
### 3.3 技术选型
## 4. 技术栈
### 4.1 框架与语言
### 4.2 核心依赖
### 4.3 构建与发布
## 5. 启动方式
### 5.1 本地启动
### 5.2 前置条件
## 6. 阅读路径
## 7. 风险与限制
## 8. 相关文档
```

#### 5.4.2 structure — 仓库结构

**分析框架**：

```
Step 1: 目录树构建
  - 生成精简的目录树（最深 3 层，忽略 node_modules/.git 等）
  - 标注每个目录的职责

Step 2: 入口识别
  - 识别所有入口文件（main/index/cli/app）
  - 标注入口类型（HTTP/CLI/cron/event）

Step 3: 模块划分
  - 识别逻辑模块（不等于目录模块）
  - 标注每个模块的职责和关键文件

Step 4: 依赖边界分析
  - 模块间依赖关系
  - 识别循环依赖
  - 标注共享模块
```

**深度锚点**：

| 锚点 | 问题 |
|------|------|
| 目录职责 | 每个顶层目录做什么？为什么这样组织？ |
| 入口文件 | 系统有哪些入口？每个入口服务什么场景？ |
| 依赖边界 | 模块间依赖是否合理？有没有循环依赖？ |
| 风险区域 | 哪些目录修改风险高？为什么？ |

#### 5.4.3 architecture — 架构设计

**分析框架**：

```
Step 1: 分层识别
  - 识别代码的分层方式（MVC/Clean Arch/DDD/自定义）
  - 画出分层图

Step 2: 模块依赖分析
  - 构建模块依赖图
  - 标注强依赖 vs 弱依赖
  - 识别循环依赖

Step 3: 调用链路追踪
  - 从入口追踪核心调用链（至少 3 条）
  - 画出调用时序

Step 4: 数据流分析
  - 识别数据从输入到输出的流转路径
  - 标注数据转换点

Step 5: 设计决策推断
  - 从代码结构推断设计决策
  - 解释为什么这样设计，而不是其他方式
```

**深度锚点**：

| 锚点 | 问题 |
|------|------|
| 分层方式 | 什么分层？为什么？每层的边界是什么？ |
| 模块依赖 | 核心模块依赖谁？谁依赖核心模块？有没有循环？ |
| 关键调用链 | 最重要的 3 条调用链是什么？经过哪些层？ |
| 设计决策 | 最关键的设计决策是什么？有什么权衡？ |
| 架构约束 | 修改代码时必须遵守什么约束？ |

#### 5.4.4 agent_system — Agent 架构

**分析框架**：

```
Step 1: Agent 生命周期分析
  - 识别 agent 的创建、调度、执行、销毁流程
  - 画出 agent 生命周期状态机

Step 2: 调度循环分析
  - 识别 agent 的核心循环（plan → execute → observe → reflect）
  - 每个阶段做什么？如何决策下一步？

Step 3: 子代理派发
  - 识别子代理创建和通信机制
  - 子代理的上下文隔离策略

Step 4: 上下文管理
  - 上下文如何构建、注入、裁剪
  - 上下文窗口管理策略

Step 5: 安全与权限
  - agent 的权限边界
  - 工具调用的审批机制
```

**深度锚点**：

| 锚点 | 问题 |
|------|------|
| 调度循环 | agent 的核心执行循环是什么？每步做什么决策？ |
| 上下文构建 | agent 如何获取和管理局部上下文？ |
| 子代理通信 | 父子代理如何通信？上下文如何隔离？ |
| 安全边界 | agent 能做什么？不能做什么？谁审批？ |

#### 5.4.5 tool_system — Tool 体系

**分析框架**：

```
Step 1: Tool 注册与发现
  - 识别所有 tool 定义
  - tool 的注册机制和发现方式

Step 2: Tool 路由
  - agent 如何选择调用哪个 tool？
  - 路由决策的输入是什么？

Step 3: Tool 执行
  - tool 的执行模型（同步/异步/流式）
  - 输入/输出格式
  - 错误处理

Step 4: 权限系统
  - tool 调用的权限控制
  - 用户审批机制
```

#### 5.4.6 plugin_system — 插件系统

**分析框架**：

```
Step 1: 插件生命周期
  - 插件的发现、加载、初始化、卸载
  - 插件的注册机制（skills/agents/hooks/commands/MCP）

Step 2: 插件交互模型
  - 插件与宿主的交互方式
  - 插件间的通信机制

Step 3: 扩展点
  - 宿主暴露了哪些扩展点？
  - 每个扩展点的契约是什么？

Step 4: 安全与隔离
  - 插件的权限边界
  - 插件故障的隔离策略
```

#### 5.4.7 context_system — 上下文系统

**分析框架**：

```
Step 1: 上下文层级
  - 识别所有上下文注入点（CLAUDE.md层级、memory、hooks注入）
  - 上下文的优先级和覆盖规则

Step 2: 上下文构建
  - 完整上下文如何组装？
  - 哪些部分是静态的？哪些是动态的？

Step 3: 上下文管理
  - 上下文窗口溢出时的裁剪策略
  - 语义检索如何工作？

Step 4: 持久化
  - 哪些上下文会持久化？
  - 跨会话的上下文恢复机制
```

#### 5.4.8 workflow_system — 工作流系统

**分析框架**：

```
Step 1: 工作流定义
  - 识别所有工作流/skill 定义
  - 工作流的步骤、检查点、条件分支

Step 2: 工作流引擎
  - 工作流的执行模型（线性/DAG/状态机）
  - 步骤间如何传递数据？

Step 3: 异常处理
  - 工作流步骤失败时的行为
  - 回滚和恢复机制

Step 4: 编排能力
  - 工作流间的组合和嵌套
  - 并行执行
```

#### 5.4.9 domain — 领域与业务

**分析框架**：

```
Step 1: 领域对象识别
  - 识别核心实体和值对象
  - 画出领域模型图

Step 2: 聚合边界
  - 识别聚合根和聚合边界
  - 聚合间通过什么方式通信？

Step 3: 状态流转
  - 识别核心业务对象的状态机
  - 什么事件触发状态变更？

Step 4: 业务规则
  - 识别关键业务规则（不变式、约束、验证规则）
  - 规则在哪里实现？

Step 5: 领域事件
  - 识别领域事件
  - 事件的发布和消费链路
```

#### 5.4.10 flows — 核心流程

**分析框架**：

```
Step 1: 流程识别
  - 识别所有核心业务流程
  - 按重要性和复杂度排序

Step 2: 主流程分析
  - 每个主流程的完整步骤
  - 关键类和方法
  - 画出调用时序

Step 3: 分支流程
  - 条件分支
  - 异常分支

Step 4: 异常处理
  - 每个步骤可能失败的方式
  - 失败后的处理策略
```

#### 5.4.11 api — 接口设计

**分析框架**：

```
Step 1: 接口分类
  - 按类型分类：HTTP / RPC / 消息消费 / CLI / 事件订阅

Step 2: 接口详情
  - 每个接口：路径、方法、入参、出参、鉴权
  - 标注幂等性和重试策略

Step 3: 错误码体系
  - 错误码分类和含义
  - 错误处理约定

Step 4: 接口演进
  - 版本策略
  - 兼容性约束
```

#### 5.4.12 data — 数据设计

**分析框架**：

```
Step 1: 存储概览
  - 列出所有存储层（DB / Cache / File / Queue）
  - 每个存储层的技术选型和用途

Step 2: 表/集合设计
  - 核心表结构
  - 字段含义和约束
  - 索引设计

Step 3: 数据流转
  - 数据从哪里来？到哪里去？
  - 读写路径

Step 4: 一致性策略
  - 数据一致性保障方式
  - 缓存失效策略
```

#### 5.4.13 config — 配置与运行

**分析框架**：

```
Step 1: 配置结构
  - 配置文件的组织方式
  - 配置项分类

Step 2: 环境划分
  - 不同环境的配置差异
  - 环境变量管理

Step 3: 本地运行
  - 完整的本地启动步骤
  - 前置依赖

Step 4: 排障入口
  - 常见配置问题
  - 健康检查方式
```

#### 5.4.14 deployment — 部署与运维

**分析框架**：

```
Step 1: 部署架构
  - 容器化方式
  - 依赖的基础设施

Step 2: CI/CD
  - 构建和发布流程
  - 环境提升策略

Step 3: 监控与告警
  - 监控指标
  - 告警规则

Step 4: 故障排查
  - 常见故障模式
  - 排查步骤
```

#### 5.4.15 testing — 测试与质量

**分析框架**：

```
Step 1: 测试结构
  - 测试分层（unit/integration/e2e）
  - 测试目录组织

Step 2: 测试策略
  - Mock 策略
  - 测试数据管理

Step 3: 覆盖分析
  - 覆盖率情况
  - 覆盖盲区

Step 4: CI 质量门禁
  - 质量检查项
  - 门禁规则
```

#### 5.4.16 risk — 风险与技术债

**分析框架**：

```
Step 1: 复杂度热点
  - 高圈复杂度的模块
  - 深度嵌套的逻辑

Step 2: 耦合分析
  - 强耦合的模块对
  - 循环依赖

Step 3: 重复代码
  - 重复或高度相似的代码模式

Step 4: 潜在风险
  - 缺少错误处理的代码路径
  - 并发安全问题
  - 性能瓶颈

Step 5: 改造建议
  - 优先级排序的改造建议
  - 每条建议的影响范围和成本估计
```

#### 5.4.17 glossary — 术语表

**分析框架**：

```
Step 1: 术语提取
  - 从代码标识符、注释、配置中提取术语
  - 分类：业务术语 / 技术术语 / 缩写

Step 2: 语义消歧
  - 同一概念的不同命名（同义词映射）
  - 同一命名的不同含义（歧义说明）

Step 3: 术语关系
  - 术语间的上下位关系
  - 术语缩写展开
```

#### 5.4.18 workspace — Workspace 架构

**分析框架**：

```
Step 1: Workspace 结构
  - apps / packages / tooling / infra 的划分
  - workspace 依赖原则

Step 2: Package 依赖图
  - package 间依赖关系
  - 核心基础包 vs 业务包
  - 循环依赖检测

Step 3: 构建编排
  - 构建工具和任务编排（turbo/nx/lerna）
  - 构建依赖图

Step 4: 共享策略
  - shared packages 的内容
  - 版本管理策略
```

### 5.5 子代理派发策略

**现有方式**：`/kb` 命令直接并行派发 extract-agent 处理各维度。

**重写后方式**：

```
doc-plan.json
    │
    ├─ 无依赖的文档（overview, structure, glossary）→ 并行派发
    │
    └─ 有依赖的文档 → 按依赖顺序串行派发
       例如：architecture 依赖 overview+structure → 等 overview 和 structure 完成后再派发
```

**并行度控制**：

- 第一波（无依赖）：overview, structure, glossary, workspace — 并行
- 第二波（依赖第一波）：architecture/agent_system, domain/tool_system, config — 并行
- 第三波（依赖第二波）：flows/workflow_system, api/plugin_system, data/context_system — 并行
- 第四波（依赖所有）：risk — 串行

**依赖信息来源**：doc-plan.json 中每个文档的 `depends_on` 字段。

**上下文传递格式**：被依赖文档完成后，提取其「核心结论」作为后续提取的输入。核心结论的格式：

```json
{
  "doc_id": "overview",
  "core_findings": ["发现1", "发现2", "发现3"],
  "key_entities": ["模块A", "模块B"],
  "confidence": "high"
}
```

后续子代理的 prompt 中注入所有 `depends_on` 文档的核心结论 JSON，而非全文——控制上下文窗口开销。

### 5.6 Extract 产出规范

**目录结构**：

```
raw/
  ├── 01-项目总览.md
  ├── 02-仓库结构.md
  ├── 02a-Workspace架构.md
  ├── 03a-Agent架构.md
  ├── 04a-Tool体系.md
  ├── 05a-插件系统.md
  ├── 06a-上下文系统.md
  ├── 07a-工作流系统.md
  ├── 11-风险与技术债.md
  └── 12-术语表.md
```

**质量约束**（写进每个 extract 技能的 prompt）：

1. **禁止空壳章节**：每个二级标题下必须有实质内容，不允许只写"待分析"
2. **禁止纯罗列**：不能只列出文件名/类名，必须解释设计意图和行为
3. **必须标注置信度**：文档顶部标注整体置信度（high/medium/low），不确定的结论加 `⚠️`
4. **必须提供典型场景**：至少 2 个具体使用场景，说明系统行为
5. **必须标注源文件**：关键分析结论必须引用源文件路径（如 `参见 src/agent/loop.ts:42`）
6. **必须回答深度锚点**：每个模板的"深度锚点"问题必须全部回答，不能跳过

---

## 6. Stage 4: TRANSFORM — 整合编排

### 6.1 职责

将 raw 碎片整合为 wiki 文档 + 知识图谱。核心是从"独立提取"到"连贯知识"的升华。

### 6.2 Transform 子步骤

```
raw/
    │
    ├─ Step 1: 术语归一
    │   读取所有 raw 文档 + glossary → 构建统一术语映射表
    │   对所有 raw 文档做术语替换和统一
    │
    ├─ Step 2: 交叉引用
    │   扫描所有 raw 文档 → 识别跨文档引用点
    │   在文档间插入双向链接
    │
    ├─ Step 3: 一致性校验
    │   检查不同文档中对同一概念的描述是否矛盾
    │   标注冲突 → 生成冲突报告
    │
    ├─ Step 4: 文档编排
    │   按 doc-plan.json 的编号顺序编排 wiki 文档
    │   添加文档间的导航链接
    │   生成目录索引
    │
    ├─ Step 5: 知识图谱构建
    │   从 raw 文档提取实体和关系
    │   构建 graph.json
    │
    └─ 输出: wiki/ + graph.json
```

### 6.3 术语归一

**输入**：所有 raw 文档 + glossary

**处理**：

1. 从 glossary 提取规范术语和同义词映射
2. 扫描所有 raw 文档，将非规范术语替换为规范术语
3. 为首次出现的术语添加 glossary 链接

**输出**：术语归一后的 raw 文档（原地更新）

### 6.4 交叉引用

**输入**：术语归一后的 raw 文档

**处理**：

1. 识别跨文档引用点（同一模块/类/概念在不同文档中被提及）
2. 在提及处插入 `→ 参见 [[02-仓库结构#模块划分]]` 格式的链接
3. 生成引用关系矩阵

**引用规则**：

| 源文档 | 目标文档 | 引用场景 |
|--------|----------|----------|
| overview | structure | 提到模块时 |
| architecture | domain | 提到领域对象时 |
| architecture | flows | 提到调用链时 |
| flows | api | 提到接口调用时 |
| flows | data | 提到数据操作时 |
| risk | *所有* | 提到风险模块时反向链接 |

### 6.5 一致性校验

**输入**：交叉引用后的 raw 文档

**检查项**：

| 检查项 | 说明 |
|--------|------|
| 术语一致性 | 同一概念在不同文档中的命名是否一致 |
| 描述一致性 | 对同一模块/类的行为描述是否矛盾 |
| 依赖一致性 | A 文档说 X 依赖 Y，B 文档是否也这样说 |
| 编号连续性 | 文档编号是否有缺失 |

**冲突处理**：

- 可自动解决的（术语不一致）→ 自动修复
- 无法自动解决的（描述矛盾）→ 生成冲突标记 `⚠️ [冲突]` 并在 wiki 文档中标注

### 6.6 文档编排

**输入**：通过一致性校验的 raw 文档 + doc-plan.json

**处理**：

1. 按 doc-plan.json 的编号顺序编排
2. 在每份 wiki 文档顶部添加导航：
   ```markdown
   ← 上一篇：01-项目总览 | **02-仓库结构** | 下一篇：03-架构设计 →
   ```
3. 生成 wiki 目录索引 `wiki/00-目录.md`
4. Agent/Platform 专用文档按逻辑位置插入（02a 在 02 后，03a 替代 03）

**输出目录**：

```
wiki/
  ├── 00-目录.md
  ├── 01-项目总览.md
  ├── 02-仓库结构.md
  ├── 02a-Workspace架构.md
  ├── 03a-Agent架构.md
  ├── 04a-Tool体系.md
  ├── 05a-插件系统.md
  ├── 06a-上下文系统.md
  ├── 07a-工作流系统.md
  ├── 11-风险与技术债.md
  └── 12-术语表.md
```

### 6.7 知识图谱构建

**输入**：所有 raw 文档 + repo-profile.json

**处理**：

1. **实体提取**：从每份文档提取核心实体（模块、类、接口、数据表、流程、概念）
2. **关系提取**：识别实体间关系（依赖、调用、包含、实现、数据流）
3. **层级构建**：按仓库结构构建实体层级（仓库 → 模块 → 类/函数）
4. **属性丰富**：为每个实体附加来源文档、置信度、关键属性

**graph.json Schema**：

```json
{
  "nodes": [
    {
      "id": "string",
      "type": "module | class | function | interface | table | flow | concept",
      "label": "string",
      "layer": "string",
      "source_doc": "string",
      "confidence": "high | medium | low",
      "properties": {}
    }
  ],
  "edges": [
    {
      "source": "string (node id)",
      "target": "string (node id)",
      "type": "depends_on | calls | contains | implements | data_flows_to | references",
      "label": "string",
      "source_doc": "string"
    }
  ],
  "layers": [
    {
      "id": "string",
      "name": "string",
      "description": "string"
    }
  ]
}
```

---

## 7. Stage 5: LOAD — 数据加载

### 7.1 职责

将 raw + wiki + graph 转换为站点可消费的格式。

### 7.2 Load 子步骤

```
raw/ + wiki/ + graph.json
    │
    ├─ Step 1: 搜索索引构建
    │   读取 raw/ 所有文档 → 构建 Fuse.js 搜索索引
    │   输出: search-index.json
    │
    ├─ Step 2: 图谱数据转换
    │   读取 graph.json → 转换为 d3-force 可消费的节点/边格式
    │   计算布局参数
    │   输出: graph-data.json
    │
    └─ Step 3: 站点数据部署
      将 raw/ + wiki/ + search-index.json + graph-data.json 复制到站点数据目录
      触发站点重新构建
```

### 7.3 站点三视图数据源

| 视图 | 数据源 | 展示方式 |
|------|--------|----------|
| Raw View | raw/ 目录 | Markdown 渲染，按文档类型浏览 |
| Wiki View | wiki/ 目录 | Markdown 渲染，按编号顺序浏览，带导航和交叉引用 |
| Graph View | graph-data.json | d3-force 力导向图，可交互 |

---

## 8. 技能/代理/命令重写清单

### 8.1 技能重写

| 现有技能 | 动作 | 对应新设计 |
|----------|------|-----------|
| scan | **重写** | Stage 1: SCAN — 输出 repo-profile.json |
| extract | **重写** | Stage 3: EXTRACT 的路由器，读取 doc-plan 派发子代理 |
| extract-topology | **删除** | 合并到 architecture/workspace 的深度模板中 |
| extract-api | **重写** | → api 文档类型的深度模板 |
| extract-data-model | **重写** | → data 文档类型的深度模板 |
| extract-flows | **重写** | → flows 文档类型的深度模板 |
| extract-concepts | **删除** | 合并到 glossary + domain 的深度模板中 |
| cross-ref | **重写** | → Stage 4: TRANSFORM 的交叉引用子步骤 |
| ingest | **重写** | → Stage 4: TRANSFORM 的术语归一 + 一致性校验 |
| transform | **重写** | → Stage 4: TRANSFORM 的编排入口 |
| build-search-index | **保留** | Stage 5 的搜索索引构建，适配新的 raw 目录结构 |
| build-graph | **重写** | → Stage 4 的知识图谱构建，使用新的 graph.json schema |
| serve | **保留** | 站点服务，适配三视图数据源 |

**新增技能**：

| 新技能 | 说明 |
|--------|------|
| plan | Stage 2: PLAN — 画像驱动的文档规划 |
| extract-overview | overview 文档类型的深度模板 |
| extract-structure | structure 文档类型的深度模板 |
| extract-architecture | architecture 文档类型的深度模板 |
| extract-domain | domain 文档类型的深度模板 |
| extract-agent-system | agent_system 文档类型的深度模板 |
| extract-tool-system | tool_system 文档类型的深度模板 |
| extract-plugin-system | plugin_system 文档类型的深度模板 |
| extract-context-system | context_system 文档类型的深度模板 |
| extract-workflow-system | workflow_system 文档类型的深度模板 |
| extract-workspace | workspace 文档类型的深度模板 |
| extract-config | config 文档类型的深度模板 |
| extract-deployment | deployment 文档类型的深度模板 |
| extract-testing | testing 文档类型的深度模板 |
| extract-risk | risk 文档类型的深度模板 |
| extract-glossary | glossary 文档类型的深度模板 |

### 8.2 代理重写

| 现有代理 | 动作 | 新设计 |
|----------|------|--------|
| extract-agent | **重写** | 通用提取代理，接收文档类型 + 深度模板 + 范围提示，输出 raw 文档 |
| transform-agent | **重写** | 通用转换代理，接收 transform 子步骤类型，执行术语归一/交叉引用/一致性校验 |

### 8.3 命令重写

| 现有命令 | 动作 | 新设计 |
|----------|------|--------|
| /kb | **重写** | 六步检查点编排，适配五阶段管道 |

**/kb 命令新流程**：

```
Step 1: SCAN
  扫描仓库 → 输出 repo-profile.json
  检查点：用户确认画像是否准确

Step 2: PLAN
  基于画像 → 输出 doc-plan.json
  检查点：用户确认文档集和提取顺序

Step 3: EXTRACT（第一波：无依赖文档）
  并行派发 extract-agent → 输出 raw 文档
  检查点：展示产出，用户确认质量

Step 4: EXTRACT（第二波+：有依赖文档）
  按依赖顺序派发 extract-agent → 输出 raw 文档
  检查点：展示产出，用户确认质量

Step 5: TRANSFORM
  术语归一 → 交叉引用 → 一致性校验 → 文档编排 → 知识图谱
  检查点：展示 wiki 产出 + graph 摘要

Step 6: LOAD
  搜索索引 → 图谱数据 → 站点部署
  检查点：站点可访问
```

---

## 9. 架构决策记录

### ADR-1: 画像驱动 vs 固定维度

- **决策**：采用画像驱动（repo-profile → doc-plan → 动态文档集）
- **替代方案**：保留固定 5 维度（topology/api/data-model/flows/concepts）
- **理由**：固定维度无法适应不同仓库类型，导致大量空壳文档和维度重叠。画像驱动能根据仓库实际特征产出有价值的文档
- **后果**：scan 阶段变重，但整体产出质量显著提升

### ADR-2: 保留 raw/wiki 双层

- **决策**：保留 raw（原始提取）和 wiki（整合文档）双层
- **替代方案**：只产出 wiki 单层
- **理由**：raw 保留提取的原始粒度，支持站点 Raw View；wiki 提供 整合后的连贯阅读体验。两层各司其职
- **后果**：存储翻倍，但站点展示更丰富

### ADR-3: Transform + Load 分离

- **决策**：Transform（raw → wiki + graph）和 Load（数据转站点格式）分开
- **替代方案**：合并为一个阶段
- **理由**：Transform 是内容加工（语义操作），Load 是数据格式转换（技术操作），职责不同。分离后可独立重跑
- **后果**：多一个阶段，但可增量更新

### ADR-4: 文档类型模板 vs 自由提取

- **决策**：每种文档类型有严格的深度模板（分析框架 + 深度锚点 + 输出结构）
- **替代方案**：只给 agent 文档标题和简要说明，让它自由发挥
- **理由**：自由提取导致质量不稳定、深度参差不齐。模板强制 agent 回答关键问题、遵循分析框架
- **后果**：灵活性降低，但质量可控

### ADR-5: Agent/Platform 专用文档 vs 通用文档扩展

- **决策**：为 agent/tool/plugin/context/workflow 系统设立专用文档类型
- **替代方案**：在 architecture 文档中加章节覆盖
- **理由**：Agent 系统的核心关注点与传统 CRUD 架构完全不同（调度循环、上下文管理、工具路由 vs 分层调用、数据流转），放在同一文档中会两头不深
- **后果**：文档类型增多，但每份文档深度更专

---

## 10. V1 实施范围

### 10.1 V1 必须实现的模板

| 优先级 | 文档类型 | 说明 |
|--------|----------|------|
| P0 | overview, structure, risk, glossary | 通用必出 |
| P0 | architecture | 通用条件出（大多数仓库满足 modules > 3） |
| P0 | agent_system | Agent/Platform 项目核心 |
| P1 | tool_system, plugin_system | Agent/Platform 项目关键 |
| P1 | api, data, flows | 传统后端项目关键 |
| P2 | workspace, context_system, workflow_system | 大型项目增强 |
| P2 | config, deployment, testing | 运维/质量增强 |

### 10.2 V1 范围

- 实现 P0 + P1 共 11 种模板（overview, structure, risk, glossary, architecture, agent_system, tool_system, plugin_system, api, data, flows）
- P2 模板用简化占位模板（只含统一骨架），待 V2 深化
- scan 阶段识别全部 6 种 repo_type
- plan 阶段支持全部条件生成规则

---

## 11. 风险与待确认项

| 风险 | 影响 | 缓解 |
|------|------|------|
| Scan 画像准确度不足 | 后续所有阶段产出偏移 | 添加用户确认检查点，支持手动修正画像 |
| P2 模板简化导致产出浅 | workspace/context/workflow 文档深度不足 | V1 先跳过这些文档，不生成空壳 |
| 子代理上下文窗口不足 | 深度分析受限 | 只传被依赖文档的核心结论 JSON，不传全文 |
| Transform 交叉引用质量 | 人工定义规则可能遗漏 | 优先保证通用引用规则，特殊引用由 agent 自行发现 |
| graph.json schema 变更 | 站点展示需适配 | 保持节点/边基础结构不变，属性可扩展 |
| raw/wiki 编号相同可能混淆 | 两个目录下有同名文件 | raw 和 wiki 目录隔离，站点视图区分清晰 |
