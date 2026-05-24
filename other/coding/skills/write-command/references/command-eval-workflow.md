# Command 评估工作流

本文件是 command 评估的完整流程，需要与用户交互。核心流程（write-command SKILL.md）不调用此文件。

## 何时使用

- command 已创建并需要验证其行为正确性
- 修改已有 command 后需要回归验证

## 评估步骤

### Step 1: 创建测试场景

设计 2-3 个用户消息场景，类型：
- **正常调用**：使用正确的参数调用命令
- **无参数调用**：不传参数时的行为
- **错误参数**：传入错误参数时的处理

场景应像真实用户会说的，包含具体细节。

### Step 2: 运行对比测试

对每个场景，运行两个版本：
1. **with-command**：Claude 有该 command 可用
2. **without-command**：Claude 没有该 command（baseline）

使用 subagent 并行运行以节省时间。

### Step 3: 评估输出

检查 with-command 版本：
- 命令是否出现在自动补全中
- 参数是否正确传递（`$ARGUMENTS`、`$N`、`$name`）
- 指令是否按预期执行
- 输出格式是否符合预期

### Step 4: 量化评估（可选）

对有客观标准的 command（如文件生成、数据提取），创建 assertions：
- 输出包含特定部分
- 参数正确引用
- 动态内容注入正确

对主观输出的 command，跳过量化评估，专注于人工审核。

### Step 5: 人工审核

向用户展示：
- with-command 和 without-command 的输出对比
- 量化指标（如有）
- 收集用户反馈

### Step 6: 优化 description

如果命令不出现在自动补全中或描述不够清晰：
- 确认 description 字段存在且非空
- 优化 description 使其更易搜索
- 确认 argument-hint 与 arguments 定义一致

### Step 7: 迭代改进

根据反馈改进 command：
1. **泛化**：不要 overfit 到测试场景
2. **保持精简**：command 应简洁，超过 50 行考虑改为 skill
3. **单一职责**：一个 command 只做一件事

重复 Step 1-6 直到行为正确。

## 评估指标

| 指标 | 目标 |
|------|------|
| 自动补全可见性 | 命令出现在补全列表中 |
| 参数传递正确性 | 参数正确引用和传递 |
| 指令执行正确性 | 输出符合预期 |
| 错误处理 | 错误参数有合理反馈 |
| Token 效率 | command 不浪费上下文 |

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 命令不出现在补全中 | description 为空或太模糊 | 添加清晰的 description |
| 参数未正确传递 | 引用语法错误 | 确认 $ARGUMENTS / $N / $name 用法 |
| 指令执行不正确 | body 指令太模糊 | 添加更具体的步骤化指令 |
| 动态内容注入失败 | !`command` 语法错误 | 确认命令可执行且输出正确 |
| Command 做了太多事 | 职责不单一 | 拆分为多个 command 或改为 skill |
