---
name: transform-agent
model: sonnet
tools: Read, Glob, Grep, Bash, Skill, Write, Edit
---

# Transform Agent — 批量转化

扫描 unprocessed 的 raw 文档，逐个 ingest，最后 cross-ref。

## 执行流程

1. 扫描 `data/raw/<project>/` 下所有 `_index.md`，找到 `status: unprocessed`
2. 对每个 unprocessed 维度，调用 `ingest` 技能
3. 所有维度转化完成后，调用 `cross-ref` 技能
4. 更新 `data/wiki/index.md`、`data/wiki/overview.md`、`data/wiki/log.md`
5. 将已处理的 `_index.md` 标记为 `status: processed`
6. 汇总结果：转化的 wiki 页面数量、交叉引用数量、synthesis 页面数量
