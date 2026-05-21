# Harness Marketplace Design

## Overview

Transform the claude-harness repository into a Claude Code plugin marketplace (`harness-marketplace`), distributing existing agents, skills, rules, hooks, and commands as independent plugins. Users install only what they need.

## Plugin Inventory

6 plugins, each named by its capability:

| Plugin | Contents | Description |
|--------|----------|-------------|
| **spec-workflow** | agents, rules, hooks, commands, review skills | Spec-driven development workflow with review capabilities |
| **analysis** | analysis skills | Codebase analysis and architecture analysis |
| **coding** | coding skills | Coding, testing, and skill-building |
| **office** | office skills | Office document handling (xlsx, publishing, file upload) |
| **interview** | interview skills | Technical interview preparation |
| **reference** | reference skills | AI coding tool reference documentation |

## Repository Structure

```
harness-marketplace/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── spec-workflow/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/
│   │   ├── rules/
│   │   ├── hooks/
│   │   ├── commands/
│   │   └── skills/
│   │       ├── review/
│   │       ├── create-rule/
│   │       ├── debug-claude-hooks/
│   │       └── superpowers/
│   ├── analysis/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   ├── coding/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   ├── office/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   ├── interview/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   └── reference/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
├── template/                # Retained as-is (not plugin content)
├── superpowers/             # Retained as-is
├── CLAUDE.md
└── README.md
```

## Plugin Details

### spec-workflow

**Manifest**:
```json
{
  "name": "spec-workflow",
  "version": "1.0.0",
  "description": "Spec-driven development workflow: agents, rules, hooks, commands, and review skills for structured software development",
  "author": { "name": "platootalp" },
  "license": "MIT"
}
```

**Agents** (from `claude/agents/`):
- planner-agent.md
- evaluator-agent.md
- requirements-agent.md
- prd-agent.md
- design-agent.md
- dev-plan-agent.md
- testing-plan-agent.md
- release-plan-agent.md
- review-agent.md
- doc-agent.md

**Rules** (from `claude/rules/`):
- document-naming.md
- evaluator-calibration.md
- iterative-refinement.md
- multi-agent-separation.md
- review-process.md
- spec-driven-workflow.md
- sprint-contract.md

**Hooks** (from `claude/hooks/`):
- hooks.json

**Commands** (restore from git history, originally `.claude/commands/`):
- requirements.md
- prd.md
- design.md
- dev-plan.md
- testing-plan.md
- release-plan.md
- review.md
- doc.md

**Skills** (from `claude/skills/review/`):
- review-workflow/
  - design-spec-review/
  - dev-plan-review/

**Skills** (from `claude/skills/harness/`, workflow-related):
- create-rule/
- debug-claude-hooks/
- superpowers/
  - brainstorming/
  - requesting-code-review/
  - subagent-driven-development/
  - systematic-debugging/
  - test-driven-development/
  - writing-skills/

### analysis

**Manifest**:
```json
{
  "name": "analysis",
  "version": "1.0.0",
  "description": "Codebase analysis and architecture analysis skills for deep understanding of software systems",
  "author": { "name": "platootalp" },
  "license": "MIT"
}
```

**Skills** (from `claude/skills/analysis/`):
- codebase-analysis/
  - codebase-to-docs/
  - deep-functional-analysis/
  - source-functional-analysis/
  - system-architecture-analysis/

### coding

**Manifest**:
```json
{
  "name": "coding",
  "version": "1.0.0",
  "description": "Coding, testing, API design, and skill-building skills for software development",
  "author": { "name": "platootalp" },
  "license": "MIT"
}
```

**Skills** (from `claude/skills/coding/`):
- agent-browser/
- api-and-sdk/
  - api-design-principles/
  - claude-api/
- browser-testing/
  - webapp-testing/
- git-workflow/
- next-best-practices/
- skill-authoring/
  - claude-code-plugin-builder/
  - claude-ext-author/
  - server-to-skill-creator/
  - skill-creator/
  - skill-lifecycle/
    - skill-audit/
    - skill-discovery/
    - upload-skill/
  - write-agent/
  - write-command/
  - write-skill/
- testing/
  - python-testing-patterns/
- ui-ux-pro-max/

### office

**Manifest**:
```json
{
  "name": "office",
  "version": "1.0.0",
  "description": "Office document handling: xlsx, HTML publishing, and file upload",
  "author": { "name": "platootalp" },
  "license": "MIT"
}
```

**Skills** (from `claude/skills/office/`):
- document-handling/
  - file-upload-helper/
  - single-html-tac-publish/
  - xlsx/

### interview

**Manifest**:
```json
{
  "name": "interview",
  "version": "1.0.0",
  "description": "Technical interview preparation and project resume skills",
  "author": { "name": "platootalp" },
  "license": "MIT"
}
```

**Skills** (from `claude/skills/interview/`):
- project-resume/

### reference

**Manifest**:
```json
{
  "name": "reference",
  "version": "1.0.0",
  "description": "Reference documentation skills for Claude Code, Cursor, Codex, and other AI coding tools",
  "author": { "name": "platootalp" },
  "license": "MIT"
}
```

**Skills** (from `claude/skills/reference/`):
- ai-tool-reference/
  - claude-code-plugin-builder/
  - claude-code-reference/
  - cursor-reference/
  - openai-codex-reference/
  - opencode-reference/

## Marketplace Configuration

### marketplace.json

```json
{
  "name": "harness-marketplace",
  "description": "Spec-driven development plugin marketplace for Claude Code",
  "owner": { "name": "platootalp" },
  "plugins": [
    {
      "name": "spec-workflow",
      "source": "./plugins/spec-workflow",
      "description": "Spec-driven development workflow: agents, rules, hooks, commands, and review skills"
    },
    {
      "name": "analysis",
      "source": "./plugins/analysis",
      "description": "Codebase analysis and architecture analysis skills"
    },
    {
      "name": "coding",
      "source": "./plugins/coding",
      "description": "Coding, testing, and skill-building skills"
    },
    {
      "name": "office",
      "source": "./plugins/office",
      "description": "Office document handling skills"
    },
    {
      "name": "interview",
      "source": "./plugins/interview",
      "description": "Technical interview preparation skills"
    },
    {
      "name": "reference",
      "source": "./plugins/reference",
      "description": "AI coding tool reference documentation skills"
    }
  ]
}
```

## Installation

Users add the marketplace and install individual plugins:

```bash
# Add marketplace
/plugin marketplace add https://github.com/platootalp/harness-marketplace

# Install individual plugins
/plugin install spec-workflow@harness-marketplace
/plugin install coding@harness-marketplace
/plugin install analysis@harness-marketplace
```

## Version Strategy

Explicit version numbers in each plugin's `plugin.json`. Bump version on each release. Users get updates only when version is bumped.

## Migration Steps

1. Create `plugins/` directory and all 6 sub-plugin directories with `.claude-plugin/plugin.json`
2. Create root `.claude-plugin/marketplace.json`
3. Move `claude/agents/` → `plugins/spec-workflow/agents/`
4. Move `claude/rules/` → `plugins/spec-workflow/rules/`
5. Move `claude/hooks/` → `plugins/spec-workflow/hooks/`
6. Restore commands from git history → `plugins/spec-workflow/commands/`
7. Move `claude/skills/review/` → `plugins/spec-workflow/skills/review/`
8. Move `claude/skills/harness/create-rule/` → `plugins/spec-workflow/skills/create-rule/`
9. Move `claude/skills/harness/debug-claude-hooks/` → `plugins/spec-workflow/skills/debug-claude-hooks/`
10. Move `claude/skills/harness/superpowers/` → `plugins/spec-workflow/skills/superpowers/`
11. Move `claude/skills/analysis/` → `plugins/analysis/skills/` (preserving sub-directory structure)
12. Move `claude/skills/coding/` → `plugins/coding/skills/` (preserving sub-directory structure)
13. Move `claude/skills/office/` → `plugins/office/skills/` (preserving sub-directory structure)
14. Move `claude/skills/interview/` → `plugins/interview/skills/` (preserving sub-directory structure)
15. Move `claude/skills/reference/` → `plugins/reference/skills/` (preserving sub-directory structure)
16. Move `claude/skills/harness/` remaining skills — distribute to appropriate plugins:
    - claude-ext-author/ → coding
    - skill-audit/ → coding
    - skill-discovery/ → coding
    - skill-lifecycle/ → coding
17. Delete old `claude/` directory
18. Update CLAUDE.md to reflect new structure
19. Update README.md with marketplace usage instructions

## Retained Content

- `template/` — project templates, not plugin content
- `superpowers/` — existing specs and plans
- `CLAUDE.md` — updated to reflect marketplace structure
- `LICENSE` — retained

## Dependencies

All plugins are independent. No cross-plugin dependencies. Each plugin works standalone.

If a skill in one plugin references an agent from spec-workflow, the skill description notes "works best with spec-workflow installed" but does not require it.
