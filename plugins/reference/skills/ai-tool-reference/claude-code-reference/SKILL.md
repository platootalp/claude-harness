---
name: claude-code-reference
description: Claude Code 官方文档参考技能。When working with Claude Code features, configuration, hooks, skills, MCP, permissions, settings.json, CLI commands, slash commands, sub-agents, Agent SDK, or any other Claude Code internals — either when users ask OR when the Agent needs to know how something works. Fetch from https://code.claude.com/office/ as the authoritative source instead of relying on training data. Make sure to use this skill whenever the Agent encounters a Claude Code feature it doesn't fully understand, needs to configure settings.json, create hooks/scripts, use MCP servers, work with skills, or needs accurate information about Claude Code commands, permissions, or APIs.
compatibility: WebFetch, Agent
---

# Claude Code Reference Skill

## Core Principle

**Always prefer fetching from official documentation over relying on training data.** When working with Claude Code features, use the official docs at `https://code.claude.com/docs/` as the authoritative source. This applies both when users ask AND when the Agent needs accurate information about how Claude Code works internally.

## When to Use This Skill

**Trigger in all these contexts:**
- User asks about Claude Code features, configuration, or commands
- Agent needs to implement hooks, skills, MCP servers, or plugins
- Agent needs to configure settings.json correctly
- Agent encounters an unfamiliar Claude Code feature or command
- Agent needs to write Claude Code scripts (hooks, slash commands, plugins)
- Agent needs to understand permissions, permission modes, or sandboxing
- Agent needs to use sub-agents, agent teams, or worktrees
- Agent needs to integrate with GitHub Actions, GitLab CI, Slack, or other platforms
- Agent needs to troubleshoot Claude Code issues
- Agent needs accurate CLI reference, environment variables, or tool usage

## Official Documentation Index

The full documentation index is at: `https://code.claude.com/docs/llms.txt`

Key documentation pages (use WebFetch to retrieve):

### Getting Started
- Overview: `/docs/en/overview.md`
- Quickstart: `/docs/en/quickstart.md`
- Setup: `/docs/en/setup.md`
- Authentication: `/docs/en/authentication.md`

### Core Configuration
- Settings: `/docs/en/settings.md`
- Environment variables: `/docs/en/env-vars.md`
- Model configuration: `/docs/en/model-config.md`
- CLI reference: `/docs/en/cli-reference.md`
- Commands: `/docs/en/commands.md`
- Tools reference: `/docs/en/tools-reference.md`

### Agent Features
- Skills: `/docs/en/skills.md`
- Hooks guide: `/docs/en/hooks-guide.md`
- Hooks reference: `/docs/en/hooks.md`
- MCP: `/docs/en/mcp.md`
- Plugins: `/docs/en/plugins.md`
- Plugins reference: `/docs/en/plugins-reference.md`
- Sub-agents: `/docs/en/sub-agents.md`

### Memory & Context
- Memory: `/docs/en/memory.md`
- Best practices: `/docs/en/best-practices.md`
- Common workflows: `/docs/en/common-workflows.md`
- Context window: `/docs/en/context-window.md`

### Workflow & Automation
- Routines: `/docs/en/routines.md`
- Scheduled tasks: `/docs/en/scheduled-tasks.md`
- Agent teams: `/docs/en/agent-teams.md`
- Worktrees: `/docs/en/worktrees.md`

### UI & Customization
- Interactive mode: `/docs/en/interactive-mode.md`
- Terminal config: `/docs/en/terminal-config.md`
- Keybindings: `/docs/en/keybindings.md`
- Status line: `/docs/en/statusline.md`
- Output styles: `/docs/en/output-styles.md`

### Permissions & Security
- Permission modes: `/docs/en/permission-modes.md`
- Configure permissions: `/docs/en/permissions.md`
- Security: `/docs/en/security.md`
- Sandboxing: `/docs/en/sandboxing.md`

### Integrations & Platforms
- Desktop app: `/docs/en/desktop.md`
- VS Code: `/docs/en/vs-code.md`
- JetBrains: `/docs/en/jetbrains.md`
- Web: `/docs/en/claude-code-on-the-web.md`
- GitHub Actions: `/docs/en/github-actions.md`
- GitLab CI/CD: `/docs/en/gitlab-ci-cd.md`
- Slack: `/docs/en/slack.md`
- Third-party integrations: `/docs/en/third-party-integrations.md`

### Agent SDK
- Agent SDK overview: `/docs/en/agent-sdk/overview.md`
- Skills in SDK: `/docs/en/agent-sdk/skills.md`
- Hooks in SDK: `/docs/en/agent-sdk/hooks.md`
- MCP in SDK: `/docs/en/agent-sdk/mcp.md`
- Permissions in SDK: `/docs/en/agent-sdk/permissions.md`

### Troubleshooting
- Troubleshooting: `/docs/en/troubleshooting.md`
- Debug your config: `/docs/en/debug-your-config.md`
- Error reference: `/docs/en/errors.md`
- Troubleshoot install: `/docs/en/troubleshoot-install.md`

### Observability
- Monitoring usage: `/docs/en/monitoring-usage.md`
- Costs: `/docs/en/costs.md`
- Analytics: `/docs/en/analytics.md`

## Workflow

### Step 1: Identify the Topic

Map the question to the most relevant documentation page(s). Use the index above for guidance.

### Step 2: Fetch from Official Docs

Use WebFetch to retrieve the relevant page(s):

```
WebFetch(url="https://code.claude.com/docs/en/[topic].md", prompt="Extract all relevant information about [specific topic]")
```

For unknown topics, fetch the index first:
```
WebFetch(url="https://code.claude.com/docs/llms.txt", prompt="Find pages related to [topic]")
```

### Step 3: Synthesize and Answer

Combine information from official docs with your own knowledge. When citing specific features, configuration options, or command syntax, **always reference the official documentation** as the source.

### Step 4: Provide Actionable Guidance

Don't just quote docs — provide concrete examples, configuration snippets, or step-by-step instructions based on what the official docs say.

## Examples

**User asks about hooks:**
→ Fetch `/docs/en/hooks.md` and `/docs/en/hooks-guide.md`, explain hook types, configuration, and provide examples.

**Agent needs to create a skill:**
→ Fetch `/docs/en/skills.md`, explain skill structure, SKILL.md format, and how to trigger skills.

**Agent needs to configure MCP:**
→ Fetch `/docs/en/mcp.md`, explain MCP server setup, settings.json configuration, and provide examples.

**User asks about permissions:**
→ Fetch `/docs/en/permissions.md` and `/docs/en/permission-modes.md`, explain permission levels and configuration.

**User asks about CLI commands:**
→ Fetch `/docs/en/cli-reference.md`, list relevant commands with flags and examples.

## Important Notes

- The documentation is extensive (131+ pages). You don't need to fetch all pages — only the ones relevant to the question.
- When users ask about "how Claude Code works" or "what can Claude Code do", fetch the overview page.
- For troubleshooting, always check the official error reference and troubleshooting guides first.
- Claude Code documentation is actively maintained — prefer real-time fetch over cached knowledge.
- If a page doesn't exist or can't be fetched, fall back to your training knowledge but clearly note when the information may be outdated.
