# Wiki Template Standardization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the wiki plugin from domain-based flat pages to type-based directories with templates, domain guides, and standardized frontmatter.

**Architecture:** Wiki directory reorganized by page type (sources/, entities/, concepts/, syntheses/) instead of by domain. Each page type gets its own template. Domain guides define Key Areas for entity/concept pages. Raw sources get standardized frontmatter. Ingest now produces two pages (source summary + entity/concept).

**Tech Stack:** Markdown files, YAML frontmatter, Claude Code plugin skills/agents/rules

---

## File Structure

**Create:**
- `plugins/wiki/skills/wiki-ingest/templates/raw-source.md` — raw source frontmatter template
- `plugins/wiki/skills/wiki-ingest/templates/page-source.md` — source summary page template
- `plugins/wiki/skills/wiki-ingest/templates/page-entity.md` — entity page template
- `plugins/wiki/skills/wiki-ingest/templates/page-concept.md` — concept page template
- `plugins/wiki/skills/wiki-ingest/templates/page-synthesis.md` — synthesis page template
- `plugins/wiki/skills/wiki-ingest/templates/page-overview.md` — overview page template
- `plugins/wiki/skills/wiki-ingest/templates/index-entry.md` — index entry format
- `plugins/wiki/skills/wiki-ingest/templates/log-entry.md` — log entry format
- `plugins/wiki/wiki/entities/_guides/ai-tools.md` — AI tools domain guide
- `plugins/wiki/wiki/sources/claude-code-docs.md` — source summary page (new)
- `plugins/wiki/wiki/sources/codex-docs.md` — source summary page (new)
- `plugins/wiki/wiki/sources/cursor-docs.md` — source summary page (new)
- `plugins/wiki/wiki/sources/opencode-docs.md` — source summary page (new)
- `plugins/wiki/wiki/sources/plugin-builder-docs.md` — source summary page (new)
- `plugins/wiki/wiki/overview.md` — living synthesis page (new)

**Modify:**
- `plugins/wiki/raw/ai-tools/claude-code.md` — add frontmatter
- `plugins/wiki/raw/ai-tools/codex.md` — add frontmatter
- `plugins/wiki/raw/ai-tools/cursor.md` — add frontmatter
- `plugins/wiki/raw/ai-tools/opencode.md` — add frontmatter
- `plugins/wiki/raw/ai-tools/plugin-builder.md` — add frontmatter
- `plugins/wiki/raw/llm-wiki.md` — add frontmatter
- `plugins/wiki/wiki/ai-tools/claude-code.md` → move to `wiki/entities/claude-code.md`, expand content
- `plugins/wiki/wiki/ai-tools/codex.md` → move to `wiki/entities/codex.md`, expand content
- `plugins/wiki/wiki/ai-tools/cursor.md` → move to `wiki/entities/cursor.md`, expand content
- `plugins/wiki/wiki/ai-tools/opencode.md` → move to `wiki/entities/opencode.md`, expand content
- `plugins/wiki/wiki/ai-tools/plugin-builder.md` → move to `wiki/entities/plugin-builder.md`, expand content
- `plugins/wiki/wiki/index.md` — restructure by page type
- `plugins/wiki/wiki/log.md` — append migration entry
- `plugins/wiki/CLAUDE.md` — rewrite with new architecture
- `plugins/wiki/skills/wiki-ingest/SKILL.md` — add template references
- `plugins/wiki/skills/wiki-query/SKILL.md` — add template references
- `plugins/wiki/skills/wiki-lint/SKILL.md` — add template references
- `plugins/wiki/agents/wiki-maintainer.md` — update path references
- `plugins/wiki/README.md` — update directory structure

**Delete:**
- `plugins/wiki/wiki/ai-tools/` — empty directory after migration

---

### Task 1: Create template files

**Files:**
- Create: `plugins/wiki/skills/wiki-ingest/templates/raw-source.md`
- Create: `plugins/wiki/skills/wiki-ingest/templates/page-source.md`
- Create: `plugins/wiki/skills/wiki-ingest/templates/page-entity.md`
- Create: `plugins/wiki/skills/wiki-ingest/templates/page-concept.md`
- Create: `plugins/wiki/skills/wiki-ingest/templates/page-synthesis.md`
- Create: `plugins/wiki/skills/wiki-ingest/templates/page-overview.md`
- Create: `plugins/wiki/skills/wiki-ingest/templates/index-entry.md`
- Create: `plugins/wiki/skills/wiki-ingest/templates/log-entry.md`

- [ ] **Step 1: Create raw-source.md template**

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
source_url: <URL or "local">
media: web | doc-index | file | pasted | transcript | notes
domain: <domain identifier for routing>
status: unprocessed | processed
---

# <Source Title>

<Raw source content follows. This file is immutable after creation.>
```

- [ ] **Step 2: Create page-source.md template**

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
source: raw/<path-to-source>.md
status: draft | stable | needs-update
page_type: source
---

# <Source Title>

## Summary

<One-paragraph summary of the source. What is it? What does it cover? What are the key takeaways?>

## Key Points

<Numbered or bulleted list of the most important points from the source. Aim for 5-10 points that capture the essential information.>

## Notable Details

<Specific details worth preserving: exact commands, configuration values, version-specific behavior, edge cases. Things that would be hard to reconstruct from memory alone.>

## See Also

- [Entity Page](../entities/<entity>.md) — <the entity this source describes>
```

- [ ] **Step 3: Create page-entity.md template**

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
sources:
  - wiki/sources/<source1>.md
status: draft | stable | needs-update
page_type: entity
---

# <Entity Name>

## Summary

<One-paragraph synthesis. What is this? What does it do? What's the key differentiator?>

## Key Areas

<Populate from the domain guide at `wiki/entities/_guides/<domain>.md`. Each area is a `###` subsection with 2-5 sentences of synthesized content. Omit areas that don't apply.>

## See Also

- [Related Entity](./<entity>.md) — <one-line reason for the link>
- [Source Summary](../sources/<source>.md) — <the source this was derived from>
```

- [ ] **Step 4: Create page-concept.md template**

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
sources:
  - wiki/sources/<source1>.md
status: draft | stable | needs-update
page_type: concept
---

# <Concept Name>

## Summary

<One-paragraph synthesis. What is this concept? Why does it matter? What problem does it solve?>

## Core Idea

<Explain the concept in depth. How does it work? What's the mental model? What's the key insight?>

## Applications

<Where is this applied? Concrete examples. Different contexts and how the concept manifests in each.>

## Trade-offs

<What are the limitations? When does this approach break down? What are the alternatives?>

## See Also

- [Related Concept](./<concept>.md) — <one-line reason for the link>
- [Source Summary](../sources/<source>.md) — <the source this was derived from>
```

- [ ] **Step 5: Create page-synthesis.md template**

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
sources:
  - wiki/entities/<entity1>.md
  - wiki/entities/<entity2>.md
status: draft | stable | needs-update
page_type: synthesis
synthesis_type: comparison | analysis | connection
---

# <Synthesis Title>

## Summary

<One-paragraph synthesis. What insight emerged? What connection was discovered?>

## Analysis

<The core content. For comparisons: use a table comparing key dimensions, then a verdict section. For analysis: develop the argument with evidence from source pages. For connections: explain how the pages relate and what new understanding emerges.>

## Implications

<What does this mean? What should change? What new questions does this raise?>

## See Also

- [Source Page 1](../entities/<page1>.md) — <why this source is relevant>
- [Source Page 2](../entities/<page2>.md) — <why this source is relevant>
```

- [ ] **Step 6: Create page-overview.md template**

```markdown
---
tags: [overview]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
status: draft | stable | needs-update
page_type: overview
---

# Wiki Overview

## Summary

<One-paragraph overview. What does this wiki cover? What's the big picture? What's the evolving thesis?>

## Domains

<For each domain, a 2-3 sentence summary of what's covered and the key insights so far. Link to the most important entity and concept pages.>

## Active Questions

<What are you currently investigating? What questions are open? What contradictions have been flagged?>

## Recent Activity

<Last 3-5 log entries, summarized. Gives context for what's been happening.>

## See Also

- [Index](./index.md) — full page catalog
- [Log](./log.md) — chronological activity record
```

- [ ] **Step 7: Create index-entry.md template**

```markdown
- [<Page Title>](<type-dir>/<page-name>.md) — <one-line summary>
```

- [ ] **Step 8: Create log-entry.md template**

```markdown
## [YYYY-MM-DD] <operation> | <Title>

<What was done. Which pages were created/updated. Which cross-references were added.>
```

- [ ] **Step 9: Commit**

```bash
git add plugins/wiki/skills/wiki-ingest/templates/
git commit -m "feat(wiki): add template files for all page types and operational documents"
```

---

### Task 2: Create domain guide and new wiki directories

**Files:**
- Create: `plugins/wiki/wiki/entities/_guides/ai-tools.md`
- Create: `plugins/wiki/wiki/sources/` (directory)
- Create: `plugins/wiki/wiki/concepts/` (directory)
- Create: `plugins/wiki/wiki/syntheses/` (directory)

- [ ] **Step 1: Create the ai-tools domain guide**

```markdown
# Domain Guide: ai-tools

## Key Areas for Entity Pages

### Overview
What is this tool? Who makes it? What problem does it solve? What's the primary interface (CLI/editor/IDE)?

### Configuration
How is it configured? Config file format and location. Key settings. Environment variables.

### Agent Features
What extensibility features exist? Skills, hooks, MCP, plugins, sub-agents, custom tools. How do they work?

### Permissions & Security
Permission model: modes, granularity, sandboxing. How are permissions configured?

### Integrations
IDE extensions, CI/CD, web, desktop, third-party integrations.

### Troubleshooting
Common issues, debugging, error reference.

## Notes
- Omit areas that don't apply to a specific tool
- The Overview area is always present
```

- [ ] **Step 2: Create empty directories with .gitkeep**

```bash
mkdir -p plugins/wiki/wiki/sources plugins/wiki/wiki/concepts plugins/wiki/wiki/syntheses
touch plugins/wiki/wiki/sources/.gitkeep plugins/wiki/wiki/concepts/.gitkeep plugins/wiki/wiki/syntheses/.gitkeep
```

- [ ] **Step 3: Commit**

```bash
git add plugins/wiki/wiki/entities/_guides/ai-tools.md plugins/wiki/wiki/sources/.gitkeep plugins/wiki/wiki/concepts/.gitkeep plugins/wiki/wiki/syntheses/.gitkeep
git commit -m "feat(wiki): add ai-tools domain guide and type-based directory structure"
```

---

### Task 3: Add frontmatter to raw sources

**Files:**
- Modify: `plugins/wiki/raw/ai-tools/claude-code.md`
- Modify: `plugins/wiki/raw/ai-tools/codex.md`
- Modify: `plugins/wiki/raw/ai-tools/cursor.md`
- Modify: `plugins/wiki/raw/ai-tools/opencode.md`
- Modify: `plugins/wiki/raw/ai-tools/plugin-builder.md`
- Modify: `plugins/wiki/raw/llm-wiki.md`

- [ ] **Step 1: Add frontmatter to claude-code.md**

Prepend to file (keep all existing content below):

```yaml
---
tags: [ai-tools, cli, coding]
date: 2026-05-22
source_url: https://code.claude.com/docs/
media: doc-index
domain: ai-tools
status: processed
---
```

- [ ] **Step 2: Add frontmatter to codex.md**

Prepend to file:

```yaml
---
tags: [ai-tools, cli, coding]
date: 2026-05-22
source_url: https://developers.openai.com/codex
media: doc-index
domain: ai-tools
status: processed
---
```

- [ ] **Step 3: Add frontmatter to cursor.md**

Prepend to file:

```yaml
---
tags: [ai-tools, editor, coding]
date: 2026-05-22
source_url: https://cursor.com/docs
media: doc-index
domain: ai-tools
status: processed
---
```

- [ ] **Step 4: Add frontmatter to opencode.md**

Prepend to file:

```yaml
---
tags: [ai-tools, cli, coding]
date: 2026-05-22
source_url: https://opencode.ai/docs/
media: doc-index
domain: ai-tools
status: processed
---
```

- [ ] **Step 5: Add frontmatter to plugin-builder.md**

Prepend to file:

```yaml
---
tags: [ai-tools, plugins, coding]
date: 2026-05-22
source_url: https://code.claude.com/docs/en/plugins-reference.md
media: doc-index
domain: ai-tools
status: processed
---
```

- [ ] **Step 6: Add frontmatter to llm-wiki.md**

Prepend to file:

```yaml
---
tags: [pattern, knowledge-base]
date: 2026-05-22
source_url: local
media: pasted
domain: llm-wiki
status: processed
---
```

- [ ] **Step 7: Commit**

```bash
git add plugins/wiki/raw/
git commit -m "feat(wiki): add standardized frontmatter to all raw sources"
```

---

### Task 4: Migrate wiki pages from ai-tools/ to entities/

**Files:**
- Create: `plugins/wiki/wiki/entities/claude-code.md` (from `wiki/ai-tools/claude-code.md`)
- Create: `plugins/wiki/wiki/entities/codex.md` (from `wiki/ai-tools/codex.md`)
- Create: `plugins/wiki/wiki/entities/cursor.md` (from `wiki/ai-tools/cursor.md`)
- Create: `plugins/wiki/wiki/entities/opencode.md` (from `wiki/ai-tools/opencode.md`)
- Create: `plugins/wiki/wiki/entities/plugin-builder.md` (from `wiki/ai-tools/plugin-builder.md`)
- Delete: `plugins/wiki/wiki/ai-tools/` (after migration)

- [ ] **Step 1: Move claude-code.md and update frontmatter + cross-references**

Move file from `wiki/ai-tools/claude-code.md` to `wiki/entities/claude-code.md`. Update:
- Add `last_updated: 2026-05-22`, `page_type: entity` to frontmatter
- Change `sources` paths from `raw/ai-tools/claude-code.md` to `wiki/sources/claude-code-docs.md`
- Update See Also links: `[Codex](./codex.md)` → `[Codex](./codex.md)` (same directory, no change needed)
- Update See Also links that referenced other domains: `[OpenCode](./opencode.md)` → `[OpenCode](./opencode.md)` (same directory)

- [ ] **Step 2: Move codex.md and update frontmatter + cross-references**

Move file from `wiki/ai-tools/codex.md` to `wiki/entities/codex.md`. Same updates as Step 1 pattern.

- [ ] **Step 3: Move cursor.md and update frontmatter + cross-references**

Move file from `wiki/ai-tools/cursor.md` to `wiki/entities/cursor.md`. Same updates as Step 1 pattern.

- [ ] **Step 4: Move opencode.md and update frontmatter + cross-references**

Move file from `wiki/ai-tools/opencode.md` to `wiki/entities/opencode.md`. Same updates as Step 1 pattern.

- [ ] **Step 5: Move plugin-builder.md and update frontmatter + cross-references**

Move file from `wiki/ai-tools/plugin-builder.md` to `wiki/entities/plugin-builder.md`. Same updates as Step 1 pattern.

- [ ] **Step 6: Delete empty wiki/ai-tools/ directory**

```bash
rm -rf plugins/wiki/wiki/ai-tools/
```

- [ ] **Step 7: Commit**

```bash
git add plugins/wiki/wiki/entities/ plugins/wiki/wiki/ai-tools/
git commit -m "feat(wiki): migrate wiki pages from domain-based to type-based directory structure"
```

---

### Task 5: Create source summary pages

**Files:**
- Create: `plugins/wiki/wiki/sources/claude-code-docs.md`
- Create: `plugins/wiki/wiki/sources/codex-docs.md`
- Create: `plugins/wiki/wiki/sources/cursor-docs.md`
- Create: `plugins/wiki/wiki/sources/opencode-docs.md`
- Create: `plugins/wiki/wiki/sources/plugin-builder-docs.md`

Each source summary page follows the `page-source.md` template. Content is derived from the corresponding raw source file. This task requires reading each raw source and synthesizing a summary.

- [ ] **Step 1: Create claude-code-docs.md**

Read `raw/ai-tools/claude-code.md` and create source summary. Remove `.gitkeep` after first file is created.

- [ ] **Step 2: Create codex-docs.md**

Read `raw/ai-tools/codex.md` and create source summary.

- [ ] **Step 3: Create cursor-docs.md**

Read `raw/ai-tools/cursor.md` and create source summary.

- [ ] **Step 4: Create opencode-docs.md**

Read `raw/ai-tools/opencode.md` and create source summary.

- [ ] **Step 5: Create plugin-builder-docs.md**

Read `raw/ai-tools/plugin-builder.md` and create source summary.

- [ ] **Step 6: Delete .gitkeep**

```bash
rm plugins/wiki/wiki/sources/.gitkeep
```

- [ ] **Step 7: Commit**

```bash
git add plugins/wiki/wiki/sources/
git commit -m "feat(wiki): create source summary pages for all raw sources"
```

---

### Task 6: Expand entity page content

**Files:**
- Modify: `plugins/wiki/wiki/entities/claude-code.md`
- Modify: `plugins/wiki/wiki/entities/codex.md`
- Modify: `plugins/wiki/wiki/entities/cursor.md`
- Modify: `plugins/wiki/wiki/entities/opencode.md`
- Modify: `plugins/wiki/wiki/entities/plugin-builder.md`

Each entity page currently has one-line Key Areas. Expand to 2-5 sentences per area using the ai-tools domain guide prompts. This requires re-reading the raw source and synthesizing richer content.

- [ ] **Step 1: Expand claude-code.md Key Areas**

Read `raw/ai-tools/claude-code.md` and the ai-tools domain guide. Rewrite each Key Area subsection with 2-5 sentences of synthesized content.

- [ ] **Step 2: Expand codex.md Key Areas**

Same process for codex.

- [ ] **Step 3: Expand cursor.md Key Areas**

Same process for cursor.

- [ ] **Step 4: Expand opencode.md Key Areas**

Same process for opencode.

- [ ] **Step 5: Expand plugin-builder.md Key Areas**

Same process for plugin-builder.

- [ ] **Step 6: Commit**

```bash
git add plugins/wiki/wiki/entities/
git commit -m "feat(wiki): expand entity page Key Areas with synthesized content from domain guide"
```

---

### Task 7: Create overview.md

**Files:**
- Create: `plugins/wiki/wiki/overview.md`

- [ ] **Step 1: Create overview.md following page-overview.md template**

Write the overview by synthesizing across all existing wiki pages. The Domains section should cover the ai-tools domain. Active Questions and Recent Activity can start sparse.

- [ ] **Step 2: Commit**

```bash
git add plugins/wiki/wiki/overview.md
git commit -m "feat(wiki): create initial overview.md living synthesis page"
```

---

### Task 8: Update index.md and log.md

**Files:**
- Modify: `plugins/wiki/wiki/index.md`
- Modify: `plugins/wiki/wiki/log.md`

- [ ] **Step 1: Rewrite index.md with type-based organization**

```markdown
# Wiki Index

## Sources

- [Claude Code Docs](sources/claude-code-docs.md) — Claude Code official documentation index
- [Codex Docs](sources/codex-docs.md) — OpenAI Codex CLI documentation index
- [Cursor Docs](sources/cursor-docs.md) — Cursor AI editor documentation index
- [OpenCode Docs](sources/opencode-docs.md) — OpenCode CLI documentation index
- [Plugin Builder Docs](sources/plugin-builder-docs.md) — Claude Code plugin reference documentation index

## Entities

- [Claude Code](entities/claude-code.md) — Anthropic's official CLI for Claude
- [Codex](entities/codex.md) — OpenAI's autonomous coding agent
- [Cursor](entities/cursor.md) — AI-first code editor built on VS Code
- [OpenCode](entities/opencode.md) — Open-source CLI for AI coding
- [Plugin Builder](entities/plugin-builder.md) — Claude Code plugin system

## Concepts

## Syntheses
```

- [ ] **Step 2: Append migration entry to log.md**

```markdown
## [2026-05-22] migration | Wiki Template Standardization

Restructured wiki from domain-based directories (wiki/ai-tools/) to type-based directories (sources/, entities/, concepts/, syntheses/). Added frontmatter to all raw sources. Created source summary pages. Expanded entity page content. Created overview.md. Created ai-tools domain guide.
```

- [ ] **Step 3: Commit**

```bash
git add plugins/wiki/wiki/index.md plugins/wiki/wiki/log.md
git commit -m "feat(wiki): update index and log for type-based directory structure"
```

---

### Task 9: Update skill files

**Files:**
- Modify: `plugins/wiki/skills/wiki-ingest/SKILL.md`
- Modify: `plugins/wiki/skills/wiki-query/SKILL.md`
- Modify: `plugins/wiki/skills/wiki-lint/SKILL.md`

- [ ] **Step 1: Update wiki-ingest/SKILL.md**

Current step 3 ("Save the raw source"):
- Add: "Save the raw source following the format in `templates/raw-source.md`"

Current step 4 ("Write the wiki page"):
- Replace the entire step with: "Write the wiki pages. Ingest produces two pages: (1) a source summary page in `wiki/sources/` following `templates/page-source.md`, and (2) an entity or concept page. Determine entity vs concept based on source content — entity for a specific thing (tool, person, project), concept for an abstract idea or pattern. For entity pages, follow `templates/page-entity.md` and read the domain guide at `wiki/entities/_guides/<domain>.md` for Key Areas. For concept pages, follow `templates/page-concept.md`. If no domain guide exists, create areas from the source's natural structure and consider creating a guide for future sources."

Current step 5 ("Update the index"):
- Add: "following the format in `templates/index-entry.md`"

Current step 6 ("Update affected pages"):
- Add after: "Update the overview (`wiki/overview.md`) following `templates/page-overview.md`"

Current step 7 ("Append to the log"):
- Add: "following the format in `templates/log-entry.md`"

- [ ] **Step 2: Update wiki-query/SKILL.md**

Current step 5 ("File substantial answers"):
- Replace with: "File substantial answers as new wiki pages in `wiki/syntheses/` following `templates/page-synthesis.md`. Set `synthesis_type` based on the answer: `comparison` for side-by-side analysis, `analysis` for deep dives, `connection` for newly discovered relationships. Only file substantial answers — not simple lookups. Update the index with the new page."

- [ ] **Step 3: Update wiki-lint/SKILL.md**

Add to step 5 (or as a new step if applying fixes): "When creating or updating pages, follow the appropriate page-type template in `templates/`. For entity/concept pages, also read the relevant domain guide."

- [ ] **Step 4: Commit**

```bash
git add plugins/wiki/skills/
git commit -m "feat(wiki): update skill files to reference templates and domain guides"
```

---

### Task 10: Update CLAUDE.md, README.md, and wiki-maintainer agent

**Files:**
- Modify: `plugins/wiki/CLAUDE.md`
- Modify: `plugins/wiki/README.md`
- Modify: `plugins/wiki/agents/wiki-maintainer.md`

- [ ] **Step 1: Rewrite CLAUDE.md**

Replace the entire file with content reflecting the new architecture. Key sections:
- What This Plugin Is (unchanged)
- Human / LLM role split (unchanged)
- Three-Layer Architecture — updated: raw/ immutable, wiki/ type-based directories (sources/, entities/, concepts/, syntheses/), CLAUDE.md as schema layer
- Page Types — table of types, directories, when created, purpose
- Key Files — index.md, log.md, overview.md
- Wiki Page Format — frontmatter fields including last_updated, page_type; Summary, Key Areas, See Also sections
- Raw Source Format — frontmatter fields: tags, date, source_url, media, domain, status
- Templates — list all template files and their purpose
- Domain Guides — _guides/<domain>.md, not listed in index
- Operations — updated ingest (produces two pages), query (files syntheses), lint
- Naming Conventions (unchanged)
- Index Format — type-based sections
- Log Format (unchanged)
- Cross-references — updated paths (../entities/, ../sources/, etc.)
- Agent Delegation (unchanged)
- Conventions (unchanged)

- [ ] **Step 2: Update README.md directory structure**

Update the directory tree to reflect type-based wiki structure:
```
wiki/
  index.md        # Catalog of all pages
  log.md          # Append-only chronological record
  overview.md     # Living synthesis across all sources
  sources/        # One summary page per source document
  entities/       # People, companies, projects, products
  concepts/       # Ideas, frameworks, methods, theories
  syntheses/      # Saved query answers
```

- [ ] **Step 3: Update wiki-maintainer agent**

Update all path references:
- `wiki/ai-tools/` → `wiki/entities/`
- "domain directory" → "type-based directory (sources/, entities/, concepts/, syntheses/)"
- Add reference to templates and domain guides
- "Read CLAUDE.md for wiki conventions" — keep this

- [ ] **Step 4: Commit**

```bash
git add plugins/wiki/CLAUDE.md plugins/wiki/README.md plugins/wiki/agents/wiki-maintainer.md
git commit -m "feat(wiki): update CLAUDE.md, README, and agent for new directory structure"
```

---

## Self-Review

**1. Spec coverage:**
- Raw source frontmatter (tags, date, source_url, media, domain, status) → Task 3
- Wiki page frontmatter (tags, date, last_updated, sources, status, page_type) → Tasks 4, 5, 6, 7
- Page-type templates (source, entity, concept, synthesis, overview) → Task 1
- Operational templates (raw-source, index-entry, log-entry) → Task 1
- Domain guides → Task 2
- Type-based directory structure → Tasks 2, 4
- Ingest produces two pages → Task 9 (skill update)
- Migration of existing files → Tasks 3, 4, 5, 6, 7, 8
- Skill file updates → Task 9
- CLAUDE.md updates → Task 10

**2. Placeholder scan:** All template content is complete. No TBD/TODO.

**3. Type consistency:**
- `media` field used consistently (not `type`) in raw sources
- `page_type` field matches template names (source, entity, concept, synthesis, overview)
- `synthesis_type` values (comparison, analysis, connection) consistent between template and query skill
- Cross-reference paths use `../entities/`, `../sources/` consistently
- `last_updated` added to all wiki page frontmatter in templates and migration steps
