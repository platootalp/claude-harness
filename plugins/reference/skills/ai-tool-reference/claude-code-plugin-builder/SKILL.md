---
name: claude-code-plugin-builder
description: >
  Build Claude Code plugins and plugin marketplaces from scratch. Use this skill whenever the user
  wants to create a plugin, build a marketplace, publish skills/agents/hooks as a distributable
  plugin, migrate standalone .claude/ configs to a plugin, or set up a plugin distribution system.
  Also use when the user mentions plugin development, plugin packaging, marketplace creation,
  plugin marketplace setup, sharing plugins with a team, or submitting plugins to the official
  Anthropic marketplace. Covers the full lifecycle: plugin structure, manifest, skills, agents,
  hooks, MCP/LSP servers, marketplace.json, hosting, versioning, and distribution.
  **Reference implementation**: see `references/codex-plugin-cc.md` for an architecture analysis of the
  openai/codex-plugin-cc production plugin (https://github.com/openai/codex-plugin-cc), covering companion
  scripts, embedded subagent skills, SessionStart/SessionEnd/Stop hooks, and command frontmatter patterns.
---

# Claude Code Plugin Builder

Build Claude Code plugins and plugin marketplaces — from a single skill plugin to a full team distribution system.

## Reference Implementation

Before building, study the reference architecture document at `references/codex-plugin-cc.md`.
It analyzes the openai/codex-plugin-cc plugin (https://github.com/openai/codex-plugin-cc) and covers:
- Companion script design and job state management
- Command frontmatter controls (`disable-model-invocation`, `allowed-tools`, `argument-hint`)
- Thin forwarder subagent pattern
- Plugin-embedded skills
- SessionStart/SessionEnd/Stop hook lifecycle
- Stop-time gate mechanism
- Hook-to-session data passing via stdin JSON

## When to Use This Skill

- Creating a new plugin (any complexity: simple skill to full enterprise plugin)
- Building a plugin marketplace to distribute plugins
- Migrating existing `.claude/` standalone configs into a shareable plugin
- Publishing plugins to the official Anthropic marketplace
- Setting up versioning, hosting, and distribution for plugins

## Core Concepts

**Plugin vs Standalone**: Standalone `.claude/` configs are for personal, single-project use. Plugins are for sharing, distribution, versioning, and cross-project reuse. Plugin skills are namespaced (`/plugin-name:skill-name`) to avoid collisions.

**Marketplace**: A directory (git repo) with a `marketplace.json` that lists plugins and their sources. Users add it via `/plugin marketplace add` and install individual plugins.

## Step 1: Decide What You're Building

Ask the user:
1. **What functionality should the plugin provide?** (skills, agents, hooks, MCP servers, LSP servers, monitors — or a combination)
2. **Who is it for?** (personal, team, community, official marketplace)
3. **How will it be distributed?** (local, GitHub repo, marketplace, npm)

If the user already has `.claude/` configs they want to share, jump to [Migrating Standalone Configs](#migrating-standalone-configs).

## Step 2: Create the Plugin Structure

### Directory Layout

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

**Critical rule**: Only `plugin.json` goes inside `.claude-plugin/`. All component directories (`skills/`, `agents/`, `hooks/`, etc.) must be at the plugin root level, NOT inside `.claude-plugin/`.

### Create the Manifest

```json
{
  "name": "my-plugin",
  "description": "Brief description of what the plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "homepage": "https://github.com/you/my-plugin",
  "repository": "https://github.com/you/my-plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"]
}
```

**Required fields**: Only `name` is required if you include a manifest. The `name` becomes the namespace prefix for skills (e.g., `/my-plugin:skill-name`).

**Version strategy**:
- Set `version` explicitly → users only get updates when you bump this field
- Omit `version` → each git commit SHA counts as a new version (best for fast iteration)

### Add Skills

Create `skills/<skill-name>/SKILL.md`:

```markdown
---
description: What this skill does and when Claude should use it
---

Instructions for Claude when this skill is invoked.
```

The `description` in frontmatter is critical — it's how Claude decides when to auto-invoke the skill. Make it specific about both what the skill does and when to use it.

**Skill arguments**: Use `$ARGUMENTS` placeholder to capture user input after the skill name.

```markdown
---
description: Generate a deployment config for the specified environment
---

Create a deployment configuration for the "$ARGUMENTS" environment...
```

**Bundled resources**: Skills can include supporting files:

```
skills/
└── pdf-processor/
    ├── SKILL.md
    ├── references/      # Docs loaded on demand
    │   └── api-spec.md
    └── scripts/         # Executable helpers
        └── extract.py
```

### Add Agents

Create `agents/<agent-name>.md`:

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities. Use when auditing code, checking for OWASP issues, or reviewing authentication logic.
model: sonnet
effort: medium
maxTurns: 20
disallowedTools: Write, Edit
---

You are a security-focused code reviewer. Analyze the provided code for:
1. Injection vulnerabilities
2. Authentication issues
3. Data exposure risks
...
```

Supported frontmatter: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`.

### Add Hooks

Create `hooks/hooks.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/lint.sh"
          }
        ]
      }
    ]
  }
}
```

**Hook types**: `command`, `http`, `mcp_tool`, `prompt`, `agent`

**Available events**: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, and many more.

**Always use `${CLAUDE_PLUGIN_ROOT}`** to reference plugin files in hook commands, MCP configs, and monitor commands. This resolves to the plugin's installed directory at runtime.

### Add MCP Servers

Create `.mcp.json` in the plugin root:

```json
{
  "mcpServers": {
    "my-tool": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server/index.js"],
      "env": {
        "CONFIG_PATH": "${CLAUDE_PLUGIN_ROOT}/config.json"
      }
    }
  }
}
```

### Add LSP Servers

Create `.lsp.json` in the plugin root:

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

### Add Monitors

Create `monitors/monitors.json`:

```json
[
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log"
  }
]
```

### User Configuration

Add `userConfig` to `plugin.json` to prompt users for values on first enable:

```json
{
  "userConfig": {
    "api_endpoint": {
      "type": "string",
      "title": "API Endpoint",
      "description": "Your team's API endpoint"
    },
    "api_token": {
      "type": "string",
      "title": "API Token",
      "description": "Authentication token",
      "sensitive": true
    }
  }
}
```

Reference values in commands and configs as `${user_config.api_endpoint}`.

## Step 3: Test the Plugin Locally

```bash
# Load plugin directly for testing
claude --plugin-dir ./my-plugin

# Load from a zip archive
claude --plugin-dir ./my-plugin.zip

# Load multiple plugins
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
```

After loading, test each component:
- Skills: `/my-plugin:skill-name`
- Agents: check `/agents`
- Hooks: trigger the relevant events
- Run `/reload-plugins` after making changes (no restart needed)

**Validate the plugin**:
```bash
claude plugin validate .
```

## Step 4: Build a Plugin Marketplace

### Marketplace Structure

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

### Create marketplace.json

```json
{
  "name": "my-marketplace",
  "description": "Description of this marketplace",
  "owner": {
    "name": "Your Team",
    "email": "team@example.com"
  },
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./plugins/my-plugin",
      "description": "What this plugin does",
      "version": "1.0.0",
      "author": {
        "name": "Author Name"
      }
    }
  ]
}
```

**Reserved marketplace names** (cannot use): `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`.

### Plugin Sources

Each plugin in the marketplace needs a `source` telling Claude Code where to get it:

| Source Type | Format | Example |
|:---|:---|:---|
| Relative path | string starting with `./` | `"./plugins/my-plugin"` |
| GitHub | object with `repo` | `{"source": "github", "repo": "owner/repo"}` |
| Git URL | object with `url` | `{"source": "url", "url": "https://gitlab.com/team/plugin.git"}` |
| Git subdirectory | object with `url` + `path` | `{"source": "git-subdir", "url": "https://github.com/org/mono.git", "path": "tools/plugin"}` |
| npm | object with `package` | `{"source": "npm", "package": "@org/plugin"}` |

Pin to specific versions with `ref` (branch/tag) or `sha` (exact commit).

### Test the Marketplace Locally

```bash
# Add marketplace
/plugin marketplace add ./my-marketplace

# Install a plugin from it
/plugin install my-plugin@my-marketplace

# Test the installed skill
/my-plugin:skill-name
```

### Validate the Marketplace

```bash
claude plugin validate .
```

## Step 5: Host and Distribute

### GitHub Hosting (Recommended)

1. Push the marketplace repo to GitHub
2. Users add it: `/plugin marketplace add owner/repo`
3. Pin to branch/tag: `/plugin marketplace add owner/repo@v2.0`

### Other Git Hosting

```bash
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### Private Repositories

For manual operations, existing git credentials work (`gh auth login`, SSH keys, etc.).

For background auto-updates, set environment tokens:
- GitHub: `GITHUB_TOKEN` or `GH_TOKEN`
- GitLab: `GITLAB_TOKEN` or `GL_TOKEN`
- Bitbucket: `BITBUCKET_TOKEN`

### Require Marketplaces for Your Team

Add to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "company-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "code-formatter@company-tools": true
  }
}
```

### Lock Down Marketplace Sources

Use `strictKnownMarketplaces` in managed settings to restrict which marketplaces users can add:

```json
{
  "strictKnownMarketplaces": [
    {"source": "github", "repo": "acme-corp/approved-plugins"},
    {"source": "hostPattern", "hostPattern": "^github\\.example\\.com$"}
  ]
}
```

### Submit to Official Anthropic Marketplace

- Claude.ai: [claude.ai/settings/plugins/submit](https://claude.ai/settings/plugins/submit)
- Console: [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)

## Step 6: Version Management

| Strategy | How | Update Behavior | Best For |
|:---|:---|:---|:---|
| Explicit version | Set `"version"` in `plugin.json` | Users get updates only when you bump this field | Published plugins with stable releases |
| Commit SHA version | Omit `version` entirely | Every git commit is a new version | Fast-moving internal/team plugins |

**Important**: If you set `version`, pushing new commits without bumping it has no effect — users stay on the cached version. Don't set `version` in both `plugin.json` and `marketplace.json`; `plugin.json` always wins silently.

### Release Channels

Create separate marketplaces pointing to different refs:

```json
// stable-marketplace/.claude-plugin/marketplace.json
{"plugins": [{"name": "tool", "source": {"source": "github", "repo": "org/tool", "ref": "stable"}}]}

// latest-marketplace/.claude-plugin/marketplace.json
{"plugins": [{"name": "tool", "source": {"source": "github", "repo": "org/tool", "ref": "latest"}}]}
```

Assign via managed settings `extraKnownMarketplaces` per user group.

## Migrating Standalone Configs

Convert existing `.claude/` configs to a plugin:

1. Create plugin structure:
   ```bash
   mkdir -p my-plugin/.claude-plugin
   ```

2. Create manifest:
   ```json
   // my-plugin/.claude-plugin/plugin.json
   {"name": "my-plugin", "description": "Migrated from standalone", "version": "1.0.0"}
   ```

3. Copy existing files:
   ```bash
   cp -r .claude/commands my-plugin/
   cp -r .claude/agents my-plugin/
   cp -r .claude/skills my-plugin/
   ```

4. Migrate hooks from `.claude/settings.json` to `my-plugin/hooks/hooks.json` (same format).

5. Test: `claude --plugin-dir ./my-plugin`

After migration, you can remove the original `.claude/` files — the plugin version takes priority.

## Environment Variables Reference

| Variable | Purpose | Use Case |
|:---|:---|:---|
| `${CLAUDE_PLUGIN_ROOT}` | Plugin install directory (changes on update) | Reference bundled scripts, binaries, configs |
| `${CLAUDE_PLUGIN_DATA}` | Persistent data directory (survives updates) | `node_modules`, virtual envs, caches, generated code |
| `${CLAUDE_PROJECT_DIR}` | Project root directory | Reference project-local scripts or configs |
| `${user_config.KEY}` | User-configured values from `userConfig` | API endpoints, tokens, settings |

**Always wrap in quotes** in shell commands: `"${CLAUDE_PLUGIN_ROOT}"`.

## Common Pitfalls

| Pitfall | Solution |
|:---|:---|
| Components inside `.claude-plugin/` | Move them to plugin root. Only `plugin.json` belongs in `.claude-plugin/`. |
| Using absolute paths | All paths must be relative with `./` prefix |
| Referencing files outside plugin dir | Plugins are copied to cache; external files aren't included. Use symlinks within the marketplace or bundle files. |
| Missing `${CLAUDE_PLUGIN_ROOT}` in hooks/MCP | Always use the variable, since install paths change on update |
| Setting version but not bumping it | Either bump on every release, or omit `version` for commit-SHA versioning |
| Relative paths in URL-based marketplaces | Relative paths only work in git-hosted marketplaces. Use GitHub/npm/git-URL sources for URL-based distribution. |
| Duplicate version in `plugin.json` and `marketplace.json` | `plugin.json` wins silently. Set version in only one place. |

## References: Troubleshooting & Debug

### Debug Tools

| Tool | Command | What It Shows |
|:---|:---|:---|
| Debug mode | `claude --debug` | Plugin loading, manifest errors, skill/agent/hook registration, MCP server init |
| Validate plugin | `claude plugin validate .` or `/plugin validate` | Syntax and schema errors in `plugin.json`, skill/agent/command frontmatter, `hooks/hooks.json` |
| Plugin details | `claude plugin details <name>` | Component inventory, token cost estimates (always-on vs on-invoke) |
| Plugin list | `claude plugin list` | Installed plugins, versions, source marketplaces, enabled status |
| Reload plugins | `/reload-plugins` | Reload hooks, MCP servers, LSP servers after changes (no restart needed) |
| Doctor | `/doctor` | Reports ignored folders when both default dir and manifest key exist (v2.1.140+) |

### Common Problems & Solutions

| Problem | Cause | Solution |
|:---|:---|:---|
| Plugin not loading | Invalid `plugin.json` | Run `claude plugin validate` to check syntax/schema errors |
| Skills not appearing | Wrong directory structure | Ensure `skills/` and `commands/` are at plugin root, NOT inside `.claude-plugin/` |
| Hooks not firing | Script not executable | Run `chmod +x script.sh` |
| MCP server fails | Missing `${CLAUDE_PLUGIN_ROOT}` | Use the variable for all plugin paths |
| Path errors | Used absolute paths | All paths must be relative with `./` prefix |
| LSP `Executable not found in $PATH` | Language server binary not installed | Install binary separately (e.g., `npm install -g typescript-language-server typescript`) |
| Plugin loads but components missing | Components inside `.claude-plugin/` | Only `plugin.json` belongs in `.claude-plugin/`; move all component dirs to root |
| Updates not reaching users | `version` set but not bumped | Bump `version` in `plugin.json`, or omit it for commit-SHA versioning |
| Default dirs ignored | Manifest key overrides default path | When manifest specifies `commands`/`agents`, default dirs are replaced. List both: `"commands": ["./commands/", "./extras/"]` |
| Monitors not starting | Not in interactive CLI | Monitors only run in interactive CLI sessions, not in `-p` mode or non-interactive hosts |

### Error Messages Reference

**Manifest validation errors**:

| Error Message | Cause | Fix |
|:---|:---|:---|
| `Invalid JSON syntax: Unexpected token } in JSON at position 142` | Malformed JSON | Check for missing commas, trailing commas, or unquoted strings in `plugin.json` |
| `Plugin has an invalid manifest file at .claude-plugin/plugin.json. Validation errors: name: Required` | Missing required field | Add `"name"` field to `plugin.json` |
| `Plugin has a corrupt manifest file at .claude-plugin/plugin.json. JSON parse error: ...` | JSON parse failure | Fix JSON syntax in manifest |

**Plugin loading errors**:

| Error Message | Cause | Fix |
|:---|:---|:---|
| `Warning: No commands found in plugin my-plugin custom directory: ./cmds. Expected .md files or SKILL.md in subdirectories.` | Custom command path exists but has no valid files | Add `.md` files or `SKILL.md` subdirectories to the referenced path |
| `Plugin directory not found at path: ./plugins/my-plugin. Check that the marketplace entry has the correct path.` | `marketplace.json` source path invalid | Fix the `source` path in marketplace entry to point to existing directory |
| `Plugin my-plugin has conflicting manifests: both plugin.json and marketplace entry specify components.` | Duplicate component definitions | Remove duplicate component defs or set `strict: false` in marketplace entry |

### Hook Troubleshooting

**Hook script not executing**:
1. Check executable permission: `chmod +x ./scripts/your-script.sh`
2. Verify shebang line: first line should be `#!/bin/bash` or `#!/usr/bin/env bash`
3. Check path uses `${CLAUDE_PLUGIN_ROOT}`: `"command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/your-script.sh"`
4. Test manually: `./scripts/your-script.sh`

**Hook not triggering on expected event**:
1. Verify event name is correct (case-sensitive): `PostToolUse` not `postToolUse`
2. Check matcher pattern matches your tool: `"matcher": "Write|Edit"` for file operations
3. Confirm hook type is valid: `command`, `http`, `mcp_tool`, `prompt`, or `agent`

**Available hook events** (case-sensitive):

| Category | Events |
|:---|:---|
| Session lifecycle | `SessionStart`, `Setup`, `Stop`, `StopFailure`, `SessionEnd` |
| User interaction | `UserPromptSubmit`, `UserPromptExpansion`, `Elicitation`, `ElicitationResult` |
| Tool execution | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionRequest`, `PermissionDenied` |
| Subagents & tasks | `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle` |
| File & config | `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove` |
| Notifications | `Notification` |
| Compaction | `PreCompact`, `PostCompact` |

### MCP Server Troubleshooting

**Server not starting**:
1. Check command exists and is executable
2. Verify all paths use `${CLAUDE_PLUGIN_ROOT}` variable
3. Check MCP server logs: `claude --debug` shows initialization errors
4. Test server manually outside Claude Code

**Server tools not appearing**:
1. Ensure server is configured in `.mcp.json` or `plugin.json`
2. Verify server correctly implements MCP protocol
3. Check debug output for connection timeouts

**Persistent data for dependencies**:

When MCP servers need installed dependencies (e.g., `node_modules`), use `${CLAUDE_PLUGIN_DATA}` for persistence across updates. Compare bundled manifest with data copy to detect when re-install is needed:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "diff -q \"${CLAUDE_PLUGIN_ROOT}/package.json\" \"${CLAUDE_PLUGIN_DATA}/package.json\" >/dev/null 2>&1 || (cd \"${CLAUDE_PLUGIN_DATA}\" && cp \"${CLAUDE_PLUGIN_ROOT}/package.json\" . && npm install) || rm -f \"${CLAUDE_PLUGIN_DATA}/package.json\""
          }
        ]
      }
    ]
  }
}
```

Then point the MCP server to the persistent modules:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.js"],
      "env": {
        "NODE_PATH": "${CLAUDE_PLUGIN_DATA}/node_modules"
      }
    }
  }
}
```

### Plugin Cache & File Resolution

**Cache behavior**: Market-installed plugins are copied to `~/.claude/plugins/cache`. Each version gets its own directory. Old versions are marked orphaned and auto-deleted after 7 days.

**Key implications for debugging**:
- `${CLAUDE_PLUGIN_ROOT}` points to the cache copy, not the source repo
- Changes to source repo require `/plugin update` to propagate
- Glob/Grep tools skip orphaned version directories automatically
- When a plugin updates mid-session, hooks/MCP/LSP continue using the OLD path until `/reload-plugins` (monitors need session restart)

**Path traversal limitation**: Installed plugins cannot reference files outside their directory. `../shared-utils` won't work after installation because external files aren't copied to cache.

**Symlink behavior in marketplaces**:
| Symlink Target | Behavior |
|:---|:---|
| Inside plugin's own directory | Preserved as relative symlink in cache |
| Elsewhere in same marketplace | Dereferenced — target content copied into cache |
| Outside marketplace | Skipped for security |

### CLI Commands Reference

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

### Installation Scopes

| Scope | Settings File | Use Case |
|:---|:---|:---|
| `user` (default) | `~/.claude/settings.json` | Personal plugins available in all projects |
| `project` | `.claude/settings.json` | Team plugins shared via version control |
| `local` | `.claude/settings.local.json` | Project-specific, gitignored |
| `managed` | Managed settings | Read-only, admin-controlled plugins |

## Quick Reference: Full Workflow

```
1. mkdir my-plugin/.claude-plugin
2. Create plugin.json with name, description, version
3. Add components: skills/, agents/, hooks/, .mcp.json, etc.
4. Test: claude --plugin-dir ./my-plugin
5. Validate: claude plugin validate .
6. For marketplace: create marketplace.json with plugin sources
7. Push to git hosting (GitHub recommended)
8. Users: /plugin marketplace add owner/repo
9. Users: /plugin install plugin-name@marketplace-name
10. Updates: /plugin update or /plugin marketplace update
```
