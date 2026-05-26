# PRD Generation Skill 设计

## 问题

当前 `/init-system` 工作流存在两个结构性缺陷：

1. **brainstorming skill 产出的是 design spec，不是 PRD**。`/init-system` Step 1 调用 brainstorming，但 brainstorming 输出的是 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`（设计规格文档），而 `system-architect` 的硬门控要求"validated PRD"。产出物格式与下游消费者期望不匹配。

2. **缺少项目路线图交付**。`/init-system` 从 PRD → 架构 → 骨架 → 验证 → 提交，但没有路线图（里程碑、功能点排期、迭代路径）。项目初始化不仅需要技术骨架，还需要交付规划。

3. **缺少竞品对标能力**。产品功能识别有两种来源：从零头脑风暴和竞品功能对标。当前只有头脑风暴一种路径。

## 设计

### 新增 prd-generation Skill

**路径**：`plugins/superpowers-pro/skills/prd-generation/SKILL.md`

**核心机制**：双模式 PRD 生成，用户选择模式后走不同子流程，最终都输出标准 PRD 文档。

#### 模式选择

Skill 启动后，首先询问用户选择模式：

- **头脑风暴模式**：从模糊想法出发，通过交互式问答逐步收敛到结构化 PRD
- **竞品对标模式**：用户提供竞品名称/领域，skill 自动研究竞品功能，结合用户差异化方向生成 PRD

#### 头脑风暴模式子流程

1. **探索项目上下文** — 检查现有文件、文档、最近提交
2. **逐一提问澄清**（一次一问）：
   - 项目愿景（要解决什么问题？为谁？）
   - 目标用户与使用场景
   - 核心功能期望
   - 约束条件（技术、时间、资源）
   - 成功指标
3. **提出 2-3 种产品方案** — 权衡分析 + 推荐
4. **用户确认方案**
5. **生成 PRD 文档**

#### 竞品对标模式子流程

1. **询问竞品信息** — 竞品名称、所属领域、URL（可选）
2. **派发竞品研究 subagent** — 调用 `competitive-researcher` subagent（见下文 subagent 定义）：
   - subagent 使用 WebSearch + WebFetch 工具研究每个竞品
   - 搜索竞品功能介绍、文档、评测
   - 提取各竞品的核心功能列表
   - 整理竞品功能矩阵（功能 × 竞品）
   - **研究结果保存为文档**（知识沉淀）：`docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-competitive-analysis.md`
   - 返回研究摘要给主 skill
3. **提问差异化方向**（一次一问）：
   - 哪些功能必须对标（行业基线）
   - 哪些功能要差异化（竞争优势）
   - 哪些功能不做（明确边界）
   - 目标用户与使用场景
   - 约束条件与成功指标
4. **提出 2-3 种差异化方案** — 基于竞品矩阵，提出不同的产品定位和功能组合 + 权衡 + 推荐
5. **用户确认方案**
6. **生成 PRD 文档**

#### Subagent 定义

##### competitive-researcher（竞品研究 subagent）

**模板路径**：`plugins/superpowers-pro/skills/prd-generation/competitive-researcher-prompt.md`

遵循项目 subagent 模板模式（参考 `subagent-driven-development/implementer-prompt.md`、`brainstorming/spec-document-reviewer-prompt.md` 的结构）：

```markdown
---
name: competitive-researcher
description: 竞品研究 subagent，自动搜索和分析竞品产品功能，产出竞品分析文档
---

You are a competitive research analyst. Your job is to thoroughly research
the specified competitors and produce a structured analysis document.

## Input

You will receive:
- **Competitors**: List of competitor names/domains/URLs
- **Industry/Domain**: The market segment these competitors operate in
- **Research Scope**: Which aspects to focus on (features, pricing, UX, tech stack, etc.)

## Your Job

1. **Search each competitor** using WebSearch:
   - Product feature pages, documentation, release notes
   - Third-party reviews, comparisons, analyses
   - Pricing pages, case studies

2. **Extract and organize** for each competitor:
   - Core feature list (with capability level: full / partial / none)
   - Target user segment
   - Differentiators and positioning
   - Notable weaknesses or gaps

3. **Build competitive matrix**:
   - Rows: Features / Capabilities
   - Columns: Each competitor + "Our Project" (left blank for user to fill)
   - Cells: Capability level or specific details

4. **Write the analysis document** to:
   `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-competitive-analysis.md`

   Document structure:
   - Executive Summary
   - Competitor Profiles (one section per competitor)
   - Competitive Feature Matrix
   - Market Gap Analysis (opportunities not covered by any competitor)
   - Key Insights & Recommendations

5. **Return summary** to the caller:
   - Number of competitors researched
   - Key findings (3-5 bullet points)
   - Path to the full analysis document

## Self-Review

Before returning, verify:
- [ ] Every competitor has at least 3 sources consulted
- [ ] Feature matrix covers all major capability areas
- [ ] No TBD/TODO placeholders in the document
- [ ] Document is saved to the correct path

## Output Format

Report one of:
- **DONE**: Research complete, document saved. Include: competitors count, key findings, document path.
- **DONE_WITH_CONCERNS**: Research partially complete. Include concerns list.
- **BLOCKED**: Cannot proceed. Include blocker description.
- **NEEDS_CONTEXT**: Missing critical information. Include what's needed.
```

##### prd-reviewer（PRD 审查 subagent）

**模板路径**：`plugins/superpowers-pro/skills/prd-generation/prd-reviewer-prompt.md`

遵循项目 reviewer subagent 模板模式（参考 `subagent-driven-development/spec-reviewer-prompt.md`、`brainstorming/spec-document-reviewer-prompt.md` 的校准原则）：

```markdown
---
name: prd-reviewer
description: PRD 文档审查 subagent，检查 PRD 完整性、一致性、可执行性
---

You are a PRD reviewer. Your job is to verify that a PRD document is
complete, consistent, and ready to serve as input for architecture design.

Distrust the PRD author's claims. Read the actual document line by line.
Verify by content, not by section headers.

## What to Check

### Completeness
- Every P0 feature has a clear description AND acceptance criteria
- No TBD, TODO, "待定", "后续补充", or empty sections
- Target users and scenarios are concrete (not generic)
- Success metrics have target values (not just names)

### Consistency
- Feature priorities don't contradict each other
- Technical constraints align with feature requirements
- Non-functional requirements are compatible with the tech constraints
- If competitive analysis appendix exists, matrix findings match the feature list

### Clarity
- No feature description could be interpreted two different ways
- Acceptance criteria are testable (specific, measurable)
- Scope boundaries are explicit (what's NOT included)

### Feasibility
- P0 feature set is achievable as an MVP (not over-scoped)
- Technical constraints don't make required features impossible
- Success metrics are realistic given the constraints

### YAGNI
- No features included "just in case" or "we might need this"
- No over-specified non-functional requirements beyond what's needed

## Calibration

Only flag issues that would cause real problems during architecture design
or implementation planning. Minor wording preferences are NOT issues.

## Output Format

**Status**: Approved | Issues Found

**Issues** (if any):
For each issue, provide:
- Section reference
- Problem description
- Suggested fix

**Recommendations** (advisory, non-blocking):
- Suggestions that would improve the PRD but are not required for approval
```

#### 知识沉淀

竞品研究产出的文档独立于 PRD 保存，作为项目知识资产：

| 产出物 | 路径 | 说明 |
|--------|------|------|
| 竞品分析报告 | `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-competitive-analysis.md` | 完整竞品研究，含功能矩阵、缺口分析、建议 |
| PRD 文档 | `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-prd.md` | 标准产品需求文档 |
| 路线图 | `docs/superpowers-pro/roadmap/YYYY-MM-DD-<project>-roadmap.md` | 里程碑与迭代规划 |

竞品分析报告作为 PRD 附录引用（PRD 第 8 节附录中链接到完整报告），但独立存储以便后续查阅和更新。

#### PRD 文档标准结构

```markdown
# <项目名称> PRD

## 1. 项目愿景
- 要解决的问题
- 为什么现在做
- 预期价值

## 2. 目标用户与使用场景
- 用户画像
- 核心使用场景（3-5 个）
- 用户旅程概述

## 3. 核心功能列表
### P0 — 必须有（MVP）
- 功能 1: <描述> — <验收标准>
- 功能 2: ...

### P1 — 应该有
- 功能 3: ...

### P2 — 可以有
- 功能 4: ...

## 4. 非功能需求
- 性能
- 安全
- 可用性
- 可扩展性

## 5. 技术约束
- 已确定的技术栈/平台
- 集成要求
- 合规要求

## 6. 成功指标
- 核心指标 + 目标值
- 辅助指标

## 7. 开放问题
- 待澄清的问题列表

## 8. 附录
### 竞品功能矩阵（仅竞品对标模式）
| 功能 | 本项目 | 竞品 A | 竞品 B | 说明 |
|------|--------|--------|--------|------|
```

#### 硬门控

- **无 PRD 不进架构** — 与 `system-architect` 的门控对齐
- **PRD 必须经过用户审批** — 在 `/init-system` 流程中由 PRD_REVIEW 步骤保障

#### 输出路径

`docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-prd.md`

#### Checklist

1. 询问用户选择模式（头脑风暴 / 竞品对标）
2. 探索项目上下文
3. 执行对应模式子流程（问答澄清 / 竞品研究 + 差异化提问）
4. 提出 2-3 种产品方案 + 权衡 + 推荐（头脑风暴模式：产品方案；竞品对标模式：差异化定位方案）
5. 用户确认方案
6. 生成 PRD 文档
7. PRD 自审 — 派发 `prd-reviewer` subagent 审查（占位符扫描、一致性检查、范围检查、歧义检查、可行性检查、YAGNI 检查）
8. 用户审批 PRD

### init-system 工作流调整

**从 7 步调整为 8 步**：

| Step | 名称 | 变化 | 调用 |
|------|------|------|------|
| 1/8 | PRD | 替换原 BRAINSTORM | `superpowers:prd-generation` |
| 2/8 | PRD_REVIEW | 不变 | 人类检查点 1 |
| 3/8 | ARCHITECT | 不变 | `superpowers:system-architect` |
| 4/8 | ARCH_REVIEW | 不变 | 人类检查点 2 |
| 5/8 | SKELETON | 不变 | 直接执行 |
| 6/8 | ROADMAP | **新增** | 直接执行（内联逻辑） |
| 7/8 | VERIFY | 原 Step 6 | `superpowers:verification-before-completion` |
| 8/8 | FINISH | 原 Step 7 | 直接执行 |

#### 新增 ROADMAP 步骤

**输入**：已审批的 PRD + 已审批的架构文档

**逻辑**：
1. 从 PRD 提取功能列表及优先级（P0/P1/P2）
2. 从架构文档提取模块依赖关系
3. 基于优先级 + 依赖关系编排里程碑
4. 生成路线图文档

**路线图文档结构**：

```markdown
# <项目名称> 路线图

## 里程碑规划

### M1: <里程碑名>（<时间范围>）
**目标**: <一句话描述>
**交付功能点**:
- [ ] 功能 A（P0）
- [ ] 功能 B（P0）
**依赖前提**: 无 / M0 完成

### M2: ...

## 功能点排期

| 功能 | 优先级 | 目标里程碑 | 依赖 | 状态 |
|------|--------|-----------|------|------|
| 功能 A | P0 | M1 | — | □ |
| 功能 B | P0 | M1 | 功能 A | □ |

## 迭代路径

- **迭代 1**（M1）: 核心功能 MVP
- **迭代 2**（M2）: 增强功能
- ...

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
```

**产出物路径**：`docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-roadmap.md`

**检查点**：`━━━ [✓] Step 6/8: ROADMAP — 路线图已生成`
**产出物**：`docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-roadmap.md`

### 与现有 skill 的关系

- **brainstorming skill** — 保持不变，仍供 `/feature`、`/fix`、`/refactor` 使用
- **system-architect skill** — 保持不变，PRD 格式与其硬门控兼容
- **prd-generation skill** — 新增，仅 `/init-system` 调用
- 两个 skill 并行存在，互不影响

## 变更范围

### 新增文件

1. `plugins/superpowers-pro/skills/prd-generation/SKILL.md` — PRD 生成 skill 定义
2. `plugins/superpowers-pro/skills/prd-generation/competitive-researcher-prompt.md` — 竞品研究 subagent 模板
3. `plugins/superpowers-pro/skills/prd-generation/prd-reviewer-prompt.md` — PRD 审查 subagent 模板

### 修改文件

2. `plugins/superpowers-pro/commands/init-system.md` — 8 步流程调整
3. `plugins/superpowers-pro/.claude-plugin/plugin.json` — 版本升级（0.1.0 → 0.2.0，minor: 新 skill + 命令调整）
4. `plugins/superpowers-pro/CHANGELOG.md` — 记录变更

### 不修改的文件

- `skills/brainstorming/SKILL.md` — 保持不变
- `skills/system-architect/SKILL.md` — 保持不变
- `commands/feature.md`、`commands/fix.md`、`commands/refactor.md` — 不受影响
