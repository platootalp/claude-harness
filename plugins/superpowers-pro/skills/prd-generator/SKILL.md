---
name: prd-generator
description: "调研驱动的 PRD 生成 — 目标对齐→竞品调研→问题提取→二次澄清→方案扩展→MVP 收敛→PRD 撰写→验证审查。Use when users ask to create a PRD, write product requirements, document a feature, 需求文档, 产品需求, or need help structuring product specifications."
---

# PRD Generator — 调研驱动流程

从用户痛点出发，经过调研驱动和问题提取，产出标准项目初始化级 PRD。8 阶段流程确保 PRD 基于真实调研数据而非空想。

<HARD-GATE>
PRD 未获用户审批前，不得调用 system-architect 或进入架构设计阶段。
</HARD-GATE>

## Core Workflow

### Phase 0: 目标对齐

**目标:** 建立调研方向。不做深度分析，只够导航后续调研。

**执行:** 与用户简短对话（3-5 问），逐一提问：

1. 给谁用？（目标用户）
2. 最大痛点是什么？
3. MVP 还是长期平台？
4. 有无对标产品？（如有，确定调研对象）
5. 当前阶段？（想法 / 原型 / 已有产品迭代）

**产出:** 对话状态（无文件产出）

**原则:**
- 一次一问，不堆叠
- 如果用户已提供充分信息（如已有 brief），跳过已回答的问题
- 目的是"调研导航"，不是需求定义

---

### Phase 1: 竞品调研

**目标:** 基于 Phase 0 确定的方向，做三层竞品调研。

**执行:** 派发 competitive-researcher subagent，读取 `competitive-researcher-prompt.md` 获取 prompt。

**输入参数:**
- 竞品列表：用户提供，或基于 Phase 0 的领域信息推断 3-5 个主要竞品
- 领域：Phase 0 确定的产品领域
- 研究范围：基于项目规模确定
- 项目名称 + 日期

**三层调研结构:**

| 层级 | 关注点 | 产出 |
|------|--------|------|
| 产品层 | 用户是谁、核心流程、产品定位、解决什么问题 | 产品定位对比 |
| 业务层 | 权限模型、工作流、生命周期、审核机制、计费模式、协作模式 | 系统复杂度评估 |
| 技术层 | 是否多租户、是否插件化、Agent 编排方式、RAG 方案、事件驱动、工作流引擎、MCP/ACP、多模型支持 | 架构输入 |

**产出:** `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-competitive-analysis.md`

---

### Phase 2: 问题提取

**目标:** 从调研结果中抽象问题空间，区分行业共性痛点 vs 差异化机会。

**执行:** 主代理分析 Phase 1 产出的竞品调研报告，提取：

- **行业共性痛点** — 多竞品用户都在抱怨的问题（意味着必须对标）
- **竞品特有痛点** — 某竞品用户独有抱怨（意味着差异化机会）
- **问题抽象** — 从观察映射到本质问题

示例映射：

| 观察 | 本质问题 |
|------|---------|
| Dify 工作流复杂 | 普通用户不会编排 |
| Claude Code 上手强 | 上下文管理做得好 |
| Cursor 易失控 | Agent 缺少边界 |

**产出:** 写入调研报告 Section 2（用户痛点 + 差异化机会）

---

### Phase 3: 二次澄清

**目标:** 基于调研结果做专业级需求澄清。

**执行:** 逐一提问（一次一问），此时问题有深度：

- 不是"要不要知识库"，而是"偏 QA 检索，还是 Agent 长上下文记忆？"
- 不是"要不要工作流"，而是"流程是固定 SOP，还是动态推理规划？"

**澄清内容:**
- 修正方向
- 补充约束（技术、资源、时间）
- 收敛范围
- 确认优先级直觉

**产出:** 对话状态（无文件产出）

---

### Phase 4: 方案头脑风暴

**目标:** 在已知问题空间内扩展方案。

**执行:**
1. 提出 2-3 个产品方案
2. 每个方案列出权衡（优势/劣势/风险）
3. 给出推荐方案 + 推荐理由
4. 等待用户选择或调整

**原则:**
- 不是从零空想，是在 Phase 2 提取的问题基础上扩展
- 方案聚焦产品定位和功能边界，不涉及技术实现
- YAGNI：移除所有"以防万一"的功能

**产出:** 对话状态（用户确认的方案方向）

---

### Phase 5: MVP 收敛

**目标:** 将确认方案拆解为优先级梯队，明确边界。

**执行:**
1. 将方案拆解为 P0（必须有）/ P1（应该有）/ P2（可以有）
2. 明确 Out of Scope + 不做的原因 + 何时可能重新考虑
3. 等待用户确认 MVP 范围

**产出:** 对话状态（用户确认的 P0/P1/P2 + Out of Scope）

---

### Phase 6: PRD 撰写

**目标:** 合并 Phase 0-5 所有产出，撰写完整 PRD 文档。

**执行步骤:**

1. **选择 PRD 格式** — 根据项目规模决定：
   - **Standard PRD** — 新产品或重大功能（参考 `reference/prd_template.md`）
   - **Lean PRD** — 功能增强（Problem + Solution + Acceptance Criteria + Metrics）
   - **One-Pager** — 小改动（Problem + Solution + Success Metrics）

2. **生成 PRD 结构** — 使用 `reference/prd_template.md` 创建文档框架

3. **创建 User Stories** — 每个 P0/P1 功能生成 User Story：
   ```
   As a [user type],
   I want to [action],
   So that [benefit/value].

   Acceptance Criteria:
   - Given [context], when [action], then [expected outcome]
   ```
   参考 `reference/user_story_examples.md`

4. **定义 Success Metrics** — 选择合适的指标框架：
   - AARRR (Pirate Metrics) — 增长导向
   - HEART Framework — UX 质量导向
   - North Star Metric — 单一核心指标
   - OKRs — 目标与关键结果

   参考 `reference/metrics_frameworks.md`

5. **合并数据源:**

   | PRD Section | 数据来源 |
   |-------------|---------|
   | Problem Statement | Phase 0 目标对齐 + Phase 2 问题提取 |
   | Vision & Positioning | Phase 4 方案头脑风暴 + Phase 1 竞品调研 |
   | Target Audience & User Stories | Phase 0 + Phase 3 二次澄清 |
   | Functional Requirements | Phase 5 MVP 收敛 |
   | Success Metrics | Phase 3 + metrics_frameworks.md |
   | Competitive Landscape | Phase 1 竞品调研 |
   | Out of Scope | Phase 5 MVP 收敛 |
   | Assumptions & Risks | Phase 3 二次澄清 |

6. **保存 PRD** — `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-prd.md`

**产出:** 完整 PRD 文档

---

### Phase 7: 验证与审查

**目标:** 确保 PRD 完整、一致、可操作，获用户审批。

**执行步骤:**

1. **运行验证脚本:**

   ```bash
   scripts/validate_prd.sh <prd_file.md>
   ```

   检查：所有必需 section 存在、User Stories 格式正确、Success Metrics 已定义、Scope 明确、无 placeholder 残留

2. **派发 prd-reviewer subagent** — 读取 `prd-reviewer-prompt.md` 获取 prompt，传入 PRD 文件路径

3. **处理审查反馈:**
   - **Critical issues** → 立即修复 → 重新审查
   - **Important issues** → 本轮修复
   - **Minor / Recommendations** → 记录但不在本轮修复
   - **审查者有误** → 理性反驳，记录理由

4. **迭代循环:** reviewer 不通过 → 修复 → 重新审查，最多 3 轮

5. **3 轮仍未通过:** 展示未通过项给用户决定

6. **审查通过后:**
   - 展示完整 PRD 给用户
   - 等待用户明确批准
   - 批准 → PRD 状态标记为 Approved，完成定稿归档
   - 要求修改 → 返回 Phase 6 修改

**硬门控:** PRD 未获用户审批前，不得调用 system-architect 或进入架构设计阶段。

**产出:** 通过审查且获用户审批的 PRD 文档

---

## PRD 文档标准结构

参考 `reference/prd_template.md`。核心章节：

1. Problem Statement（问题陈述）
2. Goals & Objectives（目标与非目标）
3. User Personas（用户画像）
4. User Stories & Requirements（用户故事与功能需求）
5. Success Metrics（成功指标 + 反指标）
6. Scope（In Scope / Out of Scope）
7. Technical Considerations（技术考量）
8. Design & UX Requirements（设计与 UX 需求）
9. Timeline & Milestones（时间线与里程碑）
10. Risks & Mitigation（风险与缓解）
11. Dependencies & Assumptions（依赖与假设）
12. Open Questions（开放问题）

## 关键原则

- **调研前置** — 先有数据，再提问题，再写 PRD。不做无根据的头脑风暴
- **一次一问** — 不用多个问题轰炸用户
- **优先多选** — 比开放式问题更容易回答
- **YAGNI** — 从所有方案中移除非必要功能
- **探索替代方案** — 提出方案前总是给出 2-3 个选项
- **What ≠ How** — PRD 只描述用户价值和功能需求（What），严格不写实现方式（How）。架构决策属于 system-architect 的输出，不出现在 PRD 中
- **痛点从用户出发** — "竞品缺 X 功能" ≠ "用户在痛 X"。必须追问竞品功能缺失背后的真实用户痛点
- **验收标准可测试** — 使用 Gherkin 格式（Given/When/Then），或至少给出具体的测试条件和阈值条件
- **反指标不可省** — 每个 Core Metric 必须配至少一个 Counter-metric，防止优化一个指标时牺牲另一个
- **Out of Scope 显式声明** — 不做的功能和做的一样重要，必须列出原因和重新考虑的时机

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

## Resources

### reference/

- **prd_template.md** — Standard PRD template structure with detailed section templates
- **user_story_examples.md** — User story patterns and examples across different domains
- **metrics_frameworks.md** — Guide to PM metrics (AARRR, HEART, North Star, OKRs)

### script/

- **validate_prd.sh** — Validates PRD completeness and quality
- **generate_prd.sh** — Interactive PRD generation workflow

### Subagent Prompts

- **competitive-researcher-prompt.md** — Prompt for competitive research subagent
- **prd-reviewer-prompt.md** — Prompt for PRD document reviewer subagent
