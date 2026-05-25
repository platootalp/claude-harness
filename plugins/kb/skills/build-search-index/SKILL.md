---
name: build-search-index
description: 内部技能——从 raw + wiki 内容构建搜索索引。由 serve 技能自动调用。
---

# Build Search Index

从 `data-raw/` 和 `data-wiki/` 读取 markdown，构建搜索索引。

## 执行

```bash
node scripts/build-search-index.mjs
```

## 输出

`public/search-index.json`
