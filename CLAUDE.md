# Harness Marketplace

## Overview

A Claude Code plugin marketplace providing spec-driven development workflow tools. Install only the plugins you need.

## Plugins

| Plugin | Description | Install |
|--------|-------------|---------|
| **spec-workflow** | Agents, rules, hooks, commands, and review skills for spec-driven development | `/plugin install spec-workflow@harness-marketplace` |
| **analysis** | Codebase analysis and architecture analysis skills | `/plugin install analysis@harness-marketplace` |
| **coding** | Coding, testing, API design, and skill-building skills | `/plugin install coding@harness-marketplace` |
| **office** | Office document handling (xlsx, publishing, file upload) | `/plugin install office@harness-marketplace` |
| **interview** | Technical interview preparation skills | `/plugin install interview@harness-marketplace` |
| **reference** | AI coding tool reference documentation | `/plugin install reference@harness-marketplace` |

## Setup

```bash
# Add the marketplace
/plugin marketplace add https://github.com/platootalp/harness-marketplace

# Install plugins
/plugin install spec-workflow@harness-marketplace
/plugin install coding@harness-marketplace
```

## Core Principles

### 1. Multi-Agent Separation
Separate the agent doing work from the agent judging it.

### 2. Three-Agent System
- **Planner**: Expands simple prompts into full product specs
- **Generator**: Works in sprints, implements features against agreed contracts
- **Evaluator**: Tests via appropriate tools, grades against concrete criteria

### 3. Sprint Contracts
Before each work chunk, Generator and Evaluator negotiate what "done" looks like.

### 4. Iterative Refinement
Multiple iteration cycles with feedback flow from Evaluator back to Generator.

### 5. Simplify as Models Improve
Every component encodes assumptions about what the model can't do. Regularly stress-test these assumptions.

## Workflow Chain

```
User → Planner → Sprint Contract → Generator → Evaluator → [Decision]
                                      ↑           ↓
                                      └── feedback ←┘
                                                ↓ (if approved)
                                           Doc Agent
                                                ↓
                                            Release
```

## Review Decisions

| Decision | Score | Next Step |
|----------|-------|-----------|
| Approved | 80-100 | Proceed to next stage |
| Approved with Conditions | 60-79 | Proceed, fix in next version |
| Needs Iteration | 40-59 | Return to Generator for refinement |
| Rejected | <40 | Major rework required |

## Document Structure

```
docs/
├── init/                    # Project init templates
├── project/                 # Living project docs (doc-agent)
├── review/                  # All review documents
│   └── calibration/         # Evaluator calibration examples
├── specs/                   # Development specs
│   ├── requirements/
│   ├── prd/
│   ├── design/
│   ├── dev-plan/
│   ├── testing-plan/
│   ├── release-plan/
│   └── sprint-contracts/    # Sprint contract documents
└── superpowers/             # Superpowers specs and plans
```
