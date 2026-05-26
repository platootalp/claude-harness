# 审查输入归一化

每次 review 都先把输入整理成统一上下文，再进入四个审查维度。不要一边看 diff 一边临时猜需求。

## 支持的输入类型

### 1. code plan / 执行计划

适用场景：
- 用户直接提供 plan 文档
- 用户贴出 implementation checklist
- 用户说明“按这个计划执行过，请 review”

归一化时至少提炼：
- 功能目标
- 涉及模块和文件落点
- 关键步骤或验收点
- 明确不在本次范围内的内容

### 2. 纯需求文本 / 工单描述

适用场景：
- 用户给了一段需求说明
- 用户给的是 PR 描述、变更摘要、业务背景

归一化时至少提炼：
- 用户流程
- 业务规则
- 关键字段、状态、权限、边界条件
- 成功路径和失败路径

### 3. Flash 地址

适用场景：
- 用户给的是 Flash story 地址
- 需求正文不在当前对话里，需要从 Flash 拉取

处理要求：
- 先从地址中定位 story 标识
- 调用 `mcp-flash` 的 `get_story_task_description`
- 只把返回结果中与本次改动相关的需求、任务描述、验收信息提炼出来

禁止做法：
- 只根据 Flash URL 文本猜需求
- 不调用 story 详情就直接下结论
- 把 Flash 的无关讨论原样复制进审查结论

## 统一上下文字段

归一化后，建议至少形成以下结构：

```json
{
  "inputType": "code-plan | requirement-text | flash-url",
  "sourceLabel": "需求文档标题 / Flash story 标题 / plan 标题",
  "sourceUrl": "可选，原始链接",
  "requirementSummary": "本次 review 的需求摘要",
  "taskDescription": "实施任务描述或计划摘要",
  "acceptanceHints": [
    "验收点 1",
    "验收点 2"
  ],
  "outOfScope": [
    "明确不在本次范围内的内容"
  ]
}
```

## 使用要求

- 没有需求上下文时，可以先 review 代码质量和 rules，但业务实现类结论必须降低信心，必要时放入“待确认问题”
- 如果同时拿到了 code plan 和需求文本，优先以需求为“做什么”的依据，以 plan 为“怎么拆”的依据
- 如果 Flash 返回内容和实际 diff 范围明显不一致，要把这种偏差作为待确认问题写出
