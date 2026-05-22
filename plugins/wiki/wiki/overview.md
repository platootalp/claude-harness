---
tags: [overview]
date: 2026-05-22
last_updated: 2026-05-22
status: stable
page_type: overview
---

# Wiki Overview

## Summary

This wiki covers AI coding tools and related patterns. It currently tracks five major coding agents (Claude Code, Codex, Cursor, OpenCode) and the plugin ecosystem (Plugin Builder), plus the LLM Wiki pattern that inspired this knowledge base. The wiki is organized by page type: sources hold raw document summaries, entities hold structured knowledge about each tool, concepts hold abstract ideas, and syntheses hold insights that connect multiple pages.

## Domains

### ai-tools

Five AI coding tools and their plugin ecosystems. Claude Code (Anthropic's CLI) and Codex (OpenAI's agent) are the most feature-complete, offering skills, hooks, MCP, plugins, and sub-agents. Cursor brings a GUI editor approach with hooks and MCP. OpenCode is provider-agnostic, supporting 75+ LLMs. Plugin Builder documents the Claude Code plugin/marketplace system. Key insight: all tools converge on similar extensibility patterns (skills, hooks, MCP, plugins) but differ in permission models, interfaces, and ecosystem maturity.

### llm-wiki

The pattern document that inspired this wiki plugin. Describes a three-layer architecture (raw sources, wiki pages, schema) where the LLM incrementally builds and maintains a persistent knowledge base. Key insight: the wiki compounds — every ingest and query adds permanent knowledge, unlike RAG which re-derives answers from scratch each time.

## Active Questions

- How do the permission models across tools compare in practice? (needs a synthesis page)
- Which tool's plugin system is most extensible for real-world workflows? (needs deeper analysis)

## Recent Activity

- [2026-05-22] migration — Restructured wiki from domain-based to type-based directories, added frontmatter, created source summaries and domain guide

## See Also

- [Index](./index.md) — full page catalog
- [Log](./log.md) — chronological activity record
