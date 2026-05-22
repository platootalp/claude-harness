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
