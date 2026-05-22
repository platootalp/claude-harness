---
tags: [ai-tools, plugins, coding]
date: 2026-05-22
last_updated: 2026-05-22
sources:
  - wiki/sources/plugin-builder-docs.md
status: stable
page_type: entity
---

# Plugin Builder

## Summary

Guide for building Claude Code plugins and marketplaces. Covers the full lifecycle from structure to distribution, with a reference implementation analysis of the openai/codex-plugin-cc production plugin.

## Key Areas

### Plugin Structure
A Claude Code plugin is a directory containing a `.claude-plugin/plugin.json` manifest (required for distribution). All component directories reside at the plugin root level, not inside `.claude-plugin/`. Components include `skills/` (reusable workflows), `agents/` (subagent definitions), `hooks/` (event hooks), `.mcp.json` (MCP server definitions), `.lsp.json` (LSP server configuration), `monitors/` (background monitors), `bin/` (executables added to PATH), `scripts/` (supporting scripts), and `settings.json` (default settings). Only `plugin.json` goes inside `.claude-plugin/`.

### Manifest
The `plugin.json` manifest requires at minimum a `name` field, which becomes the namespace prefix for skills (e.g., `/my-plugin:skill-name`). Optional fields include version, description, author, license, repository, homepage, and keywords. The `userConfig` field prompts users for configuration values on first enable, referenced as `${user_config.KEY}`. Version strategy: set `version` explicitly for controlled updates, or omit it so each git commit SHA counts as a new version for fast iteration.

### Skills
Skills are defined in `skills/<skill-name>/SKILL.md` with YAML frontmatter containing a `description` field that determines when Claude auto-invokes the skill. The `$ARGUMENTS` placeholder captures user input at invocation time. Skills can bundle `references/` (documentation loaded on demand) and `scripts/` (executable helper scripts) as subdirectories.

### Agents
Agents are defined as markdown files in `agents/<agent-name>.md` with YAML frontmatter. Supported frontmatter fields include `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, and `isolation`. The `skills` frontmatter can reference plugin-embedded skills for internal agent use.

### Hooks
Hooks are configured in `hooks/hooks.json` with five hook types: `command`, `http`, `mcp_tool`, `prompt`, and `agent`. Available events include `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, and more. All plugin file references in hook commands must use `${CLAUDE_PLUGIN_ROOT}` to ensure correct path resolution after updates.

### Testing & Validation
Plugins can be tested locally using `claude --plugin-dir ./path/to/plugin`. The `/reload-plugins` command refreshes loaded plugins during development. Structural validation is performed with `claude plugin validate .`, which checks the manifest, component layout, and configuration correctness.

### Marketplace
A marketplace is defined by a `marketplace.json` file inside `.claude-plugin/` that catalogs available plugins. Plugin sources support five types: relative path (`./plugins/my-plugin`), GitHub (`{"source": "github", "repo": "owner/repo"}`), Git URL, Git subdirectory, and npm package. Versions can be pinned with `ref` (branch/tag) or `sha` (exact commit). Reserved marketplace names cannot be used (e.g., `anthropic-marketplace`, `claude-code-marketplace`).

### Distribution
GitHub is the recommended hosting method; users add marketplaces via `/plugin marketplace add owner/repo`. Other Git hosting platforms like GitLab are also supported. Private repositories use `GITHUB_TOKEN`, `GITLAB_TOKEN`, or `BITBUCKET_TOKEN` for automatic updates. Plugins can be submitted to the official Anthropic marketplace at `https://claude.ai/settings/plugins/submit`. Installation scopes include user, project, local, and managed levels.

### Common Pitfalls
Several mistakes frequently trip up plugin authors. Placing component directories inside `.claude-plugin/` instead of the plugin root will cause discovery failures. Using absolute paths breaks portability. Referencing files outside the plugin directory is not supported. Missing `CLAUDE_PLUGIN_ROOT` in hooks and MCP configs leads to path resolution errors. Forgetting to bump the version field prevents users from receiving updates. Including a duplicate version field in both `plugin.json` and elsewhere causes conflicts. Relative paths in URL-based marketplaces do not resolve correctly.

### Reference Implementation (codex-plugin-cc)
The `openai/codex-plugin-cc` plugin demonstrates production-grade architecture patterns. A companion script (`codex-companion.mjs`) serves as the central runtime, managing background task lifecycle and communicating with external services. Command frontmatter controls Claude Code behavior (e.g., `disable-model-invocation: true` to bypass the LLM). A thin forwarder subagent delegates entirely to the companion script rather than analyzing code itself. Plugin-embedded skills (e.g., `codex-cli-runtime`, `codex-result-handling`) are private to the plugin's agents. Hooks manage session lifecycle and implement a stop-time review gate that can block session termination pending task completion.

## See Also

- [Claude Code](./claude-code.md) — The platform plugins run on
