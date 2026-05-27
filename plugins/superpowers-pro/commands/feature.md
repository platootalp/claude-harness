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
  Step 3/8  ISOLATE       □  Worktree 隔离 + 基线验证
  Step 4/8  PLAN          □  拆解 bite-sized 任务
  Step 5/8  IMPLEMENT     □  TDD + 双重审查逐 task 执行
  Step 6/8  REVIEW        □  整体代码审查
  Step 7/8  VERIFY        □  验证门控
  Step 8/8  FINISH        □  合并到初始分支 + 推送 + 清理

---

## Step 1/8: BRAINSTORM

调用 `superpowers-pro:brainstorming` skill。

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

## Step 3/8: ISOLATE

调用 `superpowers-pro:using-git-worktrees` skill。

- 检测现有隔离（GIT_DIR vs GIT_COMMON）
- 优先使用原生 worktree 工具（EnterWorktree）
- 回退 git worktree（`.worktrees/` 目录）
- 安装项目依赖
- 验证基线测试通过

检查点: `━━━ [✓] Step 3/8: ISOLATE — Worktree 已创建，基线测试通过`
产出物: worktree 路径 + 分支名 + 基线测试通过

## Step 4/8: PLAN

调用 `superpowers-pro:writing-plans` skill。

- 将设计拆解为 bite-sized 任务（每步 2-5 分钟，TDD 取向）
- 无占位符（TBD/TODO/"implement later" 均禁止）
- 固定使用 subagent-driven-development
- 保存至 `docs/superpowers-pro/plans/YYYY-MM-DD-<feature-name>.md`
- 计划文档头部标注: `REQUIRED SUB-SKILL: superpowers-pro:subagent-driven-development`

检查点: `━━━ [✓] Step 4/8: PLAN — 实施计划已产出`
产出物: `docs/superpowers-pro/plans/YYYY-MM-DD-<feature-name>.md`

## Step 5/8: IMPLEMENT

调用 `superpowers-pro:subagent-driven-development` skill。

每个 task 强制执行:
1. `superpowers-pro:test-driven-development` — RED → GREEN → REFACTOR
2. spec reviewer 子代理审查 — 不通过则 implementer 修复后重新审查
3. code quality reviewer 子代理审查 — 不通过则 implementer 修复后重新审查

**无子代理可用时: 报错停止。**

连续执行所有 task，不在 task 之间暂停问人。

检查点: `━━━ [✓] Step 5/8: IMPLEMENT — 所有 task 完成`
产出物: 所有 task 标记完成 + 最终提交 SHA

## Step 6/8: REVIEW

调用 `superpowers-pro:requesting-code-review` skill。

- 派发 final code reviewer 子代理审查整体实现
- 自动处理反馈:
  - Critical → 立即修复
  - Important → 继续前修复
  - Minor → 记录后续
  - 审查者有误 → 理性反驳

检查点: `━━━ [✓] Step 6/8: REVIEW — 代码审查完成`
产出物: 审查报告 + 反馈处理结果

## Step 7/8: VERIFY

调用 `superpowers-pro:verification-before-completion` skill。

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
5. 清理 worktree（仅清理 provenance 目录: `.worktrees/`、`worktrees/`、`~/.config/superpowers-pro/worktrees/`）
6. 删除 feature impl 分支

检查点: `━━━ [✓] Step 8/8: FINISH — 已合并到 <初始分支> 并推送`
产出物: 合并结果 + 推送结果 + 清理结果
