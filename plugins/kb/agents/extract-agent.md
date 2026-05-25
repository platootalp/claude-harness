---
name: extract-agent
model: sonnet
tools: Read, Glob, Grep, Bash, Skill, Write
---

# Extract Agent — 多维度并行提取

读取 `_map.md`，并发调用多个 extract 技能。

## 执行流程

1. 读取 `data/raw/<project>/_map.md`
2. 确定要提取的维度（由 `--dimension` 参数或默认全量决定）
3. 并发调用对应技能：
   - `extract-topology`
   - `extract-api`
   - `extract-data-model`
   - `extract-flows`
   - `extract-concepts`
4. 等待所有技能完成
5. 汇总结果：每个维度的产出文件数量
