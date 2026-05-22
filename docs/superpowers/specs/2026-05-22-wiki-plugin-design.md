# Wiki Plugin Design

Replace the `reference` plugin with a `wiki` plugin that implements the LLM Wiki pattern — a persistent, compounding knowledge base maintained by the LLM.

## Problem

The current `reference` plugin packages documentation indexes as skills. This is a poor fit:

- **Semantic mismatch**: Skills guide workflows; reference docs are lookup material
- **Context waste**: Skill triggers load entire doc indexes into context when only one section is relevant
- **No accumulation**: Each query re-derives knowledge from scratch — nothing compounds

## Solution

A wiki plugin that follows the three-layer architecture from llm-wiki.md:

1. **Raw sources** (`raw/`) — immutable source documents, read-only for the LLM
2. **Wiki pages** (`wiki/`) — LLM-generated, interlinked markdown files that synthesize and cross-reference the raw sources
3. **Schema** (`rules/wiki-schema.md`) — always-on rule defining wiki conventions, loaded into every session

The wiki is a persistent artifact. Every source ingested, every query answered, every lint pass run makes it richer. Cross-references accumulate. Contradictions get flagged. The knowledge compounds.

## Plugin Structure

```
plugins/wiki/
  .claude-plugin/plugin.json          # name: wiki, version: 0.1.0
  rules/
    wiki-schema.md                     # Wiki conventions (always loaded)
  skills/
    wiki-ingest/SKILL.md               # Add a source and integrate into wiki
    wiki-query/SKILL.md                # Answer questions from wiki content
    wiki-lint/SKILL.md                 # Health-check and maintain the wiki
  agents/
    wiki-maintainer.md                 # Subagent for complex operations
  raw/                                 # Immutable source documents
    ai-tools/                          # First domain: AI coding tools
      claude-code.md
      cursor.md
      codex.md
      opencode.md
      plugin-builder.md
  wiki/                                # LLM-generated wiki pages
    index.md                           # Content catalog
    log.md                             # Chronological activity log
    ai-tools/                          # Wiki pages for AI tools domain
      claude-code.md
      cursor.md
      ...
```

## Wiki Operations

### wiki-ingest

Add a new source and integrate it into existing pages.

1. Read the source (file, URL, or pasted text)
2. Discuss key takeaways with the user
3. Write a summary page in `wiki/`
4. Update `wiki/index.md`
5. Update affected entity/concept pages across the wiki
6. Append entry to `wiki/log.md`

Trigger: "ingest this", "add this to the wiki", "process this source"

### wiki-query

Answer questions from the wiki, optionally filing answers as new pages.

1. Read `wiki/index.md` to find relevant pages
2. Read relevant wiki pages
3. If needed, read underlying `raw/` sources for detail
4. Synthesize answer with citations (page links)
5. If answer is substantial, offer to file as new wiki page

Trigger: questions about wiki content, "look up X in the wiki"

### wiki-lint

Health-check the wiki for consistency and completeness.

1. Scan pages for: contradictions, stale claims, orphans, missing cross-references, concepts without pages
2. Check `index.md` completeness against actual pages
3. Suggest new questions and sources
4. Present findings, ask which fixes to apply
5. Apply fixes, append lint entry to `wiki/log.md`

Trigger: "lint the wiki", "health check", "what's missing"

## Wiki-Maintainer Agent

Handles complex operations that benefit from isolated execution:

- Batch ingest of multiple sources
- Full wiki lint across all pages
- Cross-page restructuring (renaming, reorganizing, merging)
- Deep queries requiring synthesis across many pages

Simple operations (single ingest, quick query) are handled by the main agent using skills directly.

## Wiki-Schema Rule

Always-on rule defining wiki conventions:

1. **Directory layout** — locations of `raw/`, `wiki/`, `index.md`, `log.md`
2. **Page format** — frontmatter (tags, date, sources, status), body structure (summary, details, cross-references)
3. **Cross-reference style** — `[relative path](./page.md)` markdown links
4. **Naming conventions** — kebab-case file names, category folders
5. **Operation cheat sheet** — brief reminders of ingest/query/lint steps
6. **Log format** — `## [YYYY-MM-DD] operation | Title`

## Migration

1. Create wiki plugin structure (rules, skills, agents)
2. Extract doc indexes from existing 5 reference skills → `raw/ai-tools/` source documents
3. Extract ai-tool-reference router logic → absorbed into `wiki-query` (reads `index.md` instead)
4. Run initial ingest on each raw source to build `wiki/ai-tools/` pages (done manually during migration, not at plugin install time — new users start with an empty wiki and ingest sources themselves)
5. Delete old skill directories
6. Rename plugin from `reference` to `wiki` in `plugin.json` and `marketplace.json`

## Key Differences from Current Reference Plugin

| Aspect | Current (reference skills) | New (wiki plugin) |
|--------|---------------------------|-------------------|
| Content location | Baked into SKILL.md | Separate markdown files |
| Knowledge accumulation | None — re-derives each time | Compounds — wiki grows richer |
| Cross-references | None between skills | Full interlinking between pages |
| Context cost | Entire doc index loaded on trigger | Only relevant pages read on demand |
| Maintenance | Manual skill updates | LLM-maintained via lint |
| Extensibility | Add a new skill per tool | Drop source in raw/, ingest |
