# Wiki Template Standardization Design

## Problem

Raw source documents and wiki pages lack standardized structure and sufficient content:

- **Raw sources** have no frontmatter — the agent cannot determine source type, origin, or domain without reading the content
- **Wiki pages** have Key Areas that are one-line summaries instead of synthesized content
- **Wiki pages are all treated as one type** — but the LLM Wiki pattern produces multiple page types (sources, entities, concepts, syntheses), each with a different structure
- **Wiki directory is organized by domain** (`wiki/ai-tools/`) — but the natural organizing dimension is page type, not domain. An entity page and a synthesis page about the same domain have completely different structures
- **Key Areas are domain-specific** — the current pages use AI-tool-specific areas (Configuration, Agent Features, Permissions) that make no sense for other domains
- **Index and log** formats are defined in CLAUDE.md but not available as copy-paste templates for the agent

## Approach

Three changes:

1. **Restructure wiki directory by page type** — `sources/`, `entities/`, `concepts/`, `syntheses/` subdirectories, plus top-level `overview.md`, `index.md`, `log.md`
2. **Page-type templates** — each page type has its own template with the appropriate structure
3. **Domain guides** — each domain defines its own Key Areas for entity and concept pages

## New Wiki Directory Structure

```
wiki/
  index.md        # Catalog of all pages — update on every ingest
  log.md          # Append-only chronological record
  overview.md     # Living synthesis across all sources
  sources/        # One summary page per source document
  entities/       # People, companies, projects, products
  concepts/       # Ideas, frameworks, methods, theories
  syntheses/      # Saved query answers
```

Pages are organized by **type**, not by domain. Domain is expressed through frontmatter tags and the domain guide system. This means:

- `wiki/entities/claude-code.md` — entity page about Claude Code
- `wiki/entities/cursor.md` — entity page about Cursor
- `wiki/concepts/llm-wiki.md` — concept page about the LLM Wiki pattern
- `wiki/syntheses/claude-code-vs-cursor.md` — comparison synthesis
- `wiki/sources/claude-code-docs.md` — source summary for the Claude Code docs

Cross-references use relative paths across directories: `[Claude Code](../entities/claude-code.md)`.

The `overview.md` is a living document that synthesizes across all sources. It's the highest-level page in the wiki — read it to understand the big picture, drill down into entities/concepts/syntheses for detail.

## Page Types

| Type | Directory | When Created | Purpose |
|------|-----------|-------------|---------|
| **source** | `sources/` | Ingest | Summary of one raw source document |
| **entity** | `entities/` | Ingest (source about a specific thing) | Structured knowledge about one entity |
| **concept** | `concepts/` | Ingest (source about an abstract idea) | Structured knowledge about one concept |
| **synthesis** | `syntheses/` | Query answer filed back | New insight connecting multiple pages |
| **overview** | top-level `overview.md` | Updated on every ingest | Living synthesis across all sources |

Note: comparison is a sub-type of synthesis — a comparison page lives in `syntheses/` and uses the comparison template.

## Template Files

### 1. `skills/wiki-ingest/templates/raw-source.md`

```yaml
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
source_url: <URL or "local">
media: web | doc-index | file | pasted | transcript | notes
domain: <domain identifier for routing>
status: unprocessed | processed
---
```

Fields:
- `tags` — list of tags for categorization (aligned with wiki page frontmatter)
- `date` — date the source was collected (aligned with wiki page `date`)
- `source_url` — origin URL, or `"local"` for non-web sources
- `media` — how the source was acquired and what form it takes:
  - `web` — full content fetched from a URL (e.g. article clipped via Obsidian Web Clipper)
  - `doc-index` — a URL index pointing to documentation pages (links, not content)
  - `file` — a local file provided by the user
  - `pasted` — text pasted directly by the user
  - `transcript` — meeting transcript, Slack thread, interview recording
  - `notes` — handwritten notes, journal entry, personal observation
- `domain` — domain identifier for routing and domain guide lookup (e.g. `ai-tools`, `research`, `reading`)
- `status` — `unprocessed` (not yet ingested) or `processed` (ingested, wiki pages created). Aligned with wiki page `status` convention.

The body after frontmatter is free-form — the raw source is immutable and its content structure is not constrained.

### 2. `skills/wiki-ingest/templates/page-source.md`

One summary page per source document. Created during ingest as the first wiki artifact from a raw source.

```yaml
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

### 3. `skills/wiki-ingest/templates/page-entity.md`

For pages about a specific thing — a tool, a person, a project, an organization.

```yaml
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

### 4. `skills/wiki-ingest/templates/page-concept.md`

For pages about an abstract idea, pattern, or methodology.

```yaml
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

### 5. `skills/wiki-ingest/templates/page-synthesis.md`

For pages that represent a new insight connecting knowledge from multiple pages — typically filed from a query answer. Comparison pages are a sub-type.

```yaml
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

The `synthesis_type` field distinguishes:
- `comparison` — side-by-side analysis of two or more entities/concepts
- `analysis` — deep dive into a single topic drawing from multiple sources
- `connection` — a newly discovered relationship between seemingly unrelated pages

### 6. `skills/wiki-ingest/templates/page-overview.md`

The top-level living synthesis. Updated on every ingest. There is only one `overview.md` at the wiki root.

```yaml
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

### 7. Domain Guides: `wiki/entities/_guides/<domain>.md`

Each domain has a guide that defines the Key Areas for entity pages in that domain. Guides live under `entities/` because they only apply to entity (and concept) page types — synthesis, source, and overview pages have their own fixed structures.

**Example: `wiki/entities/_guides/ai-tools.md`**

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

**Example: `wiki/entities/_guides/research.md`** (future domain)

```markdown
# Domain Guide: research

## Key Areas for Entity Pages

### Thesis
What is the central argument or finding? What question does this work address?

### Methodology
What approach was used? Study design, data sources, analytical methods.

### Key Findings
What were the main results? Quantitative data, qualitative insights.

### Limitations
What are the known weaknesses? Sample size, scope, assumptions.

### Related Work
How does this connect to other work in the field? Agreements, contradictions, extensions.

## Notes
- For literature reviews, merge findings across sources under each area
- For single papers, focus on extraction accuracy
```

The `_guides/` prefix convention makes these clearly meta-files. They are not listed in `wiki/index.md`.

### 8. `skills/wiki-ingest/templates/index-entry.md`

```markdown
- [<Page Title>](<type-dir>/<page-name>.md) — <one-line summary>
```

Note the path now includes the type directory (`sources/`, `entities/`, `concepts/`, `syntheses/`).

### 9. `skills/wiki-ingest/templates/log-entry.md`

```markdown
## [YYYY-MM-DD] <operation> | <Title>

<What was done. Which pages were created/updated. Which cross-references were added.>
```

## Skill Changes

### wiki-ingest

- Step 3: "Save the raw source following `templates/raw-source.md`"
- Step 4: "Write the wiki pages. Ingest produces two pages: (1) a source summary page in `wiki/sources/` following `templates/page-source.md`, and (2) an entity or concept page following `templates/page-entity.md` or `templates/page-concept.md`. Determine entity vs concept based on the source content. For entity pages, read the domain guide at `wiki/entities/_guides/<domain>.md` for Key Areas. If no guide exists, create areas from the source's natural structure and consider creating a guide for future sources."
- Step 5: "Update the index following `templates/index-entry.md`"
- Step 6: "Update the overview following `templates/page-overview.md`"
- Step 7: "Append to the log following `templates/log-entry.md`"

### wiki-query

- Step 5: "File substantial answers as new wiki pages in `wiki/syntheses/` following `templates/page-synthesis.md`. Set `synthesis_type` based on the answer: comparison, analysis, or connection."

### wiki-lint

- Step 5: "When creating/updating pages, follow the appropriate page-type template."

## Migration

### Raw sources (6 files)

Add frontmatter to each existing raw source:

| File | tags | source_url | media | domain | status |
|------|------|-----------|-------|--------|--------|
| `raw/ai-tools/claude-code.md` | `[ai-tools, cli, coding]` | `https://code.claude.com/docs/` | `doc-index` | `ai-tools` | `processed` |
| `raw/ai-tools/codex.md` | `[ai-tools, cli, coding]` | `https://developers.openai.com/codex` | `doc-index` | `ai-tools` | `processed` |
| `raw/ai-tools/cursor.md` | `[ai-tools, editor, coding]` | `https://cursor.com/docs` | `doc-index` | `ai-tools` | `processed` |
| `raw/ai-tools/opencode.md` | `[ai-tools, cli, coding]` | `https://opencode.ai/docs/` | `doc-index` | `ai-tools` | `processed` |
| `raw/ai-tools/plugin-builder.md` | `[ai-tools, plugins, coding]` | `https://code.claude.com/docs/en/plugins-reference.md` | `doc-index` | `ai-tools` | `processed` |
| `raw/llm-wiki.md` | `[pattern, knowledge-base]` | `local` | `pasted` | `llm-wiki` | `processed` |

### Restructure wiki directory

Move existing pages from `wiki/ai-tools/` to type-based directories:

| Current | New Location | page_type |
|---------|-------------|-----------|
| `wiki/ai-tools/claude-code.md` | `wiki/entities/claude-code.md` | entity |
| `wiki/ai-tools/codex.md` | `wiki/entities/codex.md` | entity |
| `wiki/ai-tools/cursor.md` | `wiki/entities/cursor.md` | entity |
| `wiki/ai-tools/opencode.md` | `wiki/entities/opencode.md` | entity |
| `wiki/ai-tools/plugin-builder.md` | `wiki/entities/plugin-builder.md` | entity |

Create new pages:

| New Page | page_type |
|----------|-----------|
| `wiki/sources/claude-code-docs.md` | source |
| `wiki/sources/codex-docs.md` | source |
| `wiki/sources/cursor-docs.md` | source |
| `wiki/sources/opencode-docs.md` | source |
| `wiki/sources/plugin-builder-docs.md` | source |
| `wiki/overview.md` | overview |

Create domain guide: `wiki/entities/_guides/ai-tools.md`

Delete empty `wiki/ai-tools/` directory after migration.

### Expand wiki page content

- Add `page_type` to frontmatter of all moved entity pages
- Expand Key Areas from one-line summaries to 2-5 sentence synthesized content per area, guided by the `ai-tools` domain guide
- Create source summary pages for each raw source
- Create initial `overview.md`
- Update all cross-references to use new paths (e.g. `../entities/claude-code.md` instead of `./claude-code.md`)

### Update index.md

Restructure index to reflect type-based organization:

```markdown
# Wiki Index

## Sources

- [Claude Code Docs](sources/claude-code-docs.md) — ...
- [Cursor Docs](sources/cursor-docs.md) — ...

## Entities

- [Claude Code](entities/claude-code.md) — ...
- [Cursor](entities/cursor.md) — ...

## Concepts

## Syntheses
```

### Log

No changes to format. Append a migration entry.

## CLAUDE Updates

Replace the current "Two-Layer Architecture" and "Key Files" sections with the new structure. Add sections for page types, templates, and domain guides. Key changes:

- Architecture section reflects type-based directory structure instead of domain-based
- Key Files section adds `overview.md` and the type directories
- Wiki Page Format section updated: `last_updated` field added alongside `date`; `page_type` field added
- Raw Source Format section added: `media` field replaces old `type`; explains the `date`/`last_updated` split
- New "Page Types" section with the type table
- New "Templates" section listing all template files
- New "Domain Guides" section explaining `_guides/<domain>.md`
- Index Format section updated to type-based organization
- Cross-reference format updated: `../entities/<page>.md`, `../sources/<page>.md`, etc.
