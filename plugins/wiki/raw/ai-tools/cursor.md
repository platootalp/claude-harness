---
tags: [ai-tools, editor, coding]
date: 2026-05-22
source_url: https://cursor.com/docs
media: doc-index
domain: ai-tools
status: processed
---

# Cursor Documentation Index

Source: https://cursor.com/docs

## Getting Started
- Overview: https://cursor.com/docs
- Quickstart: https://cursor.com/docs/intro
- Hooks: https://cursor.com/docs/hooks
- Third-party hooks: https://cursor.com/docs/reference/third-party-hooks

## CLI Reference
- CLI overview: https://cursor.com/docs/cli/reference
- Parameters: https://cursor.com/docs/cli/reference/parameters
- Permissions: https://cursor.com/docs/cli/reference/permissions
- MCP: https://cursor.com/docs/cli/mcp

## CLI Commands
- `agent` - Main agent mode command
- `agent login` / `agent logout` - Authentication
- `agent status` / `agent whoami` - Status check
- `agent models` - List available models
- `agent mcp list` - List MCP servers
- `agent mcp add` - Add MCP server
- `agent mcp login <identifier>` - Login to MCP
- `agent about` - About cursor
- `agent update` - Update cursor
- `agent ls` - List sessions
- `agent resume <session>` - Resume a session
- `agent create-chat` - Create new chat
- `agent generate-rule` / `agent rule` - Generate customization rules
- `agent install-shell-integration` - Install shell integration
- `agent -p --force` - Headless mode for CI

## Hooks System
- Hooks overview: https://cursor.com/docs/hooks
- Third-party hooks: https://cursor.com/docs/reference/third-party-hooks
- `preToolUse` hook - Called before tool execution (allow, deny, modify input)
- `postToolUse` hook - Called after successful tool execution (audit, inject context)
- Matcher support - Filter hooks by tool type (e.g., "Shell")

## MCP (Model Context Protocol)
- MCP overview: https://cursor.com/docs/cli/mcp
- `agent mcp list` - List configured MCP servers
- `agent mcp add` - Add new MCP server
- `agent mcp login <identifier>` - MCP authentication
- Configuration via `mcp.json`
- Can disable MCP tools globally

## Permissions
- Permissions docs: https://cursor.com/docs/cli/reference/permissions
- Configure allow/deny lists for:
  - Shell commands
  - File paths (glob patterns supported)
  - Web domains
  - MCP tools

## Rules
- Generate custom rules with `agent generate-rule`
- Customization rules for behavior
