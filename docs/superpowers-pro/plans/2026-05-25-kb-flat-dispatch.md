# kb 扁平调度重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 kb 插件从串行 kb-agent 调度重构为 /kb 命令直接编排 + 主会话层并行派发维度子代理。

**Architecture:** 删除 kb-agent，/kb 命令成为主编排器，采用检查点驱动 6 步管道。extract 和 transform 阶段用 Agent 工具并行派发维度级子代理，scan/cross-ref/load/serve 内联执行。保留 extract-agent 和 transform-agent 作为子代理模板定义。

**Tech Stack:** Claude Code plugin system (markdown agents/commands/skills)

---

## File Structure

| Action | File | Responsibility |
|--------|------|---------------|
| Rewrite | `plugins/kb/commands/kb.md` | 主编排器，6 步检查点管道 + 子命令路由 + 并行派发逻辑 |
| Delete | `plugins/kb/agents/kb-agent.md` | 不再需要中间层代理 |
| Rewrite | `plugins/kb/agents/extract-agent.md` | 维度级子代理模板（单维度 extract） |
| Rewrite | `plugins/kb/agents/transform-agent.md` | 维度级子代理模板（单维度 ingest） |
| Modify | `plugins/kb/.claude-plugin/plugin.json` | version 0.1.0 → 0.5.0 |
| Modify | `plugins/kb/CHANGELOG.md` | 新增 [0.5.0] 条目 |

---

### Task 1: 删除 kb-agent

**Files:**
- Delete: `plugins/kb/agents/kb-agent.md`

- [ ] **Step 1: 删除 kb-agent.md**

```bash
rm plugins/kb/agents/kb-agent.md
```

- [ ] **Step 2: 确认文件已删除**

```bash
ls plugins/kb/agents/
```

Expected: 仅剩 `extract-agent.md` 和 `transform-agent.md`

- [ ] **Step 3: Commit**

```bash
git add -u plugins/kb/agents/kb-agent.md
git commit -m "refactor(kb): remove kb-agent — dispatch logic moves to /kb command"
```

---

### Task 2: 重写 extract-agent 为维度级子代理模板

**Files:**
- Rewrite: `plugins/kb/agents/extract-agent.md`

- [ ] **Step 1: 写入新的 extract-agent.md**

新定义从"多维度并行调度器"变为"单维度提取执行器"。/kb 命令会为每个维度（topology/api/data-model/flows/concepts）派发一个此类型的子代理，每个子代理只处理一个维度。

```markdown
---
name: extract-agent
model: sonnet
tools: Read, Glob, Grep, Bash, Skill, Write
---

# Extract Agent — 单维度提取

执行指定维度的知识提取，产出 raw 文档。

## 输入参数

- `--project`: 项目名称（必需）
- `--dimension`: 提取维度（必需），取值: topology | api | data-model | flows | concepts

## 执行流程

1. 读取 `data/raw/<project>/_map.md`（硬前置：必须存在）
2. 根据 dimension 参数调用对应技能：
   - topology → `extract-topology`
   - api → `extract-api`
   - data-model → `extract-data-model`
   - flows → `extract-flows`
   - concepts → `extract-concepts`
3. 验证产出：确认 `data/raw/<project>/<dimension>/_index.md` 存在且 `modules/` 目录非空
4. 报告结果

## 报告格式

```
维度: <dimension>
状态: DONE | DONE_WITH_CONCERNS | BLOCKED
产出: _index.md + N 个 module 文件
问题: <如有>
```
```

- [ ] **Step 2: Commit**

```bash
git add plugins/kb/agents/extract-agent.md
git commit -m "refactor(kb): rewrite extract-agent as single-dimension subagent template"
```

---

### Task 3: 重写 transform-agent 为维度级子代理模板

**Files:**
- Rewrite: `plugins/kb/agents/transform-agent.md`

- [ ] **Step 1: 写入新的 transform-agent.md**

新定义从"批量转化+cross-ref"变为"单维度 ingest 执行器"。cross-ref 由 /kb 命令内联执行，不再由 transform-agent 负责。

```markdown
---
name: transform-agent
model: sonnet
tools: Read, Glob, Grep, Bash, Skill, Write, Edit
---

# Transform Agent — 单维度转化

执行指定维度的 ingest 转化，将 raw 文档转为 wiki 页面。

## 输入参数

- `--project`: 项目名称（必需）
- `--dimension`: 转化维度（必需），对应 raw 目录下的维度名

## 执行流程

1. 读取 `data/raw/<project>/<dimension>/_index.md`，确认 `status: unprocessed`
2. 调用 `ingest` 技能处理该维度
3. 写出 wiki 页面（entity/concept/synthesis）
4. 更新 `_index.md` status 为 `processed`
5. 报告结果

## 报告格式

```
维度: <dimension>
状态: DONE | DONE_WITH_CONCERNS | BLOCKED
产出: N 个 entity 页面 + M 个 concept 页面 + K 个 synthesis 页面
问题: <如有>
```
```

- [ ] **Step 2: Commit**

```bash
git add plugins/kb/agents/transform-agent.md
git commit -m "refactor(kb): rewrite transform-agent as single-dimension ingest subagent template"
```

---

### Task 4: 重写 /kb 命令为主编排器

**Files:**
- Rewrite: `plugins/kb/commands/kb.md`

- [ ] **Step 1: 写入新的 kb.md**

```markdown
---
description: "知识库 ETL 管道 — 从代码扫描到站点交付，6 步显式编排，并行化提取与转换"
argument-hint: "[scan|extract|transform|load|serve]"
effort: high
---

# /kb — 知识库 ETL 管道

你正在执行知识库 ETL 管道。严格按照以下 6 步顺序执行，每步必须输出检查点，下一步开始前必须确认上一步检查点。

用户参数: $ARGUMENTS

## 检查点协议

- 步骤状态: PENDING(□) → IN_PROGRESS(○) → DONE(✓) / SKIPPED(⊘)
- 完成时输出: `━━━ [✓] Step N/6: <NAME> — <一句话结果>` + `    产出物: <文件路径或状态>`
- 跳过时输出: `━━━ [⊘] Step N/6: <NAME> — 用户跳过，原因: <原因>` + `    产出物: <实际状态>`
- 开始前校验: `━━━ [→] Step N/6: <NAME> — 前置检查: Step N-1 <NAME> ✓`
- 前置缺失: `━━━ [✗] Step N/6: <NAME> — 阻塞: Step N-1 未完成` → 停止

## 子命令路由

根据 $ARGUMENTS 决定执行范围：

| 子命令 | 执行步骤 | 跳过步骤 |
|--------|----------|----------|
| （无） | Step 1-6 完整管道 | 无 |
| `scan` | Step 1 | Step 2-6 |
| `extract` | Step 1-3 | Step 4-6 |
| `transform` | Step 4 | Step 1-3, Step 5-6 |
| `load` | Step 5 | Step 1-4, Step 6 |
| `serve` | Step 6 | Step 1-5 |

子命令执行时，跳过的步骤用 SKIPPED(⊘) 标记，检查点协议不变。

## 进度总览

▶ /kb 启动 — 知识库 ETL 管道

  Step 1/6  SCAN       □  结构梳理，产出 _map.md
  Step 2/6  EXTRACT    □  并行派发 5 维度提取子代理
  Step 3/6  REVIEW_E   □  extract 结果审查（人类检查点）
  Step 4/6  TRANSFORM  □  并行派发 N 维度转化子代理 + 内联 cross-ref
  Step 5/6  LOAD       □  构建搜索索引 + 知识图谱数据
  Step 6/6  SERVE      □  构建站点 + 启动预览

---

## Step 1/6: SCAN

调用 `kb:scan` skill。

- 扫描代码库结构，产出模块清单、依赖关系、架构分层、入口识别、复杂度指标
- 输出: `data/raw/<project>/_map.md`
- 硬前置: 无

检查点: `━━━ [✓] Step 1/6: SCAN — _map.md 已产出`
产出物: `data/raw/<project>/_map.md`

## Step 2/6: EXTRACT

**并行派发 5 个 extract 维度子代理。**

用 Agent 工具同时派发 5 个子代理，每个处理一个维度：

| 维度 | subagent_type | prompt 要点 |
|------|--------------|-------------|
| topology | kb:extract-agent | 读取 _map.md，调用 extract-topology skill |
| api | kb:extract-agent | 读取 _map.md，调用 extract-api skill |
| data-model | kb:extract-agent | 读取 _map.md，调用 extract-data-model skill |
| flows | kb:extract-agent | 读取 _map.md，调用 extract-flows skill |
| concepts | kb:extract-agent | 读取 _map.md，调用 extract-concepts skill |

**派发方式**: 在一条消息中发出 5 个 Agent 工具调用，实现并行执行。

每个子代理 prompt 模板:
```
你是 extract 维度子代理。

项目: {project}
维度: {dimension}

执行流程:
1. 读取 data/raw/{project}/_map.md
2. 调用 kb:extract-{dimension} skill
3. 验证产出: data/raw/{project}/{dimension}/_index.md 存在且 modules/ 非空
4. 报告: 维度 / 状态 / 产出文件数量 / 问题
```

等待所有 5 个子代理完成后，汇总结果。

检查点: `━━━ [✓] Step 2/6: EXTRACT — 5 个维度提取完成`
产出物: `data/raw/<project>/{topology,api,data-model,flows,concepts}/`

## Step 3/6: REVIEW_E

**这是人类检查点。** 必须等待用户明确批准后才能继续。

- 展示每个维度的提取摘要（_index.md 关键指标 + module 数量）
- 检查输出完整性：每个维度的 _index.md 存在且 modules/ 非空
- 不完整的维度标记为需要重跑
- 等待用户响应: 批准继续 / 要求重跑特定维度 / 终止管道

检查点: `━━━ [✓] Step 3/6: REVIEW_E — 用户已批准 extract 结果`
产出物: 用户审批确认（对话状态）

## Step 4/6: TRANSFORM

**并行派发 N 个 ingest 维度子代理 + 内联 cross-ref。**

### Phase A: 并行 ingest

扫描 `data/raw/<project>/` 下 `status: unprocessed` 的维度，为每个维度用 Agent 工具并行派发一个 transform 子代理。

每个子代理 prompt 模板:
```
你是 transform 维度子代理。

项目: {project}
维度: {dimension}

执行流程:
1. 读取 data/raw/{project}/{dimension}/_index.md，确认 status: unprocessed
2. 调用 kb:ingest skill 处理该维度
3. 写出 wiki 页面（entity/concept/synthesis）
4. 更新 _index.md status 为 processed
5. 报告: 维度 / 状态 / 产出页面数量 / 问题
```

等待所有子代理完成。

### Phase B: 内联 cross-ref

所有维度 ingest 完成后，内联调用 `kb:cross-ref` skill：
- 扫描 wiki 页面，建立跨维度/跨模块关联
- 生成双向链接和 synthesis 页面
- 更新 overview.md

检查点: `━━━ [✓] Step 4/6: TRANSFORM — N 维度转化 + cross-ref 完成`
产出物: `data/wiki/<project>/` + cross-ref 结果

## Step 5/6: LOAD

内联执行，不派发子代理。

1. 调用 `kb:build-search-index` skill → `public/search-index.json`
2. 调用 `kb:build-graph` skill → `public/graph.json` + `public/projects.json`

检查点: `━━━ [✓] Step 5/6: LOAD — 索引和图谱数据已构建`
产出物: `public/search-index.json` + `public/graph.json`

## Step 6/6: SERVE

内联执行，不派发子代理。

1. `npm run setup`（创建符号链接）
2. `npm install --legacy-peer-deps`
3. `npm run build`（Astro 构建）
4. `npm run preview`（启动预览服务器）

检查点: `━━━ [✓] Step 6/6: SERVE — 站点已构建，预览已启动`
产出物: 预览 URL（默认 http://localhost:4321）
```

- [ ] **Step 2: Commit**

```bash
git add plugins/kb/commands/kb.md
git commit -m "refactor(kb): rewrite /kb command as checkpoint-driven orchestrator with parallel dispatch"
```

---

### Task 5: 更新版本号和 CHANGELOG

**Files:**
- Modify: `plugins/kb/.claude-plugin/plugin.json`
- Modify: `plugins/kb/CHANGELOG.md`

- [ ] **Step 1: 更新 plugin.json version**

将 `plugins/kb/.claude-plugin/plugin.json` 中 version 从 `0.1.0` 改为 `0.5.0`。

```json
{
  "name": "kb",
  "version": "0.5.0",
  "description": "知识库管理插件 — 从代码仓库提取、转化、加载和呈现知识",
  "author": { "name": "superpowers" },
  "license": "MIT"
}
```

- [ ] **Step 2: 更新 CHANGELOG.md**

在 `plugins/kb/CHANGELOG.md` 头部新增 `[0.5.0]` 条目：

```markdown
## [0.5.0] - 2026-05-25

### Changed
- 重构调度架构：删除 kb-agent，/kb 命令直接编排 6 步检查点管道
- extract 阶段：5 维度并行派发子代理（原串行 Skill 调用）
- transform 阶段：N 维度并行派发 ingest 子代理（原串行循环）
- cross-ref 改为内联执行（原由 transform-agent 串行调用）
- 新增人类检查点：Step 3 REVIEW_E（extract 完成后用户审查）
- extract-agent 重构为单维度子代理模板
- transform-agent 重构为单维度子代理模板
```

- [ ] **Step 3: Commit**

```bash
git add plugins/kb/.claude-plugin/plugin.json plugins/kb/CHANGELOG.md
git commit -m "chore(kb): bump version to 0.5.0 + changelog for flat-dispatch refactor"
```
