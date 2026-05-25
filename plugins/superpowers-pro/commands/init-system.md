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
