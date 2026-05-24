# Command Frontmatter 字段参考

## 推荐字段

### description
- 类型：string
- 约束：推荐 < 500 字符
- 写法：清晰描述命令用途和使用场景
- 用途：出现在自动补全中，帮助用户选择命令
- 示例：`Deploy the application to production environment`

## 可选字段

### argument-hint
- 类型：string
- 用途：在自动补全中显示参数提示
- 示例：`<environment>`, `<file-path>`, `<query>`

### arguments
- 类型：object
- 用途：定义具名位置参数
- 示例：`{ "env": { "description": "Target environment" } }`

### disable-model-invocation
- 类型：boolean
- 用途：设为 true 阻止 Claude 自动加载此命令
- 场景：仅供用户手动 `/name` 调用

### allowed-tools
- 类型：空格分隔的工具名列表
- 用途：预授权工具，无需权限确认
- 示例：`Read Grep Bash(git *)`

### model
- 类型：string
- 合法值：`sonnet`, `opus`, `haiku`, 或完整模型 ID
- 用途：指定执行命令时使用的模型

### effort
- 类型：string
- 合法值：`low`, `medium`, `high`, `xhigh`, `max`
- 用途：命令执行的努力程度

## 文件位置

| 位置 | 路径 | 作用域 |
|------|------|--------|
| 个人级 | `~/.claude/commands/<name>.md` | 所有项目 |
| 项目级 | `.claude/commands/<name>.md` | 当前项目 |
| 插件级 | `<plugin>/commands/<name>.md` | 插件启用处 |

## 参数引用

| 变量 | 描述 |
|------|------|
| `$ARGUMENTS` | 传入的所有参数 |
| `$ARGUMENTS[N]` 或 `$N` | 按索引访问参数（0-based） |
| `$name` | 具名参数（来自 arguments 定义） |
| `${CLAUDE_SESSION_ID}` | 当前会话 ID |
| `${CLAUDE_EFFORT}` | 当前努力程度 |

## 动态内容注入

用 `!`command`` 语法在命令加载时注入动态内容：

```markdown
当前分支：!`git branch --show-current`
未提交更改：!`git status --short`
```

## Body 写作原则

- 直接写指令，不需要角色定义
- 简洁直接，一个 command 做一件事
- 保持 < 50 行，超过则应考虑 skill
- 可引用参数
- 可注入动态内容
