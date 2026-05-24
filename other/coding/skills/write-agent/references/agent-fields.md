# Agent Frontmatter 字段参考

## 必填字段

### name
- 类型：string
- 约束：kebab-case，仅小写字母和连字符，max 64 字符
- 用途：agent 唯一标识，Claude 据此调度
- 示例：`code-reviewer`, `test-runner`, `deploy-agent`

### description
- 类型：string
- 约束：max 1536 字符（name + description 合计），推荐 < 500 字符
- 写法：以 "Use when..." 开头，第三人称，只描述触发条件，不含工作流摘要
- 用途：Claude 据此决定是否委派任务给该 agent
- 示例：`Use when a major project step has been completed and needs code review`

## 可选字段

### tools
- 类型：逗号分隔的工具名列表
- 用途：限制 agent 可用的工具，不填则继承所有
- 合法值：Read, Write, Edit, Grep, Glob, Bash, Skill, Agent, WebFetch, WebSearch, NotebookEdit
- 示例：`Read, Grep, Glob, Bash`

### disallowedTools
- 类型：逗号分隔的工具名列表
- 用途：禁止 agent 使用的工具

### model
- 类型：string
- 合法值：`sonnet`, `opus`, `haiku`, `inherit`, 或完整模型 ID（如 `claude-sonnet-4-6`）
- 用途：指定 agent 使用的模型，不填则继承
- 推荐：简单任务用 haiku，标准任务用 sonnet，复杂推理用 opus

### permissionMode
- 类型：string
- 合法值：`default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`
- 用途：agent 的权限模式

### maxTurns
- 类型：integer
- 用途：agent 最大执行轮次，防止无限循环

### skills
- 类型：逗号分隔的 skill 名称列表
- 用途：agent 启动时预加载的 skills

### mcpServers
- 类型：object
- 用途：agent 可用的 MCP 服务器

### hooks
- 类型：object
- 用途：agent 生命周期钩子

### memory
- 类型：string
- 合法值：`user`, `project`, `local`
- 用途：agent 的持久化内存作用域

### background
- 类型：boolean
- 用途：设为 true 则始终作为后台任务运行

### effort
- 类型：string
- 合法值：`low`, `medium`, `high`, `xhigh`, `max`
- 用途：agent 的努力程度

### isolation
- 类型：string
- 合法值：`worktree`
- 用途：设为 worktree 则在隔离的 git worktree 中运行

### color
- 类型：string
- 合法值：`red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`
- 用途：agent 在 UI 中的显示颜色

### initialPrompt
- 类型：string
- 用途：自动提交为第一条用户消息

## 文件位置

| 位置 | 路径 | 作用域 |
|------|------|--------|
| 个人级 | `~/.claude/agents/<name>.md` | 所有项目 |
| 项目级 | `.claude/agents/<name>.md` | 当前项目 |
| 插件级 | `<plugin>/agents/<name>.md` | 插件启用处 |

## Body 结构

```markdown
You are a [角色定义].

## When invoked
[行为指令 — 解释 why 而非仅 what]

## Output format
[期望的输出格式]
```

**写作原则：**
- 角色定义开头
- 解释 why，给予合理自由度
- 避免过度 MUST/NEVER
- 保持简洁，< 200 行
