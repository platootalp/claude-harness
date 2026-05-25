# Harness Marketplace

A Claude Code plugin marketplace for structured development workflows and knowledge management.

## Quick Start

```bash
# Add the marketplace
/plugin marketplace add https://github.com/platootalp/harness-marketplace

# Install the core workflow plugin
/plugin install superpowers-pro@harness-marketplace

# Install the knowledge base plugin
/plugin install kb@harness-marketplace
```

## Available Plugins

### superpowers-pro
Structured development workflows for coding agents — feature development, debugging, code review, and more.

15 skills covering the full development lifecycle:
- **Workflow entry:** using-superpowers (auto-injected on session start), brainstorming
- **Planning:** writing-plans, executing-plans, system-architect
- **Development:** test-driven-development, subagent-driven-development
- **Git:** using-git-worktrees, finishing-a-development-branch
- **Review:** requesting-code-review, receiving-code-review
- **Debugging:** systematic-debugging
- **Meta:** writing-skills, dispatching-parallel-agents, verification-before-completion

4 commands: `/feature`, `/fix`, `/init-system`, `/refactor`

### kb
知识库管理插件 — 从代码仓库提取、转化、加载和呈现知识。

ETL 管道：Extract → Transform → Load/Present，支持 15 skills、3 agents、1 command (`/kb`)。

站点：Astro 6 + React 18 + d3-force + Fuse.js，三视图（Raw/Wiki/Graph）+ 搜索 + 知识图谱。

## Development

### Testing a plugin locally

```bash
claude --plugin-dir ./plugins/superpowers-pro
claude --plugin-dir ./plugins/kb
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
