---
name: llm-wiki-lint
description: Health-check the llm-wiki for consistency and completeness. Use when the user says "lint the llm-wiki", "health check", "what's missing", "check the llm-wiki", or periodically after multiple ingests. Scans for contradictions, stale claims, orphan pages, missing cross-references, and gaps.
---

# Wiki Lint

Health-check the wiki for consistency, completeness, and quality.

## Workflow

1. **Scan all wiki pages**
   - Read every page in `wiki/` (excluding `index.md` and `log.md`)
   - Build a mental model of the wiki's current state

2. **Check for issues**
   - **Contradictions**: Do any pages make claims that conflict with other pages?
   - **Stale claims**: Are there pages with `status: needs-update` that haven't been revised?
   - **Orphan pages**: Are there pages with no inbound links from other wiki pages?
   - **Missing cross-references**: Are there concepts mentioned in passing that deserve their own page or a link to an existing page?
   - **Concepts without pages**: Are there important topics referenced across multiple pages but lacking their own dedicated page?
   - **Data gaps**: Are there topics where the wiki coverage is thin and could benefit from a new source?

3. **Check index completeness**
   - Compare `wiki/index.md` entries against actual files in `wiki/`
   - Flag any pages missing from the index
   - Flag any index entries pointing to non-existent pages

4. **Suggest improvements**
   - Present findings as a prioritized list
   - Suggest new questions to investigate
   - Suggest new sources to find and ingest
   - Ask the user which fixes to apply

5. **Apply approved fixes**
   - Fix contradictions by updating the less authoritative page
   - Add missing cross-references
   - Update the index to match actual pages
   - Set `status: needs-update` on pages that need fresh sources
   - Append a lint entry to `wiki/log.md`

## Guidelines

- Run lint after every 3-5 ingests, or when the user asks
- Focus on the most impactful issues first — a contradiction between two active pages is more important than a missing cross-reference on a low-traffic page
- Don't delete pages during lint — only update, link, or flag
- If the wiki is small (< 10 pages), lint is lightweight. As it grows, lint becomes more valuable.
