---
name: kb
description: 自动化个人知识库 — 一键 ETL 管道或分步执行
---

# /kb 命令

## 用法

| 子命令 | 行为 |
|--------|------|
| `/kb` | 一键全量管道：scan → extract-all → transform-all → load → serve |
| `/kb scan` | 只做结构梳理 |
| `/kb extract [dimension]` | 提取指定维度（topology/api/data-model/flows/concepts）；不指定则全量 |
| `/kb transform` | 全量转化 raw → wiki |
| `/kb load` | 校验 + 索引构建 |
| `/kb serve` | 构建站点 + 启动预览 |

## 执行

调用 `kb-agent`，由 agent 解析参数并分发到对应技能。
