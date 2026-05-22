# Wiki Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the reference plugin with a wiki plugin that implements the LLM Wiki pattern — a persistent, compounding knowledge base maintained by the LLM.

**Architecture:** Three-layer wiki (raw sources, wiki pages, schema rule) with three operation skills (ingest, query, lint), one delegation agent, and one always-on rule. Existing reference skill doc indexes are extracted into raw source files, then ingested into wiki pages.

**Tech Stack:** Claude Code plugin system (SKILL.md, agents, rules, plugin.json), markdown files, WebFetch for doc fetching

---

### Task 1: Create wiki plugin directory structure and manifest

**Files:**
- Create: `plugins/wiki/.claude-plugin/plugin.json`
- Create: `plugins/wiki/README.md`

- [ ] **Step 1: Create the wiki plugin directory**

```bash
mkdir -p plugins/wiki/.claude-plugin
```

- [ ] **Step 2: Create plugin.json manifest**

```json
{
  "name": "wiki",
  "version": "0.1.0",
  "description": "LLM-maintained personal knowledge base — ingest sources, query the wiki, lint for consistency",
  "author": { "name": "platootalp" },
  "license": "MIT"
}
```

- [ ] **Step 3: Create README.md**

```markdown
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
```

- [ ] **Step 4: Commit**

```bash
git add plugins/wiki/
git commit -m "feat(wiki): create wiki plugin directory and manifest"
```

---

### Task 2: Create the wiki-schema rule

**Files:**
- Create: `plugins/wiki/rules/wiki-schema.md`

- [ ] **Step 1: Create the rules directory**

```bash
mkdir -p plugins/wiki/rules
```

- [ ] **Step 2: Write wiki-schema.md**

```markdown
---
name: wiki-schema
description: Wiki conventions and structure — loaded into every session so the agent knows how the wiki works
---

# Wiki Schema

## Directory Layout

```
plugins/wiki/
  raw/          # Immutable source documents — READ ONLY, never modify
  wiki/         # LLM-generated pages — LLM writes, human reads
    index.md    # Content catalog (one line per page with link + summary)
    log.md      # Chronological activity log (append-only)
```

Source documents go in subdirectories under `raw/` by domain (e.g. `raw/ai-tools/`). Wiki pages mirror the same subdirectory structure under `wiki/`.

## Page Format

Every wiki page uses this structure:

```
---
tags: [tag1, tag2]
date: YYYY-MM-DD
sources:
  - raw/path/to/source.md
status: draft | stable | needs-update
---

# Page Title

## Summary

One-paragraph synthesis of the topic.

## Details

Full content with sections, cross-references, and citations.

## See Also

- [Related Page](./other-page.md)
```

## Cross-Reference Style

Use relative markdown links: `[Page Title](./page-name.md)`. For pages in other domains: `[Page Title](../other-domain/page-name.md)`.

## Naming Conventions

- File names: kebab-case (e.g. `claude-code.md`, `plugin-builder.md`)
- Domain folders under `raw/` and `wiki/`: kebab-case (e.g. `ai-tools/`)
- One page per concept/entity; merge related topics rather than splitting

## Index Format

`wiki/index.md` catalogs every wiki page:

```
# Wiki Index

## Domain: ai-tools

- [Claude Code](ai-tools/claude-code.md) — Claude Code CLI features, config, skills, hooks, MCP
- [Cursor](ai-tools/cursor.md) — Cursor AI editor features, CLI, hooks, MCP
```

Update index on every ingest.

## Log Format

`wiki/log.md` is append-only:

```
## [2026-05-22] ingest | Claude Code Documentation

Added Claude Code reference as raw source. Created wiki page with 12 sections. Updated index.

## [2026-05-22] lint | Full Wiki Health Check

Found 2 orphan pages, 1 stale claim. Fixed all issues.
```

## Operation Cheat Sheet

**Ingest**: Read source → Discuss with user → Write wiki page → Update index → Update affected pages → Append to log

**Query**: Read index → Find relevant pages → Read pages → Read raw sources if needed → Synthesize answer → Offer to file as new page

**Lint**: Scan for contradictions/stale claims/orphans/missing cross-references → Check index completeness → Suggest fixes → Apply approved fixes → Append to log
```

- [ ] **Step 3: Commit**

```bash
git add plugins/wiki/rules/
git commit -m "feat(wiki): add wiki-schema rule for always-on wiki conventions"
```

---

### Task 3: Create the wiki-ingest skill

**Files:**
- Create: `plugins/wiki/skills/wiki-ingest/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p plugins/wiki/skills/wiki-ingest
```

- [ ] **Step 2: Write SKILL.md**

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add plugins/wiki/skills/wiki-ingest/
git commit -m "feat(wiki): add wiki-ingest skill"
```

---

### Task 4: Create the wiki-query skill

**Files:**
- Create: `plugins/wiki/skills/wiki-query/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p plugins/wiki/skills/wiki-query
```

- [ ] **Step 2: Write SKILL.md**

```markdown
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

5. **Offer to file substantial answers as new pages**
   - If the answer required synthesizing multiple pages into a new insight (comparison, analysis, connection), offer to create a new wiki page for it
   - This is how the wiki compounds — explorations become permanent pages
   - Only offer for substantial answers, not simple lookups

## Routing Logic

The index replaces the old `ai-tool-reference` router. When a question comes in:

- Check `wiki/index.md` for matching pages
- The domain headings in the index serve as the routing table
- If unsure which domain, scan multiple domain sections

## Guidelines

- Prefer wiki pages over raw sources — the wiki is the synthesized, maintained layer
- Always cite which wiki page(s) you drew from
- If you find contradictory information between wiki pages, flag it and suggest running `/wiki-lint`
- If the wiki is empty or doesn't cover the topic, suggest running `/wiki-ingest` first
```

- [ ] **Step 3: Commit**

```bash
git add plugins/wiki/skills/wiki-query/
git commit -m "feat(wiki): add wiki-query skill"
```

---

### Task 5: Create the wiki-lint skill

**Files:**
- Create: `plugins/wiki/skills/wiki-lint/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p plugins/wiki/skills/wiki-lint
```

- [ ] **Step 2: Write SKILL.md**

```markdown
---
name: wiki-lint
description: Health-check the wiki for consistency and completeness. Use when the user says "lint the wiki", "health check", "what's missing", "check the wiki", or periodically after multiple ingests. Scans for contradictions, stale claims, orphan pages, missing cross-references, and gaps.
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
```

- [ ] **Step 3: Commit**

```bash
git add plugins/wiki/skills/wiki-lint/
git commit -m "feat(wiki): add wiki-lint skill"
```

---

### Task 6: Create the wiki-maintainer agent

**Files:**
- Create: `plugins/wiki/agents/wiki-maintainer.md`

- [ ] **Step 1: Create the agents directory**

```bash
mkdir -p plugins/wiki/agents
```

- [ ] **Step 2: Write wiki-maintainer.md**

```markdown
---
name: wiki-maintainer
description: Handles complex wiki operations — batch ingest, full lint, cross-page restructuring, and deep queries requiring synthesis across many pages
model: sonnet
tools: Read, Glob, Bash, Write, Edit, WebFetch
---

# Wiki Maintainer Agent

You are the Wiki Maintainer. You handle complex wiki operations that benefit from focused, isolated execution.

## When You're Used

- **Batch ingest** — processing multiple sources at once
- **Full wiki lint** — comprehensive health check across all pages
- **Cross-page restructuring** — renaming concepts, reorganizing categories, merging pages
- **Deep query** — questions requiring reading many pages and synthesizing across them

Simple operations (single ingest, quick query) are handled by the main agent using wiki skills directly.

## How You Work

1. Read `wiki/index.md` to understand the wiki's current state
2. Read the wiki-schema rule for conventions
3. Execute the requested operation following the same workflows as the wiki skills
4. Return a summary of all changes made

## Operation Details

### Batch Ingest

For each source:
1. Read the source
2. Create/update the wiki page
3. Update cross-references in affected pages
4. Update the index
5. Append to the log

After all sources: report a summary of pages created, pages updated, and cross-references added.

### Full Lint

1. Read every wiki page
2. Check for all issue types (contradictions, stale claims, orphans, missing cross-references, concepts without pages, data gaps)
3. Fix what you can confidently fix (index completeness, missing cross-references, obvious contradictions)
4. Flag uncertain fixes for human review
5. Append to the log

### Restructuring

1. Confirm the restructuring plan with the invoker before making changes
2. Rename/move/merge pages
3. Update all cross-references across the wiki
4. Update the index
5. Append to the log

### Deep Query

1. Read all potentially relevant pages
2. Read underlying raw sources if needed
3. Synthesize a comprehensive answer
4. If the answer is substantial, create a new wiki page for it
5. Return the answer

## Constraints

- Never modify files in `raw/` — they are immutable
- Always update `wiki/index.md` when creating or moving pages
- Always append to `wiki/log.md` after completing an operation
- Follow the page format defined in the wiki-schema rule
```

- [ ] **Step 3: Commit**

```bash
git add plugins/wiki/agents/
git commit -m "feat(wiki): add wiki-maintainer agent for complex operations"
```

---

### Task 7: Extract raw sources from existing reference skills

**Files:**
- Create: `plugins/wiki/raw/ai-tools/claude-code.md`
- Create: `plugins/wiki/raw/ai-tools/cursor.md`
- Create: `plugins/wiki/raw/ai-tools/codex.md`
- Create: `plugins/wiki/raw/ai-tools/opencode.md`
- Create: `plugins/wiki/raw/ai-tools/plugin-builder.md`

- [ ] **Step 1: Create the raw directory**

```bash
mkdir -p plugins/wiki/raw/ai-tools
```

- [ ] **Step 2: Extract claude-code.md from the skill**

Read `plugins/reference/skills/claude-code-reference/SKILL.md` and extract the documentation index section (the categorized list of doc pages with their URLs). Write it as a raw source document:

```markdown
# Claude Code Documentation Index

Source: https://code.claude.com/docs/

## Getting Started
- Overview: https://code.claude.com/docs/en/overview.md
- Quickstart: https://code.claude.com/docs/en/quickstart.md
- Setup: https://code.claude.com/docs/en/setup.md
- Authentication: https://code.claude.com/docs/en/authentication.md

## Core Configuration
- Settings: https://code.claude.com/docs/en/settings.md
- Environment Variables: https://code.claude.com/docs/en/env-vars.md
- Model Configuration: https://code.claude.com/docs/en/model-config.md
- CLI Reference: https://code.claude.com/docs/en/cli-reference.md
- Commands: https://code.claude.com/docs/en/commands.md
- Tools Reference: https://code.claude.com/docs/en/tools-reference.md

## Agent Features
- Skills: https://code.claude.com/docs/en/skills.md
- Hooks Guide: https://code.claude.com/docs/en/hooks-guide.md
- Hooks Reference: https://code.claude.com/docs/en/hooks.md
- MCP: https://code.claude.com/docs/en/MCP.md
- Plugins: https://code.claude.com/docs/en/plugins.md
- Plugins Reference: https://code.claude.com/docs/en/plugins-reference.md
- Sub-agents: https://code.claude.com/docs/en/sub-agents.md

## Memory & Context
- Memory: https://code.claude.com/docs/en/memory.md
- Best Practices: https://code.claude.com/docs/en/best-practices.md
- Common Workflows: https://code.claude.com/docs/en/common-workflows.md
- Context Window: https://code.claude.com/docs/en/context-window.md

## Workflow & Automation
- Routines: https://code.claude.com/docs/en/routines.md
- Scheduled Tasks: https://code.claude.com/docs/en/scheduled-tasks.md
- Agent Teams: https://code.claude.com/docs/en/agent-teams.md
- Worktrees: https://code.claude.com/docs/en/worktrees.md

## UI & Customization
- Interactive Mode: https://code.claude.com/docs/en/interactive-mode.md
- Terminal Config: https://code.claude.com/docs/en/terminal-config.md
- Keybindings: https://code.claude.com/docs/en/keybindings.md
- Status Line: https://code.claude.com/docs/en/statusline.md
- Output Styles: https://code.claude.com/docs/en/output-styles.md

## Permissions & Security
- Permission Modes: https://code.claude.com/docs/en/permission-modes.md
- Permissions: https://code.claude.com/docs/en/permissions.md
- Security: https://code.claude.com/docs/en/security.md
- Sandboxing: https://code.claude.com/docs/en/sandboxing.md

## Integrations & Platforms
- Desktop: https://code.claude.com/docs/en/desktop.md
- VS Code: https://code.claude.com/docs/en/vscode.md
- JetBrains: https://code.claude.com/docs/en/jetbrains.md
- Web: https://code.claude.com/docs/en/web.md
- GitHub Actions: https://code.claude.com/docs/en/github-actions.md
- GitLab CI/CD: https://code.claude.com/docs/en/gitlab-ci-cd.md
- Slack: https://code.claude.com/docs/en/slack.md
- Third Party: https://code.claude.com/docs/en/third-party.md

## Agent SDK
- Overview: https://code.claude.com/docs/en/sdk/overview.md
- Skills: https://code.claude.com/docs/en/sdk/skills.md
- Hooks: https://code.claude.com/docs/en/sdk/hooks.md
- MCP: https://code.claude.com/docs/en/sdk/MCP.md
- Permissions: https://code.claude.com/docs/en/sdk/permissions.md

## Troubleshooting
- Troubleshooting: https://code.claude.com/docs/en/troubleshooting.md
- Debug Your Config: https://code.claude.com/docs/en/debug-your-config.md
- Errors: https://code.claude.com/docs/en/errors.md
- Troubleshoot Install: https://code.claude.com/docs/en/troubleshoot-install.md

## Observability
- Monitoring Usage: https://code.claude.com/docs/en/monitoring-usage.md
- Costs: https://code.claude.com/docs/en/costs.md
- Analytics: https://code.claude.com/docs/en/analytics.md

## Index
For unknown topics, fetch: https://code.claude.com/docs/llms.txt
```

- [ ] **Step 3: Extract cursor.md from the skill**

Read `plugins/reference/skills/cursor-reference/SKILL.md` and extract the documentation index. Write as a raw source:

```markdown
# Cursor AI Editor Documentation Index

Source: https://cursor.com/docs

## Getting Started
- Overview: https://cursor.com/docs/overview
- Quickstart: https://cursor.com/docs/quickstart
- Hooks: https://cursor.com/docs/hooks
- Third-party Hooks: https://cursor.com/docs/third-party-hooks

## CLI Reference
- Overview: https://cursor.com/docs/cli/overview
- Parameters: https://cursor.com/docs/cli/parameters
- Permissions: https://cursor.com/docs/cli/permissions
- MCP: https://cursor.com/docs/cli/mcp

## CLI Commands
- agent: https://cursor.com/docs/cli/agent
- agent login/logout: https://cursor.com/docs/cli/agent-login
- agent status/whoami: https://cursor.com/docs/cli/agent-status
- agent models: https://cursor.com/docs/cli/agent-models
- agent mcp list/add/login: https://cursor.com/docs/cli/agent-mcp
- agent about: https://cursor.com/docs/cli/agent-about
- agent update: https://cursor.com/docs/cli/agent-update
- agent ls: https://cursor.com/docs/cli/agent-ls
- agent resume: https://cursor.com/docs/cli/agent-resume
- agent create-chat: https://cursor.com/docs/cli/agent-create-chat
- agent generate-rule: https://cursor.com/docs/cli/agent-generate-rule
- agent install-shell-integration: https://cursor.com/docs/cli/agent-install-shell-integration
- agent -p --force (headless): https://cursor.com/docs/cli/agent-headless

## Hooks System
- preToolUse (allow/deny/modify input): https://cursor.com/docs/hooks/preToolUse
- postToolUse (audit/inject context): https://cursor.com/docs/hooks/postToolUse
- Matcher support: https://cursor.com/docs/hooks/matchers

## MCP
- Overview: https://cursor.com/docs/mcp/overview
- CLI commands: https://cursor.com/docs/mcp/cli
- mcp.json configuration: https://cursor.com/docs/mcp/config

## Permissions
- Shell commands allow/deny: https://cursor.com/docs/permissions/shell
- File paths (glob): https://cursor.com/docs/permissions/paths
- Web domains: https://cursor.com/docs/permissions/web
- MCP tools: https://cursor.com/docs/permissions/mcp

## Rules
- generate-rule command: https://cursor.com/docs/rules/generate
- Customization rules: https://cursor.com/docs/rules/customization
```

- [ ] **Step 4: Extract codex.md from the skill**

Read `plugins/reference/skills/openai-codex-reference/SKILL.md` and extract the documentation index. Write as a raw source:

```markdown
# OpenAI Codex Documentation Index

Source: https://developers.openai.com/codex

## Getting Started
- Overview: https://developers.openai.com/codex/overview
- Quickstart: https://developers.openai.com/codex/quickstart
- Use Cases: https://developers.openai.com/codex/use-cases
- Migration: https://developers.openai.com/codex/migration
- Pricing: https://developers.openai.com/codex/pricing

## Concepts
- Prompting: https://developers.openai.com/codex/prompting
- Customization: https://developers.openai.com/codex/customization
- Memories: https://developers.openai.com/codex/memories
- Chronicle: https://developers.openai.com/codex/chronicle
- Sandboxing: https://developers.openai.com/codex/sandboxing
- Auto-review: https://developers.openai.com/codex/auto-review
- Subagents: https://developers.openai.com/codex/subagents
- Workflows: https://developers.openai.com/codex/workflows
- Models: https://developers.openai.com/codex/models
- Cyber Safety: https://developers.openai.com/codex/cyber-safety

## Using Codex - App
- Overview: https://developers.openai.com/codex/app/overview
- Features: https://developers.openai.com/codex/app/features
- Settings: https://developers.openai.com/codex/app/settings
- Review: https://developers.openai.com/codex/app/review
- Automations: https://developers.openai.com/codex/app/automations
- Worktrees: https://developers.openai.com/codex/app/worktrees
- Local Environments: https://developers.openai.com/codex/app/local-environments
- Browser: https://developers.openai.com/codex/app/browser
- Chrome Extension: https://developers.openai.com/codex/app/chrome-extension
- Computer Use: https://developers.openai.com/codex/app/computer-use
- Commands: https://developers.openai.com/codex/app/commands
- Windows: https://developers.openai.com/codex/app/windows
- Troubleshooting: https://developers.openai.com/codex/app/troubleshooting

## Using Codex - IDE Extension
- Overview: https://developers.openai.com/codex/ide/overview
- Features: https://developers.openai.com/codex/ide/features
- Settings: https://developers.openai.com/codex/ide/settings
- Commands: https://developers.openai.com/codex/ide/commands
- Slash Commands: https://developers.openai.com/codex/ide/slash-commands

## Using Codex - CLI
- Overview: https://developers.openai.com/codex/cli/overview
- Features: https://developers.openai.com/codex/cli/features
- Reference: https://developers.openai.com/codex/cli/reference
- Slash Commands: https://developers.openai.com/codex/cli/slash-commands

## Using Codex - Cloud
- Overview: https://developers.openai.com/codex/cloud/overview
- Environments: https://developers.openai.com/codex/cloud/environments
- Internet Access: https://developers.openai.com/codex/cloud/internet-access

## Integrations
- GitHub: https://developers.openai.com/codex/integrations/github
- Slack: https://developers.openai.com/codex/integrations/slack
- Linear: https://developers.openai.com/codex/integrations/linear

## Security
- Overview: https://developers.openai.com/codex/security/overview
- Setup: https://developers.openai.com/codex/security/setup
- Threat Model: https://developers.openai.com/codex/security/threat-model
- FAQ: https://developers.openai.com/codex/security/faq

## Configuration
- Basic Config: https://developers.openai.com/codex/config/basic
- Advanced Config: https://developers.openai.com/codex/config/advanced
- Config Reference: https://developers.openai.com/codex/config/reference
- Config Samples: https://developers.openai.com/codex/config/samples
- Speed Settings: https://developers.openai.com/codex/config/speed
- Rules: https://developers.openai.com/codex/config/rules
- Hooks: https://developers.openai.com/codex/config/hooks
- AGENTS.md: https://developers.openai.com/codex/config/agents-md
- MCP: https://developers.openai.com/codex/config/mcp
- Plugins: https://developers.openai.com/codex/config/plugins
- Build Plugins: https://developers.openai.com/codex/config/build-plugins
- Skills: https://developers.openai.com/codex/config/skills
- Subagents: https://developers.openai.com/codex/config/subagents

## Administration
- Authentication: https://developers.openai.com/codex/admin/authentication
- Agent Approvals & Security: https://developers.openai.com/codex/admin/agent-approvals
- Remote Connections: https://developers.openai.com/codex/admin/remote-connections
- Enterprise Admin: https://developers.openai.com/codex/admin/enterprise-admin
- Enterprise Governance: https://developers.openai.com/codex/admin/enterprise-governance
- Managed Configuration: https://developers.openai.com/codex/admin/managed-configuration

## Automation
- Non-interactive Mode: https://developers.openai.com/codex/automation/non-interactive
- SDK: https://developers.openai.com/codex/automation/sdk
- App Server: https://developers.openai.com/codex/automation/app-server
- Agents SDK Guide: https://developers.openai.com/codex/automation/agents-sdk
- GitHub Action: https://developers.openai.com/codex/automation/github-action

## Learn
- Best Practices: https://developers.openai.com/codex/learn/best-practices
- Videos: https://developers.openai.com/codex/learn/videos
- Build AI-native Team: https://developers.openai.com/codex/learn/build-ai-native-team

## Releases
- Changelog: https://developers.openai.com/codex/releases/changelog
- Feature Maturity: https://developers.openai.com/codex/releases/feature-maturity
- Open Source: https://developers.openai.com/codex/releases/open-source
```

- [ ] **Step 5: Extract opencode.md from the skill**

Read `plugins/reference/skills/opencode-reference/SKILL.md` and extract the documentation index and quick reference. Write as a raw source:

```markdown
# OpenCode CLI Documentation Index

Source: https://opencode.ai/docs/

## Getting Started
- Overview: https://opencode.ai/docs/overview
- Config: https://opencode.ai/docs/config
- Providers: https://opencode.ai/docs/providers
- Network: https://opencode.ai/docs/network
- Enterprise: https://opencode.ai/docs/enterprise
- Troubleshooting: https://opencode.ai/docs/troubleshooting
- Windows/WSL: https://opencode.ai/docs/windows

## Usage
- Go (programmatic): https://opencode.ai/docs/usage/go
- TUI: https://opencode.ai/docs/usage/tui
- CLI: https://opencode.ai/docs/usage/cli
- Web: https://opencode.ai/docs/usage/web
- IDE: https://opencode.ai/docs/usage/ide
- Zen: https://opencode.ai/docs/usage/zen
- Share: https://opencode.ai/docs/usage/share
- GitHub: https://opencode.ai/docs/usage/github
- GitLab: https://opencode.ai/docs/usage/gitlab

## Configure
- Tools: https://opencode.ai/docs/configure/tools
- Rules (AGENTS.md): https://opencode.ai/docs/configure/rules
- Agents: https://opencode.ai/docs/configure/agents
- Models: https://opencode.ai/docs/configure/models
- Themes: https://opencode.ai/docs/configure/themes
- Keybinds: https://opencode.ai/docs/configure/keybinds
- Commands: https://opencode.ai/docs/configure/commands
- Formatters: https://opencode.ai/docs/configure/formatters
- Permissions: https://opencode.ai/docs/configure/permissions
- LSP Servers: https://opencode.ai/docs/configure/lsp
- MCP Servers: https://opencode.ai/docs/configure/mcp
- ACP Support: https://opencode.ai/docs/configure/acp
- Agent Skills: https://opencode.ai/docs/configure/skills
- Custom Tools: https://opencode.ai/docs/configure/custom-tools

## Develop
- SDK: https://opencode.ai/docs/develop/sdk
- Server: https://opencode.ai/docs/develop/server
- Plugins: https://opencode.ai/docs/develop/plugins
- Ecosystem: https://opencode.ai/docs/develop/ecosystem

## Schema References
- config.json: https://opencode.ai/docs/schemas/config
- tui.json: https://opencode.ai/docs/schemas/tui

## Quick Reference

### Configuration
- JSON/JSONC config with `$schema` support
- 8 priority levels from remote to macOS managed
- TUI config for terminal UI customization

### Built-in Tools (12)
bash, edit, write, read, grep, glob, apply_patch, skill, todowrite, webfetch, websearch, question, lsp

### Built-in Agents
- Primary: Build, Plan
- Subagents: General, Explore, Scout
- Hidden system: Compaction, Title, Summary

### Permissions
- Three actions: allow, ask, deny
- Glob patterns for file matching
- Last matching rule wins

### Skills
- SKILL.md format
- Discovery paths: `.opencode/skills/`, `~/.config/opencode/skills/`
- Compatible with `.claude/skills/` and `.agents/skills/`

### Custom Commands
- JSON config or markdown files in `.opencode/commands/`

### MCP Servers
- Local: command + env
- Remote: URL + headers/OAuth
- CLI commands for management

### Plugins
- TypeScript modules, npm packages
- Key event hooks

### Custom Tools
- TypeScript files using `tool()` helper with Zod schemas

### Rules (AGENTS.md)
- Project root, global, additional instructions

### Variable Substitution
- `{env:VAR}`, `{file:path}`
```

- [ ] **Step 6: Extract plugin-builder.md from the skill**

Read `plugins/reference/skills/claude-code-plugin-builder/SKILL.md` and the `references/codex-plugin-cc.md` file. Extract the core content into a raw source document. This is the most substantial extraction — the skill is 681 lines plus a 344-line reference. Write a condensed raw source that preserves the key information:

```markdown
# Claude Code Plugin Builder Reference

Source: Claude Code plugin documentation + openai/codex-plugin-cc reference implementation

## Plugin Structure

```
my-plugin/
  .claude-plugin/plugin.json    # Required manifest
  skills/<name>/SKILL.md        # Skills
  commands/<name>.md            # Commands
  agents/<name>.md              # Subagent definitions
  hooks/hooks.json              # Hook configuration
  .mcp.json                     # MCP servers
  .lsp.json                     # LSP servers
  monitors/monitors.json        # Background monitors
  bin/                          # Executables
  settings.json                 # Default settings
  scripts/                      # Supporting scripts
  README.md
```

Critical: Only `plugin.json` goes inside `.claude-plugin/`. All component directories must be at plugin root level.

## Manifest Format (plugin.json)

Required fields: name, version, description, author, license

Optional fields: repository, homepage, keywords, environment, userConfig

Version strategy: explicit (semver string) or commit SHA (auto from git).

## Skills

SKILL.md with YAML frontmatter (name, description). Supports `$ARGUMENTS` placeholder. Can bundle `references/` and `scripts/` subdirectories.

## Agents

Markdown with frontmatter: name, description, model, effort, maxTurns, tools, disallowedTools, skills, memory, background, isolation.

## Hooks

hooks.json with types: command, http, mcp_tool, prompt, agent. Events: SessionStart, SessionEnd, Stop, PreToolUse, PostToolUse, Notification.

## MCP/LSP Servers

.mcp.json for MCP servers (command-based or URL-based). .lsp.json for LSP servers.

## Testing

- `claude --plugin-dir ./my-plugin` — test locally
- `/reload-plugins` — reload in session
- `claude plugin validate .` — validate structure

## Marketplace

marketplace.json with plugins array. Source types: relative path, GitHub, Git URL, Git subdirectory, npm.

## Distribution

GitHub hosting, private repos with auth tokens, team marketplaces via `extraKnownMarketplaces`, lockdown via `strictKnownMarketplaces`.

## Environment Variables

- `${CLAUDE_PLUGIN_ROOT}` — plugin directory path
- `${CLAUDE_PLUGIN_DATA}` — plugin data directory
- `${CLAUDE_PROJECT_DIR}` — project directory
- `${user_config.KEY}` — user-configured values

## Common Pitfalls

1. Components inside .claude-plugin/ (should be at plugin root)
2. Absolute paths (use CLAUDE_PLUGIN_ROOT)
3. Referencing files outside plugin dir
4. Missing CLAUDE_PLUGIN_ROOT in hooks/MCP
5. Version not bumped after changes
6. Relative paths in URL-based marketplaces
7. Duplicate version field

## Reference Implementation: openai/codex-plugin-cc

### Architecture Patterns
1. **Companion Script**: Central runtime handling command routing, job lifecycle, external service communication
2. **Command Frontmatter**: `disable-model-invocation`, `allowed-tools`, `argument-hint` fields
3. **Thin Forwarder Subagent**: Agent that only forwards to companion script, never analyzes code
4. **Plugin-embedded Skills**: Internal skills for runtime and result handling
5. **Hook System**: SessionStart/SessionEnd/Stop hooks with lifecycle management and stop-time gate
6. **Hook-to-Session Data**: stdin JSON input, environment variable session ID

### Task Delegation
User input → Command → Agent → Companion script → App server → Codex CLI

### App Server Communication
JSON-RPC over JSONL protocol. Broker mode (Unix socket) vs Direct Spawn mode.
```

- [ ] **Step 7: Commit**

```bash
git add plugins/wiki/raw/
git commit -m "feat(wiki): extract raw sources from reference skills into wiki raw/ai-tools/"
```

---

### Task 8: Create initial wiki pages and index

**Files:**
- Create: `plugins/wiki/wiki/index.md`
- Create: `plugins/wiki/wiki/log.md`
- Create: `plugins/wiki/wiki/ai-tools/claude-code.md`
- Create: `plugins/wiki/wiki/ai-tools/cursor.md`
- Create: `plugins/wiki/wiki/ai-tools/codex.md`
- Create: `plugins/wiki/wiki/ai-tools/opencode.md`
- Create: `plugins/wiki/wiki/ai-tools/plugin-builder.md`

- [ ] **Step 1: Create the wiki directories**

```bash
mkdir -p plugins/wiki/wiki/ai-tools
```

- [ ] **Step 2: Create index.md**

```markdown
# Wiki Index

## Domain: ai-tools

- [Claude Code](ai-tools/claude-code.md) — Claude Code CLI features, config, skills, hooks, MCP, permissions, Agent SDK
- [Cursor](ai-tools/cursor.md) — Cursor AI editor features, CLI, hooks, MCP, permissions, rules
- [OpenAI Codex](ai-tools/codex.md) — OpenAI Codex features, config, skills, plugins, sandboxing, automation
- [OpenCode](ai-tools/opencode.md) — OpenCode CLI features, config, tools, agents, permissions, plugins, custom tools
- [Plugin Builder](ai-tools/plugin-builder.md) — Claude Code plugin and marketplace construction guide
```

- [ ] **Step 3: Create log.md**

```markdown
# Wiki Log

## [2026-05-22] ingest | AI Tools Reference Sources

Initial migration from reference plugin. Extracted 5 raw sources. Created 5 wiki pages. Built index.
```

- [ ] **Step 4: Create claude-code.md wiki page**

```markdown
---
tags: [claude-code, cli, ai-tools]
date: 2026-05-22
sources:
  - raw/ai-tools/claude-code.md
status: stable
---

# Claude Code

## Summary

Claude Code is Anthropic's official CLI for Claude. It supports skills, hooks, MCP, plugins, sub-agents, memory, and the Agent SDK. Official documentation at https://code.claude.com/docs/.

## Key Areas

### Configuration
Settings via `settings.json` (project/user/global), environment variables, model configuration. CLI reference with commands and tools.

### Agent Features
Skills (SKILL.md format), hooks (PreToolUse/PostToolUse/SessionStart/SessionEnd/Stop), MCP servers, plugins, sub-agents.

### Memory & Context
Persistent memory, best practices, common workflows, context window management.

### Workflow & Automation
Routines, scheduled tasks, agent teams, worktrees for parallel work.

### Permissions & Security
Permission modes (default/plan/auto), granular permissions, security hardening, sandboxing.

### Integrations
Desktop app, VS Code, JetBrains, web, GitHub Actions, GitLab CI/CD, Slack.

### Agent SDK
Build custom agents with skills, hooks, MCP, and permissions.

### Troubleshooting
Debug config, error messages, installation issues. Observability via monitoring, costs, analytics.

## See Also

- [Plugin Builder](./plugin-builder.md) — How to build Claude Code plugins
- [Cursor](./cursor.md) — Compare with Cursor's approach
- [OpenAI Codex](./codex.md) — Compare with Codex's approach
```

- [ ] **Step 5: Create cursor.md wiki page**

```markdown
---
tags: [cursor, editor, ai-tools]
date: 2026-05-22
sources:
  - raw/ai-tools/cursor.md
status: stable
---

# Cursor

## Summary

Cursor is an AI-powered code editor with a CLI agent supporting hooks, MCP, permissions, and rules. Official documentation at https://cursor.com/docs.

## Key Areas

### CLI
Full CLI agent with login/logout, status, models, MCP management, resume, headless mode (`-p --force`).

### Hooks
preToolUse (allow/deny/modify input) and postToolUse (audit/inject context) with matcher support.

### MCP
MCP server management via CLI and mcp.json configuration.

### Permissions
Allow/deny lists for shell commands, file paths (glob), web domains, and MCP tools.

### Rules
Generate custom rules with `agent generate-rule`. Customization rules for project-specific behavior.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's approach
- [OpenAI Codex](./codex.md) — Compare with Codex's approach
```

- [ ] **Step 6: Create codex.md wiki page**

```markdown
---
tags: [codex, openai, ai-tools]
date: 2026-05-22
sources:
  - raw/ai-tools/codex.md
status: stable
---

# OpenAI Codex

## Summary

OpenAI Codex is a coding agent available as app, IDE extension, CLI, and cloud environment. Supports skills, hooks, MCP, plugins, subagents, and sandboxing. Official documentation at https://developers.openai.com/codex.

## Key Areas

### Modes
App (desktop), IDE extension (VS Code), CLI (terminal), Cloud (remote environments).

### Concepts
Prompting, customization, memories, chronicle, sandboxing, auto-review, subagents, workflows, models.

### Configuration
Basic and advanced config, AGENTS.md for rules, hooks, MCP, plugins, skills, subagents.

### Security
Threat model, setup, FAQ. Sandboxing for code execution safety.

### Administration
Authentication, agent approvals, remote connections, enterprise admin/governance/managed configuration.

### Automation
Non-interactive mode, SDK, app server, Agents SDK, GitHub Action.

### Integrations
GitHub, Slack, Linear.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's approach
- [Cursor](./cursor.md) — Compare with Cursor's approach
- [OpenCode](./opencode.md) — Compare with OpenCode's approach
```

- [ ] **Step 7: Create opencode.md wiki page**

```markdown
---
tags: [opencode, cli, ai-tools]
date: 2026-05-22
sources:
  - raw/ai-tools/opencode.md
status: stable
---

# OpenCode

## Summary

OpenCode is a provider-agnostic AI coding CLI supporting 75+ LLMs. Features TUI, CLI, web, and IDE interfaces with skills, MCP, plugins, custom tools, and permissions. Official documentation at https://opencode.ai/docs/.

## Key Areas

### Interfaces
TUI (terminal UI), CLI, Web, IDE, Zen mode, Share, GitHub/GitLab integration.

### Configuration
JSON/JSONC config with `$schema` support, 8 priority levels, TUI customization.

### Built-in Tools
12 tools: bash, edit, write, read, grep, glob, apply_patch, skill, todowrite, webfetch, websearch, question, lsp.

### Built-in Agents
Primary (Build, Plan), Subagents (General, Explore, Scout), Hidden system agents (Compaction, Title, Summary).

### Permissions
Three actions (allow, ask, deny), glob patterns, last matching rule wins.

### Skills
SKILL.md format. Discovery from `.opencode/skills/`, `~/.config/opencode/skills/`. Compatible with `.claude/skills/` and `.agents/skills/`.

### Custom Tools
TypeScript files using `tool()` helper with Zod schemas.

### Plugins
TypeScript modules, npm packages, event hooks.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's approach
- [OpenAI Codex](./codex.md) — Compare with Codex's approach
```

- [ ] **Step 8: Create plugin-builder.md wiki page**

```markdown
---
tags: [plugins, marketplace, claude-code, ai-tools]
date: 2026-05-22
sources:
  - raw/ai-tools/plugin-builder.md
status: stable
---

# Plugin Builder

## Summary

Guide for building Claude Code plugins and marketplaces. Covers the full lifecycle from structure to distribution, with a reference implementation analysis of the openai/codex-plugin-cc production plugin.

## Key Areas

### Plugin Structure
`.claude-plugin/plugin.json` manifest (required). Skills, agents, hooks, MCP/LSP servers, monitors at plugin root.

### Manifest
Required: name, version, description, author, license. Optional: repository, homepage, keywords, environment, userConfig.

### Skills
SKILL.md with frontmatter, `$ARGUMENTS` placeholder, bundled references/ and scripts/.

### Agents
Markdown with frontmatter: model, effort, maxTurns, tools, disallowedTools, skills, memory, background, isolation.

### Hooks
hooks.json with types (command, http, mcp_tool, prompt, agent) and events (SessionStart, SessionEnd, Stop, PreToolUse, PostToolUse, Notification).

### Testing & Validation
`claude --plugin-dir`, `/reload-plugins`, `claude plugin validate`.

### Marketplace
marketplace.json with source types: relative path, GitHub, Git URL, Git subdirectory, npm.

### Distribution
GitHub hosting, private repos, team marketplaces, Anthropic marketplace submission.

### Common Pitfalls
Components inside .claude-plugin/, absolute paths, referencing outside plugin dir, missing CLAUDE_PLUGIN_ROOT in hooks/MCP, version not bumped.

### Reference Implementation (codex-plugin-cc)
Companion script design, command frontmatter controls, thin forwarder subagent, plugin-embedded skills, hook lifecycle with stop-time gate, hook-to-session data passing.

## See Also

- [Claude Code](./claude-code.md) — The platform plugins run on
```

- [ ] **Step 9: Commit**

```bash
git add plugins/wiki/wiki/
git commit -m "feat(wiki): create initial wiki pages and index from reference skill content"
```

---

### Task 9: Update marketplace.json and remove old reference plugin

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Delete: `plugins/reference/` (entire directory)

- [ ] **Step 1: Update marketplace.json**

Replace the reference plugin entry with the wiki plugin entry. Change:

```json
{ "name": "reference", "source": "./plugins/reference", "description": "AI coding tool reference documentation skills" }
```

To:

```json
{ "name": "wiki", "source": "./plugins/wiki", "description": "LLM-maintained personal knowledge base — ingest sources, query the wiki, lint for consistency" }
```

- [ ] **Step 2: Remove the old reference plugin**

```bash
rm -rf plugins/reference/
```

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git add plugins/reference/
git commit -m "feat(wiki): replace reference plugin with wiki plugin in marketplace, remove old reference plugin"
```

---

### Task 10: Validate and test the wiki plugin

**Files:**
- No new files

- [ ] **Step 1: Validate the plugin structure**

```bash
claude plugin validate .
```

Expected: No errors related to the wiki plugin.

- [ ] **Step 2: Verify the wiki plugin loads**

```bash
claude --plugin-dir ./plugins/wiki --print "list available skills"
```

Expected: wiki-ingest, wiki-query, wiki-lint listed.

- [ ] **Step 3: Verify directory structure is complete**

```bash
find plugins/wiki -type f | sort
```

Expected files:
```
plugins/wiki/.claude-plugin/plugin.json
plugins/wiki/README.md
plugins/wiki/agents/wiki-maintainer.md
plugins/wiki/raw/ai-tools/claude-code.md
plugins/wiki/raw/ai-tools/codex.md
plugins/wiki/raw/ai-tools/cursor.md
plugins/wiki/raw/ai-tools/opencode.md
plugins/wiki/raw/ai-tools/plugin-builder.md
plugins/wiki/rules/wiki-schema.md
plugins/wiki/skills/wiki-ingest/SKILL.md
plugins/wiki/skills/wiki-lint/SKILL.md
plugins/wiki/skills/wiki-query/SKILL.md
plugins/wiki/wiki/ai-tools/claude-code.md
plugins/wiki/wiki/ai-tools/codex.md
plugins/wiki/wiki/ai-tools/cursor.md
plugins/wiki/wiki/ai-tools/opencode.md
plugins/wiki/wiki/ai-tools/plugin-builder.md
plugins/wiki/wiki/index.md
plugins/wiki/wiki/log.md
```

- [ ] **Step 4: Commit any fixes if needed**

If validation revealed issues, fix them and commit.
