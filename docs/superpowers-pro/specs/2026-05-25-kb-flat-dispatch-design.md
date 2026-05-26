---
date: 2026-05-25
status: approved
---

# kb 插件扁平调度重构设计

## 问题

当前 kb 执行流程完全串行：/kb 命令 → kb-agent → scan → extract-agent(串行5维度) → transform-agent(串行ingest) → load → serve。kb-agent 作为中间层代理阻塞了主会话的并行派发能力，且 Claude Code 子代理无法嵌套派发子代理，导致整个 ETL 管道无法利用并行化。

## 方案

采用方案 A'：/kb 命令直接编排 + 主会话层并行派发。删除 kb-agent，/kb 命令成为主编排器，直接用 Agent 工具并行派发维度级子代理。

## 架构

### 改动前

```
/kb 命令 → kb-agent → scan → extract-agent(串行5维度) → transform-agent(串行ingest) → load → serve
```

### 改动后

```
/kb 命令（主编排器，检查点驱动）
  Step 1/6  SCAN       □  内联 scan skill
  Step 2/6  EXTRACT    □  并行派发 5 个 extract 维度子代理
  Step 3/6  REVIEW_E   □  extract 结果审查（人类检查点）
  Step 4/6  TRANSFORM  □  并行派发 N 个 ingest 维度子代理 + 内联 cross-ref
  Step 5/6  LOAD       □  内联 build-search-index + build-graph
  Step 6/6  SERVE      □  内联 npm build + preview
```

## /kb 命令定义

```yaml
---
description: "知识库 ETL 管道 — 从代码扫描到站点交付，6 步显式编排，并行化提取与转换"
argument-hint: "[scan|extract|transform|load|serve]"
effort: high
---
```

### 子命令路由

| 子命令 | 执行步骤 |
|--------|----------|
| `/kb`（无参数） | Step 1-6 完整管道 |
| `/kb scan` | 仅 Step 1 |
| `/kb extract` | Step 1+2+3 |
| `/kb transform` | Step 4 |
| `/kb load` | Step 5 |
| `/kb serve` | Step 6 |

子命令执行时跳过无关步骤，用 SKIPPED(⊘) 标记，检查点协议不变。

## 检查点协议

参照 /feature 的检查点协议：

- 步骤状态: PENDING(□) → IN_PROGRESS(○) → DONE(✓) / SKIPPED(⊘)
- 完成时输出: `━━━ [✓] Step N/6: <NAME> — <一句话结果>` + `产出物: <文件路径或状态>`
- 跳过时输出: `━━━ [⊘] Step N/6: <NAME> — 用户跳过，原因: <原因>` + `产出物: <实际状态>`
- 开始前校验: `━━━ [→] Step N/6: <NAME> — 前置检查: Step N-1 <NAME> ✓`
- 前置缺失: `━━━ [✗] Step N/6: <NAME> — 阻塞: Step N-1 未完成` → 停止

## 人类检查点

Step 3 (REVIEW_E) — extract 完成后暂停，用户确认数据质量后再进入 transform。这是合理的，因为 extract 是最耗时的阶段，且 extract 结果质量直接影响后续 transform。

## 子代理设计

### extract 维度子代理

- **定义位置**: 保留 `agents/extract-agent.md`，重构为维度级模板
- **模型**: sonnet
- **工具**: Read, Glob, Grep, Bash, Skill, Write
- **派发方式**: /kb 命令用 Agent 工具并行派发 5 个子代理，每个子代理的 prompt 指定单一维度
- **执行流程**:
  1. 读取 `_map.md`
  2. 调用对应 extract-* skill（如 extract-topology）
  3. 写出 `_index.md` + `modules/*.md`
  4. 报告完成状态

### transform 维度子代理

- **定义位置**: 保留 `agents/transform-agent.md`，重构为维度级模板
- **模型**: sonnet
- **工具**: Read, Glob, Grep, Bash, Skill, Write, Edit
- **派发方式**: /kb 命令用 Agent 工具并行派发 N 个子代理，每个处理一个维度
- **执行流程**:
  1. 读取对应维度的 `_index.md` + `modules/*.md`
  2. 调用 ingest skill 处理该维度
  3. 写出 wiki 页面（entity/concept/synthesis）
  4. 更新 `_index.md` status 为 processed
  5. 报告完成状态

### cross-ref

不派发子代理，/kb 命令内联调用 cross-ref skill。原因：cross-ref 需要读取所有维度的 wiki 输出，必须等所有 ingest 完成，且无并行收益。

## 删除项

- **删除** `agents/kb-agent.md` — 调度逻辑提升到 /kb 命令
- **保留** `agents/extract-agent.md` — 作为维度子代理模板
- **保留** `agents/transform-agent.md` — 作为维度子代理模板
- **保留** 所有 skills 不变 — 子代理通过 Skill 工具调用

## 版本与变更记录

- plugin.json version: 0.4.0 → 0.5.0（minor：架构重构）
- CHANGELOG.md 新增 `[0.5.0]` 条目
