# KB 插件深度重写设计文档

> 日期：2026-05-26
> 状态：设计阶段
> 核心问题：Extract 阶段 prompt 过浅 + 维度固定一刀切 + 全链路质量不达标

---

## 1. 设计目标

1. **画像驱动**：先扫描仓库特征，再决定生成什么文档——不同仓库产出不同文档集
2. **复杂度驱动深度**：基础文档保证覆盖面，深度文档从代码复杂度热点中"长出来"——不是固定模板，而是从代码中发现的具体问题/模式
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
│  职责: 结构扫描 + 框架识别 + 能力检测 + 复杂度热点发现        │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 2: PLAN                                              │
│  输入: repo-profile.json                                     │
│  输出: doc-plan.json                                         │
│  职责: 基础文档 + 深度文档规划（复杂度热点驱动）               │
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
| 维度划分 | 固定 5 维（topology/api/data-model/flows/concepts） | 基础文档（固定）+ 深度文档（复杂度热点驱动） |
| Scan 输出 | 文件列表 + 语言统计 | repo-profile.json（仓库画像 + 复杂度热点） |
| 中间编排 | 无（直接跑所有 extract） | doc-plan.json（基础文档 + 深度文档规划） |
| Extract 产出 | 自由格式 Markdown | 统一骨架 + 热点类型指引驱动的结构化 Markdown |
| Transform | 仅 cross-ref 关联 | 交叉引用 + 一致性校验 + 术语归一 + 文档编排 |
| 站点数据源 | raw + wiki + graph | raw + wiki + graph（保持三视图） |

---

## 3. Stage 1: SCAN — 仓库画像与复杂度热点

### 3.1 职责

扫描仓库，产出结构化画像 **和复杂度热点**。只观察，不决策——决策留给 PLAN 阶段。

### 3.2 扫描内容

| 扫描维度 | 检测项 | 检测方法 |
|----------|--------|----------|
| 技术栈 | 主要语言、框架、运行时 | 文件扩展名统计 + package.json/pom.xml/pyproject.toml 解析 |
| 仓库类型 | backend/frontend/sdk/platform/agent/tool | 框架特征 + 目录结构 + 入口模式 |
| 代码组织 | 分层架构 / DDD / Clean Arch / 模块化单体 / Monorepo | 目录模式匹配 + 层间依赖检测 |
| 能力特征 | has_api / has_db / has_queue / has_auth / has_plugin_system / has_agent_runtime / has_workflow / has_frontend / has_scheduler / has_ai | 特征文件 + 目录 + 依赖包检测 |
| 复杂度指标 | 模块数量 / 包深度 / 入口数量 / 调用链长度 / 外部依赖数量 | 文件统计 + import 分析 |
| 关键资产 | API 入口 / 数据模型 / 配置文件 / 部署描述 | 路径模式匹配 |
| **复杂度热点** | 复杂状态机 / 深层调用链 / 核心抽象 / 一致性机制 / 工作流 / 并发模式 | 模式检测 + 结构分析 |

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

### 3.4 复杂度热点发现

**这是 SCAN 阶段的核心新增能力。**

复杂度热点不是"模块 A 有 50 个文件"——而是"模块 A 中的订单状态机有 8 种状态、15 条转换、3 种异常分支，是整个系统最核心也最脆弱的部分"。

#### 3.4.1 热点类型

| 热点类型 | 识别信号 | 典型场景 |
|----------|----------|----------|
| `state_machine` | 多个状态字段 + 状态转换方法 + 状态校验逻辑 | 订单状态流转、审批流、发布流程 |
| `call_chain` | 深层调用（>4 层）+ 跨模块/服务调用 + 异步回调 | 支付链路、数据管道、Agent 调度循环 |
| `core_abstraction` | 抽象层 + 多种实现 + 注册/发现机制 + 生命周期管理 | 插件系统、Tool 体系、策略模式集群 |
| `consistency` | 事务管理 + 补偿逻辑 + 幂等设计 + 最终一致性保障 | 分布式事务、数据同步、缓存一致性 |
| `workflow` | 步骤编排 + 检查点 + 条件分支 + 回滚逻辑 | TDD 工作流、CI/CD、Skill 编排 |
| `concurrency` | 锁机制 + 并发控制 + 异步队列 + 竞态条件处理 | 并发调度、资源池、消息消费 |
| `data_pipeline` | 多源输入 + 转换链 + 输出路由 + 错误恢复 | ETL 管道、数据同步、日志处理 |
| `security_boundary` | 权限检查 + 审批机制 + 沙箱隔离 + 资源访问控制 | Tool 权限、多租户隔离、API 鉴权 |

#### 3.4.2 热点识别方法

```
对每个模块:
  1. 扫描文件结构 → 识别模式信号
     - state_machine: 搜索 status/state 字段 + transition/advance/flow 方法
     - call_chain: 追踪入口调用的深度 + 跨模块调用次数
     - core_abstraction: 识别 interface/abstract + impl/adapter 目录结构
     - consistency: 搜索 transaction/compensate/idempotent 关键词
     - workflow: 识别 step/checkpoint/phase/rollback 模式
     - concurrency: 识别 lock/mutex/queue/async/await/semaphore
     - data_pipeline: 识别 source/transform/sink/pipeline 模式
     - security_boundary: 识别 permission/authorize/sandbox/isolate

  2. 评估复杂度
     - 状态数 × 转换数 × 异常分支数 → state_machine 复杂度
     - 调用深度 × 跨模块数 × 异步比例 → call_chain 复杂度
     - 实现数 × 交互点 × 生命周期步骤 → core_abstraction 复杂度
     - ...

  3. 过滤阈值
     - 复杂度低于阈值的热点不输出（避免简单模式被标记为热点）
     - 同一模块的多个热点合并（如一个模块既有状态机又有调用链）

  4. 生成热点描述
     - 一句话说明这个热点为什么复杂
     - 涉及的关键文件
     - 建议的深度文档标题
```

#### 3.4.3 热点示例

**订单系统**：
```json
{
  "type": "state_machine",
  "module": "order",
  "description": "订单状态机有 8 种状态、15 条转换路径，含支付回调异常、超时取消、部分退款等边界场景",
  "key_files": ["src/order/order.entity.ts", "src/order/order.service.ts", "src/order/state-machine.ts"],
  "suggested_title": "订单生命周期深度解析"
}
```

**Claude Code 插件项目**：
```json
{
  "type": "core_abstraction",
  "module": "plugins",
  "description": "插件系统有 skills/agents/hooks/commands/MCP 五种扩展点，每种有独立生命周期和交互协议",
  "key_files": ["plugins/superpowers-pro/skills/", "plugins/kb/agents/", "plugins/kb/hooks/"],
  "suggested_title": "插件机制深度解析"
}
```

### 3.5 repo-profile.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["repo_name", "repo_type", "primary_language", "frameworks", "architecture_style", "complexity_level", "capabilities", "entry_points", "modules", "complexity_hotspots"],
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
    },
    "complexity_hotspots": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "module", "description", "key_files", "suggested_title"],
        "properties": {
          "type": {
            "type": "string",
            "enum": ["state_machine", "call_chain", "core_abstraction", "consistency", "workflow", "concurrency", "data_pipeline", "security_boundary"]
          },
          "module": { "type": "string" },
          "description": { "type": "string", "description": "一句话说明为什么这个热点值得深度分析" },
          "key_files": { "type": "array", "items": { "type": "string" } },
          "suggested_title": { "type": "string", "description": "建议的深度文档标题" }
        }
      }
    }
  }
}
```

---

## 4. Stage 2: PLAN — 基础文档 + 深度文档规划

### 4.1 职责

基于仓库画像和复杂度热点，规划两类文档：
1. **基础文档**：固定的小集合，保证覆盖面
2. **深度文档**：从复杂度热点生长，标题和范围由热点决定

### 4.2 文档类型体系

#### 4.2.1 基础文档（所有仓库必须生成）

| ID | 文档名 | 编号 | 说明 |
|----|--------|------|------|
| `overview` | 项目总览 | 01 | 项目目标、核心能力、技术栈、阅读路径 |
| `structure` | 仓库结构 | 02 | 目录树、模块职责、入口文件、依赖边界 |
| `risk` | 风险与技术债 | 11 | 高复杂度模块、强耦合、技术债、改造建议 |
| `glossary` | 术语表 | 12 | 业务术语、技术术语、缩写、同义词映射 |

**为什么只保留 4 份基础文档？**

原来设计有 12-18 种通用模板（架构设计、领域与业务、核心流程、接口设计、数据设计...），但问题是：同一个模板套在不同仓库上要么太空（没有领域模型的仓库生成"领域与业务"文档），要么太浅（有复杂领域模型的仓库用一个通用模板无法覆盖）。通用模板只能回答"有什么"，不能回答"难点在哪"。

深度文档承担了这个责任——它不是"架构设计"这种笼统的标题，而是"订单生命周期深度解析"、"Agent 调度循环深度解析"这种从代码中长出来的具体标题。

#### 4.2.2 深度文档（从复杂度热点生长）

深度文档不是预设的固定列表——每个仓库的深度文档都不一样。

**生成规则**：repo-profile.json 中的每个 complexity_hotspot 生成一份深度文档。

**文档标题**：取自热点的 `suggested_title` 字段。

**文档编号**：从 03 开始，按逻辑顺序编排（overview=01, structure=02, 深度文档=03/04/05/..., risk=11, glossary=12）。

**示例**：

**订单系统**的深度文档：
| 编号 | 标题 | 来源热点 |
|------|------|----------|
| 03 | 订单生命周期深度解析 | state_machine: 订单状态机 |
| 04 | 支付回调异常处理 | call_chain: 支付链路 |
| 05 | 库存一致性保障机制 | consistency: 库存扣减 |
| 06 | 接口设计 | call_chain: API 调用链 |

**Claude Code 插件项目**的深度文档：
| 编号 | 标题 | 来源热点 |
|------|------|----------|
| 03 | Agent 调度循环深度解析 | call_chain: Agent 执行循环 |
| 04 | Skill 编排检查点机制 | workflow: Skill 工作流 |
| 05 | 插件机制深度解析 | core_abstraction: 插件系统 |
| 06 | Tool 权限审批流程 | security_boundary: Tool 权限 |

### 4.3 doc-plan.json Schema

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
        "required": ["id", "type", "title", "number", "reason"],
        "properties": {
          "id": { "type": "string", "description": "文档唯一标识" },
          "type": {
            "type": "string",
            "enum": ["baseline", "deep_analysis"],
            "description": "baseline=基础文档，deep_analysis=深度文档"
          },
          "title": { "type": "string" },
          "number": { "type": "string", "description": "编排编号，如 01, 03, 11" },
          "reason": { "type": "string", "description": "为什么生成这份文档" },
          "hotspot_type": {
            "type": "string",
            "description": "深度文档对应的热点类型（仅 deep_analysis 类型）",
            "enum": ["state_machine", "call_chain", "core_abstraction", "consistency", "workflow", "concurrency", "data_pipeline", "security_boundary"]
          },
          "scope_hint": { "type": "string", "description": "提取时的范围提示" },
          "key_files": {
            "type": "array",
            "items": { "type": "string" },
            "description": "深度文档涉及的关键文件（仅 deep_analysis 类型）"
          },
          "depends_on": {
            "type": "array",
            "items": { "type": "string" },
            "description": "依赖的其他文档 ID"
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

### 4.4 doc-plan 示例

**Claude Code 插件项目（agentic_platform）**：

```json
{
  "profile_ref": "repo-profile.json",
  "documents": [
    { "id": "overview", "type": "baseline", "title": "项目总览", "number": "01", "reason": "基础文档" },
    { "id": "structure", "type": "baseline", "title": "仓库结构", "number": "02", "reason": "基础文档" },
    { "id": "agent-loop", "type": "deep_analysis", "title": "Agent 调度循环深度解析", "number": "03", "reason": "核心调度机制，整个系统的心脏", "hotspot_type": "call_chain", "scope_hint": "追踪 Agent 从接收消息到完成响应的完整循环，包括 plan→execute→observe→reflect 各阶段的决策逻辑", "key_files": ["src/agent/loop.ts", "src/agent/planner.ts", "src/agent/executor.ts"], "depends_on": ["overview", "structure"] },
    { "id": "skill-orchestration", "type": "deep_analysis", "title": "Skill 编排检查点机制", "number": "04", "reason": "工作流驱动系统，定义了开发流程的硬性约束", "hotspot_type": "workflow", "scope_hint": "分析 skill 的步骤编排、检查点机制、条件分支、失败回滚", "key_files": ["plugins/superpowers-pro/skills/brainstorming/SKILL.md", "plugins/superpowers-pro/skills/test-driven-development/SKILL.md"], "depends_on": ["overview"] },
    { "id": "plugin-system", "type": "deep_analysis", "title": "插件机制深度解析", "number": "05", "reason": "五种扩展点（skills/agents/hooks/commands/MCP）有独立生命周期和交互协议", "hotspot_type": "core_abstraction", "scope_hint": "分析插件的发现、加载、生命周期、扩展点契约、安全隔离", "key_files": ["plugins/superpowers-pro/", "plugins/kb/"], "depends_on": ["agent-loop"] },
    { "id": "tool-permission", "type": "deep_analysis", "title": "Tool 权限审批流程", "number": "06", "reason": "权限边界决定了 Agent 能做什么、不能做什么", "hotspot_type": "security_boundary", "scope_hint": "分析 tool 调用的权限控制、用户审批机制、沙箱隔离", "key_files": ["src/tools/permission.ts", "src/tools/sandbox.ts"], "depends_on": ["agent-loop"] },
    { "id": "risk", "type": "baseline", "title": "风险与技术债", "number": "11", "reason": "基础文档", "depends_on": ["agent-loop", "plugin-system", "tool-permission"] },
    { "id": "glossary", "type": "baseline", "title": "术语表", "number": "12", "reason": "基础文档" }
  ],
  "extraction_order": ["overview", "structure", "glossary", "agent-loop", "skill-orchestration", "plugin-system", "tool-permission", "risk"]
}
```

**订单系统（backend_service）**：

```json
{
  "profile_ref": "repo-profile.json",
  "documents": [
    { "id": "overview", "type": "baseline", "title": "项目总览", "number": "01", "reason": "基础文档" },
    { "id": "structure", "type": "baseline", "title": "仓库结构", "number": "02", "reason": "基础文档" },
    { "id": "order-lifecycle", "type": "deep_analysis", "title": "订单生命周期深度解析", "number": "03", "reason": "8 种状态、15 条转换、3 种异常分支——系统最核心也最脆弱的部分", "hotspot_type": "state_machine", "scope_hint": "追踪订单从创建到完成的全生命周期，包括支付回调异常、超时取消、部分退款等边界场景", "key_files": ["src/order/order.entity.ts", "src/order/order.service.ts", "src/order/state-machine.ts"], "depends_on": ["overview", "structure"] },
    { "id": "payment-callback", "type": "deep_analysis", "title": "支付回调异常处理", "number": "04", "reason": "调用链跨越 3 个服务，有异步回调和重试逻辑", "hotspot_type": "call_chain", "scope_hint": "追踪支付发起→第三方回调→订单状态变更→库存确认的完整链路", "key_files": ["src/payment/payment.service.ts", "src/payment/callback.controller.ts"], "depends_on": ["order-lifecycle"] },
    { "id": "inventory-consistency", "type": "deep_analysis", "title": "库存一致性保障机制", "number": "05", "reason": "库存扣减+订单创建需要分布式事务保障，有补偿逻辑", "hotspot_type": "consistency", "scope_hint": "分析库存扣减的事务策略、失败场景、补偿机制、幂等设计", "key_files": ["src/inventory/inventory.service.ts", "src/inventory/compensation.ts"], "depends_on": ["order-lifecycle"] },
    { "id": "api-design", "type": "deep_analysis", "title": "接口设计", "number": "06", "reason": "有 30+ HTTP 接口，需要系统化梳理", "hotspot_type": "call_chain", "scope_hint": "按资源分类梳理接口，重点分析鉴权、幂等、错误码", "key_files": ["src/controller/"], "depends_on": ["overview"] },
    { "id": "risk", "type": "baseline", "title": "风险与技术债", "number": "11", "reason": "基础文档", "depends_on": ["order-lifecycle", "payment-callback", "inventory-consistency"] },
    { "id": "glossary", "type": "baseline", "title": "术语表", "number": "12", "reason": "基础文档" }
  ],
  "extraction_order": ["overview", "structure", "glossary", "api-design", "order-lifecycle", "payment-callback", "inventory-consistency", "risk"]
}
```

---

## 5. Stage 3: EXTRACT — 基础提取 + 深度分析

### 5.1 职责

根据 doc-plan.json，按文档类型派生子代理。基础文档用基础模板，深度文档用统一深度骨架 + 热点类型指引。

### 5.2 提取策略

**核心设计：两层模板体系**

- **基础文档模板**：4 份固定模板（overview/structure/risk/glossary），每份有专属的分析框架和深度锚点
- **深度文档模板**：统一深度分析骨架 + 热点类型指引。骨架是所有深度文档共用的写作框架，指引根据热点类型定制分析侧重点

### 5.3 统一文档骨架

所有文档（基础和深度）的 raw 产出必须遵循：

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

### 5.4 深度分析骨架（所有 deep_analysis 文档共用）

```markdown
# {从热点 suggested_title 生成的标题}

> 置信度：{high/medium/low}
> 分析范围：{hotspot.key_files}
> 热点类型：{hotspot.type}

## 1. 问题定义

{这个复杂度热点是什么？为什么它难？为什么值得深入理解？}

## 2. 核心结论

{3-5 条关键发现}

## 3. 当前实现

{代码中是如何处理的？逐步追踪关键路径}
### 3.1 关键路径追踪
{从入口到出口的完整调用/状态/流转路径，带文件路径和行号}
### 3.2 核心机制解析
{支撑这个热点运作的核心机制——不是罗列代码，而是解释设计意图}

## 4. {热点类型专属章节}

{根据 hotspot.type 插入的定制章节，见 5.5}

## 5. 关键设计决策

{设计者做了什么取舍？为什么这样而不是那样？有哪些隐含约束？}

## 6. 异常与边界

{什么情况下会出问题？失败场景有哪些？如何恢复？}
### 6.1 已知的失败场景
### 6.2 恢复与补偿机制
### 6.3 尚未处理的边界

## 7. 典型场景

{至少 2 个具体场景，展示系统在真实使用中的行为}

## 8. 改进方向

{可能的优化方向、风险和成本}

## 9. 代码证据

{关键路径的文件路径 + 行号，带简要说明}

## 10. 相关文档

{链接到其他相关 raw 文档}
```

### 5.5 热点类型指引

每种热点类型在深度分析骨架的第 4 章插入定制内容：

#### state_machine 指引

**第 4 章：状态流转深度分析**

```markdown
## 4. 状态流转深度分析

### 4.1 状态定义
{列出所有状态，每个状态的含义和业务语义}

### 4.2 转换规则
{列出所有合法的状态转换，每个转换的触发条件}
| 当前状态 | 目标状态 | 触发事件 | 前置条件 | 实现位置 |
|----------|----------|----------|----------|----------|

### 4.3 状态转换图
{Mermaid stateDiagram-v2}

### 4.4 异常状态处理
{非法状态转换的防护、状态不一致的检测与修复}

### 4.5 状态查询与监控
{如何查询当前状态、状态变更的审计日志}
```

#### call_chain 指引

**第 4 章：调用链深度分析**

```markdown
## 4. 调用链深度分析

### 4.1 调用时序
{Mermaid sequenceDiagram，展示完整调用链}

### 4.2 各层职责
{调用链中每个节点的职责和边界}

### 4.3 跨边界调用
{跨模块/跨服务调用的协议、序列化、错误传播}

### 4.4 超时与重试
{各环节的超时设置、重试策略、降级方案}

### 4.5 异步与回调
{异步调用的模式、回调处理、结果聚合}
```

#### core_abstraction 指引

**第 4 章：抽象体系深度分析**

```markdown
## 4. 抽象体系深度分析

### 4.1 扩展点清单
{列出所有扩展点/扩展方式}

### 4.2 生命周期
{每种实现的创建→初始化→使用→销毁流程}

### 4.3 注册与发现
{如何注册实现、如何被发现和选择}

### 4.4 交互协议
{扩展点与宿主的交互接口和契约}

### 4.5 组合与冲突
{多种扩展点组合使用的规则、冲突检测}
```

#### consistency 指引

**第 4 章：一致性机制深度分析**

```markdown
## 4. 一致性机制深度分析

### 4.1 一致性策略
{使用什么一致性模型？为什么？}

### 4.2 事务边界
{事务的边界在哪？跨哪些资源？}

### 4.3 失败场景
{每个步骤可能失败的方式和影响}

### 4.4 补偿机制
{失败后的补偿逻辑、幂等设计}

### 4.5 最终一致性保障
{异步场景下如何保证最终一致？对账机制？}
```

#### workflow 指引

**第 4 章：工作流深度分析**

```markdown
## 4. 工作流深度分析

### 4.1 步骤编排
{完整步骤列表、每步的输入/输出/检查点}

### 4.2 条件分支
{哪些步骤有条件分支？条件是什么？}

### 4.3 检查点机制
{哪些步骤有硬性检查点？不通过时如何处理？}

### 4.4 回滚策略
{步骤失败后的回滚逻辑}

### 4.5 并行步骤
{哪些步骤可以并行执行？如何聚合结果？}
```

#### concurrency 指引

**第 4 章：并发模型深度分析**

```markdown
## 4. 并发模型深度分析

### 4.1 并发模型
{使用什么并发模型？线程池？协程？事件循环？}

### 4.2 锁与同步
{锁的粒度、类型、获取顺序}

### 4.3 竞态条件
{可能产生竞态的场景和防护}

### 4.4 死锁检测
{死锁的可能性和检测/预防机制}
```

#### data_pipeline 指引

**第 4 章：数据管道深度分析**

```markdown
## 4. 数据管道深度分析

### 4.1 数据源
{数据从哪里来？格式是什么？}

### 4.2 转换链
{每个转换步骤的输入/输出/转换逻辑}

### 4.3 输出路由
{数据输出到哪里？路由规则？}

### 4.4 错误恢复
{管道步骤失败时的重试、跳过、补偿策略}
```

#### security_boundary 指引

**第 4 章：安全边界深度分析**

```markdown
## 4. 安全边界深度分析

### 4.1 权限模型
{权限如何定义？角色？策略？}

### 4.2 审批机制
{什么操作需要审批？审批流程？}

### 4.3 沙箱隔离
{哪些操作在沙箱中执行？隔离策略？}

### 4.4 资源访问控制
{文件/网络/进程等资源的访问控制规则}
```

### 5.6 基础文档模板

#### 5.6.1 overview — 项目总览

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

#### 5.6.2 structure — 仓库结构

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

#### 5.6.3 risk — 风险与技术债

**分析框架**：

```
Step 1: 复杂度热点
  - 从 repo-profile.json 的 complexity_hotspots 提取高风险点
  - 结合已有 deep_analysis 文档的风险发现

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

#### 5.6.4 glossary — 术语表

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

### 5.7 子代理派发策略

```
doc-plan.json
    │
    ├─ 无依赖的文档（overview, structure, glossary）→ 并行派发
    │
    └─ 有依赖的文档 → 按依赖顺序派发
       例如：agent-loop 依赖 overview+structure → 等两者完成后再派发
```

**并行度控制**：

- 第一波（无依赖）：overview, structure, glossary — 并行
- 第二波（依赖第一波）：所有 depends_on 仅含第一波文档的深度文档 — 并行
- 第三波（依赖第二波）：depends_on 含第二波文档的深度文档 — 并行
- 逐波推进，直到所有文档完成

**依赖信息来源**：doc-plan.json 中每个文档的 `depends_on` 字段。

**上下文传递格式**：被依赖文档完成后，提取其核心结论作为后续提取的输入：

```json
{
  "doc_id": "overview",
  "core_findings": ["发现1", "发现2", "发现3"],
  "key_entities": ["模块A", "模块B"],
  "confidence": "high"
}
```

后续子代理的 prompt 中注入所有 `depends_on` 文档的核心结论 JSON，而非全文——控制上下文窗口开销。

### 5.8 Extract 产出规范

**目录结构**：

```
raw/
  ├── 01-项目总览.md
  ├── 02-仓库结构.md
  ├── 03-Agent调度循环深度解析.md
  ├── 04-Skill编排检查点机制.md
  ├── 05-插件机制深度解析.md
  ├── 06-Tool权限审批流程.md
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
7. **深度文档必须追踪关键路径**：从入口到出口的完整路径，带文件路径和行号

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
2. 在提及处插入 `→ 参见 [[03-Agent调度循环深度解析#核心机制]]` 格式的链接
3. 生成引用关系矩阵

**引用规则**：

| 源文档 | 目标文档 | 引用场景 |
|--------|----------|----------|
| overview | structure | 提到模块时 |
| deep_analysis | deep_analysis | 提到其他热点涉及的模块/机制时 |
| deep_analysis | risk | 提到风险模块时反向链接 |
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
   ← 上一篇：01-项目总览 | **02-仓库结构** | 下一篇：03-订单生命周期深度解析 →
   ```
3. 生成 wiki 目录索引 `wiki/00-目录.md`
4. 深度文档按热点逻辑位置编排（在 structure 后、risk 前）

**输出目录**：

```
wiki/
  ├── 00-目录.md
  ├── 01-项目总览.md
  ├── 02-仓库结构.md
  ├── 03-Agent调度循环深度解析.md
  ├── 04-Skill编排检查点机制.md
  ├── 05-插件机制深度解析.md
  ├── 06-Tool权限审批流程.md
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
      "type": "module | class | function | interface | table | flow | concept | hotspot",
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
| scan | **重写** | Stage 1: SCAN — 输出 repo-profile.json（含复杂度热点） |
| extract | **重写** | Stage 3: EXTRACT 的路由器，读取 doc-plan 派发子代理 |
| extract-topology | **删除** | 功能由深度文档的 call_chain 热点类型覆盖 |
| extract-api | **删除** | 功能由深度文档的 call_chain/security_boundary 热点类型覆盖 |
| extract-data-model | **删除** | 功能由深度文档的 consistency/data_pipeline 热点类型覆盖 |
| extract-flows | **删除** | 功能由深度文档的 state_machine/workflow 热点类型覆盖 |
| extract-concepts | **删除** | 功能由 glossary 基础文档覆盖 |
| cross-ref | **重写** | → Stage 4: TRANSFORM 的交叉引用子步骤 |
| ingest | **重写** | → Stage 4: TRANSFORM 的术语归一 + 一致性校验 |
| transform | **重写** | → Stage 4: TRANSFORM 的编排入口 |
| build-search-index | **保留** | Stage 5 的搜索索引构建，适配新的 raw 目录结构 |
| build-graph | **重写** | → Stage 4 的知识图谱构建，使用新的 graph.json schema |
| serve | **保留** | 站点服务，适配三视图数据源 |

**新增技能**：

| 新技能 | 说明 |
|--------|------|
| plan | Stage 2: PLAN — 基础文档 + 深度文档规划 |
| extract-overview | overview 基础文档模板 |
| extract-structure | structure 基础文档模板 |
| extract-risk | risk 基础文档模板 |
| extract-glossary | glossary 基础文档模板 |
| extract-deep | 深度文档通用模板（统一深度骨架 + 热点类型指引） |

**关键变化**：不再为每种文档类型创建独立技能。深度文档只用一个 `extract-deep` 技能，通过 hotspot_type 参数选择对应的指引。基础文档各有专属技能（因为模板差异大）。

### 8.2 代理重写

| 现有代理 | 动作 | 新设计 |
|----------|------|--------|
| extract-agent | **重写** | 通用提取代理，接收文档类型（baseline/deep_analysis）+ 模板 + 热点类型 + 范围提示 + 依赖文档核心结论，输出 raw 文档 |
| transform-agent | **重写** | 通用转换代理，接收 transform 子步骤类型，执行术语归一/交叉引用/一致性校验 |

### 8.3 命令重写

| 现有命令 | 动作 | 新设计 |
|----------|------|--------|
| /kb | **重写** | 六步检查点编排，适配五阶段管道 |

**/kb 命令新流程**：

```
Step 1: SCAN
  扫描仓库 → 输出 repo-profile.json（含复杂度热点）
  检查点：用户确认画像和热点是否准确

Step 2: PLAN
  基于画像 + 热点 → 输出 doc-plan.json（基础文档 + 深度文档）
  检查点：用户确认文档集和提取顺序

Step 3: EXTRACT（第一波：无依赖文档）
  并行派发 extract-agent → 输出 raw 文档
  检查点：展示产出，用户确认质量

Step 4: EXTRACT（后续波：有依赖文档）
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

### ADR-1: 基础文档 + 深度文档双层

- **决策**：文档分为基础层（固定 4 种）和深度层（复杂度热点驱动）
- **替代方案 A**：全部用固定模板（原设计 12-18 种通用模板）
- **替代方案 B**：全部用发现式提取（无固定文档）
- **理由**：纯固定模板无法体现仓库特异性的复杂度（订单系统的核心难点是状态机，插件系统的核心难点是抽象体系，这不是同一个模板能覆盖的）；纯发现式又缺乏兜底，简单仓库可能什么深度文档都发现不了。双层混合保证覆盖面的同时允许深度文档从代码中"长出来"
- **后果**：SCAN 阶段需要增加复杂度热点识别能力；PLAN 阶段逻辑更复杂

### ADR-2: 深度文档用统一骨架 + 热点类型指引

- **决策**：所有深度文档共用统一深度分析骨架，通过 hotspot_type 参数插入定制章节
- **替代方案**：每种热点类型有独立模板
- **理由**：深度文档的核心写作框架是相同的（问题定义→当前实现→设计决策→异常边界→改进方向），差异只在分析侧重点（状态机关注转换规则、调用链关注时序和重试、抽象体系关注生命周期和注册机制）。统一骨架 + 指引既保证结构一致性，又允许分析重点不同
- **后果**：只需维护一个 extract-deep 技能 + 8 种热点类型指引

### ADR-3: 保留 raw/wiki 双层

- **决策**：保留 raw（原始提取）和 wiki（整合文档）双层
- **替代方案**：只产出 wiki 单层
- **理由**：raw 保留提取的原始粒度，支持站点 Raw View；wiki 提供 transform 后的连贯阅读体验。两层各司其职
- **后果**：存储翻倍，但站点展示更丰富

### ADR-4: Transform + Load 分离

- **决策**：Transform（raw → wiki + graph）和 Load（数据转站点格式）分开
- **替代方案**：合并为一个阶段
- **理由**：Transform 是内容加工（语义操作），Load 是数据格式转换（技术操作），职责不同。分离后可独立重跑
- **后果**：多一个阶段，但可增量更新

### ADR-5: 删除原有 5 维度 extract 技能

- **决策**：删除 extract-topology/api/data-model/flows/concepts，由深度文档覆盖
- **替代方案**：保留原有维度作为"基础文档"的一部分
- **理由**：原 5 维度的职责已被深度文档完全覆盖且更深入——topology 由 call_chain 热点覆盖、api 由 call_chain/security_boundary 覆盖、data-model 由 consistency/data_pipeline 覆盖、flows 由 state_machine/workflow 覆盖、concepts 由 glossary 覆盖。保留会导致职责重叠
- **后果**：技能总数减少（5 个 extract-* → 1 个 extract-deep + 4 个 baseline extract）

---

## 10. V1 实施范围

### 10.1 V1 必须实现

| 优先级 | 组件 | 说明 |
|--------|------|------|
| P0 | scan（含复杂度热点发现） | 核心能力，驱动后续所有阶段 |
| P0 | plan | 基础文档 + 深度文档规划 |
| P0 | extract-deep（含全部 8 种热点类型指引） | 深度文档核心 |
| P0 | extract-overview, extract-structure | 基础文档 |
| P0 | transform（术语归一 + 交叉引用 + 一致性校验 + 文档编排） | raw → wiki 升华 |
| P1 | extract-risk, extract-glossary | 基础文档 |
| P1 | build-graph（使用新 schema） | 知识图谱 |
| P1 | /kb 命令重写 | 六步检查点编排 |
| P2 | load（搜索索引 + 图谱数据转换） | 站点集成 |
| P2 | 站点适配 | 三视图适配新数据结构 |

### 10.2 V1 热点类型指引优先级

| 优先级 | 热点类型 | 理由 |
|--------|----------|------|
| P0 | state_machine, call_chain, core_abstraction | 最常见、价值最高 |
| P1 | consistency, workflow | 中等常见 |
| P2 | concurrency, data_pipeline, security_boundary | 特定场景 |

P2 热点类型在 V1 中用简化指引（只含核心章节，不含完整子章节），V2 深化。

---

## 11. 风险与待确认项

| 风险 | 影响 | 缓解 |
|------|------|------|
| 复杂度热点识别准确度不足 | 深度文档可能关注错误方向 | 用户确认检查点，支持手动增删热点 |
| P2 热点指引简化导致产出浅 | 并发/管道/安全文档深度不足 | V1 先跳过这些热点，不生成空壳文档 |
| 子代理上下文窗口不足 | 深度分析受限 | 只传被依赖文档的核心结论 JSON，不传全文 |
| Transform 交叉引用质量 | 人工定义规则可能遗漏 | 优先保证通用引用规则，特殊引用由 agent 自行发现 |
| graph.json schema 变更 | 站点展示需适配 | 保持节点/边基础结构不变，属性可扩展 |
| 深度文档标题由热点 suggested_title 生成 | 标题可能不够精确 | 用户可在 PLAN 检查点修改标题 |
| 基础文档只有 4 种 | 对仓库的"广度覆盖"可能不足 | 深度文档已经承担了架构/模块/流程等内容的覆盖 |
