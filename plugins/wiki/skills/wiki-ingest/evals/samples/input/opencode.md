---
tags: [ai-tools, cli, coding]
date: 2026-05-22
source_url: https://opencode.ai/docs/
media: doc-index
domain: ai-tools
status: processed
---

# OpenCode Documentation Index

Source: https://opencode.ai/docs/

Schema references:
- Config schema: https://opencode.ai/config.json
- TUI schema: https://opencode.ai/tui.json

## Getting Started
- Overview: https://opencode.ai/docs/
- Configuration: https://opencode.ai/docs/config/
- Providers: https://opencode.ai/docs/providers/
- Network: https://opencode.ai/docs/network/
- Enterprise: https://opencode.ai/docs/enterprise/
- Troubleshooting: https://opencode.ai/docs/troubleshooting/
- Windows/WSL: https://opencode.ai/docs/windows-wsl

## Usage
- Go (programmatic): https://opencode.ai/docs/go/
- TUI: https://opencode.ai/docs/tui/
- CLI: https://opencode.ai/docs/cli/
- Web: https://opencode.ai/docs/web/
- IDE: https://opencode.ai/docs/ide/
- Zen (curated models): https://opencode.ai/docs/zen/
- Share: https://opencode.ai/docs/share/
- GitHub integration: https://opencode.ai/docs/github/
- GitLab integration: https://opencode.ai/docs/gitlab/

## Configure
- Tools: https://opencode.ai/docs/tools/
- Rules (AGENTS.md): https://opencode.ai/docs/rules/
- Agents: https://opencode.ai/docs/agents/
- Models: https://opencode.ai/docs/models/
- Themes: https://opencode.ai/docs/themes/
- Keybinds: https://opencode.ai/docs/keybinds/
- Commands: https://opencode.ai/docs/commands/
- Formatters: https://opencode.ai/docs/formatters/
- Permissions: https://opencode.ai/docs/permissions/
- LSP Servers: https://opencode.ai/docs/lsp/
- MCP Servers: https://opencode.ai/docs/mcp-servers/
- ACP Support: https://opencode.ai/docs/acp/
- Agent Skills: https://opencode.ai/docs/skills/
- Custom Tools: https://opencode.ai/docs/custom-tools/

## Develop
- SDK: https://opencode.ai/docs/sdk/
- Server: https://opencode.ai/docs/server/
- Plugins: https://opencode.ai/docs/plugins/
- Ecosystem: https://opencode.ai/docs/ecosystem/

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
