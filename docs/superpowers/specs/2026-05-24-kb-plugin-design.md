# KB Plugin Design — Automated Personal Knowledge Base

## Overview

A new plugin (`kb`) that merges the capabilities of `analysis` and `wiki` into an ETL-pipeline architecture for building an automated personal knowledge base, with codebase understanding as the core focus.

**ETL Pipeline:**

```
Extract (codebase analysis) → Transform (structured knowledge) → Load/Present (site + graph)
```

- **Extract**: Scan codebases, produce deep analysis documents across multiple dimensions
- **Transform**: Convert raw analysis into structured, cross-referenced wiki pages
- **Load/Present**: Render everything as a searchable Astro site with knowledge graph visualization

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | ETL pipeline | Stages decouple through filesystem; supports one-click automation and granular control |
| Core focus | Codebase understanding | Extract is optimized for code analysis; other sources are future extensions |
| Extract phases | Two: scan → deep analysis | Structure map guides deep extraction; no "survey" mode — all output is deep |
| Extract dimensions | 5 orthogonal dimensions | topology, api, data-model, flows, concepts — each is a single-responsibility skill |
| Identity | New plugin | Not an upgrade of analysis or wiki; clean architecture from scratch |
| Runtime | Dual mode | Claude Code plugin (slash commands + agents) + standalone (Astro site) |
| Presentation | Reuse + enhance Astro site | Three views: Raw docs, Wiki pages, Knowledge graph |

---

## Stage 1: Extract

### Two-Phase Design

**Phase 1 — Structure Scan** (`scan` skill)

Scans the codebase, produces a structure map (`_map.md`) as the roadmap for Phase 2. Not a user-facing document.

Output: `data/raw/<project>/_map.md`

Structure map contents:
- Module inventory (path, responsibility, tech stack, external interface count)
- Dependency graph (inter-module calls/references)
- Architecture layers (which modules belong to which layer, inter-layer dependency rules)
- Entry point identification (main, router, config, etc.)
- Analysis suggestions (most complex modules, tightest coupling, recommended analysis order)

**Phase 2 — Deep Analysis** (5 dimension skills)

Each skill reads `_map.md` to determine scope, then produces deep analysis documents per module/flow/entity. No survey mode exists — all output is thorough.

| Skill | Dimension | Analyzes | Output Directory |
|-------|-----------|----------|-----------------|
| `extract-topology` | topology | Module internals, responsibility boundaries, upstream/downstream interactions | `data/raw/<project>/topology/` |
| `extract-api` | api | Full API contracts, parameters, return values, error handling, call examples | `data/raw/<project>/api/` |
| `extract-data-model` | data-model | Entity schemas, relationships, constraints, state machines, access patterns | `data/raw/<project>/data-model/` |
| `extract-flows` | flows | End-to-end paths, branches, exception handling, performance characteristics | `data/raw/<project>/flows/` |
| `extract-concepts` | concepts | Domain concept definitions, code mappings, inter-concept relationships | `data/raw/<project>/concepts/` |

**Router skill**: `extract` — dispatches to specific dimension skills; supports `--all` for full extraction.

### Output Directory Structure

```
data/raw/<project>/
├── _map.md                              # Structure map (Phase 1 output)
├── topology/
│   ├── _index.md                        # Index with frontmatter
│   └── modules/
│       ├── <module-a>.md               # One deep doc per module
│       └── <module-b>.md
├── api/
│   ├── _index.md
│   ├── http/
│   │   ├── <resource-a>.md
│   │   └── <resource-b>.md
│   ├── cli/
│   │   └── <command-group>.md
│   └── events/
│       └── <event-type>.md
├── data-model/
│   ├── _index.md
│   ├── entities/
│   │   └── <entity>.md
│   └── state-machines/
│       └── <state-entity>.md
├── flows/
│   ├── _index.md
│   ├── <flow-a>.md
│   └── <flow-b>.md
└── concepts/
    ├── _index.md
    ├── terms.md
    └── <domain>.md
```

File count scales with codebase size. Templates define required sections per dimension, not file count.

### Frontmatter

Only `_index.md` carries frontmatter. Sub-files inherit context from parent.

```yaml
---
project: claude-harness
dimension: topology
date: 2026-05-24
status: unprocessed
tags: [plugins, marketplace]
---
```

| Field | Purpose |
|-------|---------|
| `project` | Identifies which project this analysis belongs to |
| `dimension` | Which extraction dimension; Transform uses this to route to the correct wiki page type |
| `date` | Extraction timestamp; used for staleness detection and log |
| `status` | `unprocessed` / `processed`; Transform scans for unprocessed docs and marks them after consumption |
| `tags` | Semantic tags for categorization and query |

### Mapping from Existing Analysis Skills

| Existing skill | New skill | Change |
|----------------|-----------|--------|
| `codebase-analysis` | `extract` (router) | Renamed, pipeline-aware |
| `codebase-to-docs` | Split into `extract-topology` + `extract-flows` | Dual-axis (architecture + workflows) becomes two independent skills |
| `system-architecture-analysis` | Merged into `extract-topology` | C4 model becomes a sub-template of topology |
| `source-functional-analysis` | `extract-flows` | Renamed, output format aligned |
| `deep-functional-analysis` | `extract-topology` (deep module analysis) | Absorbed as topology's per-module deep analysis |
| (none) | `extract-api` | New |
| (none) | `extract-data-model` | New |
| (none) | `extract-concepts` | New |

---

## Stage 2: Transform

### Skill Design

| Skill | Responsibility |
|-------|---------------|
| `transform` | Router: dispatch to ingest or cross-ref |
| `ingest` | Single-dimension/single-doc transformation: raw → wiki page |
| `cross-ref` | Cross-document linking: supplement cross-references + generate synthesis pages |
| `lint` | Knowledge base health check |
| `query` | Knowledge base query and synthesis |

### Transformation Mapping

| Extract dimension | Wiki page type | Rationale |
|-------------------|---------------|-----------|
| topology/modules/* | entity | Each module is an entity |
| api/* | entity | Each API group is an entity |
| data-model/entities/* | entity | Each data entity is an entity |
| flows/* | concept | Each flow is a concept (cross-entity behavioral pattern) |
| concepts/* | concept | Each domain concept is a concept |
| Cross-dimension synthesis | synthesis | Auto-generated when cross-dimension relationships are discovered |

### Transform Execution Flow

1. Scan all `_index.md` files under `data/raw/<project>/`, find `status: unprocessed`
2. Per dimension, read all deep analysis documents
3. Per document: determine target wiki page type, generate page from template, write to `data/wiki/`, add cross-references to existing pages
4. Scan all new pages, discover cross-dimension relationships, generate synthesis pages
5. Update `data/wiki/index.md`, `data/wiki/overview.md`, `data/wiki/log.md`
6. Mark processed `_index.md` files as `status: processed`

### Wiki Data Structure

```
data/wiki/
├── index.md                    # Content catalog
├── overview.md                 # Cross-project synthesis
├── log.md                      # Activity log
├── projects/
│   └── <project>/
│       ├── overview.md         # Project-level overview
│       ├── entities/           # Entity pages
│       │   ├── <module>.md
│       │   ├── <api-group>.md
│       │   └── <data-entity>.md
│       ├── concepts/           # Concept pages
│       │   ├── <flow>.md
│       │   └── <domain-concept>.md
│       └── syntheses/          # Synthesis pages
│           └── <cross-dimension>.md
└── cross-project/              # Cross-project synthesis
    └── <synthesis>.md
```

Key change from existing wiki: added `projects/` layer because the knowledge base may contain analysis results from multiple projects.

---

## Stage 3: Load/Present

### Three Views

The site presents three views of the same knowledge base, each serving a different purpose.

**Raw View** — Browse Extract's deep analysis documents

- Entry: grouped by dimension (topology, api, data-model, flows, concepts), showing doc count per group
- Detail: renders raw markdown with Mermaid diagrams, code blocks, callouts
- Sidebar: tree navigation by dimension
- Use: inspect specific module analysis details, code evidence, technical mechanisms

**Wiki View** — Browse Transform's structured knowledge pages

- Entry: grouped by page type (entity, concept, synthesis), showing page count per type
- Detail: renders wiki page with cross-reference links and source traceability (link back to raw doc)
- Sidebar: tree navigation by page type
- Use: quick lookup, follow cross-references to explore related knowledge

**Graph View** — Interactive knowledge graph

- Force-directed graph: nodes = wiki pages (entity/concept/synthesis), edges = cross-reference relationships
- Click node: summary card with link to wiki detail page
- Color modes: by dimension (which Extract dimension), by type (entity/concept/synthesis), by project
- Filters: by dimension, type, project
- Layout controls: collapse/expand, focus on node neighbors
- Use: discover unknown relationships, understand knowledge structure at a glance

### Site Structure

```
site/
├── src/
│   ├── pages/
│   │   ├── index.astro                    # Home: project card list
│   │   ├── projects/
│   │   │   └── [project]/
│   │   │       ├── index.astro            # Project home: three view entries
│   │   │       ├── raw/
│   │   │       │   ├── index.astro        # Raw docs overview: grouped by dimension
│   │   │       │   └── [...slug].astro    # Raw doc detail page
│   │   │       ├── wiki/
│   │   │       │   ├── index.astro        # Wiki overview: grouped by page type
│   │   │       │   └── [...slug].astro    # Wiki page detail page
│   │   │       └── graph.astro            # Knowledge graph: force-directed
│   │   └── search.astro                   # Global search
│   ├── components/
│   │   ├── ProjectSwitcher.astro          # Project switcher
│   │   ├── DimensionFilter.astro          # Dimension filter (raw view)
│   │   ├── PageTypeFilter.astro           # Page type filter (wiki view)
│   │   ├── KnowledgeGraph.tsx             # Force-directed graph component
│   │   ├── GraphControls.tsx              # Graph control panel
│   │   └── ...                            # Reuse existing components
│   └── ...
```

### Project Home Page

```
┌─────────────────────────────────────────────┐
│  claude-harness                              │
├─────────────┬──────────────┬────────────────┤
│  Raw Docs   │  Wiki Pages  │  Knowledge     │
│  23 docs    │  15 pages    │  Graph         │
│  5 dims     │  3 types     │  45 nodes      │
│             │              │  67 edges       │
│  [Browse]   │  [Browse]    │  [Explore]     │
├─────────────┴──────────────┴────────────────┤
│  Recent Activity                            │
│  • topology extracted — 2026-05-24          │
│  • api extracted — 2026-05-24               │
│  • wiki transformed — 2026-05-24            │
└─────────────────────────────────────────────┘
```

### Load Skills

| Skill | Responsibility |
|-------|---------------|
| `serve` | Build Astro site + start preview server |
| `build-search-index` | Build Fuse.js search index from wiki + raw content |
| `build-graph` | Extract cross-references from wiki pages, build graph data (JSON) for force-directed visualization |

These are called automatically by `/kb serve`, not invoked directly by users.

### Dual Mode

- **Plugin mode**: Users interact via `/kb` commands and agents in Claude Code
- **Standalone mode**: `npm run dev` or `npm run build` directly; consumes existing `data/wiki/` content without Claude Code

---

## Pipeline Commands

| Command | Pipeline stages | Description |
|---------|----------------|-------------|
| `/kb` | scan → extract-all → ingest → cross-ref → serve | Full pipeline, one click |
| `/kb scan` | scan | Structure scan only |
| `/kb extract [dimension]` | scan + extract-* | Extract specified dimension (topology/api/data-model/flows/concepts); all if unspecified |
| `/kb transform [dimension]` | ingest + cross-ref | Transform specified dimension's raw to wiki; all if unspecified |
| `/kb query <question>` | query | Query knowledge base |
| `/kb lint` | lint | Knowledge base health check |
| `/kb serve` | serve | Build + start site |

## Agents

| Agent | Responsibility | Model |
|-------|---------------|-------|
| `kb-agent` | Main router: parse `/kb` command args, dispatch to skills | sonnet |
| `extract-agent` | Multi-dimension parallel extraction: read `_map.md`, call extract skills concurrently | sonnet |
| `transform-agent` | Batch transformation: scan unprocessed raw, ingest per doc, then cross-ref | sonnet |

## Plugin Directory Structure

```
plugins/kb/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── extract/
│   │   └── SKILL.md                         # Extract router
│   ├── scan/
│   │   └── SKILL.md                         # Phase 1: structure scan
│   ├── extract-topology/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── topology.md                  # Required sections for topology docs
│   ├── extract-api/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── api.md
│   ├── extract-data-model/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── data-model.md
│   ├── extract-flows/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── flows.md
│   ├── extract-concepts/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── concepts.md
│   ├── transform/
│   │   └── SKILL.md                         # Transform router
│   ├── ingest/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       ├── entity.md                    # Entity page template
│   │       ├── concept.md                   # Concept page template
│   │       └── synthesis.md                 # Synthesis page template
│   ├── cross-ref/
│   │   └── SKILL.md
│   ├── lint/
│   │   └── SKILL.md
│   ├── query/
│   │   └── SKILL.md
│   ├── serve/
│   │   └── SKILL.md
│   ├── build-search-index/
│   │   └── SKILL.md
│   └── build-graph/
│       └── SKILL.md
├── agents/
│   ├── kb-agent.md
│   ├── extract-agent.md
│   └── transform-agent.md
├── commands/
│   └── kb.md                                # /kb command
├── data/
│   ├── config.json                          # {"dataDir": "data"}
│   ├── raw/                                 # Extract output (gitignored)
│   └── wiki/                                # Transform output (gitignored)
├── site/                                    # Astro site (enhanced from analysis)
├── .gitignore
└── CHANGELOG.md
```

## Roadmap

### Phase 1: Core Pipeline

- `scan` + 5 extract skills + templates
- `ingest` + `cross-ref` + wiki page templates
- `serve` + Astro site with raw/wiki/graph views
- `/kb` command + 3 agents
- Validation: analyze `claude-harness` itself end-to-end

### Phase 2: Extended Sources

- Remote repo ingestion (clone + scan)
- URL ingestion
- File ingestion (PDF, docx, etc.)
- Non-codebase raw → wiki transformation

### Phase 3: Intelligence

- Incremental extraction (only re-analyze changed files)
- Diff impact analysis (`extract-impact`)
- Design decision extraction (`extract-decisions`)
- Auto-update via git hooks
- Knowledge graph community detection

### Phase 4: Ecosystem

- Export to PDF/DOCX (office plugin integration)
- Multi-project cross-synthesis
- Team sharing (graph as JSON, commit to repo)
- API documentation hosting
