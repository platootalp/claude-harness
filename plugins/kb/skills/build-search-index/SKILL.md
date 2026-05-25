---
name: build-search-index
description: 内部技能——从 raw + wiki 内容构建搜索索引。由 serve 技能自动调用。
---

# Build Search Index

## 输入参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--kb-data-root <path>` | 否 | `data` | 知识库数据根目录，所有路径基于此 |

从 `{KB_DATA_ROOT}/raw/` 和 `{KB_DATA_ROOT}/wiki/` 读取 markdown，构建搜索索引。

## 执行

```bash
node scripts/build-search-index.mjs
```

## 输出

输出: `{KB_DATA_ROOT}/../site/public/search-index.json`
