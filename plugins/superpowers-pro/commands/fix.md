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
  Step 3/8  ISOLATE       □  Worktree 隔离 + 基线验证
  Step 4/8  PLAN          □  拆解 bite-sized 任务
  Step 5/8  IMPLEMENT     □  TDD + 双重审查逐 task 执行
  Step 6/8  REVIEW        □  整体代码审查
  Step 7/8  VERIFY        □  验证门控 + 回归测试
  Step 8/8  FINISH        □  合并到初始分支 + 推送 + 清理

---

## Step 1/8: DIAGNOSE

调用 `superpowers-pro:systematic-debugging` skill 的 Phase 1-3（仅调查，不修复）。

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

## Step 3/8: ISOLATE

调用 `superpowers-pro:using-git-worktrees` skill。

- 检测现有隔离 → 创建 worktree → 安装依赖 → 验证基线测试通过

检查点: `━━━ [✓] Step 3/8: ISOLATE — Worktree 已创建，基线测试通过`
产出物: worktree 路径 + 分支名 + 基线测试通过

## Step 4/8: PLAN

调用 `superpowers-pro:writing-plans` skill。

- 将修复方案拆解为 bite-sized 任务（每步 2-5 分钟，TDD 取向）
- 无占位符
- 固定使用 subagent-driven-development
- 保存至 `docs/superpowers-pro/plans/YYYY-MM-DD-<fix-name>.md`

检查点: `━━━ [✓] Step 4/8: PLAN — 实施计划已产出`
产出物: `docs/superpowers-pro/plans/YYYY-MM-DD-<fix-name>.md`

## Step 5/8: IMPLEMENT

调用 `superpowers-pro:subagent-driven-development` skill。

每个 task 强制执行:
1. `superpowers-pro:test-driven-development` — RED → GREEN → REFACTOR
2. spec reviewer 子代理审查
3. code quality reviewer 子代理审查

**无子代理可用时: 报错停止。**

检查点: `━━━ [✓] Step 5/8: IMPLEMENT — 所有 task 完成`
产出物: 所有 task 标记完成 + 最终提交 SHA

## Step 6/8: REVIEW

调用 `superpowers-pro:requesting-code-review` skill。

- 派发 final code reviewer 子代理审查整体修复
- 自动处理反馈: Critical 立即修 → Important 继续前修 → Minor 记录 → 审查者有误反驳

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

1. 记录初始分支名（用户启动 /fix 时所在的分支）
2. 合并 worktree 分支到初始分支
3. 合并后运行测试验证 — 失败则自动回滚合并并报告
4. 推送初始分支到远端
5. 清理 worktree（provenance 校验）
6. 删除 fix impl 分支

检查点: `━━━ [✓] Step 8/8: FINISH — 已合并到 <初始分支> 并推送`
产出物: 合并结果 + 推送结果 + 清理结果
