---
name: opencode-reference
description: OpenCode AI CLI 官方文档参考技能。When working with OpenCode features, configuration, plugins, skills, MCP, permissions, agents, custom tools, TUI, CLI commands, SDK, or any other OpenCode internals — either when users ask OR when the Agent needs to know how something works. Fetch from https://opencode.ai/office/ as the authoritative source instead of relying on training data. Make sure to use this skill whenever the Agent encounters an OpenCode feature it doesn't fully understand, needs to configure opencode.json, create plugins/tools, use MCP servers, work with skills/agents, or needs accurate information about OpenCode commands, permissions, or APIs.
compatibility: WebFetch, Agent
---

# OpenCode AI Reference Skill

## Core Principle

**Always prefer fetching from official documentation over relying on training data.** When working with OpenCode features, use the official docs at `https://opencode.ai/docs/` as the authoritative source. This applies both when users ask AND when the Agent needs accurate information about how OpenCode works internally.

## When to Use This Skill

**Trigger in all these contexts:**
- User asks about OpenCode features, configuration, or commands
- Agent needs to implement plugins, skills, or MCP servers for OpenCode
- Agent needs to configure opencode.json or tui.json correctly
- Agent encounters an unfamiliar OpenCode feature or command
- Agent needs to write OpenCode plugins with event hooks
- Agent needs to create custom agents, custom tools, or custom commands
- Agent needs to understand the permissions system
- Agent needs to use OpenCode TUI, CLI, or non-interactive mode
- Agent needs to integrate with MCP servers (local or remote)
- Agent needs to configure formatters, LSP servers, or themes
- Agent needs to troubleshoot OpenCode issues
- Agent needs accurate CLI reference, environment variables, or tool usage
- Agent needs to work with the OpenCode SDK or server mode

## Official Documentation Index

The documentation site is at: `https://opencode.ai/docs/`

Key documentation pages (use WebFetch to retrieve):

### Getting Started
- Overview: `/docs/`
- Configuration: `/docs/config/`
- Providers: `/docs/providers/`
- Network: `/docs/network/`
- Enterprise: `/docs/enterprise/`
- Troubleshooting: `/docs/troubleshooting/`
- Windows/WSL: `/docs/windows-wsl`

### Usage
- Go (programmatic): `/docs/go/`
- TUI: `/docs/tui/`
- CLI: `/docs/cli/`
- Web: `/docs/web/`
- IDE: `/docs/ide/`
- Zen (curated models): `/docs/zen/`
- Share: `/docs/share/`
- GitHub integration: `/docs/github/`
- GitLab integration: `/docs/gitlab/`

### Configure
- Tools: `/docs/tools/`
- Rules (AGENTS.md): `/docs/rules/`
- Agents: `/docs/agents/`
- Models: `/docs/models/`
- Themes: `/docs/themes/`
- Keybinds: `/docs/keybinds/`
- Commands: `/docs/commands/`
- Formatters: `/docs/formatters/`
- Permissions: `/docs/permissions/`
- LSP Servers: `/docs/lsp/`
- MCP Servers: `/docs/mcp-servers/`
- ACP Support: `/docs/acp/`
- Agent Skills: `/docs/skills/`
- Custom Tools: `/docs/custom-tools/`

### Develop
- SDK: `/docs/sdk/`
- Server: `/docs/server/`
- Plugins: `/docs/plugins/`
- Ecosystem: `/docs/ecosystem/`

### Schema References
- Config schema: `https://opencode.ai/config.json`
- TUI schema: `https://opencode.ai/tui.json`

## Workflow

### Step 1: Identify the Topic

Map the question to the most relevant documentation page(s). Use the index above for guidance.

### Step 2: Fetch from Official Docs

Use WebFetch to retrieve the relevant page(s):

```
WebFetch(url="https://opencode.ai/docs/[topic]/", prompt="Extract all relevant information about [specific topic]")
```

For config schema details:
```
WebFetch(url="https://opencode.ai/config.json", prompt="Extract the configuration schema for OpenCode")
```

### Step 3: Synthesize and Answer

Combine information from official docs with your own knowledge. When citing specific features, configuration options, or command syntax, **always reference the official documentation** as the source.

### Step 4: Provide Actionable Guidance

Don't just quote docs — provide concrete examples, configuration snippets, or step-by-step instructions based on what the official docs say.

## Quick Reference

### Configuration

OpenCode uses **JSON/JSONC** config files with `$schema` support:
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true,
  "server": { "port": 4096 }
}
```

**Config locations (merged, lowest to highest priority):**
1. Remote config (`.well-known/opencode`)
2. Global config (`~/.config/opencode/opencode.json`)
3. Custom config (`OPENCODE_CONFIG` env var)
4. Project config (`opencode.json` in project root)
5. `.opencode` directories
6. Inline config (`OPENCODE_CONFIG_CONTENT` env var)
7. Managed config files (system directories)
8. macOS managed preferences (`.mobileconfig` via MDM)

**TUI config:** `~/.config/opencode/tui.json` (separate from main config)

### Built-in Tools

| Tool | Description | Permission Key |
|------|-------------|----------------|
| `bash` | Execute shell commands | `bash` |
| `edit` | Modify files via string replacement | `edit` |
| `write` | Create/overwrite files | `edit` |
| `read` | Read file contents | `read` |
| `grep` | Search content (regex) | `grep` |
| `glob` | Find files by glob pattern | `glob` |
| `apply_patch` | Apply patch/diff files | `edit` |
| `skill` | Load a SKILL.md file | `skill` |
| `todowrite` | Manage todo/task lists | `todowrite` |
| `webfetch` | Fetch web pages | `webfetch` |
| `websearch` | Web search via Exa AI | `websearch` |
| `question` | Ask user questions | `question` |
| `lsp` | LSP code intelligence (experimental) | `lsp` |

### Built-in Agents

**Primary agents:** Build (default, full tools), Plan (restricted, edit/bash=ask)

**Subagents:** General (full tools, no todo), Explore (read-only codebase search), Scout (read-only external docs/dependency research)

**Hidden system agents:** Compaction, Title, Summary

### Permissions

Three actions: `"allow"`, `"ask"`, `"deny"`. Configured in `opencode.json`:
```json
{
  "permission": {
    "*": "ask",
    "read": "allow",
    "bash": { "*": "ask", "git status *": "allow" },
    "edit": { "~/projects/personal/**": "deny" }
  }
}
```

Last matching rule wins. Glob patterns supported: `*` (any chars), `?` (single char).

### Skills

SKILL.md files in `.opencode/skills/<name>/` or `~/.config/opencode/skills/<name>/`.
Also compatible with `.claude/skills/` and `.agents/skills/` directories.

```markdown
---
name: my-skill
description: What this skill does
---
Skill instructions here...
```

### Custom Commands

Defined in `opencode.json` under `command`, or as markdown files in `.opencode/commands/`:
```jsonc
{
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report.\nFocus on failing tests and suggest fixes.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-haiku-4-5"
    }
  }
}
```

### MCP Servers

```jsonc
{
  "mcp": {
    "my-local-server": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-command"],
      "enabled": true,
      "environment": { "MY_ENV_VAR": "value" }
    },
    "my-remote-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "enabled": true,
      "headers": { "Authorization": "Bearer {env:MY_API_KEY}" },
      "oauth": false
    }
  }
}
```

CLI: `opencode mcp add`, `opencode mcp list`, `opencode mcp auth <name>`

### Plugins

TypeScript modules in `.opencode/plugins/` or `~/.config/opencode/plugins/`, or npm packages:
```json
{ "plugin": ["opencode-helicone-session", "@my-org/custom-plugin"] }
```

Key event hooks: `tool.execute.before`, `tool.execute.after`, `session.created`, `session.idle`, `message.updated`, `file.edited`, `shell.env`

### Custom Tools

TypeScript files in `.opencode/tools/` or `~/.config/opencode/tools/`:
```ts
import { tool } from "@opencode-ai/plugin"
export default tool({
  description: "Query the project database",
  args: { query: tool.schema.string().describe("SQL query") },
  async execute(args) { return `Executed: ${args.query}` }
})
```

### Rules (AGENTS.md)

- Project: `AGENTS.md` in project root (or `CLAUDE.md` as fallback)
- Global: `~/.config/opencode/AGENTS.md`
- Additional: `instructions` field in `opencode.json` (supports glob patterns and remote URLs)

### Variable Substitution

- `{env:VARIABLE_NAME}` — environment variable (empty string if unset)
- `{file:path/to/file}` — file contents (relative, absolute, or `~` paths)

### Key CLI Commands

| Command | Description |
|---------|-------------|
| `opencode` | Start TUI |
| `opencode run [message]` | Non-interactive mode |
| `opencode serve` | Headless HTTP server |
| `opencode auth login` | Configure API keys |
| `opencode agent create` | Create custom agent |
| `opencode mcp add` | Add MCP server |
| `opencode models` | List available models |
| `opencode session list` | List sessions |
| `opencode stats` | Token usage and costs |
| `opencode export [id]` | Export session as JSON |

## Examples

**User asks about plugins:**
→ Fetch `/docs/plugins/`, explain Plugin API, event hooks, npm/local loading, and provide TypeScript examples.

**Agent needs to configure MCP:**
→ Fetch `/docs/mcp-servers/`, explain local and remote MCP server configuration, OAuth, and provide examples.

**User asks about custom agents:**
→ Fetch `/docs/agents/`, explain built-in agents, custom agent creation (JSON and Markdown), permissions, and subagent configuration.

**User asks about skills:**
→ Fetch `/docs/skills/`, explain SKILL.md format, discovery paths, triggering, and permissions.

**User asks about permissions:**
→ Fetch `/docs/permissions/`, explain permission actions, granular rules, glob patterns, per-agent overrides, and bash-specific permissions.

**User asks about CLI commands:**
→ Fetch `/docs/cli/`, list relevant commands with flags and examples.

**User asks about configuration:**
→ Fetch `/docs/config/`, explain config file locations, merge order, schema options, variable substitution, and provide examples.

**User asks about TUI usage:**
→ Fetch `/docs/tui/`, explain slash commands, keybinds, file references, editor integration, and tui.json options.

**User asks about custom tools:**
→ Fetch `/docs/custom-tools/`, explain tool definition with `tool()` helper, argument schemas, context, and multi-language support.

**User asks about rules/instructions:**
→ Fetch `/docs/rules/`, explain AGENTS.md, precedence, custom instructions, and Claude Code compatibility.

## Important Notes

- OpenCode uses **JSON/JSONC** config format (not YAML/TOML) in `opencode.json` and `tui.json`.
- Configuration files are **merged** (not replaced) — later configs override only conflicting keys.
- OpenCode is **provider-agnostic** — supports 75+ LLM providers through Models.dev.
- Skills are loaded **on-demand** via the `skill` tool, not pre-loaded into context.
- The `edit` permission controls `write`, `edit`, and `apply_patch` tools together.
- MCP servers can be **local** (command + env) or **remote** (URL + headers/OAuth).
- Plugins are written in **TypeScript/JavaScript** using the `@opencode-ai/plugin` package.
- Custom tools use **Zod** for argument schema validation.
- OpenCode is compatible with Claude Code conventions (`CLAUDE.md`, `.claude/skills/`) as fallbacks.
- OpenCode documentation is actively maintained — prefer real-time fetch over cached knowledge.
- If a page doesn't exist or can't be fetched, fall back to your training knowledge but clearly note when the information may be outdated.
