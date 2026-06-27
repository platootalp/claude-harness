# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A Claude Code plugin marketplace (`harness-marketplace`) that distributes development workflow tools. Users add the marketplace and install individual plugins. This repo contains the marketplace definition and all plugin source code.

## Repo Structure

```
.claude-plugin/marketplace.json   # Marketplace registry — lists all plugins with name + source path
plugins/                           # Active plugin packages
  superpowers-pro/                 # Structured development workflows (pure markdown, no build step)
  kb/                              # Knowledge base management (ETL pipeline + Astro site)
  self-evolution/                  # Auto-extract skills from conversations (TypeScript runtime)
other/                             # Previously removed plugins kept for reference
  analysis/                        # Codebase analysis skills + Astro docs site + embedded office plugin
  coding/                          # Coding, testing, and skill-authoring skills (22 total)
  wiki/                            # Wiki ingest/query/lint skills + raw wiki data
docs/                              # Internal specs and plans (not shipped)
```

## Marketplace Registry

`marketplace.json` 注册 3 个活跃插件：

| Plugin | marketplace.json source | 状态 |
|--------|------------------------|------|
| **superpowers-pro** | `./plugins/superpowers-pro` | 活跃 |
| **kb** | `./plugins/kb` | 活跃 |
| **self-evolution** | `./plugins/self-evolution` | 活跃 |

旧插件（analysis, coding, office, interview, wiki）已移至 `other/` 保留源码，但未在 marketplace 注册。修改 marketplace.json 或移动插件目录时，必须保持两者一致。

## Build & Test Commands

### self-evolution (only plugin with a build step)

```bash
cd plugins/self-evolution
npm install
npm run build          # esbuild bundle → dist/runtime.mjs
npm test               # vitest run (all 20 tests, single-fork mode)
npx vitest run src/__tests__/security-scan.test.ts  # single test file
```

### kb site

```bash
cd plugins/kb/site
npm install
npm run setup          # symlinks data-raw and data-wiki from sibling data/
npm run dev            # Astro dev server
```

### superpowers-pro (pure markdown, no build)

No build step. Skills and hooks are markdown/bash files loaded directly by Claude Code.

### Marketplace validation

```bash
claude plugin validate .
```

### Local plugin testing

```bash
claude --plugin-dir ./plugins/superpowers-pro
claude --plugin-dir ./plugins/kb
claude --plugin-dir ./plugins/self-evolution
```

## Active Plugin: superpowers-pro

18 skills + 4 commands (`/feat`, `/fix`, `/init`, `/refactor`) covering structured development workflows.

| Category | Skills |
|----------|--------|
| Workflow entry | using-superpowers (injected on session start), brainstorming |
| Planning | writing-plans, executing-plans, system-architect, prd-generator |
| Development | test-driven-development, subagent-driven-development |
| Git | using-git-worktrees, finishing-a-development-branch |
| Review | requesting-code-review, receiving-code-review |
| Debugging | systematic-debugging, issue-scanning |
| Meta | writing-skills, dispatching-parallel-agents, verification-before-completion, variables, refactor-assessment |

The `session-start` hook (`hooks/session-start`) reads `skills/using-superpowers/SKILL.md` and `.claude-plugin/variables.json`, then injects them as context. The hook script is platform-aware (Claude Code / Cursor / Copilot CLI) and uses `printf` instead of heredoc (workaround for bash 5.3+ hang, issue #571). `run-hook.cmd` is a cross-platform polyglot wrapper (batch + bash in one file).

**Variables system**: `variables.json` defines user-configurable settings (e.g., `finish-mode: auto|interactive`, `review-mode: section-by-section|full`) that the session-start hook injects into context.

**Eval scripts**: `skills/finishing-a-development-branch/evals/` contains 6 bash eval scripts testing merge logic, PR/MR URL derivation, and fallback behavior. Each creates a temp git repo, runs logic under test, asserts output.

## Active Plugin: kb

ETL 管道：Extract → Transform → Load/Present。13 skills, 2 agents, 1 command (`/kb`)。

| Phase | Skills | Agents |
|-------|--------|--------|
| Extract | scan, extract (路由), extract-topology, extract-api, extract-data-model, extract-flows, extract-concepts | extract-agent (单维度) |
| Transform | transform (路由), ingest, cross-ref | transform-agent (单维度) |
| Load | build-search-index, build-graph, serve | — |

站点：`plugins/kb/site/`（Astro 6 + React 18 + d3-force + Fuse.js），三视图（Raw/Wiki/Graph）+ 搜索 + 知识图谱。Build pipeline: `build-search-index.mjs` → `build-graph-data.mjs` → `astro build`。

## Active Plugin: self-evolution

TypeScript runtime that auto-extracts reusable workflows from conversations and generates skills. Companion-mode: Stop hook spawns detached `claude -p` process running the skill-reviewer pipeline.

### Architecture

```
src/
├── runtime.ts          # Command router — all CLI commands pass through here
├── types.ts            # Shared TypeScript interfaces
├── commands/           # 12 command handlers (session-start, post-tool-use, stop-gate, security-scan, review-context, log-decision, status, validate-skill, verify-skill, delete-skill, config-get, config-set)
└── lib/
    ├── adapter.ts      # Platform detection + adapter factory
    ├── adapters/       # claude-code.ts, codex.ts, cursor.ts
    ├── config.ts       # Config loading, env var overrides (SELF_EVOLUTION_ prefix), schema validation
    ├── logger.ts       # JSONL session logger
    ├── security.ts     # Pattern-based content scanner (injection, dangerous bash, secrets, base64)
    ├── spawner.ts      # Companion process spawning + prompt variant selection
    ├── state.ts        # State persistence (sessions, jobs)
    └── transcript.ts   # Transcript parsing + summary
```

**Hook flow**: `PostToolUse` → increment counter → set `pending_review` at nudge threshold → `Stop` hook → consume `pending_review` → spawn detached companion → reviewer pipeline. The `post-tool-use` and `stop-gate` commands read hook input from **stdin** (not CLI args).

**Multi-platform**: Three `PlatformAdapter` implementations (Claude Code, Codex, Cursor). Detection priority: `CLAUDE_PLUGIN_ROOT` → `CODEX_SESSION_ID` → `CURSOR_PROJECT_DIR` → manifest directory check → default claude-code. All share the same `dist/runtime.mjs` bundle.

**Security model**: `security-scan` enforces path whitelist (only skill dirs writable), content scanning (injection, dangerous bash, secrets, base64, binary extensions), and size/count limits. Scanning happens inside the reviewer agent flow, not via global PreToolUse hook.

**Data locations**: Plugin data at `~/.claude/plugins/data/self-evolution-self-evolution-marketplace/` (sessions/, stats.json, state.json).

## Adding a Skill to superpowers-pro

Create `plugins/superpowers-pro/skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`) and markdown body. Skills can include `references/`, `templates/`, `scripts/`, and `evals/` subdirectories.

## Adding a New Plugin

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`
2. Add skills to `plugins/<name>/skills/`
3. Register in `.claude-plugin/marketplace.json` under `plugins` array
4. Validate: `claude plugin validate .`

## Key Conventions

- All plugin content is markdown — agents, commands, rules, and skills are `.md` files
- Skills use `SKILL.md` as the entry point with YAML frontmatter (`name`, `description` fields minimum)
- **文档语言：** 所有文档（设计文档、spec、CHANGELOG、README 等）均使用中文编写
- **Version control (SemVer):** Every plugin change must update `version` in `.claude-plugin/plugin.json`
  - **Patch**: bug fix, doc correction, minor adjustment
  - **Minor**: new skill/agent/command/rule, feature enhancement
  - **Major**: breaking changes
- **Changelog:** On every plugin content change, simultaneously: (1) update `plugin.json` version, (2) add entry under `[Unreleased]` in the plugin's `CHANGELOG.md`; each plugin versions independently
- **Worktree isolation:** 所有功能开发使用隔离 worktree，测试通过后合并到主分支
