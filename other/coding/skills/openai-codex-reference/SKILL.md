---
name: openai-codex-reference
description: OpenAI Codex 官方文档参考技能。When working with OpenAI Codex features, configuration, hooks, skills, MCP, AGENTS.md, CLI, plugins, subagents, sandboxing, or any other Codex internals — either when users ask OR when the Agent needs to know how something works. Fetch from https://developers.openai.com/codex as the authoritative source instead of relying on training data. Make sure to use this skill whenever the Agent encounters a Codex feature it doesn't fully understand, needs to configure Codex settings, create hooks/scripts, use MCP servers, work with skills, or needs accurate information about Codex commands, permissions, or APIs.
compatibility: WebFetch, Agent
---

# OpenAI Codex Reference Skill

## Core Principle

**Always prefer fetching from official documentation over relying on training data.** When working with Codex features, use the official docs at `https://developers.openai.com/codex` as the authoritative source. This applies both when users ask AND when the Agent needs accurate information about how Codex works internally.

## When to Use This Skill

**Trigger in all these contexts:**
- User asks about Codex features, configuration, or commands
- Agent needs to implement hooks, skills, MCP servers, or plugins for Codex
- Agent needs to configure Codex settings (config files, rules, AGENTS.md)
- Agent encounters an unfamiliar Codex feature or command
- Agent needs to write Codex scripts (hooks, slash commands)
- Agent needs to understand sandboxing, subagents, or workflows
- Agent needs to integrate with GitHub, Slack, Linear, or other platforms
- Agent needs to use Codex CLI, IDE extension, or cloud features
- Agent needs to troubleshoot Codex issues
- Agent needs accurate API reference, SDK usage, or configuration syntax

## Official Documentation Index

Base URL: `https://developers.openai.com/codex`

### Getting Started
- Overview: `/codex`
- Quickstart: `/codex/quickstart`
- Use cases: `/codex/use-cases`
- Migration guide: `/codex/migrate`
- Pricing: `/codex/pricing`

### Concepts
- Prompting: `/codex/prompting`
- Customization: `/codex/concepts/customization`
- Memories: `/codex/concepts/memories`
- Chronicle: `/codex/concepts/memories/chronicle`
- Sandboxing: `/codex/concepts/sandboxing`
- Auto-review: `/codex/concepts/sandboxing/auto-review`
- Subagents: `/codex/concepts/subagents`
- Workflows: `/codex/workflows`
- Models: `/codex/models`
- Cyber Safety: `/codex/concepts/cyber-safety`

### Using Codex - App
- App overview: `/codex/app`
- App features: `/codex/app/features`
- App settings: `/codex/app/settings`
- App review: `/codex/app/review`
- App automations: `/codex/app/automations`
- Worktrees: `/codex/app/worktrees`
- Local environments: `/codex/app/local-environments`
- Browser: `/codex/app/browser`
- Chrome extension: `/codex/app/chrome-extension`
- Computer use: `/codex/app/computer-use`
- Commands: `/codex/app/commands`
- Windows: `/codex/app/windows`
- Troubleshooting: `/codex/app/troubleshooting`

### Using Codex - IDE Extension
- IDE overview: `/codex/ide`
- IDE features: `/codex/ide/features`
- IDE settings: `/codex/ide/settings`
- IDE commands: `/codex/ide/commands`
- Slash commands: `/codex/ide/slash-commands`

### Using Codex - CLI
- CLI overview: `/codex/cli`
- CLI features: `/codex/cli/features`
- CLI reference: `/codex/cli/reference`
- Slash commands: `/codex/cli/slash-commands`

### Using Codex - Cloud
- Cloud overview: `/codex/cloud`
- Environments: `/codex/cloud/environments`
- Internet access: `/codex/cloud/internet-access`

### Integrations
- GitHub: `/codex/integrations/github`
- Slack: `/codex/integrations/slack`
- Linear: `/codex/integrations/linear`

### Security
- Security overview: `/codex/security`
- Security setup: `/codex/security/setup`
- Threat model: `/codex/security/threat-model`
- Security FAQ: `/codex/security/faq`

### Configuration
- Basic config: `/codex/config-basic`
- Advanced config: `/codex/config-advanced`
- Config reference: `/codex/config-reference`
- Config samples: `/codex/config-sample`
- Speed settings: `/codex/speed`
- Rules: `/codex/rules`
- Hooks: `/codex/hooks`
- AGENTS.md: `/codex/guides/agents-md`
- MCP: `/codex/mcp`
- Plugins: `/codex/plugins`
- Build plugins: `/codex/plugins/build`
- Skills: `/codex/skills`
- Subagents: `/codex/subagents`

### Administration
- Authentication: `/codex/auth`
- Agent approvals & security: `/codex/agent-approvals-security`
- Remote connections: `/codex/remote-connections`
- Enterprise admin: `/codex/enterprise/admin-setup`
- Enterprise governance: `/codex/enterprise/governance`
- Managed configuration: `/codex/enterprise/managed-configuration`
- Windows: `/codex/windows`

### Automation
- Non-interactive mode: `/codex/noninteractive`
- Codex SDK: `/codex/sdk`
- App Server: `/codex/app-server`
- Agents SDK guide: `/codex/guides/agents-sdk`
- GitHub Action: `/codex/github-action`

### Learn
- Best practices: `/codex/learn/best-practices`
- Videos: `/codex/videos`
- Build AI-native team: `/codex/guides/build-ai-native-engineering-team`

### Releases
- Changelog: `/codex/changelog`
- Feature maturity: `/codex/feature-maturity`
- Open source: `/codex/open-source`

## Workflow

### Step 1: Identify the Topic

Map the question to the most relevant documentation page(s). Use the index above for guidance.

### Step 2: Fetch from Official Docs

Use WebFetch to retrieve the relevant page(s):

```
WebFetch(url="https://developers.openai.com/codex/[topic]", prompt="Extract all relevant information about [specific topic]")
```

For unknown topics, start with the main Codex page:
```
WebFetch(url="https://developers.openai.com/codex", prompt="Find documentation related to [topic]")
```

### Step 3: Synthesize and Answer

Combine information from official docs with your own knowledge. When citing specific features, configuration options, or command syntax, **always reference the official documentation** as the source.

### Step 4: Provide Actionable Guidance

Don't just quote docs — provide concrete examples, configuration snippets, or step-by-step instructions based on what the official docs say.

## Examples

**User asks about hooks:**
→ Fetch `/codex/hooks`, explain hook types, configuration, and provide examples.

**Agent needs to create a skill:**
→ Fetch `/codex/skills`, explain skill structure, SKILL.md format, and how to trigger skills.

**Agent needs to configure MCP:**
→ Fetch `/codex/mcp`, explain MCP server setup, configuration, and provide examples.

**User asks about AGENTS.md:**
→ Fetch `/codex/guides/agents-md`, explain the purpose and format of AGENTS.md files.

**User asks about CLI commands:**
→ Fetch `/codex/cli/reference`, list relevant commands with flags and examples.

**User asks about sandboxing:**
→ Fetch `/codex/concepts/sandboxing`, explain how Codex sandboxing works and its security implications.

## Important Notes

- The documentation is comprehensive. You don't need to fetch all pages — only the ones relevant to the question.
- When users ask about "how Codex works" or "what can Codex do", start with the overview page `/codex`.
- Codex has many similarities to Claude Code but also differences — always fetch the specific Codex documentation rather than assuming features work the same way.
- Codex documentation is actively maintained — prefer real-time fetch over cached knowledge.
- If a page doesn't exist or can't be fetched, fall back to your training knowledge but clearly note when the information may be outdated.
