# Changelog

## [Unreleased]

### Changed
- **system-architect: 重设计为 11 章结构** — 采用中文企业级架构文档结构（文档概述/业务背景/技术选型/总体架构/模块设计/数据存储/接口通信/代码库工程结构/非功能设计/部署运维/风险演进），替代原四维度结构（应用/信息/集成/技术架构）；全深度可实现（每个组件要求算法+状态机+Schema+错误链）；新增 architecture-reviewer/researcher subagent prompt；4 个 reference 合并为 architecture-guide.md；新增 anti-patterns.md；更新 depth-requirements.md（全深度模型）、architecture-review-checklist.md（11 章审查）、adr-template.md（中文+章节引用）

### Changed
- **prd-generation: 全面升级 PRD 模板至项目初始化级别** — 新增 Problem Statement（痛点+证据+代价）、Vision & Positioning、User Stories（Gherkin 验收标准）、Out of Scope、Counter-metrics、Assumptions/Dependencies/Risks、Milestones 章节；强化 What≠How 原则（PRD 不写架构决策）；竞品分析聚焦用户痛点而非功能缺口
- **competitive-researcher: 增加痛点提炼** — 输出结构新增"用户痛点"章节（行业共性痛点 vs 竞品特有痛点），每个痛点必须关联证据来源
- **prd-reviewer: 增加结构化审查矩阵** — 新增 Vision & Positioning、What vs How、Counter-metrics、Assumptions & Risks 审查维度；验收标准检查 Gherkin 格式；Out of Scope 检查是否被埋在技术约束中

### Changed
- 统一插件内所有 `superpowers` 引用为 `superpowers-pro`（skill 调用前缀、文件系统路径、文档路径、品牌文案）
- 保留 `using-superpowers` skill 功能名、`obra/superpowers` 上游 URL、`You have superpowers` 品牌文案不变

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
