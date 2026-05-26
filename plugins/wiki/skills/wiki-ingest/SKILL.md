---
name: wiki-ingest
description: Add a new source to the wiki and integrate it into existing pages. Use when the user says "ingest this", "add this to the wiki", "process this source", or drops a file into raw/. Handles reading the source, discussing key takeaways, creating a wiki page, updating the index, updating affected pages, and logging the operation.
---

# Wiki Ingest

Add a new source document to the wiki and integrate its knowledge into existing pages.

## Path Resolution

All paths resolve through `data/config.json`. Read this file first to determine the data root:
- `dataDir: "."` (default) → data root is `data/` inside the plugin directory
- `dataDir: "/absolute/path"` → data root is the specified absolute path

All `raw/` and `wiki/` references below are relative to the resolved data root. For example, `raw/ai-tools/` means `<data-root>/raw/ai-tools/`.

## Workflow

1. **Read the source**
   - If the user provides a file path, read it with the Read tool
   - If the user provides a URL, fetch it with WebFetch
   - If the user pastes text, use it directly
   - If the source is already in `<data-root>/raw/`, read it from there

2. **Discuss key takeaways with the user**
   - Summarize the main points
   - Ask if there are specific aspects to emphasize or de-emphasize
   - Confirm which domain folder the source belongs in (e.g. `<data-root>/raw/ai-tools/`)

3. **Save the raw source** (if not already in `<data-root>/raw/`)
   - Write the source document to `<data-root>/raw/<domain>/<source-name>.md`
   - Raw sources are immutable — never modify them after saving
   - Follow the frontmatter format in `templates/raw-source.md`

4. **Write the wiki pages** — ingest produces two pages
   - **Read the full template before writing** — templates include depth targets, example content, and quality checklists. Follow these to produce thorough, long-form pages.
   - (1) A source summary page in `<data-root>/wiki/sources/<source-name>-docs.md` following `templates/page-source.md`
   - (2) An entity or concept page — determine based on source content: entity for a specific thing (tool, person, project), concept for an abstract idea or pattern
   - For entity pages: write to `<data-root>/wiki/entities/<page-name>.md` following `templates/page-entity.md`. Read the domain guide at `<data-root>/wiki/entities/_guides/<domain>.md` for Key Areas. If no guide exists, create areas from the source's natural structure and consider creating a guide
   - For concept pages: write to `<data-root>/wiki/concepts/<page-name>.md` following `templates/page-concept.md`

5. **Update the index**
   - Read `<data-root>/wiki/index.md`
   - Add the new page entry under the appropriate domain heading
   - If the domain heading doesn't exist, create it
   - following the format in `templates/index-entry.md`

6. **Update the overview**
   - Read `<data-root>/wiki/overview.md` and update it following `templates/page-overview.md`
   - Add the new source to the Domains section, update Active Questions if relevant

7. **Append to the log**
   - Add an entry to `<data-root>/wiki/log.md` in the format: `## [YYYY-MM-DD] ingest | <Source Title>`
   - Briefly describe what was added and which pages were affected
   - following the format in `templates/log-entry.md`

## Guidelines

- One source = one wiki page. If a source covers multiple distinct topics, create separate pages for each and link them.
- The wiki page should synthesize, not copy. Rewrite in your own words, organize by concept rather than following the source's structure.
- Always check for existing pages before creating a new one. If a page already covers this topic, update it instead of creating a duplicate.
- When updating existing pages, add a brief note at the end of the affected section: `*(Updated YYYY-MM-DD with info from [Source](../../raw/domain/source.md))*`
- **Follow template depth targets** — each template specifies word counts and content requirements per section. These are minimums, not maximums. Aim for thorough, substantive content.
- **Self-check with the Quality Checklist** — every template ends with a checklist. Review it before finalizing any page.
