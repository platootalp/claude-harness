---
name: extract-concepts
description: 当需要理解模块的核心概念、领域术语、概念关系、或命名规范时使用。读取结构地图，逐模块提取概念术语文档。
---

# Extract Concepts — 概念术语提取

读取结构地图，逐模块提取概念术语文档。

<HARD-GATE>
`data/raw/<project>/_map.md` 必须存在（由 scan 技能产出）。如果没有，先调用 scan 技能。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--target <path>` | 是 | - | 目标代码库路径 |
| `--project <name>` | 是 | - | 项目名称 |
| `--module <name>` | 否 | 全量 | 只分析指定模块 |

## 前置条件

- `data/raw/<project>/_map.md` 必须存在

## 输出

- `data/raw/<project>/concepts/_index.md`（带 frontmatter 的索引）
- `data/raw/<project>/concepts/modules/<module>.md`（每个模块一份概念术语文档）

## 反模式

| 想法 | 问题 |
|------|------|
| "术语表只列生僻词就行" | 领域常见词对新人同样是障碍，术语表需全量覆盖 |
| "概念关系凭经验画" | 概念关系必须有代码证据支撑，凭经验推断会产生错误关联 |
| "命名规范从 README 抄" | README 可能过时，必须从实际代码提取命名模式 |
| "概念层次按目录结构来" | 目录结构是组织视角，概念层次是抽象视角，两者经常不一致 |

## 执行流程

1. 读取 `_map.md`，获取模块清单
2. 如果指定了 `--module`，只分析该模块；否则分析所有模块
3. 对每个模块：
   a. 扫描核心代码文件（模型定义、常量声明、类型别名、配置结构）
   b. 提取术语定义（领域术语、缩写、行话）
   c. 识别核心概念（关键抽象、设计模式、领域实体）
   d. 构建概念关系（依赖、组合、继承、关联）
   e. 提取命名规范（变量命名模式、函数命名约定、缩写表）
   f. 识别概念演进（废弃术语、重命名历史、版本间概念变化）
   g. 生成 Mermaid 概念关系图和概念层次图
   h. 按 `templates/concepts.md` 模板生成概念术语文档，写入 `concepts/modules/<module>.md`
4. 生成 `concepts/_index.md`（概念清单 + 跨模块概念关系图 + frontmatter）

## `_index.md` frontmatter

```yaml
---
project: <project>
dimension: concepts
date: YYYY-MM-DD
status: unprocessed
tags: [...]
---
```

## 模板

遵循 `templates/concepts.md` 定义的必含章节和质量要求。

## 关键原则

- **概念必须有代码证据：** 每个核心概念必须关联到具体的代码路径，不接受无代码支撑的纯理论概念
- **术语表需全量覆盖：** 所有领域特定术语都必须收录，包括看似常见的词——对新成员而言没有"显而易见"的术语
- **概念层次是推断：** 概念的抽象层次基于代码中的使用模式推断，可能与设计者意图不一致，后续 Transform 可修正
