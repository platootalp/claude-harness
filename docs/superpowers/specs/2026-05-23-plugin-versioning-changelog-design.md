# Plugin Installation, Versioning, and Changelog Design

**Date:** 2026-05-23
**Status:** Approved

## Problem

The CLAUDE.md lacks plugin installation instructions, there is no versioning discipline when plugins change, and no changelog exists in the repository. Users don't know how to install plugins, and there's no record of what changed between versions.

## Design

### 1. CLAUDE.md — New "Installing Plugins" Section

Insert a new section before "Development Commands" with marketplace-level install commands:

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

### 2. CLAUDE.md — Version Control Rules in "Key Conventions"

Add to the existing conventions section:

- **Patch** (`0.1.0` → `0.1.1`): bug fix, doc correction, minor adjustment that doesn't change functional behavior
- **Minor** (`0.1.0` → `0.2.0`): new skill/agent/command/rule, feature enhancement, non-breaking changes
- **Major** (`0.x.y` → `1.0.0`): breaking changes — removed skills, changed interfaces, incompatible config changes
- Every plugin file change must update the `version` field in the plugin's `plugin.json`
- Multiple plugins changed in one session each bump their version independently

### 3. CHANGELOG.md — Root-Level Changelog

Create `CHANGELOG.md` at repository root following [Keep a Changelog](https://keepachangelog.com) format, organized by plugin:

```markdown
# Changelog

## [Unreleased]

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

Each version entry groups changes by plugin name, then by category (`Added` / `Changed` / `Deprecated` / `Removed` / `Fixed` / `Security`).

### 4. Workflow Rules in CLAUDE.md

Add to "Key Conventions":

- On every plugin content change, simultaneously: (1) update `plugin.json` version, (2) add entry under `[Unreleased]` in `CHANGELOG.md`
- Version numbers are finalized (from `[Unreleased]` to a specific version) at release time
- Each plugin versions independently — a change to wiki doesn't bump spec-workflow's version

## Files Changed

| File | Action |
|------|--------|
| `CLAUDE.md` | Add "Installing Plugins" section, add versioning and changelog conventions |
| `CHANGELOG.md` | Create with initial release entries for all 6 plugins |
| `plugins/*/\.claude-plugin/plugin.json` | No version changes yet — current versions are the baseline |

## Scope

This design covers documentation and process only. No code changes to plugins themselves.
