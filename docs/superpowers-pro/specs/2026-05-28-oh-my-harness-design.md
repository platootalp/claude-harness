# oh-my-harness 编排插件设计文档

> 基于 oh-my-claudecode (OMC) v4.14.4 架构，为 harness-marketplace 构建的多代理编排插件

## 1. 项目定位

**oh-my-harness** 是一个混合架构的 Claude Code 编排插件，提供多代理协作、持久执行模式、状态管理和团队编排能力。与 superpowers-pro 的"结构化工作流纪律"互补，oh-my-harness 专注"多代理自主编排"。

### 与 superpowers-pro 的关系

| 维度 | superpowers-pro | oh-my-harness |
|------|----------------|---------------|
| 定位 | 结构化工作流纪律 | 多代理自主编排 |
| 代理模型 | 临时子代理 | 19 个命名代理 + 模型路由 |
| 执行模式 | 8 步线性管道 + 人类检查点 | 持久循环 + 自主执行 |
| 状态管理 | 会话内文本检查点 | 文件持久化 + 崩溃恢复 |
| 适用场景 | 需要人类审批的结构化开发 | 需要自主执行的大规模任务 |

**冲突解决**：
- 命名空间隔离：`superpowers-pro:brainstorming` vs `oh-my-harness:ralph`
- 魔法关键词优先：oh-my-harness 的关键词检测优先于 superpowers-pro 的技能发现
- 状态目录隔离：superpowers-pro 无状态文件，oh-my-harness 使用 `.omh/`
- Hook 不冲突：两个插件注册同一事件的独立钩子，Claude Code 依次执行

**使用场景选择**：
- "一步步走、每步审批" → superpowers-pro 的 `/feature`、`/fix`
- "自主执行、持续循环" → oh-my-harness 的 `autopilot`、`ralph`
- "多人并行" → oh-my-harness 的 `team`

## 2. 整体架构

```
plugins/oh-my-harness/
  .claude-plugin/plugin.json       # 插件清单 + hooks + MCP 注册
  agents/                          # 19 命名代理（Markdown 定义）
  skills/                          # 工作流技能（Markdown）
  commands/                        # 斜杠命令（Markdown）
  hooks/                           # 生命周期钩子（.mjs）
  src/                             # TypeScript 编排引擎
    index.ts                       # 入口：createOmhSession()
    agents/definitions.ts          # 代理元数据 + 提示词加载
    config/                        # 配置加载、模型路由
    features/                      # 核心特性模块
      keyword-detector/            # 魔法关键词检测
      persistent-mode/             # 持久模式（Sisyphus 循环）
      state-manager/               # 状态管理
      mode-registry/               # 模式注册表
      delegation-enforcer/         # 代理委派强制
      context-injector/            # 上下文注入
    hooks/                         # 钩子实现
    lib/                           # 工具函数
      atomic-write.ts              # 原子写入
      mode-state-io.ts             # 模式状态 I/O
      session-isolation.ts         # 会话隔离
      paths.ts                     # 路径管理
    mcp/                           # MCP 服务器
      tools-server.ts              # 内置 MCP 工具
    team/                           # 团队编排
      unified-team.ts              # 统一团队编排
      inbox-outbox.ts              # 收发箱 IPC
    tools/                         # MCP 工具实现
      state.ts                     # state_read/write/clear
      notepad.ts                   # notepad_read/write
      memory.ts                    # project_memory_*
  bridge/                          # 编译产物（bundled CJS）
  scripts/                         # 构建和运行脚本
```

**核心设计原则**（从 OMC 提炼）：
1. **Hook-driven orchestration**：8 个生命周期钩子拦截所有关键事件
2. **Sisyphus persistence**：持久模式钩子阻止过早停止
3. **Compositional skill hierarchy**：技能分层组合而非重复
4. **READ-ONLY analysis agents**：分析代理不能写入代码
5. **File-based state + atomic writes**：状态持久化 + 崩溃恢复
6. **Session isolation**：会话间状态隔离

## 3. Agent 系统

### 3.1 代理分层

19 个命名代理，3 个模型层级：

| 层级 | 模型 | 代理 | 职责 |
|------|------|------|------|
| **Opus（战略层）** | opus | architect, critic, planner, analyst, code-reviewer | 只读分析，不修改代码 |
| **Sonnet（执行层）** | sonnet | executor, debugger, designer, tracer, verifier, test-engineer, security-reviewer, qa-tester, scientist, git-master | 实现和验证 |
| **Haiku（探测层）** | haiku | explorer, writer | 低成本上下文收集和文档 |

### 3.2 代理定义格式

```yaml
---
name: architect
description: Strategic analysis and debugging advisor
model: opus
level: 3
disallowedTools: [Write, Edit]
---
# Architect Agent

You are a strategic analysis agent. Your role:
- Provide architectural guidance and debugging advice
- Cite file:line for all references
- Provide steelman antithesis in review contexts
- NEVER modify code — you are READ-ONLY
```

### 3.3 关键设计

- **只读代理**：architect、critic、planner 禁用 Write/Edit，强制分析与实现分离
- **代理委派路由**：主代理根据任务类型自动选择最合适的代理
- **模型路由**：按任务复杂度路由到不同模型层级（Haiku 探索 → Sonnet 实现 → Opus 规划）
- **3-failure 升级**：executor 失败 3 次后自动升级到 architect

## 4. Hook 系统

### 4.1 生命周期钩子

| 事件 | 钩子脚本 | 职责 |
|------|---------|------|
| **UserPromptSubmit** | `keyword-detector.mjs`, `skill-injector.mjs` | 检测魔法关键词，注入已学习技能 |
| **SessionStart** | `session-start.mjs`, `project-memory-session.mjs` | 恢复持久模式状态，加载项目记忆 |
| **PreToolUse** | `pre-tool-enforcer.mjs` | 注入上下文提醒，强制代理工具限制，模型路由验证 |
| **PermissionRequest** | `permission-handler.mjs` | 自动批准/拒绝 Bash 权限请求 |
| **PostToolUse** | `post-tool-verifier.mjs`, `project-memory-posttool.mjs` | 验证提醒，项目记忆积累 |
| **SubagentStart/Stop** | `subagent-tracker.mjs` | 子代理生命周期追踪 |
| **PreCompact** | `pre-compact.mjs`, `project-memory-precompact.mjs` | 压缩前保存关键状态 |
| **Stop** | `persistent-mode.mjs`, `context-guard-stop.mjs` | Sisyphus 持久循环，阻止过早停止 |

### 4.2 Sisyphus 持久模式

核心机制：Stop 事件触发时，检查 `.omh/state/{mode}-state.json` 是否有活跃模式。

- 如果模式活跃，输出继续指令，阻止 Claude 停止
- 安全限制：`OMH_SECURITY=strict` 时硬性最大迭代次数（默认 200）
- 模式完成时：`/cancel` 清除所有状态文件

### 4.3 魔法关键词

优先级排序：

`cancelomh` > `ralph` > `autopilot` > `team` > `ultrawork`/`ulw` > `ralplan` > `deep-interview` > `tdd` > `code-review` > `security-review` > `ultrathink` > `deepsearch` > `analyze`

## 5. 技能系统

### 5.1 组合式层级

```
ultrawork（并行执行层）
  └── ralph（添加持久循环 + PRD 驱动 + 验证）
       └── autopilot（添加完整生命周期：扩展 → 规划 → 执行 → QA → 验证）
```

### 5.2 核心技能

| 技能 | 层级 | 职责 | 组合关系 |
|------|------|------|---------|
| **ultrawork** | 基础 | 并行执行引擎，按任务复杂度路由模型层级 | 独立 |
| **ralph** | 中层 | PRD 驱动持久循环，逐 story 迭代直到全部通过 | 包含 ultrawork |
| **autopilot** | 顶层 | 全自主 5 阶段：扩展 → 规划 → 执行 → QA → 验证 | 包含 ralph |
| **ralplan** | 规划 | 共识规划：Planner → Architect → Critic 循环（最多 5 轮） | ralph 前置 |
| **team** | 编排 | 多 worker 并行执行，支持 Claude/Codex/Gemini 混合 | 独立 |
| **ultraqa** | QA | 质量保证流水线 | 被 autopilot 调用 |

### 5.3 辅助技能

| 技能 | 职责 |
|------|------|
| deep-interview | 需求访谈和 PRD 生成 |
| ai-slop-cleaner | AI 生成代码清理 |
| tdd | 测试驱动开发 |
| code-review | 代码审查 |
| security-review | 安全审查 |
| writer-memory | 跨会话记忆持久化 |
| project-memory | 项目级知识管理 |

### 5.4 技能调用方式

1. 斜杠命令：`/oh-my-harness:autopilot`
2. 魔法关键词：输入 `autopilot`、`ralph` 等触发
3. CLI 命令：`omh team 3:executor "fix all TS errors"`

### 5.5 技能详细设计

#### autopilot

全自主 5 阶段流水线：

1. **Expansion** — deep-interview 扩展需求，生成 spec
2. **Planning** — ralplan 共识规划，产出实施计划
3. **Execution** — ralph 持久循环执行，逐 story 实现
4. **QA** — ultraqa 质量保证，多视角验证
5. **Validation** — 多代理交叉验证（architect + critic + verifier）

状态文件：`.omh/autopilot/spec.md`、`.omh/plans/autopilot-impl.md`

#### ralph

PRD 驱动持久循环：

- 逐 story 迭代 `prd.json`，直到全部 story 通过验收标准
- 会话作用域 PRD：`.omh/state/sessions/{sessionId}/prd.json`
- 每个 story 完成前验证验收标准（新鲜证据）
- 审查者选择：`--critic=architect|critic|codex`
- 批准后强制 deslop（调用 ai-slop-cleaner）
- deslop 后回归验证

7.5 步链：approval → deslop → regression → cancel（永不在 approval 暂停）

#### ralplan

共识规划循环：

- Planner → Architect → Critic 循环，最多 5 轮
- RALPLAN-DR 结构化审议（Principles, Decision Drivers, Viable Options）
- 前置门控：拦截模糊的 ralph/autopilot/team 请求
- `--interactive` 模式：在草案审查和批准时 AskUserQuestion
- `--deliberate` 模式：高风险工作的 pre-mortem + 扩展测试计划

#### team

多 worker 并行编排：

- 分阶段流水线：team-plan → team-prd → team-exec → team-verify → team-fix（循环）
- 混合执行：Claude agent + Codex CLI（tmux）+ Gemini CLI（tmux）
- 每角色 provider/model 路由：`.claude/omh.jsonc` team.roleRouting
- Git worktree 隔离 MCP worker
- Worker 前导协议：claim → work → complete → report → next
- Outbox/inbox JSONL 消息用于 CLI worker
- 动态缩放：`OMH_TEAM_SCALING_ENABLED=1`

#### ultrawork

并行执行引擎：

- 同时派发独立代理
- 模型层级路由：Haiku（简单）、Sonnet（标准）、Opus（复杂）
- 构建/测试后台执行
- 可组合：ralph 包含 ultrawork，autopilot 包含 ralph

## 6. 状态管理

### 6.1 状态文件布局

```
.omh/
  state/
    {mode}-state.json          # 模式激活状态（ralph-state.json 等）
    sessions/{sessionId}/      # 会话作用域状态
      prd.json                 # Ralph PRD
      skill-active-state.json  # 技能活跃状态账本
    team/
      {teamName}/              # 团队运行时状态
        tasks/{id}.json        # 任务文件
        events.jsonl           # 事件日志
        workers/{name}/        # worker 状态/心跳
    boulder.json               # 进度追踪
    mission-state.json         # 任务面板
  notepads/{plan-name}/       # 便签文件
  plans/                       # 计划文件
  research/                    # 研究产物
  handoffs/                    # 阶段交接文档
  worktrees/{team}/{worker}/  # 团队 Git worktree 隔离
```

### 6.2 核心机制

- **原子写入**：所有状态写入使用 write-to-temp + rename，防止崩溃时部分写入
- **会话隔离**：状态按 sessionId 隔离，防止跨会话干扰
- **项目隔离**：状态目录在项目根目录（`.omh/`），不同项目互不干扰
- **TTL 缓存**：读取缓存 5 秒 TTL，最大 200 条，防止频繁磁盘 I/O
- **文件锁**：O_EXCL 锁文件，跨进程原子读-修改-写
- **过期清理**：活跃状态默认 4 小时 TTL，自动清理陈旧状态

### 6.3 MCP 状态工具

| 工具 | 用途 |
|------|------|
| `state_read` | 读取模式状态 |
| `state_write` | 写入模式状态 |
| `state_clear` | 清除指定模式状态 |
| `state_list_active` | 列出所有活跃模式 |
| `state_get_status` | 获取当前模式状态摘要 |

## 7. MCP 工具层

MCP 工具服务器注册为 `omh`，通过 `bridge/mcp-server.cjs` 提供。

| 类别 | 工具 | 用途 |
|------|------|------|
| **状态** | `state_read/write/clear/list_active/get_status` | 模式状态管理 |
| **便签** | `notepad_read/write_priority/write_working/write_manual` | 代理间知识共享 |
| **记忆** | `project_memory_read/write/add_note/add_directive` | 项目级持久记忆 |
| **LSP** | `hover`, `goto_definition`, `find_references`, `diagnostics`, `completion`, `document_symbols`, `workspace_symbols`, `type_definition`, `call_hierarchy_incoming`, `call_hierarchy_outgoing`, `folding_range`, `selection_range` | 代码智能（12 个工具） |
| **AST** | `grep_search/grep_replace` | 结构化代码搜索/替换 |
| **Python** | `python_repl` | Python REPL 执行 |
| **共享内存** | `shared_memory_read/write` | 跨代理共享状态 |

## 8. Team 编排

### 8.1 Leader-Worker 模式

- 1 个 leader 代理分发任务，N 个 worker 并行执行
- 混合执行：支持 Claude agent + Codex CLI（tmux）+ Gemini CLI（tmux）

### 8.2 Worker 生命周期

```
claim → work → complete → report → next
```

### 8.3 通信机制

- **Claude worker**：通过 SendMessage 通信
- **CLI worker**（Codex/Gemini）：通过 inbox/outbox JSONL 文件通信，字节偏移游标实现拉取式监控

### 8.4 隔离和安全

- **Git Worktree 隔离**：每个 worker 独立 worktree，完成后合并
- **动态缩放**：`OMH_TEAM_SCALING_ENABLED=1` 时根据任务量动态调整 worker 数量
- **安全约束**：team 模式有特定的 worker 访问限制

### 8.5 Team 流水线

```
team-plan → team-prd → team-exec → team-verify → team-fix（循环）
```

## 9. CLI 命令（omh）

`omh` 是一个 Node.js CLI 入口（`scripts/omh.ts` → 编译为 `bridge/omh.mjs`），通过 `node bridge/omh.mjs` 调用。

支持命令：
- `omh team <N>:<role> "<task>"` — 启动 team 编排
- `omh status` — 查看当前活跃模式和状态
- `omh cancel` — 取消所有活跃模式
- `omh config` — 查看/编辑配置

通过 `package.json` 的 `bin` 字段注册，`npm install -g` 后可直接使用。

## 10. 配置系统

配置文件：`.claude/omh.jsonc`（JSON with Comments），支持项目级和用户级（`~/.claude/omh.jsonc`）。

```jsonc
{
  // 模型路由
  "modelRouting": {
    "default": "sonnet",
    "agents": {
      "architect": "opus",
      "explorer": "haiku"
    }
  },
  // Team 角色路由
  "team": {
    "roleRouting": {
      "executor": { "provider": "claude", "model": "sonnet" },
      "reviewer": { "provider": "codex", "model": "o3" }
    },
    "maxWorkers": 5,
    "scalingEnabled": false
  },
  // 持久模式
  "persistentMode": {
    "maxIterations": 200,
    "securityLevel": "standard"  // "standard" | "strict"
  },
  // LSP 集成
  "lsp": {
    "enabled": true,
    "servers": {
      "typescript": "typescript-language-server"
    }
  }
}
```

配置加载优先级：项目级 `.claude/omh.jsonc` > 用户级 `~/.claude/omh.jsonc` > 内置默认值。

## 11. 编排流（端到端）

1. **用户输入**进入：CLI、斜杠命令、魔法关键词、自然语言
2. **UserPromptSubmit 钩子**：keyword-detector 检测关键词，skill-injector 注入技能
3. **编排器钩子**：确定激活哪个代理/模式
4. **代理委派**：按任务类型和复杂度选择代理（带模型层级）
5. **模式激活**：持久模式触发时，状态写入 `.omh/state/`
6. **执行循环**：代理工作，persistent-mode 钩子阻止过早停止
7. **质量控制钩子**：在关键检查点验证输出
8. **状态持久化**：模式状态持续更新
9. **后处理钩子**：输出格式化、恢复、通知
10. **完成**：模式退出条件满足时，persistent-mode 钩子允许 Stop 事件

## 12. 目标用户（渐进式覆盖）

1. **个人开发者**：用 Claude Code 做日常开发，希望自动化更多流程
2. **团队协作**：共享代理配置、工作流模板、状态同步
3. **插件开发者**：用编排能力构建更复杂的插件生态

## 13. 技术栈

- **编排引擎**：TypeScript（src/），编译为 bundled CJS（bridge/）
- **代理/技能/命令**：Markdown（.md 文件 + YAML frontmatter）
- **钩子**：ESM JavaScript（.mjs）
- **MCP 服务器**：TypeScript，通过 `@anthropic-ai/claude-agent-sdk` 的 `createSdkMcpServer`
- **构建**：esbuild（`scripts/build.ts`），入口 `src/index.ts`，输出到 `bridge/omh.cjs`（MCP server）+ `bridge/omh.mjs`（CLI）
- **状态存储**：文件系统（JSON + JSONL），原子写入
