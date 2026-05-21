# Harness Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the claude-harness repository into a Claude Code plugin marketplace with 6 independent plugins.

**Architecture:** Move existing agents/skills/rules/hooks/commands from `claude/` into `plugins/<name>/` directories, each with its own `.claude-plugin/plugin.json`. A root `.claude-plugin/marketplace.json` catalogs all plugins. The old `claude/` directory is deleted after migration.

**Tech Stack:** Claude Code plugin system (marketplace.json, plugin.json), git mv for file migration

---

## File Structure

### New files to create:

| File | Purpose |
|------|---------|
| `.claude-plugin/marketplace.json` | Marketplace catalog listing all 6 plugins |
| `plugins/spec-workflow/.claude-plugin/plugin.json` | spec-workflow plugin manifest |
| `plugins/analysis/.claude-plugin/plugin.json` | analysis plugin manifest |
| `plugins/coding/.claude-plugin/plugin.json` | coding plugin manifest |
| `plugins/office/.claude-plugin/plugin.json` | office plugin manifest |
| `plugins/interview/.claude-plugin/plugin.json` | interview plugin manifest |
| `plugins/reference/.claude-plugin/plugin.json` | reference plugin manifest |
| `plugins/spec-workflow/commands/requirements.md` | Restored from git history |
| `plugins/spec-workflow/commands/prd.md` | Restored from git history |
| `plugins/spec-workflow/commands/design.md` | Restored from git history |
| `plugins/spec-workflow/commands/dev-plan.md` | Restored from git history |
| `plugins/spec-workflow/commands/testing-plan.md` | Restored from git history |
| `plugins/spec-workflow/commands/release-plan.md` | Restored from git history |
| `plugins/spec-workflow/commands/review.md` | Restored from git history |
| `plugins/spec-workflow/commands/doc.md` | Restored from git history |

### Files to move (preserving directory structure):

| Source | Destination | Plugin |
|--------|-------------|--------|
| `claude/agents/` | `plugins/spec-workflow/agents/` | spec-workflow |
| `claude/rules/` | `plugins/spec-workflow/rules/` | spec-workflow |
| `claude/hooks/` | `plugins/spec-workflow/hooks/` | spec-workflow |
| `claude/skills/review/` | `plugins/spec-workflow/skills/review/` | spec-workflow |
| `claude/skills/harness/create-rule/` | `plugins/spec-workflow/skills/create-rule/` | spec-workflow |
| `claude/skills/harness/debug-claude-hooks/` | `plugins/spec-workflow/skills/debug-claude-hooks/` | spec-workflow |
| `claude/skills/harness/superpowers/` | `plugins/spec-workflow/skills/superpowers/` | spec-workflow |
| `claude/skills/analysis/` | `plugins/analysis/skills/` | analysis |
| `claude/skills/coding/` | `plugins/coding/skills/` | coding |
| `claude/skills/harness/claude-ext-author/` | `plugins/coding/skills/claude-ext-author/` | coding |
| `claude/skills/harness/skill-audit/` | `plugins/coding/skills/skill-audit/` | coding |
| `claude/skills/harness/skill-discovery/` | `plugins/coding/skills/skill-discovery/` | coding |
| `claude/skills/harness/skill-lifecycle/` | `plugins/coding/skills/skill-lifecycle/` | coding |
| `claude/skills/office/` | `plugins/office/skills/` | office |
| `claude/skills/interview/` | `plugins/interview/skills/` | interview |
| `claude/skills/reference/` | `plugins/reference/skills/` | reference |

### Files to modify:

| File | Change |
|------|--------|
| `CLAUDE.md` | Update to reflect marketplace structure |
| `README.md` | Add marketplace usage instructions |

### Directories to delete:

| Directory | Reason |
|-----------|--------|
| `claude/` | All content migrated to plugins |

---

### Task 1: Create directory structure and marketplace.json

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `plugins/spec-workflow/.claude-plugin/plugin.json`
- Create: `plugins/analysis/.claude-plugin/plugin.json`
- Create: `plugins/coding/.claude-plugin/plugin.json`
- Create: `plugins/office/.claude-plugin/plugin.json`
- Create: `plugins/interview/.claude-plugin/plugin.json`
- Create: `plugins/reference/.claude-plugin/plugin.json`

- [ ] **Step 1: Create all plugin directories**

```bash
mkdir -p plugins/spec-workflow/.claude-plugin
mkdir -p plugins/spec-workflow/agents
mkdir -p plugins/spec-workflow/rules
mkdir -p plugins/spec-workflow/hooks
mkdir -p plugins/spec-workflow/commands
mkdir -p plugins/spec-workflow/skills
mkdir -p plugins/analysis/.claude-plugin
mkdir -p plugins/analysis/skills
mkdir -p plugins/coding/.claude-plugin
mkdir -p plugins/coding/skills
mkdir -p plugins/office/.claude-plugin
mkdir -p plugins/office/skills
mkdir -p plugins/interview/.claude-plugin
mkdir -p plugins/interview/skills
mkdir -p plugins/reference/.claude-plugin
mkdir -p plugins/reference/skills
mkdir -p .claude-plugin
```

- [ ] **Step 2: Create marketplace.json**

Write `.claude-plugin/marketplace.json`:

```json
{
  "name": "harness-marketplace",
  "description": "Spec-driven development plugin marketplace for Claude Code",
  "owner": {
    "name": "platootalp"
  },
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

- [ ] **Step 3: Create spec-workflow plugin.json**

Write `plugins/spec-workflow/.claude-plugin/plugin.json`:

```json
{
  "name": "spec-workflow",
  "version": "1.0.0",
  "description": "Spec-driven development workflow: agents, rules, hooks, commands, and review skills for structured software development",
  "author": {
    "name": "platootalp"
  },
  "license": "MIT"
}
```

- [ ] **Step 4: Create analysis plugin.json**

Write `plugins/analysis/.claude-plugin/plugin.json`:

```json
{
  "name": "analysis",
  "version": "1.0.0",
  "description": "Codebase analysis and architecture analysis skills for deep understanding of software systems",
  "author": {
    "name": "platootalp"
  },
  "license": "MIT"
}
```

- [ ] **Step 5: Create coding plugin.json**

Write `plugins/coding/.claude-plugin/plugin.json`:

```json
{
  "name": "coding",
  "version": "1.0.0",
  "description": "Coding, testing, API design, and skill-building skills for software development",
  "author": {
    "name": "platootalp"
  },
  "license": "MIT"
}
```

- [ ] **Step 6: Create office plugin.json**

Write `plugins/office/.claude-plugin/plugin.json`:

```json
{
  "name": "office",
  "version": "1.0.0",
  "description": "Office document handling: xlsx, HTML publishing, and file upload",
  "author": {
    "name": "platootalp"
  },
  "license": "MIT"
}
```

- [ ] **Step 7: Create interview plugin.json**

Write `plugins/interview/.claude-plugin/plugin.json`:

```json
{
  "name": "interview",
  "version": "1.0.0",
  "description": "Technical interview preparation and project resume skills",
  "author": {
    "name": "platootalp"
  },
  "license": "MIT"
}
```

- [ ] **Step 8: Create reference plugin.json**

Write `plugins/reference/.claude-plugin/plugin.json`:

```json
{
  "name": "reference",
  "version": "1.0.0",
  "description": "Reference documentation skills for Claude Code, Cursor, Codex, and other AI coding tools",
  "author": {
    "name": "platootalp"
  },
  "license": "MIT"
}
```

- [ ] **Step 9: Commit directory structure and manifests**

```bash
git add .claude-plugin/ plugins/
git commit -m "feat: create plugin marketplace structure with 6 plugin manifests"
```

---

### Task 2: Migrate spec-workflow content (agents, rules, hooks)

**Files:**
- Move: `claude/agents/` → `plugins/spec-workflow/agents/`
- Move: `claude/rules/` → `plugins/spec-workflow/rules/`
- Move: `claude/hooks/` → `plugins/spec-workflow/hooks/`

- [ ] **Step 1: Move agents**

```bash
git mv claude/agents/planner-agent.md plugins/spec-workflow/agents/planner-agent.md
git mv claude/agents/evaluator-agent.md plugins/spec-workflow/agents/evaluator-agent.md
git mv claude/agents/requirements-agent.md plugins/spec-workflow/agents/requirements-agent.md
git mv claude/agents/prd-agent.md plugins/spec-workflow/agents/prd-agent.md
git mv claude/agents/design-agent.md plugins/spec-workflow/agents/design-agent.md
git mv claude/agents/dev-plan-agent.md plugins/spec-workflow/agents/dev-plan-agent.md
git mv claude/agents/testing-plan-agent.md plugins/spec-workflow/agents/testing-plan-agent.md
git mv claude/agents/release-plan-agent.md plugins/spec-workflow/agents/release-plan-agent.md
git mv claude/agents/review-agent.md plugins/spec-workflow/agents/review-agent.md
git mv claude/agents/doc-agent.md plugins/spec-workflow/agents/doc-agent.md
```

- [ ] **Step 2: Move rules**

```bash
git mv claude/rules/document-naming.md plugins/spec-workflow/rules/document-naming.md
git mv claude/rules/evaluator-calibration.md plugins/spec-workflow/rules/evaluator-calibration.md
git mv claude/rules/iterative-refinement.md plugins/spec-workflow/rules/iterative-refinement.md
git mv claude/rules/multi-agent-separation.md plugins/spec-workflow/rules/multi-agent-separation.md
git mv claude/rules/review-process.md plugins/spec-workflow/rules/review-process.md
git mv claude/rules/spec-driven-workflow.md plugins/spec-workflow/rules/spec-driven-workflow.md
git mv claude/rules/sprint-contract.md plugins/spec-workflow/rules/sprint-contract.md
```

- [ ] **Step 3: Move hooks**

```bash
git mv claude/hooks/hooks.json plugins/spec-workflow/hooks/hooks.json
```

- [ ] **Step 4: Verify files moved correctly**

```bash
ls plugins/spec-workflow/agents/
ls plugins/spec-workflow/rules/
ls plugins/spec-workflow/hooks/
```

Expected: 10 agent files, 7 rule files, 1 hooks.json

- [ ] **Step 5: Commit**

```bash
git add plugins/spec-workflow/agents/ plugins/spec-workflow/rules/ plugins/spec-workflow/hooks/
git commit -m "feat: migrate agents, rules, and hooks to spec-workflow plugin"
```

---

### Task 3: Restore commands from git history

**Files:**
- Create: `plugins/spec-workflow/commands/requirements.md`
- Create: `plugins/spec-workflow/commands/prd.md`
- Create: `plugins/spec-workflow/commands/design.md`
- Create: `plugins/spec-workflow/commands/dev-plan.md`
- Create: `plugins/spec-workflow/commands/testing-plan.md`
- Create: `plugins/spec-workflow/commands/release-plan.md`
- Create: `plugins/spec-workflow/commands/review.md`
- Create: `plugins/spec-workflow/commands/doc.md`

- [ ] **Step 1: Restore all command files from git history**

```bash
for cmd in requirements prd design dev-plan testing-plan release-plan review doc; do
  git show 135389d:.claude/commands/${cmd}.md > plugins/spec-workflow/commands/${cmd}.md
done
```

- [ ] **Step 2: Verify commands restored**

```bash
ls plugins/spec-workflow/commands/
```

Expected: 8 .md files

- [ ] **Step 3: Commit**

```bash
git add plugins/spec-workflow/commands/
git commit -m "feat: restore workflow commands from git history into spec-workflow plugin"
```

---

### Task 4: Migrate spec-workflow skills (review, create-rule, debug-claude-hooks, superpowers)

**Files:**
- Move: `claude/skills/review/` → `plugins/spec-workflow/skills/review/`
- Move: `claude/skills/harness/create-rule/` → `plugins/spec-workflow/skills/create-rule/`
- Move: `claude/skills/harness/debug-claude-hooks/` → `plugins/spec-workflow/skills/debug-claude-hooks/`
- Move: `claude/skills/harness/superpowers/` → `plugins/spec-workflow/skills/superpowers/`

- [ ] **Step 1: Move review skills**

```bash
git mv claude/skills/review/review-workflow plugins/spec-workflow/skills/review-workflow
```

- [ ] **Step 2: Move create-rule skill**

```bash
git mv claude/skills/harness/create-rule plugins/spec-workflow/skills/create-rule
```

- [ ] **Step 3: Move debug-claude-hooks skill**

```bash
git mv claude/skills/harness/debug-claude-hooks plugins/spec-workflow/skills/debug-claude-hooks
```

- [ ] **Step 4: Move superpowers skills**

```bash
git mv claude/skills/harness/superpowers plugins/spec-workflow/skills/superpowers
```

- [ ] **Step 5: Verify spec-workflow skills**

```bash
ls plugins/spec-workflow/skills/
```

Expected: review-workflow, create-rule, debug-claude-hooks, superpowers

- [ ] **Step 6: Commit**

```bash
git add plugins/spec-workflow/skills/
git commit -m "feat: migrate review, create-rule, debug-claude-hooks, superpowers skills to spec-workflow"
```

---

### Task 5: Migrate analysis plugin skills

**Files:**
- Move: `claude/skills/analysis/` → `plugins/analysis/skills/`

- [ ] **Step 1: Move analysis skills**

```bash
git mv claude/skills/analysis/codebase-analysis plugins/analysis/skills/codebase-analysis
```

- [ ] **Step 2: Verify analysis skills**

```bash
find plugins/analysis/skills -name 'SKILL.md'
```

Expected: 5 SKILL.md files (codebase-analysis, codebase-to-docs, deep-functional-analysis, source-functional-analysis, system-architecture-analysis)

- [ ] **Step 3: Commit**

```bash
git add plugins/analysis/skills/
git commit -m "feat: migrate analysis skills to analysis plugin"
```

---

### Task 6: Migrate coding plugin skills

**Files:**
- Move: `claude/skills/coding/` → `plugins/coding/skills/`
- Move: `claude/skills/harness/claude-ext-author/` → `plugins/coding/skills/claude-ext-author/`
- Move: `claude/skills/harness/skill-audit/` → `plugins/coding/skills/skill-audit/`
- Move: `claude/skills/harness/skill-discovery/` → `plugins/coding/skills/skill-discovery/`
- Move: `claude/skills/harness/skill-lifecycle/` → `plugins/coding/skills/skill-lifecycle/`

- [ ] **Step 1: Move coding skills**

```bash
git mv claude/skills/coding/agent-browser plugins/coding/skills/agent-browser
git mv claude/skills/coding/api-and-sdk plugins/coding/skills/api-and-sdk
git mv claude/skills/coding/browser-testing plugins/coding/skills/browser-testing
git mv claude/skills/coding/git-workflow plugins/coding/skills/git-workflow
git mv claude/skills/coding/next-best-practices plugins/coding/skills/next-best-practices
git mv claude/skills/coding/testing-patterns plugins/coding/skills/testing-patterns
git mv claude/skills/coding/ui-ux-pro-max plugins/coding/skills/ui-ux-pro-max
```

- [ ] **Step 2: Move harness skill-authoring skills to coding**

```bash
git mv claude/skills/harness/claude-ext-author plugins/coding/skills/claude-ext-author
git mv claude/skills/harness/skill-audit plugins/coding/skills/skill-audit
git mv claude/skills/harness/skill-discovery plugins/coding/skills/skill-discovery
git mv claude/skills/harness/skill-lifecycle plugins/coding/skills/skill-lifecycle
```

- [ ] **Step 3: Verify coding skills**

```bash
ls plugins/coding/skills/
```

Expected: agent-browser, api-and-sdk, browser-testing, claude-ext-author, git-workflow, next-best-practices, skill-audit, skill-discovery, skill-lifecycle, testing-patterns, ui-ux-pro-max

- [ ] **Step 4: Commit**

```bash
git add plugins/coding/skills/
git commit -m "feat: migrate coding and skill-authoring skills to coding plugin"
```

---

### Task 7: Migrate office, interview, reference plugin skills

**Files:**
- Move: `claude/skills/office/` → `plugins/office/skills/`
- Move: `claude/skills/interview/` → `plugins/interview/skills/`
- Move: `claude/skills/reference/` → `plugins/reference/skills/`

- [ ] **Step 1: Move office skills**

```bash
git mv claude/skills/office/document-handling plugins/office/skills/document-handling
```

- [ ] **Step 2: Move interview skills**

```bash
git mv claude/skills/interview/project-resume plugins/interview/skills/project-resume
```

- [ ] **Step 3: Move reference skills**

```bash
git mv claude/skills/reference/ai-tool-reference plugins/reference/skills/ai-tool-reference
```

- [ ] **Step 4: Verify all three plugins**

```bash
find plugins/office/skills -name 'SKILL.md'
find plugins/interview/skills -name 'SKILL.md'
find plugins/reference/skills -name 'SKILL.md'
```

Expected:
- office: document-handling, docx, pdf, pptx, xlsx (5 SKILL.md)
- interview: project-resume (1 SKILL.md)
- reference: ai-tool-reference, claude-code-plugin-builder, claude-code-reference, cursor-reference, openai-codex-reference, opencode-reference (6 SKILL.md)

- [ ] **Step 5: Commit**

```bash
git add plugins/office/ plugins/interview/ plugins/reference/
git commit -m "feat: migrate office, interview, and reference skills to their plugins"
```

---

### Task 8: Clean up old claude/ directory

**Files:**
- Delete: `claude/` directory (all content should now be migrated)

- [ ] **Step 1: Verify all content has been migrated**

```bash
# Check that claude/ only has empty directories left
find claude/ -type f
```

Expected: No files remaining (or only empty directory structure)

- [ ] **Step 2: Remove old claude/ directory**

```bash
git rm -r claude/
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "refactor: remove old claude/ directory after migration to plugins"
```

---

### Task 9: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Rewrite CLAUDE.md to reflect marketplace structure**

Replace the entire content of `CLAUDE.md` with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md to reflect marketplace structure"
```

---

### Task 10: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite README.md with marketplace usage instructions**

Replace the entire content of `README.md` with:

```markdown
# Harness Marketplace

A Claude Code plugin marketplace for spec-driven development workflows.

## Quick Start

```bash
# Add the marketplace
/plugin marketplace add https://github.com/platootalp/harness-marketplace

# Install the core workflow plugin
/plugin install spec-workflow@harness-marketplace

# Install additional plugins as needed
/plugin install coding@harness-marketplace
/plugin install analysis@harness-marketplace
```

## Available Plugins

### spec-workflow
Spec-driven development workflow with agents, rules, hooks, commands, and review skills.

Includes 10 agents (planner, evaluator, requirements, PRD, design, dev-plan, testing-plan, release-plan, review, doc), 7 rules, hooks, 8 commands, and workflow skills (review, create-rule, debug-claude-hooks, superpowers).

### analysis
Codebase analysis and architecture analysis skills for deep understanding of software systems.

### coding
Coding, testing, API design, and skill-building skills including agent-browser, API design, browser testing, git workflow, Next.js best practices, testing patterns, UI/UX, and skill authoring tools.

### office
Office document handling: xlsx, HTML publishing, and file upload.

### interview
Technical interview preparation and project resume skills.

### reference
Reference documentation skills for Claude Code, Cursor, Codex, OpenCode, and other AI coding tools.

## Development

### Testing a plugin locally

```bash
claude --plugin-dir ./plugins/spec-workflow
```

### Validating the marketplace

```bash
claude plugin validate .
```

### Adding a new plugin

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`
2. Add skills to `plugins/<name>/skills/`
3. Register in `.claude-plugin/marketplace.json`
4. Validate: `claude plugin validate .`

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README with marketplace usage instructions"
```

---

### Task 11: Validate the marketplace

- [ ] **Step 1: Validate marketplace structure**

```bash
claude plugin validate .
```

Expected: No validation errors

- [ ] **Step 2: Test loading a plugin locally**

```bash
claude --plugin-dir ./plugins/spec-workflow
```

Verify that agents, skills, rules, and hooks load correctly.

- [ ] **Step 3: Fix any validation issues found**

Address any errors from the validation command. Common issues:
- Missing SKILL.md frontmatter `description` field
- Invalid JSON in plugin.json or marketplace.json
- Skills inside `.claude-plugin/` instead of plugin root

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "fix: resolve marketplace validation issues"
```
