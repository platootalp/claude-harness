---
tags: [plugins, marketplace, claude-code, ai-tools]
date: 2026-05-22
sources:
  - raw/ai-tools/plugin-builder.md
status: stable
---

# Plugin Builder

## Summary

Guide for building Claude Code plugins and marketplaces. Covers the full lifecycle from structure to distribution, with a reference implementation analysis of the openai/codex-plugin-cc production plugin.

## Key Areas

### Plugin Structure
`.claude-plugin/plugin.json` manifest (required). Skills, agents, hooks, MCP/LSP servers, monitors at plugin root.

### Manifest
Required: name, version, description, author, license. Optional: repository, homepage, keywords, environment, userConfig.

### Skills
SKILL.md with frontmatter, `$ARGUMENTS` placeholder, bundled references/ and scripts/.

### Agents
Markdown with frontmatter: model, effort, maxTurns, tools, disallowedTools, skills, memory, background, isolation.

### Hooks
hooks.json with types (command, http, mcp_tool, prompt, agent) and events (SessionStart, SessionEnd, Stop, PreToolUse, PostToolUse, Notification).

### Testing & Validation
`claude --plugin-dir`, `/reload-plugins`, `claude plugin validate`.

### Marketplace
marketplace.json with source types: relative path, GitHub, Git URL, Git subdirectory, npm.

### Distribution
GitHub hosting, private repos, team marketplaces, Anthropic marketplace submission.

### Common Pitfalls
Components inside .claude-plugin/, absolute paths, referencing outside plugin dir, missing CLAUDE_PLUGIN_ROOT in hooks/MCP, version not bumped, duplicate version field, relative paths in URL-based marketplaces.

### Reference Implementation (codex-plugin-cc)
Companion script design, command frontmatter controls, thin forwarder subagent, plugin-embedded skills, hook lifecycle with stop-time gate, hook-to-session data passing.

## See Also

- [Claude Code](./claude-code.md) — The platform plugins run on
