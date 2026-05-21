# Skill Frontmatter 字段参考

## 必填字段

### name
- 类型：string
- 约束：kebab-case，仅小写字母、数字和连字符，max 64 字符
- 用途：skill 标识，用于 `/name` 调用和自动触发
- 推荐写法：动名词（-ing）或动作词
- 示例：`writing-skills`, `systematic-debugging`, `deploy`

### description
- 类型：string
- 约束：max 1024 字符，推荐 < 500 字符
- 写法：以 "Use when..." 开头，第三人称，只描述触发条件，**不含工作流摘要**
- 用途：Claude 据此决定是否触发该 skill
- 示例：`Use when creating or modifying Claude Code skill files`

**CSO（Claude Search Optimization）关键规则：**
- description 只写触发条件，不写流程
- 包含具体触发词、症状、场景
- 技术特定的 skill 要明确标注
- 写得稍微 "pushy" 一点以对抗 undertrigger 倾向

## 可选字段

### when_to_use
- 类型：string
- 用途：额外触发上下文

### disable-model-invocation
- 类型：boolean
- 默认：false
- 用途：设为 true 阻止 Claude 自动触发，仅供用户 `/name` 调用

### user-invocable
- 类型：boolean
- 默认：true
- 用途：设为 false 隐藏 `/` 菜单，仅供 Claude 自动触发

### argument-hint
- 类型：string
- 用途：自动补全中的参数提示

### arguments
- 类型：object
- 用途：定义具名位置参数

### allowed-tools
- 类型：空格分隔的工具名列表
- 用途：预授权工具，无需权限确认
- 示例：`Read Grep Bash(git *)`

### model
- 类型：string
- 合法值：`sonnet`, `opus`, `haiku`, 或完整模型 ID
- 用途：指定执行 skill 时使用的模型

### effort
- 类型：string
- 合法值：`low`, `medium`, `high`, `xhigh`, `max`
- 用途：skill 执行的努力程度

### context
- 类型：string
- 合法值：`fork`
- 用途：设为 fork 则在子代理中运行

### agent
- 类型：string
- 用途：指定使用的子代理类型

### hooks
- 类型：object
- 用途：skill 生命周期钩子

### paths
- 类型：glob 模式列表
- 用途：限制 skill 激活的文件路径

### shell
- 类型：string
- 合法值：`bash`, `powershell`
- 用途：内联命令使用的 shell

## 字符串替换变量

| 变量 | 描述 |
|------|------|
| `$ARGUMENTS` | 传入的所有参数 |
| `$ARGUMENTS[N]` / `$N` | 按索引访问参数（0-based） |
| `$name` | 具名参数（来自 arguments） |
| `${CLAUDE_SESSION_ID}` | 当前会话 ID |
| `${CLAUDE_EFFORT}` | 当前努力程度 |
| `${CLAUDE_SKILL_DIR}` | SKILL.md 所在目录 |

## 动态内容注入

```markdown
当前分支：!`git branch --show-current`
未提交更改：!`git status --short`
```

运行命令并将输出替换到内容中，在 Claude 看到内容之前完成。

## 文件位置

| 位置 | 路径 | 作用域 |
|------|------|--------|
| 企业级 | Managed settings | 组织内所有用户 |
| 个人级 | `~/.claude/skills/<name>/SKILL.md` | 所有项目 |
| 项目级 | `.claude/skills/<name>/SKILL.md` | 当前项目 |
| 插件级 | `<plugin>/skills/<name>/SKILL.md` | 插件启用处 |
