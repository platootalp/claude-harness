---
tags: [claude-code, cli, ai-tools]
date: 2026-05-22
sources:
  - raw/ai-tools/claude-code.md
status: stable
---

# Claude Code

## Summary

Claude Code is Anthropic's official CLI for Claude. It supports skills, hooks, MCP, plugins, sub-agents, memory, and the Agent SDK. Official documentation at https://code.claude.com/docs/.

## Key Areas

### Configuration
Settings via `settings.json` (project/user/global), environment variables, model configuration. CLI reference with commands and tools.

### Agent Features
Skills (SKILL.md format), hooks (PreToolUse/PostToolUse/SessionStart/SessionEnd/Stop), MCP servers, plugins, sub-agents.

### Memory & Context
Persistent memory, best practices, common workflows, context window management.

### Workflow & Automation
Routines, scheduled tasks, agent teams, worktrees for parallel work.

### Permissions & Security
Permission modes (default/plan/auto), granular permissions, security hardening, sandboxing.

### Integrations
Desktop app, VS Code, JetBrains, web, GitHub Actions, GitLab CI/CD, Slack.

### Agent SDK
Build custom agents with skills, hooks, MCP, and permissions.

### Troubleshooting
Debug config, error messages, installation issues. Observability via monitoring, costs, analytics.

## See Also

- [Plugin Builder](./plugin-builder.md) — How to build Claude Code plugins
- [Cursor](./cursor.md) — Compare with Cursor's approach
- [OpenAI Codex](./codex.md) — Compare with Codex's approach
