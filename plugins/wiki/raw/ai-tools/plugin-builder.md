# Claude Code Plugin Builder Documentation Index

Source: https://code.claude.com/docs/en/plugins.md

Reference implementation: https://github.com/openai/codex-plugin-cc

## Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json         # Plugin manifest (required for distribution)
├── skills/                  # Skills as <name>/SKILL.md
│   └── my-skill/
│       └── SKILL.md
├── commands/                # Skills as flat .md files (legacy, prefer skills/)
│   └── status.md
├── agents/                  # Subagent definitions
│   └── reviewer.md
├── hooks/                   # Hook configuration
│   └── hooks.json
├── .mcp.json               # MCP server definitions
├── .lsp.json               # LSP server configuration
├── monitors/                # Background monitors
│   └── monitors.json
├── bin/                     # Executables added to PATH
├── settings.json            # Default settings when plugin is enabled
├── scripts/                 # Supporting scripts
└── README.md
```

Critical rule: Only `plugin.json` goes inside `.claude-plugin/`. All component directories (`skills/`, `agents/`, `hooks/`, etc.) must be at the plugin root level, NOT inside `.claude-plugin/`.

## Plugin Manifest (plugin.json)

Required fields: Only `name` is required. The `name` becomes the namespace prefix for skills (e.g., `/my-plugin:skill-name`).

```json
{
  "name": "my-plugin",
  "description": "Brief description of what the plugin does",
  "version": "1.0.0",
  "author": { "name": "Your Name", "email": "you@example.com" },
  "homepage": "https://github.com/you/my-plugin",
  "repository": "https://github.com/you/my-plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"]
}
```

Version strategy:
- Set `version` explicitly -> users only get updates when you bump this field
- Omit `version` -> each git commit SHA counts as a new version (best for fast iteration)

## Skills

Create `skills/<skill-name>/SKILL.md`:

```markdown
---
description: What this skill does and when Claude should use it
---

Instructions for Claude when this skill is invoked.
```

The `description` in frontmatter is critical -- it's how Claude decides when to auto-invoke the skill.

Skill arguments: Use `$ARGUMENTS` placeholder to capture user input.

Bundled resources: Skills can include `references/` (docs loaded on demand) and `scripts/` (executable helpers).

## Agents

Create `agents/<agent-name>.md`:

Supported frontmatter: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`.

## Hooks

Create `hooks/hooks.json`. Hook types: `command`, `http`, `mcp_tool`, `prompt`, `agent`.

Available events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, and many more.

Always use `${CLAUDE_PLUGIN_ROOT}` to reference plugin files in hook commands, MCP configs, and monitor commands.

## MCP Servers

Create `.mcp.json` in the plugin root. Use `${CLAUDE_PLUGIN_ROOT}` for all plugin paths.

## LSP Servers

Create `.lsp.json` in the plugin root.

## Monitors

Create `monitors/monitors.json`. Monitors only run in interactive CLI sessions.

## User Configuration

Add `userConfig` to `plugin.json` to prompt users for values on first enable. Reference values as `${user_config.KEY}`.

## Marketplace Structure

```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace catalog
├── plugins/
│   ├── my-plugin/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   └── another-plugin/
│       └── ...
└── README.md
```

Reserved marketplace names (cannot use): `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`.

## Plugin Sources

| Source Type | Format | Example |
|:---|:---|:---|
| Relative path | string starting with `./` | `"./plugins/my-plugin"` |
| GitHub | object with `repo` | `{"source": "github", "repo": "owner/repo"}` |
| Git URL | object with `url` | `{"source": "url", "url": "https://gitlab.com/team/plugin.git"}` |
| Git subdirectory | object with `url` + `path` | `{"source": "git-subdir", "url": "https://github.com/org/mono.git", "path": "tools/plugin"}` |
| npm | object with `package` | `{"source": "npm", "package": "@org/plugin"}` |

Pin to specific versions with `ref` (branch/tag) or `sha` (exact commit).

## Hosting & Distribution

- GitHub (recommended): Users add via `/plugin marketplace add owner/repo`
- Other Git hosting: `/plugin marketplace add https://gitlab.com/company/plugins.git`
- Private repos: Use `GITHUB_TOKEN`, `GITLAB_TOKEN`, or `BITBUCKET_TOKEN` for auto-updates
- Submit to official Anthropic marketplace: https://claude.ai/settings/plugins/submit or https://platform.claude.com/plugins/submit

## Environment Variables

| Variable | Purpose | Use Case |
|:---|:---|:---|
| `${CLAUDE_PLUGIN_ROOT}` | Plugin install directory (changes on update) | Reference bundled scripts, binaries, configs |
| `${CLAUDE_PLUGIN_DATA}` | Persistent data directory (survives updates) | `node_modules`, virtual envs, caches, generated code |
| `${CLAUDE_PROJECT_DIR}` | Project root directory | Reference project-local scripts or configs |
| `${user_config.KEY}` | User-configured values from `userConfig` | API endpoints, tokens, settings |

Always wrap in quotes in shell commands: `"${CLAUDE_PLUGIN_ROOT}"`.

## CLI Commands

| Command | Purpose |
|:---|:---|
| `claude plugin install <name> [-s scope]` | Install plugin (scope: user/project/local) |
| `claude plugin uninstall <name> [-s scope] [--keep-data] [--prune]` | Uninstall plugin |
| `claude plugin enable <name> [-s scope]` | Enable disabled plugin |
| `claude plugin disable <name> [-s scope]` | Disable without uninstalling |
| `claude plugin update <name> [-s scope]` | Update to latest version |
| `claude plugin list [--json] [--available]` | List installed plugins |
| `claude plugin details <name>` | Show components and token cost |
| `claude plugin validate .` | Validate plugin/marketplace structure |
| `claude plugin prune [-s scope] [--dry-run]` | Remove orphaned dependency plugins |
| `claude plugin tag [--push] [--dry-run] [-f]` | Create release git tag for plugin |

## Installation Scopes

| Scope | Settings File | Use Case |
|:---|:---|:---|
| `user` (default) | `~/.claude/settings.json` | Personal plugins available in all projects |
| `project` | `.claude/settings.json` | Team plugins shared via version control |
| `local` | `.claude/settings.local.json` | Project-specific, gitignored |
| `managed` | Managed settings | Read-only, admin-controlled plugins |

## Reference Implementation: codex-plugin-cc

Source: https://github.com/openai/codex-plugin-cc

The openai/codex-plugin-cc plugin is a production-grade reference for complex plugin architecture.

### Directory Structure

```
plugins/codex/
├── .claude-plugin/
│   └── plugin.json
├── commands/                     # slash commands (.md files)
│   ├── review.md
│   ├── adversarial-review.md
│   ├── rescue.md
│   ├── setup.md
│   ├── status.md
│   ├── cancel.md
│   └── result.md
├── agents/
│   └── codex-rescue.md
├── skills/                       # plugin-embedded skills (for agent use)
│   ├── codex-cli-runtime/
│   ├── codex-result-handling/
│   └── gpt-5-4-prompting/
├── prompts/                      # hook script prompt templates
├── hooks/
│   └── hooks.json
├── scripts/                      # core runtime (Node.js)
│   ├── codex-companion.mjs
│   ├── session-lifecycle-hook.mjs
│   ├── stop-review-gate-hook.mjs
│   ├── app-server-broker.mjs
│   └── lib/
├── schemas/
├── package.json
└── tsconfig.app-server.json
```

### Core Architecture Patterns

1. **Companion Script** (`scripts/codex-companion.mjs`): Central runtime for all commands. Manages background task lifecycle (spawn/track PIDs/write state.json), communicates with external services, outputs structured results.

2. **Command Frontmatter Controls**: Commands use YAML frontmatter to control Claude Code behavior:
   - `disable-model-invocation: true` -- disables Claude LLM, only executes script
   - `allowed-tools: Bash(node:*)` -- whitelist specific tools
   - `argument-hint` -- parameter format hint

3. **Thin Forwarder Subagent** (`agents/codex-rescue.md`): Agent that only forwards to companion script, never analyzes code itself. Uses `skills:` frontmatter to reference plugin-embedded skills.

4. **Plugin-Embedded Skills** (`skills/`): Private skills for internal agent use via `skills:` frontmatter:
   - codex-cli-runtime -- companion script invocation interface
   - codex-result-handling -- output presentation rules (verbatim, no auto-fix)

5. **Hook System** (`hooks/hooks.json`): SessionStart/SessionEnd manage broker lifecycle and clean orphan jobs. Stop hook implements a review gate that can block or allow session termination.

6. **Hook-to-Session Data Passing**: Hook input via stdin JSON. SessionEnd reads `${CLAUDE_PLUGIN_DATA}/state.json` for task status.

### Key Files

| Purpose | URL |
|:---|:---|
| Companion script | https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/scripts/codex-companion.mjs |
| Hook definition | https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/hooks/hooks.json |
| Command example (with frontmatter) | https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/commands/review.md |
| Subagent definition | https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/agents/codex-rescue.md |
| Lifecycle hook handler | https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/scripts/session-lifecycle-hook.mjs |
| Stop gate hook handler | https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/scripts/stop-review-gate-hook.mjs |
| CLI runtime skill | https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/skills/codex-cli-runtime/SKILL.md |
| Result handling skill | https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/skills/codex-result-handling/SKILL.md |
| Plugin manifest | https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/.claude-plugin/plugin.json |
