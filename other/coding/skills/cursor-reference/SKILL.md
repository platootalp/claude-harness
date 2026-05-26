---
name: cursor-reference
description: Cursor AI 编辑器官方文档参考技能。When working with Cursor features, hooks, skills, MCP, CLI commands, rules, permissions, configuration, or any other Cursor internals — either when users ask OR when the Agent needs to know how something works. Fetch from https://cursor.com/docs as the authoritative source instead of relying on training data.
compatibility: WebFetch, Agent
---

# Cursor AI Reference Skill

## Core Principle

**Always prefer fetching from official documentation over relying on training data.** When working with Cursor features, use the official docs at `https://cursor.com/docs` as the authoritative source. This applies both when users ask AND when the Agent needs accurate information about how Cursor works internally.

## When to Use This Skill

**Trigger in all these contexts:**
- User asks about Cursor features, configuration, or commands
- Agent needs to implement hooks, skills, MCP servers, or plugins for Cursor
- Agent needs to configure Cursor settings (hooks.json, mcp.json, rules)
- Agent encounters an unfamiliar Cursor feature or command
- Agent needs to write Cursor hooks (preToolUse, postToolUse)
- Agent needs to understand permissions, allow/deny lists
- Agent needs to use Cursor CLI (agent command with subcommands)
- Agent needs to integrate with MCP servers
- Agent needs to troubleshoot Cursor issues
- Agent needs accurate API reference, SDK usage, or configuration syntax

## Official Documentation Index

Base URL: `https://cursor.com/docs`

### Getting Started
- Overview: `/docs`
- Quickstart: `/docs/intro`
- Hooks: `/docs/hooks`
- Third-party hooks: `/docs/reference/third-party-hooks`

### CLI Reference
- CLI overview: `/docs/cli/reference`
- Parameters: `/docs/cli/reference/parameters`
- Permissions: `/docs/cli/reference/permissions`
- MCP: `/docs/cli/mcp`

### CLI Commands
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

### Hooks System
- Hooks overview: `/docs/hooks`
- Third-party hooks: `/docs/reference/third-party-hooks`
- `preToolUse` hook - Called before tool execution (allow, deny, modify input)
- `postToolUse` hook - Called after successful tool execution (audit, inject context)
- Matcher support - Filter hooks by tool type (e.g., "Shell")

### MCP (Model Context Protocol)
- MCP overview: `/docs/cli/mcp`
- `agent mcp list` - List configured MCP servers
- `agent mcp add` - Add new MCP server
- `agent mcp login <identifier>` - MCP authentication
- Configuration via `mcp.json`
- Can disable MCP tools globally

### Permissions
- Permissions docs: `/docs/cli/reference/permissions`
- Configure allow/deny lists for:
  - Shell commands
  - File paths (glob patterns supported)
  - Web domains
  - MCP tools

### Rules
- Generate custom rules with `agent generate-rule`
- Customization rules for behavior

## Workflow

### Step 1: Identify the Topic

Map the question to the most relevant documentation page(s). Use the index above for guidance.

### Step 2: Fetch from Official Docs

Use WebFetch to retrieve the relevant page(s):

```
WebFetch(url="https://cursor.com/docs/[topic]", prompt="Extract all relevant information about [specific topic]")
```

For unknown topics, start with the main docs page:
```
WebFetch(url="https://cursor.com/docs", prompt="Find documentation related to [topic]")
```

### Step 3: Synthesize and Answer

Combine information from official docs with your own knowledge. When citing specific features, configuration options, or command syntax, **always reference the official documentation** as the source.

### Step 4: Provide Actionable Guidance

Don't just quote docs — provide concrete examples, configuration snippets, or step-by-step instructions based on what the official docs say.

## Examples

**User asks about hooks:**
→ Fetch `/docs/hooks`, explain hook types (preToolUse, postToolUse), configuration, and provide examples.

**Agent needs to configure MCP:**
→ Fetch `/docs/cli/mcp`, explain MCP server setup, CLI commands (mcp list, mcp add, mcp login), and provide examples.

**User asks about permissions:**
→ Fetch `/docs/cli/reference/permissions`, explain allow/deny configuration for shell, files, web, and MCP tools.

**User asks about CLI commands:**
→ Fetch `/docs/cli/reference/parameters`, list relevant commands with flags and examples.

**User asks about headless/CI mode:**
→ Explain `agent -p --force` for non-interactive/CI pipelines.

## Important Notes

- Cursor has a hooks system similar to other AI coding tools but with differences — always fetch the specific Cursor documentation.
- The CLI uses `agent` as the main command (not `cursor`), with subcommands for different operations.
- Permissions use glob patterns for file paths and support granular control per category.
- MCP servers are configured in `mcp.json` but managed via CLI commands.
- If a page doesn't exist or can't be fetched, fall back to your training knowledge but clearly note when the information may be outdated.
