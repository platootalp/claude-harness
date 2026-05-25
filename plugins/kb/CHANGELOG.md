# Changelog

## [0.4.0] - 2026-05-25

### Added
- 知识图谱页面：KnowledgeGraph.tsx（d3-force 力导向布局）、GraphControls.tsx、NodeCard.tsx
- 构建脚本：build-search-index.mjs（raw + wiki 搜索索引）、build-graph-data.mjs（图谱数据 + projects.json）
- serve skill：构建与预览管道（setup → install → build:index → build:graph → build → preview）
- build-search-index skill 和 build-graph skill（内部技能）
- Sidebar 动态导航：按项目/维度/类型分组，当前页面高亮
- Wiki 视图：总览页（按 page_type 分组）、详情页（Content + CrossReferences + SourceTraceability）
- Raw 视图：总览页（按 dimension 分组）、详情页（Content + RawDocMeta）
- 项目首页：ViewCard + DimensionBar 组件
- HomeLayout + 全局首页：ProjectCard + ProjectSwitcher 组件
- 复用 analysis 站点组件：DocLayout、TopNav（+ProjectSwitcher 插槽）、Pagination、TableOfContents、ReadingProgress、ThemeToggle、SearchModal 等
- 站点骨架：package.json（+d3 依赖）、astro.config.mjs、site.config.ts、content.config.ts（raw + wiki 双集合）

## [0.3.0] - 2026-05-25

### Added
- cross-ref skill：跨文档关联与综合，发现跨维度/跨模块关联，建立双向链接
- transform 路由 skill：解析用户意图，分发到 ingest / cross-ref 技能
- wiki 数据目录：index.md、overview.md、log.md、projects/.gitkeep

## [0.2.0] - 2026-05-25

### Added
- scan skill：代码库结构梳理，产出 `_map.md`
- extract-topology skill + topology 模板
- extract-api skill + api 模板
- extract-data-model skill + data-model 模板
- extract-flows skill + flows 模板
- extract-concepts skill + concepts 模板
- extract 路由 skill
- /kb 命令 + kb-agent + extract-agent + transform-agent

## [0.1.0] - 2026-05-25

### Added
- 初始插件骨架