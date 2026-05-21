---
name: ai-tool-reference
description: Look up official documentation for AI coding tools — Claude Code, Cursor, OpenAI Codex, OpenCode, or Claude Code plugin building. Routes to the appropriate reference based on which tool you're working with. Use when asking about AI coding tool features, configuration, or APIs.
---

# AI Tool Reference

Routes to the appropriate documentation reference based on which AI coding tool you're working with.

## Decision Matrix

| Your Need | Route To | Documentation Source |
|-----------|----------|---------------------|
| Claude Code features, config, skills, hooks, MCP | `claude-code-reference` | https://code.claude.com/docs/ |
| Claude Code plugin/marketplace building | `claude-code-plugin-builder` | Plugin construction guide |
| Cursor AI editor features, CLI, hooks, MCP | `cursor-reference` | https://cursor.com/docs |
| OpenAI Codex features, config, skills, plugins | `openai-codex-reference` | https://developers.openai.com/codex |
| OpenCode CLI features, config, tools, plugins | `opencode-reference` | https://opencode.ai/docs/ |

## How to Use

1. Identify which AI tool the user is asking about
2. Invoke the appropriate sub-skill directly — it will fetch official docs via WebFetch
3. This orchestrator only routes; it does not duplicate sub-skill content

## Sub-skills

- **claude-code-reference** — Claude Code official docs: 131+ pages covering skills, hooks, MCP, plugins, sub-agents, memory, workflows, permissions, integrations
- **claude-code-plugin-builder** — Claude Code plugin construction: manifest, skills, agents, hooks, MCP/LSP, marketplace, distribution
- **cursor-reference** — Cursor docs: CLI (agent command), hooks, MCP, permissions, rules
- **openai-codex-reference** — Codex docs: app/IDE/CLI/cloud modes, skills, hooks, MCP, plugins, enterprise admin
- **opencode-reference** — OpenCode docs: provider-agnostic (75+ LLMs), JSON config, skills, custom tools, plugins