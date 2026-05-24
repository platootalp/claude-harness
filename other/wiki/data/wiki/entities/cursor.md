---
tags: [ai-tools, editor, coding]
date: 2026-05-22
last_updated: 2026-05-22
sources:
  - wiki/sources/cursor-docs.md
status: stable
page_type: entity
---

# Cursor

## Summary

Cursor is an AI-powered code editor with a CLI agent supporting hooks, MCP, permissions, and rules. Official documentation at https://cursor.com/docs.

## Key Areas

### Overview
Cursor is an AI-powered code editor built by Cursor Inc. that integrates intelligent coding assistance directly into the editing experience. It extends beyond the editor with a full CLI agent that supports hooks, MCP server integration, fine-grained permissions, and customizable rules. The combination of editor-native AI and a standalone CLI agent allows developers to work with AI in both interactive and automated contexts.

### CLI
The Cursor CLI agent provides a comprehensive command-line interface. Key commands include `agent` for the main agent mode, `agent login`/`agent logout` for authentication, `agent status`/`agent whoami` for checking state, and `agent models` for listing available models. Session management is supported via `agent ls` and `agent resume`. Headless mode (`-p --force`) enables non-interactive execution suitable for CI/CD pipelines. Shell integration can be installed for enhanced terminal support.

### Hooks
The hooks system provides two primary event types. `preToolUse` hooks fire before a tool executes and can allow, deny, or modify the tool input. `postToolUse` hooks fire after successful tool execution and are useful for auditing and injecting context. Matcher support allows filtering hooks by tool type (for example, targeting only "Shell" tool invocations). Third-party hooks are also supported.

### MCP
Model Context Protocol (MCP) support enables integration with external tools and data sources. MCP servers can be managed via CLI commands: `agent mcp list` to view configured servers, `agent mcp add` to register new ones, and `agent mcp login` for authentication. Configuration is also supported through an `mcp.json` file. MCP tools can be disabled globally if needed.

### Permissions
Permissions are configured using allow and deny lists across four categories: shell commands, file paths (with glob pattern support), web domains, and MCP tools. This provides fine-grained control over what the agent can access and execute, balancing autonomy with safety.

### Rules
Custom rules define project-specific behavioral constraints for the agent. Rules can be generated interactively using the `agent generate-rule` command. These rules guide the agent's behavior to align with team conventions, coding standards, or project-specific requirements.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's approach
- [OpenAI Codex](./codex.md) — Compare with Codex's approach
