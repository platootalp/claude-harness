---
tags: [ai-tools, editor, coding, cursor, documentation]
date: 2026-05-22
last_updated: 2026-05-22
source: raw/ai-tools/cursor.md
status: stable
page_type: source
---

# Cursor Documentation Index

## Summary
The Cursor documentation index covers the official documentation for Cursor, an AI-powered code editor with a CLI agent interface. The index is organized around four main areas: Getting Started, CLI Reference, the Hooks system, and MCP (Model Context Protocol) integration. Compared to other AI coding tools, Cursor's documentation is more compact and focused, reflecting its editor-centric design with a CLI agent component. The documentation is hosted at `cursor.com/docs`.

## Key Points
- Cursor provides both an editor-based experience and a full CLI agent interface, with the CLI serving as the primary programmatic interaction method.
- The CLI agent supports a rich command set including `agent` (main mode), `agent login/logout` (auth), `agent status/whoami` (status), `agent models` (model listing), `agent mcp list/add/login` (MCP management), `agent generate-rule` (customization), and `agent -p --force` (headless CI mode).
- The Hooks system supports `preToolUse` (allow, deny, or modify tool input) and `postToolUse` (audit or inject context after execution), with matcher support for filtering hooks by tool type.
- MCP integration is first-class: servers can be listed, added, and authenticated via CLI commands, with configuration through `mcp.json`. MCP tools can be disabled globally.
- Permissions are configurable with allow/deny lists covering shell commands, file paths (glob patterns), web domains, and MCP tools.
- Customization rules can be generated via `agent generate-rule` to control agent behavior.
- Session management is supported through `agent ls` (list sessions), `agent resume <session>` (resume), and `agent create-chat` (new chat).
- Shell integration can be installed via `agent install-shell-integration` for enhanced terminal experience.
- Third-party hooks are supported and documented separately from the core hooks system.
- Headless mode (`agent -p --force`) enables CI/CD integration without interactive prompts.

## Notable Details
- Source URL: `https://cursor.com/docs`
- CLI parameters documented at `https://cursor.com/docs/cli/reference/parameters`
- Permissions reference at `https://cursor.com/docs/cli/reference/permissions`
- MCP documentation at `https://cursor.com/docs/cli/mcp`
- Hooks documentation at `https://cursor.com/docs/hooks`
- Third-party hooks at `https://cursor.com/docs/reference/third-party-hooks`
- The `preToolUse` hook can return allow, deny, or modify input -- giving fine-grained control over tool execution
- Matcher support in hooks enables filtering by tool type (e.g., targeting only "Shell" tool invocations)

## See Also
- [[claude-code-docs]] -- Claude Code documentation index
- [[codex-docs]] -- OpenAI Codex documentation index
- [[opencode-docs]] -- OpenCode documentation index
- [[plugin-builder-docs]] -- Claude Code Plugin Builder documentation
