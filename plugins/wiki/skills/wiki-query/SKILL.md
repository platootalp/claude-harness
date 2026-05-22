---
name: wiki-query
description: Answer questions from wiki content. Use when the user asks about a topic that might be covered in the wiki, says "look up X in the wiki", "what does the wiki say about Y", or asks about AI coding tools, features, configuration, or any topic the wiki covers. Routes to the right wiki pages via the index, reads them, and synthesizes an answer.
---

# Wiki Query

Answer questions from the wiki by reading relevant pages and synthesizing an answer.

## Workflow

1. **Read the index**
   - Read `wiki/index.md` to find pages relevant to the question
   - Match the question topic against page titles and summaries in the index

2. **Read relevant wiki pages**
   - Read the most relevant pages identified from the index
   - If a page references other pages that seem relevant, read those too
   - Stop when you have enough context to answer the question

3. **Read raw sources if needed**
   - If the wiki pages lack detail on the specific question, read the underlying raw sources listed in the page's frontmatter `sources` field
   - Only read raw sources when the wiki synthesis is insufficient

4. **Synthesize the answer**
   - Answer the question directly, citing wiki pages with markdown links
   - If the answer combines information from multiple pages, make the connections explicit
   - If the wiki doesn't cover the topic, say so and suggest ingesting a source
   - Answers can take different forms depending on the question: markdown page, comparison table, slide deck (Marp), chart (matplotlib), canvas

5. **File substantial answers as new wiki pages**
   - If the answer required synthesizing multiple pages into a new insight (comparison, analysis, connection), create a new wiki page for it in `wiki/syntheses/` following `templates/page-synthesis.md`
   - Set `synthesis_type` based on the answer: `comparison` for side-by-side analysis, `analysis` for deep dives, `connection` for newly discovered relationships
   - This is how the wiki compounds — explorations become permanent knowledge, not lost in chat history
   - Only file substantial answers, not simple lookups
   - Update the index with the new page entry following `templates/index-entry.md`

## Routing Logic

The index is organized by page type (Sources, Entities, Concepts, Syntheses). When a question comes in:

- Check `wiki/index.md` for matching pages across all type sections
- Start with Entities section for questions about specific things
- Start with Concepts section for questions about ideas and patterns
- Check Syntheses for existing comparisons or analyses

## Path Resolution

All wiki paths are relative to the wiki plugin root (`plugins/wiki/`). When the skill references `wiki/index.md`, the full path is `plugins/wiki/wiki/index.md`. When a wiki page references a raw source like `raw/ai-tools/claude-code.md`, the full path is `plugins/wiki/raw/ai-tools/claude-code.md`.

## Guidelines

- Prefer wiki pages over raw sources — the wiki is the synthesized, maintained layer
- Always cite which wiki page(s) you drew from
- If you find contradictory information between wiki pages, flag it and suggest running `/wiki-lint`
- If the wiki is empty or doesn't cover the topic, suggest running `/wiki-ingest` first
