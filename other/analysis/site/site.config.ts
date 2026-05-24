export default {
  name: "Analysis Plugin Docs",
  description: "Generated documentation from codebase analysis",
  url: "http://localhost:4321",

  nav: [
    { label: "Docs", href: "/docs" },
    { label: "Search", href: "/search" },
  ],

  sidebar: {
    auto: true,
  },

  features: {
    search: true,
    mermaid: true,
    callout: true,
    readingProgress: true,
    themeToggle: true,
    keyboardShortcuts: true,
  },
} as const;

export type SiteConfig = typeof import('./site.config').default;
