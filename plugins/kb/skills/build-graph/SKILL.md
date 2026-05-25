---
name: build-graph
description: 内部技能——从 wiki 页面提取交叉引用，构建图谱数据。由 serve 技能自动调用。
---

# Build Graph Data

## 输入参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--kb-data-root <path>` | 否 | `data` | 知识库数据根目录，所有路径基于此 |

从 `{KB_DATA_ROOT}/wiki/` 下的 wiki 页面提取交叉引用，构建图谱数据。

## 执行

```bash
node scripts/build-graph-data.mjs
```

## 输出

`public/graph.json` + `public/projects.json`
