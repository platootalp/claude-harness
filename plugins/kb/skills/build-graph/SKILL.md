---
name: build-graph
description: 内部技能——从 wiki 页面提取交叉引用，构建图谱数据。由 serve 技能自动调用。
---

# Build Graph Data

从 `data-wiki/` 下的 wiki 页面提取交叉引用，构建图谱数据。

## 执行

```bash
node scripts/build-graph-data.mjs
```

## 输出

`public/graph.json` + `public/projects.json`
