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

Cursor is an AI-powered code editor developed by Cursor Inc. that integrates intelligent coding assistance directly into the editing experience. Unlike standalone CLI agents, Cursor combines a full-featured code editor with an AI assistant, providing editor-native completions, chat, and code generation alongside traditional editing capabilities. Its key differentiator is the dual-interface design: a polished editor experience for interactive work and a CLI agent (`cursor agent`) for automated and headless workflows, connected through a shared configuration and permission system.

## Key Areas

### Overview

Cursor is built around the idea that AI assistance should be native to the editing experience rather than bolted on as a separate tool. The editor provides inline AI completions, a chat panel for conversational coding, and code generation features that operate directly on the open file. Beyond the editor, the CLI agent extends Cursor's capabilities to terminal-based and automated workflows — it can be used interactively or in headless mode for CI/CD integration. The two interfaces share configuration, permissions, and the same underlying AI models, creating a consistent experience whether you're in the editor or the terminal.

A concrete example: a developer can use the editor's chat to prototype a function, then switch to the CLI agent to run the same AI capabilities on a batch of files via headless mode. The configuration and rules defined in the editor apply to the CLI agent as well.

An important edge case: the CLI agent and editor are separate processes — closing the editor does not affect running CLI agent sessions, and vice versa. This is by design for reliability, but it means state (like active MCP connections) is not shared between them.

### CLI

The Cursor CLI agent provides a comprehensive command-line interface accessible via the `cursor agent` command. The primary subcommands are: `agent` for the main interactive agent mode, `agent login`/`agent logout` for authentication, `agent status`/`agent whoami` for checking connection state, and `agent models` for listing available AI models. Session management is supported through `agent ls` (list sessions) and `agent resume <session>` (resume a previous session), enabling developers to pick up where they left off.

For automation, headless mode (`cursor agent -p "<prompt>" --force`) enables non-interactive execution suitable for CI/CD pipelines and scripted workflows. The `--force` flag skips all confirmation prompts, which is essential for unattended execution but should be used with caution since it grants the agent full autonomy within its permission boundaries.

A notable detail: shell integration can be installed via `agent install-shell-integration`, which enhances terminal support by allowing the agent to better understand the shell environment. However, this integration is optional — the CLI agent works without it, just with reduced context about the shell state.

### Hooks

The hooks system provides two primary event types that allow custom code to run at key points in the agent's execution cycle. `preToolUse` hooks fire before a tool executes and can take three actions: allow (proceed), deny (block the tool call), or modify the tool input (change parameters before execution). `postToolUse` hooks fire after successful tool execution and are primarily useful for auditing (logging what was done) and injecting context (adding information to the agent's awareness after a tool runs).

Matcher support allows filtering hooks by tool type — for example, targeting only "Shell" tool invocations to add custom validation for shell commands without affecting file operations. Third-party hooks are also supported, enabling community extensions to the hook system.

A limitation: hooks run synchronously, meaning a slow `preToolUse` hook will delay the tool execution. There is no timeout mechanism built into the hook system, so a misbehaving hook can effectively freeze the agent. This is important to keep in mind when writing hooks that make network calls or perform heavy computation.

### MCP

Model Context Protocol (MCP) support enables Cursor to integrate with external tools and data sources through a standardized interface. MCP servers can be managed via CLI commands: `agent mcp list` to view currently configured servers, `agent mcp add` to register new ones, and `agent mcp login <identifier>` for authentication with servers that require it. Configuration is also supported through an `mcp.json` file for declarative server setup, which is useful for project-specific MCP configurations that can be committed to version control.

MCP tools provided by connected servers appear alongside Cursor's built-in tools and can be used by the agent in the same way. If needed, MCP tools can be disabled globally through configuration — this is useful when a server is causing issues and you want to quickly disable it without removing the configuration.

An edge case: MCP server connections are established at agent startup. Adding a new server via `agent mcp add` requires restarting the agent session for the new server to become available. There is no hot-reload mechanism for MCP servers.

### Permissions

Permissions are configured using allow and deny lists across four categories: shell commands, file paths, web domains, and MCP tools. File path permissions support glob pattern matching — for example, `src/**/*.ts` allows access to all TypeScript files under `src/`, while `!**/.env` explicitly denies access to environment files. The deny list takes precedence over the allow list when both match, following a "deny by default" security philosophy.

This four-category approach provides fine-grained control over what the agent can access and execute, balancing autonomy with safety. A developer can allow broad file access while restricting specific sensitive directories, or allow general shell commands while blocking dangerous ones like `rm -rf`.

A practical gotcha: glob patterns in file path permissions are evaluated relative to the project root, not the current working directory. This means `*.json` matches JSON files only in the project root, not in subdirectories. Use `**/*.json` to match recursively.

### Rules

Custom rules define project-specific behavioral constraints for the agent, guiding it to align with team conventions, coding standards, or project-specific requirements. Rules can be generated interactively using the `agent generate-rule` command, which walks through a series of questions to produce a rule definition. Rules can also be written manually.

Rules are loaded from project-level configuration and apply to all agent sessions within that project. They provide a way to encode team knowledge — for example, "always use absolute imports in this project" or "never modify files in the generated/ directory" — so that the agent follows the same conventions as the human developers.

A limitation: rules are advisory, not enforced. The agent will attempt to follow them, but complex or contradictory rules may be applied inconsistently. For hard security boundaries, use the permissions system instead of rules.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's approach to CLI agent and permissions
- [OpenCode](./opencode.md) — Compare with OpenCode's provider-agnostic approach
- [Codex](./codex.md) — Compare with Codex's cloud-sandboxed execution model
- [Cursor Docs Source](../sources/cursor-docs.md) — The source document this page was derived from
