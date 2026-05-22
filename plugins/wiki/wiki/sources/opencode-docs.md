---
tags: [ai-tools, cli, coding, opencode, documentation]
date: 2026-05-22
last_updated: 2026-05-22
source: raw/ai-tools/opencode.md
status: stable
page_type: source
---

# OpenCode Documentation Index

## Summary
The OpenCode documentation index covers the official documentation for OpenCode, an open-source AI coding agent with strong emphasis on configurability and extensibility. The index is organized into four sections: Getting Started, Usage, Configure, and Develop. OpenCode distinguishes itself with a detailed quick reference section that documents built-in tools, agents, permissions, skills, custom commands, MCP servers, plugins, custom tools, rules, and variable substitution -- providing a compact but information-dense reference alongside the full documentation. The documentation is hosted at `opencode.ai/docs/`.

## Key Points
- OpenCode supports multiple usage interfaces: Go (programmatic), TUI (terminal UI), CLI, Web, IDE, Zen (curated models), Share, and integrations with GitHub and GitLab.
- Configuration uses JSON/JSONC with `$schema` support and 8 priority levels ranging from remote to macOS managed settings. A separate TUI config handles terminal UI customization.
- 12 built-in tools are provided: bash, edit, write, read, grep, glob, apply_patch, skill, todowrite, webfetch, websearch, question, lsp.
- Built-in agents include Primary (Build, Plan), Subagents (General, Explore, Scout), and hidden system agents (Compaction, Title, Summary).
- Permissions use three actions (allow, ask, deny) with glob patterns for file matching, where the last matching rule wins.
- Skills follow the SKILL.md format with discovery paths at `.opencode/skills/` and `~/.config/opencode/skills/`, and are compatible with `.claude/skills/` and `.agents/skills/` directories.
- Custom commands can be defined via JSON config or markdown files in `.opencode/commands/`.
- MCP servers support both local (command + env) and remote (URL + headers/OAuth) configurations with CLI management commands.
- Plugins are TypeScript modules distributed as npm packages with key event hooks.
- Custom tools use TypeScript files with the `tool()` helper and Zod schemas for validation.
- Variable substitution supports `{env:VAR}` for environment variables and `{file:path}` for file contents.

## Notable Details
- Source URL: `https://opencode.ai/docs/`
- Config schema available at `https://opencode.ai/config.json`
- TUI schema available at `https://opencode.ai/tui.json`
- ACP (Agent Communication Protocol) support documented at `https://opencode.ai/docs/acp/`
- LSP server configuration at `https://opencode.ai/docs/lsp/`
- SDK documentation at `https://opencode.ai/docs/sdk/`
- Server mode at `https://opencode.ai/docs/server/`
- Ecosystem overview at `https://opencode.ai/docs/ecosystem/`
- Rules follow the AGENTS.md convention at `https://opencode.ai/docs/rules/`
- Windows/WSL support documented at `https://opencode.ai/docs/windows-wsl`
- Enterprise documentation at `https://opencode.ai/docs/enterprise/`

## See Also
- [[claude-code-docs]] -- Claude Code documentation index
- [[codex-docs]] -- OpenAI Codex documentation index
- [[cursor-docs]] -- Cursor documentation index
- [[plugin-builder-docs]] -- Claude Code Plugin Builder documentation
