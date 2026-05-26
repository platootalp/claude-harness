# 审查输出模板

请先整理结构化 findings JSON，再使用以下固定结构输出 markdown：

```markdown
## 审查发现

### 1. 业务功能的实现
- 功能点核对：
  - [通过/不通过] 功能点名称：明确说明是否已实现，以及审查依据。
- [严重程度][file:line] 问题描述、影响范围，以及为什么它与需求或实施计划不一致。

### 2. 代码的质量
- [严重程度][file:line] 问题描述、影响范围，以及它违反了哪条代码质量审查规则。

### 3. 架构的合理性
- [严重程度][file:line] 问题描述、影响范围，以及它为什么不符合实施计划或合理分层。

### 4. 项目 rules 的遵循情况
- [严重程度][file:line] 问题描述、影响范围，以及它违反了哪条项目 rules。

## 待确认问题

- 缺失的需求背景、不清晰的改动意图，或影响审查信心的验证缺口。

## 审查结论

- Ready: Yes / No / With fixes
- Reasoning: 1-2 句话说明判断依据
```

## 使用说明

- markdown 和 HTML 必须来自同一份结构化 findings 数据
- 首次组织 findings 时，可参考 `templates/findings-example.json`
- findings 顶层 `meta.reviewedFiles` 应列出本次实际审查的文件清单，并排除 ignore 掉的文件
- `meta.businessChecks` 应列出业务功能点、是否实现，以及明确审查结果
- 输出前先确认 findings 至少包含：`dimension`、`severity`、`mustFix`、`filePath`、`line`、`problem`、`risk`、`evidence`
- 如果要生成 HTML 报告，把同一份 findings JSON 交给 `scripts/render-review-report.mjs`
- `findings JSON` 和 HTML 默认应落到 `docs/superpowers/reports/<timestamp>/`，每次一个新目录
- 如果某个部分没有发现问题，写 `- 无`
- 如果整体没有发现问题，也要明确写出“无审查发现”
- 如果证据不足，不要强行下结论，放入“待确认问题”
- markdown 中每条 finding 的语义应与结构化 finding 对齐，不要扩写成另一套结论
