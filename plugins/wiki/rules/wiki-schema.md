---
name: wiki-schema
description: Wiki conventions and structure — loaded into every session so the agent knows how the wiki works
---

# Wiki Schema

## Directory Layout

```
plugins/wiki/
  raw/          # Immutable source documents — READ ONLY, never modify
  wiki/         # LLM-generated pages — LLM writes, human reads
    index.md    # Content catalog (one line per page with link + summary)
    log.md      # Chronological activity log (append-only)
```

Source documents go in subdirectories under `raw/` by domain (e.g. `raw/ai-tools/`). Wiki pages mirror the same subdirectory structure under `wiki/`.

## Page Format

Every wiki page uses this structure:

```
---
tags: [tag1, tag2]
date: YYYY-MM-DD
sources:
  - raw/path/to/source.md
status: draft | stable | needs-update
---

# Page Title

## Summary

One-paragraph synthesis of the topic.

## Details

Full content with sections, cross-references, and citations.

## See Also

- [Related Page](./other-page.md)
```

## Cross-Reference Style

Use relative markdown links: `[Page Title](./page-name.md)`. For pages in other domains: `[Page Title](../other-domain/page-name.md)`.

## Naming Conventions

- File names: kebab-case (e.g. `claude-code.md`, `plugin-builder.md`)
- Domain folders under `raw/` and `wiki/`: kebab-case (e.g. `ai-tools/`)
- One page per concept/entity; merge related topics rather than splitting

## Index Format

`wiki/index.md` catalogs every wiki page:

```
# Wiki Index

## Domain: ai-tools

- [Claude Code](ai-tools/claude-code.md) — Claude Code CLI features, config, skills, hooks, MCP
- [Cursor](ai-tools/cursor.md) — Cursor AI editor features, CLI, hooks, MCP
```

Update index on every ingest.

## Log Format

`wiki/log.md` is append-only:

```
## [2026-05-22] ingest | Claude Code Documentation

Added Claude Code reference as raw source. Created wiki page with 12 sections. Updated index.

## [2026-05-22] lint | Full Wiki Health Check

Found 2 orphan pages, 1 stale claim. Fixed all issues.
```

## Operation Cheat Sheet

**Ingest**: Read source → Discuss with user → Write wiki page → Update index → Update affected pages → Append to log

**Query**: Read index → Find relevant pages → Read pages → Read raw sources if needed → Synthesize answer → Offer to file as new page

**Lint**: Scan for contradictions/stale claims/orphans/missing cross-references → Check index completeness → Suggest fixes → Apply approved fixes → Append to log
