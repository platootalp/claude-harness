# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A Claude Code plugin marketplace (`harness-marketplace`) that distributes development workflow tools. Users add the marketplace and install individual plugins. This repo contains the marketplace definition and all plugin source code.

## Repo Structure

```
.claude-plugin/marketplace.json   # Marketplace registry — lists all plugins with name + source path
plugins/                           # Active plugin packages
  superpowers-pro/                 # Structured development workflows
    .claude-plugin/plugin.json     # Plugin manifest (name, version, description, author, license)
    skills/<skill-name>/SKILL.md   # Skill definitions with frontmatter + body
    hooks/                         # Session-start hook (injects using-superpowers skill on startup)
  kb/                              # Knowledge base management (ETL pipeline)
    .claude-plugin/plugin.json
    agents/                        # extract-agent, transform-agent (维度级子代理)
    commands/                      # /kb command
    skills/                        # 15 skills (scan, extract-*, transform, ingest, etc.)
    site/                          # Astro 6 + React 18 + d3-force + Fuse.js
other/                             # Previously removed plugins kept for reference
  analysis/                        # Codebase analysis skills + Astro docs site + embedded office plugin
  coding/                          # Coding, testing, and skill-authoring skills (22 total)
  wiki/                            # Wiki ingest/query/lint skills + raw wiki data
docs/                              # Internal specs and plans (not shipped)
  superpowers/plans/               # Implementation plans
  superpowers/specs/               # Design specs
```

## Marketplace Registry

`marketplace.json` 注册 2 个活跃插件：

| Plugin | marketplace.json source | 状态 |
|--------|------------------------|------|
| **superpowers-pro** | `./plugins/superpowers-pro` | 活跃 |
| **kb** | `./plugins/kb` | 活跃 |

旧插件（analysis, coding, office, interview, wiki）已移至 `other/` 保留源码，但未在 marketplace 注册。修改 marketplace.json 或移动插件目录时，必须保持两者一致。

## Active Plugin: superpowers-pro

`plugins/` 下的活跃插件之一。15 skills 覆盖结构化开发工作流：

| Category | Skills |
|----------|--------|
| Workflow entry | using-superpowers (injected on session start), brainstorming |
| Planning | writing-plans, executing-plans, system-architect |
| Development | test-driven-development, subagent-driven-development |
| Git | using-git-worktrees, finishing-a-development-branch |
| Review | requesting-code-review, receiving-code-review |
| Debugging | systematic-debugging |
| Meta | writing-skills, dispatching-parallel-agents, verification-before-completion |

The `session-start` hook automatically injects `using-superpowers` SKILL.md content into agent context, establishing skill discovery behavior for every session.

## Active Plugin: kb

`plugins/kb/` — 知识库管理插件 v0.5.0。ETL 管道：Extract → Transform → Load/Present。

| Phase | Skills | Agents |
|-------|--------|--------|
| Extract | scan, extract (路由), extract-topology, extract-api, extract-data-model, extract-flows, extract-concepts | extract-agent (单维度) |
| Transform | transform (路由), ingest, cross-ref | transform-agent (单维度) |
| Load | build-search-index, build-graph, serve | — |
| Present | （通过站点交互式展示） | — |
| Entry | /kb 命令（6 步检查点编排，并行派发子代理） | extract-agent, transform-agent |

站点：`plugins/kb/site/`（Astro 6 + React 18 + d3-force + Fuse.js），三视图（Raw/Wiki/Graph）+ 搜索 + 知识图谱。

## Inactive Plugins (other/)

已从 marketplace 移除但保留源码的旧插件，位于 `other/`：

- **analysis** (v0.2.0) — 5 skills, 2 agents, 3 commands, Astro docs site；内嵌 office 插件
- **coding** (v0.1.0) — 22 skills（含 skill-creator 评估工具链、ui-ux-pro-max 设计数据）
- **wiki** (v0.1.0) — 3 skills, 1 agent, 三层 wiki 架构（raw sources → wiki pages → query）

这些插件未在 marketplace.json 注册，仅作参考保留。

## Development Commands

```bash
# Test a plugin locally
claude --plugin-dir ./plugins/superpowers-pro

# Validate the marketplace
claude plugin validate .

# Analysis docs site (in other/analysis/)
cd other/analysis/site && npm install && npm run setup && npm run dev
```

## Adding a Skill to superpowers-pro

Create `plugins/superpowers-pro/skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`) and markdown body. Skills can include `references/`, `templates/`, `scripts/`, and `evals/` subdirectories.

## Adding a New Plugin

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`
2. Add skills to `plugins/<name>/skills/`
3. Register in `.claude-plugin/marketplace.json` under `plugins` array
4. Validate: `claude plugin validate .`

## Key Conventions

- All plugin content is markdown — agents, commands, rules, and skills are `.md` files
- Skills use `SKILL.md` as the entry point with YAML frontmatter (`name`, `description` fields minimum)
- **文档语言：** 所有文档（设计文档、spec、CHANGELOG、README 等）均使用中文编写
- **Version control (SemVer):** Every plugin change must update `version` in `.claude-plugin/plugin.json`
  - **Patch**: bug fix, doc correction, minor adjustment
  - **Minor**: new skill/agent/command/rule, feature enhancement
  - **Major**: breaking changes
- **Changelog:** On every plugin content change, simultaneously: (1) update `plugin.json` version, (2) add entry under `[Unreleased]` in the plugin's `CHANGELOG.md`; each plugin versions independently
- **Worktree isolation:** 所有功能开发使用隔离 worktree，测试通过后合并到主分支
