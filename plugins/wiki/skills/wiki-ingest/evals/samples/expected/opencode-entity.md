---
tags: [ai-tools, cli, coding]
date: 2026-05-22
last_updated: 2026-05-22
sources:
  - wiki/sources/opencode-docs.md
status: stable
page_type: entity
---

# OpenCode

## Summary

OpenCode is a provider-agnostic AI coding CLI that supports over 75 LLM providers through a single interface, allowing developers to use models from Anthropic, OpenAI, Google, and many others without being locked into one vendor. It offers multiple interaction modes — a terminal UI (TUI), CLI, web interface, and IDE integration — along with a rich extension system featuring skills, MCP servers, plugins, and custom tools. Its key differentiator is the provider-agnostic architecture: unlike Claude Code (Claude-only) or Codex (OpenAI-only), OpenCode treats the LLM as a pluggable component, making it the only tool that natively supports multi-model workflows and model switching within a single session.

## Key Areas

### Overview

OpenCode is designed around the principle that developers should choose their AI coding tools independently of their LLM provider. It supports 75+ providers through a unified configuration system, with a "Zen" mode that offers curated model selections for users who don't want to choose. The tool provides four interaction interfaces: a terminal UI (TUI) as the primary interactive mode, a CLI for scripted and headless usage, a web interface for browser-based access, and IDE integration for editor-embedded workflows. GitHub and GitLab integrations connect directly to repository workflows, enabling AI-assisted code review and issue management.

A concrete example: a team can configure OpenCode to use Claude for complex reasoning tasks and a faster model (like Haiku) for simple edits, switching between them within the same session based on task complexity. This multi-model approach is unique among AI coding tools.

An important edge case: while OpenCode supports many providers, the quality of the experience varies significantly by provider. Features like extended thinking, tool use, and prompt caching are provider-specific — not all models support all features. The configuration documentation notes which features require specific providers.

### Interfaces

OpenCode provides four distinct ways to interact with the agent, each optimized for a different workflow context. The TUI (terminal UI) is the primary interactive interface with full customization support — themes, keybindings, and layout can all be configured. The CLI mode enables scripted and headless usage, suitable for automation and CI/CD integration. A web interface provides browser-based access, which is useful for remote development scenarios. IDE integration brings OpenCode into the editor environment.

Zen mode offers a simplified experience with curated model options, removing the burden of model selection. The Share feature enables collaboration by allowing users to share session state and outputs. GitHub and GitLab integrations connect directly to repository workflows for AI-assisted code review and issue management.

A practical detail: the TUI and CLI modes share the same configuration but have separate keybinding and theme settings. Customizing the TUI appearance does not affect CLI behavior, and vice versa.

### Configuration

Configuration uses JSON or JSONC files with `$schema` support for validation and autocompletion in editors. The system defines eight priority levels that determine which settings take precedence, ranging from remote configuration (highest priority) down to macOS managed preferences (lowest). This hierarchical approach allows organizational policies to override individual preferences while still permitting project-specific customization.

TUI-specific configuration allows customizing the terminal interface appearance and behavior independently from the core agent configuration. Network and enterprise configurations support organizational deployments with proxy settings, authentication, and compliance requirements.

A notable edge case: the eight priority levels can create confusing behavior when multiple configuration sources are active. The documentation recommends using `opencode config list` to see the effective configuration and which source each setting comes from. Without this, debugging why a particular setting isn't taking effect can be frustrating.

### Built-in Tools

OpenCode ships with 12 built-in tools that cover the core operations needed for AI-assisted coding: bash (shell command execution), edit (file editing with diff support), write (file creation), read (file reading), grep (content search with regex support), glob (file pattern matching), apply_patch (patch application for precise edits), skill (skill invocation for workflow automation), todowrite (task tracking within sessions), webfetch (HTTP requests for API interaction), websearch (web search for documentation lookup), question (user prompts for clarification), and lsp (language server protocol integration for code intelligence).

The LSP tool is particularly notable — it provides real-time code intelligence (go-to-definition, find-references, diagnostics) without requiring a separate language server process. This gives the agent access to the same code understanding that IDEs provide.

A limitation: the built-in tools cannot be disabled or overridden. If you need different behavior for a tool (e.g., a sandboxed bash), you must use the permissions system to restrict it rather than replacing it.

### Built-in Agents

OpenCode organizes its agents into three tiers. Primary agents handle the main workflows: Build (for implementation and code modification tasks) and Plan (for analysis and planning before implementation). Subagents handle specialized work: General for broad tasks that don't fit the primary categories, Explore for codebase navigation and understanding, and Scout for targeted searching and investigation.

Hidden system agents manage infrastructure that users don't directly invoke: Compaction for context window management (keeping conversations within model limits), Title for automatic session naming, and Summary for conversation summarization. These run automatically based on triggers.

A practical detail: the Build and Plan agents can be selected explicitly via configuration or CLI flags, but the subagent routing is automatic based on the task type. Users cannot directly invoke Explore or Scout — they are dispatched by the primary agents when needed.

### Permissions

The permission model defines three actions: allow (execute without prompting), ask (require user approval before execution), and deny (block execution entirely). Permissions use glob patterns for file matching, and the last matching rule wins in case of conflicts — this is a "most specific match wins" approach that provides predictable behavior.

For example, if you have `allow: src/**` followed by `deny: src/secrets/**`, a file in `src/secrets/` will be denied because the deny rule is more specific (appears later). This ordering-based resolution is simple but requires careful rule ordering to avoid unintended access patterns.

A gotcha: the "last matching rule wins" behavior means rule order matters critically. Adding a new allow rule at the end of the configuration can unintentionally override earlier deny rules. The documentation recommends placing deny rules last to avoid this pitfall.

### Skills

Skills follow the SKILL.md format with YAML frontmatter defining the skill's name and description, and a markdown body containing the workflow instructions. Discovery paths include `.opencode/skills/` at the project level and `~/.config/opencode/skills/` globally. OpenCode is also compatible with skills from `.claude/skills/` and `.agents/skills/` directories, enabling cross-tool skill reuse — a skill written for Claude Code can work in OpenCode without modification.

This cross-compatibility is a significant advantage for teams that use multiple AI coding tools. A team can maintain a single set of skills and use them across Claude Code, OpenCode, and any other tool that supports the SKILL.md format.

A limitation: while the skill format is compatible, the tool names and capabilities available within a skill may differ between tools. A skill that uses Claude Code's `Agent` tool will not work in OpenCode if OpenCode doesn't provide an equivalent tool. The skill author must be aware of tool availability across platforms.

### Custom Tools

Custom tools are written as TypeScript files using the `tool()` helper function with Zod schemas for input validation. This approach provides type-safe, validated tool implementations that integrate seamlessly with the agent framework. The Zod schema serves double duty: it validates inputs at runtime and provides type information to the LLM for correct tool invocation.

Custom tools are discovered from configured directories and appear alongside built-in tools in the agent's tool list. They can be used in the same way as built-in tools — the agent decides when to invoke them based on the task context.

An edge case: custom tools run in the same process as the OpenCode agent, which means a poorly written tool (e.g., one with an infinite loop or memory leak) can crash the entire agent. There is no sandboxing for custom tools, unlike Codex's approach of running everything in isolated containers.

### Plugins

Plugins are TypeScript modules distributed as npm packages that can hook into key events in the OpenCode lifecycle. Unlike skills (which are markdown-based workflow instructions) and custom tools (which add individual tool capabilities), plugins can modify the agent's behavior at a structural level — intercepting events, adding middleware, and changing how the agent processes requests.

The plugin system supports both local development (loading from a directory) and published package distribution (installing from npm). Key event hooks allow plugins to run code at specific points in the agent's execution cycle, similar to Cursor's hooks system but with the full power of TypeScript rather than shell scripts.

A limitation: plugins have access to OpenCode's internal APIs, which means they can break when OpenCode is updated. There is no stable plugin API guarantee — plugin authors must keep their plugins up to date with OpenCode releases.

## See Also

- [Claude Code](./claude-code.md) — Compare with Claude Code's Claude-specific approach
- [Cursor](./cursor.md) — Compare with Cursor's editor-native approach
- [Codex](./codex.md) — Compare with Codex's cloud-sandboxed approach
- [OpenCode Docs Source](../sources/opencode-docs.md) — The source document this page was derived from
