# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A Claude Code plugin marketplace (`harness-marketplace`) that distributes development workflow tools. Users add the marketplace and install individual plugins. This repo contains the marketplace definition and all plugin source code.

## Repo Structure

```
.claude-plugin/marketplace.json   # Marketplace registry — lists all plugins with name + source path
plugins/                           # All plugin packages live here
  <plugin-name>/
    .claude-plugin/plugin.json     # Plugin manifest (name, version, description, author, license)
    agents/                        # Subagent definitions (markdown)
    commands/                      # Slash command definitions (markdown)
    rules/                         # Behavioral rules loaded into agent context
    skills/<skill-name>/SKILL.md   # Skill definitions with frontmatter + body
    hooks/hooks.json               # Event hooks
obsolete/                          # Deprecated plugins kept for reference
docs/                              # Superpowers specs and plans (internal, not shipped)
```

## The Five Plugins

| Plugin | Key Contents |
|--------|-------------|
| **analysis** | 5 skills (codebase-to-docs, system-architecture-analysis, deep-functional-analysis, source-functional-analysis, codebase-analysis), 2 agents, 3 commands, Astro-based docs site |
| **coding** | Skills: write-skill, write-agent, write-command, skill-creator/audit/discovery, api-design, testing-patterns, browser-testing, agent-browser, ui-ux-pro-max, next-best-practices, git-workflow, sdk-development, mcp-builder, claude-ext-author |
| **office** | Skills: xlsx, pdf, pptx, docx (each with Python scripts for document manipulation) |
| **interview** | Skills: project-resume (with evals and template) |
| **wiki** | Skills: wiki-ingest, wiki-query, wiki-lint. Agent: wiki-maintainer. Rule: wiki-schema. Raw sources and LLM-maintained wiki pages for AI coding tools (Claude Code, Cursor, Codex, OpenCode, Plugin Builder) |

## Installing Plugins

First, add the marketplace:

```bash
/plugin marketplace add platootalp/claude-harness
```

Then install individual plugins:

```bash
/plugin install analysis
/plugin install coding
/plugin install office
/plugin install interview
/plugin install wiki
```

## Development Commands

### Test a plugin locally
```bash
claude --plugin-dir ./plugins/<plugin-name>
```

### Validate the marketplace
```bash
claude plugin validate .
```

### Analysis plugin docs site
```bash
cd plugins/analysis/site
npm install
npm run setup     # Symlink ../docs into site/
npm run dev       # Astro dev server
npm run build     # Build search index + static site
```

## Adding a New Plugin

1. Create `plugins/<name>/` directory with `.claude-plugin/plugin.json`
2. Add skills to `plugins/<name>/skills/<skill-name>/SKILL.md`
3. Optionally add agents, commands, rules, hooks subdirectories
4. Register in `.claude-plugin/marketplace.json` under `plugins` array
5. Validate: `claude plugin validate .`

## Adding a Skill to an Existing Plugin

Create `plugins/<plugin>/skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`) and markdown body. Skills can include `references/`, `templates/`, `scripts/`, and `evals/` subdirectories for supporting content.

## Key Conventions

- All plugin content is markdown — agents, commands, rules, and skills are `.md` files
- Skills use `SKILL.md` as the entry point with YAML frontmatter (`name`, `description` fields minimum)
- The analysis plugin's `.gitignore` excludes generated `docs/` and site build artifacts (`site/node_modules/`, `site/dist/`, `site/.astro/`)
- **Version control (SemVer):** Every plugin change must update `version` in its `.claude-plugin/plugin.json`
  - **Patch** (`0.1.0` → `0.1.1`): bug fix, doc correction, minor adjustment that doesn't change functional behavior
  - **Minor** (`0.1.0` → `0.2.0`): new skill/agent/command/rule, feature enhancement, non-breaking changes
  - **Major** (`0.x.y` → `1.0.0`): breaking changes — removed skills, changed interfaces, incompatible config
- **Changelog:** On every plugin content change, simultaneously: (1) update `plugin.json` version, (2) add entry under `[Unreleased]` in `CHANGELOG.md`; versions are finalized at release time; each plugin versions independently
- **文档语言：** 所有文档（设计文档、spec、CHANGELOG、README 等）均使用中文编写
