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
