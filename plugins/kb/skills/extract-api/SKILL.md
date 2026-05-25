---
name: extract-api
description: 当需要理解模块对外暴露的接口、协议、参数格式、或调用方式时使用。读取结构地图，逐模块提取 API 接口文档。
---

# Extract API — API 接口提取

读取结构地图，逐模块提取 API 接口文档。

<HARD-GATE>
`data/raw/<project>/_map.md` 必须存在（由 scan 技能产出）。如果没有，先调用 scan 技能。
</HARD-GATE>

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--target <path>` | 是 | - | 目标代码库路径 |
| `--project <name>` | 是 | - | 项目名称 |
| `--module <name>` | 否 | 全量 | 只分析指定模块 |

## 前置条件

- `data/raw/<project>/_map.md` 必须存在

## 输出

- `data/raw/<project>/api/_index.md`（带 frontmatter 的索引）
- `data/raw/<project>/api/modules/<module>.md`（每个模块一份接口文档）

## 反模式

| 想法 | 问题 |
|------|------|
| "只提取 HTTP 接口就够了" | CLI 命令、事件、SDK 导出同样是接口，遗漏它们会导致知识库不完整 |
| "参数和返回值从类型定义抄就行" | 类型定义不含业务含义。必须结合 handler 代码理解参数的实际用途和约束 |
| "调用示例用伪代码" | 伪代码无法验证。必须用实际的 curl 命令或代码片段，确保可执行 |
| "接口之间没有关系就不用画图" | 即使没有顺序依赖，也有数据依赖和共享资源。序列图揭示隐含关系 |

## 执行流程

1. 读取 `_map.md`，获取模块清单和对外接口数量
2. 如果指定了 `--module`，只分析该模块；否则分析所有模块
3. 对每个模块：
   a. 识别接口文件（路由定义、handler 函数、命令注册、事件声明、SDK 导出）
   b. 提取接口定义（方法、路径/名称、用途、认证要求）
   c. 提取参数和响应格式（字段、类型、必填、说明）
   d. 提取错误码（错误码、含义、触发条件）
   e. 提取调用模式（调用序列、分页/游标、幂等性）
   f. 生成 Mermaid 序列图（典型调用流程）
   g. 按 `templates/api.md` 模板生成接口文档
   h. 写入 `api/modules/<module>.md`
4. 生成 `api/_index.md`（接口清单 + 调用总图 + frontmatter）

## `_index.md` frontmatter

```yaml
---
project: <project>
dimension: api
date: YYYY-MM-DD
status: unprocessed
tags: [...]
---
```

## 模板

遵循 `templates/api.md` 定义的必含章节和质量要求。

## 关键原则

- **契约完整性：** 参数、返回值、错误码三者缺一不可，否则无法作为接口参考
- **可验证的示例：** 调用示例必须可执行，不是伪代码
- **按模块组织：** 每个模块一份接口文档，保证独立性和 Transform 阶段的可处理性
