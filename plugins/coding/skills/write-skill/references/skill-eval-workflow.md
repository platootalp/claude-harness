# Skill 评估工作流

本文件是 skill 评估的完整流程，需要与用户交互。核心流程（write-skill SKILL.md）不调用此文件。

本流程沿用 skill-creator 的评估循环，核心是：草稿 → 测试 → 人工审核 → 改进 → 重复。

## 何时使用

- skill 已创建并需要验证触发准确性和行为质量
- 修改已有 skill 后需要回归验证

## 评估步骤

### Step 1: 创建测试用例

设计 2-3 个真实的用户消息场景，类型：

- **应该触发**：用户请求明确属于 skill 职责范围
- **不应触发**：用户请求相关但属于其他 skill
- **边缘情况**：请求模糊，需要 skill 的 description 来决定

测试用例应像真实用户会说的，不是抽象请求。包含具体细节：文件路径、上下文、技术术语。

### Step 2: 运行对比测试

对每个测试场景，运行两个版本：
1. **with-skill**：Claude 有该 skill 可用
2. **without-skill**：Claude 没有该 skill（baseline）

使用 subagent 并行运行。

### Step 3: 评估触发准确性

检查 with-skill 版本：
- Claude 是否在正确时机触发了 skill
- Claude 是否在错误时机触发了 skill
- 触发后是否按 skill 指令执行

### Step 4: 量化评估（可选）

对有客观标准的 skill：
- 创建 assertions（具体可验证的预期输出）
- 对比 with-skill 和 without-skill 的输出
- 计算通过率

对主观输出的 skill（写作风格、设计质量）：
- 跳过量化评估
- 专注于人工审核

### Step 5: 人工审核

向用户展示：
- with-skill 和 without-skill 的输出对比
- 量化指标（如有）
- 收集用户反馈

### Step 6: 迭代改进

根据反馈改进 skill：
1. **泛化**：不要 overfit 到测试用例，改进应该适用于广泛场景
2. **保持精简**：移除不 pull weight 的内容
3. **解释 why**：理解任务本质，将理解传递到指令中
4. **识别重复工作**：如果测试中所有 subagent 都独立写了类似的辅助脚本，应该内置到 skill 的 scripts/

### Step 7: Description 优化

skill 稳定后，优化 description 以提高触发准确性：

1. 生成 20 个触发评估查询（8-10 应触发，8-10 不应触发）
2. 用 `skill-creator` 的 `scripts/improve_description.py` 或 `scripts/run_loop.py` 优化
3. 应用最佳 description

## 评估指标

| 指标 | 目标 |
|------|------|
| 触发召回率 | 该触发时触发了 |
| 触发精确率 | 不该触发时没触发 |
| 行为合规率 | 执行结果符合 skill 指令 |
| 输出质量 | 输出格式和内容达标 |
| Token 效率 | skill 不浪费上下文 |

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| Skill 不被触发 | description 太模糊或缺少触发词 | 扩展 description，添加更多触发场景 |
| Skill 误触发 | description 太宽泛 | 缩小范围，添加排除条件 |
| Claude 跳过 skill body | description 包含工作流摘要 | 删除工作流摘要，只保留触发条件 |
| 输出不一致 | 指令太模糊 | 添加更具体的步骤和示例 |
| Token 浪费 | SKILL.md 太长 | 拆分到 references/，保持 body < 500 行 |
