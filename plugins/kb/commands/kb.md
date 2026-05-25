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

## 路径约定

所有数据写入路径基于 `KB_DATA_ROOT`，计算规则：

1. 读取本 command 文件所在目录，向上两级即为插件根目录（`commands/` → plugin root）
2. `KB_DATA_ROOT = <plugin-root>/data/`
3. 所有子代理 prompt 中，将 `data/raw/` 替换为 `{KB_DATA_ROOT}/raw/`，`data/wiki/` 替换为 `{KB_DATA_ROOT}/wiki/`
4. 在派发子代理时，将 `KB_DATA_ROOT` 的绝对路径作为参数传入 prompt

**示例：** 插件安装在 `/Users/x/.claude/plugins/cache/harness-marketplace/kb/0.6.0/`，则 `KB_DATA_ROOT = /Users/x/.claude/plugins/cache/harness-marketplace/kb/0.6.0/data/`

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
- 输出: `{KB_DATA_ROOT}/raw/<project>/_map.md`
- 硬前置: 无

检查点: `━━━ [✓] Step 1/6: SCAN — _map.md 已产出`
产出物: `{KB_DATA_ROOT}/raw/<project>/_map.md`

## Step 2/6: EXTRACT

**按模块并行派发 extract 子代理。**

1. 读取 `{KB_DATA_ROOT}/raw/<project>/_map.md`，解析模块清单
2. 对每个维度 × 每个模块，派发一个子代理（最多同时 10 个并行）
3. 每个子代理 prompt 模板:
```
你是 extract 模块子代理。

项目: {project}
维度: {dimension}
模块: {module}
数据根目录: {KB_DATA_ROOT}
目标代码库: {target_path}

执行流程:
1. 读取 {KB_DATA_ROOT}/raw/{project}/_map.md
2. 读取目标模块的源代码文件
3. 调用 kb:extract-{dimension} skill（仅分析 {module} 模块，传入 --module {module} 参数）
4. 验证产出: {KB_DATA_ROOT}/raw/{project}/{dimension}/modules/{module}.md 存在且内容满足验收标准
5. 报告: 维度 / 模块 / 状态 / 产出行数 / 验收通过项
```

5 个维度: topology, api, data-model, flows, concepts
模块列表: 从 _map.md 的模块清单表格提取

等待所有子代理完成后，汇总结果。对每个维度生成 `_index.md`（汇总该维度所有模块的产出）。

检查点: `━━━ [✓] Step 2/6: EXTRACT — 所有维度×模块提取完成`
产出物: `{KB_DATA_ROOT}/raw/<project>/{topology,api,data-model,flows,concepts}/`

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

扫描 `{KB_DATA_ROOT}/raw/<project>/` 下 `status: unprocessed` 的维度，为每个维度用 Agent 工具并行派发一个 transform 子代理。

每个子代理 prompt 模板:
```
你是 transform 维度子代理。

项目: {project}
维度: {dimension}
数据根目录: {KB_DATA_ROOT}

执行流程:
1. 读取 {KB_DATA_ROOT}/raw/{project}/{dimension}/_index.md，确认 status: unprocessed
2. 调用 kb:ingest skill 处理该维度（传入 --kb-data-root {KB_DATA_ROOT} 参数）
3. 写出 wiki 页面到 {KB_DATA_ROOT}/wiki/{project}/（entity/concept/synthesis）
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
产出物: `{KB_DATA_ROOT}/wiki/<project>/` + cross-ref 结果

## Step 5/6: LOAD

内联执行，不派发子代理。

1. 调用 `kb:build-search-index` skill → `{KB_DATA_ROOT}/../site/public/search-index.json`
2. 调用 `kb:build-graph` skill → `{KB_DATA_ROOT}/../site/public/graph.json` + `{KB_DATA_ROOT}/../site/public/projects.json`

检查点: `━━━ [✓] Step 5/6: LOAD — 索引和图谱数据已构建`
产出物: `{KB_DATA_ROOT}/../site/public/search-index.json` + `{KB_DATA_ROOT}/../site/public/graph.json`

## Step 6/6: SERVE

内联执行，不派发子代理。

1. `npm run setup`（创建符号链接）
2. `npm install --legacy-peer-deps`
3. `npm run build`（Astro 构建）
4. `npm run preview`（启动预览服务器）

检查点: `━━━ [✓] Step 6/6: SERVE — 站点已构建，预览已启动`
产出物: 预览 URL（默认 http://localhost:4321），站点目录: `{KB_DATA_ROOT}/../site/`
