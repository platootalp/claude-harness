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
