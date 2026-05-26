# Reviewer 提示词附加模板

把本文件拼接到标准 `superpower` reviewer 骨架后面使用。

## 推荐组合方式

1. 先使用当前环境的标准 reviewer 骨架，例如 `superpowers:requesting-code-review`
2. 正常填写审查范围、需求说明、`BASE_SHA`、`HEAD_SHA` 和改动摘要
3. 再把下面这段附加要求拼上去，让 reviewer 同时遵循本仓库的规则

## 项目附加要求

```md
在标准审查清单之外，直接以以下文件作为唯一事实来源：
- `.cursor/skills/code-review-skills/references/review-inputs.md`
- `.cursor/skills/code-review-skills/references/review-dimensions.md`
- `.cursor/skills/code-review-skills/references/review-checklist.md`
- `.cursor/skills/code-review-skills/references/review-findings-schema.md`
- `.cursor/skills/code-review-skills/references/review-score-rules.md`
- `.cursor/skills/code-review-skills/references/code-quality-rules.md`
- `.cursor/skills/code-review-skills/references/project-rules-index.md`
- `.cursor/skills/code-review-skills/templates/output-template.md`
- `.cursor/skills/code-review-skills/templates/findings-example.json`

要求：
- 先识别输入来源：code plan、需求文本或 Flash 地址
- 如果输入是 Flash 地址，先调用 `mcp-flash` 的 `get_story_task_description`
- 先将需求上下文归一化，再开始对比 diff
- 如果用户没有明确指定审查范围，先运行 `node .cursor/skills/code-review-skills/scripts/review-scope.mjs`
- 默认只审查该脚本产出的 includedFiles 与对应 diff
- `.cursor/skills/code-review-skills/scripts/review-ignore.json` 中匹配到的文件不参与 review
- 不要重复改写这些文件中的规则、维度或模板
- 输出顺序必须固定：
  1. 先形成完整的 findings JSON，可参考 `templates/findings-example.json`
  2. 再基于同一份 findings JSON 输出 markdown
  3. 最后再基于同一份 findings JSON 生成 HTML 报告
- 每条 finding 都必须先形成结构化对象，再输出 markdown
- 每条 finding 都必须包含 `file:line`、问题是什么、为什么重要，以及具体风险
- 每条 finding 至少要有：`dimension`、`severity`、`mustFix`、`filePath`、`line`、`codeSnippet`、`problem`、`risk`、`evidence`
- findings 的 `meta.reviewedFiles` 必须列出本次实际审查的文件清单，并排除 ignore 掉的文件
- findings 的 `meta.businessChecks` 必须列出业务功能点、是否已实现，以及明确审查结论
- 审查结束后，用同一份 findings JSON 调用 `node .cursor/skills/code-review-skills/scripts/render-review-report.mjs --input <json> --output <html>`
- `findings JSON` 和 HTML 报告默认输出到项目根目录下的 `docs/superpowers/reports/<timestamp>/`
- 每次审查必须新建一个独立目录，并至少包含 `review-findings.json` 和 `review-report.html`
- 除非用户明确要求审 automation 或 skill 文件，否则不要审 `.cursor/` 目录
- 如果某个部分没有发现问题，按输出模板写 `- 无`
- 如果没有发现问题，要明确写出“无审查发现”，并补充剩余测试缺口或信心边界
- 评分必须遵循 `review-score-rules.md`，不要自定义另一套算法
```

## 兜底方式

如果标准 superpower reviewer 不可用，就把本文件和 `SKILL.md` 一起作为完整的审查说明使用。
