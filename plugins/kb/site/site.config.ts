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
