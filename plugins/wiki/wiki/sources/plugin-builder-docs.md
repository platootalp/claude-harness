---
tags: [ai-tools, plugins, coding, claude-code, documentation]
date: 2026-05-22
last_updated: 2026-05-22
source: raw/ai-tools/plugin-builder.md
status: stable
page_type: source
---

# Claude Code Plugin Builder Documentation Index

## Summary
The Plugin Builder documentation index provides a comprehensive reference for building, distributing, and managing plugins for Claude Code. It covers the full plugin lifecycle: directory structure, manifest configuration, component types (skills, agents, hooks, MCP servers, LSP servers, monitors), user configuration, marketplace creation, plugin sources and hosting, environment variables, CLI commands, and installation scopes. The documentation also includes a detailed reference implementation analysis of the `openai/codex-plugin-cc` plugin, which demonstrates production-grade plugin architecture patterns including companion scripts, command frontmatter controls, thin forwarder subagents, plugin-embedded skills, hook systems, and hook-to-session data passing.

## Key Points
- Plugin structure places only `plugin.json` inside `.claude-plugin/`; all component directories (skills/, agents/, hooks/, etc.) must be at the plugin root level, not inside `.claude-plugin/`.
- The plugin manifest (`plugin.json`) requires only a `name` field. The name becomes the namespace prefix for skills (e.g., `/my-plugin:skill-name`). Version strategy: explicit `version` for controlled updates, or omit `version` for continuous delivery via git commit SHA.
- Skills use `skills/<skill-name>/SKILL.md` with YAML frontmatter. The `description` field in frontmatter is critical as it determines when Claude auto-invokes the skill. Skills support `$ARGUMENTS` for user input and can bundle `references/` and `scripts/` subdirectories.
- Agents are defined in `agents/<agent-name>.md` with frontmatter supporting `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, and `isolation`.
- Hooks are configured in `hooks/hooks.json` with types: command, http, mcp_tool, prompt, agent. Available events include SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, and more.
- Three key environment variables: `${CLAUDE_PLUGIN_ROOT}` (install directory, changes on update), `${CLAUDE_PLUGIN_DATA}` (persistent data, survives updates), `${CLAUDE_PROJECT_DIR}` (project root). User-configured values via `${user_config.KEY}`.
- Plugin sources support relative paths, GitHub repos, Git URLs, Git subdirectories, and npm packages. Versions can be pinned with `ref` (branch/tag) or `sha` (exact commit).
- Marketplace structure uses `.claude-plugin/marketplace.json` as the catalog. Eight reserved marketplace names are blocked (e.g., `claude-code-marketplace`, `anthropic-marketplace`).
- Installation scopes: user (default, `~/.claude/settings.json`), project (`.claude/settings.json`), local (`.claude/settings.local.json`, gitignored), managed (read-only, admin-controlled).
- The codex-plugin-cc reference implementation demonstrates six architecture patterns: companion scripts for command execution, command frontmatter for behavior control, thin forwarder subagents, plugin-embedded skills, hook lifecycle management, and hook-to-session data passing via stdin JSON and state files.

## Notable Details
- Source URL: `https://code.claude.com/docs/en/plugins-reference.md`
- Reference implementation: `https://github.com/openai/codex-plugin-cc`
- CLI command for validation: `claude plugin validate .`
- CLI command for marketplace add: `/plugin marketplace add owner/repo`
- Submit plugins to Anthropic marketplace at `https://claude.ai/settings/plugins/submit` or `https://platform.claude.com/plugins/submit`
- Private repo support via `GITHUB_TOKEN`, `GITLAB_TOKEN`, or `BITBUCKET_TOKEN` environment variables
- Command frontmatter can include `disable-model-invocation: true` to skip LLM processing and only execute scripts
- Monitors only run in interactive CLI sessions
- User configuration prompts on first enable via `userConfig` in `plugin.json`
- The codex-plugin-cc companion script manages background task lifecycle including spawn/track PIDs and writing state.json
- Always wrap environment variables in quotes in shell commands: `"${CLAUDE_PLUGIN_ROOT}"`

## See Also
- [[claude-code-docs]] -- Claude Code documentation index
- [[codex-docs]] -- OpenAI Codex documentation index
- [[cursor-docs]] -- Cursor documentation index
- [[opencode-docs]] -- OpenCode documentation index
