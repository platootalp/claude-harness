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
