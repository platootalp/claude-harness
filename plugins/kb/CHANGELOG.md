# Changelog

## [0.6.0] - 2026-05-25

### Fixed

- **输出目录错误**：所有 skill/agent/command 的数据路径改为基于 `KB_DATA_ROOT` 绝对路径，不再依赖 CWD
- **子代理粒度过粗**：extract-agent 从维度级改为模块级，每个子代理只处理一个模块，覆盖率从 5-10% 提升到 100%
- **文档质量不足**：增加质量约束（Mermaid 图 ≥ 3/模块、对比表格、量化权衡、边界条件）和验收标准勾选框
- **模板双源问题**：extract-* skill 的模板必含章节内联到 skill 中，删除 templates/ 子目录

### Changed

- `/kb` command 增加 `KB_DATA_ROOT` 路径计算逻辑和模块级派发
- extract-agent 改为单模块提取（新增 `--module` 和 `--kb-data-root` 参数）
- transform-agent 增加 `--kb-data-root` 参数
- ingest skill 深化转化指导（重组而非复制）

## [0.5.0] - 2026-05-25

### Changed
- 重构调度架构：删除 kb-agent，/kb 命令直接编排 6 步检查点管道
- extract 阶段：5 维度并行派发子代理（原串行 Skill 调用）
- transform 阶段：N 维度并行派发 ingest 子代理（原串行循环）
- cross-ref 改为内联执行（原由 transform-agent 串行调用）
- 新增人类检查点：Step 3 REVIEW_E（extract 完成后用户审查）
- extract-agent 重构为单维度子代理模板
- transform-agent 重构为单维度子代理模板

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