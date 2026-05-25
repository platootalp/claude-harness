# superpowers-pro 插件工作流文档

> 版本：0.2.0 | 更新日期：2026-05-25

## 概述

superpowers-pro 插件包含 15 个 skill，覆盖从创意构思到代码交付的完整开发生命周期。这些 skill 通过明确的调用链组成 **5 条完整工作流**，每条工作流包含其全部分支路径和穿插的纪律门控。

---

## 工作流 1：功能开发（Feature Development）

从零到一构建新功能的主线流程，是插件最完整、使用频率最高的工作流。包含完整的构思→规划→隔离→执行（含 TDD + 审查）→验证→收尾链路。

### 完整调用链

```
using-superpowers
  → brainstorming
    → writing-plans
      → using-git-worktrees（创建隔离工作区）
        → subagent-driven-development（推荐路径）
          ├─ 每个 task：TDD（RED→GREEN→REFACTOR）
          ├─ 每个 task 后：spec review → code quality review
          ├─ 全部 task 完成后：requesting-code-review（整体审查）
          └─ verification-before-completion（凭证据声明完成）
            → finishing-a-development-branch
              ├─ 验证测试通过（verification-before-completion）
              └─ 选择：本地合并 / PR / 保留 / 丢弃
        ↘ executing-plans（备选路径，无子代理时）
          ├─ 每个 task：按计划逐步执行 + 验证
          └─ verification-before-completion
            → finishing-a-development-branch
```

### 分阶段详解

#### 阶段 0：会话入口 — using-superpowers

- **触发：** session-start hook 自动注入
- **职责：** 建立 skill 发现规则，任何响应前先检查是否有 skill 适用
- **规则：** 流程 skill 优先（brainstorming, debugging），实现 skill 其次

#### 阶段 1：构思 — brainstorming

| 步骤 | 动作 |
|------|------|
| 1 | 探索项目上下文（文件、文档、最近提交） |
| 2 | 如有视觉相关问题，单独消息提议 visual companion |
| 3 | 逐一提问澄清需求（偏好多选，一次一问） |
| 4 | 提出 2-3 种方案 + 权衡 + 推荐 |
| 5 | 分节展示设计，每节确认 |
| 6 | 写设计文档至 `docs/superpowers/specs/` |
| 7 | Spec 自审（占位符扫描、一致性、范围、歧义） |
| 8 | 用户审阅 spec |
| 9 | **唯一出口：** 调用 writing-plans |

**硬门控：** 不得跳过设计直接实现，不得调用 writing-plans 以外的实现 skill

#### 阶段 2：规划 — writing-plans

| 步骤 | 动作 |
|------|------|
| 1 | 范围检查（多子系统建议拆分） |
| 2 | 映射文件结构（哪些文件创建/修改，各自职责） |
| 3 | 拆分为 bite-sized 任务（每个 2-5 分钟，TDD 取向） |
| 4 | 无占位符（每步必须有实际内容、代码、命令） |
| 5 | 自审（spec 覆盖率、占位符、类型一致性） |
| 6 | 保存至 `docs/superpowers/plans/` |
| 7 | 选择执行方式：子代理驱动（推荐）或内联执行 |

**产出：** 计划文件头部标注 `REQUIRED SUB-SKILL` 指向 subagent-driven-development 或 executing-plans

#### 阶段 3：工作区隔离 — using-git-worktrees

执行前必须调用，确保变更在隔离环境中进行。

| 步骤 | 动作 |
|------|------|
| Step 0 | 检测现有隔离（GIT_DIR vs GIT_COMMON） |
| Step 1a | 优先使用原生 worktree 工具（EnterWorktree） |
| Step 1b | 回退 git worktree（`.worktrees/` 目录，验证 gitignore） |
| Step 3 | 自动检测并安装项目依赖 |
| Step 4 | 验证测试基线通过 |

#### 阶段 4a：子代理执行 — subagent-driven-development（推荐路径）

**核心循环（每个 task）：**

```
派发 implementer 子代理
  → 子代理内部遵循 TDD：RED → GREEN → REFACTOR
  → 子代理自审
  → 子代理提交
派发 spec reviewer 子代理
  → 不通过 → implementer 修复 → 重新 spec review
  → 通过 ↓
派发 code quality reviewer 子代理
  → 不通过 → implementer 修复 → 重新 quality review
  → 通过 ↓
标记 task 完成
```

**全部 task 完成后：**

1. 派发 final code reviewer 对整体实现审查（requesting-code-review）
2. 按 Critical/Important/Minor 处理反馈
3. verification-before-completion：运行完整验证命令，凭证据声明完成

**模型选择策略：**

| 任务类型 | 推荐模型 |
|---------|---------|
| 机械实现（1-2 文件、完整 spec） | 便宜/快速 |
| 集成与判断（多文件协调、模式匹配） | 标准 |
| 架构、设计、审查 | 最强 |

**子代理状态处理：**

| 状态 | 处理 |
|------|------|
| DONE | 进入 spec review |
| DONE_WITH_CONCERNS | 读顾虑，正确性/范围问题先处理，观察性备注记录后继续 |
| NEEDS_CONTEXT | 提供缺失上下文，重新派发 |
| BLOCKED | 上下文问题→补上下文；推理不足→换更强模型；任务过大→拆分；计划错误→上报人类 |

#### 阶段 4b：内联执行 — executing-plans（备选路径）

无子代理时的逐条执行模式：

| 步骤 | 动作 |
|------|------|
| Step 1 | 加载计划、批判性审查、有疑虑先提出 |
| Step 2 | 逐 task 执行：标记 in_progress → 按步骤执行 → 运行验证 → 标记 completed |
| Step 3 | 全部完成后调用 finishing-a-development-branch |

**阻塞时停止：** 缺依赖、测试失败、指令不清、验证反复失败 — 问人，不猜

#### 阶段 5：验证 — verification-before-completion

穿插于执行阶段多个节点，任何声称"完成/修复/通过"前必须通过门控：

```
1. IDENTIFY — 什么命令能证明此声明？
2. RUN — 完整运行（当前、全新）
3. READ — 完整输出，检查退出码，统计失败数
4. VERIFY — 输出是否确认声明？
   → 否：陈述实际状态 + 证据
   → 是：声明 + 证据
5. ONLY THEN — 才能做出声明
```

**铁律：** NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE

**适用节点：**
- 子代理报告 task 完成时
- 全部 task 完成后
- 修复 bug 后
- finishing-a-development-branch 验证测试时
- 准备 commit/PR 时

#### 阶段 6：代码审查 — requesting-code-review

在 subagent-driven-development 的两个层级触发：

**Task 级审查（每个 task）：** spec reviewer + code quality reviewer 子代理

**整体审查（全部 task 后）：** 派发 final code reviewer 子代理

1. 获取 git SHAs（base 与 head）
2. 派发 code-reviewer 子代理（使用 `code-reviewer.md` 模板）
3. 按严重级别处理反馈：
   - Critical → 立即修复
   - Important → 继续前修复
   - Minor → 记录后续
   - 审查者有误 → 理性反驳

#### 阶段 7：分支收尾 — finishing-a-development-branch

| 步骤 | 动作 |
|------|------|
| Step 1 | 验证测试通过（verification-before-completion）— 不通过则停止 |
| Step 2 | 检测环境（普通仓库 / worktree / detached HEAD） |
| Step 3 | 确定 base branch |
| Step 4 | 展示选项 |

**普通仓库 / named-branch worktree — 4 选项：**

| 选项 | 合并 | 推送 | 保留 Worktree | 删除分支 | 清理 Worktree |
|------|------|------|--------------|---------|--------------|
| 1. 本地合并 | yes | - | - | yes | yes |
| 2. 创建 PR | - | yes | yes | - | - |
| 3. 保留原样 | - | - | yes | - | - |
| 4. 丢弃 | - | - | - | yes (force) | yes |

**Detached HEAD — 3 选项：** 推送+PR / 保留 / 丢弃（需输入 "discard" 确认）

**Worktree 清理规则：** 仅清理 `.worktrees/`、`worktrees/`、`~/.config/superpowers/worktrees/` 下由 Superpowers 创建的 worktree

### 关键产出物

- `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` — 设计文档
- `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md` — 实施计划
- Git 分支 / PR

---

## 工作流 2：系统架构设计（System Architecture）

面向 0→1 项目，在 PRD 已验证后进行完整的四层架构设计，完成后接入功能开发工作流的规划阶段。

### 完整调用链

```
brainstorming（产出并验证 PRD）
  → system-architect
    ├─ 应用架构（C4 图）
    ├─ 信息架构
    ├─ 集成架构
    ├─ 技术架构
    ├─ ADR 决策记录
    └─ 审查与验证
  → writing-plans → （接入功能开发工作流阶段 3 起）
```

### 分阶段详解

#### 阶段 1：需求验证 — brainstorming

产出并验证 PRD，作为架构设计的硬门控输入。

#### 阶段 2：架构设计 — system-architect

| 步骤 | 动作 | 产出 |
|------|------|------|
| 1 | 确认 PRD 就绪 | 硬门控：无 PRD 不做架构 |
| 2 | 上下文摄取 | 解析 PRD，提取需求与质量属性 |
| 3 | 应用架构 | C4 图（Context → Container → Component）、服务边界、API 契约 |
| 4 | 信息架构 | 领域模型、数据流、存储策略、一致性 |
| 5 | 集成架构 | 外部接口、协议、同步策略、故障隔离 |
| 6 | 技术架构 | 技术栈、部署拓扑、安全、可观测性 |
| 7 | 决策记录 | ADR（使用 `references/adr-template.md`） |
| 8 | 审查与验证 | 覆盖率、一致性、可行性、风险识别 |
| 9 | 输出架构文档 → 用户审批 | |

**参考文件：** `references/application-architecture.md`、`references/information-architecture.md`、`references/integration-architecture.md`、`references/technical-architecture.md`、`references/adr-template.md`、`references/architecture-review-checklist.md`

#### 阶段 3：衔接开发

架构文档用户审批后，调用 writing-plans 进入功能开发工作流（从阶段 3 开始）。

### 关键产出物

- `docs/specs/YYYY-MM-DD-<project>-architecture.md` — 架构文档
- ADR（Architecture Decision Records）

---

## 工作流 3：系统化调试（Systematic Debugging）

遇到 bug 或测试失败时启动的严格调查-修复流程，禁止猜测式修复。

### 完整调用链

```
systematic-debugging
  ├─ Phase 1：根因调查（必须完成）
  ├─ Phase 2：模式分析
  ├─ Phase 3：假设验证
  └─ Phase 4：实施修复
       → test-driven-development（写失败测试 → 最小修复）
       → verification-before-completion（凭证据声明修复完成）
```

### 分阶段详解

| 阶段 | 动作 | 硬约束 |
|------|------|--------|
| Phase 1：根因调查 | 读错误信息、稳定复现、检查最近变更、追踪数据流 | **必须完成才能进入 Phase 2** |
| Phase 2：模式分析 | 找正常样例、对比差异、理解依赖 | |
| Phase 3：假设验证 | 单一假设、最小测试、单变量验证 | |
| Phase 4：实施修复 | TDD 写失败测试 → 实施最小修复 → verification-before-completion 验证 | 3 次修复失败 → 停止，上报人类 |

**TDD 在修复中的角色：** 先写一个能复现 bug 的失败测试（RED），然后实施最小修复使其通过（GREEN），确认不再回归（REFACTOR）。

**verification-before-completion 在修复中的角色：** 修复后必须运行完整验证命令，确认：(1) 原始症状消失，(2) 所有既有测试仍然通过，(3) 回归测试有效（revert fix → 失败 → restore → 通过）。

**辅助文件：** `root-cause-tracing.md`、`defense-in-depth.md`、`condition-based-waiting.md`

---

## 工作流 4：代码审查（Code Review）

覆盖审查请求与审查反馈两个方向的完整闭环，贯穿功能开发全过程，也可独立触发。

### 完整调用链

```
                    ┌─ requesting-code-review（发起审查）
开发完成 ───────────┤
                    └─ receiving-code-review（收到反馈后处理）
                         → verification-before-completion（修复后验证）
```

### requesting-code-review 流程

1. 获取 git SHAs（base 与 head）
2. 派发 code-reviewer 子代理（使用 `code-reviewer.md` 模板）
3. 按严重级别处理反馈：

| 级别 | 处理方式 |
|------|---------|
| Critical | 立即修复 |
| Important | 继续前修复 |
| Minor | 记录后续 |
| 审查者有误 | 理性反驳 |

4. 修复后 verification-before-completion 验证

### receiving-code-review 流程

1. **READ** — 完整阅读反馈，不急于反应
2. **UNDERSTAND** — 用自己的话复述要求（或提问澄清）
3. **VERIFY** — 对照代码库实际状态验证
4. **EVALUATE** — 技术上是否合理？
5. **RESPOND** — 技术性确认或理性反驳
6. **IMPLEMENT** — 逐条实施，每条测试
7. **verification-before-completion** — 验证修复正确

**核心原则：** 技术严谨，不表演性同意，不盲从实施。对模糊反馈必须停下发问。

**反驳条件：** 建议破坏功能 / 审查者缺上下文 / 违反 YAGNI / 与用户决策冲突

### 在功能开发中的嵌入位置

- **Task 级：** subagent-driven-development 中每个 task 后的 spec review + code quality review
- **整体级：** 全部 task 完成后的 final code review
- **PR 级：** finishing-a-development-branch 选择创建 PR 后

---

## 工作流 5：Skill 创作（Skill Authoring）

创建、编辑和验证新 skill 的元工作流，采用 TDD 思维应用于文档。

### 完整调用链

```
writing-skills
  ├─ RED：无 skill 基线测试 → 暴露问题
  ├─ GREEN：写最小 skill → 验证合规
  └─ REFACTOR：堵漏洞 → 反复测试至无懈可击
       → test-driven-development（RED→GREEN→REFACTOR 原则应用于 skill 文档）
       → verification-before-completion（验证 skill 确实改变了子代理行为）
```

### 分阶段详解

| 阶段 | 动作 | 目标 |
|------|------|------|
| RED | 无 skill 情况下对子代理跑压力场景，记录基线行为、辩解话术、违规行为 | 暴露 skill 要解决的问题 |
| GREEN | 写最小 skill 解决已识别的辩解话术，同场景重新测试，验证合规 | 让 skill 生效 |
| REFACTOR | 堵漏洞（新辩解、显式反驳、辩解表格、红旗列表），反复测试至无懈可击 | 让 skill 健壮 |

**TDD 在 skill 创作中的角色：** 与代码 TDD 同构 — RED 是没有 skill 时子代理的失败行为，GREEN 是最小 skill 使子代理通过，REFACTOR 是堵住新辩解路径。

**verification-before-completion 的角色：** 不靠"感觉"判断 skill 有效，而是对比有无 skill 时子代理的行为差异作为证据。

**辅助文件：** `testing-skills-with-subagents.md`、`persuasion-principles.md`、`anthropic-best-practices.md`、`graphviz-conventions.dot`、`render-graphs.js`

---

## Skill 调用关系全景图

```
                            ┌─────────────────────────┐
                            │    using-superpowers     │ ← session-start hook 自动注入
                            │    （元 skill / 入口）     │
                            └────────────┬────────────┘
                                         │ 发现 & 调用
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                     ▼
           ┌──────────────┐    ┌────────────────┐    ┌───────────────┐
           │ brainstorming │    │ systematic-    │    │ writing-      │
           │              │    │ debugging      │    │ skills        │
           └──────┬───────┘    └───────┬────────┘    └───────────────┘
                  │                    │
      ┌───────────┤                    │ TDD (Phase 4 修复)
      ▼           ▼                    ▼
┌───────────┐ ┌──────────────┐ ┌────────────────┐
│ system-   │ │ writing-     │ │ verification-  │ ← 所有工作流的完成节点
│ architect │ │ plans        │ │ before-        │
└─────┬─────┘ └──────┬───────┘ │ completion     │
      │              │         └────────────────┘
      │     ┌────────┴────────┐
      │     ▼                 ▼
      │ ┌─────────────────────────────┐    ┌──────────────────────┐
      │ │ using-git-worktrees         │    │ test-driven-         │
      │ │ （执行前创建隔离工作区）      │    │ development          │
      │ └─────────────────────────────┘    │ （执行中每个 task）    │
      │                                    └──────────────────────┘
      │     ┌─────────────────────────────┐
      │     │ subagent-driven-development │ ← 推荐
      │     │   ├─ implementer (TDD)      │
      │     │   ├─ spec reviewer          │
      │     │   └─ code quality reviewer  │
      │     ├─────────────────────────────┤
      │     │ executing-plans             │ ← 备选
      │     └─────────────────────────────┘
      │              │
      │     ┌────────┴────────────────────┐
      │     │ requesting-code-review      │ ← 整体审查 + PR 审查
      │     └────────┬────────────────────┘
      │              ▼
      │   ┌──────────────────────────────┐
      │   │ finishing-a-development-     │
      │   │ branch                       │
      │   └──────────────────────────────┘
      │
      ▼
 ┌────────────────────────┐
 │ receiving-code-review  │ ← 收到外部审查反馈时独立触发
 └────────────────────────┘

 ┌──────────────────────────┐
 │ dispatching-parallel-    │ ← 独立模式，任意工作流中
 │ agents                   │    有 2+ 独立任务时按需使用
 └──────────────────────────┘
```

---

## Skill 分类总览

| 类型 | Skill | 说明 |
|------|-------|------|
| **元 skill** | using-superpowers | 会话入口，skill 发现引擎 |
| **元 skill** | writing-skills | skill 创作的 TDD 方法论 |
| **流程 skill** | brainstorming | 创意构思，需求探索 |
| **流程 skill** | writing-plans | 设计 → 实施计划的桥梁 |
| **流程 skill** | executing-plans | 无子代理时的逐条执行模式 |
| **流程 skill** | subagent-driven-development | 子代理并行执行 + 双重审查 |
| **流程 skill** | finishing-a-development-branch | 开发分支收尾决策 |
| **流程 skill** | system-architect | 0→1 项目四层架构设计 |
| **纪律 skill** | test-driven-development | RED-GREEN-REFACTOR 铁律 |
| **纪律 skill** | verification-before-completion | 无证据不声明完成 |
| **纪律 skill** | receiving-code-review | 技术严谨，不盲从反馈 |
| **技术 skill** | systematic-debugging | 四阶段根因调查与修复 |
| **技术 skill** | using-git-worktrees | 工作区隔离 |
| **技术 skill** | requesting-code-review | 代码审查发起与反馈处理 |
| **模式 skill** | dispatching-parallel-agents | 并行独立任务派发模式 |

---

## Session-Start Hook

插件通过 `hooks/session-start` 在每次会话启动时自动注入 `using-superpowers` skill 内容：

1. 确定插件根目录
2. 检测遗留目录 `~/.config/superpowers/skills`，生成迁移警告
3. 读取 `using-superpowers/SKILL.md`
4. 包装为 `<EXTREMELY_IMPORTANT>` 块注入对话上下文
5. 按平台输出不同格式：Claude Code / Cursor / Copilot CLI

这使得每个会话的 agent 自动获得 skill 发现能力，无需用户手动操作。

---

## 工作流触发速查

| 用户意图 | 触发的工作流 | 入口 Skill |
|---------|-------------|-----------|
| "做一个新功能" | 功能开发 | brainstorming |
| "从零设计一个系统" | 系统架构设计 | brainstorming → system-architect |
| "这个 bug 怎么修" | 系统化调试 | systematic-debugging |
| "帮我 review 这段代码" | 代码审查 | requesting-code-review |
| "收到 review 反馈了" | 代码审查 | receiving-code-review |
| "写一个新 skill" | Skill 创作 | writing-skills |
| "执行这个计划" | 功能开发（执行阶段） | subagent-driven-development 或 executing-plans |
| "开发完了，怎么收尾" | 功能开发（收尾阶段） | finishing-a-development-branch |
| "这几个问题能并行处理吗" | 功能开发 / 调试中的并行派发 | dispatching-parallel-agents |
