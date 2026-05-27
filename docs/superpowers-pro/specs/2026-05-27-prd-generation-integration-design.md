# prd-generation Skill 重构设计文档

> 日期: 2026-05-27 | 状态: Draft | 作者: Claude | 审批人: 待定

---

## 1. Problem Statement

### 1.1 用户痛点

当前 `prd-generation` skill 存在以下问题：
- **头脑风暴与竞品调研二选一**：用户必须选择其中一种模式，但实际需求往往两者都需要——先澄清需求（头脑风暴），再补充差异化视角（竞品调研）
- **缺少参考文档**：skill 内没有 metrics frameworks、user story examples 等参考资料，agent 生成 PRD 时缺乏行业标准的指标框架和用户故事模板
- **缺少 PRD 模板**：只有 SKILL.md 中的标准结构描述，没有独立的模板文件供 agent 参考
- **流程不够结构化**：缺少验证检查点和明确的产出格式定义

### 1.2 参考实现的价值

`reference/prd-generator/` 提供了：
- 丰富的参考文档（prd_template.md, metrics_frameworks.md, user_story_examples.md）
- 更细粒度的 phase 内子步骤结构
- validation checklist 逻辑（从 validate_prd.sh 可提炼）

### 1.3 如果不做会怎样

- 用户在需要同时做头脑风暴和竞品调研时，被迫分两次调用 skill
- PRD 中 Success Metrics 缺乏标准化框架支撑
- User Stories 格式不一致，缺少行业最佳实践参考

---

## 2. Vision & Positioning

### 2.1 产品一句话描述

prd-generation 帮助产品经理从需求澄清到竞品对标产出标准项目初始化级 PRD，通过五阶段结构化流程确保 PRD 覆盖核心六问。

### 2.2 与现有设计的差异

- 从"二选一"改为"串行必选"：头脑风暴 → 竞品调研，两者产出合并到 PRD
- 以参考实现的流程结构为主骨架，融入我们的竞品调研和 review 子代理

---

## 3. Target Audience & User Stories

### 3.1 用户画像

| 画像 | 角色 | 核心诉求 | 当前替代方案 | 痛点严重度 |
|------|------|---------|------------|-----------|
| 产品经理 | 定义需求 | 产出结构化 PRD | 手动写文档 | 高 |
| 技术创始人 | 从零到一规划 | 既要需求澄清又要竞品对标 | 分两步调用 skill | 中 |
| 开发团队 lead | 功能增强规划 | 快速产出 lean PRD | 直接写 tech spec | 低 |

### 3.2 核心用户故事

- US-1: [P0] 作为产品经理，我想要一个同时包含需求澄清和竞品调研的 PRD 生成流程，以便一次产出包含用户视角和市场竞争视角的完整 PRD
- US-2: [P0] 作为技术创始人，我想要在 PRD 生成过程中参考行业标准的指标框架和用户故事模板，以便 PRD 的 Success Metrics 和 User Stories 符合行业规范
- US-3: [P1] 作为产品经理，我想要选择不同 PRD 格式（标准/Lean/One-Pager），以便根据项目规模产出适当详细度的文档

---

## 4. Functional Requirements

### P0 — MVP 必须有

**功能名**: 五阶段 PRD 生成流程
- **关联用户故事**: US-1
- **验收标准**: Given 用户调用 prd-generation skill, When 流程启动, Then 按顺序执行 Phase 1-5，每阶段有验证检查点

**功能名**: 串行执行头脑风暴 + 竞品调研
- **关联用户故事**: US-1
- **验收标准**: Given Phase 1 完成, When 进入 Phase 2, Then 基于 Phase 1 产出做竞品调研；两者产出合并到 Phase 3 PRD

**功能名**: 参考文档集成
- **关联用户故事**: US-2
- **验收标准**: Given skill 目录包含 references/ 子目录, When agent 生成 PRD, Then 参考 metrics_frameworks.md 选择指标框架，参考 user_story_examples.md 写用户故事

### P1 — 应该有

**功能名**: PRD 格式选择
- **关联用户故事**: US-3
- **验收标准**: Given 用户指定项目规模, When Phase 3 开始, Then 选择标准 PRD / Lean PRD / One-Pager 格式

---

## 5. Out of Scope

| 不做的功能 | 原因 | 何时可能重新考虑 |
|-----------|------|----------------|
| shell 脚本复制（generate_prd.sh / validate_prd.sh） | 保持 agent 驱动的 skill 风格，validate_prd.sh 的逻辑由主代理在 Phase 4 自执行 | 如果用户需要 CLI 工具 |
| 自动 WebSearch 竞品调研 | 竞品调研通过 competitive-researcher subagent 执行，subagent 已具备 WebSearch 能力 | 不需要 |
| PRD 版本管理 | 超出 skill 范围，应由项目管理流程处理 | 后续版本 |

---

## 6. Design Details

### 6.1 整体流程架构

```
Phase 1: Requirements Gathering (需求澄清)
  → 调用 superpowers-pro:brainstorming skill
  → 产出: 需求概要设计文档
  ↓
Phase 2: Competitive Research (竞品调研)
  → 调用 competitive-researcher subagent
  → 产出: 竞品对标表 + 差异化机会
  ↓
Phase 3: PRD Draft (撰写 PRD)
  → 参考 references/prd_template.md 选择格式
  → 参考 references/metrics_frameworks.md 写 Success Metrics
  → 参考 references/user_story_examples.md 写 User Stories
  → 合并 Phase 1 + Phase 2 产出
  → 产出: 完整 PRD 文档
  ↓
Phase 4: Review & Iteration (审查迭代)
  → 派发 prd-reviewer subagent
  → 处理反馈 (Critical→修复→重审, Important→本轮修复, Minor→记录)
  → 自执行 validation checklist（从 validate_prd.sh 逻辑提炼）
  → 最多 3 轮迭代
  ↓
Phase 5: Finalization (定稿归档)
  → 用户审批（硬门控）
  → 定稿归档到 docs/superpowers-pro/projects/
```

### 6.2 Phase 1 — Requirements Gathering

直接调用 `superpowers-pro:brainstorming` skill，在 PRD 语境下执行：
- brainstorming 的探索上下文 → 理解项目背景
- brainstorming 的逐项提问 → 澄清目标用户、场景、痛点、功能范围、成功指标
- brainstorming 的方案提议 → 2-3 种产品方向 + 权衡
- brainstorming 的产出 → 需求概要设计文档

不额外定义子步骤，完全复用 brainstorming skill 的流程。

### 6.3 Phase 2 — Competitive Research

基于 Phase 1 产出的需求概要，调用 `competitive-researcher-prompt.md` 定义的 subagent：

- 输入: Phase 1 需求概要（目标用户、核心场景、痛点）+ 竞品名称（用户提供或 agent 从领域推断）
- 执行: 逐个分析竞品功能覆盖、定价、用户抱怨、差异化机会
- 产出: 竞品对标表 + 差异化机会，保存为 `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-competitive-analysis.md`

### 6.4 Phase 3 — PRD Draft

合并 Phase 1 和 Phase 2 产出，撰写完整 PRD：

1. **选择 PRD 格式**:
   - 新产品 / 重大功能 → 标准 PRD（参考 `references/prd_template.md`）
   - 功能增强 → Lean PRD
   - 小改动 → One-Pager

2. **撰写各 section**，引用来源:
   | PRD Section | 数据来源 |
   |-------------|---------|
   | Problem Statement | Phase 1 需求概要 |
   | Target Audience | Phase 1 需求概要 |
   | User Stories | Phase 1 需求概要 + `references/user_story_examples.md` |
   | Success Metrics | Phase 1 需求概要 + `references/metrics_frameworks.md` |
   | Competitive Landscape | Phase 2 竞品调研 |
   | 差异化定位 | Phase 2 竞品调研 |
   | Out of Scope | Phase 1 需求概要 |
   | Assumptions & Risks | Phase 1 需求概要 |

3. **User Stories 格式**: `作为 <角色>，我想要 <行为>，以便 <价值>` + Gherkin 验收标准

4. **保存**: `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-prd.md`

### 6.5 Phase 4 — Review & Iteration

1. **派发 prd-reviewer subagent** — 使用 `prd-reviewer-prompt.md`
2. **处理反馈**:
   - Critical → 立即修复 → 重新审查
   - Important → 本轮修复
   - Minor / Recommendations → 记录但不在本轮修复
   - 审查者有误 → 理性反驳，记录理由
3. **迭代循环**: reviewer 不通过 → 修复 → 重新审查，最多 3 轮
4. **Self-validation checklist**（从 `validate_prd.sh` 逻辑提炼，由主代理执行而非 shell 脚本）:
   - 所有必需 section 是否存在（Problem Statement, User Stories, Success Metrics, Scope）
   - User Stories 是否按标准格式 + 有验收标准
   - Success Metrics 是否有量化目标和基线
   - 是否有 placeholder/TBD/TODO/待定/后续补充 残留
   - Scope 是否明确区分 In/Out
   - 每个 Core Metric 是否配 Counter-metric
   - 里程碑是否有依赖关系

### 6.6 Phase 5 — Finalization

1. **用户审批** — 硬门控：PRD 未获用户审批前，不得调用 `system-architect` 或进入架构设计
2. **如需修改** → 返回 Phase 3 或 Phase 4
3. **定稿归档**:
   - PRD 状态标记为 `Approved`
   - 更新 Change Log
   - 归档到 `docs/superpowers-pro/projects/<project>/`

---

## 7. SKILL.md 结构大纲

重构后的 SKILL.md 将以参考实现的 SKILL.md 为骨架，融入我们的差异化内容：

```markdown
---
name: prd-generation
description: Generate comprehensive PRDs through a structured 5-phase workflow...
---

# PRD Generation — 五阶段产品需求文档生成

<HARD-GATE>
PRD 未获用户审批前，不得调用 system-architect 或进入架构设计阶段。
</HARD-GATE>

## PRD 要解决的 6 个核心问题
（保留现有内容）

## Core Workflow
### Phase 1: Requirements Gathering
→ 调用 brainstorming skill
### Phase 2: Competitive Research
→ 调用 competitive-researcher subagent
### Phase 3: PRD Draft
→ 参考 references/ 文档，合并 Phase 1+2 产出
### Phase 4: Review & Iteration
→ prd-reviewer subagent + self-validation checklist
### Phase 5: Finalization
→ 用户审批 + 定稿归档

## PRD 文档标准结构
（保留现有内容，与 references/prd_template.md 保持一致）

## PRD 格式选择
（新增：标准/Lean/One-Pager）

## 关键原则
（保留现有内容 + 新增 validation 相关原则）
```

---

## 8. 文件变更清单

| 操作 | 源路径 | 目标路径 | 说明 |
|------|--------|---------|------|
| 重写 | — | `skills/prd-generation/SKILL.md` | 以参考实现为主骨架重写 |
| 保留 | — | `skills/prd-generation/prd-reviewer-prompt.md` | 不变 |
| 保留 | — | `skills/prd-generation/competitive-researcher-prompt.md` | 不变 |
| 复制 | `reference/prd-generator/reference/prd_template.md` | `skills/prd-generation/references/prd_template.md` | 完整复制 |
| 复制 | `reference/prd-generator/reference/metrics_frameworks.md` | `skills/prd-generation/references/metrics_frameworks.md` | 完整复制 |
| 复制 | `reference/prd-generator/reference/user_story_examples.md` | `skills/prd-generation/references/user_story_examples.md` | 完整复制 |

---

## 9. Assumptions & Risks

| 假设 | 如果不成立的应对 | 验证方式 |
|------|----------------|-----------|
| brainstorming skill 能在 PRD 语境下工作 | brainstorming skill 设计为通用设计流程，PRD 语境是其自然子集 | 调用时传入 PRD 语境参数 |
| competitive-researcher subagent 能基于 Phase 1 产出做调研 | subagent prompt 已有清晰的输入参数定义 | 测试验证 |
| references 文档内容足够支撑 PRD 生成 | 参考实现已验证这些文档的实用性 | 使用后收集反馈 |

| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|---------|
| SKILL.md 过长 | 中 | 中 | Progressive Disclosure，主体流程简洁，详细内容放在 references/ |
| brainstorming 和竞品调研产出合并困难 | 低 | 中 | Phase 3 明确的映射表（section → 数据来源） |

---

## 10. Milestones

| 里程碑 | 交付范围 | 依赖 |
|--------|---------|------|
| M0: 文件复制 | references/ 三个文档复制完成 | 无 |
| M1: SKILL.md 重写 | 新 SKILL.md 产出 | M0 |
| M2: 验证 | 用新 skill 跑一次完整流程验证 | M1 |