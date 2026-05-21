---
name: analysis-plugin-docs-integration
description: Integrate docs-site-template into analysis plugin with extensible skills, agents, and commands
metadata:
  type: project
---

# Analysis Plugin Docs Integration Design

## Goal

Merge the Astro docs-site-template into the analysis plugin, creating a self-contained plugin that can analyze codebases, generate documentation, and serve it as a web site. Add extensible agents and commands that orchestrate skills and the web layer.

## Approach: Full Embed

The entire Astro site moves into `plugins/analysis/site/`. The plugin owns skills, agents, commands, and the web presentation layer. One `--plugin-dir` install gives the full stack.

## Directory Structure

```
plugins/analysis/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── analysis-agent.md
│   └── doc-gen-agent.md
├── commands/
│   ├── analyze.md
│   ├── gen-docs.md
│   └── serve-docs.md
├── skills/
│   ├── codebase-analysis/
│   ├── codebase-to-docs/
│   ├── system-architecture-analysis/
│   ├── deep-functional-analysis/
│   └── source-functional-analysis/
├── docs/                        ← generated markdown (gitignored)
│   └── (auto-populated by skills)
└── site/                        ← Astro site (from docs-site-template)
    ├── astro.config.mjs
    ├── site.config.ts
    ├── tailwind.config.mjs
    ├── package.json
    ├── tsconfig.json
    ├── scripts/
    │   └── build-search-index.mjs
    ├── src/
    │   ├── components/
    │   ├── layouts/
    │   ├── lib/
    │   ├── pages/
    │   └── styles/
    ├── public/
    └── docs → ../docs            ← symlink
```

## Key Design Decisions

### Symlink: site/docs → ../docs

Skills write markdown to `plugins/analysis/docs/`. Astro reads from `site/docs/` which is a symlink to `../docs`. Zero duplication, no copy step. On Windows, a junction point serves the same purpose.

### docs/ is gitignored

Generated content is not source. Skills regenerate it on demand. The `.gitignore` in `plugins/analysis/` excludes `docs/` and `site/docs/`.

### site/ has its own package.json

Astro dependencies (astro, react, tailwind, fuse.js, etc.) are isolated in `site/package.json`. The plugin itself has no Node.js dependency. This keeps the plugin manifest clean and avoids version conflicts.

### site.config.ts is pre-configured

Branded for the analysis plugin:
- `name`: "Analysis Plugin Docs"
- `sidebar.auto`: true (groups by top-level directory matching skill names)
- `features`: all enabled (search, mermaid, callout, reading progress, theme toggle, keyboard shortcuts)

## Agents

### analysis-agent

Orchestration agent that routes user requests to the right skill.

**Routing logic:**

| User Need | Routes To | Output |
|-----------|-----------|--------|
| Full codebase documentation site | codebase-to-docs | Multi-page docs in docs/ |
| Architecture analysis (C4 model) | system-architecture-analysis | Single architecture doc |
| Deep dive into one mechanism | deep-functional-analysis | Deep-analysis doc |
| Breadth-first functional inventory | source-functional-analysis | Functional points doc |
| Unsure what analysis to run | codebase-analysis | Decision recommendation |

**Model:** sonnet (routing doesn't need opus-level reasoning)

**Tools:** Read, Glob, Grep, Bash, Skill

### doc-gen-agent

Orchestrates the full documentation generation pipeline: skill generates markdown → search index builds → site is ready to serve.

**Workflow:**
1. Invoke `codebase-to-docs` skill on the target codebase
2. Verify generated docs exist in `docs/`
3. Run `node scripts/build-search-index.mjs` inside `site/`
4. Report: "N docs generated. Run /serve-docs to view."

**Model:** sonnet

**Tools:** Read, Glob, Bash, Skill, Write

## Commands

### /analyze \<target\>

Invokes `analysis-agent` which routes to the appropriate skill based on the target and context.

```
/analyze src/auth/          → routes to deep-functional-analysis
/analyze --architecture     → routes to system-architecture-analysis
/analyze --full             → routes to codebase-to-docs
/analyze --inventory        → routes to source-functional-analysis
```

If no flag is given, `analysis-agent` reads the target and decides.

### /gen-docs \<target\>

Invokes `doc-gen-agent` which runs `codebase-to-docs`, builds the search index, and reports results.

```
/gen-docs src/auth/
/gen-docs .                  → entire project
```

### /serve-docs

Builds the Astro site and starts the preview server.

```
/serve-docs                  → builds + serves on localhost:4321
/serve-docs --port 8080      → custom port
/serve-docs --build-only     → just builds, no serve
```

**Implementation:** Runs `npm run build && npm run preview` inside `site/`. The command handles `npm install` if `node_modules/` doesn't exist.

## Data Flow

```
User runs /gen-docs src/auth/
  → doc-gen-agent invoked
  → codebase-to-docs skill reads src/auth/
  → writes markdown to plugins/analysis/docs/
  → build-search-index.mjs reads docs/ → writes public/search-index.json
  → reports: "12 docs generated"

User runs /serve-docs
  → astro build reads site/docs/ (symlink → ../docs/)
  → generates static HTML + JS + CSS into site/dist/
  → astro preview serves on localhost:4321
  → user browses docs with search, TOC, navigation
```

## Extensibility

### Adding a new skill

1. Create `plugins/analysis/skills/new-skill/SKILL.md`
2. Update `analysis-agent.md` routing table with the new entry
3. If the skill generates docs, ensure it writes to `plugins/analysis/docs/`

### Adding a new agent

1. Create `plugins/analysis/agents/new-agent.md` with frontmatter (name, description, model, tools)
2. Create a command that invokes it, or add it to an existing command's workflow

### Adding a new command

1. Create `plugins/analysis/commands/new-command.md`
2. Wire it to invoke one or more agents/skills

## Migration Steps

1. **Move site:** Copy `docs-site-template/` contents into `plugins/analysis/site/`
2. **Create symlink:** `site/docs → ../docs`
3. **Update site.config.ts:** Brand for analysis plugin, set `docsDir` config if Astro supports it
4. **Update content.config.ts:** Ensure glob loader points to `docs/` (via symlink)
5. **Add .gitignore:** Exclude `docs/`, `site/docs/`, `site/node_modules/`, `site/dist/`, `site/.astro/`
6. **Create agents:** Write `analysis-agent.md` and `doc-gen-agent.md`
7. **Create commands:** Write `analyze.md`, `gen-docs.md`, `serve-docs.md`
8. **Update codebase-to-docs skill:** Ensure output path is `plugins/analysis/docs/`
9. **Remove docs-site-template/:** No longer needed at project root
10. **Test:** Run `/gen-docs` on a sample project, then `/serve-docs`

## Out of Scope (Future)

- Web-based CRUD for docs
- Database-backed dynamic content
- User authentication
- Multi-project doc hosting
- Auto-rebuild on file watch
