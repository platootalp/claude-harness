---
name: upstream-sync-design
description: superpowers-pro 与上游 obra/superpowers skills 全量同步设计文档
---

# 上游同步设计：superpowers-pro ↔ obra/superpowers

## 背景

superpowers-pro 基于 obra/superpowers 二开。上游已有多项改动（新功能、通用化重构、多平台支持），需要同步到本地，同时保留二开定制。

## 同步范围

### 包含

- 12 个有差异的共享 skill（全部同步上游改动）
- 上游新增文件：
  - `using-superpowers/references/antigravity-tools.md`
  - `using-superpowers/references/pi-tools.md`
  - `using-superpowers/references/claude-code-tools.md`
  - `subagent-driven-development/scripts/`（review-package、sdd-workspace、task-brief）
  - `subagent-driven-development/task-reviewer-prompt.md`

### 排除

- `executing-plans` skill（已决定不需要）
- 5 个本地独有 skill（issue-scanning、prd-generator、refactor-assessment、system-architect、variables）不做修改
- `verification-before-completion`（已与上游完全相同）

## 同步原则

1. **以上游版本为基准**，将二开定制重新应用
2. **采用上游通用化格式**：`Subagent (general-purpose):` 替代 `Task tool (general-purpose):`，`{PLACEHOLDER}` 替代 `[PLACEHOLDER]`，通用 `todos` 替代 `TodoWrite`
3. **保留 superpowers-pro 命名空间**：所有 `superpowers:` → `superpowers-pro:`，`docs/superpowers/` → `docs/superpowers-pro/`，`.superpowers/` → `.superpowers-pro/`
4. **保留二开功能**：finish-mode 变量、review-mode 变量、源分支确认（Step 0.5）

## 逐 Skill 合并策略

### brainstorming

- **SKILL.md**：采用上游版本，重新应用 review-mode 变量声明 + Review Modes 章节 + 流程图增加 visual companion 分支 + section-by-section/full 双模式 + `docs/superpowers-pro/specs/` 路径
- **visual-companion.md**：采用上游版本，替换 `.superpowers/` → `.superpowers-pro/`
- **spec-document-reviewer-prompt.md**：采用上游版本，替换 `docs/superpowers/specs/` → `docs/superpowers-pro/specs/`
- **scripts/**：全部采用上游版本，替换 `.superpowers/` → `.superpowers-pro/`

### dispatching-parallel-agents

- **SKILL.md**：采用上游版本（`Subagent (general-purpose):` 格式），无需额外定制

### finishing-a-development-branch

- **SKILL.md**：采用上游版本，重新应用 finish-mode 变量声明 + description 更新 + Variable Resolution 章节 + auto/interactive 双模式流程图 + 源分支确认逻辑
- **evals/**、**references/**：保留本地独有文件不动

### receiving-code-review

- **SKILL.md**：采用上游版本，无需额外定制

### requesting-code-review

- **SKILL.md**：采用上游版本，替换 `docs/superpowers/` → `docs/superpowers-pro/`
- **code-reviewer.md**：采用上游版本

### subagent-driven-development

- **SKILL.md**：采用上游版本，替换 `superpowers:` → `superpowers-pro:`。上游将两阶段审查合并为单 task-reviewer，跟随上游方案
- **implementer-prompt.md**：采用上游版本
- **新增** `task-reviewer-prompt.md`：从上游复制，替换 `superpowers:` → `superpowers-pro:`
- **新增** `scripts/` 目录：从上游复制 review-package、sdd-workspace、task-brief
- **删除** `spec-reviewer-prompt.md`、`code-quality-reviewer-prompt.md`：上游已合并为 task-reviewer

### systematic-debugging

- **SKILL.md**：采用上游版本，替换 `superpowers:` → `superpowers-pro:`

### test-driven-development

- **SKILL.md**：采用上游版本

### using-git-worktrees

- **SKILL.md**：采用上游版本，重新应用 Step 0.5 源分支确认逻辑

### using-superpowers

- **SKILL.md**：采用上游版本，替换 `Superpowers` → `Superpowers-Pro`、`superpowers:` → `superpowers-pro:`
- **references/**：全部采用上游版本（codex、copilot、gemini 更新版 + 新增 claude-code、antigravity、pi）

### writing-plans

- **SKILL.md**：采用上游版本，替换 `superpowers:` → `superpowers-pro:`、`docs/superpowers/` → `docs/superpowers-pro/`。删除 executing-plans 选项，只保留 subagent-driven-development
- **plan-document-reviewer-prompt.md**：采用上游版本

### writing-skills

- **SKILL.md**：采用上游版本，替换 `superpowers:` → `superpowers-pro:`
- **anthropic-best-practices.md**：采用上游版本
- **persuasion-principles.md**：采用上游版本
- **testing-skills-with-subagents.md**：采用上游版本，替换 `superpowers:` → `superpowers-pro:`

## 版本与 Changelog

- 同步完成后 bump `plugin.json` version（minor）
- CHANGELOG.md 添加 `[Unreleased]` 条目

## 验证

- 对每个修改的 skill，diff 确认上游改动已合入 + 二开定制已保留
- 运行 `claude plugin validate .` 验证插件结构
