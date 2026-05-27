# Architecture Anti-Patterns

架构文档最常见的失败模式。这些 anti-pattern 会导致文档"看起来正确但无法落地"。在设计每个章节时、在可实现性门控时、在 reviewer 审查时，都必须检查这些 anti-pattern。

## 1. 接口-only

**症状：** 组件只有接口签名，无算法、状态机、错误处理

**检测方法：** 检查组件描述是否有算法/伪代码/状态机

**修复：** 每个接口需要：错误类型 + 至少 1 个使用示例 + 主方法的算法/伪代码

**示例：**
```
❌ interface IRouter { resolve(task): ModelSelection; }
✅ interface IRouter {
     resolve(task: string, ctx: RoutingContext): ModelSelection;
   }
   // 错误类型: RouteNotFoundError, AmbiguousRouteError
   // 算法: explicit → category → default 三级解析
```

## 2. Happy-path-only

**症状：** 序列图只有成功流，错误处理散落各处

**检测方法：** 检查每个交互序列是否有 alt 错误分支

**修复：** 每个序列必须包含 ≥1 错误/降级路径

**示例：**
```
❌ User → API → Service → DB → Done
✅ User → API → Service → DB → Done
   User → API → Service → DB Error → Retry/Fallback
```

## 3. 标签-only 组件

**症状：** 组件名无职责描述，只有名字

**检测方法：** 检查每个组件是否有"做什么/不做什么"

**修复：** 每个组件需要：职责（1 句话）+ 关键方法 + 不做什么

**示例：**
```
❌ DAGEngine
✅ DAGEngine: 按依赖顺序执行工作流步骤。关键方法: execute(workflow)。不解析 YAML，不管理状态持久化。
```

## 4. 状态机无触发

**症状：** 状态转换无触发条件，如 "running → done"

**检测方法：** 检查每个状态转换是否有 [触发条件] 和 /副作用

**修复：** 每个状态转换需要：触发事件 + 守卫条件 + 副作用

**示例：**
```
❌ Running → Done
✅ Running → Done [agent 返回成功] / 写审计日志，存储输出
```

## 5. 扩展点无示例

**症状：** "用策略模式" 但无接口签名

**检测方法：** 检查扩展点是否有接口 + 1 个实现示例

**修复：** 每个扩展点需要：接口签名 + 1 个具体实现示例 + 注册机制

**示例：**
```
❌ "支持自定义路由策略"
✅ interface IRoutingStrategy { resolve(task, ctx): ModelSelection; }
   class DefaultStrategy implements IRoutingStrategy { ... }
   class RoutingManager { constructor(strategy?: IRoutingStrategy) { ... } }
```

## 6. Schema-less 数据

**症状：** "存为 JSON" 但无字段

**检测方法：** 检查每个持久化数据是否有 JSON/YAML 样本

**修复：** 每个持久化数据结构需要具体的 Schema 示例

**示例：**
```
❌ "会话状态存为 JSON"
✅ { "session_id": "sess_abc", "status": "running", "steps": { "review": { "status": "done" } } }
```

## 7. 质量标签化

**症状：** "高性能" "高可用" 但无具体设计决策和量化目标

**检测方法：** 检查质量属性是否有具体机制和量化指标

**修复：** 每个质量属性必须包含：具体设计决策 + 可量化目标

**示例：**
```
❌ 性能: 高性能
✅ 性能: 采用连接池复用（maxConnections=20）+ 异步 I/O，延迟目标 p99 < 100ms
```

## 8. 缺少 Non-Goals

**症状：** 无"不做的事"章节

**检测方法：** 检查 §2.4 Non-Goals 章节是否存在且非空

**修复：** Non-Goals 必须明确列出"不做的事 + 原因 + 何时可能重新考虑"

**示例：**
```
✅ | 不做的事 | 原因 | 何时可能重新考虑 |
   | 自建对象存储 | 一期使用云厂商方案 | 日均存储 > 100TB 时 |
   | 在线编辑 | 非核心需求 | 二期 |
   | AI 内容审核 | 合规要求尚未明确 | 法务明确后 |
```

---

## Anti-Pattern 检查清单

| Anti-Pattern | 检查问题 | 通过标准 |
|-------------|---------|---------|
| 接口-only | 每个组件是否有算法或伪代码？ | 非平凡组件 100% 有 |
| Happy-path-only | 每个交互序列是否有错误路径？ | 每个序列 ≥1 错误路径 |
| 标签-only | 每个组件是否有职责描述？ | 100% 有 |
| 状态机无触发 | 每个状态转换是否有触发条件？ | 有状态组件 100% 有 |
| 扩展点无示例 | 每个扩展点是否有实现示例？ | 100% 有 |
| Schema-less | 每个持久化数据是否有 Schema？ | 100% 有 |
| 质量标签化 | 非功能设计是否有具体机制？ | 100% 有具体决策 |
| 缺少 Non-Goals | Non-Goals 是否存在且非空？ | 存在且 ≥3 条 |
