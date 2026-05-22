# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Plugin Is

An LLM-maintained personal knowledge base implementing the "LLM Wiki" pattern: raw sources are ingested into synthesized wiki pages, queryable and lintable. Three skills (ingest, query, lint) plus a wiki-maintainer agent for complex operations.

The human's job is to curate sources, direct the analysis, ask good questions, and think about what it all means. The LLM's job is everything else — summarizing, cross-referencing, filing, and bookkeeping.

## Three-Layer Architecture

- **`raw/`** — Immutable source documents. Never modify these. They are ground truth for re-synthesis if wiki pages go stale.
- **`wiki/`** — LLM-generated synthesis pages organized by type. The LLM writes these; humans read them. A single source may touch 10-15 wiki pages via cross-references and updates.
- **`CLAUDE.md`** (this file) — The schema layer. Tells the LLM how the wiki is structured, what conventions to follow, and what workflows to execute. You and the LLM co-evolve this over time as you figure out what works for your domain.

## Page Types

Wiki pages are not all the same structure. The page type determines the directory and sections:

| Type | Directory | When Created | Key Sections |
|------|-----------|-------------|-------------|
| source | `sources/` | Ingest | Summary, Key Points, Notable Details, See Also |
| entity | `entities/` | Ingest (source about a specific thing) | Summary, Key Areas (from domain guide), See Also |
| concept | `concepts/` | Ingest (source about an abstract idea) | Summary, Core Idea, Applications, Trade-offs, See Also |
| synthesis | `syntheses/` | Query answer filed back | Summary, Analysis, Implications, See Also |
| overview | top-level `overview.md` | Updated on every ingest | Summary, Domains, Active Questions, Recent Activity, See Also |

Comparison is a sub-type of synthesis (`synthesis_type: comparison`) — a comparison page lives in `syntheses/` with a table and verdict section.

The `page_type` field in frontmatter identifies the type. Each type has a template in `skills/wiki-ingest/templates/`.

## Key Files

- `wiki/index.md` — Content catalog organized by page type (Sources, Entities, Concepts, Syntheses). Updated on every ingest. The wiki-query skill reads this first to find relevant pages. Works well at moderate scale (~100 sources, ~hundreds of pages) without embedding-based RAG.
- `wiki/log.md` — Append-only activity log. Never rewrite, only append entries in `## [YYYY-MM-DD] operation | Title` format. The consistent prefix makes it parseable: `grep "^## \[" log.md | tail -5`.
- `wiki/overview.md` — Living synthesis across all sources. Updated on every ingest. The highest-level page in the wiki.

## Wiki Page Format

Every wiki page uses YAML frontmatter with these fields:

- `tags` — list of tags for categorization
- `date` — creation date (never changes)
- `last_updated` — date of last modification (updated on every edit)
- `sources` — list of source pages this was derived from
- `status` — `draft | stable | needs-update`
- `page_type` — `source | entity | concept | synthesis | overview`

Synthesis pages also have `synthesis_type: comparison | analysis | connection`.

The `date`/`last_updated` split tracks the page's lifecycle: `date` is set once on creation, `last_updated` is updated every time the page is modified.

## Raw Source Format

Every raw source uses YAML frontmatter with these fields:

- `tags` — list of tags for categorization
- `date` — date the source was collected
- `source_url` — origin URL or `"local"`
- `media` — `web | doc-index | file | pasted | transcript | notes`
- `domain` — domain identifier for routing
- `status` — `unprocessed | processed`

## Templates

Template files in `skills/wiki-ingest/templates/` define the required format for each document type. Skills reference templates in their workflow steps. When writing a document, read the template first, then fill in the placeholders.

- `templates/raw-source.md` — raw source frontmatter
- `templates/page-source.md` — source summary page
- `templates/page-entity.md` — entity page structure
- `templates/page-concept.md` — concept page structure
- `templates/page-synthesis.md` — synthesis page structure
- `templates/page-overview.md` — overview page structure
- `templates/index-entry.md` — index entry format
- `templates/log-entry.md` — log entry format

## Domain Guides

Each domain has a guide at `wiki/entities/_guides/<domain>.md` that defines the Key Areas for entity pages in that domain. When ingesting a source, the agent reads the domain guide to determine which areas to create and what information to extract. If no guide exists, the agent creates areas from the source's natural structure and should consider creating a guide for future sources.

Domain guides are meta-files — they are not listed in `wiki/index.md`.

## Naming Conventions

- File names: kebab-case (e.g. `claude-code.md`, `plugin-builder.md`)
- Domain folders under `raw/`: kebab-case (e.g. `ai-tools/`)
- One page per concept/entity; merge related topics rather than splitting
- When a page is superseded, mark it `needs-update` rather than deleting

## Cross-Reference Format

Pages reference each other using relative paths across type directories:

- Same directory: `[Codex](./codex.md)`
- To sources: `[Source](../sources/codex-docs.md)`
- To entities: `[Entity](../entities/codex.md)`
- To concepts: `[Concept](../concepts/llm-wiki.md)`
- To syntheses: `[Comparison](../syntheses/claude-code-vs-codex.md)`
- To overview: `[Overview](../overview.md)` (from subdirectories)

## Index Format

`wiki/index.md` catalogs every wiki page, organized by page type:

```markdown
# Wiki Index

## Sources
- [Claude Code Docs](sources/claude-code-docs.md) — ...

## Entities
- [Claude Code](entities/claude-code.md) — ...

## Concepts

## Syntheses
```

Update index on every ingest.

## Log Format

`wiki/log.md` is append-only. Never rewrite. Each entry follows:

```markdown
## [YYYY-MM-DD] operation | Title

Description of what was done.
```

## Operations

- **Ingest** (`/wiki-ingest`): Read source → discuss with user → save raw (with frontmatter) → write source summary page + entity/concept page → update index → update overview → update affected pages' cross-references → append to log
- **Query** (`/wiki-query`): Read index → find relevant pages → read pages → fall back to raw sources if needed → synthesize answer. Answers can take different forms: markdown page, comparison table, slide deck (Marp), chart (matplotlib). Substantial answers should be filed as synthesis pages in `wiki/syntheses/` — this is how the wiki compounds.
- **Lint** (`/wiki-lint`): Scan for contradictions, stale claims, orphan pages, missing cross-references → check index completeness → suggest new questions and sources → apply approved fixes → append to log. Never delete pages during lint.

## Agent Delegation

Simple operations (single ingest, quick query) run as skills on the main agent. Complex operations (batch ingest, full lint, cross-page restructuring, deep queries) delegate to the `wiki-maintainer` agent, which has write tools and operates in isolation.

## Conventions

- One source → one source summary page + one entity/concept page. Synthesize in the LLM's own words, organized by concept rather than mirroring source structure.
