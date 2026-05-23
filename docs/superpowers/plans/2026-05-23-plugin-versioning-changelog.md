# Plugin Installation, Versioning, and Changelog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add plugin install instructions, versioning conventions, and a root-level CHANGELOG.md to the repository.

**Architecture:** Documentation-only changes to CLAUDE.md and a new CHANGELOG.md file. No code changes. Three edits to CLAUDE.md (new section + expanded conventions) and one new file.

**Tech Stack:** Markdown only.

---

### Task 1: Add "Installing Plugins" section to CLAUDE.md

**Files:**
- Modify: `CLAUDE.md:42` (insert before `## Development Commands`)

- [ ] **Step 1: Insert the Installing Plugins section**

Insert the following block before the `## Development Commands` line (currently line 42):

```markdown
## Installing Plugins

First, add the marketplace:
```
/plugin marketplace add platootalp/claude-harness
```

Then install individual plugins:
```
/plugin install spec-workflow
/plugin install analysis
/plugin install coding
/plugin install office
/plugin install interview
/plugin install wiki
```

```

- [ ] **Step 2: Verify the section renders correctly**

Run: `head -60 CLAUDE.md`
Expected: "Installing Plugins" section appears between "The Six Plugins" table and "Development Commands"

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add Installing Plugins section with marketplace install commands"
```

---

### Task 2: Add versioning and changelog conventions to CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` — append to `## Key Conventions` section (after the last bullet, currently the `.gitignore` bullet)

- [ ] **Step 1: Append versioning rules and changelog workflow to Key Conventions**

After the last existing bullet in Key Conventions (the one about `.gitignore`), append:

```markdown
- **Version control (SemVer):** Every plugin change must update `version` in its `.claude-plugin/plugin.json`
  - **Patch** (`0.1.0` → `0.1.1`): bug fix, doc correction, minor adjustment that doesn't change functional behavior
  - **Minor** (`0.1.0` → `0.2.0`): new skill/agent/command/rule, feature enhancement, non-breaking changes
  - **Major** (`0.x.y` → `1.0.0`): breaking changes — removed skills, changed interfaces, incompatible config
- **Changelog:** On every plugin content change, simultaneously: (1) update `plugin.json` version, (2) add entry under `[Unreleased]` in `CHANGELOG.md`; versions are finalized at release time; each plugin versions independently
```

- [ ] **Step 2: Verify conventions are complete**

Run: `grep -A 8 "Version control" CLAUDE.md`
Expected: Patch/Minor/Major definitions appear, followed by the Changelog bullet

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add SemVer versioning rules and changelog workflow to conventions"
```

---

### Task 3: Create CHANGELOG.md with initial release entries

**Files:**
- Create: `CHANGELOG.md`

- [ ] **Step 1: Write CHANGELOG.md**

Create `CHANGELOG.md` at repository root with this content:

```markdown
# Changelog

All notable changes to the plugins in this marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-23

### analysis
#### Changed
- Updated description in plugin.json

## [0.1.0] - 2026-05-23

### spec-workflow
#### Added
- Initial release: 10 agents, 7 rules, 8 commands, 12 skills

### analysis
#### Added
- Initial release: 5 skills, 2 agents, 3 commands

### coding
#### Added
- Initial release: 14 skills

### office
#### Added
- Initial release: 4 skills (xlsx, pdf, pptx, docx)

### interview
#### Added
- Initial release: project-resume skill

### wiki
#### Added
- Initial release: wiki-ingest, wiki-query, wiki-lint skills
```

Note: analysis starts at 0.2.0 since its `plugin.json` already shows `0.2.0`. All other plugins start at 0.1.0.

- [ ] **Step 2: Verify the file**

Run: `head -20 CHANGELOG.md`
Expected: Changelog header, Unreleased section, then 0.2.0 for analysis, then 0.1.0 for all plugins

- [ ] **Step 3: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add CHANGELOG.md with initial release entries for all plugins"
```
