# Wiki Plugin

An LLM-maintained personal knowledge base for Claude Code. Implements the LLM Wiki pattern: ingest sources, query the wiki, lint for consistency.

## Operations

- **wiki-ingest** — Add a source and integrate it into the wiki
- **wiki-query** — Answer questions from wiki content
- **wiki-lint** — Health-check and maintain the wiki

## Structure

- `raw/` — Immutable source documents (read-only for the LLM)
- `wiki/` — LLM-generated wiki pages (LLM writes, you read)
- `rules/wiki-schema.md` — Wiki conventions loaded into every session

## Getting Started

1. Drop a source into `raw/` or paste text
2. Run `/wiki-ingest` to process the source
3. Query with `/wiki-query` or ask naturally
4. Periodically `/wiki-lint` to keep the wiki healthy
