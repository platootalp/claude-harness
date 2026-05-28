---
description: "系统初始化完整流水线 — 从 PRD 到架构设计到路线图到项目骨架，8 步显式编排"
argument-hint: "<project-name>"
effort: high
---

# /init-system — 系统初始化工作流

你正在执行系统初始化完整流水线。严格按照以下 8 步顺序执行，每步必须输出检查点，下一步开始前必须确认上一步检查点。

项目名称: $ARGUMENTS

## 检查点协议

- 步骤状态: PENDING(□) → IN_PROGRESS(○) → DONE(✓) / SKIPPED(⊘)
- 完成时输出: `━━━ [✓] Step N/8: <NAME> — <一句话结果>` + `    产出物: <文件路径或状态>`
- 跳过时输出: `━━━ [⊘] Step N/8: <NAME> — 用户跳过，原因: <原因>` + `    产出物: <实际状态>`
- 开始前校验: `━━━ [→] Step N/8: <NAME> — 前置检查: Step N-1 <NAME> ✓`
- 前置缺失: `━━━ [✗] Step N/8: <NAME> — 阻塞: Step N-1 未完成` → 停止

## 进度总览

▶ /init-system 启动 — 系统初始化工作流

  Step 1/8  PRD           □  产品需求文档（头脑风暴或竞品对标）
  Step 2/8  PRD_REVIEW    □  PRD 审批（人类检查点 1）
  Step 3/8  ARCHITECT     □  四层架构设计 + ADR
  Step 4/8  ARCH_REVIEW   □  架构文档审批（人类检查点 2）
  Step 5/8  SKELETON      □  创建项目骨架
  Step 6/8  ROADMAP       □  项目路线图（里程碑、功能点、迭代路径）
  Step 7/8  VERIFY        □  验证项目可运行
  Step 8/8  FINISH        □  初始提交 + 推送

---

## Step 1/8: PRD

调用 `superpowers-pro:prd-generation` skill。

检查点: `━━━ [✓] Step 1/8: PRD — PRD 已产出`
产出物: `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-prd.md`

## Step 2/8: PRD_REVIEW

**人类检查点 1。** 必须等待用户明确批准后才能继续。

- 展示 PRD 内容
- 等待用户响应: 批准 / 要求修改 / 否决
- 如果要求修改: 修改后重新展示，再次等待

检查点: `━━━ [✓] Step 2/8: PRD_REVIEW — 用户已批准 PRD`
产出物: 用户审批确认（对话状态）

## Step 3/8: ARCHITECT

调用 `superpowers-pro:system-architect` skill。

确认 PRD 就绪（硬门控: 无 PRD 不做架构）。

检查点: `━━━ [✓] Step 3/8: ARCHITECT — 架构设计完成`
产出物: `docs/superpowers-pro/projects/<project>/YYYY-MM-DD-<project>-architecture.md` + `docs/superpowers-pro/projects/<project>/adr/` 下的 ADR 文件

## Step 4/8: ARCH_REVIEW

**人类检查点 2。** 必须等待用户明确批准后才能继续。

- 展示架构文档内容
- 等待用户响应: 批准 / 要求修改 / 否决
- 如果要求修改: 修改后重新展示，再次等待

检查点: `━━━ [✓] Step 4/8: ARCH_REVIEW — 用户已批准架构文档`
产出物: 用户审批确认（对话状态）

## Step 5/8: SKELETON

根据架构文档创建项目骨架。不写业务代码，只搭骨架。

- 创建目录结构（按架构定义的模块/服务划分）
- 创建配置文件（package.json / Cargo.toml / pyproject.toml / go.mod 等，根据技术栈）
- 安装基础依赖
- 创建 CI/CD 配置（如 GitHub Actions）
- 创建 README.md
- 创建 .gitignore
- 创建基础测试框架配置

检查点: `━━━ [✓] Step 5/8: SKELETON — 项目骨架已创建`
产出物: 项目目录结构 + 依赖安装完成

## Step 6/8: ROADMAP

基于已审批的 PRD 和架构文档制定项目路线图。

- 从 PRD 提取功能列表及优先级（P0/P1/P2）
- 从架构文档提取模块依赖关系
- 基于优先级 + 依赖关系编排里程碑
- 生成路线图文档

路线图文档结构:

```markdown
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

## Step 7/8: VERIFY

调用 `superpowers-pro:verification-before-completion` skill。

验证内容:
- build 成功（exit 0）
- lint 通过
- 基础测试框架可运行（哪怕 0 个测试）
- 目录结构符合架构文档定义

检查点: `━━━ [✓] Step 7/8: VERIFY — 项目可运行，架构覆盖率确认`
产出物: 验证命令输出 + 架构覆盖率确认

## Step 8/8: FINISH

调用 `superpowers-pro:finishing-a-development-branch` skill（finish-mode: auto）。

检查点: `━━━ [✓] Step 8/8: FINISH — 初始提交完成并推送`
产出物: 初始提交 SHA + 远端推送结果