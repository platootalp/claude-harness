---
name: superpowers
description: Development workflow orchestrator that routes to the right superpower based on your current phase — brainstorming, debugging, TDD, code review, or parallel implementation. Use before starting any non-trivial development work.
---

# Superpowers

Routes to the right development workflow skill based on your current phase.

## Decision Matrix

| Your Need | Route To | When |
|-----------|----------|------|
| Creative work / feature design | `brainstorming` | Before any creative work — creating features, building components, adding functionality |
| Bug / test failure | `systematic-debugging` | When debugging bugs, test failures, or unexpected behavior |
| Writing SKILL.md files | `writing-skills` | When creating or improving Claude Code skills |
| TDD workflow | `test-driven-development` | When implementing features with test-driven development |
| Code review request | `requesting-code-review` | When requesting a code review with proper context |
| Parallel implementation | `subagent-driven-development` | When implementing independent tasks from a plan in parallel |

## How to Use

1. Identify which superpower matches your current need from the decision matrix above
2. Invoke that sub-skill directly — it has its own detailed workflow
3. This orchestrator only routes; it does not duplicate sub-skill content

## Available Superpowers

- **brainstorming** — Collaborative design: explore intent → ask questions → propose approaches → validate design → write plan
- **systematic-debugging** — Structured debugging: root-cause tracing, defense-in-depth, condition-based waiting, test pressure patterns
- **writing-skills** — Skill authoring: Anthropic best practices, graphviz conventions, persuasion principles, testing with subagents
- **test-driven-development** — TDD workflow with anti-pattern reference
- **requesting-code-review** — Code review with code-reviewer.md reference
- **subagent-driven-development** — Parallel implementation with implementer, spec-reviewer, and code-quality-reviewer prompts