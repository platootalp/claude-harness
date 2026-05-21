# Agent 评估工作流

本文件是 agent 评估的完整流程，需要与用户交互。核心流程（write-agent SKILL.md）不调用此文件。

## 何时使用

- agent 已创建并需要验证其调度准确性和行为质量
- 修改已有 agent 后需要回归验证

## 评估步骤

### Step 1: 创建测试场景

设计 2-3 个用户消息场景，验证：
- Claude 能否正确识别并调度该 agent
- Agent 被调度后能否正确执行任务

**场景类型：**
- 直接匹配：用户明确请求 agent 职责范围内的事
- 边缘情况：用户请求相关但模糊
- 负面案例：用户请求不属于该 agent 的任务

场景应像真实用户会说的，包含具体细节：文件路径、上下文、技术术语。

### Step 2: 运行对比测试

对每个场景，运行两个版本：
1. **with-agent**：Claude 有该 agent 可用
2. **without-agent**：Claude 没有该 agent（baseline）

使用 subagent 并行运行以节省时间。

### Step 3: 评估调度准确性

检查 with-agent 版本中：
- Claude 是否在正确的时机调度了 agent
- Claude 是否在错误的时机调度了 agent（误触发）
- Agent 的行为是否符合预期

### Step 4: 量化评估（可选）

对有客观标准的 agent（如输出格式、文件结构），创建 assertions：
- 输出包含特定部分
- 输出格式符合预期
- 行为符合 frontmatter 约束（tools、model 等）

对主观输出的 agent（如写作风格、设计建议），跳过量化评估，专注于人工审核。

### Step 5: 人工审核

向用户展示：
- with-agent 和 without-agent 的输出对比
- 量化指标（如有）
- 收集用户反馈

### Step 6: 优化 description

如果调度不准确，优化 description：
- 误触发：缩小 description 范围，添加排除条件
- 漏触发：扩展 description，添加更多触发词

### Step 7: 迭代改进

根据反馈改进 agent：
1. **泛化**：不要 overfit 到测试场景，改进应适用于广泛场景
2. **保持精简**：agent prompt 应简洁，移除不 pull weight 的内容
3. **解释 why**：理解任务本质，将理解传递到指令中

重复 Step 1-6 直到调度准确且行为正确。

## 评估指标

| 指标 | 目标 |
|------|------|
| 调度召回率 | 该调的时候调了 |
| 调度精确率 | 不该调的时候没调 |
| 行为合规率 | 执行结果符合预期 |
| 输出质量 | 输出格式和内容达标 |
| Token 效率 | agent 不浪费上下文 |

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| Agent 不被调度 | description 太模糊或缺少触发词 | 扩展 description，添加更多触发场景 |
| Agent 误触发 | description 太宽泛 | 缩小范围，添加排除条件 |
| Agent 行为不一致 | prompt 指令太模糊 | 添加更具体的行为指令和输出格式 |
| Agent 忽略工具限制 | tools 字段未正确设置 | 确认 tools/disallowedTools 配置正确 |
| Agent 输出过长 | prompt 缺少输出格式约束 | 添加 Output format 部分 |
