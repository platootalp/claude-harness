# Changelog

## [Unreleased]

### Added
- `prd-generation` skill: 双模式 PRD 生成（头脑风暴 / 竞品对标）
- `competitive-researcher` subagent: 竞品自动研究 + 分析文档生成
- `prd-reviewer` subagent: PRD 文档完整性、一致性、可执行性审查
- `/init-system` 新增 Step 6/8 ROADMAP（里程碑、功能点、迭代路径）

### Changed
- `/init-system` Step 1 从调用 `brainstorming` 改为调用 `prd-generation`
- `/init-system` 从 7 步扩展为 8 步
- 产出物路径统一为 `docs/superpowers-pro/projects/<project>/` 按项目聚合

All notable changes to the superpowers-pro plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `system-architect` skill — AI acts as system architect for 0→1 projects, consuming PRD and producing architecture design covering application, information, integration, and technical dimensions with C4 diagrams, ADRs, and risk register
- `/feature` command — 功能开发完整流水线（8 步显式编排）
- `/fix` command — Bug 修复完整流水线（8 步显式编排）
- `/refactor` command — 重构/优化完整流水线（8 步显式编排）
- `/init-system` command — 系统初始化完整流水线（7 步显式编排）
