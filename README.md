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
