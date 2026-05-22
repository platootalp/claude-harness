---
name: llm-wiki-query
description: Answer questions from llm-wiki content. Use when the user asks about a topic that might be covered in the llm-wiki, says "look up X in the llm-wiki", "what does the llm-wiki say about Y", or asks about AI coding tools, features, configuration, or any topic the llm-wiki covers. Routes to the right llm-wiki pages via the index, reads them, and synthesizes an answer.
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

5. **Offer to file substantial answers as new pages**
   - If the answer required synthesizing multiple pages into a new insight (comparison, analysis, connection), offer to create a new wiki page for it
   - This is how the wiki compounds — explorations become permanent pages
   - Only offer for substantial answers, not simple lookups

## Routing Logic

The index replaces the old `ai-tool-reference` router. When a question comes in:

- Check `wiki/index.md` for matching pages
- The domain headings in the index serve as the routing table
- If unsure which domain, scan multiple domain sections

## Path Resolution

All wiki paths are relative to the wiki plugin root (`plugins/wiki/`). When the skill references `wiki/index.md`, the full path is `plugins/wiki/wiki/index.md`. When a wiki page references a raw source like `raw/ai-tools/claude-code.md`, the full path is `plugins/wiki/raw/ai-tools/claude-code.md`.

## Guidelines

- Prefer wiki pages over raw sources — the wiki is the synthesized, maintained layer
- Always cite which wiki page(s) you drew from
- If you find contradictory information between wiki pages, flag it and suggest running `/wiki-lint`
- If the wiki is empty or doesn't cover the topic, suggest running `/wiki-ingest` first
