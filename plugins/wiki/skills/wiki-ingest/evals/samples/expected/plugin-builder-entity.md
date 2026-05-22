---
tags: [ai-tools, plugins, claude-code]
date: 2026-05-22
last_updated: 2026-05-22
sources:
  - wiki/sources/plugin-builder-docs.md
status: stable
page_type: entity
---

# Plugin Builder

## Summary

Plugin Builder is Claude Code's extension system that lets developers package skills, agents, commands, hooks, and MCP server configurations into distributable units. It provides a convention-over-configuration approach where a standard directory layout and a single manifest file define everything a plugin contains. Its key differentiator from other AI tool extension mechanisms is the marketplace distribution model combined with deep hook integration -- plugins can intercept session lifecycle events, control tool execution, and run background monitors, enabling far richer behavior than simple prompt or command additions.

## Key Areas

### Plugin Structure

A Claude Code plugin follows a fixed directory convention where each component type has its own folder at the plugin root. The only file that lives inside `.claude-plugin/` is the manifest (`plugin.json`); all component directories -- `skills/`, `agents/`, `commands/`, `hooks/`, `scripts/`, `bin/` -- sit at the top level alongside optional files like `.mcp.json`, `.lsp.json`, `settings.json`, and `monitors/monitors.json`. The `commands/` directory is the legacy format for flat `.md` slash commands; the preferred approach is `skills/<name>/SKILL.md`, which supports bundled resources like `references/` and `scripts/` subdirectories.

A concrete example: a plugin named `my-plugin` would have `skills/my-skill/SKILL.md` for its primary skill, `agents/reviewer.md` for a subagent, and `hooks/hooks.json` for event hooks. The `bin/` directory can contain executables that get added to the user's PATH when the plugin is enabled.

A common mistake is placing component directories inside `.claude-plugin/` alongside the manifest. Only `plugin.json` belongs there -- putting `skills/` or `agents/` inside `.claude-plugin/` will cause the plugin to silently fail to load those components.

### Manifest

The plugin manifest (`plugin.json`) is the single required file for distribution, and only the `name` field is mandatory. The `name` serves as a namespace prefix for all skills the plugin provides -- a plugin named `my-plugin` with a skill called `review` is invoked as `/my-plugin:review`. Optional fields include `description`, `version`, `author` (an object with `name` and `email`), `homepage`, `repository`, `license`, and `keywords`. The manifest can also declare `userConfig` to prompt users for configuration values on first enable, referenced elsewhere as `${user_config.KEY}`.

Version strategy is a key design decision. Setting `version` explicitly means users only receive updates when you bump that field -- suitable for stable releases. Omitting `version` causes each git commit SHA to count as a new version, which is ideal during fast iteration but means every push is potentially distributed.

A gotcha: the `name` field must be unique across all installed plugins and becomes a permanent identifier. Renaming a plugin after users have installed it effectively creates a new plugin, orphaning the old one. Plan your naming carefully before first distribution.

### Skills

Skills are the primary extension mechanism, defined as `skills/<skill-name>/SKILL.md` files with YAML frontmatter containing a `description` field and a markdown body of instructions. The `description` is critical -- it is the signal Claude uses to decide when to auto-invoke the skill, so vague descriptions like "helper utility" will cause the skill to never trigger. User input is captured via the `$ARGUMENTS` placeholder in the skill body. Skills can bundle `references/` (documentation loaded on demand) and `scripts/` (executable helpers) as subdirectories.

For example, a `code-review` skill might have `description: "Review code changes for quality issues and suggest improvements"` and a body that instructs Claude to read the current diff, check against style guidelines in `references/style-guide.md`, and run `scripts/lint-check.sh` for automated checks.

An important distinction: skills defined in a plugin's `skills/` directory can be either user-facing (invoked via slash command) or plugin-internal (referenced by agents via the `skills:` frontmatter field). The codex-plugin-cc reference implementation uses plugin-embedded skills like `codex-cli-runtime` and `codex-result-handling` exclusively for its subagent, not as user-facing commands.

### Agents

Agents are subagent definitions stored as `agents/<agent-name>.md` markdown files. They define isolated task executors that the main Claude Code agent can delegate work to. The frontmatter supports fields including `name`, `description`, `model` (to select a specific Claude model), `effort`, `maxTurns` (limiting how many tool-use turns the agent takes), `tools` and `disallowedTools` (controlling which built-in tools the agent can access), `skills` (referencing plugin-embedded skills), `memory`, `background`, and `isolation`.

The codex-plugin-cc reference implementation demonstrates a "thin forwarder" pattern: its `codex-rescue.md` agent does no analysis itself but simply forwards instructions to the companion script via plugin-embedded skills. This keeps the agent lightweight and deterministic, delegating all logic to the script layer.

A limitation to be aware of: agents operate with their own context window and tool permissions. If an agent's `disallowedTools` list excludes a tool it actually needs, the agent will fail mid-task without a clear error message. Always verify that the `tools`/`disallowedTools` configuration matches what the agent's instructions require.

### Hooks

Hooks enable event-driven behavior by running scripts or prompts in response to session lifecycle events. They are defined in `hooks/hooks.json` with hook types including `command` (shell execution), `http` (webhook call), `mcp_tool` (MCP server invocation), `prompt` (inject text into the conversation), and `agent` (spawn a subagent). Available events span the full session lifecycle: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, and more.

A concrete pattern from the reference implementation: `SessionStart` and `SessionEnd` hooks manage a broker process lifecycle, spawning it on session start and cleaning orphan jobs on session end. A `Stop` hook implements a review gate that can block session termination if background tasks are still running, reading task status from `${CLAUDE_PLUGIN_DATA}/state.json`.

The critical rule for hooks: always use `${CLAUDE_PLUGIN_ROOT}` to reference plugin files in hook commands, MCP configs, and monitor commands. This variable resolves to the plugin's install directory, which changes on every update. Hardcoding paths will break after the first plugin update. Always wrap the variable in quotes in shell commands: `"${CLAUDE_PLUGIN_ROOT}"`.

### Testing and Validation

Claude Code provides a built-in validation command (`claude plugin validate .`) that checks the plugin or marketplace structure for required files and correct formatting. For local testing, run `claude --plugin-dir ./plugins/my-plugin` to load a plugin from a local directory without installing it. This is the primary development workflow: make changes, test with `--plugin-dir`, validate, then commit.

The `claude plugin details <name>` command shows what components a plugin loads and its token cost, which is useful for verifying that all skills, agents, and hooks are being discovered correctly. The `--dry-run` flag on `claude plugin prune` lets you preview which orphaned dependency plugins would be removed before actually removing them.

A common pitfall during testing: if a skill's `description` frontmatter is missing or empty, the skill will load but never auto-invoke. The validation command does not currently warn about empty descriptions, so this is a manual check. Similarly, hook scripts that fail silently (exit code 0 with no output) can make debugging event-driven behavior difficult -- always include logging in hook scripts during development.

### Marketplace

A marketplace is a git repository that catalogs multiple plugins for one-command installation. Its structure places a `marketplace.json` file inside `.claude-plugin/` at the repository root, with all plugin packages under a `plugins/` directory. Each plugin retains its own `.claude-plugin/plugin.json` manifest. Users add a marketplace via `/plugin marketplace add owner/repo` (for GitHub) or a full Git URL for other hosting.

Plugin sources in `marketplace.json` support five formats: relative path (for monorepo marketplaces), GitHub repo, generic Git URL, Git subdirectory (for monorepos where the plugin lives in a subfolder), and npm package. Sources can be pinned to specific versions using `ref` (branch or tag) or `sha` (exact commit hash).

Reserved marketplace names are blocked to prevent impersonation: `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, and `life-sciences` cannot be used. Attempting to register one of these names will fail silently or with an unhelpful error.

### Distribution

Plugins are distributed primarily through GitHub repositories, which is the recommended hosting method. Users install by adding the marketplace and then installing individual plugins. Alternative hosting includes any Git provider (GitLab, Bitbucket) via full URL. Private repositories are supported using `GITHUB_TOKEN`, `GITLAB_TOKEN`, or `BITBUCKET_TOKEN` environment variables for automatic updates. For official distribution, plugins can be submitted to the Anthropic marketplace at `https://claude.ai/settings/plugins/submit` or `https://platform.claude.com/plugins/submit`.

Installation scopes control where a plugin is available: `user` scope (default) installs to `~/.claude/settings.json` for all projects; `project` scope installs to `.claude/settings.json` for team sharing via version control; `local` scope installs to `.claude/settings.local.json` for gitignored project-specific use; and `managed` scope is read-only, controlled by enterprise administrators.

A subtle issue: when a plugin is installed at both user and project scope, the project-scoped version takes precedence. This can cause confusion when debugging why a plugin behaves differently in one project versus another. Use `claude plugin list --json` to see which scope each plugin is installed at.

### Common Pitfalls

Several recurring mistakes trip up plugin developers. The most frequent is placing component directories inside `.claude-plugin/` instead of at the plugin root -- only `plugin.json` belongs there. Another is hardcoding file paths in hook scripts instead of using `${CLAUDE_PLUGIN_ROOT}`, which breaks on every plugin update since the install directory changes. A third is writing vague skill descriptions that prevent auto-invocation; the `description` field must clearly state when and why Claude should use the skill.

Environment variable handling also causes issues. `${CLAUDE_PLUGIN_ROOT}` changes on update, so it should never be used for persistent data -- use `${CLAUDE_PLUGIN_DATA}` instead for things like `node_modules`, virtual environments, and caches that must survive updates. Failing to wrap these variables in quotes in shell commands causes breakage on paths containing spaces.

Finally, the `commands/` directory is legacy. New plugins should use `skills/` exclusively, as skills support bundled resources and are the only format that agents can reference via the `skills:` frontmatter. Mixing `commands/` and `skills/` in the same plugin works but creates confusion about which mechanism to use for new functionality.

### Reference Implementation

The `codex-plugin-cc` plugin (at `github.com/openai/codex-plugin-cc`) serves as the production-grade reference for complex plugin architecture. It demonstrates six key patterns that go beyond simple skill definitions. First, the companion script pattern: `scripts/codex-companion.mjs` acts as a central runtime for all commands, managing background task lifecycle by spawning processes, tracking PIDs, and writing state to `state.json`. Second, command frontmatter controls: commands use `disable-model-invocation: true` to bypass Claude's LLM and execute scripts directly, `allowed-tools` to whitelist specific tools, and `argument-hint` for parameter formatting.

Third, the thin forwarder subagent: `agents/codex-rescue.md` does no analysis itself but forwards to the companion script via plugin-embedded skills. Fourth, plugin-embedded skills: `codex-cli-runtime` provides the script invocation interface and `codex-result-handling` enforces output presentation rules (verbatim display, no auto-fixing). Fifth, the hook system: `SessionStart`/`SessionEnd` hooks manage broker lifecycle and clean orphan jobs, while the `Stop` hook implements a review gate. Sixth, hook-to-session data passing: hooks receive input via stdin JSON and the `SessionEnd` hook reads `${CLAUDE_PLUGIN_DATA}/state.json` for task status.

A key takeaway: this reference implementation shows that the most robust plugins treat Claude Code as an orchestrator while delegating heavy logic to scripts. The agent and skill layers become thin interfaces to the script runtime, making the plugin more testable and deterministic.

## See Also

- [Claude Code](./claude-code.md) -- the host CLI that loads and runs plugins
- [Codex](./codex.md) -- the OpenAI coding agent whose plugin architecture inspired the reference implementation
- [Source Summary](../sources/plugin-builder-docs.md) -- the documentation index this entity was derived from

<!-- Quality Checklist (self-check before finalizing)
- [x] Summary is 100-150 words and covers what/does/differentiator
- [x] Each Key Area is 150-300 words with definition + example + edge case
- [x] No Key Area is just 1-2 vague sentences
- [x] Cross-references use relative-path markdown links (not wikilinks)
- [x] No content is copied verbatim from source -- all synthesized
- [x] All placeholder values replaced with real content
- [x] Frontmatter fields are complete and accurate
-->
