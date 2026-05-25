---
name: extract
description: 当需要对代码库进行多维度深度分析时使用。路由到具体维度的提取技能，或一键全量提取。scan 的自然后续步骤。
---

# Extract — 提取路由

解析用户意图，分发到具体的维度提取技能。

<HARD-GATE>
`_map.md` 不存在时，必须先调用 scan 技能。extract 不负责 scan——它只路由到维度提取技能。
</HARD-GATE>

## 用法

| 命令 | 行为 |
|------|------|
| `extract --target <path> --project <name>` | 全量提取（5 个维度） |
| `extract --target <path> --project <name> --dimension topology` | 只提取拓扑 |
| `extract --target <path> --project <name> --dimension api` | 只提取接口 |
| `extract --target <path> --project <name> --dimension data-model` | 只提取数据模型 |
| `extract --target <path> --project <name> --dimension flows` | 只提取业务流程 |
| `extract --target <path> --project <name> --dimension concepts` | 只提取领域概念 |
| `extract --kb-data-root <path>` | 指定数据根目录 |

## 反模式

| 反模式 | 正确做法 |
|--------|----------|
| "我直接调用 extract-topology，不需要 extract 路由" | 可以，但 extract 路由帮你处理 scan 前置检查和多维度并发编排 |
| "全量提取太慢了，先做两个维度" | 合理。用 `--dimension` 参数选择需要的维度，后续可以增量补充 |

## 执行流程

1. 如果 `{KB_DATA_ROOT}/raw/<project>/_map.md` 不存在，先调用 `scan` 技能
2. 根据 `--dimension` 参数决定调用哪些技能：
   - `topology` → `extract-topology`
   - `api` → `extract-api`
   - `data-model` → `extract-data-model`
   - `flows` → `extract-flows`
   - `concepts` → `extract-concepts`
   - 不指定 → 全部 5 个
3. 逐个调用对应技能（传入 `--kb-data-root` 参数），或并发调用（如果 extract-agent 可用，或由 /kb 命令并行派发）
4. 汇总结果，报告每个维度的产出文件数量

## 关键原则

- **路由，非实现：** extract 不做提取工作，只做分发和编排
- **前置检查：** scan 是所有维度提取的前提，extract 必须确保它已完成
- **增量友好：** 支持按维度提取，允许分步完成全量分析
