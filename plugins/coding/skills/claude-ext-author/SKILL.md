---
name: claude-ext-author
description: Create or modify Claude Code extensibility files — agents, commands, or skills. Routes to the appropriate authoring sub-skill based on what you want to create. Use when creating agents, commands, or skills for Claude Code.
---

# Claude Extension Author

Routes to the appropriate authoring sub-skill based on what you want to create.

## Decision Matrix

| Your Need | Route To | Artifact Type |
|-----------|----------|---------------|
| Create or modify an agent definition | `write-agent` | `.claude/agents/*.md` — isolated sub-conversations with tool restrictions |
| Create or modify a command | `write-command` | `.claude/commands/*.md` — lightweight single-purpose instructions |
| Create or modify a skill | `write-skill` | `skills/*/SKILL.md` — reusable workflows with support files |

## Choosing the Right Artifact

| Feature | Command | Skill | Agent |
|---------|---------|-------|-------|
| Complexity | Simple instruction | Multi-step workflow | Isolated sub-conversation |
| Support files | No | Yes (references/, scripts/) | No |
| Tool restrictions | No | No | Yes (disallowedTools) |
| Model override | No | No | Yes |
| Typical size | <50 lines | <500 lines | <200 lines |

If a command exceeds 50 lines or needs support files, it should be a skill.

## How to Use

1. Identify which sub-skill matches your need from the decision matrix above
2. Invoke that sub-skill directly — it has its own detailed workflow and quality gates
3. This orchestrator only routes; it does not duplicate sub-skill content

## Sub-skills

- **write-agent** — Create agent `.md` files with frontmatter (model, effort, maxTurns, disallowedTools), role definition, behavior instructions
- **write-command** — Create command `.md` files with argument-hint, $ARGUMENTS support, direct instructions
- **write-skill** — Create skill directories with SKILL.md + support files (references/, scripts/, assets/), 4 body types (discipline, workflow, technique, reference)