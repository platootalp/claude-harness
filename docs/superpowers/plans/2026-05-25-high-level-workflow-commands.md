# 高维度工作流 Commands 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 4 条高维度 Command（/feature、/fix、/refactor、/init-system），通过显式步骤编排和检查点机制防止 agent 静默丢失工作流步骤。

**Architecture:** 每条 Command 是一个 .md 文件，放在 `plugins/superpowers-pro/commands/` 下。Command 文件内包含完整的步骤链定义、检查点协议、各步骤的具体指令（调用哪个 skill、产出什么、前置校验什么）。Command 不替代 skill，而是编排 skill。

**Tech Stack:** Claude Code plugin commands（.md frontmatter + markdown body）、现有 superpowers-pro skills

---

## File Structure

| 操作 | 文件 | 职责 |
|------|------|------|
| Create | `plugins/superpowers-pro/commands/feature.md` | /feature 功能开发工作流 |
| Create | `plugins/superpowers-pro/commands/fix.md` | /fix Bug 修复工作流 |
| Create | `plugins/superpowers-pro/commands/refactor.md` | /refactor 重构/优化工作流 |
| Create | `plugins/superpowers-pro/commands/init-system.md` | /init-system 系统初始化工作流 |
| Modify | `plugins/superpowers-pro/.claude-plugin/plugin.json` | 版本号 0.2.0 → 0.3.0（新增 4 commands = minor） |
| Modify | `plugins/superpowers-pro/CHANGELOG.md` | 添加 [Unreleased] 条目 |

---

### Task 1: 创建 /feature 命令

**Files:**
- Create: `plugins/superpowers-pro/commands/feature.md`

- [ ] **Step 1: 创建 feature.md 命令文件**

```markdown
---
description: "功能开发完整流水线 — 从需求构思到代码交付，8 步显式编排，防止步骤静默丢失"
argument-hint: "<feature-description>"
effort: high
---

# /feature — 功能开发工作流

你正在执行功能开发完整流水线。严格按照以下 8 步顺序执行，每步必须输出检查点，下一步开始前必须确认上一步检查点。

用户需求: $ARGUMENTS

## 检查点协议

- 步骤状态: PENDING(□) → IN_PROGRESS(○) → DONE(✓) / SKIPPED(⊘)
- 完成时输出: `━━━ [✓] Step N/8: <NAME> — <一句话结果>` + `    产出物: <文件路径或状态>`
- 跳过时输出: `━━━ [⊘] Step N/8: <NAME> — 用户跳过，原因: <原因>` + `    产出物: <实际状态>`
- 开始前校验: `━━━ [→] Step N/8: <NAME> — 前置检查: Step N-1 <NAME> ✓`
- 前置缺失: `━━━ [✗] Step N/8: <NAME> — 阻塞: Step N-1 未完成` → 停止

## 进度总览

▶ /feature 启动 — 功能开发工作流

  Step 1/8  BRAINSTORM    □  探索需求，产出 spec 文档
  Step 2/8  SPEC_REVIEW   □  spec 审批（唯一人类检查点）
  Step 3/8  PLAN          □  拆解 bite-sized 任务
  Step 4/8  ISOLATE       □  Worktree 隔离 + 基线验证
  Step 5/8  IMPLEMENT     □  TDD + 双重审查逐 task 执行
  Step 6/8  REVIEW        □  整体代码审查
  Step 7/8  VERIFY        □  验证门控
  Step 8/8  FINISH        □  合并到初始分支 + 推送 + 清理

---

## Step 1/8: BRAINSTORM

调用 `superpowers:brainstorming` skill。

- 探索项目上下文（文件、文档、最近提交）
- 逐一提问澄清需求（一次一问，偏好多选）
- 提出 2-3 种方案 + 权衡 + 推荐
- 分节展示设计，每节确认
- 写设计文档至 `docs/superpowers-pro/specs/YYYY-MM-DD-<topic>-design.md`
- 设计文档自审：占位符扫描、一致性检查、范围检查、歧义检查

如果发现此需求不需要新设计（只是 bug 修复或小调整），停止并建议用户改用 `/fix` 或 `/refactor`。

检查点: `━━━ [✓] Step 1/8: BRAINSTORM — 设计文档已产出`
产出物: `docs/superpowers-pro/specs/YYYY-MM-DD-<topic>-design.md`

## Step 2/8: SPEC_REVIEW

**这是唯一的人类检查点。** 必须等待用户明确批准后才能继续。

- 展示设计文档内容
- 等待用户响应: 批准 / 要求修改 / 建议改用其他工作流
- 如果要求修改: 修改后重新展示，再次等待
- 如果建议改用其他工作流: 停止当前流程，提示用户使用建议的工作流

检查点: `━━━ [✓] Step 2/8: SPEC_REVIEW — 用户已批准设计文档`
产出物: 用户审批确认（对话状态）

## Step 3/8: PLAN

调用 `superpowers:writing-plans` skill。

- 将设计拆解为 bite-sized 任务（每步 2-5 分钟，TDD 取向）
- 无占位符（TBD/TODO/"implement later" 均禁止）
- 固定使用 subagent-driven-development，不提供 executing-plans 选项
- 保存至 `docs/superpowers-pro/plans/YYYY-MM-DD-<feature-name>.md`
- 计划文档头部标注: `REQUIRED SUB-SKILL: superpowers:subagent-driven-development`

检查点: `━━━ [✓] Step 3/8: PLAN — 实施计划已产出`
产出物: `docs/superpowers-pro/plans/YYYY-MM-DD-<feature-name>.md`

## Step 4/8: ISOLATE

调用 `superpowers:using-git-worktrees` skill。

- 检测现有隔离（GIT_DIR vs GIT_COMMON）
- 优先使用原生 worktree 工具（EnterWorktree）
- 回退 git worktree（`.worktrees/` 目录）
- 安装项目依赖
- 验证基线测试通过

检查点: `━━━ [✓] Step 4/8: ISOLATE — Worktree 已创建，基线测试通过`
产出物: worktree 路径 + 分支名 + 基线测试通过

## Step 5/8: IMPLEMENT

调用 `superpowers:subagent-driven-development` skill。

每个 task 强制执行:
1. `superpowers:test-driven-development` — RED → GREEN → REFACTOR
2. spec reviewer 子代理审查 — 不通过则 implementer 修复后重新审查
3. code quality reviewer 子代理审查 — 不通过则 implementer 修复后重新审查

**无子代理可用时: 报错停止，不回退到 executing-plans。**

连续执行所有 task，不在 task 之间暂停问人。

检查点: `━━━ [✓] Step 5/8: IMPLEMENT — 所有 task 完成`
产出物: 所有 task 标记完成 + 最终提交 SHA

## Step 6/8: REVIEW

调用 `superpowers:requesting-code-review` skill。

- 派发 final code reviewer 子代理审查整体实现
- 自动处理反馈:
  - Critical → 立即修复
  - Important → 继续前修复
  - Minor → 记录后续
  - 审查者有误 → 理性反驳

检查点: `━━━ [✓] Step 6/8: REVIEW — 代码审查完成`
产出物: 审查报告 + 反馈处理结果

## Step 7/8: VERIFY

调用 `superpowers:verification-before-completion` skill。

执行完整门控:
1. IDENTIFY — 什么命令能证明完成?
2. RUN — 完整运行（当前、全新）
3. READ — 完整输出，检查退出码
4. VERIFY — 输出是否确认声明?
5. ONLY THEN — 做出声明

重读 spec 文档 + 计划，逐条检查需求覆盖率。未覆盖的 gap 必须记录。

检查点: `━━━ [✓] Step 7/8: VERIFY — 验证通过，需求覆盖率 N/M`
产出物: 验证命令输出 + 需求覆盖率报告

## Step 8/8: FINISH

1. 记录初始分支名（用户启动 /feature 时所在的分支）
2. 合并 worktree 分支到初始分支
3. 合并后运行测试验证 — 失败则自动回滚合并并报告
4. 推送初始分支到远端
5. 清理 worktree（仅清理 provenance 目录: `.worktrees/`、`worktrees/`、`~/.config/superpowers/worktrees/`）
6. 删除 feature impl 分支

检查点: `━━━ [✓] Step 8/8: FINISH — 已合并到 <初始分支> 并推送`
产出物: 合并结果 + 推送结果 + 清理结果
```

- [ ] **Step 2: 验证文件格式正确**

Run: `head -5 plugins/superpowers-pro/commands/feature.md`
Expected: frontmatter 以 `---` 开始，包含 `description` 字段

- [ ] **Step 3: 提交**

```bash
git add plugins/superpowers-pro/commands/feature.md
git commit -m "feat: add /feature command — full feature development pipeline"
```

---

### Task 2: 创建 /fix 命令

**Files:**
- Create: `plugins/superpowers-pro/commands/fix.md`

- [ ] **Step 1: 创建 fix.md 命令文件**

```markdown
---
description: "Bug 修复完整流水线 — 从根因诊断到修复交付，8 步显式编排，防止步骤静默丢失"
argument-hint: "<issue-description>"
effort: high
---

# /fix — Bug 修复工作流

你正在执行 Bug 修复完整流水线。严格按照以下 8 步顺序执行，每步必须输出检查点，下一步开始前必须确认上一步检查点。

问题描述: $ARGUMENTS

## 检查点协议

- 步骤状态: PENDING(□) → IN_PROGRESS(○) → DONE(✓) / SKIPPED(⊘)
- 完成时输出: `━━━ [✓] Step N/8: <NAME> — <一句话结果>` + `    产出物: <文件路径或状态>`
- 跳过时输出: `━━━ [⊘] Step N/8: <NAME> — 用户跳过，原因: <原因>` + `    产出物: <实际状态>`
- 开始前校验: `━━━ [→] Step N/8: <NAME> — 前置检查: Step N-1 <NAME> ✓`
- 前置缺失: `━━━ [✗] Step N/8: <NAME> — 阻塞: Step N-1 未完成` → 停止

## 进度总览

▶ /fix 启动 — Bug 修复工作流

  Step 1/8  DIAGNOSE      □  根因调查，产出 issue 文档
  Step 2/8  SPEC_REVIEW   □  issue 文档审批（唯一人类检查点）
  Step 3/8  PLAN          □  拆解 bite-sized 任务
  Step 4/8  ISOLATE       □  Worktree 隔离 + 基线验证
  Step 5/8  IMPLEMENT     □  TDD + 双重审查逐 task 执行
  Step 6/8  REVIEW        □  整体代码审查
  Step 7/8  VERIFY        □  验证门控 + 回归测试
  Step 8/8  FINISH        □  合并到初始分支 + 推送 + 清理

---

## Step 1/8: DIAGNOSE

调用 `superpowers:systematic-debugging` skill 的 Phase 1-3（仅调查，不修复）。

- Phase 1 — 根因调查:
  - 读错误信息
  - 稳定复现
  - 检查最近变更（git log, git diff）
  - 追踪数据流
  - **必须完成才能进入 Phase 2**

- Phase 2 — 模式分析:
  - 找正常样例
  - 对比差异
  - 理解依赖关系

- Phase 3 — 假设验证:
  - 形成单一假设
  - 最小化验证
  - 单变量确认

产出 issue 文档至 `docs/superpowers-pro/issues/YYYY-MM-DD-<issue-name>.md`，格式:

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

如果诊断发现此问题需要新设计（非简单 bug），停止并建议用户改用 `/feature`。

检查点: `━━━ [✓] Step 1/8: DIAGNOSE — 根因已定位，issue 文档已产出`
产出物: `docs/superpowers-pro/issues/YYYY-MM-DD-<issue-name>.md`

## Step 2/8: SPEC_REVIEW

**这是唯一的人类检查点。** 必须等待用户明确批准后才能继续。

- 展示 issue 文档内容
- 等待用户响应: 批准 / 要求修改 / 建议改用其他工作流
- 如果要求修改: 修改后重新展示，再次等待

检查点: `━━━ [✓] Step 2/8: SPEC_REVIEW — 用户已批准 issue 文档`
产出物: 用户审批确认（对话状态）

## Step 3/8: PLAN

调用 `superpowers:writing-plans` skill。

- 将修复方案拆解为 bite-sized 任务（每步 2-5 分钟，TDD 取向）
- 无占位符
- 固定使用 subagent-driven-development
- 保存至 `docs/superpowers-pro/plans/YYYY-MM-DD-<fix-name>.md`

检查点: `━━━ [✓] Step 3/8: PLAN — 实施计划已产出`
产出物: `docs/superpowers-pro/plans/YYYY-MM-DD-<fix-name>.md`

## Step 4/8: ISOLATE

调用 `superpowers:using-git-worktrees` skill。

- 检测现有隔离 → 创建 worktree → 安装依赖 → 验证基线测试通过

检查点: `━━━ [✓] Step 4/8: ISOLATE — Worktree 已创建，基线测试通过`
产出物: worktree 路径 + 分支名 + 基线测试通过

## Step 5/8: IMPLEMENT

调用 `superpowers:subagent-driven-development` skill。

每个 task 强制执行:
1. `superpowers:test-driven-development` — RED → GREEN → REFACTOR
2. spec reviewer 子代理审查
3. code quality reviewer 子代理审查

**无子代理可用时: 报错停止。**

检查点: `━━━ [✓] Step 5/8: IMPLEMENT — 所有 task 完成`
产出物: 所有 task 标记完成 + 最终提交 SHA

## Step 6/8: REVIEW

调用 `superpowers:requesting-code-review` skill。

- 派发 final code reviewer 子代理审查整体修复
- 自动处理反馈: Critical 立即修 → Important 继续前修 → Minor 记录 → 审查者有误反驳

检查点: `━━━ [✓] Step 6/8: REVIEW — 代码审查完成`
产出物: 审查报告 + 反馈处理结果

## Step 7/8: VERIFY

调用 `superpowers:verification-before-completion` skill。

执行完整门控: IDENTIFY → RUN → READ → VERIFY → ONLY THEN

**额外验证（回归测试）:**
- 重读 issue 文档中的复现条件
- 确认原始症状已消失
- 确认修复未引入新问题

检查点: `━━━ [✓] Step 7/8: VERIFY — 验证通过，原始症状已消失`
产出物: 验证命令输出 + 回归测试通过

## Step 8/8: FINISH

1. 记录初始分支名（用户启动 /fix 时所在的分支）
2. 合并 worktree 分支到初始分支
3. 合并后运行测试验证 — 失败则自动回滚合并并报告
4. 推送初始分支到远端
5. 清理 worktree（provenance 校验）
6. 删除 fix impl 分支

检查点: `━━━ [✓] Step 8/8: FINISH — 已合并到 <初始分支> 并推送`
产出物: 合并结果 + 推送结果 + 清理结果
```

- [ ] **Step 2: 验证文件格式正确**

Run: `head -5 plugins/superpowers-pro/commands/fix.md`
Expected: frontmatter 以 `---` 开始，包含 `description` 字段

- [ ] **Step 3: 提交**

```bash
git add plugins/superpowers-pro/commands/fix.md
git commit -m "feat: add /fix command — full bug fix pipeline"
```

---

### Task 3: 创建 /refactor 命令

**Files:**
- Create: `plugins/superpowers-pro/commands/refactor.md`

- [ ] **Step 1: 创建 refactor.md 命令文件**

```markdown
---
description: "重构/优化完整流水线 — 从目标评估到代码交付，8 步显式编排，防止步骤静默丢失"
argument-hint: "<refactor-target>"
effort: high
---

# /refactor — 重构/优化工作流

你正在执行重构/优化完整流水线。严格按照以下 8 步顺序执行，每步必须输出检查点，下一步开始前必须确认上一步检查点。

重构目标: $ARGUMENTS

## 检查点协议

- 步骤状态: PENDING(□) → IN_PROGRESS(○) → DONE(✓) / SKIPPED(⊘)
- 完成时输出: `━━━ [✓] Step N/8: <NAME> — <一句话结果>` + `    产出物: <文件路径或状态>`
- 跳过时输出: `━━━ [⊘] Step N/8: <NAME> — 用户跳过，原因: <原因>` + `    产出物: <实际状态>`
- 开始前校验: `━━━ [→] Step N/8: <NAME> — 前置检查: Step N-1 <NAME> ✓`
- 前置缺失: `━━━ [✗] Step N/8: <NAME> — 阻塞: Step N-1 未完成` → 停止

## 进度总览

▶ /refactor 启动 — 重构/优化工作流

  Step 1/8  ASSESS        □  评估重构目标，产出 refactor 文档
  Step 2/8  SPEC_REVIEW   □  refactor 文档审批（唯一人类检查点）
  Step 3/8  PLAN          □  拆解 bite-sized 任务
  Step 4/8  ISOLATE       □  Worktree 隔离 + 基线验证
  Step 5/8  IMPLEMENT     □  TDD + 双重审查逐 task 执行
  Step 6/8  REVIEW        □  整体代码审查
  Step 7/8  VERIFY        □  验证门控 + 行为不变性验证
  Step 8/8  FINISH        □  合并到初始分支 + 推送 + 清理

---

## Step 1/8: ASSESS

分析当前代码结构，识别重构目标。不需要诊断根因（根因已知: 代码结构差/性能差/可维护性差）。

- 阅读相关代码，理解当前结构
- 识别要重构的模块/函数/文件
- 确定重构后的目标状态
- 识别行为不变性（重构过程中必须保持不变的行为）
- 评估风险和影响范围

产出 refactor 文档至 `docs/superpowers-pro/refactors/YYYY-MM-DD-<refactor-name>.md`，格式:

```markdown
# Refactor: <标题>

## 当前问题
<为什么要重构: 性能、可维护性、可读性等>

## 重构目标
<重构后的目标状态>

## 行为不变性
<重构过程中必须保持不变的行为，作为验证基准>

## 风险点
<重构可能破坏的东西>

## 影响范围
<受影响的文件/模块>
```

如果评估发现此问题实际是 bug（有错误行为），停止并建议用户改用 `/fix`。
如果评估发现需要新设计，停止并建议用户改用 `/feature`。

检查点: `━━━ [✓] Step 1/8: ASSESS — 重构目标已评估，refactor 文档已产出`
产出物: `docs/superpowers-pro/refactors/YYYY-MM-DD-<refactor-name>.md`

## Step 2/8: SPEC_REVIEW

**这是唯一的人类检查点。** 必须等待用户明确批准后才能继续。

- 展示 refactor 文档内容
- 等待用户响应: 批准 / 要求修改 / 建议改用其他工作流
- 如果要求修改: 修改后重新展示，再次等待

检查点: `━━━ [✓] Step 2/8: SPEC_REVIEW — 用户已批准 refactor 文档`
产出物: 用户审批确认（对话状态）

## Step 3/8: PLAN

调用 `superpowers:writing-plans` skill。

- 将重构方案拆解为 bite-sized 任务（每步 2-5 分钟，TDD 取向）
- 无占位符
- 固定使用 subagent-driven-development
- 保存至 `docs/superpowers-pro/plans/YYYY-MM-DD-<refactor-name>.md`

检查点: `━━━ [✓] Step 3/8: PLAN — 实施计划已产出`
产出物: `docs/superpowers-pro/plans/YYYY-MM-DD-<refactor-name>.md`

## Step 4/8: ISOLATE

调用 `superpowers:using-git-worktrees` skill。

- 检测现有隔离 → 创建 worktree → 安装依赖 → 验证基线测试通过

检查点: `━━━ [✓] Step 4/8: ISOLATE — Worktree 已创建，基线测试通过`
产出物: worktree 路径 + 分支名 + 基线测试通过

## Step 5/8: IMPLEMENT

调用 `superpowers:subagent-driven-development` skill。

每个 task 强制执行:
1. `superpowers:test-driven-development` — RED → GREEN → REFACTOR
2. spec reviewer 子代理审查
3. code quality reviewer 子代理审查

**无子代理可用时: 报错停止。**

检查点: `━━━ [✓] Step 5/8: IMPLEMENT — 所有 task 完成`
产出物: 所有 task 标记完成 + 最终提交 SHA

## Step 6/8: REVIEW

调用 `superpowers:requesting-code-review` skill。

- 派发 final code reviewer 子代理审查整体重构
- 自动处理反馈: Critical 立即修 → Important 继续前修 → Minor 记录 → 审查者有误反驳

检查点: `━━━ [✓] Step 6/8: REVIEW — 代码审查完成`
产出物: 审查报告 + 反馈处理结果

## Step 7/8: VERIFY

调用 `superpowers:verification-before-completion` skill。

执行完整门控: IDENTIFY → RUN → READ → VERIFY → ONLY THEN

**额外验证（行为不变性）:**
- 重读 refactor 文档中的行为不变性
- 逐条确认重构后行为未变
- 运行完整测试套件确认无回归

检查点: `━━━ [✓] Step 7/8: VERIFY — 验证通过，行为不变性已确认`
产出物: 验证命令输出 + 行为不变性确认

## Step 8/8: FINISH

1. 记录初始分支名（用户启动 /refactor 时所在的分支）
2. 合并 worktree 分支到初始分支
3. 合并后运行测试验证 — 失败则自动回滚合并并报告
4. 推送初始分支到远端
5. 清理 worktree（provenance 校验）
6. 删除 refactor impl 分支

检查点: `━━━ [✓] Step 8/8: FINISH — 已合并到 <初始分支> 并推送`
产出物: 合并结果 + 推送结果 + 清理结果
```

- [ ] **Step 2: 验证文件格式正确**

Run: `head -5 plugins/superpowers-pro/commands/refactor.md`
Expected: frontmatter 以 `---` 开始，包含 `description` 字段

- [ ] **Step 3: 提交**

```bash
git add plugins/superpowers-pro/commands/refactor.md
git commit -m "feat: add /refactor command — full refactor/optimization pipeline"
```

---

### Task 4: 创建 /init-system 命令

**Files:**
- Create: `plugins/superpowers-pro/commands/init-system.md`

- [ ] **Step 1: 创建 init-system.md 命令文件**

```markdown
---
description: "系统初始化完整流水线 — 从 PRD 到架构设计到项目骨架，7 步显式编排"
argument-hint: "<project-name>"
effort: high
---

# /init-system — 系统初始化工作流

你正在执行系统初始化完整流水线。严格按照以下 7 步顺序执行，每步必须输出检查点，下一步开始前必须确认上一步检查点。

项目名称: $ARGUMENTS

## 检查点协议

- 步骤状态: PENDING(□) → IN_PROGRESS(○) → DONE(✓) / SKIPPED(⊘)
- 完成时输出: `━━━ [✓] Step N/7: <NAME> — <一句话结果>` + `    产出物: <文件路径或状态>`
- 跳过时输出: `━━━ [⊘] Step N/7: <NAME> — 用户跳过，原因: <原因>` + `    产出物: <实际状态>`
- 开始前校验: `━━━ [→] Step N/7: <NAME> — 前置检查: Step N-1 <NAME> ✓`
- 前置缺失: `━━━ [✗] Step N/7: <NAME> — 阻塞: Step N-1 未完成` → 停止

## 进度总览

▶ /init-system 启动 — 系统初始化工作流

  Step 1/7  BRAINSTORM    □  探索项目需求，产出 PRD
  Step 2/7  PRD_REVIEW    □  PRD 审批（人类检查点 1）
  Step 3/7  ARCHITECT     □  四层架构设计 + ADR
  Step 4/7  ARCH_REVIEW   □  架构文档审批（人类检查点 2）
  Step 5/7  SKELETON      □  创建项目骨架
  Step 6/7  VERIFY        □  验证项目可运行
  Step 7/7  FINISH        □  初始提交 + 推送

---

## Step 1/7: BRAINSTORM

调用 `superpowers:brainstorming` skill。

- 探索项目愿景、目标用户、核心功能、技术约束
- 逐一提问澄清需求（一次一问）
- 提出 2-3 种方案 + 权衡 + 推荐
- 产出 PRD 文档

检查点: `━━━ [✓] Step 1/7: BRAINSTORM — PRD 已产出`
产出物: `docs/superpowers-pro/prd/YYYY-MM-DD-<project>-prd.md`

## Step 2/7: PRD_REVIEW

**人类检查点 1。** 必须等待用户明确批准后才能继续。

- 展示 PRD 内容
- 等待用户响应: 批准 / 要求修改 / 否决
- 如果要求修改: 修改后重新展示，再次等待

检查点: `━━━ [✓] Step 2/7: PRD_REVIEW — 用户已批准 PRD`
产出物: 用户审批确认（对话状态）

## Step 3/7: ARCHITECT

调用 `superpowers:system-architect` skill。

- 确认 PRD 就绪（硬门控: 无 PRD 不做架构）
- 四层架构设计:
  1. 应用架构（C4 图: Context → Container → Component、服务边界、API 契约）
  2. 信息架构（领域模型、数据流、存储策略、一致性）
  3. 集成架构（外部接口、协议、同步策略、故障隔离）
  4. 技术架构（技术栈、部署拓扑、安全、可观测性）
- 产出 ADR（Architecture Decision Records）
- 架构文档自审: 覆盖率、一致性、可行性、风险识别

检查点: `━━━ [✓] Step 3/7: ARCHITECT — 架构设计完成`
产出物: `docs/superpowers-pro/architecture/YYYY-MM-DD-<project>-architecture.md` + `docs/superpowers-pro/architecture/adr/` 下的 ADR 文件

## Step 4/7: ARCH_REVIEW

**人类检查点 2。** 必须等待用户明确批准后才能继续。

- 展示架构文档内容
- 等待用户响应: 批准 / 要求修改 / 否决
- 如果要求修改: 修改后重新展示，再次等待

检查点: `━━━ [✓] Step 4/7: ARCH_REVIEW — 用户已批准架构文档`
产出物: 用户审批确认（对话状态）

## Step 5/7: SKELETON

根据架构文档创建项目骨架。不写业务代码，只搭骨架。

- 创建目录结构（按架构定义的模块/服务划分）
- 创建配置文件（package.json / Cargo.toml / pyproject.toml / go.mod 等，根据技术栈）
- 安装基础依赖
- 创建 CI/CD 配置（如 GitHub Actions）
- 创建 README.md
- 创建 .gitignore
- 创建基础测试框架配置

检查点: `━━━ [✓] Step 5/7: SKELETON — 项目骨架已创建`
产出物: 项目目录结构 + 依赖安装完成

## Step 6/7: VERIFY

调用 `superpowers:verification-before-completion` skill。

验证内容:
- build 成功（exit 0）
- lint 通过
- 基础测试框架可运行（哪怕 0 个测试）
- 目录结构符合架构文档定义

检查点: `━━━ [✓] Step 6/7: VERIFY — 项目可运行，架构覆盖率确认`
产出物: 验证命令输出 + 架构覆盖率确认

## Step 7/7: FINISH

1. 初始化 git 仓库（如果尚未是 git 仓库）:

```bash
git init
git add .
git commit -m "init: project skeleton based on architecture design"
```

2. 推送到远端:
   - 自动检测已有 origin → 推送
   - 无 origin → 询问用户远端地址后推送

3. 不做合并（0→1 项目，无分支合并概念）

检查点: `━━━ [✓] Step 7/7: FINISH — 初始提交完成并推送`
产出物: 初始提交 SHA + 远端推送结果
```

- [ ] **Step 2: 验证文件格式正确**

Run: `head -5 plugins/superpowers-pro/commands/init-system.md`
Expected: frontmatter 以 `---` 开始，包含 `description` 字段

- [ ] **Step 3: 提交**

```bash
git add plugins/superpowers-pro/commands/init-system.md
git commit -m "feat: add /init-system command — full system initialization pipeline"
```

---

### Task 5: 更新 plugin.json 版本号和 CHANGELOG

**Files:**
- Modify: `plugins/superpowers-pro/.claude-plugin/plugin.json`
- Modify: `plugins/superpowers-pro/CHANGELOG.md`

- [ ] **Step 1: 更新 plugin.json 版本号**

将 `"version": "0.2.0"` 改为 `"version": "0.3.0"`（新增 4 commands = minor bump）

- [ ] **Step 2: 更新 CHANGELOG.md**

在 `[Unreleased]` 段添加:

```markdown
### Added
- `/feature` command — 功能开发完整流水线（8 步显式编排）
- `/fix` command — Bug 修复完整流水线（8 步显式编排）
- `/refactor` command — 重构/优化完整流水线（8 步显式编排）
- `/init-system` command — 系统初始化完整流水线（7 步显式编排）
```

- [ ] **Step 3: 提交**

```bash
git add plugins/superpowers-pro/.claude-plugin/plugin.json plugins/superpowers-pro/CHANGELOG.md
git commit -m "chore: bump version to 0.3.0, update CHANGELOG for 4 new commands"
```
