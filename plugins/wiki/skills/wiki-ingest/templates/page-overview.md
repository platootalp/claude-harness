---
tags: [overview]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
status: draft | stable | needs-update
page_type: overview
---

# Wiki Overview

## Summary

**100-150 words.** Must cover: (1) what this wiki covers — the domains and scope, (2) the big picture — the overarching theme or thesis that connects the domains, (3) the current state — how mature the wiki is and what's actively being developed.

> **Example:**
> This wiki covers AI coding tools and the LLM Wiki pattern itself. The overarching theme is the emergence of LLM-powered developer tools that combine conversational AI with direct code manipulation capabilities. The wiki currently has five entity pages covering the major tools (Claude Code, Cursor, Codex, OpenCode, Plugin Builder), with active investigation into how their permission models and plugin ecosystems compare. The LLM Wiki concept page documents the pattern this wiki itself follows.

## Domains

For each domain, **100-200 words.** Must include: (1) what the domain covers, (2) key insights discovered so far, (3) links to the most important entity and concept pages in this domain. Each domain should give a reader enough context to understand the domain without reading every page.

> **Example:**
> ### ai-tools
>
> Covers AI-powered coding assistants and their ecosystems. Five tools are currently documented: Claude Code (Anthropic's CLI agent with deep model integration and plugin support), Cursor (editor-native AI with a CLI agent), Codex (OpenAI's cloud-sandboxed coding agent), OpenCode (provider-agnostic CLI supporting 75+ LLMs), and Plugin Builder (the Claude Code extension framework). Key insight: these tools differ most fundamentally in their execution model (local vs. cloud) and extensibility (plugin system vs. monolithic), not in their feature lists. See [Claude Code](entities/claude-code.md), [Cursor](entities/cursor.md), [Codex](entities/codex.md), [OpenCode](entities/opencode.md), [Plugin Builder](entities/plugin-builder.md).

## Active Questions

Must be specific, actionable questions — not vague statements. Each question should suggest what source or analysis could resolve it. 3-5 questions is a good target.

> **Example:**
> - **How do permission models compare across tools?** — A comparison synthesis page would resolve this. Need to verify Codex's sandboxing details from official docs.
> - **Is MCP becoming a universal standard?** — Need to ingest MCP specification docs and check which tools have adopted it beyond Claude Code and Cursor.
> - **What's the real-world performance difference between local and cloud execution?** — Would need benchmark data or user reports as sources.

## Recent Activity

Summarize the last 5 log entries with dates. Each entry: date + operation + one-line summary. Gives context for what's been happening without requiring the reader to open the log.

> **Example:**
> - 2026-05-22: ingest | OpenCode Documentation — created entity page with 9 Key Areas
> - 2026-05-22: ingest | Plugin Builder Documentation — created entity page with 10 Key Areas
> - 2026-05-22: ingest | Cursor Documentation — created entity page with 6 Key Areas
> - 2026-05-21: restructure | Template Standardization — migrated wiki to type-based directories with templates
> - 2026-05-20: migrate | Initial Wiki Setup — migrated existing pages to new format

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
