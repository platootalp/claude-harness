# Changelog

## [Unreleased]

### Added
- cross-ref skill：跨文档关联与综合，发现跨维度/跨模块关联，建立双向链接，生成综合分析页面
- transform 路由 skill：解析用户意图，分发到 ingest / cross-ref 技能
- wiki 数据目录：index.md、overview.md、log.md、projects/.gitkeep

### Added
- scan skill：代码库结构梳理，产出 `_map.md` 作为 Extract 管道起点
- extract-data-model skill：读取结构地图，逐模块提取数据模型文档（实体、字段、关系、枚举、生命周期）
- extract-data-model 模板：data-model.md，定义数据模型文档的必含章节和质量要求

## [0.1.0] - 2026-05-25

### Added
- 初始插件骨架
- kb-extract 流程：从代码仓库提取知识图谱、实体术语、流程图、架构分析
- kb-transform 流程：归一化、去重、交叉引用、质量评分
- kb-load 流程：校验、索引构建
- kb-present 流程：查询、解释、影响分析
