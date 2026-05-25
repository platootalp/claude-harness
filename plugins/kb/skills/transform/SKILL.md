---
name: transform
description: 当需要将 raw 提取产出转化为结构化 wiki 页面、建立交叉引用时使用。路由到 ingest 和 cross-ref 技能。extract 的自然后续步骤。
---

# Transform — 转化路由

解析用户意图，分发到具体的转化技能。

## 前置条件

- 至少 1 个维度的 raw 提取已完成

## 用法

| 命令 | 行为 |
|------|------|
| `transform --project <name>` | 全量转化 + 交叉引用 |
| `transform --project <name> --dimension topology` | 只转化指定维度 |
| `transform --project <name> --skip-cross-ref` | 跳过交叉引用 |
| `transform --kb-data-root <path>` | 指定数据根目录 |

## 反模式

| 反模式 | 说明 |
|--------|------|
| 在路由技能中实现转化逻辑 | 路由只负责分发，具体逻辑由 ingest / cross-ref 技能实现 |
| 跳过前置条件检查直接转化 | 未确认 raw 提取产出存在就开始转化，会导致空输出或错误 |

## 执行流程

1. 扫描 `{KB_DATA_ROOT}/raw/<project>/` 目录，找到 unprocessed 的维度
2. 调用 ingest 技能转化
3. 如果未跳过 cross-ref，调用 cross-ref 技能（注意：在 /kb 命令管道中，cross-ref 由 /kb 命令内联执行，不由 transform 路由负责）
4. 汇总结果

## 关键原则

- **路由非实现** — 本技能只负责意图解析与分发，不包含具体转化逻辑
- **前置检查** — 执行前必须确认 raw 提取产出存在且完整
- **增量友好** — 只处理未转化的维度，已转化的跳过
