# KB 插件实现计划 — Load/Present 阶段

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 KB 插件的 Load/Present 阶段——从 analysis 现有 Astro 站点增强，实现 Raw/Wiki/Graph 三视图、多项目导航、知识图谱可视化、搜索增强。

**Architecture:** 复用 analysis 站点的 DocLayout、TopNav、Sidebar、SearchModal 等组件，扩展路由体系支持多项目多视图，新增知识图谱（d3-force React 组件），新增 HomeLayout 和项目首页组件。两个 content collection（raw + wiki）替代单一 docs 集合。

**Tech Stack:** Astro 6 + React 18 + Tailwind 3 + d3-force + Fuse.js + Mermaid

**依赖的设计文档：** `docs/superpowers/specs/2026-05-24-kb-plugin-design.md`

**前置条件：** Extract + Transform 阶段已完成（`data/raw/` 和 `data/wiki/` 下有内容）

---

## 文件结构

### 从 analysis 复制并修改的文件

```
plugins/kb/site/
├── astro.config.mjs                    # 修改：raw+wiki 双集合
├── site.config.ts                      # 修改：KB 站点配置
├── tailwind.config.mjs                 # 复制
├── tsconfig.json                       # 复制
├── package.json                        # 修改：+d3 依赖
├── scripts/
│   └── build-search-index.mjs          # 重写：覆盖 raw+wiki
├── public/
│   ├── favicon.svg                     # 复制
│   └── robots.txt                      # 复制
├── src/
│   ├── content.config.ts               # 重写：raw+wiki 双集合
│   ├── layouts/
│   │   ├── DocLayout.astro             # 复用（微调 TopNav 插槽）
│   │   └── HomeLayout.astro            # 新增
│   ├── pages/
│   │   ├── index.astro                 # 重写：全局首页
│   │   ├── projects/
│   │   │   └── [project]/
│   │   │       ├── index.astro         # 新增：项目首页
│   │   │       ├── raw/
│   │   │       │   ├── index.astro     # 新增：Raw 总览
│   │   │       │   └── [...slug].astro # 新增：Raw 详情
│   │   │       ├── wiki/
│   │   │       │   ├── index.astro     # 新增：Wiki 总览
│   │   │       │   └── [...slug].astro # 新增：Wiki 详情
│   │   │       └── graph.astro         # 新增：知识图谱
│   │   ├── search.astro                # 修改：增强搜索
│   │   ├── sitemap.xml.astro           # 复制
│   │   └── 404.astro                   # 复制
│   ├── components/
│   │   ├── TopNav.astro                # 修改：+ProjectSwitcher
│   │   ├── Sidebar.astro               # 重写：动态导航树
│   │   ├── SearchModal.tsx             # 修改：raw+wiki 搜索
│   │   ├── ProjectSwitcher.astro       # 新增
│   │   ├── ProjectCard.astro           # 新增
│   │   ├── ViewCard.astro              # 新增
│   │   ├── DimensionBar.astro          # 新增
│   │   ├── RawDocMeta.astro            # 新增
│   │   ├── CrossReferences.astro       # 新增
│   │   ├── SourceTraceability.astro    # 新增
│   │   ├── KnowledgeGraph.tsx          # 新增
│   │   ├── GraphControls.tsx           # 新增
│   │   ├── NodeCard.tsx                # 新增
│   │   ├── Pagination.astro            # 复制
│   │   ├── TableOfContents.tsx         # 复制
│   │   ├── ReadingProgress.tsx         # 复制
│   │   ├── ThemeToggle.tsx             # 复制
│   │   ├── SearchTrigger.tsx           # 复制
│   │   ├── KeyboardShortcuts.astro     # 复制
│   │   ├── Breadcrumb.astro            # 复制
│   │   └── mermaid-block.ts            # 复制
│   ├── lib/
│   │   ├── rehype-callout.ts           # 复制
│   │   └── remark-mermaid.mjs          # 复制
│   └── styles/
│       └── global.css                  # 修改：+图谱样式
```

### 新增 skill 文件

```
plugins/kb/skills/
├── serve/SKILL.md
├── build-search-index/SKILL.md
└── build-graph/SKILL.md
```

---

## Task 1: 站点骨架 — 复制 + 配置

**Files:**
- Create: `plugins/kb/site/package.json`
- Create: `plugins/kb/site/astro.config.mjs`
- Create: `plugins/kb/site/site.config.ts`
- Create: `plugins/kb/site/tailwind.config.mjs`
- Create: `plugins/kb/site/tsconfig.json`

- [ ] **Step 1: 从 analysis 复制站点骨架**

```bash
mkdir -p plugins/kb/site
cp other/analysis/site/tailwind.config.mjs plugins/kb/site/
cp other/analysis/site/tsconfig.json plugins/kb/site/
mkdir -p plugins/kb/site/public
cp other/analysis/site/public/favicon.svg plugins/kb/site/public/
cp other/analysis/site/public/robots.txt plugins/kb/site/public/
mkdir -p plugins/kb/site/src/lib
cp other/analysis/site/src/lib/rehype-callout.ts plugins/kb/site/src/lib/
cp other/analysis/site/src/lib/remark-mermaid.mjs plugins/kb/site/src/lib/
cp other/analysis/site/src/styles/global.css plugins/kb/site/src/styles/global.css 2>/dev/null || true
```

- [ ] **Step 2: 创建 package.json（增加 d3 依赖）**

```json
{
  "name": "kb-plugin-site",
  "type": "module",
  "version": "0.1.0",
  "private": true,
  "engines": { "node": ">=22.12.0" },
  "scripts": {
    "dev": "astro dev",
    "build": "node scripts/build-search-index.mjs && node scripts/build-graph-data.mjs && astro build",
    "build:index": "node scripts/build-search-index.mjs",
    "build:graph": "node scripts/build-graph-data.mjs",
    "preview": "astro preview",
    "setup": "test -e data-raw || ln -s ../data/raw data-raw; test -e data-wiki || ln -s ../data/wiki data-wiki",
    "astro": "astro"
  },
  "dependencies": {
    "@astrojs/react": "^4.2.1",
    "@astrojs/tailwind": "^6.0.2",
    "@tailwindcss/typography": "^0.5.16",
    "astro": "^6.1.5",
    "d3-force": "^3.0.0",
    "d3-zoom": "^3.0.0",
    "d3-selection": "^3.0.0",
    "fuse.js": "^7.3.0",
    "hastscript": "^9.0.1",
    "mermaid": "^11.14.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "tailwindcss": "^3.4.17",
    "unist-util-visit": "^5.1.0"
  },
  "devDependencies": {
    "@types/d3-force": "^3.0.5",
    "@types/d3-zoom": "^3.0.8",
    "@types/d3-selection": "^3.0.10",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "typescript": "^5.7.3"
  }
}
```

- [ ] **Step 3: 创建 site.config.ts**

```typescript
export default {
  name: 'KB 知识库',
  description: '自动化个人知识库 — 代码库深度分析、结构化知识、交互式图谱',
  url: 'http://localhost:4321',
  nav: [
    { label: '首页', href: '/' },
    { label: '搜索', href: '/search' },
  ],
  sidebar: { auto: true },
  features: {
    search: true,
    mermaid: true,
    callout: true,
    readingProgress: true,
    themeToggle: true,
    keyboardShortcuts: true,
    knowledgeGraph: true,
  },
};
```

- [ ] **Step 4: 创建 astro.config.mjs**

```javascript
// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';
import { remarkMermaid } from './src/lib/remark-mermaid.mjs';
import { rehypeCallout } from './src/lib/rehype-callout.ts';
import config from './site.config.ts';

const rehypePlugins = [];
if (config.features.mermaid) rehypePlugins.push(remarkMermaid);
if (config.features.callout) rehypePlugins.push(rehypeCallout);

export default defineConfig({
  site: config.url,
  integrations: [react(), tailwind()],
  output: 'static',
  markdown: {
    remarkPlugins: [],
    rehypePlugins,
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark' },
    },
  },
  vite: {
    optimizeDeps: {
      include: [
        ...(config.features.mermaid ? ['mermaid'] : []),
        'react',
        'react-dom',
        'react-dom/client',
        'd3-force',
        'd3-zoom',
        'd3-selection',
      ],
    },
  },
});
```

- [ ] **Step 5: 创建 content.config.ts（双集合）**

```typescript
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = resolve(fileURLToPath(import.meta.url), '..');
const RAW_ROOT = resolve(__dirname, '../../data-raw');
const WIKI_ROOT = resolve(__dirname, '../../data-wiki');

const raw = defineCollection({
  loader: glob({ pattern: '**/*.md', base: RAW_ROOT, ignore: ['**/_map.md'] }),
  schema: z.object({
    project: z.string().optional(),
    dimension: z.enum(['topology', 'api', 'data-model', 'flows', 'concepts']).optional(),
    date: z.string().optional(),
    status: z.enum(['unprocessed', 'processed']).optional(),
    tags: z.array(z.string()).optional(),
  }),
});

const wiki = defineCollection({
  loader: glob({ pattern: 'projects/**/*.md', base: WIKI_ROOT }),
  schema: z.object({
    page_type: z.enum(['entity', 'concept', 'synthesis']).optional(),
    dimension: z.enum(['topology', 'api', 'data-model', 'flows', 'concepts']).optional(),
    project: z.string().optional(),
    tags: z.array(z.string()).optional(),
    sources: z.array(z.string()).optional(),
    date: z.string().optional(),
    last_updated: z.string().optional(),
    status: z.string().optional(),
  }),
});

export const collections = { raw, wiki };
```

- [ ] **Step 6: 提交**

```bash
git add plugins/kb/site/
git commit -m "feat(kb): 站点骨架 — package.json + astro config + 双 content collection"
```

---

## Task 2: 复用组件 — 复制 + 微调

**Files:**
- Copy: DocLayout, TopNav, Pagination, TableOfContents, ReadingProgress, ThemeToggle, SearchTrigger, SearchModal, KeyboardShortcuts, Breadcrumb, mermaid-block, global.css

- [ ] **Step 1: 复制可复用组件**

```bash
cd plugins/kb/site/src
mkdir -p components layouts pages styles

# 复制布局
cp ../../../../other/analysis/site/src/layouts/DocLayout.astro layouts/

# 复制组件
cp ../../../../other/analysis/site/src/components/Pagination.astro components/
cp ../../../../other/analysis/site/src/components/TableOfContents.tsx components/
cp ../../../../other/analysis/site/src/components/ReadingProgress.tsx components/
cp ../../../../other/analysis/site/src/components/ThemeToggle.tsx components/
cp ../../../../other/analysis/site/src/components/SearchTrigger.tsx components/
cp ../../../../other/analysis/site/src/components/SearchModal.tsx components/
cp ../../../../other/analysis/site/src/components/KeyboardShortcuts.astro components/
cp ../../../../other/analysis/site/src/components/Breadcrumb.astro components/
cp ../../../../other/analysis/site/src/components/mermaid-block.ts components/

# 复制样式
cp ../../../../other/analysis/site/src/styles/global.css styles/

# 复制页面骨架
cp ../../../../other/analysis/site/src/pages/404.astro pages/
cp ../../../../other/analysis/site/src/pages/sitemap.xml.astro pages/
cp ../../../../other/analysis/site/src/pages/search.astro pages/
```

- [ ] **Step 2: 复制 TopNav 并添加 ProjectSwitcher 插槽**

修改 `components/TopNav.astro`，在 Logo 和 Nav 之间添加 ProjectSwitcher 位置：

在 `<nav class="flex items-center gap-1">` 的开头添加：

```astro
---
import ProjectSwitcher from './ProjectSwitcher.astro';
---
<!-- ProjectSwitcher 放在 nav 的最前面 -->
<ProjectSwitcher client:idle />
```

- [ ] **Step 3: 提交**

```bash
git add plugins/kb/site/src/
git commit -m "feat(kb): 复用 analysis 站点组件 + TopNav 增加 ProjectSwitcher 插槽"
```

---

## Task 3: HomeLayout + 全局首页

**Files:**
- Create: `plugins/kb/site/src/layouts/HomeLayout.astro`
- Create: `plugins/kb/site/src/components/ProjectCard.astro`
- Create: `plugins/kb/site/src/components/ProjectSwitcher.astro`
- Create: `plugins/kb/site/src/pages/index.astro`

- [ ] **Step 1: 创建 HomeLayout.astro**

基于 DocLayout，但无侧边栏，全宽内容区：

```astro
---
import TopNav from '../components/TopNav.astro';
import SearchModal from '../components/SearchModal.tsx';
import KeyboardShortcuts from '../components/KeyboardShortcuts.astro';
import config from '../../site.config';
import '../styles/global.css';

interface Props {
  title?: string;
  description?: string;
}

const { title, description = config.description } = Astro.props;
const fullTitle = title ? `${title} — ${config.name}` : config.name;
---

<!doctype html>
<html lang="zh" class="scroll-smooth">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{fullTitle}</title>
    <meta name="description" content={description} />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <script is:inline>
      (function() {
        var stored = localStorage.getItem('theme');
        var root = document.documentElement;
        root.classList.remove('dark');
        if (stored === 'dark') { root.classList.add('dark'); }
        else if (!stored || stored === 'system') {
          if (window.matchMedia('(prefers-color-scheme: dark)').matches) root.classList.add('dark');
        }
      })();
    </script>
  </head>
  <body class="min-h-screen bg-[var(--color-bg)] text-[var(--color-text)] transition-colors duration-300">
    <TopNav title={title} />
    {config.features.search && <SearchModal client:load />}
    {config.features.keyboardShortcuts && <KeyboardShortcuts />}
    <main class="pt-16">
      <slot />
    </main>
  </body>
</html>
```

- [ ] **Step 2: 创建 ProjectCard.astro**

```astro
---
interface Props {
  name: string;
  rawCount: number;
  wikiCount: number;
  dimensions: number;
  lastUpdated: string;
}

const { name, rawCount, wikiCount, dimensions, lastUpdated } = Astro.props;
---

<a href={`/projects/${name}/`} class="block p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] hover:shadow-lg hover:border-[var(--color-primary)] transition-all no-underline group">
  <h3 class="text-lg font-semibold text-[var(--color-text)] group-hover:text-[var(--color-primary)] transition-colors">{name}</h3>
  <div class="mt-3 space-y-1 text-sm text-[var(--color-text-muted)]">
    <p>{rawCount} raw · {wikiCount} wiki · {dimensions} 维度</p>
    <p>最近更新: {lastUpdated}</p>
  </div>
</a>
```

- [ ] **Step 3: 创建 ProjectSwitcher.astro**

```astro
---
import { getCollection } from 'astro:content';

const allRaw = await getCollection('raw');
const projects = [...new Set(allRaw.map(doc => doc.data.project).filter(Boolean))];
---

<div class="relative">
  <select
    id="project-switcher"
    class="appearance-none bg-transparent border border-[var(--color-border)] rounded-md px-3 py-1 text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:border-[var(--color-primary)] transition-all cursor-pointer pr-8"
    onchange="if(this.value) window.location.href = this.value"
  >
    <option value="/">选择项目</option>
    {projects.map(p => (
      <option value={`/projects/${p}/`}>{p}</option>
    ))}
  </select>
  <svg class="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-[var(--color-text-muted)] pointer-events-none" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
  </svg>
</div>
```

- [ ] **Step 4: 创建全局首页 index.astro**

```astro
---
import HomeLayout from '../layouts/HomeLayout.astro';
import ProjectCard from '../components/ProjectCard.astro';
import { getCollection } from 'astro:content';

const allRaw = await getCollection('raw');
const allWiki = await getCollection('wiki');

// 获取项目列表
const projectNames = [...new Set(allRaw.map(doc => doc.data.project).filter(Boolean))];

// 每个项目的统计
const projectStats = projectNames.map(name => {
  const rawDocs = allRaw.filter(doc => doc.data.project === name);
  const wikiDocs = allWiki.filter(doc => doc.data.project === name);
  const dimensions = [...new Set(rawDocs.map(doc => doc.data.dimension).filter(Boolean))];
  const dates = rawDocs.map(doc => doc.data.date).filter(Boolean).sort().reverse();
  return {
    name,
    rawCount: rawDocs.length,
    wikiCount: wikiDocs.length,
    dimensions: dimensions.length,
    lastUpdated: dates[0] || '-',
  };
});
---

<HomeLayout title="首页">
  <div class="max-w-5xl mx-auto px-6 py-16">
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold text-[var(--color-text)]">KB — 自动化个人知识库</h1>
      <p class="mt-4 text-lg text-[var(--color-text-muted)]">代码库深度分析 → 结构化知识转化 → 交互式展示</p>
    </div>

    {projectNames.length > 0 ? (
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projectStats.map(stat => (
          <ProjectCard
            name={stat.name}
            rawCount={stat.rawCount}
            wikiCount={stat.wikiCount}
            dimensions={stat.dimensions}
            lastUpdated={stat.lastUpdated}
          />
        ))}
      </div>
    ) : (
      <div class="text-center py-12 text-[var(--color-text-muted)]">
        <p>知识库暂无项目。使用 <code class="bg-[var(--color-code-bg)] px-1.5 py-0.5 rounded text-sm">/kb</code> 命令开始提取。</p>
      </div>
    )}
  </div>
</HomeLayout>
```

- [ ] **Step 5: 提交**

```bash
git add plugins/kb/site/src/
git commit -m "feat(kb): HomeLayout + 全局首页 + ProjectCard + ProjectSwitcher"
```

---

## Task 4: 项目首页 + 视图入口

**Files:**
- Create: `plugins/kb/site/src/pages/projects/[project]/index.astro`
- Create: `plugins/kb/site/src/components/ViewCard.astro`
- Create: `plugins/kb/site/src/components/DimensionBar.astro`

- [ ] **Step 1: 创建 ViewCard.astro**

```astro
---
interface Props {
  title: string;
  count: number;
  subtitle: string;
  href: string;
  icon: string;
}

const { title, count, subtitle, href, icon } = Astro.props;
---

<a href={href} class="block p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] hover:shadow-lg hover:border-[var(--color-primary)] transition-all no-underline group">
  <div class="text-2xl mb-2">{icon}</div>
  <h3 class="text-lg font-semibold text-[var(--color-text)] group-hover:text-[var(--color-primary)] transition-colors">{title}</h3>
  <p class="mt-1 text-sm text-[var(--color-text-muted)]">{count} {subtitle}</p>
</a>
```

- [ ] **Step 2: 创建 DimensionBar.astro**

```astro
---
interface Props {
  dimensions: { name: string; count: number }[];
}

const { dimensions } = Astro.props;
const maxCount = Math.max(...dimensions.map(d => d.count), 1);

const dimensionColors: Record<string, string> = {
  topology: 'bg-blue-500',
  api: 'bg-emerald-500',
  'data-model': 'bg-amber-500',
  flows: 'bg-violet-500',
  concepts: 'bg-rose-500',
};
---

<div class="space-y-2">
  {dimensions.map(d => (
    <div class="flex items-center gap-3">
      <span class="w-24 text-sm text-[var(--color-text-muted)] text-right">{d.name}</span>
      <div class="flex-1 bg-[var(--color-surface)] rounded-full h-4 overflow-hidden">
        <div class={`h-full rounded-full ${dimensionColors[d.name] || 'bg-gray-500'}`} style={`width: ${(d.count / maxCount) * 100}%`}></div>
      </div>
      <span class="w-8 text-sm text-[var(--color-text-muted)]">{d.count}</span>
    </div>
  ))}
</div>
```

- [ ] **Step 3: 创建项目首页**

```astro
---
import DocLayout from '../../../layouts/DocLayout.astro';
import ViewCard from '../../../components/ViewCard.astro';
import DimensionBar from '../../../components/DimensionBar.astro';
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  const allRaw = await getCollection('raw');
  const projects = [...new Set(allRaw.map(doc => doc.data.project).filter(Boolean))];
  return projects.map(p => ({ params: { project: p } }));
}

const { project } = Astro.params;
const allRaw = await getCollection('raw');
const allWiki = await getCollection('wiki');

const rawDocs = allRaw.filter(doc => doc.data.project === project);
const wikiDocs = allWiki.filter(doc => doc.data.project === project);
const dimensions = [...new Set(rawDocs.map(doc => doc.data.dimension).filter(Boolean))];
const dimensionCounts = dimensions.map(d => ({
  name: d,
  count: rawDocs.filter(doc => doc.data.dimension === d).length,
}));
const currentPath = `/projects/${project}/`;
---

<DocLayout title={project} currentPath={currentPath}>
  <div class="px-6 py-10 max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-[var(--color-text)]">{project}</h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
      <ViewCard title="Raw 文档" count={rawDocs.length} subtitle="docs" href={`/projects/${project}/raw/`} icon="📄" />
      <ViewCard title="Wiki 页面" count={wikiDocs.length} subtitle="pages" href={`/projects/${project}/wiki/`} icon="📖" />
      <ViewCard title="知识图谱" count={0} subtitle="explore" href={`/projects/${project}/graph/`} icon="🕸️" />
    </div>

    <div class="mt-10">
      <h2 class="text-xl font-semibold text-[var(--color-text)] mb-4">维度覆盖</h2>
      <DimensionBar dimensions={dimensionCounts} />
    </div>
  </div>
</DocLayout>
```

- [ ] **Step 4: 提交**

```bash
git add plugins/kb/site/src/
git commit -m "feat(kb): 项目首页 + ViewCard + DimensionBar"
```

---

## Task 5: Raw 视图页面

**Files:**
- Create: `plugins/kb/site/src/pages/projects/[project]/raw/index.astro`
- Create: `plugins/kb/site/src/pages/projects/[project]/raw/[...slug].astro`
- Create: `plugins/kb/site/src/components/RawDocMeta.astro`

- [ ] **Step 1: 创建 RawDocMeta.astro**

```astro
---
interface Props {
  project: string;
  dimension: string;
  date: string;
  wikiHref?: string;
}

const { project, dimension, date, wikiHref } = Astro.props;
---

<div class="mt-8 p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-sm">
  <h4 class="font-semibold text-[var(--color-text)] mb-2">来源信息</h4>
  <dl class="space-y-1 text-[var(--color-text-muted)]">
    <div class="flex"><dt class="w-16">项目:</dt><dd>{project}</dd></div>
    <div class="flex"><dt class="w-16">维度:</dt><dd>{dimension}</dd></div>
    <div class="flex"><dt class="w-16">时间:</dt><dd>{date}</dd></div>
    {wikiHref && (
      <div class="flex"><dt class="w-16">Wiki:</dt><dd><a href={wikiHref} class="text-[var(--color-primary)] hover:underline">查看对应 Wiki 页面 →</a></dd></div>
    )}
  </dl>
</div>
```

- [ ] **Step 2: 创建 Raw 总览页**

```astro
---
import DocLayout from '../../../../../layouts/DocLayout.astro';
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  const allRaw = await getCollection('raw');
  const projects = [...new Set(allRaw.map(doc => doc.data.project).filter(Boolean))];
  return projects.map(p => ({ params: { project: p } }));
}

const { project } = Astro.params;
const allRaw = await getCollection('raw');
const rawDocs = allRaw.filter(doc => doc.data.project === project);

const dimensionGroups = ['topology', 'api', 'data-model', 'flows', 'concepts']
  .map(d => ({
    name: d,
    docs: rawDocs.filter(doc => doc.data.dimension === d),
  }))
  .filter(g => g.docs.length > 0);

const currentPath = `/projects/${project}/raw/`;
---

<DocLayout title={`Raw — ${project}`} currentPath={currentPath}>
  <div class="px-6 py-10 max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-[var(--color-text)]">Raw 文档 — {project}</h1>

    <div class="mt-8 space-y-8">
      {dimensionGroups.map(group => (
        <section>
          <h2 class="text-xl font-semibold text-[var(--color-text)] mb-3 pb-2 border-b border-[var(--color-border)]">
            {group.name} <span class="text-sm font-normal text-[var(--color-text-muted)]">({group.docs.length} docs)</span>
          </h2>
          <ul class="space-y-1">
            {group.docs.map(doc => {
              const slug = doc.id.replace(/\.md$/, '');
              return (
                <li>
                  <a href={`/projects/${project}/raw/${slug}/`} class="text-[var(--color-primary)] hover:underline text-sm">
                    {doc.data.title || slug}
                  </a>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  </div>
</DocLayout>
```

- [ ] **Step 3: 创建 Raw 详情页**

```astro
---
import { getCollection, render } from 'astro:content';
import DocLayout from '../../../../../layouts/DocLayout.astro';
import TableOfContents from '../../../../../components/TableOfContents.tsx';
import ReadingProgress from '../../../../../components/ReadingProgress.tsx';
import RawDocMeta from '../../../../../components/RawDocMeta.astro';

export async function getStaticPaths() {
  const allRaw = await getCollection('raw');
  return allRaw.map(doc => {
    const parts = doc.id.split('/');
    const project = doc.data.project || parts[0];
    const slug = doc.id.replace(/\.md$/, '');
    return {
      params: { project, slug: slug.startsWith(`${project}/`) ? slug.slice(project.length + 1) : slug },
      props: { doc },
    };
  });
}

const { doc } = Astro.props;
const { Content, headings } = await render(doc);
const project = doc.data.project || '';
const dimension = doc.data.dimension || '';
const date = doc.data.date || '';
const currentH2s = headings.filter(h => h.depth === 2 || h.depth === 3);
const currentPath = `/projects/${project}/raw/${Astro.params.slug}/`;
---

<DocLayout title={doc.data.title || Astro.params.slug} currentPath={currentPath}>
  <ReadingProgress client:load />

  <div class="flex flex-col xl:flex-row xl:items-start xl:gap-8 xl:max-w-screen-xl xl:w-full xl:mx-auto px-6 xl:px-10 py-10">
    <div>
      <article class="prose prose-slate dark:prose-invert prose-headings:font-semibold prose-headings:text-[var(--color-text)] prose-h1:text-3xl prose-h1:font-bold prose-p:text-[var(--color-text)] prose-a:text-[var(--color-primary)] prose-code:text-[var(--color-primary)] prose-code:bg-[var(--color-code-bg)] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-pre:bg-[#1e293b] prose-pre:rounded-lg prose-pre:p-0">
        <Content />
      </article>

      <RawDocMeta project={project} dimension={dimension} date={date} />
    </div>

    {currentH2s.length > 2 && (
      <aside class="hidden xl:block xl:sticky xl:top-24 xl:self-start xl:flex-shrink-0 xl:w-36 xl:ml-4">
        <TableOfContents headings={currentH2s} currentPath={currentPath} client:load />
      </aside>
    )}
  </div>
</DocLayout>
```

- [ ] **Step 4: 提交**

```bash
git add plugins/kb/site/src/
git commit -m "feat(kb): Raw 视图 — 总览页 + 详情页 + RawDocMeta"
```

---

## Task 6: Wiki 视图页面

**Files:**
- Create: `plugins/kb/site/src/pages/projects/[project]/wiki/index.astro`
- Create: `plugins/kb/site/src/pages/projects/[project]/wiki/[...slug].astro`
- Create: `plugins/kb/site/src/components/CrossReferences.astro`
- Create: `plugins/kb/site/src/components/SourceTraceability.astro`

- [ ] **Step 1: 创建 CrossReferences.astro**

```astro
---
interface Props {
  references: { title: string; href: string; type: string }[];
}

const { references } = Astro.props;
const byType = references.reduce((acc, ref) => {
  if (!acc[ref.type]) acc[ref.type] = [];
  acc[ref.type].push(ref);
  return acc;
}, {} as Record<string, typeof references>);
---

<div class="mt-8 p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]">
  <h4 class="font-semibold text-[var(--color-text)] mb-3">交叉引用</h4>
  {Object.entries(byType).map(([type, refs]) => (
    <div class="mb-2">
      <span class="text-xs uppercase tracking-wider text-[var(--color-text-muted)]">{type}</span>
      <ul class="mt-1 space-y-1">
        {refs.map(ref => (
          <li><a href={ref.href} class="text-sm text-[var(--color-primary)] hover:underline">{ref.title}</a></li>
        ))}
      </ul>
    </div>
  ))}
</div>
```

- [ ] **Step 2: 创建 SourceTraceability.astro**

```astro
---
interface Props {
  sources: string[];
  project: string;
}

const { sources, project } = Astro.props;
---

<div class="mt-4 p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]">
  <h4 class="font-semibold text-[var(--color-text)] mb-2">来源追溯</h4>
  <ul class="space-y-1">
    {sources.map(src => {
      const slug = src.replace(/\.md$/, '');
      return (
        <li>
          <a href={`/projects/${project}/raw/${slug}/`} class="text-sm text-[var(--color-primary)] hover:underline">
            ← {src}
          </a>
        </li>
      );
    })}
  </ul>
</div>
```

- [ ] **Step 3: 创建 Wiki 总览页**

结构与 Raw 总览类似，但按 page_type（entity/concept/synthesis）分组，entity 下再按 dimension 细分。此处省略完整代码（与 Task 5 的 Raw 总览结构对称，替换 collection 为 wiki、分组键为 page_type）。

- [ ] **Step 4: 创建 Wiki 详情页**

结构与 Raw 详情页类似，但在文章下方渲染 CrossReferences 和 SourceTraceability 组件：

```astro
<!-- 在 <article> 之后添加 -->
<CrossReferences references={crossRefs} />
<SourceTraceability sources={doc.data.sources || []} project={project} />
```

其中 `crossRefs` 从 wiki 页面的"另见"章节解析而来。

- [ ] **Step 5: 提交**

```bash
git add plugins/kb/site/src/
git commit -m "feat(kb): Wiki 视图 — 总览页 + 详情页 + CrossReferences + SourceTraceability"
```

---

## Task 7: 知识图谱页面

**Files:**
- Create: `plugins/kb/site/src/pages/projects/[project]/graph.astro`
- Create: `plugins/kb/site/src/components/KnowledgeGraph.tsx`
- Create: `plugins/kb/site/src/components/GraphControls.tsx`
- Create: `plugins/kb/site/src/components/NodeCard.tsx`

- [ ] **Step 1: 创建 NodeCard.tsx**

```tsx
import { useState } from 'react';

interface NodeCardProps {
  node: { id: string; label: string; type: string; dimension?: string; summary: string; project: string };
  x: number;
  y: number;
}

export default function NodeCard({ node, x, y }: NodeCardProps) {
  const wikiHref = `/projects/${node.project}/wiki/${node.id.replace(/\.md$/, '')}/`;
  const rawHref = `/projects/${node.project}/raw/${node.id.replace(/\.md$/, '')}/`;

  return (
    <div
      className="fixed z-50 p-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-lg text-sm max-w-xs"
      style={{ left: x + 15, top: y + 15 }}
    >
      <h5 className="font-semibold text-[var(--color-text)]">{node.label}</h5>
      <p className="text-xs text-[var(--color-text-muted)] mt-1">
        类型: {node.type} · 维度: {node.dimension || '-'}
      </p>
      <p className="text-xs text-[var(--color-text-muted)] mt-1">{node.summary}</p>
      <div className="mt-2 flex gap-2">
        <a href={wikiHref} className="text-xs text-[var(--color-primary)] hover:underline">Wiki</a>
        <a href={rawHref} className="text-xs text-[var(--color-primary)] hover:underline">Raw</a>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 创建 GraphControls.tsx**

```tsx
interface GraphControlsProps {
  colorMode: 'dimension' | 'type' | 'project';
  onColorModeChange: (mode: 'dimension' | 'type' | 'project') => void;
  visibleCount: number;
  totalCount: number;
  visibleEdges: number;
  totalEdges: number;
}

export default function GraphControls({
  colorMode, onColorModeChange, visibleCount, totalCount, visibleEdges, totalEdges,
}: GraphControlsProps) {
  return (
    <div className="flex flex-wrap items-center gap-3 p-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-sm">
      <label className="text-[var(--color-text-muted)]">着色:</label>
      <select
        value={colorMode}
        onChange={e => onColorModeChange(e.target.value as typeof colorMode)}
        className="bg-transparent border border-[var(--color-border)] rounded px-2 py-1 text-[var(--color-text)]"
      >
        <option value="dimension">维度</option>
        <option value="type">类型</option>
        <option value="project">项目</option>
      </select>
      <span className="text-[var(--color-text-muted)]">
        {visibleCount}/{totalCount} 节点 · {visibleEdges}/{totalEdges} 边
      </span>
    </div>
  );
}
```

- [ ] **Step 3: 创建 KnowledgeGraph.tsx**

核心组件，使用 d3-force 实现力导向布局。关键实现：

```tsx
import { useEffect, useRef, useState } from 'react';
import {
  forceSimulation, forceLink, forceManyBody, forceCenter,
} from 'd3-force';
import { zoom, zoomIdentity } from 'd3-zoom';
import { select } from 'd3-selection';
import NodeCard from './NodeCard';
import GraphControls from './GraphControls';

interface GraphData {
  nodes: Array<{
    id: string; label: string; type: 'entity' | 'concept' | 'synthesis';
    dimension?: string; project: string; summary: string;
  }>;
  edges: Array<{
    source: string; target: string;
    signal: 'name-overlap' | 'shared-code' | 'parent-child' | 'flow-participation';
  }>;
}

const DIMENSION_COLORS: Record<string, string> = {
  topology: '#3b82f6', api: '#10b981', 'data-model': '#f59e0b',
  flows: '#8b5cf6', concepts: '#f43f5e',
};
const TYPE_COLORS: Record<string, string> = {
  entity: '#3b82f6', concept: '#10b981', synthesis: '#f59e0b',
};

export default function KnowledgeGraph() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [data, setData] = useState<GraphData | null>(null);
  const [hoveredNode, setHoveredNode] = useState<{ node: GraphData['nodes'][0]; x: number; y: number } | null>(null);
  const [colorMode, setColorMode] = useState<'dimension' | 'type' | 'project'>('dimension');

  useEffect(() => {
    fetch('/graph.json').then(r => r.json()).then(setData);
  }, []);

  useEffect(() => {
    if (!data || !svgRef.current) return;
    // d3-force simulation + zoom + render
    // 完整实现包含：力导向布局计算、SVG 渲染、缩放/平移、拖拽、悬浮、点击聚焦
    // 此处为骨架，实际实现约 200 行
  }, [data, colorMode]);

  if (!data) return <div className="text-[var(--color-text-muted)] p-8">加载图谱数据...</div>;

  return (
    <div className="relative w-full h-[calc(100vh-8rem)]">
      <div className="absolute top-4 left-4 z-10">
        <GraphControls
          colorMode={colorMode}
          onColorModeChange={setColorMode}
          visibleCount={data.nodes.length}
          totalCount={data.nodes.length}
          visibleEdges={data.edges.length}
          totalEdges={data.edges.length}
        />
      </div>
      <svg ref={svgRef} className="w-full h-full" />
      {hoveredNode && (
        <NodeCard node={hoveredNode.node} x={hoveredNode.x} y={hoveredNode.y} />
      )}
    </div>
  );
}
```

- [ ] **Step 4: 创建图谱页面 graph.astro**

```astro
---
import DocLayout from '../../../../layouts/DocLayout.astro';
import KnowledgeGraph from '../../../../components/KnowledgeGraph.tsx';
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  const allWiki = await getCollection('wiki');
  const projects = [...new Set(allWiki.map(doc => doc.data.project).filter(Boolean))];
  return projects.map(p => ({ params: { project: p } }));
}

const { project } = Astro.params;
const currentPath = `/projects/${project}/graph/`;
---

<DocLayout title={`图谱 — ${project}`} currentPath={currentPath}>
  <div class="px-2 py-2">
    <KnowledgeGraph client:load />
  </div>
</DocLayout>
```

- [ ] **Step 5: 提交**

```bash
git add plugins/kb/site/src/
git commit -m "feat(kb): 知识图谱 — KnowledgeGraph + GraphControls + NodeCard + graph 页面"
```

---

## Task 8: 构建脚本 + serve skill

**Files:**
- Create: `plugins/kb/site/scripts/build-search-index.mjs`
- Create: `plugins/kb/site/scripts/build-graph-data.mjs`
- Create: `plugins/kb/skills/serve/SKILL.md`
- Create: `plugins/kb/skills/build-search-index/SKILL.md`
- Create: `plugins/kb/skills/build-graph/SKILL.md`

- [ ] **Step 1: 创建 build-search-index.mjs**

增强版搜索索引构建，覆盖 raw + wiki 两个集合。从 `data-raw/` 和 `data-wiki/` 目录读取 markdown，解析 frontmatter，提取标题和正文，写入 `public/search-index.json`。

- [ ] **Step 2: 创建 build-graph-data.mjs**

从 `data-wiki/projects/` 下的 wiki 页面提取交叉引用关系，构建 `graph.json`（nodes + edges），写入 `public/graph.json`。

节点：每个 wiki 页面一个节点，包含 id、label、type、dimension、project、summary。

边：从 wiki 页面的"另见"章节解析链接，每对链接生成一条边，signal 字段根据链接来源推断。

- [ ] **Step 3: 创建 serve SKILL.md**

```markdown
---
name: serve
description: 构建 Astro 站点并启动预览服务器。
---

# Serve — 构建与预览

## 执行流程

1. 确保数据符号链接存在：`npm run setup`
2. 安装依赖：`npm install --legacy-peer-deps`
3. 构建搜索索引：`npm run build:index`
4. 构建图谱数据：`npm run build:graph`
5. 构建站点：`npm run build`（包含上述两步）
6. 启动预览：`npm run preview`

## 用法

- `serve --port <port>`：指定端口（默认 4321）
- `serve --build-only`：只构建，不启动预览
```

- [ ] **Step 4: 创建 build-search-index 和 build-graph 的 SKILL.md**

两个内部 skill，文档说明各自职责和执行方式，用户不直接调用。

- [ ] **Step 5: 提交**

```bash
git add plugins/kb/site/scripts/ plugins/kb/skills/serve/ plugins/kb/skills/build-search-index/ plugins/kb/skills/build-graph/
git commit -m "feat(kb): 构建脚本 + serve/build-search-index/build-graph skills"
```

---

## Task 9: Sidebar 动态导航

**Files:**
- Modify: `plugins/kb/site/src/components/Sidebar.astro`

- [ ] **Step 1: 重写 Sidebar.astro**

现有 Sidebar 从单一 `docs` 集合构建导航。重写为根据当前路径动态构建：

- 路径匹配 `/projects/<project>/raw/*` → Raw 视图侧边栏（按维度分组）
- 路径匹配 `/projects/<project>/wiki/*` → Wiki 视图侧边栏（按页面类型分组）
- 路径匹配 `/projects/<project>/graph` → 图谱页侧边栏（收起为 icon-rail）
- 其他 → 项目首页侧边栏（Raw / Wiki / Graph 三组）

关键改动：Sidebar 接收 `view` prop（raw/wiki/graph/home），根据 view 值从对应的 content collection 构建导航树。

- [ ] **Step 2: 提交**

```bash
git add plugins/kb/site/src/components/Sidebar.astro
git commit -m "feat(kb): Sidebar 动态导航 — 根据 view 类型构建不同导航树"
```

---

## Task 10: 端到端验证

**前置条件：** Extract + Transform 阶段已产出内容，站点代码已完成

- [ ] **Step 1: 安装依赖并构建**

```bash
cd plugins/kb/site
npm run setup
npm install --legacy-peer-deps
npm run build
```

预期：构建成功，`public/search-index.json` 和 `public/graph.json` 生成。

- [ ] **Step 2: 启动预览并验证页面**

```bash
npm run preview
```

验证：
- `/` — 全局首页显示项目卡片
- `/projects/claude-harness/` — 项目首页显示三视图入口和维度覆盖
- `/projects/claude-harness/raw/` — Raw 总览按维度分组
- `/projects/claude-harness/raw/topology/modules/spec-workflow/` — Raw 详情渲染 markdown + Mermaid + 来源信息
- `/projects/claude-harness/wiki/` — Wiki 总览按类型分组
- `/projects/claude-harness/wiki/entities/spec-workflow/` — Wiki 详情渲染 + 交叉引用 + 来源追溯
- `/projects/claude-harness/graph/` — 知识图谱力导向图可交互
- 搜索（Ctrl+K）覆盖 raw + wiki 内容

- [ ] **Step 3: 提交验证结果**

```bash
git add -A
git commit -m "feat(kb): Load/Present 阶段端到端验证"
```