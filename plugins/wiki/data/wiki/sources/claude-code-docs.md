---
tags: [ai-tools, cli, coding, claude-code, documentation]
date: 2026-05-22
last_updated: 2026-05-22
source: raw/ai-tools/claude-code.md
status: stable
page_type: source
---

# Claude Code Documentation Index

## Summary
The Claude Code documentation index is a comprehensive catalog of all official documentation pages for Claude Code, Anthropic's CLI-based AI coding agent. The index covers the full product surface from initial setup through advanced automation, spanning core configuration, agent features, memory and context management, workflow automation, UI customization, permissions and security, platform integrations, the Agent SDK, troubleshooting, and observability. The documentation is hosted at `code.claude.com/docs/` with a full machine-readable index at `code.claude.com/docs/llms.txt`.

## Key Points
- Claude Code offers a layered documentation structure: Getting Started, Core Configuration, Agent Features, Memory & Context, Workflow & Automation, UI & Customization, Permissions & Security, Integrations & Platforms, Agent SDK, Troubleshooting, and Observability.
- Agent features include Skills, Hooks (both guide and reference), MCP (Model Context Protocol), Plugins (usage and reference), and Sub-agents -- providing multiple extension mechanisms.
- Memory and context management is a first-class concern with dedicated docs for memory, best practices, common workflows, and context window handling.
- Workflow automation capabilities include Routines, Scheduled tasks, Agent teams, and Worktrees for parallel development.
- The Agent SDK provides programmatic access with dedicated sub-docs for Skills, Hooks, MCP, and Permissions within the SDK context.
- Platform integrations cover Desktop app, VS Code, JetBrains, Web, GitHub Actions, GitLab CI/CD, Slack, and third-party integrations.
- Security documentation spans permission modes, permission configuration, general security, and sandboxing.
- UI customization options include interactive mode, terminal config, keybindings, status line, and output styles.
- Observability tooling covers monitoring usage, costs, and analytics for tracking agent activity and spend.
- Troubleshooting resources include general troubleshooting, config debugging, error reference, and install troubleshooting.

## Notable Details
- Source URL: `https://code.claude.com/docs/`
- Full LLM-readable index: `https://code.claude.com/docs/llms.txt`
- All doc pages follow the pattern `https://code.claude.com/docs/en/<topic>.md`
- Agent SDK docs use a nested path pattern: `https://code.claude.com/docs/en/agent-sdk/<topic>.md`
- The documentation domain is `ai-tools` and media type is `doc-index`
- Dual hooks documentation: a user-facing guide (`hooks-guide.md`) and a reference spec (`hooks.md`)

## See Also
- [[codex-docs]] -- OpenAI Codex documentation index
- [[cursor-docs]] -- Cursor documentation index
- [[opencode-docs]] -- OpenCode documentation index
- [[plugin-builder-docs]] -- Claude Code Plugin Builder documentation
