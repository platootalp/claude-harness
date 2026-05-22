---
tags: [ai-tools, cli, coding]
date: 2026-05-22
last_updated: 2026-05-22
sources:
  - wiki/sources/codex-docs.md
status: stable
page_type: entity
---

# OpenAI Codex

## Summary

OpenAI Codex is a coding agent available as app, IDE extension, CLI, and cloud environment. Supports skills, hooks, MCP, plugins, subagents, and sandboxing. Official documentation at https://developers.openai.com/codex.

## Key Areas

### Overview
OpenAI Codex is a coding agent developed by OpenAI, accessible through multiple interfaces: a desktop app, a VS Code IDE extension, a CLI for terminal use, and a cloud environment for remote execution. It supports skills, hooks, MCP servers, plugins, subagents, and sandboxed execution. The tool is designed to handle autonomous coding tasks across local and remote environments.

### Modes
Codex offers four primary interfaces. The App mode provides a desktop application with features like worktrees, local environments, browser integration, a Chrome extension, computer use capabilities, and custom commands. The IDE Extension mode integrates into VS Code with dedicated features, settings, commands, and slash commands. The CLI mode provides terminal access with its own feature set, reference documentation, and slash commands. The Cloud mode runs tasks in remote environments with configurable internet access.

### Concepts
Core concepts include prompting strategies for effective interaction, customization of agent behavior, persistent memories for cross-session retention, a chronicle feature for tracking history, sandboxing for safe code execution, auto-review for automated code review, subagents for task delegation, workflow orchestration, model selection, and cyber safety considerations.

### Configuration
Configuration spans basic and advanced settings with a full config reference and sample configurations. Speed settings allow performance tuning. Rules define behavioral constraints. Hooks enable event-driven automation. `AGENTS.md` files provide project-level instructions. MCP servers extend tool capabilities. Plugins and skills add reusable workflows and custom functionality. Subagents can be configured for delegated tasks.

### Security
The security model is built around a documented threat model, setup procedures, and a security FAQ. Sandboxing isolates code execution to prevent unauthorized system access. Agent approvals and security settings provide governance over autonomous actions. Enterprise features include admin setup, governance policies, and managed configuration for organizational control.

### Administration
Administrative features cover authentication, agent approval policies, and remote connection management. Enterprise administration includes governance controls and managed configuration. Windows support is available with specific considerations.

### Automation
Non-interactive mode enables headless execution for CI/CD pipelines. The Codex SDK provides programmatic access. An App Server supports running Codex as a service. The Agents SDK guide covers building custom agents. A GitHub Action integrates Codex directly into CI/CD workflows.

### Integrations
Codex integrates with GitHub for repository operations, Slack for team notifications and interactions, and Linear for issue tracking. Each integration provides bidirectional workflows between Codex and the external service.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's approach
- [Cursor](./cursor.md) — Compare with Cursor's approach
- [OpenCode](./opencode.md) — Compare with OpenCode's approach
