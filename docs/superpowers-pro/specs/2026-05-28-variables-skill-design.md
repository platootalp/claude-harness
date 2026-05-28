# variables Skill 设计

## 概述

新增 `variables` skill，帮助用户查看和修改 superpowers-pro 插件的 `variables.json` 配置。

**触发方式:**
- `/superpowers-pro:variables` — 查看所有变量及当前值
- `/superpowers-pro:variables <name> <value>` — 修改变量值

**能力边界:**
- 仅查看和修改，不支持新增/删除变量
- 仅操作 superpowers-pro 自身的 `variables.json`
- 修改时严格校验值必须在 `values` 列表中
- 修改后本次会话立即生效

## 核心行为

### 查看模式（无参数）

1. 读取 `variables.json`，格式化输出每个变量：
   ```
   finish-mode: auto (可选: auto, interactive) — auto = 确定性合并推送清理; interactive = 菜单选择模式
   review-mode: section-by-section (可选: section-by-section, full) — section-by-section = 分节审批; full = 一次展示
   ```
2. 无副作用，纯展示。

### 修改模式（带参数 `<name> <value>`）

1. 校验 `<name>` 是否存在于 `variables.json` 的 key 中，不存在则报错并列出可用变量名
2. 校验 `<value>` 是否在该变量的 `values` 列表中，不在则报错并列出可选值
3. 通过脚本修改 `variables.json` 中对应变量的 `default` 字段
4. 在当前会话中立即应用新值

### 会话生效机制

变量通过 session-start hook 注入会话上下文，修改 JSON 文件不会自动更新当前会话。解决方案：SKILL.md 中明确指令 agent 在修改变量后，以明确的文本声明覆盖当前会话的变量值：

> 变量 `finish-mode` 已修改为 `interactive`。本次会话中 `finish-mode` 的值现在是 `interactive`。

此文本进入对话上下文后，agent 后续行为会遵循新值。

## 脚本设计

**文件:** `skills/variables/scripts/variables.sh`

**接口:**

```bash
# 查看所有变量
./variables.sh show <variables-json-path>

# 修改变量
./variables.sh set <variables-json-path> <name> <value>
```

### `show` 命令

- 读取 JSON，按 `key: default (可选: values) — description` 格式逐行输出
- 与 session-start hook 中的 python3 格式化逻辑保持一致

### `set` 命令

1. 读取 JSON
2. 校验 key 存在，不存在则输出 `ERROR: unknown variable "<name>". Available: finish-mode, review-mode` 并 exit 1
3. 校验 value 在 values 列表中，不在则输出 `ERROR: invalid value "<value>" for <name>. Valid values: auto, interactive` 并 exit 1
4. 修改对应 key 的 `default` 字段为 `<value>`
5. 写回 JSON（保持 2-space 缩进）
6. 输出 `OK: <name> = <value>`

**实现语言:** bash + python3（与 session-start hook 一致）

**错误处理:** 所有错误输出到 stderr，exit code 非零。SKILL.md 指导 agent 检查 exit code 并向用户报告错误。

## SKILL.md 结构

**Frontmatter:**

```yaml
---
name: variables
description: 查看和修改 superpowers-pro 插件变量。无参数查看所有变量，带 name 和 value 参数修改变量。
---
```

**Body 结构:**

1. **触发说明** — 两种调用方式（查看/修改）
2. **读取变量文件** — 定位 `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/variables.json`
3. **查看流程** — 调用 `scripts/variables.sh show`，展示输出
4. **修改流程** — 调用 `scripts/variables.sh set`，检查 exit code
   - 成功：展示确认信息，在对话中声明新值生效
   - 失败：展示错误信息（未知变量 / 非法值）
5. **会话覆盖规则** — 修改后当前会话以新值为准，忽略 session-start 注入的旧值
