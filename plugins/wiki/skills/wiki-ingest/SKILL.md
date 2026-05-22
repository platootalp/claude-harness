---
name: wiki-ingest
description: Add a new source to the wiki and integrate it into existing pages. Use when the user says "ingest this", "add this to the wiki", "process this source", or drops a file into raw/. Handles reading the source, discussing key takeaways, creating a wiki page, updating the index, updating affected pages, and logging the operation.
---

# Wiki Ingest

Add a new source document to the wiki and integrate its knowledge into existing pages.

## Workflow

1. **Read the source**
   - If the user provides a file path, read it with the Read tool
   - If the user provides a URL, fetch it with WebFetch
   - If the user pastes text, use it directly
   - If the source is already in `raw/`, read it from there

2. **Discuss key takeaways with the user**
   - Summarize the main points
   - Ask if there are specific aspects to emphasize or de-emphasize
   - Confirm which domain folder the source belongs in (e.g. `raw/ai-tools/`)

3. **Save the raw source** (if not already in `raw/`)
   - Write the source document to `raw/<domain>/<source-name>.md`
   - Raw sources are immutable — never modify them after saving

4. **Write the wiki page**
   - Create `wiki/<domain>/<page-name>.md` following the page format from wiki-schema
   - Include frontmatter (tags, date, sources, status)
   - Write a Summary section (one paragraph)
   - Write Details sections covering the key information
   - Add a See Also section with cross-references to related wiki pages

5. **Update the index**
   - Read `wiki/index.md`
   - Add the new page entry under the appropriate domain heading
   - If the domain heading doesn't exist, create it

6. **Update affected pages**
   - Scan existing wiki pages for concepts that overlap with the new source
   - Update cross-references, add links to the new page
   - If the new source contradicts or supersedes existing claims, update those pages and set their status to `needs-update`
   - Keep changes focused — don't rewrite pages, just add references and note updates

7. **Append to the log**
   - Add an entry to `wiki/log.md` in the format: `## [YYYY-MM-DD] ingest | <Source Title>`
   - Briefly describe what was added and which pages were affected

## Guidelines

- One source = one wiki page. If a source covers multiple distinct topics, create separate pages for each and link them.
- The wiki page should synthesize, not copy. Rewrite in your own words, organize by concept rather than following the source's structure.
- Always check for existing pages before creating a new one. If a page already covers this topic, update it instead of creating a duplicate.
- When updating existing pages, add a brief note at the end of the affected section: `*(Updated YYYY-MM-DD with info from [Source](../../raw/domain/source.md))*`
