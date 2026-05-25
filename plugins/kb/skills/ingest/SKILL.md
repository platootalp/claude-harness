---
name: ingest
description: 当需要将 raw 提取文档转化为结构化 wiki 页面时使用。逐维度读取 raw 产出，按模板生成 entity/concept/synthesis 页面。
---

# Ingest — Raw → Wiki 转化

逐维度读取 raw 提取产出，按模板生成结构化 wiki 页面。

## 前置条件

对应维度的 raw `_index.md` 存在且 `status: unprocessed`

## Input

| 参数 | 必填 | 说明 |
|------|------|------|
| --project | 是 | 项目名称 |
| --dimension | 否 | 指定维度，默认全量 |
| --kb-data-root | 否 | 插件 data 目录绝对路径 | 数据根目录，所有读写基于此路径 |

## Output

| 产出 | 说明 |
|------|------|
| entity pages | 按实体模板生成的结构化页面 |
| concept pages | 按概念模板生成的结构化页面 |
| synthesis pages | 按综合模板生成的跨模块分析页面 |

## 反模式

| 反模式 | 正确做法 |
|--------|----------|
| ingest 产出太细碎，我来合并多个维度 | 综合分析由 cross-ref 负责，ingest 保持每维度独立 |
| ingest 产出的 wiki 页面内容不够 | ingest 是归一化，不是补充。内容来自 raw 提取 |
| 跳过 ingest，直接用 raw 文档 | raw 文档格式不统一，缺少交叉引用和综合分析 |
| synthesis 页面应该人工编写 | synthesis 由 ingest 根据模板自动生成，人工可以后续修订 |

## 执行流程

1. **扫描 raw 目录** — 列出 `{KB_DATA_ROOT}/raw/<project>/` 下所有维度目录
2. **过滤 dimension** — 如指定 `--dimension`，仅处理该维度；否则处理全部
3. **对每个维度执行：**
   - a. 读取 `_index.md` 和所有模块文档
   - b. **实体识别与重组**：每个模块即为一个实体。从 raw 文档中提取信息，按 entity 模板结构重组（不是复制，是提取关键字段、补充约束和代码映射、生成 Mermaid 结构图）
   - c. **概念识别与重组**：从 raw 文档中提取领域术语和核心概念，按 concept 模板结构重组（补充原理、实现示例、演进历史）
   - d. **跨模块综合**：识别跨模块/跨维度主题，按 synthesis 模板生成综合分析页面（必须包含全景图、深度分析、交叉引用、洞察）
   - e. 写入 `{KB_DATA_ROOT}/wiki/<project>/`
   - f. 更新 `_index.md` 状态为 `processed`
   - g. **质量自检**：每个 entity 页面行数 ≥ 80、每个 synthesis 页面行数 ≥ 60、每个页面至少 1 张 Mermaid 图

## 关键原则

- **模板驱动** — 所有产出严格按模板结构生成，确保一致性
- **保持维度边界** — 每个维度独立处理，不跨维度合并
- **状态追踪** — 通过 `_index.md` 的 status 字段追踪处理进度

## 质量约束

- 每个模块必须生成 1 个 entity 页面（从 raw 文档重组，非复制）
- 每个维度至少 1 个 synthesis 页面（跨模块综合分析）
- 每个页面至少 1 张 Mermaid 图
- entity 页面行数 ≥ 80，synthesis 页面行数 ≥ 60
- 重组而非复制：ingest 是信息提取和结构重组，不是格式转换。raw 文档的内容需要按模板结构重新组织，补充约束、代码映射、Mermaid 图等缺失信息
