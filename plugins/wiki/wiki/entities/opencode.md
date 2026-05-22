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

OpenCode is a provider-agnostic AI coding CLI supporting 75+ LLMs. Features TUI, CLI, web, and IDE interfaces with skills, MCP, plugins, custom tools, and permissions. Official documentation at https://opencode.ai/docs/.

## Key Areas

### Overview
OpenCode is a provider-agnostic AI coding CLI that supports over 75 LLM providers, allowing developers to use models from Anthropic, OpenAI, Google, and many others through a single interface. It offers multiple interaction modes including a terminal UI (TUI), a command-line interface, a web interface, and IDE integration. A "Zen" mode provides curated model selections, and a "Share" feature enables collaboration.

### Interfaces
OpenCode provides several ways to interact with the agent. The TUI (terminal UI) is the primary interactive interface with full customization support. The CLI mode enables scripted and headless usage. A web interface provides browser-based access. IDE integration brings OpenCode into the editor. Zen mode offers a simplified experience with curated model options. GitHub and GitLab integrations connect directly to repository workflows.

### Configuration
Configuration uses JSON or JSONC files with `$schema` support for validation and autocompletion. Eight priority levels determine which settings take precedence, ranging from remote configuration down to macOS managed preferences. TUI-specific configuration allows customizing the terminal interface appearance and behavior. Network and enterprise configurations support organizational deployments.

### Built-in Tools
OpenCode ships with 12 built-in tools: bash (shell command execution), edit (file editing), write (file creation), read (file reading), grep (content search), glob (file pattern matching), apply_patch (patch application), skill (skill invocation), todowrite (task tracking), webfetch (HTTP requests), websearch (web search), question (user prompts), and lsp (language server protocol integration).

### Built-in Agents
Primary agents include Build (for implementation tasks) and Plan (for planning and analysis). Subagents handle specialized work: General for broad tasks, Explore for codebase navigation, and Scout for targeted searching. Hidden system agents manage infrastructure: Compaction for context management, Title for session naming, and Summary for conversation summarization.

### Permissions
The permission model defines three actions: allow (execute without prompting), ask (require user approval), and deny (block execution). Permissions use glob patterns for file matching, and the last matching rule wins in case of conflicts. This provides flexible and predictable access control.

### Skills
Skills follow the SKILL.md format with YAML frontmatter. Discovery paths include `.opencode/skills/` at the project level and `~/.config/opencode/skills/` globally. OpenCode is also compatible with skills from `.claude/skills/` and `.agents/skills/` directories, enabling cross-tool skill reuse.

### Custom Tools
Custom tools are written as TypeScript files using the `tool()` helper function with Zod schemas for input validation. This allows developers to extend OpenCode's capabilities with type-safe, validated tool implementations that integrate seamlessly with the agent framework.

### Plugins
Plugins are TypeScript modules distributed as npm packages. They can hook into key events in the OpenCode lifecycle, enabling deep customization and extension of the platform. The plugin system supports both local development and published package distribution.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's approach
- [OpenAI Codex](./codex.md) — Compare with Codex's approach
