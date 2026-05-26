# PRD Generation Skill 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 prd-generation skill（双模式 PRD 生成 + 竞品研究 subagent + PRD 审查 subagent），调整 init-system 命令为 8 步流程，升级插件版本。

**Architecture:** 新 skill 独立于现有 brainstorming，通过双模式子流程（头脑风暴 / 竞品对标）产出标准 PRD 文档。竞品研究由 competitive-researcher subagent 执行，PRD 自审由 prd-reviewer subagent 执行。init-system 从 7 步扩展为 8 步（Step 1 改用 prd-generation，Step 6 新增 ROADMAP）。

**Tech Stack:** Markdown skill 定义 + subagent prompt 模板（无代码变更）

---

## File Structure

| 操作 | 路径 | 职责 |
|------|------|------|
| Create | `plugins/superpowers-pro/skills/prd-generation/SKILL.md` | PRD 生成 skill 主文件，双模式流程定义 |
| Create | `plugins/superpowers-pro/skills/prd-generation/competitive-researcher-prompt.md` | 竞品研究 subagent prompt 模板 |
| Create | `plugins/superpowers-pro/skills/prd-generation/prd-reviewer-prompt.md` | PRD 审查 subagent prompt 模板 |
| Modify | `plugins/superpowers-pro/commands/init-system.md` | 7 步 → 8 步流程调整 |
| Modify | `plugins/superpowers-pro/.claude-plugin/plugin.json` | 版本 0.1.0 → 0.2.0 |
| Modify | `plugins/superpowers-pro/CHANGELOG.md` | 新增 [Unreleased] 条目 |

---

### Task 1: 创建 competitive-researcher subagent prompt

**Files:**
- Create: `plugins/superpowers-pro/skills/prd-generation/competitive-researcher-prompt.md`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p plugins/superpowers-pro/skills/prd-generation
```

- [ ] **Step 2: 写入 competitive-researcher-prompt.md**

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
- **Project Name**: The project name (used in output file path)
- **Date**: Current date in YYYY-MM-DD format (used in output file path)

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
   ```markdown
   # <项目名称> 竞品分析报告

   ## 概述
   研究范围、竞品数量、核心发现摘要

   ## 竞品概览

   ### <竞品 A>
   - 定位与目标用户
   - 核心功能列表
   - 差异化优势
   - 主要不足

   ### <竞品 B>
   ...

   ## 竞品功能矩阵

   | 功能/能力 | 本项目 | 竞品 A | 竞品 B | 说明 |
   |-----------|--------|--------|--------|------|
   | 功能 1    |        | ✅     | ⚠️    | ...  |
   | 功能 2    |        | ❌     | ✅     | ...  |

   图例: ✅ 完整支持 | ⚠️ 部分支持 | ❌ 不支持 | 留空待填

   ## 市场缺口分析
   竞品均未覆盖的功能/能力 → 潜在差异化机会

   ## 关键洞察与建议
   3-5 条可操作的产品建议
   ```

5. **Return summary** to the caller:
   - Number of competitors researched
   - Key findings (3-5 bullet points)
   - Path to the full analysis document

## Self-Review

Before returning, verify:
- [ ] Every competitor has at least 3 sources consulted
- [ ] Feature matrix covers all major capability areas
- [ ] No TBD/TODO/待定 placeholders in the document
- [ ] Document is saved to the correct path

## Output Format

Report one of:
- **DONE**: Research complete, document saved. Include: competitors count, key findings, document path.
- **DONE_WITH_CONCERNS**: Research partially complete. Include concerns list.
- **BLOCKED**: Cannot proceed. Include blocker description.
- **NEEDS_CONTEXT**: Missing critical information. Include what's needed.
```

- [ ] **Step 3: 验证文件**

```bash
head -5 plugins/superpowers-pro/skills/prd-generation/competitive-researcher-prompt.md
```

Expected: 文件以 `---` 开头，包含 frontmatter

---

### Task 2: 创建 prd-reviewer subagent prompt

**Files:**
- Create: `plugins/superpowers-pro/skills/prd-generation/prd-reviewer-prompt.md`

- [ ] **Step 1: 写入 prd-reviewer-prompt.md**

```markdown
---
name: prd-reviewer
description: PRD 文档审查 subagent，检查 PRD 完整性、一致性、可执行性
---

You are a PRD reviewer. Your job is to verify that a PRD document is
complete, consistent, and ready to serve as input for architecture design.

Distrust the PRD author's claims. Read the actual document line by line.
Verify by content, not by section headers.

## Input

You will receive:
- **PRD Path**: Path to the PRD document to review

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
- **Section**: Which section of the PRD
- **Problem**: What's wrong
- **Suggested fix**: How to resolve it

**Recommendations** (advisory, non-blocking):
- Suggestions that would improve the PRD but are not required for approval
```

- [ ] **Step 2: 验证文件**

```bash
head -5 plugins/superpowers-pro/skills/prd-generation/prd-reviewer-prompt.md
```

Expected: 文件以 `---` 开头，包含 frontmatter

---

### Task 3: 创建 prd-generation SKILL.md

**Files:**
- Create: `plugins/superpowers-pro/skills/prd-generation/SKILL.md`

- [ ] **Step 1: 写入 SKILL.md**

```markdown
---
name: prd-generation
description: 双模式 PRD 生成 — 头脑风暴模式（从想法澄清到结构化 PRD）或竞品对标模式（竞品研究 + 差异化定位），产出标准 PRD 文档
---

# PRD Generation — 双模式产品需求文档生成

从产品功能识别出发，产出标准 PRD 文档。两种模式覆盖不同的需求来源：从零头脑风暴或基于竞品对标。

<HARD-GATE>
PRD 未获用户审批前，不得调用 system-architect 或进入架构设计阶段。
</HARD-GATE>

## Checklist

1. 选择模式（头脑风暴 / 竞品对标）
2. 探索项目上下文
3. 执行对应模式子流程
4. 提出 2-3 种产品方案 + 权衡 + 推荐
5. 用户确认方案
6. 生成 PRD 文档
7. PRD 自审（派发 prd-reviewer subagent）
8. 用户审批 PRD

## 模式选择

启动后首先询问用户选择模式：

- **头脑风暴模式**：从模糊想法出发，通过交互式问答逐步收敛到结构化 PRD
- **竞品对标模式**：研究竞品功能，结合差异化方向生成 PRD

## 头脑风暴模式

### 子流程

1. **探索项目上下文** — 检查现有文件、文档、最近提交，了解项目现状
2. **逐一提问澄清**（一次一问）：
   - 项目愿景（要解决什么问题？为谁？）
   - 目标用户与使用场景
   - 核心功能期望
   - 约束条件（技术、时间、资源）
   - 成功指标
3. **提出 2-3 种产品方案** — 权衡分析 + 推荐
4. **用户确认方案**
5. **生成 PRD 文档**（按下方标准结构）
6. **PRD 自审** — 派发 prd-reviewer subagent 审查
7. **用户审批 PRD**

## 竞品对标模式

### 子流程

1. **询问竞品信息** — 竞品名称、所属领域、URL（可选）
2. **派发 competitive-researcher subagent** — 读取 `skills/prd-generation/competitive-researcher-prompt.md` 获取 prompt，通过 Agent 工具派发：
   - 传入竞品列表、领域、研究范围、项目名称、日期
   - subagent 使用 WebSearch + WebFetch 研究竞品
   - 研究结果保存为 `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-competitive-analysis.md`
   - subagent 返回研究摘要
3. **提问差异化方向**（一次一问）：
   - 哪些功能必须对标（行业基线）
   - 哪些功能要差异化（竞争优势）
   - 哪些功能不做（明确边界）
   - 目标用户与使用场景
   - 约束条件与成功指标
4. **提出 2-3 种差异化定位方案** — 基于竞品矩阵，提出不同的产品定位和功能组合 + 权衡 + 推荐
5. **用户确认方案**
6. **生成 PRD 文档**（按下方标准结构）
7. **PRD 自审** — 派发 prd-reviewer subagent 审查
8. **用户审批 PRD**

## PRD 文档标准结构

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
- 功能 2: <描述> — <验收标准>

### P1 — 应该有
- 功能 3: <描述> — <验收标准>

### P2 — 可以有
- 功能 4: <描述> — <验收标准>

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
完整竞品分析报告: [链接](./YYYY-MM-DD-<project>-competitive-analysis.md)

| 功能 | 本项目 | 竞品 A | 竞品 B | 说明 |
|------|--------|--------|--------|------|
```

## 输出路径

`docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-prd.md`

## 关键原则

- **一次一问** — 不用多个问题轰炸用户
- **优先多选** — 比开放式问题更容易回答
- **YAGNI** — 从所有方案中移除非必要功能
- **探索替代方案** — 提出方案前总是给出 2-3 个选项
- **增量验证** — 每步确认，不要到最后才发现方向错了
```

- [ ] **Step 2: 验证文件**

```bash
head -5 plugins/superpowers-pro/skills/prd-generation/SKILL.md
```

Expected: 文件以 `---` 开头，frontmatter 包含 name: prd-generation

---

### Task 4: 修改 init-system 命令

**Files:**
- Modify: `plugins/superpowers-pro/commands/init-system.md`

- [ ] **Step 1: 替换进度总览（7 步 → 8 步）**

将原来的进度总览：

```
▶ /init-system 启动 — 系统初始化工作流

  Step 1/7  BRAINSTORM    □  探索项目需求，产出 PRD
  Step 2/7  PRD_REVIEW    □  PRD 审批（人类检查点 1）
  Step 3/7  ARCHITECT     □  四层架构设计 + ADR
  Step 4/7  ARCH_REVIEW   □  架构文档审批（人类检查点 2）
  Step 5/7  SKELETON      □  创建项目骨架
  Step 6/7  VERIFY        □  验证项目可运行
  Step 7/7  FINISH        □  初始提交 + 推送
```

替换为：

```
▶ /init-system 启动 — 系统初始化工作流

  Step 1/8  PRD           □  产品需求文档（头脑风暴或竞品对标）
  Step 2/8  PRD_REVIEW    □  PRD 审批（人类检查点 1）
  Step 3/8  ARCHITECT     □  四层架构设计 + ADR
  Step 4/8  ARCH_REVIEW   □  架构文档审批（人类检查点 2）
  Step 5/8  SKELETON      □  创建项目骨架
  Step 6/8  ROADMAP       □  项目路线图（里程碑、功能点、迭代路径）
  Step 7/8  VERIFY        □  验证项目可运行
  Step 8/8  FINISH        □  初始提交 + 推送
```

- [ ] **Step 2: 替换 Step 1（BRAINSTORM → PRD）**

将：

```markdown
## Step 1/7: BRAINSTORM

调用 `superpowers:brainstorming` skill。

- 探索项目愿景、目标用户、核心功能、技术约束
- 逐一提问澄清需求（一次一问）
- 提出 2-3 种方案 + 权衡 + 推荐
- 产出 PRD 文档

检查点: `━━━ [✓] Step 1/7: BRAINSTORM — PRD 已产出`
产出物: `docs/superpowers-pro/prd/YYYY-MM-DD-<project>-prd.md`
```

替换为：

```markdown
## Step 1/8: PRD

调用 `superpowers:prd-generation` skill。

- 询问用户选择模式：头脑风暴 / 竞品对标
- 头脑风暴模式：从想法出发，问答澄清，产出 PRD
- 竞品对标模式：派发 competitive-researcher subagent 研究竞品，差异化定位，产出 PRD
- PRD 自审：派发 prd-reviewer subagent 审查

检查点: `━━━ [✓] Step 1/8: PRD — PRD 已产出`
产出物: `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-prd.md`
```

- [ ] **Step 3: 更新 Step 2-5 的编号（7 → 8）**

将文件中所有 `Step 2/7` → `Step 2/8`，`Step 3/7` → `Step 3/8`，`Step 4/7` → `Step 4/8`，`Step 5/7` → `Step 5/8`。

同时更新 Step 3 ARCHITECT 的产出物路径：

将：
```
产出物: `docs/superpowers-pro/architecture/YYYY-MM-DD-<project>-architecture.md` + `docs/superpowers-pro/architecture/adr/` 下的 ADR 文件
```

替换为：
```
产出物: `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-architecture.md` + `docs/superpowers-pro/projects/<project>/adr/` 下的 ADR 文件
```

- [ ] **Step 4: 在 Step 5（SKELETON）之后插入 Step 6（ROADMAP）**

在 Step 5 的检查点之后、原 Step 6（VERIFY）之前，插入：

```markdown
## Step 6/8: ROADMAP

基于已审批的 PRD 和架构文档制定项目路线图。

- 从 PRD 提取功能列表及优先级（P0/P1/P2）
- 从架构文档提取模块依赖关系
- 基于优先级 + 依赖关系编排里程碑
- 生成路线图文档

路线图文档结构：

```
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

检查点: `━━━ [✓] Step 6/8: ROADMAP — 路线图已生成`
产出物: `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-roadmap.md`
```

- [ ] **Step 5: 更新原 Step 6/7 → Step 7/8（VERIFY）和原 Step 7/7 → Step 8/8（FINISH）**

将所有 `Step 6/7` → `Step 7/8`，`Step 7/7` → `Step 8/8`。

- [ ] **Step 6: 验证文件完整性**

```bash
grep -n "Step [0-9]/" plugins/superpowers-pro/commands/init-system.md
```

Expected: 8 行，分别是 Step 1/8 到 Step 8/8，无残留的 /7 编号

---

### Task 5: 升级插件版本 + 更新 CHANGELOG

**Files:**
- Modify: `plugins/superpowers-pro/.claude-plugin/plugin.json`
- Modify: `plugins/superpowers-pro/CHANGELOG.md`

- [ ] **Step 1: 更新 plugin.json 版本号**

将 `"version": "0.1.0"` 改为 `"version": "0.2.0"`

- [ ] **Step 2: 在 CHANGELOG.md 顶部新增 [Unreleased] 条目**

在文件顶部（如果已有 `[Unreleased]` 则在其下方）添加：

```markdown
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
```

- [ ] **Step 3: 验证版本号**

```bash
grep '"version"' plugins/superpowers-pro/.claude-plugin/plugin.json
```

Expected: `"version": "0.2.0"`

---

### Task 6: 提交所有变更

**Files:**
- All files from Tasks 1-5

- [ ] **Step 1: 查看变更状态**

```bash
git status
git diff --stat
```

- [ ] **Step 2: 提交**

```bash
git add plugins/superpowers-pro/skills/prd-generation/SKILL.md \
  plugins/superpowers-pro/skills/prd-generation/competitive-researcher-prompt.md \
  plugins/superpowers-pro/skills/prd-generation/prd-reviewer-prompt.md \
  plugins/superpowers-pro/commands/init-system.md \
  plugins/superpowers-pro/.claude-plugin/plugin.json \
  plugins/superpowers-pro/CHANGELOG.md
git commit -m "feat(superpowers-pro): add prd-generation skill + competitive-researcher/prd-reviewer subagents + init-system 8-step workflow"
```

- [ ] **Step 3: 验证提交**

```bash
git log --oneline -1
git diff HEAD~1 --stat
```

Expected: 6 files changed, 1 commit
