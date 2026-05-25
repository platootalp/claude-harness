---
name: serve
description: 当需要构建知识库站点并启动预览服务器时使用。串联搜索索引构建、图谱数据构建、Astro 构建和预览服务。
---

# Serve — 构建与预览

构建知识库站点并启动预览服务器。

## 执行流程

1. 确保数据符号链接存在：`npm run setup`
2. 安装依赖：`npm install --legacy-peer-deps`
3. 构建搜索索引：`npm run build:index`
4. 构建图谱数据：`npm run build:graph`
5. 构建站点：`npm run build`
6. 启动预览：`npm run preview`

## 反模式

| 想法 | 问题 |
|------|------|
| "直接 `astro dev` 就行" | dev 模式不执行搜索索引和图谱数据构建 |
| "跳过 setup 步骤" | 没有符号链接，Astro 的 content collection 找不到数据 |

## 关键原则

- **构建管线不可跳步：** setup → install → build:index → build:graph → build → preview
- **数据优先：** 站点只是展示层，数据质量决定站点质量
