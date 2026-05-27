# System Architect 重设计 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-pro:subagent-driven-development (recommended) or superpowers-pro:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 system-architect 技能从四维度结构重设计为 11 章结构，全深度可实现，新增 subagent 审查机制。

**Architecture:** 删除 4 个旧 reference 文件，合并为 1 个 architecture-guide.md；新增 2 个 subagent prompt；重写 SKILL.md 为 11 章流程；更新 depth-requirements/anti-patterns/review-checklist/adr-template。

**Tech Stack:** Markdown skill files，无代码依赖。

---

## File Structure

| 操作 | 文件 | 职责 |
|------|------|------|
| 重写 | `SKILL.md` | 主技能文件，11 章流程 + 全深度 + subagent |
| 新增 | `architecture-researcher-prompt.md` | 行业调研 subagent prompt |
| 新增 | `architecture-reviewer-prompt.md` | 架构审查 subagent prompt |
| 新增 | `references/architecture-guide.md` | 合并 4 个旧 reference + §3/§8 新内容 |
| 新增 | `references/anti-patterns.md` | 从 SKILL.md 拆出的 anti-pattern 检测清单 |
| 更新 | `references/depth-requirements.md` | 全深度要求 + 技术选型对比深度 |
| 更新 | `references/architecture-review-checklist.md` | 11 章审查 + anti-pattern 检查 |
| 更新 | `references/adr-template.md` | 章节引用 + 中文本地化 |
| 删除 | `references/application-architecture.md` | 并入 architecture-guide.md |
| 删除 | `references/information-architecture.md` | 并入 architecture-guide.md |
| 删除 | `references/integration-architecture.md` | 并入 architecture-guide.md |
| 删除 | `references/technical-architecture.md` | 并入 architecture-guide.md |
| 更新 | `.claude-plugin/plugin.json` | 版本 0.3.0 → 0.4.0 |
| 更新 | `CHANGELOG.md` | 记录变更 |

---

### Task 1: 创建 references/architecture-guide.md

**Files:**
- Create: `skills/system-architect/references/architecture-guide.md`

将 4 个旧 reference 的内容按 11 章结构重新组织，并新增 §3 技术选型和 §8 代码库工程结构的内容。

- [ ] **Step 1: 创建 architecture-guide.md**

文件内容按以下结构组织，每个章节提供模板和指引：

```
# Architecture Design Guide

## §3 技术选型与架构决策
  - 选型原则模板
  - 架构模式选型对比表（方案/优点/缺点/是否采用）
  - 核心技术选型对比表（能力/候选方案/选定/原因/风险）
  - AI 相关选型表（如适用）
  - 技术风险评估模板

## §4 总体架构设计
  - C4 Context Diagram 模板（来自 application-architecture.md）
  - C4 Container Diagram 模板（来自 application-architecture.md）
  - 架构原则模板
  - 核心链路设计指引（时序图 + 错误路径必须）

## §5 模块设计
  - 模块描述模板（职责/不做什么/核心能力/关键方法/伪代码/状态机）
  - 模块关系图
  - 模块拆分方法（来自 application-architecture.md 的 Service Boundary Decomposition）
  - 红旗信号

## §6 数据与存储设计
  - ER 图模板（来自 information-architecture.md）
  - 聚合边界分析
  - 存储选型矩阵（来自 information-architecture.md）
  - 数据 Schema 示例要求
  - 数据流转图
  - 数据一致性模式（来自 information-architecture.md）

## §7 接口与通信设计
  - API 规范模板（来自 application-architecture.md）
  - 事件契约模板
  - 协议选择框架（来自 integration-architecture.md）
  - 外部系统集成模板（来自 integration-architecture.md）
  - 故障隔离模式（熔断器、降级策略、错误映射链）（来自 integration-architecture.md）

## §8 代码库与工程结构设计
  - 仓库策略对比表（Monorepo vs Multi-repo）
  - DDD 单体目录结构模板
  - 微服务目录结构模板
  - 分层结构设计（controller/application/domain/infrastructure）
  - 禁止依赖规则
  - 模块依赖关系图
  - 工程规范清单

## §9 非功能设计
  - 可用性设计（多副本/熔断/限流/重试/灰度）
  - 性能设计（容量预估表/热路径分析/优化策略）
  - 安全设计（STRIDE 威胁模型 + 安全清单）（来自 technical-architecture.md）
  - 可观测性（三支柱/关键指标定义/告警策略）（来自 technical-architecture.md）

## §10 部署与运维设计
  - 环境划分
  - 部署拓扑模板（单体/应用+DB分离）（来自 technical-architecture.md）
  - CI/CD 模板
  - 配置管理

## §11 风险与架构演进
  - 风险登记模板
  - 常见风险类别
  - 架构演进路线模板（按指标规划，不是按时间）
  - 迁移计划模板（有现有系统时）
```

从旧文件提取内容时的映射：
- `application-architecture.md` → §4 C4 模板、§5 模块拆分、§7 API 规范
- `information-architecture.md` → §6 全部
- `integration-architecture.md` → §7 协议选择、外部集成、故障隔离
- `technical-architecture.md` → §9 安全/可观测性、§10 部署拓扑

§3 技术选型和 §8 代码库工程结构是新内容，参考 arch.md 讨论编写。

- [ ] **Step 2: Commit**

```bash
git add plugins/superpowers-pro/skills/system-architect/references/architecture-guide.md
git commit -m "feat(superpowers-pro): add consolidated architecture-guide.md for 11-chapter structure"
```

---

### Task 2: 创建 references/anti-patterns.md

**Files:**
- Create: `skills/system-architect/references/anti-patterns.md`

- [ ] **Step 1: 创建 anti-patterns.md**

包含 8 个 anti-pattern（来自 spec §3.4），每个有：症状、检测方法、修复方式、示例。末尾附检查清单表格。

8 个 anti-pattern：
1. 接口-only — 组件只有接口签名
2. Happy-path-only — 序列图只有成功流
3. 标签-only 组件 — 组件名无职责描述
4. 状态机无触发 — 状态转换无触发条件
5. 扩展点无示例 — "用策略模式" 无接口签名
6. Schema-less 数据 — "存为 JSON" 无字段
7. 质量标签化 — "高性能" 无具体设计
8. 缺少 Non-Goals — 无"不做的事"

每个 anti-pattern 的格式：

```markdown
## N. [名称]

**症状：** [什么表现]

**检测方法：** [怎么发现]

**修复：** [怎么修]

**示例：**
❌ [错误示例]
✅ [正确示例]
```

末尾检查清单：

```markdown
## Anti-Pattern 检查清单

| Anti-Pattern | 检查问题 | 通过标准 |
|-------------|---------|---------|
| 接口-only | 每个组件是否有算法或伪代码？ | 非平凡组件 100% 有 |
| Happy-path-only | 每个交互序列是否有错误路径？ | 每个序列 ≥1 错误路径 |
| 标签-only | 每个组件是否有职责描述？ | 100% 有 |
| 状态机无触发 | 每个状态转换是否有触发条件？ | 有状态组件 100% 有 |
| 扩展点无示例 | 每个扩展点是否有实现示例？ | 100% 有 |
| Schema-less | 每个持久化数据是否有 Schema？ | 100% 有 |
| 质量标签化 | 非功能设计是否有具体机制？ | 100% 有具体决策 |
| 缺少 Non-Goals | Non-Goals 是否存在且非空？ | 存在且 ≥3 条 |
```

- [ ] **Step 2: Commit**

```bash
git add plugins/superpowers-pro/skills/system-architect/references/anti-patterns.md
git commit -m "feat(superpowers-pro): add anti-patterns.md for architecture review"
```

---

### Task 3: 更新 references/depth-requirements.md

**Files:**
- Modify: `skills/system-architect/references/depth-requirements.md`

- [ ] **Step 1: 重写 depth-requirements.md**

保留现有的深浅对比示例（它们很好），做以下变更：

1. **删除风险驱动深度**：移除 🔴🟡🟢 三级深度、深度等级映射表
2. **改为全深度要求表**：直接列出每个元素类型必须达到的深度（来自 spec §3.2 的统一深度要求表）
3. **新增技术选型对比深度**：浅（"用 Kafka"）vs 深（对比表：候选/选定/原因/风险）
4. **删除 QAS 深度章节**：非功能设计直接写具体机制和量化目标，不需要 QAS 场景模板
5. **更新开头说明**：明确"架构文档就是详细设计文档，每个元素都必须全深度"

保留的现有内容：
- 组件/模块描述 深浅对比
- API 契约 深浅对比
- 状态机 深浅对比
- 数据 Schema 深浅对比
- 交互序列 深浅对比
- 扩展点 深浅对比
- 算法 深浅对比
- 错误映射链 深浅对比

新增的内容：
- 技术选型对比 深浅对比
- 统一深度要求表（来自 spec）

- [ ] **Step 2: Commit**

```bash
git add plugins/superpowers-pro/skills/system-architect/references/depth-requirements.md
git commit -m "feat(superpowers-pro): update depth-requirements to full-depth model, remove risk-driven levels"
```

---

### Task 4: 更新 references/architecture-review-checklist.md

**Files:**
- Modify: `skills/system-architect/references/architecture-review-checklist.md`

- [ ] **Step 1: 重写 review checklist**

从当前 5 节结构（Requirements Coverage / Cross-Dimension Consistency / Feasibility / Risk Identification / Completeness）改为按 11 章审查：

```
## 1. 章节完整性
  - §1-§6, §8-§9, §11 必须存在
  - §7 无外部依赖时可简化（注明原因）
  - §10 单进程时可简化（注明原因）
  - 每个章节的子节不是空标题

## 2. 需求覆盖
  - 追溯矩阵覆盖每个 PRD 需求
  - 每行映射到具体章节和设计元素

## 3. 可实现性
  - 每个组件有输入/输出类型 + 错误类型
  - 非平凡组件有算法/伪代码
  - 有状态组件有状态机
  - 扩展点有接口签名 + 实现示例 + 注册机制
  - 持久化数据有 Schema 示例
  - 集成点有错误映射链
  - 红旗信号列表

## 4. 跨章节一致性
  - §5 模块边界 vs §6 数据所有权
  - §4 API 契约 vs §7 通信协议
  - §3 技术选型 vs §4 架构
  - §8 代码库结构 vs §5 模块设计
  - ADR vs 设计不矛盾

## 5. 模式锚定
  - 每个主要设计选择引用业界模式
  - 业界模式引用准确

## 6. Anti-Pattern 检查
  - 引用 references/anti-patterns.md 的 8 项检查

## 7. 可行性
  - 团队经验、基础设施可用性、SLA、预算、时间线

## 8. 非功能设计具体性
  - 每个非功能维度有具体设计决策和量化目标
  - 无模糊标签

## 9. 技术选型
  - 架构模式有对比表
  - 核心技术有对比表
  - 技术风险评估存在

## 通过标准
  - Blocker 级：缺少必须章节、组件无法独立实现、需求覆盖有缺口
  - Major 级：anti-pattern 存在、一致性矛盾
  - Minor 级：措辞、示例补充
```

- [ ] **Step 2: Commit**

```bash
git add plugins/superpowers-pro/skills/system-architect/references/architecture-review-checklist.md
git commit -m "feat(superpowers-pro): rewrite review checklist for 11-chapter structure"
```

---

### Task 5: 更新 references/adr-template.md

**Files:**
- Modify: `skills/system-architect/references/adr-template.md`

- [ ] **Step 1: 更新 adr-template.md**

3 处修改：

1. **文件头部**加说明：ADR 在 §3.4 汇总引用，完整内容放附录 B
2. **示例 ADR** 翻译为中文（现有示例是英文，改为中文保持文档语言一致）
3. **Required ADRs** 更新为中文，增加章节引用：

```
## 必须的 ADR

1. **架构模式选型** — 单体 vs 微服务 vs 模块化单体（对应 §3.2）
2. **技术栈选型** — 主语言、框架及理由（对应 §3.3）
3. **数据存储选型** — 主数据库及理由（对应 §3.3）
4. **通信协议选型** — 服务/系统间通信方式（对应 §3.3）

非 CRUD 架构额外必须的 ADR：
5. **插件/Hook 架构** — 执行语义、隔离模型、扩展机制
6. **状态机设计** — 状态类型、转换触发、一致性模型
7. **事件驱动设计** — 事件总线语义、排序保证、错误传播
8. **内容验证策略** — 哈希算法、验证流程、恢复机制

ADR 在 §3.4 汇总引用，完整内容放在附录 B。
```

保留现有的 4 个 ADR 示例（PostgreSQL / Monolith-First / Hook Pipeline / BLAKE2b），翻译为中文。

- [ ] **Step 2: Commit**

```bash
git add plugins/superpowers-pro/skills/system-architect/references/adr-template.md
git commit -m "feat(superpowers-pro): update adr-template with Chinese examples and chapter references"
```

---

### Task 6: 创建 subagent prompt 文件

**Files:**
- Create: `skills/system-architect/architecture-researcher-prompt.md`
- Create: `skills/system-architect/architecture-reviewer-prompt.md`

- [ ] **Step 1: 创建 architecture-researcher-prompt.md**

内容要点：
- 角色：架构调研 subagent，只提供事实和模式，不做架构决策
- 输入：PRD 核心技术挑战
- 调研方法：对每个挑战研究 2-3 个现有系统，提取模式名称/核心数据结构/关键算法/适用性
- 输出格式：挑战分组 + 模式列表 + 调研总结表
- 深度规则：研究成果织入架构文档各章节，不产出独立文档
- 验证：每个 TOP 3 挑战至少 1 个业界模式

- [ ] **Step 2: 创建 architecture-reviewer-prompt.md**

内容要点：
- 角色：架构审查 subagent，不信任声明，逐行验证内容
- 审查维度：章节完整性、可实现性、错误路径、Anti-Patterns（引用 anti-patterns.md）、一致性、追溯性
- 输出格式：Status: Approved / Issues Found + Section/Problem/Severity/Suggested fix
- 严重等级：Blocker（必须修）/ Major（强烈建议修）/ Minor（可选）
- 循环规则：Issues Found → 主 agent 修复 → 重新派发，直到 Approved
- 验证清单：12 项快速检查（章节存在、Non-Goals、对比表、C4 图、错误路径、模块职责、Schema、状态机、非功能具体性、风险登记、追溯矩阵、无 Blocker anti-pattern）

- [ ] **Step 3: Commit**

```bash
git add plugins/superpowers-pro/skills/system-architect/architecture-researcher-prompt.md \
       plugins/superpowers-pro/skills/system-architect/architecture-reviewer-prompt.md
git commit -m "feat(superpowers-pro): add architecture researcher and reviewer subagent prompts"
```

---

### Task 7: 重写 SKILL.md

**Files:**
- Modify: `skills/system-architect/SKILL.md`

这是核心文件，需要完全重写。

- [ ] **Step 1: 重写 SKILL.md**

完整内容结构：

**Frontmatter:**
```yaml
---
name: system-architect
description: "Use when designing system architecture for a 0→1 project after PRD is validated — produces implementable architecture with tech selection comparisons, code structure design, algorithms, state machines, data schemas, and ADRs. Triggers on: design architecture, system architecture, architect from scratch, architecture design, 架构设计, 系统架构"
---
```

**正文结构：**

```
# System Architect

<HARD-GATE>
NO ARCHITECTURE WITHOUT A VALIDATED PRD.
</HARD-GATE>

## 职责边界
  - 6 行表格：技术选型/总体架构+模块/数据存储/接口通信/代码库工程/非功能设计 → 本技能
  - 功能架构/业务架构 → 产品（非本技能）

## Anti-Patterns 警告
  - 8 行表格（来自 anti-patterns.md 的摘要版）
  - 注明：详见 references/anti-patterns.md

## Checklist（9 步）
  1. 确认 PRD 就绪
  2. 上下文摄取（追溯矩阵）
  3. 行业调研（派发 researcher subagent）
  4. 解决方案策略（用户确认）
  5. 按章节设计（11 章顺序）
  6. 可实现性门控
  7. 写架构文档
  8. Architecture Reviewer 审查（循环）
  9. 用户审阅

## Process Flow（dot 图）

## Phase 1: PRD 确认与上下文摄取
  - Step 1: 确认 PRD 就绪
  - Step 2: 上下文摄取（提取需求、质量属性、追溯矩阵、澄清歧义）

## Phase 2: 调研与策略
  - Step 3: 行业调研（派发 architecture-researcher subagent）
  - Step 4: 解决方案策略（3-5 句总览，向用户确认）

## Phase 3: 架构设计
  - Step 5: 按章节设计
    - 设计顺序与依赖关系
    - 每章验证门
    - 全深度要求（引用 references/depth-requirements.md）
    - 章节简化规则（§7/§10）

## Phase 4: 验证与交付
  - Step 6: 可实现性门控（4 问）
  - Step 7: 写架构文档
  - Step 8: Architecture Reviewer 审查（派发 subagent，循环）
  - Step 9: 用户审阅

## 输出文档模板
  - 11 章 + 3 附录的完整 markdown 模板（来自 spec §6）

## 关键原则
  - PRD-first
  - 全深度可实现
  - 模式锚定
  - 可实现
  - 每章验证
  - 一次一问
  - Show, don't tell
  - YAGNI
  - 错误路径一等公民
  - 选型有据
```

关键变更点（vs 现有 SKILL.md）：
- 四维度（应用/信息/集成/技术架构）→ 11 章结构
- 12 步 → 9 步（移除风险评估步骤、合并信息/集成/技术架构步骤）
- 新增 Step 4 解决方案策略（用户确认点）
- 新增 subagent 派发（researcher Step 3、reviewer Step 8）
- 深度要求从"分维度"改为"全深度统一"
- 输出文档模板从 7 章（概述/应用/信息/集成/技术/ADR/风险）改为 11 章+3 附录
- 文档语言：全中文
- Anti-patterns 表格新增"质量标签化"和"缺少 Non-Goals"

- [ ] **Step 2: Commit**

```bash
git add plugins/superpowers-pro/skills/system-architect/SKILL.md
git commit -m "feat(superpowers-pro): rewrite system-architect SKILL.md with 11-chapter structure and full-depth model"
```

---

### Task 8: 删除旧 reference 文件

**Files:**
- Delete: `skills/system-architect/references/application-architecture.md`
- Delete: `skills/system-architect/references/information-architecture.md`
- Delete: `skills/system-architect/references/integration-architecture.md`
- Delete: `skills/system-architect/references/technical-architecture.md`

- [ ] **Step 1: 删除 4 个旧文件**

这些文件的内容已合并到 architecture-guide.md（Task 1），可以安全删除。

```bash
rm plugins/superpowers-pro/skills/system-architect/references/application-architecture.md \
   plugins/superpowers-pro/skills/system-architect/references/information-architecture.md \
   plugins/superpowers-pro/skills/system-architect/references/integration-architecture.md \
   plugins/superpowers-pro/skills/system-architect/references/technical-architecture.md
```

- [ ] **Step 2: 验证文件结构**

```bash
find plugins/superpowers-pro/skills/system-architect -type f | sort
```

预期输出：
```
SKILL.md
architecture-researcher-prompt.md
architecture-reviewer-prompt.md
references/adr-template.md
references/anti-patterns.md
references/architecture-guide.md
references/architecture-review-checklist.md
references/depth-requirements.md
```

- [ ] **Step 3: Commit**

```bash
git add -u plugins/superpowers-pro/skills/system-architect/references/
git commit -m "refactor(superpowers-pro): remove old reference files, consolidated into architecture-guide.md"
```

---

### Task 9: 更新 plugin.json 和 CHANGELOG.md

**Files:**
- Modify: `plugins/superpowers-pro/.claude-plugin/plugin.json`
- Modify: `plugins/superpowers-pro/CHANGELOG.md`

- [ ] **Step 1: 更新 plugin.json 版本**

将 `"version": "0.3.0"` 改为 `"version": "0.4.0"`

- [ ] **Step 2: 更新 CHANGELOG.md**

在 `[Unreleased]` 部分最前面添加：

```markdown
### Changed
- **system-architect: 重设计为 11 章结构** — 采用中文企业级架构文档结构（文档概述/业务背景/技术选型/总体架构/模块设计/数据存储/接口通信/代码库工程结构/非功能设计/部署运维/风险演进），替代原四维度结构；全深度可实现（每个组件要求算法+状态机+Schema+错误链）；新增 architecture-reviewer/researcher subagent prompt；4 个 reference 合并为 architecture-guide.md；新增 anti-patterns.md；更新 depth-requirements.md（全深度模型）、architecture-review-checklist.md（11 章审查）、adr-template.md（中文+章节引用）
```

- [ ] **Step 3: Commit**

```bash
git add plugins/superpowers-pro/.claude-plugin/plugin.json \
       plugins/superpowers-pro/CHANGELOG.md
git commit -m "chore(superpowers-pro): bump version to 0.4.0, update CHANGELOG"
```

---

## Self-Review

**1. Spec coverage:**

| Spec 章节 | Plan Task | 状态 |
|-----------|----------|------|
| §3.1 文档模板 11 章 | Task 7 (SKILL.md) | ✅ |
| §3.2 全深度可实现 | Task 3 (depth-requirements) + Task 7 | ✅ |
| §3.3 Subagent 审查 | Task 6 (subagent prompts) + Task 7 | ✅ |
| §3.4 Anti-Patterns | Task 2 (anti-patterns.md) + Task 4 (review checklist) | ✅ |
| §4 文件结构变更 | Task 1-8 全部 | ✅ |
| §5 流程详述 9 步 | Task 7 (SKILL.md) | ✅ |
| §6 输出文档模板 | Task 7 (SKILL.md) | ✅ |
| §7 与 prd-generation 衔接 | Task 7 (HARD-GATE 保留) | ✅ |
| §8 不做的事 | 已在 spec 中明确，plan 不实现这些 | ✅ |
| §9 成功指标 | Task 4 (review checklist 中体现) | ✅ |

**2. Placeholder scan:** 无 TBD/TODO/placeholder。

**3. Type consistency:** 所有 markdown 文件，无类型/函数签名一致性问题。
