# Claude Harness - Spec-Driven Development

## Overview
This harness provides a spec-driven development workflow using specialized agents
for each stage of the development process.

## Workflow Chain
Requirements → PRD → Design → Dev-Plan → Testing-Plan → Release-Plan → Doc
     ↓           ↓        ↓          ↓             ↓               ↓      ↓
  [Review]   [Review]  [Review]   [Review]      [Review]       [Review]  (end)

## Available Commands
| Command | Agent | Purpose |
|---------|-------|---------|
| /requirements | Requirements Agent | Create requirements document |
| /prd | PRD Agent | Create product requirements document |
| /design | Design Agent | Create technical design documents |
| /dev-plan | Dev-Plan Agent | Create development plan |
| /testing-plan | Testing-Plan Agent | Create testing plan |
| /release-plan | Release-Plan Agent | Create release plan |
| /review | Review Agent | Review any spec document |
| /doc | Doc Agent | Update living project docs |

## Document Structure
```
docs/
├── init/                    # Project init templates
├── project/                 # Living project docs (doc-agent)
├── review/                  # All review documents
└── specs/                  # Development specs
    ├── requirements/
    ├── prd/
    ├── design/
    ├── dev-plan/
    ├── testing-plan/
    └── release-plan/
```

## Rules
1. Follow spec-driven workflow - do not skip stages
2. All specs must be reviewed before proceeding
3. Use specialized agents - do not mix responsibilities
4. Follow naming conventions exactly

## Agents Configuration
See .claude/agents/ directory for agent definitions.
See .claude/rules/ directory for workflow rules.
