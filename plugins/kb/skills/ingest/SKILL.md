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

1. **扫描 raw 目录** — 列出 `data/raw/<project>/` 下所有维度目录
2. **过滤 dimension** — 如指定 `--dimension`，仅处理该维度；否则处理全部
3. **对每个维度执行：**
   - a. 读取 `_index.md` 和所有模块文档
   - b. 识别实体 → 用 entity 模板生成页面
   - c. 识别概念 → 用 concept 模板生成页面
   - d. 跨模块综合 → 用 synthesis 模板生成页面
   - e. 写入 `data/wiki/<project>/`
   - f. 更新 `_index.md` 状态为 `processed`

## 关键原则

- **模板驱动** — 所有产出严格按模板结构生成，确保一致性
- **保持维度边界** — 每个维度独立处理，不跨维度合并
- **状态追踪** — 通过 `_index.md` 的 status 字段追踪处理进度
