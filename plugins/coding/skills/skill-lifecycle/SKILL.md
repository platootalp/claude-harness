---
name: skill-lifecycle
description: Manage the full lifecycle of Claude Code skills — interactive creation with evals or automated generation from workflow context. Use when creating new skills, improving existing skills, or auto-capturing reusable workflows.
---

# Skill Lifecycle

Routes to the appropriate skill creation sub-skill based on context.

## Decision Matrix

| Your Need | Route To | When |
|-----------|----------|------|
| Interactive skill creation with evaluation and iteration | `skill-creator` | Creating a new skill from scratch, or significantly improving an existing one |
| Auto-generate SKILL.md from a captured workflow | `evolve-skill-writer` | Self-evolution system detected a reusable pattern (auto via Stop hook or manual via /evolve-review) |

## How to Use

1. Identify which sub-skill matches your need from the decision matrix above
2. Invoke that sub-skill directly — it has its own detailed workflow
3. This orchestrator only routes; it does not duplicate sub-skill content

## Sub-skills

- **skill-creator** — Full interactive lifecycle: capture intent → interview → write SKILL.md → create test cases → run evaluations → generate reviewer → read feedback → improve. 8 steps with subagent-based testing.
- **evolve-skill-writer** — Non-interactive auto-generator: receives structured context (decision, workflow_summary, key_steps) and outputs a complete SKILL.md. Strict naming conventions (8 category prefixes), content safety checks, no evals.