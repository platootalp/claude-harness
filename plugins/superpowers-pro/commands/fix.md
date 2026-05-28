---
description: "Bug 修复完整流水线 — 从问题扫描到修复交付，8 步显式编排，防止步骤静默丢失"
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

  Step 1/8  DIAGNOSE      □  系统性问题扫描，产出 issue 文档
  Step 2/8  SPEC_REVIEW   □  issue 文档审批（唯一人类检查点）
  Step 3/8  ISOLATE       □  Worktree 隔离 + 基线验证
  Step 4/8  PLAN          □  拆解 bite-sized 任务
  Step 5/8  IMPLEMENT     □  TDD + 双重审查逐 task 执行
  Step 6/8  REVIEW        □  整体代码审查
  Step 7/8  VERIFY        □  验证门控 + 回归测试
  Step 8/8  FINISH        □  合并到初始分支 + 推送 + 清理

---

## Step 1/8: DIAGNOSE

调用 `superpowers-pro:issue-scanning` skill。

如果诊断发现此问题需要新设计（非简单 bug），停止并建议用户改用 `/feature`。

检查点: `━━━ [✓] Step 1/8: DIAGNOSE — 问题清单已产出`
产出物: `docs/superpowers-pro/issues/YYYY-MM-DD-<scope>-issues.md`

## Step 2/8: SPEC_REVIEW

**这是唯一的人类检查点。** 必须等待用户明确批准后才能继续。

- 展示 issue 文档内容
- 等待用户响应: 批准 / 要求修改 / 建议改用其他工作流
- 如果要求修改: 修改后重新展示，再次等待

检查点: `━━━ [✓] Step 2/8: SPEC_REVIEW — 用户已批准 issue 文档`
产出物: 用户审批确认（对话状态）

## Step 3/8: ISOLATE

调用 `superpowers-pro:using-git-worktrees` skill。

检查点: `━━━ [✓] Step 3/8: ISOLATE — Worktree 已创建，基线测试通过`
产出物: worktree 路径 + 分支名 + 基线测试通过

## Step 4/8: PLAN

调用 `superpowers-pro:writing-plans` skill。

保存至 `docs/superpowers-pro/plans/YYYY-MM-DD-<fix-name>.md`。

检查点: `━━━ [✓] Step 4/8: PLAN — 实施计划已产出`
产出物: `docs/superpowers-pro/plans/YYYY-MM-DD-<fix-name>.md`

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

检查点: `━━━ [✓] Step 6/8: REVIEW — 代码审查完成`
产出物: 审查报告 + 反馈处理结果

## Step 7/8: VERIFY

调用 `superpowers-pro:verification-before-completion` skill。

执行完整门控: IDENTIFY → RUN → READ → VERIFY → ONLY THEN

**额外验证（回归测试）:**
- 重读 issue 文档中的复现条件
- 确认原始症状已消失
- 确认修复未引入新问题

检查点: `━━━ [✓] Step 7/8: VERIFY — 验证通过，原始症状已消失`
产出物: 验证命令输出 + 回归测试通过

## Step 8/8: FINISH

调用 `superpowers-pro:finishing-a-development-branch` skill（finish-mode: auto）。

检查点: `━━━ [✓] Step 8/8: FINISH — 已合并到 <初始分支> 并推送`
产出物: 合并结果 + 推送结果 + 清理结果