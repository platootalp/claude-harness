# prd-generation Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-pro:subagent-driven-development (recommended) or superpowers-pro:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate reference prd-generator into our prd-generation skill — adopt reference SKILL.md as the main skeleton, add competitive research as Phase 2, make brainstorming + competitive research serial mandatory (not either/or), and copy reference documents.

**Architecture:** 5-phase flow: Requirements Gathering (brainstorming) → Competitive Research → PRD Draft → Review & Iteration → Finalization. The SKILL.md is rewritten based on the reference implementation's structure, keeping our competitive-researcher and prd-reviewer subagents and our PRD standard structure. Three reference documents are copied verbatim.

**Tech Stack:** Markdown skill files, no code dependencies.

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `skills/prd-generation/SKILL.md` | Rewrite | Main skill definition — 5-phase flow, based on reference skeleton |
| `skills/prd-generation/prd-reviewer-prompt.md` | Keep unchanged | PRD reviewer subagent prompt |
| `skills/prd-generation/competitive-researcher-prompt.md` | Keep unchanged | Competitive researcher subagent prompt |
| `skills/prd-generation/references/prd_template.md` | Create (copy) | Standard PRD template |
| `skills/prd-generation/references/metrics_frameworks.md` | Create (copy) | AARRR/HEART/OKR metrics frameworks |
| `skills/prd-generation/references/user_story_examples.md` | Create (copy) | User story patterns and examples |
| `.claude-plugin/plugin.json` | Modify | bump version (minor) |
| `CHANGELOG.md` | Modify | add entry under [Unreleased] |

---

### Task 1: Copy reference documents

**Files:**
- Create: `skills/prd-generation/references/prd_template.md`
- Create: `skills/prd-generation/references/metrics_frameworks.md`
- Create: `skills/prd-generation/references/user_story_examples.md`

- [ ] **Step 1: Create references directory and copy files**

```bash
mkdir -p /Users/lijunyi/road/claude-harness/plugins/superpowers-pro/skills/prd-generation/references
cp /Users/lijunyi/road/claude-harness/reference/prd-generator/reference/prd_template.md /Users/lijunyi/road/claude-harness/plugins/superpowers-pro/skills/prd-generation/references/prd_template.md
cp /Users/lijunyi/road/claude-harness/reference/prd-generator/reference/metrics_frameworks.md /Users/lijunyi/road/claude-harness/plugins/superpowers-pro/skills/prd-generation/references/metrics_frameworks.md
cp /Users/lijunyi/road/claude-harness/reference/prd-generator/reference/user_story_examples.md /Users/lijunyi/road/claude-harness/plugins/superpowers-pro/skills/prd-generation/references/user_story_examples.md
```

- [ ] **Step 2: Verify files copied correctly**

```bash
ls -la /Users/lijunyi/road/claude-harness/plugins/superpowers-pro/skills/prd-generation/references/
```

Expected: 3 files listed, matching the reference originals in line count.

- [ ] **Step 3: Commit**

```bash
cd /Users/lijunyi/road/claude-harness
git add plugins/superpowers-pro/skills/prd-generation/references/
git commit -m "feat(superpowers-pro): add PRD reference documents (template, metrics, user stories)"
```

---

### Task 2: Rewrite SKILL.md

**Files:**
- Rewrite: `skills/prd-generation/SKILL.md`

This is the core task. The new SKILL.md adopts the reference implementation's structure (overview, core workflow with phases, usage patterns, best practices) but integrates our competitive research phase and our PRD standard structure.

- [ ] **Step 1: Write the new SKILL.md**

The new SKILL.md content (full text):

```markdown
---
name: prd-generation
description: Generate comprehensive, well-structured Product Requirements Documents (PRDs) through a 5-phase workflow. Use this skill when users ask to "create a PRD", "write product requirements", "document a feature", "需求文档", "产品需求", or need help structuring product specifications.
---

# PRD Generation — 五阶段产品需求文档生成

从用户痛点出发，产出标准项目初始化级 PRD。五阶段流程覆盖需求澄清、竞品调研、PRD 撰写、审查迭代、定稿归档。

<HARD-GATE>
PRD 未获用户审批前，不得调用 system-architect 或进入架构设计阶段。
</HARD-GATE>

## PRD 要解决的 6 个核心问题

项目初始化级 PRD 的根本目的是**让团队在动手前对齐"做什么、为谁做、为什么做、不做什么"**：

1. **Why** — Problem Statement + 证据链，证明痛点真实存在且值得解决
2. **Who** — Target Audience + User Stories，明确用户画像和使用场景
3. **What** — 功能需求 + 优先级，只描述用户价值，不描述实现方式
4. **What Not** — Out of Scope 显式声明，防止范围蔓延
5. **How to Know** — Success Metrics + Counter-metrics，可测试的验收标准
6. **What Could Go Wrong** — Assumptions + Dependencies + Risks，提前暴露致命点

## Core Workflow

When a user requests to create a PRD, follow this 5-phase workflow:

### Phase 1: Requirements Gathering（需求澄清）

**目标:** 从模糊想法收敛到结构化需求概要。

**执行:** 调用 `superpowers-pro:brainstorming` skill，在 PRD 语境下执行。

brainstorming skill 会：
- 探索项目上下文（文件、文档、最近提交）
- 逐一提问澄清需求（一次一问，偏多多选）
- 提出 2-3 种产品方案 + 权衡 + 推荐
- 用户确认方案后，产出需求概要设计文档

**产出:** 需求概要设计文档，保存至 `docs/superpowers-pro/specs/YYYY-MM-DD-<topic>-design.md`

**验证检查点:**
- 目标用户是否明确？
- 核心场景是否覆盖？
- 痛点是否有证据支撑？
- 成功指标是否可量化？

---

### Phase 2: Competitive Research（竞品调研）

**目标:** 基于 Phase 1 的需求概要，调研竞品以补充差异化视角。

**执行:** 派发 competitive-researcher subagent，读取 `skills/prd-generation/competitive-researcher-prompt.md` 获取 prompt。

**输入参数:**
- 竞品列表：用户提供，或基于 Phase 1 的领域信息推断 3-5 个主要竞品
- 领域：Phase 1 需求概要中的产品领域
- 研究范围：基于项目规模确定
- 项目名称 + 日期

**subagent 使用 WebSearch + WebFetch 研究竞品**，产出：
- 竞品对标表（功能覆盖、定价、优势/劣势）
- 用户痛点提炼（从竞品用户抱怨中提取）
- 差异化机会（行业共性痛点 vs 竞品特有痛点）
- 建议策略

**产出:** 竞品分析报告，保存至 `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-competitive-analysis.md`

**验证检查点:**
- 竞品是否覆盖了主要对手（至少 3 个）？
- 对标维度是否与核心场景相关？
- 痛点是否有证据（用户引述、Issue 链接）支撑？

---

### Phase 3: PRD Draft（撰写 PRD）

**目标:** 合并 Phase 1 + Phase 2 产出，生成完整 PRD 文档。

**执行步骤:**

1. **选择 PRD 格式** — 根据项目规模决定：
   - **标准 PRD** — 新产品或重大功能（参考 `references/prd_template.md`）
   - **Lean PRD** — 功能增强（Problem + Solution + Acceptance Criteria + Metrics）
   - **One-Pager** — 小改动（Problem + Solution + Success Metrics）

2. **撰写各 section** — 合并数据来源：

   | PRD Section | 数据来源 |
   |-------------|---------|
   | Problem Statement | Phase 1 需求概要 |
   | Vision & Positioning | Phase 1 需求概要 + Phase 2 竞品调研 |
   | Target Audience & User Stories | Phase 1 需求概要 + `references/user_story_examples.md` |
   | Functional Requirements | Phase 1 需求概要 |
   | Success Metrics | Phase 1 需求概要 + `references/metrics_frameworks.md` |
   | Competitive Landscape | Phase 2 竞品调研 |
   | Out of Scope | Phase 1 需求概要 |
   | Assumptions & Risks | Phase 1 需求概要 |

3. **User Stories 格式** — 参考 `references/user_story_examples.md`：

```
作为 <角色>，我想要 <行为>，以便 <价值>

验收标准 (Gherkin):
Given <前提> When <操作> Then <结果>
```

4. **Success Metrics** — 参考 `references/metrics_frameworks.md`，选择合适的指标框架：
   - AARRR (Pirate Metrics) — 增长导向
   - HEART Framework — UX 质量导向
   - North Star Metric — 单一核心指标
   - OKRs — 目标与关键结果

5. **保存 PRD** — `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-prd.md`

**验证检查点:**
- PRD 是否覆盖了 6 个核心问题？
- 每个 P0 功能是否有关联的 User Story + 验收标准？
- 每个 Core Metric 是否配了 Counter-metric？

---

### Phase 4: Review & Iteration（审查迭代）

**目标:** 确保 PRD 完整、一致、可操作。

**执行步骤:**

1. **派发 prd-reviewer subagent** — 读取 `skills/prd-generation/prd-reviewer-prompt.md` 获取 prompt，传入 PRD 文件路径

2. **处理审查反馈:**
   - **Critical issues** → 立即修复 → 重新审查
   - **Important issues** → 本轮修复
   - **Minor / Recommendations** → 记录但不在本轮修复
   - **审查者有误** → 理性反驳，记录理由

3. **迭代循环:** reviewer 不通过 → 修复 → 重新审查，最多 3 轮

4. **Self-validation checklist** — 主代理自执行（不运行 shell 脚本）：
   - 所有必需 section 是否存在（Problem Statement, User Stories, Success Metrics, Scope）
   - User Stories 是否按标准格式 + 有验收标准
   - Success Metrics 是否有量化目标和基线值
   - 是否有 placeholder / TBD / TODO / 待定 / 后续补充 残留
   - Scope 是否明确区分 In/Out
   - 每个 Core Metric 是否配 Counter-metric
   - 里程碑是否有依赖关系

**产出:** 通过审查的 PRD 文档

---

### Phase 5: Finalization（定稿归档）

**目标:** 用户审批 PRD，完成定稿归档。

**执行步骤:**

1. **用户审批** — 展示完整 PRD，等待用户明确批准
   - 批准 → 进入定稿
   - 要求修改 → 返回 Phase 3 或 Phase 4

2. **定稿归档:**
   - PRD 状态标记为 `Approved`
   - 更新 Change Log section
   - 确认归档路径：`docs/superpowers-pro/projects/<project>/`

**硬门控:** PRD 未获用户审批前，不得调用 `system-architect` 或进入架构设计阶段。

---

## PRD 文档标准结构

```markdown
# <项目名称> PRD

> 日期 | 版本 | 状态 | 作者 | 审批人

---

## 1. Problem Statement（问题陈述）

### 1.1 用户痛点
从用户视角描述痛点，不是从竞品视角。格式：
- **谁** 在 **什么场景下** 遆到 **什么问题**，导致 **什么后果**

### 1.2 痛点证据
支撑痛点真实存在的数据/研究/用户反馈来源：
- 用户访谈 N 人，X% 提到此问题
- 社区讨论/Issue 数量
- 竞品用户抱怨的具体引述

### 1.3 为什么现在做
市场时机、技术成熟度、战略窗口期

### 1.4 如果不做会怎样
不解决此问题的代价（用户流失、效率损失、竞争劣势）

---

## 2. Vision & Positioning（愿景与定位）

### 2.1 产品一句话描述
<产品名> 帮助 <目标用户> <解决什么问题>，通过 <核心方式>

### 2.2 与竞品的差异化定位
基于竞品分析的核心差异化（不是功能列表对比，是定位差异）
竞品分析完整报告: [链接](./YYYY-MM-DD-<project>-competitive-analysis.md)

---

## 3. Target Audience & User Stories（目标用户与用户故事）

### 3.1 用户画像
| 画像 | 角色 | 核心诉求 | 当前替代方案 | 痛点严重度 |

### 3.2 核心用户故事
按优先级排列，格式：作为 <角色>，我想要 <行为>，以便 <价值>
- US-1: [P0] 作为 <角色>，我想要 <行为>，以便 <价值>
- US-2: [P1] ...

### 3.3 用户旅程
关键路径的步骤流程图

---

## 4. Functional Requirements（功能需求）

### P0 — MVP 必须有
每个功能：
- **功能名**: 一句话用户价值描述（不写实现方式）
- **关联用户故事**: US-X
- **验收标准**: Given <前提> When <操作> Then <结果>（Gherkin 格式，可测试）
- **边界条件**: 正常路径 + 边界情况

### P1 — 应该有
（同上格式）

### P2 — 可以有
（同上格式，可简化）

---

## 5. Non-Functional Requirements（非功能需求）

| 维度 | 要求 | 验收标准 | 优先级 |
|------|------|---------|--------|
| 性能 | ... | 在 <条件> 下 <指标> <阈值> | P0/P1 |
| 安全 | ... | ... | ... |
| 可用性 | ... | ... | ... |
| 可扩展性 | ... | ... | ... |

---

## 6. Out of Scope（明确不做）

| 不做的功能 | 原因 | 何时可能重新考虑 |
|-----------|------|----------------|
| ... | ... | ... |

---

## 7. Success Metrics（成功指标）

### 7.1 核心指标
| 指标 | 基线（当前值） | 目标值 | 衡量方式 | 优先级 |

### 7.2 反指标（Counter-metrics）
| 指标 | 基线 | 不可超过的阈值 | 原因 |

---

## 8. Assumptions, Dependencies & Risks（假设、依赖与风险）

### 8.1 假设
| 假设 | 如果假设不成立的应对方案 | 验证方式 |

### 8.2 依赖
| 依赖项 | 类型（技术/组织/外部） | 影响范围 | 缓解方案 |

### 8.3 风险
| 风险 | 概率 | 影响 | 缓解策略 |

---

## 9. Milestones（里程碑）

| 里程碑 | 交付范围 | 目标日期 | 依赖 |
|--------|---------|---------|------|
| M0: 技术验证 | 核心假设验证 | ... | ... |
| M1: MVP | P0 功能 | ... | ... |
| M2: V1.0 | P0 + P1 | ... | ... |

---

## 10. Open Questions（开放问题）

| # | 问题 | 影响 | 负责人 | 截止日期 | 状态 |
|---|------|------|--------|---------|------|
| 1 | ... | ... | ... | ... | Open/Resolved |

---

## 附录

### A. 竞品功能矩阵
| 功能 | 本项目 | 竞品 A | 竞品 B | 说明 |
|------|--------|--------|--------|------|

### B. 术语表
（项目特定术语定义）

### C. 参考文档
（相关设计文档、研究报告链接）
```

## PRD Formats

### Standard PRD
Full comprehensive document — all 10 sections + appendices. Use for new products or major features. Reference `references/prd_template.md` for detailed section templates.

### Lean PRD
Streamlined for agile teams:
- Problem Statement (1 paragraph)
- Proposed Solution (2-3 bullet points)
- User Stories + Acceptance Criteria (core stories only)
- Success Metrics (North Star + 2-3 supporting)
- Out of Scope (5 items max)
- Timeline (target date only)

### One-Pager
Executive summary format:
- Problem (1 sentence)
- Solution (1 paragraph)
- Key Metrics (3 max)
- Target Users (1 line)
- Launch Date

Specify format when requesting: "Create a lean PRD for..." or "Generate a standard PRD for..."

## Usage Patterns

### Pattern 1: New Product PRD

**User Request:** "Create a PRD for a new analytics dashboard product"

**Execution:**
1. Phase 1: brainstorming — comprehensive discovery (market, users, goals)
2. Phase 2: competitive research — identify 3-5 competing analytics tools
3. Phase 3: standard PRD format with full competitive analysis section
4. Phase 4: prd-reviewer validates completeness
5. Phase 5: user approves

### Pattern 2: Feature Enhancement PRD

**User Request:** "Write requirements for improving our search functionality"

**Execution:**
1. Phase 1: brainstorming — identify current pain points and desired improvements
2. Phase 2: competitive research — research search features in similar products
3. Phase 3: lean PRD with before/after metrics
4. Phase 4: prd-reviewer validates
5. Phase 5: user approves

### Pattern 3: Quick Fix PRD

**User Request:** "Create a lightweight PRD for a small bug fix feature"

**Execution:**
1. Phase 1: brainstorming — quick problem clarification (skip deep discovery if user provides brief)
2. Phase 2: competitive research — skip if no relevant competitors, or quick scan only
3. Phase 3: one-pager format
4. Phase 4: self-validation only (skip subagent review for small scope)
5. Phase 5: user approves

## PRD Best Practices

### Writing Quality Requirements

**Good Requirements Are:**
- **Specific**: Clear and unambiguous
- **Measurable**: Can be verified/tested
- **Achievable**: Technically feasible
- **Relevant**: Tied to user/business value
- **Time-bound**: Has clear timeline

**Avoid:**
- Vague language ("fast", "easy", "intuitive")
- Implementation details (let engineers decide how)
- Feature creep (stick to core requirements)
- Assumptions without validation

### User Story Best Practices

**DO:**
- Focus on user value, not features
- Write from user perspective
- Include clear acceptance criteria (Gherkin: Given/When/Then)
- Keep stories independent and small
- Use consistent format: "作为 <角色>，我想要 <行为>，以便 <价值>"
- Reference `references/user_story_examples.md` for patterns

**DON'T:**
- Write technical implementation details
- Create dependencies between stories
- Make stories too large (epics)
- Use internal jargon
- Skip acceptance criteria

### Scope Management

**In-Scope:**
- List specific features/capabilities included
- Be explicit and detailed
- Link to user stories

**Out-of-Scope:**
- Explicitly state what's NOT included
- Prevents scope creep
- Include reason and when to reconsider

### Success Metrics Guidelines

Reference `references/metrics_frameworks.md` for detailed guidance on each framework.

**Choose Metrics That:**
- Align with business objectives
- Are measurable and trackable
- Have clear targets/thresholds
- Include both leading and lagging indicators
- Consider user and business value

**Every Core Metric MUST have a Counter-metric:**
- Counter-metrics prevent optimizing one metric at the expense of another
- Example: "Increase conversion rate" → Counter: "Ensure support tickets don't increase > 10%"

## Self-Review Checklist

Before finalizing the PRD, verify:

- [ ] **Problem is clear**: Anyone can understand what we're solving
- [ ] **Users are identified**: We know who this is for
- [ ] **Success is measurable**: We can determine if it worked (with quantified targets + baselines)
- [ ] **Scope is bounded**: Clear what's in and out
- [ ] **Requirements are testable**: QA can verify completion (Gherkin acceptance criteria)
- [ ] **Counter-metrics defined**: Every core metric has a counter-metric
- [ ] **No placeholders**: No TBD, TODO, 待定, 后续补充, or empty sections
- [ ] **What ≠ How**: PRD describes user value, not implementation
- [ ] **Risks are identified**: We've thought through what could go wrong

## 关键原则

- **一次一问** — 不用多个问题轰炸用户
- **优先多选** — 比开放式问题更容易回答
- **YAGNI** — 从所有方案中移除非必要功能
- **探索替代方案** — 提出方案前总是给出 2-3 个选项
- **增量验证** — 每步确认，不要到最后才发现方向错了
- **What ≠ How** — PRD 只描述用户价值和功能需求（What），严格不写实现方式（How）。架构决策属于 system-architect 的输出，不出现在 PRD 中
- **痛点从用户出发** — "竞品缺 X 功能" ≠ "用户在痛"。必须追问竞品功能缺失背后的真实用户痛点
- **验收标准可测试** — 使用 Gherkin 格式（Given/When/Then），或至少给出具体的测试条件和阈值条件
- **反指标不可省** — 每个 Core Metric 必须配至少一个 Counter-metric，防止优化一个指标时牺牲另一个
- **Out of Scope 显式声明** — 不做的功能和做的一样重要，必须列出原因和重新考虑的时机

## Resources

This skill includes bundled resources:

### references/

- **prd_template.md** — Standard PRD template structure with detailed section templates
- **user_story_examples.md** — User story patterns and examples across different domains
- **metrics_frameworks.md** — Guide to PM metrics (AARRR, HEART, North Star, OKRs)

### Subagent Prompts

- **competitive-researcher-prompt.md** — Prompt for competitive research subagent
- **prd-reviewer-prompt.md** — Prompt for PRD document reviewer subagent

## Tips for Product Managers

### Before Writing the PRD

1. **Do your research**: User interviews, data analysis, competitive analysis
2. **Validate the problem**: Ensure it's worth solving
3. **Check strategic alignment**: Does this fit our roadmap?
4. **Consider alternatives**: Is this the best solution?

### During PRD Creation

1. **Be clear, not clever**: Simple language wins
2. **Show, don't tell**: Use examples, mockups, diagrams
3. **Think edge cases**: What could go wrong?
4. **Prioritize ruthlessly**: What's MVP vs. nice-to-have?
5. **Collaborate early**: Don't work in isolation

### After PRD Completion

1. **Review with stakeholders**: Get feedback early
2. **Iterate based on input**: PRDs are living documents
3. **Get formal sign-off**: Ensure commitment
4. **Keep it updated**: Adjust as understanding evolves
```

- [ ] **Step 2: Verify SKILL.md was written correctly**

```bash
wc -l /Users/lijunyi/road/claude-harness/plugins/superpowers-pro/skills/prd-generation/SKILL.md
head -5 /Users/lijunyi/road/claude-harness/plugins/superpowers-pro/skills/prd-generation/SKILL.md
```

Expected: ~300+ lines, frontmatter with `name: prd-generation`, first heading "PRD Generation — 五阶段产品需求文档生成".

- [ ] **Step 3: Commit**

```bash
cd /Users/lijunyi/road/claude-harness
git add plugins/superpowers-pro/skills/prd-generation/SKILL.md
git commit -m "feat(superpowers-pro): rewrite prd-generation SKILL.md with 5-phase workflow and competitive research integration"
```

---

### Task 3: Update version and changelog

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Read current plugin.json version**

```bash
cat /Users/lijunyi/road/claude-harness/plugins/superpowers-pro/.claude-plugin/plugin.json
```

- [ ] **Step 2: Bump version (minor) and update CHANGELOG**

Read `plugin.json`, bump version from current to next minor (e.g. 0.2.1 → 0.3.0). Add changelog entry under `[Unreleased]`.

- [ ] **Step 3: Commit version bump**

```bash
cd /Users/lijunyi/road/claude-harness
git add plugins/superpowers-pro/.claude-plugin/plugin.json plugins/superpowers-pro/CHANGELOG.md
git commit -m "feat(superpowers-pro): bump version to 0.3.0 for prd-generation integration"
```

---

## Self-Review

**1. Spec coverage check:**

| Spec Requirement | Covered by Task |
|-----------------|----------------|
| 5-phase flow (brainstorming → competitive → PRD → review → finalize) | Task 2 (SKILL.md rewrite) |
| Brainstorming + competitive research serial mandatory | Task 2 (SKILL.md Phase 1+2) |
| Copy 3 reference documents | Task 1 |
| Keep prd-reviewer-prompt.md unchanged | Not touched (implicit) |
| Keep competitive-researcher-prompt.md unchanged | Not touched (implicit) |
| PRD format selection (Standard/Lean/One-Pager) | Task 2 (SKILL.md Formats section) |
| Validation checklist (from validate_prd.sh logic) | Task 2 (SKILL.md Phase 4 + Self-Review Checklist) |
| Version bump + changelog | Task 3 |

All spec requirements covered. No gaps.

**2. Placeholder scan:** No TBD, TODO, "implement later", "fill in details" found. All code/content is complete.

**3. Type consistency:** No code types involved — all markdown files. File paths are consistent across all tasks.