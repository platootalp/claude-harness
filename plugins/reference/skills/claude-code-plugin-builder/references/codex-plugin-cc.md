# codex-plugin-cc 参考实现解析

> Reference: https://github.com/openai/codex-plugin-cc

openai/codex-plugin-cc 是一个生产级的 Claude Code 插件，将 OpenAI Codex 集成进来做代码审查和任务委托。其架构设计是构建复杂插件的最佳参考模板。

---

## 目录结构

```
plugins/codex/
├── .claude-plugin/
│   └── plugin.json              # 插件清单
├── commands/                     # slash 命令（.md 文件）
│   ├── review.md                # 标准代码审查
│   ├── adversarial-review.md   # 对抗性审查（质疑设计决策）
│   ├── rescue.md                # 任务委托
│   ├── setup.md                 # 环境检查
│   ├── status.md                # 后台任务状态
│   ├── cancel.md                # 取消任务
│   └── result.md                # 查看结果
├── agents/                       # 子 agent 定义
│   └── codex-rescue.md
├── skills/                       # 插件内嵌 skill（供 agent 调用）
│   ├── codex-cli-runtime/
│   │   └── SKILL.md            # companion 脚本调用接口
│   ├── codex-result-handling/
│   │   └── SKILL.md            # 输出呈现规范
│   └── gpt-5-4-prompting/
│       ├── SKILL.md
│       └── references/
├── prompts/                      # hook 脚本用的 prompt 模板
│   ├── adversarial-review.md
│   └── stop-review-gate.md
├── hooks/
│   └── hooks.json               # SessionStart / SessionEnd / Stop hooks
├── scripts/                     # 核心运行时（Node.js）
│   ├── codex-companion.mjs      # CLI 桥接器 — 所有命令的入口
│   ├── session-lifecycle-hook.mjs  # 会话生命周期 hook 处理器
│   ├── stop-review-gate-hook.mjs    # 停止时审查门
│   ├── app-server-broker.mjs
│   └── lib/                         # 共享模块
│       ├── app-server.mjs
│       ├── broker-lifecycle.mjs
│       ├── state.mjs
│       ├── job-control.mjs
│       ├── process.mjs
│       └── workspace.mjs
├── schemas/
│   └── review-output.schema.json
├── package.json
└── tsconfig.app-server.json
```

**核心原则**：只有 `plugin.json` 放在 `.claude-plugin/` 下，其余全部在插件根目录。

---

## 核心架构模式

### 1. Companion Script（companion script 设计）

`scripts/codex-companion.mjs` 是整个插件的核心运行时，负责：
- 解析命令行参数
- 管理后台任务生命周期（spawn / track PIDs / 写入 state.json）
- 与外部服务通信（App Server / CLI）
- 输出结构化结果

```javascript
// 关键模式：子进程管理
const child = spawn(process.execPath, [scriptPath, "task", "--json", prompt], {
  cwd,
  env: childEnv,
  encoding: "utf8",
  timeout: STOP_REVIEW_TIMEOUT_MS
});

// 关键模式：Job 状态持久化
state.jobs.push({ id, sessionId, status: "running", pid });
saveState(workspaceRoot, state);
```

### 2. 命令 Frontmatter 控制

Commands 使用 YAML frontmatter 控制 Claude Code 的行为：

```markdown
---
---
description: Check the status of Codex background jobs
argument-hint: '[job-id]'
disable-model-invocation: true        # 禁用 Claude LLM，仅执行脚本
allowed-tools: Bash(node:*)           # 白名单工具
---

!`node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" status "$ARGUMENTS"`
```

| 字段 | 作用 |
|:---|:---|
| `description` | 用户输入命令时显示的提示 |
| `argument-hint` | 参数格式提示 |
| `disable-model-invocation` | `true` 时 Claude 不会自行调用 LLM，仅执行脚本 |
| `allowed-tools` | 白名单具体工具，防止 agent 越界 |

### 3. 子 Agent 设计（thin forwarder 模式）

`agents/codex-rescue.md` 定义了一个薄转发 agent：

```markdown
---
name: codex-rescue
model: sonnet
tools: Bash
skills: codex-cli-runtime, gpt-5-4-prompting
---

You are a thin forwarder. Your only job is to invoke the companion script once and return its output.

Rules:
- Use the companion script for ALL work
- Do not inspect the repo, solve the task, or add analysis
- Return stdout exactly as-is
```

### 4. 插件内嵌 Skill

`skills/` 目录下的 skill 是插件私有的，供内部 agent 调用（通过 `skills:` frontmatter 引用）：

- **codex-cli-runtime** — 规范了 companion 脚本的调用方式
- **codex-result-handling** — 规范了如何向用户呈现输出（保留原文verbatim、不自动修复、显式询问）

### 5. Hook 系统

`hooks/hooks.json` 定义了三种 hook：

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup",
      "hooks": [{
        "type": "command",
        "command": "node \"${CLAUDE_PLUGIN_ROOT}/scripts/session-lifecycle-hook.mjs\" SessionStart",
        "timeout": 5
      }]
    }],
    "SessionEnd": [{ ... }],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "node \"${CLAUDE_PLUGIN_ROOT}/scripts/stop-review-gate-hook.mjs\"",
        "timeout": 900,
        "statusMessage": "Running stop-time review..."
      }]
    }]
  }
}
```

**SessionStart/SessionEnd**：管理 broker session 生命周期，清理孤儿任务。

**Stop**：停止时审查门（gate）。hook 脚本通过 stdout 输出 JSON 决策：

```javascript
// 阻止：emitDecision({ decision: "block", reason: "..." })
// 允许：emitDecision({ decision: "allow" })
```

### 6. Hook 脚本与主会话的数据传递

Hook 输入通过 stdin 传递 JSON：

```javascript
function readHookInput() {
  const raw = fs.readFileSync(0, "utf8").trim();
  return JSON.parse(raw);
}

// 在 hook 中读取 session_id
const { session_id, cwd, last_assistant_message } = readHookInput();
```

SessionEnd 通过 `${CLAUDE_PLUGIN_DATA}/state.json` 读取任务状态，通过环境变量 `${CODEX_COMPANION_SESSION_ID}` 关联任务与会话。

---

## 核心能力：任务委托机制详解

这是该插件最核心的能力——在 Claude Code 中将任务委托给 Codex 执行。

### 完整调用链路

```
用户输入 /codex:rescue "帮我修复这个 bug"
    ↓
commands/rescue.md → 调用 codex:codex-rescue 子 agent
    ↓
codex:codex-rescue (agents/codex-rescue.md)
  - thin forwarder 模式：只做转发，不自己分析
  - 调用 codex-companion.mjs task
    ↓
scripts/codex-companion.mjs task
  - 解析参数（--resume, --fresh, --write 等）
  - 检查是否有可恢复的 thread
  - 写入 state.json 创建 job 记录
    ↓
  - 调用 CodexAppServerClient
    ↓
scripts/lib/app-server.mjs
  两种连接模式：
  1. Broker 模式：Unix socket 连接到已有的 broker 进程
  2. Direct Spawn：直接 spawn `codex app-server` 子进程
    ↓
  JSON-RPC over JSONL 协议
  - request/response 通过 stdin/stdout
  - notification (streaming delta) 通过回调处理
    ↓
Codex App Server (codex CLI 内置)
  执行实际的 LLM 推理 + 代码操作
```

### 1. Thin Forwarder 模式（核心约束）

`agents/codex-rescue.md` 定义了子 agent 的行为约束——**绝不自己分析代码**：

```
只允许一个 Bash 调用：
node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" task "<user input>"

禁止行为：
- 不读取文件 / grep / 搜索
- 不分析问题本身
- 不做后续跟进
- 返回 stdout 完全保持原样，不加工
```

这是最关键的设计选择：Claude Code 的 agent 退化为 pure forwarder，所有智能交给 Codex。

### 2. Companion Script 作为中央路由

`scripts/codex-companion.mjs` 是所有 slash 命令的统一分发点：

| 命令 | Companion 子命令 |
|:---|:---|
| `/codex:review` | `codex-companion.mjs review` |
| `/codex:rescue` | `codex-companion.mjs task` |
| `/codex:status` | `codex-companion.mjs status` |
| `/codex:cancel` | `codex-companion.mjs cancel` |
| `/codex:result` | `codex-companion.mjs result` |

好处：
- **Job 状态统一管理**：所有任务写入 `state.json`，带 session_id 关联
- **前后台统一接口**：同一个 `task` 子命令支持 `--background` / `--wait`
- **参数规范化**：统一的 resume / fresh / model / effort 参数处理

### 3. App Server 通信协议（scripts/lib/app-server.mjs）

外部服务（Codex）通过 JSON-RPC 协议通信，支持两种传输模式：

**Broker 模式**（推荐）：
```
Codex Companion Process (Unix socket)
    ↕  TCP / Unix Socket
Codex App Server Broker (长期运行的后台进程)
    ↕  JSONL over stdin/stdout
Codex App Server (codex CLI 内置)
```

**Direct Spawn 模式**：
```
Codex Companion Process (stdin/stdout)
    ↕  JSONL
Codex App Server (每次新 spawn 的子进程)
```

Broker 模式的优势：多个 Codex 操作共享同一个 App Server 进程，复用上下文。

### 4. Session 与 Job 关联

```
SessionStart hook → session_id 注入环境变量
    ↓
codex-companion 创建 job 时关联 session_id
    ↓
SessionEnd hook → 读取 state.json
    → 清理当前 session 的孤儿 job
    → 终止 orphaned Codex 进程
    → 清理 broker session
```

### 5. 参数路由（codex-cli-runtime skill）

`skills/codex-cli-runtime/SKILL.md` 规范了参数如何从子 agent 传递到 companion：

| 用户意图 | Companion 参数 |
|:---|:---|
| 继续之前的工作 | `--resume` → `--resume-last` |
| 重新开始 | `--fresh` → 不加 `--resume-last` |
| 指定模型 | `--model gpt-5.3-codex-spark` |
| 指定推理 effort | `--effort high` |
| 写入文件 | 默认加 `--write` |
| 只读诊断 | 用户明确说明 |

### 6. 委托能力总结

| 能力 | 实现位置 |
|:---|:---|
| 薄转发（agent 不越界） | `agents/codex-rescue.md` |
| 统一命令路由 + Job 管理 | `scripts/codex-companion.mjs` |
| 进程生命周期管理 | `scripts/session-lifecycle-hook.mjs` |
| 外部服务 JSON-RPC 通信 | `scripts/lib/app-server.mjs` |
| Broker Session 复用 | `scripts/lib/broker-lifecycle.mjs` |
| 参数规范化传递 | `skills/codex-cli-runtime/SKILL.md` |
| 输出原样呈现（不加工） | `skills/codex-result-handling/SKILL.md` |

---

## 关键文件速查

| 用途 | 文件 |
|:---|:---|
| Companion 脚本（命令路由） | `https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/scripts/codex-companion.mjs` |
| Hook 定义 | `https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/hooks/hooks.json` |
| 命令示例（带 frontmatter） | `https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/commands/review.md` |
| 子 Agent 定义 | `https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/agents/codex-rescue.md` |
| 生命周期 Hook 处理器 | `https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/scripts/session-lifecycle-hook.mjs` |
| Stop Gate Hook 处理器 | `https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/scripts/stop-review-gate-hook.mjs` |
| CLI Runtime Skill | `https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/skills/codex-cli-runtime/SKILL.md` |
| 结果呈现规范 | `https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/skills/codex-result-handling/SKILL.md` |
| 插件清单 | `https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/.claude-plugin/plugin.json` |

---

## 构建自己插件时参考此仓库的场景

1. **需要后台任务管理** → 看 `codex-companion.mjs` + `state.mjs`
2. **需要 slash 命令控制 Claude LLM 行为** → 看命令 frontmatter（`disable-model-invocation`、`allowed-tools`）
3. **需要子 agent 转发任务** → 看 `agents/codex-rescue.md` + `skills/codex-cli-runtime/SKILL.md`
4. **需要会话生命周期管理** → 看 `session-lifecycle-hook.mjs`
5. **需要停止时审查门** → 看 `stop-review-gate-hook.mjs` + `hooks/hooks.json`
6. **需要与外部服务通信** → 看 `scripts/lib/app-server.mjs`
