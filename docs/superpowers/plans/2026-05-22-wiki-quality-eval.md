# Wiki Quality & Eval System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the wiki plugin's output path, enhance templates for long-form quality, and add an LLM-as-judge eval system.

**Architecture:** Migrate `raw/` and `wiki/` into a `data/` directory with `config.json` for path configuration. Enhance all 7 templates with depth targets, examples, and quality checklists. Build eval system with rubric, golden samples, and a shell-based runner that calls Claude API as judge.

**Tech Stack:** Markdown templates, JSON config, bash + curl + jq for eval runner, Claude API for judging.

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `data/config.json` | Plugin data path configuration |
| Create | `data/raw/` | Migrated raw sources (from `raw/`) |
| Create | `data/wiki/` | Migrated wiki pages (from `wiki/`) |
| Delete | `raw/` | Removed after migration |
| Delete | `wiki/` | Removed after migration |
| Modify | `skills/wiki-ingest/templates/page-entity.md` | Enhanced entity template |
| Modify | `skills/wiki-ingest/templates/page-source.md` | Enhanced source template |
| Modify | `skills/wiki-ingest/templates/page-concept.md` | Enhanced concept template |
| Modify | `skills/wiki-ingest/templates/page-synthesis.md` | Enhanced synthesis template |
| Modify | `skills/wiki-ingest/templates/page-overview.md` | Enhanced overview template |
| Modify | `skills/wiki-ingest/templates/raw-source.md` | Enhanced raw source template |
| Modify | `skills/wiki-ingest/SKILL.md` | Path resolution, template guidance |
| Modify | `skills/wiki-query/SKILL.md` | Path resolution update |
| Modify | `skills/wiki-lint/SKILL.md` | Path resolution update |
| Modify | `agents/wiki-maintainer.md` | Path resolution update |
| Modify | `CLAUDE.md` | Directory structure, path docs |
| Create | `skills/wiki-ingest/evals/rubric.md` | Scoring criteria |
| Create | `skills/wiki-ingest/evals/samples/input/cursor.md` | Short eval input |
| Create | `skills/wiki-ingest/evals/samples/input/opencode.md` | Medium eval input |
| Create | `skills/wiki-ingest/evals/samples/input/plugin-builder.md` | Long eval input |
| Create | `skills/wiki-ingest/evals/samples/expected/cursor-entity.md` | Golden entity page for cursor |
| Create | `skills/wiki-ingest/evals/samples/expected/opencode-entity.md` | Golden entity page for opencode |
| Create | `skills/wiki-ingest/evals/samples/expected/plugin-builder-entity.md` | Golden entity page for plugin-builder |
| Create | `skills/wiki-ingest/evals/run-eval.sh` | Eval runner script |
| Create | `skills/wiki-ingest/evals/judge-prompt.md` | LLM judge system prompt |
| Create | `skills/wiki-ingest/evals/results/.gitkeep` | Results directory |

---

### Task 1: Create data directory and config.json

**Files:**
- Create: `data/config.json`
- Create: `data/results/.gitkeep` (placeholder to ensure dir exists in git)

- [ ] **Step 1: Create the data directory structure**

```bash
cd /Users/lijunyi/road/claude-harness/plugins/wiki
mkdir -p data
```

- [ ] **Step 2: Create config.json**

Write `data/config.json`:

```json
{
  "dataDir": "."
}
```

- [ ] **Step 3: Commit**

```bash
git add data/config.json
git commit -m "feat(wiki): add data directory with config.json for path configuration"
```

---

### Task 2: Migrate raw/ and wiki/ into data/

**Files:**
- Move: `raw/` → `data/raw/`
- Move: `wiki/` → `data/wiki/`
- Delete: `raw/` (old location)
- Delete: `wiki/` (old location)

- [ ] **Step 1: Move raw/ into data/raw/**

```bash
cd /Users/lijunyi/road/claude-harness/plugins/wiki
mv raw data/raw
```

- [ ] **Step 2: Move wiki/ into data/wiki/**

```bash
mv wiki data/wiki
```

- [ ] **Step 3: Verify migration**

```bash
ls data/raw/ai-tools/ && ls data/wiki/entities/ && ls data/wiki/sources/
```

Expected: both directories show their files (claude-code.md, codex.md, etc.)

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor(wiki): migrate raw/ and wiki/ into data/ directory"
```

---

### Task 3: Update CLAUDE.md with new directory structure and path resolution

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the Three-Layer Architecture section**

Replace the current Three-Layer Architecture section (lines 11-15) with:

```markdown
## Three-Layer Architecture

All wiki data lives in the `data/` directory, configured via `data/config.json`. The `dataDir` field in config.json specifies the data root relative to the plugin directory (default: `"."` meaning `data/` itself). All skills resolve `raw/` and `wiki/` paths inside the configured data directory.

- **`data/raw/`** — Immutable source documents. Never modify these. They are ground truth for re-synthesis if wiki pages go stale.
- **`data/wiki/`** — LLM-generated synthesis pages organized by type. The LLM writes these; humans read them. A single source may touch 10-15 wiki pages via cross-references and updates.
- **`CLAUDE.md`** (this file) — The schema layer. Tells the LLM how the wiki is structured, what conventions to follow, and what workflows to execute. You and the LLM co-evolve this over time as you figure out what works for your domain.
```

- [ ] **Step 2: Update Key Files section**

Replace the Key Files section (lines 33-37) with:

```markdown
## Key Files

- `data/config.json` — Plugin configuration. `dataDir` field sets the data root (default: `"."` = `data/` directory). Can be an absolute path to store wiki data elsewhere.
- `data/wiki/index.md` — Content catalog organized by page type (Sources, Entities, Concepts, Syntheses). Updated on every ingest. The wiki-query skill reads this first to find relevant pages. Works well at moderate scale (~100 sources, ~hundreds of pages) without embedding-based RAG.
- `data/wiki/log.md` — Append-only activity log. Never rewrite, only append entries in `## [YYYY-MM-DD] operation | Title` format. The consistent prefix makes it parseable: `grep "^## \[" log.md | tail -5`.
- `data/wiki/overview.md` — Living synthesis across all sources. Updated on every ingest. The highest-level page in the wiki.
```

- [ ] **Step 3: Update Templates section**

Replace the Templates section (lines 65-76) with:

```markdown
## Templates

Template files in `skills/wiki-ingest/templates/` define the required format for each document type. Skills reference templates in their workflow steps. When writing a document, read the template first, then fill in the placeholders. Templates include depth targets, example content, and quality checklists — follow these to produce thorough, long-form wiki pages.

- `templates/raw-source.md` — raw source frontmatter
- `templates/page-source.md` — source summary page
- `templates/page-entity.md` — entity page structure
- `templates/page-concept.md` — concept page structure
- `templates/page-synthesis.md` — synthesis page structure
- `templates/page-overview.md` — overview page structure
- `templates/index-entry.md` — index entry format
- `templates/log-entry.md` — log entry format
```

- [ ] **Step 4: Update Domain Guides section**

Replace the Domain Guides section (lines 79-82) with:

```markdown
## Domain Guides

Each domain has a guide at `data/wiki/entities/_guides/<domain>.md` that defines the Key Areas for entity pages in that domain. When ingesting a source, the agent reads the domain guide to determine which areas to create and what information to extract. If no guide exists, the agent creates areas from the source's natural structure and should consider creating a guide for future sources.

Domain guides are meta-files — they are not listed in `data/wiki/index.md`.
```

- [ ] **Step 5: Update Naming Conventions section**

Replace the Naming Conventions section (lines 84-89) with:

```markdown
## Naming Conventions

- File names: kebab-case (e.g. `claude-code.md`, `plugin-builder.md`)
- Domain folders under `data/raw/`: kebab-case (e.g. `ai-tools/`)
- One page per concept/entity; merge related topics rather than splitting
- When a page is superseded, mark it `needs-update` rather than deleting
```

- [ ] **Step 6: Update Cross-Reference Format section**

Replace the Cross-Reference Format section (lines 91-100) with:

```markdown
## Cross-Reference Format

Pages reference each other using relative paths across type directories. All paths are relative to `data/wiki/`:

- Same directory: `[Codex](./codex.md)`
- To sources: `[Source](../sources/codex-docs.md)`
- To entities: `[Entity](../entities/codex.md)`
- To concepts: `[Concept](../concepts/llm-wiki.md)`
- To syntheses: `[Comparison](../syntheses/claude-code-vs-codex.md)`
- To overview: `[Overview](../overview.md)` (from subdirectories)
- To raw sources: `[Raw](../../raw/ai-tools/codex.md)` (from wiki subdirectories)
```

- [ ] **Step 7: Update Index Format section**

Replace the Index Format section (lines 102-120) with:

```markdown
## Index Format

`data/wiki/index.md` catalogs every wiki page, organized by page type:

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
```

- [ ] **Step 8: Update Log Format section**

Replace the Log Format section (lines 122-131) with:

```markdown
## Log Format

`data/wiki/log.md` is append-only. Never rewrite. Each entry follows:

```markdown
## [YYYY-MM-DD] operation | Title

Description of what was done.
```
```

- [ ] **Step 9: Update Operations section**

Replace the Operations section (lines 133-136) with:

```markdown
## Operations

- **Ingest** (`/wiki-ingest`): Read source → discuss with user → save raw (with frontmatter) → write source summary page + entity/concept page → update index → update overview → update affected pages' cross-references → append to log
- **Query** (`/wiki-query`): Read index → find relevant pages → read pages → fall back to raw sources if needed → synthesize answer. Answers can take different forms: markdown page, comparison table, slide deck (Marp), chart (matplotlib). Substantial answers should be filed as synthesis pages in `data/wiki/syntheses/` — this is how the wiki compounds.
- **Lint** (`/wiki-lint`): Scan for contradictions, stale claims, orphan pages, missing cross-references → check index completeness → suggest new questions and sources → apply approved fixes → append to log. Never delete pages during lint.
```

- [ ] **Step 10: Update Conventions section**

Replace the Conventions section (lines 139-144) with:

```markdown
## Conventions

- One source → one source summary page + one entity/concept page. Synthesize in the LLM's own words, organized by concept rather than mirroring source structure.
- All data paths resolve through `data/config.json`. Default data root is `data/`.
```

- [ ] **Step 11: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(wiki): update CLAUDE.md with data/ directory structure and path resolution"
```

---

### Task 4: Update wiki-ingest SKILL.md with path resolution

**Files:**
- Modify: `skills/wiki-ingest/SKILL.md`

- [ ] **Step 1: Add path resolution section after the title**

Insert after line 6 (`# Wiki Ingest`):

```markdown
## Path Resolution

All paths resolve through `data/config.json`. Read this file first to determine the data root:
- `dataDir: "."` (default) → data root is `data/` inside the plugin directory
- `dataDir: "/absolute/path"` → data root is the specified absolute path

All `raw/` and `wiki/` references below are relative to the resolved data root. For example, `raw/ai-tools/` means `<data-root>/raw/ai-tools/`.
```

- [ ] **Step 2: Update workflow step 3 (Save the raw source)**

Replace step 3 (lines 23-26):

```markdown
3. **Save the raw source** (if not already in `raw/`)
   - Write the source document to `<data-root>/raw/<domain>/<source-name>.md`
   - Raw sources are immutable — never modify them after saving
   - Follow the frontmatter format in `templates/raw-source.md`
```

- [ ] **Step 3: Update workflow step 4 (Write the wiki pages)**

Replace step 4 (lines 28-33):

```markdown
4. **Write the wiki pages** — ingest produces two pages
   - (1) A source summary page in `<data-root>/wiki/sources/<source-name>-docs.md` following `templates/page-source.md`
   - (2) An entity or concept page — determine based on source content: entity for a specific thing (tool, person, project), concept for an abstract idea or pattern
   - For entity pages: write to `<data-root>/wiki/entities/<page-name>.md` following `templates/page-entity.md`. Read the domain guide at `<data-root>/wiki/entities/_guides/<domain>.md` for Key Areas. If no guide exists, create areas from the source's natural structure and consider creating a guide
   - For concept pages: write to `<data-root>/wiki/concepts/<page-name>.md` following `templates/page-concept.md`
   - **Read the full template before writing** — templates include depth targets, example content, and quality checklists. Follow these to produce thorough, long-form pages.
```

- [ ] **Step 4: Update workflow step 5 (Update the index)**

Replace step 5 (lines 35-39):

```markdown
5. **Update the index**
   - Read `<data-root>/wiki/index.md`
   - Add the new page entry under the appropriate type heading (Sources, Entities, Concepts, Syntheses)
   - If the type heading doesn't exist, create it
   - following the format in `templates/index-entry.md`
```

- [ ] **Step 5: Update workflow step 6 (Update the overview)**

Replace step 6 (lines 41-43):

```markdown
6. **Update the overview**
   - Read `<data-root>/wiki/overview.md` and update it following `templates/page-overview.md`
   - Add the new source to the Domains section, update Active Questions if relevant
```

- [ ] **Step 6: Update workflow step 7 (Append to the log)**

Replace step 7 (lines 45-48):

```markdown
7. **Append to the log**
   - Add an entry to `<data-root>/wiki/log.md` in the format: `## [YYYY-MM-DD] ingest | <Source Title>`
   - Briefly describe what was added and which pages were affected
   - following the format in `templates/log-entry.md`
```

- [ ] **Step 7: Update Guidelines section**

Replace the Guidelines section (lines 49-54):

```markdown
## Guidelines

- One source = one wiki page. If a source covers multiple distinct topics, create separate pages for each and link them.
- The wiki page should synthesize, not copy. Rewrite in your own words, organize by concept rather than following the source's structure.
- Always check for existing pages before creating a new one. If a page already covers this topic, update it instead of creating a duplicate.
- When updating existing pages, add a brief note at the end of the affected section: `*(Updated YYYY-MM-DD with info from [Source](../../raw/domain/source.md))*`
- **Follow template depth targets** — each template specifies word counts and content requirements per section. These are minimums, not maximums. Aim for thorough, substantive content.
- **Self-check with the Quality Checklist** — every template ends with a checklist. Review it before finalizing any page.
```

- [ ] **Step 8: Commit**

```bash
git add skills/wiki-ingest/SKILL.md
git commit -m "feat(wiki): add path resolution and template guidance to wiki-ingest skill"
```

---

### Task 5: Update wiki-query SKILL.md with path resolution

**Files:**
- Modify: `skills/wiki-query/SKILL.md`

- [ ] **Step 1: Add path resolution section after the title**

Insert after line 6 (`# Wiki Query`):

```markdown
## Path Resolution

All paths resolve through `data/config.json`. Read this file first to determine the data root:
- `dataDir: "."` (default) → data root is `data/` inside the plugin directory
- `dataDir: "/absolute/path"` → data root is the specified absolute path

All `wiki/` and `raw/` references below are relative to the resolved data root.
```

- [ ] **Step 2: Update workflow step 1**

Replace step 1 (lines 12-14):

```markdown
1. **Read the index**
   - Read `<data-root>/wiki/index.md` to find pages relevant to the question
   - Match the question topic against page titles and summaries in the index
```

- [ ] **Step 3: Update workflow step 2**

Replace step 2 (lines 16-19):

```markdown
2. **Read relevant wiki pages**
   - Read the most relevant pages identified from the index (all under `<data-root>/wiki/`)
   - If a page references other pages that seem relevant, read those too
   - Stop when you have enough context to answer the question
```

- [ ] **Step 4: Update workflow step 3**

Replace step 3 (lines 21-24):

```markdown
3. **Read raw sources if needed**
   - If the wiki pages lack detail on the specific question, read the underlying raw sources (under `<data-root>/raw/`) listed in the page's frontmatter `sources` field
   - Only read raw sources when the wiki synthesis is insufficient
```

- [ ] **Step 5: Update workflow step 5**

Replace step 5 (lines 31-37):

```markdown
5. **File substantial answers as new wiki pages**
   - If the answer required synthesizing multiple pages into a new insight (comparison, analysis, connection), create a new wiki page for it in `<data-root>/wiki/syntheses/` following `templates/page-synthesis.md`
   - Set `synthesis_type` based on the answer: `comparison` for side-by-side analysis, `analysis` for deep dives, `connection` for newly discovered relationships
   - This is how the wiki compounds — explorations become permanent knowledge, not lost in chat history
   - Only file substantial answers, not simple lookups
   - Update `<data-root>/wiki/index.md` with the new page entry following `templates/index-entry.md`
```

- [ ] **Step 6: Update Path Resolution section (the existing one)**

Replace the existing Path Resolution section (lines 48-49):

```markdown
## Path Resolution

All wiki paths resolve through `data/config.json`. The data root defaults to `data/` inside the plugin directory. When the skill references `wiki/index.md`, the full path is `<data-root>/wiki/index.md`. When a wiki page references a raw source like `raw/ai-tools/claude-code.md`, the full path is `<data-root>/raw/ai-tools/claude-code.md`.
```

- [ ] **Step 7: Commit**

```bash
git add skills/wiki-query/SKILL.md
git commit -m "feat(wiki): add path resolution to wiki-query skill"
```

---

### Task 6: Update wiki-lint SKILL.md with path resolution

**Files:**
- Modify: `skills/wiki-lint/SKILL.md`

- [ ] **Step 1: Add path resolution section after the title**

Insert after line 6 (`# Wiki Lint`):

```markdown
## Path Resolution

All paths resolve through `data/config.json`. Read this file first to determine the data root:
- `dataDir: "."` (default) → data root is `data/` inside the plugin directory
- `dataDir: "/absolute/path"` → data root is the specified absolute path

All `wiki/` and `raw/` references below are relative to the resolved data root.
```

- [ ] **Step 2: Update workflow step 1**

Replace step 1 (lines 12-14):

```markdown
1. **Scan all wiki pages**
   - Read every page in `<data-root>/wiki/sources/`, `<data-root>/wiki/entities/`, `<data-root>/wiki/concepts/`, and `<data-root>/wiki/syntheses/` (plus `<data-root>/wiki/overview.md`)
   - Build a mental model of the wiki's current state
```

- [ ] **Step 3: Update workflow step 3**

Replace step 3 (lines 25-29):

```markdown
3. **Check index completeness**
   - Compare `<data-root>/wiki/index.md` entries against actual files in the type directories
   - Verify entries exist in the correct type section (Sources, Entities, Concepts, Syntheses)
   - Flag any pages missing from the index
   - Flag any index entries pointing to non-existent pages
```

- [ ] **Step 4: Update workflow step 5**

Replace step 5 (lines 36-43):

```markdown
5. **Apply approved fixes**
   - Fix contradictions by updating the less authoritative page
   - Add missing cross-references
   - Update `<data-root>/wiki/index.md` to match actual pages
   - Set `status: needs-update` on pages that need fresh sources
   - Append a lint entry to `<data-root>/wiki/log.md`
   - When creating or updating pages, follow the appropriate page-type template in `templates/`
   - For entity/concept pages, also read the relevant domain guide at `<data-root>/wiki/entities/_guides/<domain>.md`
```

- [ ] **Step 5: Commit**

```bash
git add skills/wiki-lint/SKILL.md
git commit -m "feat(wiki): add path resolution to wiki-lint skill"
```

---

### Task 7: Update wiki-maintainer agent with path resolution

**Files:**
- Modify: `agents/wiki-maintainer.md`

- [ ] **Step 1: Add path resolution to How You Work section**

Replace the How You Work section (lines 22-25):

```markdown
## How You Work

1. Read `data/config.json` to resolve the data root path (default: `data/` inside the plugin directory)
2. Read `<data-root>/wiki/index.md` and `<data-root>/wiki/overview.md` to understand the wiki's current state
3. Read `CLAUDE.md` for wiki conventions, including page types, templates, and domain guides
4. Execute the requested operation following the same workflows as the wiki skills
5. Return a summary of all changes made
```

- [ ] **Step 2: Update Constraints section**

Replace the Constraints section (lines 66-70):

```markdown
## Constraints

- Never modify files in `<data-root>/raw/` — they are immutable
- Always update `<data-root>/wiki/index.md` when creating or moving pages
- Always append to `<data-root>/wiki/log.md` after completing an operation
- Follow the page format defined in CLAUDE.md. Use the appropriate page-type template from `skills/wiki-ingest/templates/` and the domain guide from `<data-root>/wiki/entities/_guides/<domain>.md` when creating entity pages.
- **Follow template depth targets and quality checklists** — templates specify word counts and content requirements. Produce thorough, long-form pages.
```

- [ ] **Step 3: Commit**

```bash
git add agents/wiki-maintainer.md
git commit -m "feat(wiki): add path resolution and template guidance to wiki-maintainer agent"
```

---

### Task 8: Enhance page-entity.md template

**Files:**
- Modify: `skills/wiki-ingest/templates/page-entity.md`

- [ ] **Step 1: Replace the entire template**

Write the full enhanced template:

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
sources:
  - wiki/sources/<source1>.md
status: draft | stable | needs-update
page_type: entity
---

# <Entity Name>

## Summary

<100-150 words. Must cover three things: (1) what this entity is — its category and scope, (2) what it does — its primary function or purpose, (3) its key differentiator — what sets it apart from similar entities. Write as a single cohesive paragraph, not a list.>

<example>
Claude Code is Anthropic's official CLI agent for Claude, providing an interactive terminal-based interface for software engineering tasks. It operates as a conversational coding assistant that can read and write files, execute shell commands, search codebases, and interact with external tools via MCP servers. Its key differentiator from other AI coding tools is its deep integration with the Claude model family — it leverages Claude's extended thinking, tool use, and prompt caching capabilities natively, rather than wrapping a generic LLM API. Claude Code also uniquely supports a plugin ecosystem via the Claude Plugin Builder, enabling community extensions.
</example>

## Key Areas

<Populate from the domain guide at `wiki/entities/_guides/<domain>.md`. Each area is a `###` subsection. Target 150-300 words per area. Each area MUST include: (1) a clear definition of what this area covers, (2) at least one concrete example or specific detail, (3) an edge case, limitation, or "gotcha" where applicable. Omit areas that have no applicable content from the source — do not pad with vague statements.>

<example>
### Configuration

Claude Code uses a hierarchical configuration system with settings files at multiple levels. The primary configuration file is `settings.json`, which can exist at the project level (`.claude/settings.json`), user level (`~/.claude/settings.json`), or enterprise managed level. Each level can override the one below it, with project settings taking highest priority for project-specific behavior.

Configuration covers several categories: permissions (which tools and commands are allowed), environment variables, MCP server connections, and behavioral preferences like model selection and thinking mode. A key detail is that permissions use glob patterns for file path matching — `src/**/*.ts` grants access to all TypeScript files under `src/`, while `!**/.env` explicitly denies access to environment files.

An important edge case: when both `settings.json` and `settings.local.json` exist in the same directory, the local file takes precedence. This is designed so that `.gitignore`d local settings can override committed project settings without modifying tracked files. However, this can cause confusion when debugging permission issues — always check both files.
</example>

<example>
### Agent Features

Claude Code's agent capabilities center on its tool-use architecture. The agent has access to a fixed set of built-in tools: Read, Edit, Write, Bash, Glob, Grep, WebFetch, and WebSearch. Each tool invocation is visible to the user and requires permission (unless pre-approved via settings). The agent can also invoke sub-agents via the Agent tool, enabling task delegation — for example, spawning a research agent to investigate a codebase while the main agent continues with implementation.

A concrete example of agent delegation: when running `/review`, the main agent spawns a code-reviewer subagent that reads the diff, checks against coding standards, and returns findings. The main agent then presents the review to the user. This separation allows the subagent to work with a focused context window.

A limitation to note: sub-agents cannot spawn further sub-agents — the delegation depth is limited to one level. This prevents recursive agent spawning but means complex multi-step workflows must be orchestrated by the main agent rather than delegated hierarchically.
</example>

## See Also

<Must use relative-path markdown links (e.g., `[Name](./page.md)` or `[Name](../sources/page.md)`). NOT wikilinks. At least 2 cross-references. Include both related entities and the source summary page this was derived from.>

- [Related Entity](./<entity>.md) — <one-line reason for the link>
- [Source Summary](../sources/<source>.md) — <the source this was derived from>

<!-- Quality Checklist (self-check before finalizing)
- [ ] Summary is 100-150 words and covers what/does/differentiator
- [ ] Each Key Area is 150-300 words with definition + example + edge case
- [ ] No Key Area is just 1-2 vague sentences
- [ ] Cross-references use relative-path markdown links (not wikilinks)
- [ ] No content is copied verbatim from source — all synthesized
- [ ] All placeholder values replaced with real content
- [ ] Frontmatter fields are complete and accurate
-->
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/templates/page-entity.md
git commit -m "feat(wiki): enhance page-entity template with depth targets, examples, and quality checklist"
```

---

### Task 9: Enhance page-source.md template

**Files:**
- Modify: `skills/wiki-ingest/templates/page-source.md`

- [ ] **Step 1: Replace the entire template**

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
source: raw/<path-to-source>.md
status: draft | stable | needs-update
page_type: source
---

# <Source Title>

## Summary

<100-150 words. Must cover three things: (1) what the source is — its type and origin, (2) what it covers — the scope of topics, (3) key takeaways — the most important things a reader should know. Write as a single cohesive paragraph.>

<example>
The Claude Code official documentation is a comprehensive reference covering all aspects of Anthropic's CLI coding agent. Sourced from the official docs site, it spans configuration, agent features, memory and context management, workflow automation, permissions and security, integrations, the Agent SDK, and troubleshooting. The key takeaway is that Claude Code is designed as a deeply integrated CLI tool — not just a chat wrapper — with native support for extended thinking, tool use, prompt caching, and a plugin ecosystem that enables community extensions.
</example>

## Key Points

<8-15 numbered points, each 1-2 sentences. Cover the most important information from the source. Prioritize actionable knowledge over abstract descriptions. Each point should be self-contained and specific.>

<example>
1. Configuration uses a hierarchical `settings.json` system with project, user, and enterprise levels, where higher-priority settings override lower ones.
2. The agent has 8 built-in tools (Read, Edit, Write, Bash, Glob, Grep, WebFetch, WebSearch) and can invoke sub-agents via the Agent tool.
3. Memory is managed through CLAUDE.md files at project and user levels, plus a conversation-level memory system that persists across sessions.
4. Permissions use glob patterns for file matching and support allow/deny lists for shell commands, file paths, web domains, and MCP tools.
5. MCP (Model Context Protocol) servers extend the agent with external tools and data sources, configured in settings.json.
6. The Agent SDK enables building custom agents on top of Claude Code's infrastructure, with support for tool use and streaming.
7. Hooks allow running shell commands before/after tool use events, enabling custom validation and automation.
8. Prompt caching reduces API costs by reusing context across turns — the system automatically caches CLAUDE.md and tool definitions.
</example>

## Notable Details

<Must include at least 3 specific items that would be hard to reconstruct from memory alone. These are the "save for later" details: exact commands, configuration values, version-specific behavior, edge cases, or non-obvious interactions. Format as a bulleted list with brief context for each item.>

<example>
- **Permission glob syntax**: `src/**/*.ts` matches all TypeScript files recursively; `!**/.env` explicitly denies. The `!` prefix for deny rules is not documented prominently.
- **Sub-agent depth limit**: Only one level of delegation is allowed — sub-agents cannot spawn further sub-agents.
- **settings.local.json precedence**: When both `settings.json` and `settings.local.json` exist, the local file wins. The local file is typically `.gitignore`d.
- **CLAUDE.md auto-loading**: Files named `CLAUDE.md` in the project root and `~/.claude/CLAUDE.md` are automatically loaded into every conversation context.
</example>

## See Also

<Must use relative-path markdown links. Link to the entity page this source describes.>

- [Entity Page](../entities/<entity>.md) — <the entity this source describes>

<!-- Quality Checklist (self-check before finalizing)
- [ ] Summary is 100-150 words and covers what/covers/takeaways
- [ ] Key Points has 8-15 numbered items, each 1-2 sentences
- [ ] Notable Details has at least 3 specific, hard-to-reconstruct items
- [ ] Cross-references use relative-path markdown links (not wikilinks)
- [ ] No content is copied verbatim from source — all synthesized
- [ ] All placeholder values replaced with real content
- [ ] Frontmatter fields are complete and accurate
-->
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/templates/page-source.md
git commit -m "feat(wiki): enhance page-source template with depth targets, examples, and quality checklist"
```

---

### Task 10: Enhance page-concept.md template

**Files:**
- Modify: `skills/wiki-ingest/templates/page-concept.md`

- [ ] **Step 1: Replace the entire template**

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
sources:
  - wiki/sources/<source1>.md
status: draft | stable | needs-update
page_type: concept
---

# <Concept Name>

## Summary

<100-150 words. Must cover three things: (1) what the concept is — a clear definition, (2) why it matters — the problem it solves or the value it provides, (3) what distinguishes it from related concepts. Write as a single cohesive paragraph.>

<example>
The LLM Wiki pattern is a knowledge management approach where an LLM maintains a structured wiki from raw source documents. Unlike traditional wikis where humans write and organize content, the LLM Wiki delegates all bookkeeping — summarizing, cross-referencing, filing, and updating — to the LLM. The human's role shifts to curating sources, directing analysis, and asking questions. This pattern matters because it makes personal knowledge bases viable for individuals who lack the time for manual wiki maintenance, while producing more structured and cross-referenced output than simple note-taking tools.
</example>

## Core Idea

<200-400 words. This is the heart of the concept page. Must include: (1) the mental model — how to think about this concept, (2) the key insight — the non-obvious thing that makes it work, (3) how it works step-by-step — the mechanism or process. Write in depth; this section should leave the reader with a solid understanding they could explain to someone else.>

<example>
The LLM Wiki pattern is built on a three-layer architecture that separates concerns between source material, synthesized knowledge, and schema conventions.

The first layer is **raw sources** — immutable documents that serve as ground truth. These are never modified after creation, which means they can always be used to re-synthesize wiki pages if the synthesized layer becomes stale or contradictory. Think of raw sources as the "primary sources" in academic research.

The second layer is **wiki pages** — LLM-generated synthesis organized by type (source summaries, entities, concepts, syntheses). Each page type has a different structure optimized for its purpose: entity pages have domain-specific Key Areas, concept pages explore ideas in depth, and synthesis pages capture insights that emerge from cross-referencing multiple sources. The key insight is that organizing by page type rather than by domain produces better structure — an entity page and a synthesis page about the same domain have fundamentally different shapes.

The third layer is **schema conventions** (embodied in CLAUDE.md and templates) — the rules that tell the LLM how to structure the wiki. This layer is co-evolved between human and LLM over time, as you discover what works for your domain.

The workflow is: ingest a source → the LLM reads it, discusses key points with the human, then writes source summary + entity/concept pages, updates the index and overview, and adds cross-references to related pages. Over time, the wiki compounds — query answers get filed as synthesis pages, creating new connections that weren't visible from any single source.
</example>

## Applications

<2+ concrete scenarios, each 50-100 words. Show how the concept manifests in different contexts. Each scenario should be specific enough that a reader can see how to apply the concept themselves.>

<example>
**Personal knowledge base for a developer**: A developer collects documentation from multiple AI coding tools (Claude Code, Cursor, Codex). Each tool's docs get ingested as a source, producing entity pages with structured Key Areas. When the developer wonders "which tool has the best permission model?", a query produces a comparison synthesis page that persists for future reference.

**Research notebook for a team**: A research team ingests papers, meeting notes, and internal docs. The wiki grows to include concept pages for key ideas and synthesis pages connecting findings across sources. New team members can query the wiki to get up to speed without reading every raw source.
</example>

## Trade-offs

<Must include: (1) at least one limitation or scenario where the concept breaks down, (2) at least one alternative approach and when to prefer it. Be honest — every concept has weaknesses.>

<example>
The main limitation is **trust in synthesis quality**. The LLM may introduce subtle errors during summarization that are hard to detect without re-reading the original source. This is mitigated by the raw source layer (always available for verification) and the lint skill (which checks for contradictions), but it remains a fundamental trade-off: you gain maintenance-free structure at the cost of potential synthesis errors.

An alternative approach is **Zettelkasten** (manual note-linking), which gives the human full control over connections and ensures every link represents a genuine insight. Prefer Zettelkasten when the domain requires precise, expert-validated connections (e.g., legal reasoning, medical knowledge). Prefer LLM Wiki when the volume of sources makes manual maintenance impractical and approximate synthesis is acceptable.
</example>

## See Also

<Must use relative-path markdown links. At least 2 cross-references.>

- [Related Concept](./<concept>.md) — <one-line reason for the link>
- [Source Summary](../sources/<source>.md) — <the source this was derived from>

<!-- Quality Checklist (self-check before finalizing)
- [ ] Summary is 100-150 words and covers what/matters/distinguishes
- [ ] Core Idea is 200-400 words with mental model + key insight + step-by-step
- [ ] Applications has 2+ concrete scenarios, each 50-100 words
- [ ] Trade-offs includes at least 1 limitation and 1 alternative
- [ ] Cross-references use relative-path markdown links (not wikilinks)
- [ ] No content is copied verbatim from source — all synthesized
- [ ] All placeholder values replaced with real content
- [ ] Frontmatter fields are complete and accurate
-->
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/templates/page-concept.md
git commit -m "feat(wiki): enhance page-concept template with depth targets, examples, and quality checklist"
```

---

### Task 11: Enhance page-synthesis.md template

**Files:**
- Modify: `skills/wiki-ingest/templates/page-synthesis.md`

- [ ] **Step 1: Replace the entire template**

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
sources:
  - wiki/entities/<entity1>.md
  - wiki/entities/<entity2>.md
status: draft | stable | needs-update
page_type: synthesis
synthesis_type: comparison | analysis | connection
---

# <Synthesis Title>

## Summary

<100-150 words. Must state the insight or connection discovered. For comparisons: what are the key differences and the overall verdict. For analysis: what argument is being developed and the conclusion. For connections: what relationship was discovered and why it matters.>

<example>
Comparing Claude Code, Cursor, and Codex reveals three distinct approaches to AI coding assistance. Claude Code prioritizes deep model integration and plugin extensibility, Cursor focuses on editor-native AI with a polished CLI agent, and Codex emphasizes cloud-based sandboxed execution for safety. The key finding is that these tools are not direct substitutes — each excels in a different workflow context, and the best choice depends on whether you need local control (Claude Code), editor integration (Cursor), or isolated execution (Codex).
</example>

## Analysis

<The core content. Structure depends on synthesis_type:>

### For comparison (synthesis_type: comparison)

<Must include: (1) a comparison table with key dimensions as rows and entities as columns, (2) a narrative analysis of each dimension (50-100 words per dimension), (3) a Verdict section with a clear recommendation.>

<example>
| Dimension | Claude Code | Cursor | Codex |
|-----------|-------------|--------|-------|
| Execution | Local CLI | Local CLI + Editor | Cloud sandbox |
| Model access | Claude only | Multi-provider | OpenAI only |
| Plugin system | Yes (Plugin Builder) | Limited | No |
| Permissions | Glob-based allow/deny | Glob-based allow/deny | Sandboxed by default |
| MCP support | Full | Full | No |

**Execution model**: Claude Code and Cursor run locally, giving developers full control over their environment. Codex runs in a cloud sandbox, which is safer for untrusted code but requires network access and has latency overhead.

**Verdict**: For daily development with trusted codebases, Claude Code or Cursor are preferable due to local execution and richer tool access. For reviewing untrusted code or running in CI, Codex's sandboxed model provides better safety guarantees.
</example>

### For analysis (synthesis_type: analysis)

<Must include: (1) a clear thesis statement, (2) evidence from source pages supporting the thesis, (3) a counter-argument or limitation, (4) a conclusion. Target 300-500 words total.>

### For connection (synthesis_type: connection)

<Must include: (1) what the connected pages have in common, (2) how they differ in approach or scope, (3) what new understanding emerges from the connection, (4) why this connection matters. Target 300-500 words total.>

## Implications

<Must include: (1) at least one actionable recommendation — what should the reader do differently based on this synthesis, (2) at least one new question raised — what should be investigated next.>

<example>
**Recommendation**: Teams evaluating AI coding tools should test all three in their actual workflow rather than choosing based on feature lists alone. The execution model difference (local vs. cloud) has more practical impact than any feature comparison suggests.

**Open question**: How will MCP server ecosystems evolve across tools? If MCP becomes a universal standard, the plugin advantage of Claude Code may diminish, making execution model the primary differentiator.
</example>

## See Also

<Must use relative-path markdown links. Link to all source pages that contributed to this synthesis.>

- [Source Page 1](../entities/<page1>.md) — <why this source is relevant>
- [Source Page 2](../entities/<page2>.md) — <why this source is relevant>

<!-- Quality Checklist (self-check before finalizing)
- [ ] Summary is 100-150 words and states the insight/connection
- [ ] Analysis follows the correct structure for synthesis_type
- [ ] Comparison has table + narrative + verdict
- [ ] Analysis has thesis + evidence + counter-argument + conclusion
- [ ] Connection has commonality + difference + new understanding + why it matters
- [ ] Implications has at least 1 recommendation and 1 new question
- [ ] Cross-references use relative-path markdown links (not wikilinks)
- [ ] No content is copied verbatim from source — all synthesized
- [ ] All placeholder values replaced with real content
- [ ] Frontmatter fields are complete and accurate
-->
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/templates/page-synthesis.md
git commit -m "feat(wiki): enhance page-synthesis template with type-specific structure, examples, and quality checklist"
```

---

### Task 12: Enhance page-overview.md template

**Files:**
- Modify: `skills/wiki-ingest/templates/page-overview.md`

- [ ] **Step 1: Replace the entire template**

```markdown
---
tags: [overview]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
status: draft | stable | needs-update
page_type: overview
---

# Wiki Overview

## Summary

<100-150 words. Must cover: (1) what this wiki covers — the domains and scope, (2) the big picture — the overarching theme or thesis that connects the domains, (3) the current state — how mature the wiki is and what's actively being developed.>

<example>
This wiki covers AI coding tools and the LLM Wiki pattern itself. The overarching theme is the emergence of LLM-powered developer tools that combine conversational AI with direct code manipulation capabilities. The wiki currently has five entity pages covering the major tools (Claude Code, Cursor, Codex, OpenCode, Plugin Builder), with active investigation into how their permission models and plugin ecosystems compare. The LLM Wiki concept page documents the pattern this wiki itself follows.
</example>

## Domains

<For each domain, 100-200 words. Must include: (1) what the domain covers, (2) key insights discovered so far, (3) links to the most important entity and concept pages in this domain. Each domain should give a reader enough context to understand the domain without reading every page.>

<example>
### ai-tools

Covers AI-powered coding assistants and their ecosystems. Five tools are currently documented: Claude Code (Anthropic's CLI agent with deep model integration and plugin support), Cursor (editor-native AI with a CLI agent), Codex (OpenAI's cloud-sandboxed coding agent), OpenCode (provider-agnostic CLI supporting 75+ LLMs), and Plugin Builder (the Claude Code extension framework). Key insight: these tools differ most fundamentally in their execution model (local vs. cloud) and extensibility (plugin system vs. monolithic), not in their feature lists. See [Claude Code](entities/claude-code.md), [Cursor](entities/cursor.md), [Codex](entities/codex.md), [OpenCode](entities/opencode.md), [Plugin Builder](entities/plugin-builder.md).
</example>

## Active Questions

<Must be specific, actionable questions — not vague statements. Each question should suggest what source or analysis could resolve it. 3-5 questions is a good target.>

<example>
- **How do permission models compare across tools?** — A comparison synthesis page would resolve this. Need to verify Codex's sandboxing details from official docs.
- **Is MCP becoming a universal standard?** — Need to ingest MCP specification docs and check which tools have adopted it beyond Claude Code and Cursor.
- **What's the real-world performance difference between local and cloud execution?** — Would need benchmark data or user reports as sources.
</example>

## Recent Activity

<Summarize the last 5 log entries with dates. Each entry: date + operation + one-line summary. Gives context for what's been happening without requiring the reader to open the log.>

<example>
- 2026-05-22: ingest | OpenCode Documentation — created entity page with 9 Key Areas
- 2026-05-22: ingest | Plugin Builder Documentation — created entity page with 10 Key Areas
- 2026-05-22: ingest | Cursor Documentation — created entity page with 6 Key Areas
- 2026-05-21: restructure | Template Standardization — migrated wiki to type-based directories with templates
- 2026-05-20: migrate | Initial Wiki Setup — migrated existing pages to new format
</example>

## See Also

- [Index](./index.md) — full page catalog
- [Log](./log.md) — chronological activity record

<!-- Quality Checklist (self-check before finalizing)
- [ ] Summary is 100-150 words and covers scope/theme/state
- [ ] Each Domain entry is 100-200 words with links to key pages
- [ ] Active Questions are specific and suggest how to resolve them
- [ ] Recent Activity has last 5 log entries with dates
- [ ] Cross-references use relative-path markdown links (not wikilinks)
- [ ] All placeholder values replaced with real content
- [ ] Frontmatter fields are complete and accurate
-->
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/templates/page-overview.md
git commit -m "feat(wiki): enhance page-overview template with depth targets, examples, and quality checklist"
```

---

### Task 13: Enhance raw-source.md template

**Files:**
- Modify: `skills/wiki-ingest/templates/raw-source.md`

- [ ] **Step 1: Replace the entire template**

```markdown
---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
source_url: <URL or "local">
media: web | doc-index | file | pasted | transcript | notes
domain: <domain identifier for routing>
status: unprocessed | processed
---

# <Source Title>

<Raw source content follows. This file is immutable after creation.>

<!-- Field guidance:
- tags: use kebab-case, include the domain as a tag (e.g., [ai-tools, cli, coding])
- date: the date this source was collected, not the publication date of the original
- source_url: the origin URL, or "local" if the source was pasted or is a local file
- media:
    - web: full article or page fetched from the internet
    - doc-index: a structured index of documentation URLs (common for tool docs)
    - file: a local file provided by the user
    - pasted: text pasted directly by the user
    - transcript: a conversation or meeting transcript
    - notes: the user's own notes or observations
- domain: kebab-case identifier matching the directory name under raw/ (e.g., "ai-tools" for raw/ai-tools/)
- status: set to "unprocessed" on creation, changed to "processed" after wiki-ingest completes
-->
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/templates/raw-source.md
git commit -m "feat(wiki): enhance raw-source template with field guidance comments"
```

---

### Task 14: Create eval rubric

**Files:**
- Create: `skills/wiki-ingest/evals/rubric.md`

- [ ] **Step 1: Create the rubric file**

```markdown
# Wiki Ingest Quality Rubric

Used by the LLM judge to score wiki page output quality.

## Scoring

Score each dimension 0-5. Calculate the weighted total (0-5 scale). Passing threshold: 3.5/5.

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 25% | Are all key information from the source extracted and present in the wiki page? |
| Accuracy | 25% | Is the content factually consistent with the source material? No invented details. |
| Structure | 15% | Does the page follow its template? All required sections present, correct frontmatter. |
| Depth | 20% | Does each section meet the depth target? Not just 1-2 sentence summaries. |
| Cross-references | 15% | Are links present, correctly formatted (relative-path markdown), and pointing to relevant pages? |

## Dimension Details

### Completeness (25%)

| Score | Criteria |
|-------|----------|
| 0 | Major information from the source is missing — key features, concepts, or details not mentioned |
| 1 | Several important points missing; page covers less than half the source's content |
| 2 | Some important points missing; page covers about half the source's content |
| 3 | Most important points present; minor details may be missing |
| 4 | Nearly all important points present; only trivial details missing |
| 5 | All key information extracted and synthesized; nothing important is missing |

### Accuracy (25%)

| Score | Criteria |
|-------|----------|
| 0 | Contains factual errors that contradict the source material |
| 1 | Multiple errors or significant misrepresentations |
| 2 | A few errors or oversimplifications that change the meaning |
| 3 | Mostly accurate with minor imprecisions that don't change meaning |
| 4 | Accurate with only trivial imprecisions |
| 5 | Fully consistent with source material; no errors or misrepresentations |

### Structure (15%)

| Score | Criteria |
|-------|----------|
| 0 | Does not follow template at all; missing major sections |
| 1 | Follows template loosely; several sections missing or misplaced |
| 2 | Follows template partially; some sections present, some missing |
| 3 | Follows template mostly; all major sections present but some subsections missing |
| 4 | Follows template well; all sections present with minor formatting issues |
| 5 | Follows template completely; all sections present, correct frontmatter, proper formatting |

### Depth (20%)

| Score | Criteria |
|-------|----------|
| 0 | Every section is 1-2 sentences; no substance |
| 1 | Most sections are shallow; only 1-2 sentences each |
| 2 | Some sections have depth; others are shallow |
| 3 | Most sections meet minimum depth targets |
| 4 | All sections meet depth targets with some exceeding them |
| 5 | All sections are thorough with definition + example + edge case where applicable |

### Cross-references (15%)

| Score | Criteria |
|-------|----------|
| 0 | No cross-references at all, or all use wrong format (wikilinks instead of relative paths) |
| 1 | Very few cross-references; most expected links missing |
| 2 | Some cross-references present but format inconsistent or links point to wrong targets |
| 3 | Most expected cross-references present; format mostly correct |
| 4 | All expected cross-references present with correct format |
| 5 | All expected cross-references present, correctly formatted, and linking to the most relevant pages |

## Output Format

Return scores as JSON:

```json
{
  "completeness": { "score": 0, "reason": "..." },
  "accuracy": { "score": 0, "reason": "..." },
  "structure": { "score": 0, "reason": "..." },
  "depth": { "score": 0, "reason": "..." },
  "cross_references": { "score": 0, "reason": "..." },
  "weighted_total": 0.0,
  "pass": false
}
```

Weighted total = completeness×0.25 + accuracy×0.25 + structure×0.15 + depth×0.20 + cross_references×0.15
Pass = weighted_total >= 3.5
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/evals/rubric.md
git commit -m "feat(wiki): add LLM-as-judge eval rubric with 5 scoring dimensions"
```

---

### Task 15: Create LLM judge prompt

**Files:**
- Create: `skills/wiki-ingest/evals/judge-prompt.md`

- [ ] **Step 1: Create the judge prompt file**

```markdown
You are an expert evaluator for wiki page quality. You will be given:

1. A **rubric** defining 5 scoring dimensions (completeness, accuracy, structure, depth, cross-references)
2. A **raw source** document (the input)
3. An **expected output** (a golden sample wiki page showing target quality)
4. An **actual output** (the wiki page to evaluate)

Your job: score the actual output against the rubric, comparing it to both the raw source (for completeness/accuracy) and the expected output (for structure/depth/cross-references quality level).

## Evaluation Process

1. Read the raw source carefully. Note all key information points.
2. Read the expected output. Note the depth, structure, and cross-reference quality.
3. Read the actual output. Compare against the source and expected output.
4. Score each dimension per the rubric. Provide a specific reason for each score.
5. Calculate the weighted total and determine pass/fail.

## Important Rules

- Score based on what's actually in the output, not what you wish was there
- Be strict on accuracy — any factual error vs. the source is a real problem
- Be strict on depth — 1-2 sentence sections are not acceptable for any page type
- Be lenient on cross-reference targets — if a link points to a reasonable page even if not the exact same as the expected output, that's fine
- Do not penalize for different wording — only penalize for missing information or wrong information
- The expected output shows the TARGET quality level, not the exact content to match

## Output

Return ONLY valid JSON in this format:

```json
{
  "completeness": { "score": 0, "reason": "specific reason referencing what's missing or present" },
  "accuracy": { "score": 0, "reason": "specific reason referencing any errors or consistency" },
  "structure": { "score": 0, "reason": "specific reason about template adherence" },
  "depth": { "score": 0, "reason": "specific reason about section depth with examples" },
  "cross_references": { "score": 0, "reason": "specific reason about link presence and format" },
  "weighted_total": 0.0,
  "pass": false
}
```
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/evals/judge-prompt.md
git commit -m "feat(wiki): add LLM judge system prompt for eval scoring"
```

---

### Task 16: Create eval input samples

**Files:**
- Create: `skills/wiki-ingest/evals/samples/input/cursor.md`
- Create: `skills/wiki-ingest/evals/samples/input/opencode.md`
- Create: `skills/wiki-ingest/evals/samples/input/plugin-builder.md`

- [ ] **Step 1: Create evals directory structure**

```bash
cd /Users/lijunyi/road/claude-harness/plugins/wiki
mkdir -p skills/wiki-ingest/evals/samples/input
mkdir -p skills/wiki-ingest/evals/samples/expected
mkdir -p skills/wiki-ingest/evals/results
```

- [ ] **Step 2: Copy cursor raw source as eval input**

```bash
cp data/raw/ai-tools/cursor.md skills/wiki-ingest/evals/samples/input/cursor.md
```

- [ ] **Step 3: Copy opencode raw source as eval input**

```bash
cp data/raw/ai-tools/opencode.md skills/wiki-ingest/evals/samples/input/opencode.md
```

- [ ] **Step 4: Copy plugin-builder raw source as eval input**

```bash
cp data/raw/ai-tools/plugin-builder.md skills/wiki-ingest/evals/samples/input/plugin-builder.md
```

- [ ] **Step 5: Create results/.gitkeep**

```bash
touch skills/wiki-ingest/evals/results/.gitkeep
```

- [ ] **Step 6: Commit**

```bash
git add skills/wiki-ingest/evals/samples/input/ skills/wiki-ingest/evals/results/.gitkeep
git commit -m "feat(wiki): add eval input samples and results directory"
```

---

### Task 17: Create golden sample for cursor entity page

**Files:**
- Create: `skills/wiki-ingest/evals/samples/expected/cursor-entity.md`

This is a hand-curated golden sample demonstrating the target quality level for a short source (~500 words) → entity page. It follows the enhanced page-entity template with 150-300 word Key Areas.

- [ ] **Step 1: Write the golden sample**

```markdown
---
tags: [ai-tools, editor, coding]
date: 2026-05-22
last_updated: 2026-05-22
sources:
  - wiki/sources/cursor-docs.md
status: stable
page_type: entity
---

# Cursor

## Summary

Cursor is an AI-powered code editor developed by Cursor Inc. that integrates intelligent coding assistance directly into the editing experience. Unlike standalone CLI agents, Cursor combines a full-featured code editor with an AI assistant, providing editor-native completions, chat, and code generation alongside traditional editing capabilities. Its key differentiator is the dual-interface design: a polished editor experience for interactive work and a CLI agent (`cursor agent`) for automated and headless workflows, connected through a shared configuration and permission system.

## Key Areas

### Overview

Cursor is built around the idea that AI assistance should be native to the editing experience rather than bolted on as a separate tool. The editor provides inline AI completions, a chat panel for conversational coding, and code generation features that operate directly on the open file. Beyond the editor, the CLI agent extends Cursor's capabilities to terminal-based and automated workflows — it can be used interactively or in headless mode for CI/CD integration. The two interfaces share configuration, permissions, and the same underlying AI models, creating a consistent experience whether you're in the editor or the terminal.

A concrete example: a developer can use the editor's chat to prototype a function, then switch to the CLI agent to run the same AI capabilities on a batch of files via headless mode. The configuration and rules defined in the editor apply to the CLI agent as well.

An important edge case: the CLI agent and editor are separate processes — closing the editor does not affect running CLI agent sessions, and vice versa. This is by design for reliability, but it means state (like active MCP connections) is not shared between them.

### CLI

The Cursor CLI agent provides a comprehensive command-line interface accessible via the `cursor agent` command. The primary subcommands are: `agent` for the main interactive agent mode, `agent login`/`agent logout` for authentication, `agent status`/`agent whoami` for checking connection state, and `agent models` for listing available AI models. Session management is supported through `agent ls` (list sessions) and `agent resume <session>` (resume a previous session), enabling developers to pick up where they left off.

For automation, headless mode (`cursor agent -p "<prompt>" --force`) enables non-interactive execution suitable for CI/CD pipelines and scripted workflows. The `--force` flag skips all confirmation prompts, which is essential for unattended execution but should be used with caution since it grants the agent full autonomy within its permission boundaries.

A notable detail: shell integration can be installed via `agent install-shell-integration`, which enhances terminal support by allowing the agent to better understand the shell environment. However, this integration is optional — the CLI agent works without it, just with reduced context about the shell state.

### Hooks

The hooks system provides two primary event types that allow custom code to run at key points in the agent's execution cycle. `preToolUse` hooks fire before a tool executes and can take three actions: allow (proceed), deny (block the tool call), or modify the tool input (change parameters before execution). `postToolUse` hooks fire after successful tool execution and are primarily useful for auditing (logging what was done) and injecting context (adding information to the agent's awareness after a tool runs).

Matcher support allows filtering hooks by tool type — for example, targeting only "Shell" tool invocations to add custom validation for shell commands without affecting file operations. Third-party hooks are also supported, enabling community extensions to the hook system.

A limitation: hooks run synchronously, meaning a slow `preToolUse` hook will delay the tool execution. There is no timeout mechanism built into the hook system, so a misbehaving hook can effectively freeze the agent. This is important to keep in mind when writing hooks that make network calls or perform heavy computation.

### MCP

Model Context Protocol (MCP) support enables Cursor to integrate with external tools and data sources through a standardized interface. MCP servers can be managed via CLI commands: `agent mcp list` to view currently configured servers, `agent mcp add` to register new ones, and `agent mcp login <identifier>` for authentication with servers that require it. Configuration is also supported through an `mcp.json` file for declarative server setup, which is useful for project-specific MCP configurations that can be committed to version control.

MCP tools provided by connected servers appear alongside Cursor's built-in tools and can be used by the agent in the same way. If needed, MCP tools can be disabled globally through configuration — this is useful when a server is causing issues and you want to quickly disable it without removing the configuration.

An edge case: MCP server connections are established at agent startup. Adding a new server via `agent mcp add` requires restarting the agent session for the new server to become available. There is no hot-reload mechanism for MCP servers.

### Permissions

Permissions are configured using allow and deny lists across four categories: shell commands, file paths, web domains, and MCP tools. File path permissions support glob pattern matching — for example, `src/**/*.ts` allows access to all TypeScript files under `src/`, while `!**/.env` explicitly denies access to environment files. The deny list takes precedence over the allow list when both match, following a "deny by default" security philosophy.

This four-category approach provides fine-grained control over what the agent can access and execute, balancing autonomy with safety. A developer can allow broad file access while restricting specific sensitive directories, or allow general shell commands while blocking dangerous ones like `rm -rf`.

A practical gotcha: glob patterns in file path permissions are evaluated relative to the project root, not the current working directory. This means `*.json` matches JSON files only in the project root, not in subdirectories. Use `**/*.json` to match recursively.

### Rules

Custom rules define project-specific behavioral constraints for the agent, guiding it to align with team conventions, coding standards, or project-specific requirements. Rules can be generated interactively using the `agent generate-rule` command, which walks through a series of questions to produce a rule definition. Rules can also be written manually.

Rules are loaded from project-level configuration and apply to all agent sessions within that project. They provide a way to encode team knowledge — for example, "always use absolute imports in this project" or "never modify files in the generated/ directory" — so that the agent follows the same conventions as the human developers.

A limitation: rules are advisory, not enforced. The agent will attempt to follow them, but complex or contradictory rules may be applied inconsistently. For hard security boundaries, use the permissions system instead of rules.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's approach to CLI agent and permissions
- [OpenCode](./opencode.md) — Compare with OpenCode's provider-agnostic approach
- [Codex](./codex.md) — Compare with Codex's cloud-sandboxed execution model
- [Cursor Docs Source](../sources/cursor-docs.md) — The source document this page was derived from
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/evals/samples/expected/cursor-entity.md
git commit -m "feat(wiki): add golden sample entity page for cursor eval"
```

---

### Task 18: Create golden sample for opencode entity page

**Files:**
- Create: `skills/wiki-ingest/evals/samples/expected/opencode-entity.md`

This is a hand-curated golden sample for a medium source (~1500 words) → entity page with many Key Areas.

- [ ] **Step 1: Write the golden sample**

```markdown
---
tags: [ai-tools, cli, coding]
date: 2026-05-22
last_updated: 2026-05-22
sources:
  - wiki/sources/opencode-docs.md
status: stable
page_type: entity
---

# OpenCode

## Summary

OpenCode is a provider-agnostic AI coding CLI that supports over 75 LLM providers through a single interface, allowing developers to use models from Anthropic, OpenAI, Google, and many others without being locked into one vendor. It offers multiple interaction modes — a terminal UI (TUI), CLI, web interface, and IDE integration — along with a rich extension system featuring skills, MCP servers, plugins, and custom tools. Its key differentiator is the provider-agnostic architecture: unlike Claude Code (Claude-only) or Codex (OpenAI-only), OpenCode treats the LLM as a pluggable component, making it the only tool that natively supports multi-model workflows and model switching within a single session.

## Key Areas

### Overview

OpenCode is designed around the principle that developers should choose their AI coding tools independently of their LLM provider. It supports 75+ providers through a unified configuration system, with a "Zen" mode that offers curated model selections for users who don't want to choose. The tool provides four interaction interfaces: a terminal UI (TUI) as the primary interactive mode, a CLI for scripted and headless usage, a web interface for browser-based access, and IDE integration for editor-embedded workflows. GitHub and GitLab integrations connect directly to repository workflows, enabling AI-assisted code review and issue management.

A concrete example: a team can configure OpenCode to use Claude for complex reasoning tasks and a faster model (like Haiku) for simple edits, switching between them within the same session based on task complexity. This multi-model approach is unique among AI coding tools.

An important edge case: while OpenCode supports many providers, the quality of the experience varies significantly by provider. Features like extended thinking, tool use, and prompt caching are provider-specific — not all models support all features. The configuration documentation notes which features require specific providers.

### Interfaces

OpenCode provides four distinct ways to interact with the agent, each optimized for a different workflow context. The TUI (terminal UI) is the primary interactive interface with full customization support — themes, keybindings, and layout can all be configured. The CLI mode enables scripted and headless usage, suitable for automation and CI/CD integration. A web interface provides browser-based access, which is useful for remote development scenarios. IDE integration brings OpenCode into the editor environment.

Zen mode offers a simplified experience with curated model options, removing the burden of model selection. The Share feature enables collaboration by allowing users to share session state and outputs. GitHub and GitLab integrations connect directly to repository workflows for AI-assisted code review and issue management.

A practical detail: the TUI and CLI modes share the same configuration but have separate keybinding and theme settings. Customizing the TUI appearance does not affect CLI behavior, and vice versa.

### Configuration

Configuration uses JSON or JSONC files with `$schema` support for validation and autocompletion in editors. The system defines eight priority levels that determine which settings take precedence, ranging from remote configuration (highest priority) down to macOS managed preferences (lowest). This hierarchical approach allows organizational policies to override individual preferences while still permitting project-specific customization.

TUI-specific configuration allows customizing the terminal interface appearance and behavior independently from the core agent configuration. Network and enterprise configurations support organizational deployments with proxy settings, authentication, and compliance requirements.

A notable edge case: the eight priority levels can create confusing behavior when multiple configuration sources are active. The documentation recommends using `opencode config list` to see the effective configuration and which source each setting comes from. Without this, debugging why a particular setting isn't taking effect can be frustrating.

### Built-in Tools

OpenCode ships with 12 built-in tools that cover the core operations needed for AI-assisted coding: bash (shell command execution), edit (file editing with diff support), write (file creation), read (file reading), grep (content search with regex support), glob (file pattern matching), apply_patch (patch application for precise edits), skill (skill invocation for workflow automation), todowrite (task tracking within sessions), webfetch (HTTP requests for API interaction), websearch (web search for documentation lookup), question (user prompts for clarification), and lsp (language server protocol integration for code intelligence).

The LSP tool is particularly notable — it provides real-time code intelligence (go-to-definition, find-references, diagnostics) without requiring a separate language server process. This gives the agent access to the same code understanding that IDEs provide.

A limitation: the built-in tools cannot be disabled or overridden. If you need different behavior for a tool (e.g., a sandboxed bash), you must use the permissions system to restrict it rather than replacing it.

### Built-in Agents

OpenCode organizes its agents into three tiers. Primary agents handle the main workflows: Build (for implementation and code modification tasks) and Plan (for analysis and planning before implementation). Subagents handle specialized work: General for broad tasks that don't fit the primary categories, Explore for codebase navigation and understanding, and Scout for targeted searching and investigation.

Hidden system agents manage infrastructure that users don't directly invoke: Compaction for context window management (keeping conversations within model limits), Title for automatic session naming, and Summary for conversation summarization. These run automatically based on triggers.

A practical detail: the Build and Plan agents can be selected explicitly via configuration or CLI flags, but the subagent routing is automatic based on the task type. Users cannot directly invoke Explore or Scout — they are dispatched by the primary agents when needed.

### Permissions

The permission model defines three actions: allow (execute without prompting), ask (require user approval before execution), and deny (block execution entirely). Permissions use glob patterns for file matching, and the last matching rule wins in case of conflicts — this is a "most specific match wins" approach that provides predictable behavior.

For example, if you have `allow: src/**` followed by `deny: src/secrets/**`, a file in `src/secrets/` will be denied because the deny rule is more specific (appears later). This ordering-based resolution is simple but requires careful rule ordering to avoid unintended access patterns.

A gotcha: the "last matching rule wins" behavior means rule order matters critically. Adding a new allow rule at the end of the configuration can unintentionally override earlier deny rules. The documentation recommends placing deny rules last to avoid this pitfall.

### Skills

Skills follow the SKILL.md format with YAML frontmatter defining the skill's name and description, and a markdown body containing the workflow instructions. Discovery paths include `.opencode/skills/` at the project level and `~/.config/opencode/skills/` globally. OpenCode is also compatible with skills from `.claude/skills/` and `.agents/skills/` directories, enabling cross-tool skill reuse — a skill written for Claude Code can work in OpenCode without modification.

This cross-compatibility is a significant advantage for teams that use multiple AI coding tools. A team can maintain a single set of skills and use them across Claude Code, OpenCode, and any other tool that supports the SKILL.md format.

A limitation: while the skill format is compatible, the tool names and capabilities available within a skill may differ between tools. A skill that uses Claude Code's `Agent` tool will not work in OpenCode if OpenCode doesn't provide an equivalent tool. The skill author must be aware of tool availability across platforms.

### Custom Tools

Custom tools are written as TypeScript files using the `tool()` helper function with Zod schemas for input validation. This approach provides type-safe, validated tool implementations that integrate seamlessly with the agent framework. The Zod schema serves double duty: it validates inputs at runtime and provides type information to the LLM for correct tool invocation.

Custom tools are discovered from configured directories and appear alongside built-in tools in the agent's tool list. They can be used in the same way as built-in tools — the agent decides when to invoke them based on the task context.

An edge case: custom tools run in the same process as the OpenCode agent, which means a poorly written tool (e.g., one with an infinite loop or memory leak) can crash the entire agent. There is no sandboxing for custom tools, unlike Codex's approach of running everything in isolated containers.

### Plugins

Plugins are TypeScript modules distributed as npm packages that can hook into key events in the OpenCode lifecycle. Unlike skills (which are markdown-based workflow instructions) and custom tools (which add individual tool capabilities), plugins can modify the agent's behavior at a structural level — intercepting events, adding middleware, and changing how the agent processes requests.

The plugin system supports both local development (loading from a directory) and published package distribution (installing from npm). Key event hooks allow plugins to run code at specific points in the agent's execution cycle, similar to Cursor's hooks system but with the full power of TypeScript rather than shell scripts.

A limitation: plugins have access to OpenCode's internal APIs, which means they can break when OpenCode is updated. There is no stable plugin API guarantee — plugin authors must keep their plugins up to date with OpenCode releases.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's Claude-specific approach
- [Cursor](./cursor.md) — Compare with Cursor's editor-native approach
- [Codex](./codex.md) — Compare with Codex's cloud-sandboxed approach
- [OpenCode Docs Source](../sources/opencode-docs.md) — The source document this page was derived from
```

- [ ] **Step 2: Commit**

```bash
git add skills/wiki-ingest/evals/samples/expected/opencode-entity.md
git commit -m "feat(wiki): add golden sample entity page for opencode eval"
```

---

### Task 19: Create golden sample for plugin-builder entity page

**Files:**
- Create: `skills/wiki-ingest/evals/samples/expected/plugin-builder-entity.md`

This is a hand-curated golden sample for a long source (~3000+ words) → entity page. I need to read the raw source first to write an accurate golden sample.

- [ ] **Step 1: Read the plugin-builder raw source**

Read `data/raw/ai-tools/plugin-builder.md` to understand the full content.

- [ ] **Step 2: Write the golden sample**

Write a thorough entity page following the enhanced page-entity template, with 150-300 word Key Areas covering all the major topics from the source. Include the Plugin Structure, Manifest, Skills, Agents, Hooks, Testing & Validation, Marketplace, Distribution, Common Pitfalls, and Reference Implementation areas. Each area must have definition + example + edge case.

- [ ] **Step 3: Commit**

```bash
git add skills/wiki-ingest/evals/samples/expected/plugin-builder-entity.md
git commit -m "feat(wiki): add golden sample entity page for plugin-builder eval"
```

---

### Task 20: Create eval runner script

**Files:**
- Create: `skills/wiki-ingest/evals/run-eval.sh`

- [ ] **Step 1: Write the eval runner script**

```bash
#!/usr/bin/env bash
# Wiki Ingest Quality Evaluator
# Runs LLM-as-judge evaluation against golden samples
#
# Requirements:
#   - ANTHROPIC_API_KEY environment variable set
#   - jq installed (brew install jq)
#   - curl installed
#
# Usage:
#   ./run-eval.sh                    # Run all samples
#   ./run-eval.sh cursor             # Run specific sample
#   ./run-eval.sh --model opus       # Use different judge model

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/results"
SAMPLES_DIR="${SCRIPT_DIR}/samples"
RUBRIC="${SCRIPT_DIR}/rubric.md"
JUDGE_PROMPT="${SCRIPT_DIR}/judge-prompt.md"
MODEL="claude-sonnet-4-6"
API_URL="https://api.anthropic.com/v1/messages"

# Parse arguments
SAMPLE_FILTER=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL="$2"
      shift 2
      ;;
    *)
      SAMPLE_FILTER="$1"
      shift
      ;;
  esac
done

# Check prerequisites
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "Error: ANTHROPIC_API_KEY environment variable not set"
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed"
  exit 1
fi

# Create results directory
mkdir -p "${RESULTS_DIR}"

# Read rubric and judge prompt
RUBRIC_CONTENT=$(cat "${RUBRIC}")
JUDGE_PROMPT_CONTENT=$(cat "${JUDGE_PROMPT}")

# Find samples
SAMPLES=()
for input_file in "${SAMPLES_DIR}/input/"*.md; do
  [[ -f "$input_file" ]] || continue
  sample_name=$(basename "$input_file" .md)
  if [[ -n "$SAMPLE_FILTER" && "$sample_name" != "$SAMPLE_FILTER" ]]; then
    continue
  fi
  SAMPLES+=("$sample_name")
done

if [[ ${#SAMPLES[@]} -eq 0 ]]; then
  echo "No samples found matching filter: ${SAMPLE_FILTER:-all}"
  exit 1
fi

echo "Running eval with model: ${MODEL}"
echo "Samples: ${SAMPLES[*]}"
echo "---"

# Run evaluation for each sample
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ALL_SCORES=()

for sample in "${SAMPLES[@]}"; do
  echo "Evaluating: ${sample}"

  INPUT_FILE="${SAMPLES_DIR}/input/${sample}.md"
  EXPECTED_FILE="${SAMPLES_DIR}/expected/${sample}-entity.md"

  if [[ ! -f "$EXPECTED_FILE" ]]; then
    echo "  Skipping: no expected output file at ${EXPECTED_FILE}"
    continue
  fi

  INPUT_CONTENT=$(cat "$INPUT_FILE")
  EXPECTED_CONTENT=$(cat "$EXPECTED_FILE")

  # For actual output, we use the existing wiki entity page if it exists
  # Otherwise, the user must generate it first by running wiki-ingest
  ACTUAL_FILE="${SCRIPT_DIR}/../../data/wiki/entities/${sample}.md"
  if [[ ! -f "$ACTUAL_FILE" ]]; then
    echo "  Skipping: no actual output file at ${ACTUAL_FILE}"
    echo "  Run wiki-ingest on this source first, then re-run eval"
    continue
  fi
  ACTUAL_CONTENT=$(cat "$ACTUAL_FILE")

  # Build the judge request
  JUDGE_USER_CONTENT=$(cat <<HEREDOC
## Rubric

${RUBRIC_CONTENT}

## Raw Source

${INPUT_CONTENT}

## Expected Output (Golden Sample)

${EXPECTED_CONTENT}

## Actual Output (To Evaluate)

${ACTUAL_CONTENT}
HEREDOC
)

  # Call Claude API
  RESPONSE=$(curl -s "${API_URL}" \
    -H "Content-Type: application/json" \
    -H "x-api-key: ${ANTHROPIC_API_KEY}" \
    -H "anthropic-version: 2023-06-01" \
    -d "$(jq -n \
      --arg model "$MODEL" \
      --arg system "$JUDGE_PROMPT_CONTENT" \
      --arg user "$JUDGE_USER_CONTENT" \
      '{
        model: $model,
        max_tokens: 1024,
        system: $system,
        messages: [{role: "user", content: $user}]
      }')")

  # Extract the score JSON from the response
  SCORE_TEXT=$(echo "$RESPONSE" | jq -r '.content[0].text // empty')

  if [[ -z "$SCORE_TEXT" ]]; then
    echo "  Error: no response from API"
    echo "  Response: $(echo "$RESPONSE" | jq -c '.error // .')"
    continue
  fi

  # Try to parse as JSON (the model should return JSON)
  SCORE_JSON=$(echo "$SCORE_TEXT" | jq '.' 2>/dev/null || echo "null")

  if [[ "$SCORE_JSON" == "null" ]]; then
    # Try to extract JSON from markdown code block
    SCORE_JSON=$(echo "$SCORE_TEXT" | sed -n '/```json/,/```/p' | head -n -1 | tail -n +2 | jq '.' 2>/dev/null || echo "null")
  fi

  # Save individual result
  RESULT_FILE="${RESULTS_DIR}/${sample}-${TIMESTAMP}.json"
  echo "$SCORE_JSON" > "$RESULT_FILE"

  # Display score
  if [[ "$SCORE_JSON" != "null" ]]; then
    TOTAL=$(echo "$SCORE_JSON" | jq -r '.weighted_total // "N/A"')
    PASS=$(echo "$SCORE_JSON" | jq -r '.pass // "N/A"')
    echo "  Score: ${TOTAL}/5.0 | Pass: ${PASS}"
    ALL_SCORES+=("$TOTAL")
  else
    echo "  Error: could not parse score JSON"
    echo "  Raw response saved to ${RESULT_FILE}"
  fi
done

# Summary
echo "---"
echo "Results saved to: ${RESULTS_DIR}/"
if [[ ${#ALL_SCORES[@]} -gt 0 ]]; then
  AVG=$(echo "${ALL_SCORES[@]}" | awk '{s=0; for(i=1;i<=NF;i++) s+=$i; print s/NF}')
  echo "Average score: ${AVG}/5.0"
  echo "Passing threshold: 3.5/5.0"
fi
```

- [ ] **Step 2: Make the script executable**

```bash
chmod +x skills/wiki-ingest/evals/run-eval.sh
```

- [ ] **Step 3: Add results/ to .gitignore**

Create or update `skills/wiki-ingest/evals/.gitignore`:

```
results/*.json
```

- [ ] **Step 4: Commit**

```bash
git add skills/wiki-ingest/evals/run-eval.sh skills/wiki-ingest/evals/.gitignore
git commit -m "feat(wiki): add eval runner script with LLM-as-judge scoring"
```

---

### Task 21: Update README.md with new directory structure and eval info

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read current README.md**

Read the file to understand current content.

- [ ] **Step 2: Update directory structure section**

Replace any references to `raw/` and `wiki/` at the plugin root with `data/raw/` and `data/wiki/`. Add `data/config.json` to the directory listing. Add an "Evaluation" section describing the eval system.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(wiki): update README with data/ directory structure and eval system"
```

---

## Self-Review

**1. Spec coverage:**
- Data path migration + config.json → Tasks 1-3, 4-7, 21
- Template enhancement (6 page templates + raw-source) → Tasks 8-13
- Eval system (rubric, 3 samples, runner script) → Tasks 14-20
- All spec requirements covered.

**2. Placeholder scan:**
- Task 19 (plugin-builder golden sample) has a "read the source first" step instead of inline content. This is intentional — the golden sample must be accurate to the source content, which is ~10K and cannot be fully held in the plan. The step instructs the implementer to read the source and write accordingly.
- No TBD, TODO, or "implement later" patterns found.

**3. Type consistency:**
- `dataDir` field in config.json matches across all references.
- Template frontmatter fields consistent with CLAUDE.md documentation.
- Eval JSON output format consistent between rubric.md and judge-prompt.md.
- Path references (`<data-root>/`) consistent across all SKILL.md files and agent.
