# Changelog

## [0.6.0] - 2026-05-27

### Changed
- **prd-generation: 重构为五阶段流程** — 以参考实现 prd-generator SKILL.md 为骨架重写；头脑风暴与竞品调研从二选一改为串行必选（Phase 1 需求澄清 → Phase 2 竞品调研）；新增 Phase 3 PRD Draft（合并 Phase 1+2 产出 + PRD 格式选择）、Phase 4 Review & Iteration（审查反馈分级处理 + 自执行 validation checklist）、Phase 5 Finalization（用户审批硬门控 + 定稿归档）；新增 PRD Formats（Standard/Lean/One-Pager）、Usage Patterns（3 种使用场景）、PRD Best Practices、Self-Review Checklist、Resources 章节；Phase 1 直接调用 brainstorming skill（不再内联定义子步骤）

### Added
- `references/prd_template.md` — 从 reference/prd-generator 复制，Standard PRD 完整模板
- `references/metrics_frameworks.md` — 从 reference/prd-generator 复制，AARRR/HEART/North Star/OKRs 指标框架指南
- `references/user_story_examples.md` — 从 reference/prd-generator 复制，用户故事范例与最佳实践

## [Unreleased]

### Added

- **brainstorming: 新增 review-mode frontmatter 变量** — 支持 `section-by-section`（默认，每节确认）和 `full`（一次性呈现，跳过分节确认）两种设计呈现模式；`full` 模式下 User Review Gate 仍保留

### Removed

- **executing-plans: 移除技能** — subagent-driven-development 成为唯一开发执行流程；writing-plans 不再提供执行方式选择，计划完成后直接使用 SDD；SDD 决策图简化，移除 executing-plans 对比和引用

### Added
- **prd-generation: 集成 jamesrochabrun/skills prd-generator 参考资源** — 新增 `references/prd_template.md`（Standard/Lean/One-Pager 三种规模 PRD 模板，融合项目初始化级结构与行业最佳实践）、`references/user_story_examples.md`（用户故事编写指南：INVEST 原则、10 个领域示例、验收标准模式、常见错误、拆分技巧）、`references/metrics_frameworks.md`（指标框架指南：AARRR、HEART、North Star、OKRs、PMF 指标、框架选择矩阵）、`scripts/generate_prd.sh`（交互式 PRD 生成脚本）、`scripts/validate_prd.sh`（PRD 完整性与质量校验脚本，支持中文 PRD 结构和 What≠How 检查）；SKILL.md 新增 PRD 类型选择、用户故事/指标框架参考步骤、Self-Review Checklist、Resources 章节

### Changed
- **Breaking:** /feature、/fix、/refactor 命令中 ISOLATE 步骤前移至 PLAN 之前（Step 3 ↔ Step 4 互换）
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
