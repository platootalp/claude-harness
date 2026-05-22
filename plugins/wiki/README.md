# Wiki Plugin

An LLM-maintained personal knowledge base for Claude Code. Implements the LLM Wiki pattern: ingest sources, query the wiki, lint for consistency.

## Install

```bash
# Add the marketplace (if not already added)
/plugin marketplace add https://github.com/platootalp/harness-marketplace

# Install the wiki plugin
/plugin install wiki@harness-marketplace
```

## Plugin Contents

| Type | Name | Description |
|------|------|-------------|
| Skill | `wiki-ingest` | Add a source and integrate it into the wiki |
| Skill | `wiki-query` | Answer questions from wiki content |
| Skill | `wiki-lint` | Health-check and maintain the wiki |
| Agent | `wiki-maintainer` | Handles complex operations (batch ingest, full lint, restructuring, deep queries) |

## Slash Commands

- `/wiki-ingest` — Process a new source into the wiki
- `/wiki-query` — Ask a question against wiki content
- `/wiki-lint` — Run a consistency and completeness check

## Three-Layer Architecture

```
raw/          Immutable source documents (read-only)
wiki/         LLM-generated synthesis pages
CLAUDE.md     Schema layer — conventions, templates, workflows
```

- **`raw/`** — Ground truth. Never modify after creation.
- **`wiki/`** — The LLM writes; humans read. Organized by page type.
- **`CLAUDE.md`** — Co-evolved with the wiki as domains and conventions grow.

## Wiki Page Types

| Type | Directory | Created When | Purpose |
|------|-----------|-------------|---------|
| source | `wiki/sources/` | Ingest | Summary of a raw source document |
| entity | `wiki/entities/` | Ingest (about a specific thing) | People, companies, products, projects |
| concept | `wiki/concepts/` | Ingest (about an abstract idea) | Ideas, frameworks, methods, theories |
| synthesis | `wiki/syntheses/` | Query answer filed back | Comparisons, analyses, connections |
| overview | `wiki/overview.md` | Updated every ingest | Living synthesis across all sources |

## Directory Structure

```
wiki/
├── .claude-plugin/plugin.json    # Plugin manifest
├── CLAUDE.md                     # Wiki schema and conventions
├── agents/wiki-maintainer.md     # Complex operation agent
├── skills/
│   ├── wiki-ingest/              # Ingest skill + templates/
│   ├── wiki-query/               # Query skill
│   └── wiki-lint/                # Lint skill
├── raw/                          # Immutable source documents
│   ├── ai-tools/                 # Domain-organized sources
│   └── llm-wiki.md              # Pattern reference
└── wiki/                         # LLM-maintained wiki pages
    ├── index.md                  # Content catalog
    ├── overview.md               # Cross-source synthesis
    ├── log.md                    # Append-only activity log
    ├── sources/                  # Source summary pages
    ├── entities/                 # Entity pages + _guides/
    ├── concepts/                 # Concept pages
    └── syntheses/                # Synthesis pages
```

## Current Domains

The wiki currently covers **AI coding tools**:

- Claude Code, Codex, Cursor, OpenCode, Plugin Builder
- Domain guide at `wiki/entities/_guides/ai-tools.md`

## Getting Started

1. Drop a source into `raw/` or paste text
2. Run `/wiki-ingest` to process the source
3. Query with `/wiki-query` or ask naturally
4. Periodically `/wiki-lint` to keep the wiki healthy
