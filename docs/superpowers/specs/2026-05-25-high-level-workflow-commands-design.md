# 高维度工作流 Commands 设计文档

> 日期：2026-05-25 | 状态：已确认

## 问题背景

superpowers-pro 现有 15 个 skill 通过调用链组成工作流，但所有步骤依赖 agent 自律，没有显式的步骤编排和检查点。分析发现以下步骤容易被静默丢失：

| 丢失步骤 | 严重度 | 原因 |
|---------|--------|------|
| 跳过 brainstorming 直接实现 | CRITICAL | agent 认为"太简单不需要设计" |
| 跳过 verification 门控 | CRITICAL | agent 凭信心声称完成，不运行验证 |
| 跳过 TDD | HIGH | "先写代码后补测试更快" |
| 跳过 spec/quality 双重审查 | HIGH | controller 自行决定不派发 reviewer |
| 跳过最终代码审查 | MEDIUM-HIGH | "task 级审查够了" |
| 跳过 worktree 隔离 | MEDIUM-HIGH | "我已在分支上" |
| 跳过分支收尾 | MEDIUM-HIGH | "直接 commit 就行" |
| 缺失版本/变更日志更新 | LOW-MEDIUM | 工作流中完全不存在此步骤 |

## 设计目标

用 4 条高维度 Command 替代分散的 skill 调用链，通过显式步骤编排和检查点机制防止静默丢失。

## 四条 Command 总览

| Command | 触发场景 | 入口阶段 | 人类检查点 | 步骤数 |
|---------|---------|---------|-----------|--------|
| `/feature` | 需要新设计的改动 | BRAINSTORM → spec | 1 个（SPEC_REVIEW） | 8 |
| `/fix` | Bug/故障 | DIAGNOSE → issue | 1 个（SPEC_REVIEW） | 8 |
| `/refactor` | 重构/优化/调整 | ASSESS → refactor | 1 个（SPEC_REVIEW） | 8 |
| `/init-system` | 0→1 新项目 | BRAINSTORM → PRD → ARCHITECT | 2 个（PRD_REVIEW + ARCH_REVIEW） | 7 |

**核心设计原则：**
- Command 是自动流水线，不是交互式向导
- 每步有检查点输出，下一步依赖上一步检查点
- 固定走 subagent-driven-development，不回退 executing-plans
- FINISH 默认合并到初始分支 + 推送远端，不推送需用户显式指令

---

## 检查点机制

### 步骤状态机

```
PENDING → IN_PROGRESS → DONE
                      → SKIPPED（用户显式跳过，记录原因）
```

| 状态 | 标记 | 含义 | 下一步能否继续 |
|------|------|------|---------------|
| PENDING | `□` | 未开始 | 不能 |
| IN_PROGRESS | `○` | 进行中 | 不能 |
| DONE | `✓` | 完成，有产出物 | 能 |
| SKIPPED | `⊘` | 用户跳过，记录了原因 | 能 |

### 检查点输出格式

**步骤完成时：**

```
━━━ [✓] Step 3/8: ISOLATE — Worktree created at .worktrees/feat-login
    产出物: .worktrees/feat-login (git worktree, branch: feat-login)
```

**步骤跳过时：**

```
━━━ [⊘] Step 3/8: ISOLATE — 用户跳过，原因: 已在独立分支上工作
    产出物: 当前分支 feat-login (非隔离 worktree)
```

**步骤开始前校验：**

```
━━━ [→] Step 4/8: IMPLEMENT — 前置检查: Step 3 ISOLATE ✓
```

**前置缺失时阻塞：**

```
━━━ [✗] Step 4/8: IMPLEMENT — 阻塞: Step 3 ISOLATE 未完成
    缺失: 未检测到 worktree 隔离环境
    操作: 请先完成 Step 3 或手动确认跳过原因
```

### 进度总览

Command 启动时输出完整步骤链：

```
▶ /feature 启动 — 功能开发工作流

  Step 1/8  BRAINSTORM    □
  Step 2/8  SPEC_REVIEW   □
  Step 3/8  PLAN          □
  Step 4/8  ISOLATE       □
  Step 5/8  IMPLEMENT     □
  Step 6/8  REVIEW        □
  Step 7/8  VERIFY        □
  Step 8/8  FINISH        □

━━━ [→] Step 1/8: BRAINSTORM — 开始
```

每步完成时更新对应行为 `✓` 或 `⊘`。

---

## `/feature` — 功能开发

### 步骤链

```
Step 1/8  BRAINSTORM    □  自动 — 探索需求，产出 spec 文档
Step 2/8  SPEC_REVIEW   □  等待人类 — spec 审批（唯一人类检查点）
Step 3/8  PLAN          □  自动 — 拆解 bite-sized 任务
Step 4/8  ISOLATE       □  自动 — Worktree 隔离 + 基线验证
Step 5/8  IMPLEMENT     □  自动 — TDD + 双重审查逐 task 执行
Step 6/8  REVIEW        □  自动 — 整体代码审查
Step 7/8  VERIFY        □  自动 — 验证门控
Step 8/8  FINISH        □  自动 — 合并到初始分支 + 推送 + 清理
```

### 各步骤详解

#### Step 1/8 BRAINSTORM

- 调用 `superpowers:brainstorming`
- 探索项目上下文、逐一提问、提出 2-3 方案、分节展示设计
- 产出：`docs/superpowers-pro/specs/YYYY-MM-DD-<topic>-design.md`

#### Step 2/8 SPEC_REVIEW

- 设计文档自审：占位符扫描、一致性检查、范围检查、歧义检查
- 展示文档内容，等待用户审批
- 用户可以：批准 / 要求修改 / 建议改用 `/fix` 或 `/refactor`
- 产出：用户审批确认（对话状态）

#### Step 3/8 PLAN

- 调用 `superpowers:writing-plans`
- 拆解为 bite-sized 任务，每步 2-5 分钟，TDD 取向
- 无占位符（TBD/TODO/"implement later" 均禁止）
- 固定使用 subagent-driven-development，不提供 executing-plans 选项
- 产出：`docs/superpowers-pro/plans/YYYY-MM-DD-<feature-name>.md`

#### Step 4/8 ISOLATE

- 调用 `superpowers:using-git-worktrees`
- 检测现有隔离 → 创建 worktree → 安装依赖 → 验证基线测试
- 产出：worktree 路径 + 分支名 + 基线测试通过

#### Step 5/8 IMPLEMENT

- 调用 `superpowers:subagent-driven-development`
- 每个 task 强制：
  - `superpowers:test-driven-development`（RED → GREEN → REFACTOR）
  - spec reviewer 子代理审查
  - code quality reviewer 子代理审查
  - 审查不通过 → implementer 修复 → 重新审查
- 无子代理可用时：报错停止，不回退到 executing-plans
- 产出：所有 task 标记完成 + 最终提交 SHA

#### Step 6/8 REVIEW

- 调用 `superpowers:requesting-code-review`
- 派发 final code reviewer 子代理审查整体实现
- 自动处理反馈：Critical/Important 自动修，Minor 记录，审查者有误自动反驳
- 产出：审查报告 + 反馈处理结果

#### Step 7/8 VERIFY

- 调用 `superpowers:verification-before-completion`
- 完整门控：IDENTIFY → RUN → READ → VERIFY → ONLY THEN
- 重读 spec 文档 + 计划，逐条检查需求覆盖率
- 产出：验证命令输出 + 需求覆盖率报告

**`/fix` VERIFY 额外验证：** 重读 issue 文档中的复现条件，确认原始症状消失（回归测试通过）

**`/refactor` VERIFY 额外验证：** 重读 refactor 文档中的行为不变性，逐条确认重构后行为未变

#### Step 8/8 FINISH

- 合并到初始分支（非 master，是用户启动 Command 时所在的分支）
- 合并后验证测试，失败则自动回滚并报告
- 推送初始分支到远端
- 清理 worktree（provenance 校验：仅清理 `.worktrees/`、`worktrees/`、`~/.config/superpowers/worktrees/` 下的）
- 删除 feature impl 分支
- 产出：合并结果 + 推送结果 + 清理结果

---

## `/fix` — Bug 修复

### 步骤链

```
Step 1/8  DIAGNOSE      □  自动 — 根因调查，产出 issue 文档
Step 2/8  SPEC_REVIEW   □  等待人类 — issue 文档审批
Step 3/8  PLAN          □  自动 — 拆解 bite-sized 任务
Step 4/8  ISOLATE       □  自动 — Worktree 隔离 + 基线验证
Step 5/8  IMPLEMENT     □  自动 — TDD + 双重审查逐 task 执行
Step 6/8  REVIEW        □  自动 — 整体代码审查
Step 7/8  VERIFY        □  自动 — 验证门控
Step 8/8  FINISH        □  自动 — 合并到初始分支 + 推送 + 清理
```

### Step 1/8 DIAGNOSE — 与 `/feature` 唯一差异点

- 调用 `superpowers:systematic-debugging` Phase 1-3（仅调查，不修复）
  - Phase 1：读错误信息、稳定复现、检查最近变更、追踪数据流
  - Phase 2：找正常样例、对比差异、理解依赖
  - Phase 3：单一假设、最小验证、单变量确认
- 产出：`docs/superpowers-pro/issues/YYYY-MM-DD-<issue-name>.md`

**Issue 文档模板：**

```markdown
# Issue: <标题>

## 根因
<根因描述>

## 影响范围
<受影响的文件/模块/用户场景>

## 复现条件
<复现步骤或触发条件>

## 修复假设
<基于根因的修复方向，可能多个>

## 风险
<修复可能引入的副作用>
```

### Step 2-8

与 `/feature` Step 2-8 完全一致。SPEC_REVIEW 审批的是 issue 文档而非 spec 文档，但行为相同。

---

## `/refactor` — 重构/优化

### 步骤链

```
Step 1/8  ASSESS        □  自动 — 评估重构目标，产出 refactor 文档
Step 2/8  SPEC_REVIEW   □  等待人类 — refactor 文档审批
Step 3/8  PLAN          □  自动 — 拆解 bite-sized 任务
Step 4/8  ISOLATE       □  自动 — Worktree 隔离 + 基线验证
Step 5/8  IMPLEMENT     □  自动 — TDD + 双重审查逐 task 执行
Step 6/8  REVIEW        □  自动 — 整体代码审查
Step 7/8  VERIFY        □  自动 — 验证门控
Step 8/8  FINISH        □  自动 — 合并到初始分支 + 推送 + 清理
```

### Step 1/8 ASSESS — 与 `/feature` 唯一差异点

- 分析当前代码结构，识别重构目标
- 不需要诊断根因（根因已知：代码结构差/性能差/可维护性差）
- 产出：`docs/superpowers-pro/refactors/YYYY-MM-DD-<refactor-name>.md`

**Refactor 文档模板：**

```markdown
# Refactor: <标题>

## 当前问题
<为什么要重构：性能、可维护性、可读性等>

## 重构目标
<重构后的目标状态>

## 行为不变性
<重构过程中必须保持不变的行为，作为验证基准>

## 风险点
<重构可能破坏的东西>

## 影响范围
<受影响的文件/模块>
```

### Step 2-8

与 `/feature` Step 2-8 完全一致。SPEC_REVIEW 审批的是 refactor 文档。

---

## `/init-system` — 系统初始化

### 步骤链

```
Step 1/7  BRAINSTORM    □  自动 — 探索项目需求，产出 PRD
Step 2/7  PRD_REVIEW    □  等待人类 — PRD 审批
Step 3/7  ARCHITECT     □  自动 — 四层架构设计 + ADR
Step 4/7  ARCH_REVIEW   □  等待人类 — 架构文档审批
Step 5/7  SKELETON      □  自动 — 创建项目骨架
Step 6/7  VERIFY        □  自动 — 验证项目可运行
Step 7/7  FINISH        □  自动 — 初始提交 + 推送
```

### 各步骤详解

#### Step 1/7 BRAINSTORM

- 调用 `superpowers:brainstorming`
- 探索项目愿景、目标用户、核心功能、技术约束
- 产出：`docs/superpowers-pro/prd/YYYY-MM-DD-<project>-prd.md`

#### Step 2/7 PRD_REVIEW

- 展示 PRD 内容，等待用户审批
- 用户可以：批准 / 要求修改 / 否决
- 产出：用户审批确认

#### Step 3/7 ARCHITECT

- 调用 `superpowers:system-architect`
- 确认 PRD 就绪（硬门控：无 PRD 不做架构）
- 四层架构设计：
  1. 应用架构（C4 图、服务边界、API 契约）
  2. 信息架构（领域模型、数据流、存储策略）
  3. 集成架构（外部接口、协议、故障隔离）
  4. 技术架构（技术栈、部署拓扑、安全、可观测性）
- 产出 ADR
- 产出：`docs/superpowers-pro/architecture/YYYY-MM-DD-<project>-architecture.md` + `docs/superpowers-pro/architecture/adr/` 下的 ADR 文件

#### Step 4/7 ARCH_REVIEW

- 展示架构文档内容，等待用户审批
- 产出：用户审批确认

#### Step 5/7 SKELETON

- 根据架构文档创建项目骨架：
  - 目录结构（按架构定义的模块/服务划分）
  - 配置文件（package.json / Cargo.toml / pyproject.toml 等）
  - 基础依赖安装
  - CI/CD 配置
  - README.md
  - .gitignore
- 不写业务代码，只搭骨架
- 产出：项目目录结构 + 依赖安装完成

#### Step 6/7 VERIFY

- 调用 `superpowers:verification-before-completion`
- 验证内容：
  - build 成功（exit 0）
  - lint 通过
  - 基础测试框架可运行
  - 目录结构符合架构文档定义
- 产出：验证命令输出 + 架构覆盖率确认

#### Step 7/7 FINISH

- 初始提交：

```bash
git init（如果尚未是 git 仓库）
git add .
git commit -m "init: project skeleton based on architecture design"
```

- 推送到远端（自动检测已有 origin，或需用户指定）
- 不做合并（0→1 项目，无分支合并概念）
- 产出：初始提交 SHA + 远端推送结果

---

## 四条 Command 对比

| 维度 | `/feature` | `/fix` | `/refactor` | `/init-system` |
|------|-----------|--------|-------------|----------------|
| 触发条件 | 需要新设计 | Bug/故障 | 重构/优化/调整 | 0→1 新项目 |
| Step 1 | BRAINSTORM | DIAGNOSE | ASSESS | BRAINSTORM |
| Step 1 产出 | spec 文档 | issue 文档 | refactor 文档 | PRD |
| 人类检查点 | 1 个 | 1 个 | 1 个 | 2 个 |
| 步骤数 | 8 | 8 | 8 | 7 |
| 是否 worktree | 是 | 是 | 是 | 否 |
| 是否 TDD 实施 | 是 | 是 | 是 | 否 |
| FINISH 行为 | 合并到初始分支 + 推送 | 同左 | 同左 | 初始提交 + 推送 |

### 边界冲突处理

| 场景 | 处理 |
|------|------|
| `/fix` DIAGNOSE 发现需要新设计 | 停止，建议 `/feature` |
| `/refactor` ASSESS 发现实际是 bug | 停止，建议 `/fix` |
| `/refactor` ASSESS 发现需要新设计 | 停止，建议 `/feature` |
| `/feature` BRAINSTORM 发现只是小修复 | 停止，建议 `/fix` 或 `/refactor` |

---

## 文档产出物路径

| 文档类型 | 路径 |
|---------|------|
| PRD | `docs/superpowers-pro/prd/` |
| 架构文档 | `docs/superpowers-pro/architecture/` |
| ADR | `docs/superpowers-pro/architecture/adr/` |
| Spec（功能设计） | `docs/superpowers-pro/specs/` |
| Issue 文档 | `docs/superpowers-pro/issues/` |
| Refactor 文档 | `docs/superpowers-pro/refactors/` |
| Plan（实施计划） | `docs/superpowers-pro/plans/` |

---

## 防静默丢失清单

| 原可丢失步骤 | Command 中的保障位置 |
|------------|---------------------|
| 跳过 brainstorming 直接实现 | Step 1 显式步骤，检查点链阻断 |
| 跳过 spec 自审 | Step 2 独立步骤 |
| 跳过 writing-plans | Step 3 显式步骤 |
| 跳过 worktree 隔离 | Step 4 显式步骤 |
| 跳过 TDD | Step 5 内强制（原为 "if task says to"） |
| 跳过 spec/quality 双重审查 | Step 5 内强制（原 controller 可选） |
| 跳过最终代码审查 | Step 6 独立步骤 |
| 跳过 verification 门控 | Step 7 独立步骤 |
| 跳过验证需求覆盖率 | Step 7 显式要求重读设计文档 |
| 跳过分支收尾 | Step 8 显式步骤 |
