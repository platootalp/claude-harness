---
tags: [ai-tools, cli, coding]
date: 2026-05-22
last_updated: 2026-05-22
sources:
  - wiki/sources/claude-code-docs.md
status: stable
page_type: entity
---

# Claude Code

## Summary

Claude Code is Anthropic's official CLI for Claude. It supports skills, hooks, MCP, plugins, sub-agents, memory, and the Agent SDK. Official documentation at https://code.claude.com/docs/.

## Key Areas

### Overview
Claude Code is Anthropic's official CLI for Claude, providing an agentic coding experience that runs directly in the terminal. It can read and write files, execute shell commands, and interact with the codebase autonomously. Beyond the CLI, it is also available as a desktop app, a web application, and IDE extensions for VS Code and JetBrains. The terminal remains the primary interface, with the desktop and web apps offering alternative entry points.

### Configuration
Configuration is managed through `settings.json` files at three levels: project (`.claude/settings.json`), user (`~/.claude/settings.json`), and managed (admin-controlled). Environment variables control API keys, model selection, and runtime behavior. The `/model` command and `model-config` settings allow switching between Claude models. CLI commands and tools are documented in a comprehensive reference. Project-specific instructions are defined in `CLAUDE.md` files placed at the repository root or in subdirectories.

### Agent Features
Claude Code supports a rich extensibility model. Skills are reusable workflows defined in `SKILL.md` files with YAML frontmatter and can include bundled references and scripts. Hooks are event-driven scripts (`hooks.json`) that respond to lifecycle events like `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, and `Stop`. MCP servers enable integration with external tools and data sources. Sub-agents allow dispatching parallel tasks. A plugin system supports distribution via marketplaces. Slash commands provide quick-access workflows.

### Memory & Context
Persistent memory allows Claude Code to retain information across sessions. Best practices guidance covers how to structure project instructions and manage the context window effectively. Common workflow patterns help users get the most out of multi-step tasks. Context window management strategies include compaction and selective context loading to handle large codebases.

### Workflow & Automation
Routines define repeatable sequences of actions. Scheduled tasks enable time-based automation. Agent teams coordinate multiple agents on complex projects. Git worktrees support parallel development by allowing agents to work on different branches simultaneously without conflicts.

### Permissions & Security
Claude Code offers three permission modes: default (interactive approval), plan (read-only with approval for writes), and auto (full autonomy). Granular permissions can be configured at the tool level using allow and deny lists. Security hardening guides cover sandboxing, network restrictions, and safe execution practices. Session-scoped approvals reduce repetitive prompts within a single session.

### Integrations
Claude Code integrates with VS Code and JetBrains as IDE extensions, and is available as a standalone desktop app and web application. CI/CD integration is supported through GitHub Actions and GitLab CI/CD pipelines. A Slack integration enables interaction from team chat. Third-party integrations extend connectivity to additional platforms and services.

### Agent SDK
The Agent SDK allows developers to build custom agents that leverage Claude Code's infrastructure, including skills, hooks, MCP server integration, and the permissions system. It provides programmatic access to create specialized workflows and automate coding tasks at scale.

### Troubleshooting
Common issues include API key misconfiguration, permission prompt frequency, and context window limits. The `--debug` flag enables verbose logging for diagnosis. Dedicated guides cover config debugging, error message reference, and installation troubleshooting. Observability features include usage monitoring, cost tracking, and analytics dashboards.

## See Also

- [Plugin Builder](./plugin-builder.md) — How to build Claude Code plugins
- [Cursor](./cursor.md) — Compare with Cursor's approach
- [OpenAI Codex](./codex.md) — Compare with Codex's approach
