---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback
---

# Using Git Worktrees

## Overview

Ensure work happens in an isolated workspace. Prefer your platform's native worktree tools. Fall back to manual git worktrees only when no native tool is available.

**Core principle:** Detect existing isolation first. Then use native tools. Then fall back to git. Never fight the harness.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## Step 0: Detect Existing Isolation

**Before creating anything, check if you are already in an isolated workspace.**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**Submodule guard:** `GIT_DIR != GIT_COMMON` is also true inside git submodules. Before concluding "already in a worktree," verify you are not in a submodule:

```bash
# If this returns a path, you're in a submodule, not a worktree — treat as normal repo
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**If `GIT_DIR != GIT_COMMON` (and not a submodule):** You are already in a linked worktree. Skip to Step 3 (Project Setup). Do NOT create another worktree.

Report with branch state:
- On a branch: "Already in isolated workspace at `<path>` on branch `<name>`."
- Detached HEAD: "Already in isolated workspace at `<path>` (detached HEAD, externally managed). Branch creation needed at finish time."

**If `GIT_DIR == GIT_COMMON` (or in a submodule):** You are in a normal repo checkout.

Has the user already indicated their worktree preference in your instructions? If not, ask for consent before creating a worktree:

> "Would you like me to set up an isolated worktree? It protects your current branch from changes."

Honor any existing declared preference without asking. If the user declines consent, work in place and skip to Step 3.

## Step 0.5: Confirm Source Branch

**核心原则**：worktree 创建**前**必须明确源分支，**不**静默推断成主仓库 HEAD。原因：用户的主仓库 HEAD 可能停在分支 X（出于其他工作），但他想为分支 Y 创建 worktree。

**跳过场景**：Step 0 检测到"已在 worktree 内"时跳到 Step 3，本步不执行。

优先级:
1. 调用方显式传入 `EXPLICIT_SOURCE_BRANCH` (如 skill 调用参数 / conversation 已明确)
2. 弹菜单询问用户 (默认 = 主仓库 HEAD)
3. detached HEAD 或非法值 → 报错退出

bash 实现:

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
MAIN_HEAD=$(git -C "$MAIN_ROOT" symbolic-ref --short HEAD 2>/dev/null)

if [ -n "${EXPLICIT_SOURCE_BRANCH:-}" ]; then
  SOURCE_BRANCH="$EXPLICIT_SOURCE_BRANCH"
  echo "Using explicit source branch: $SOURCE_BRANCH"
else
  echo "请选择 worktree 的源分支（按回车采用默认）："
  echo "  [1] $MAIN_HEAD  (主仓库当前 HEAD - 默认)"

  i=2
  CANDIDATES=("$MAIN_HEAD")
  LOCAL_BRANCHES=$(git for-each-ref --sort=-committerdate --format='%(refname:short)' refs/heads/ | head -10)
  for b in $LOCAL_BRANCHES; do
    [ "$b" = "$MAIN_HEAD" ] && continue
    echo "  [$i] $b"
    CANDIDATES+=("$b")
    i=$((i+1))
  done

  REMOTE_FEATURES=$(git for-each-ref --format='%(refname:short)' refs/remotes/origin/ 2>/dev/null | grep -v 'HEAD' | head -10)
  for r in $REMOTE_FEATURES; do
    LOCAL_NAME=${r#origin/}
    git show-ref --quiet "refs/heads/$LOCAL_NAME" && continue
    echo "  [$i] $r"
    CANDIDATES+=("$r")
    i=$((i+1))
  done

  echo "  [c] 自定义输入分支名"
  read -r CHOICE

  case "$CHOICE" in
    "") SOURCE_BRANCH="$MAIN_HEAD" ;;
    [0-9]*) IDX=$((CHOICE-1)); SOURCE_BRANCH="${CANDIDATES[$IDX]:-}" ;;
    c|C) echo "请输入源分支名："; read -r SOURCE_BRANCH ;;
    *) SOURCE_BRANCH="$CHOICE" ;;
  esac
fi

if [ -z "$SOURCE_BRANCH" ] || [ "$SOURCE_BRANCH" = "HEAD" ]; then
  echo "ERROR: 无法在 detached HEAD 上创建 worktree。请明确指定源分支。"
  exit 1
fi

if ! git rev-parse --verify "$SOURCE_BRANCH" >/dev/null 2>&1; then
  echo "ERROR: 源分支 '$SOURCE_BRANCH' 不存在。"
  exit 1
fi

echo "Source branch confirmed: $SOURCE_BRANCH"
```

**为什么必须显式确认**：以前的设计静默用主仓库 HEAD。但实际工作中主仓库可能停在 feature-A（保留其他工作的状态），而你想为 feature-B 开始多 worktree 任务——若不显式确认，会错误地基于 feature-A 创建 worktree。

## Step 1: Create Isolated Workspace

**所有创建路径必须使用 Step 0.5 确认的 `SOURCE_BRANCH` 作为 base**，不再依赖主仓库 HEAD。

**You have two mechanisms. Try them in this order.**

### 1a. Native Worktree Tools (preferred)

The user has asked for an isolated workspace (Step 0 consent). Do you already have a way to create a worktree? It might be a tool with a name like `EnterWorktree`, `WorktreeCreate`, a `/worktree` command, or a `--worktree` flag. If you do, use it and skip to Step 3.

Native tools handle directory placement, branch creation, and cleanup automatically. Using `git worktree add` when you have a native tool creates phantom state your harness can't see or manage.

Only proceed to Step 1b if you have no native worktree tool available.

**Native tool base ref 限制处理**：native tool（如 `EnterWorktree`）通常只支持有限的 base ref 模式（`fresh` = origin/<default-branch>，`head` = 主仓库 HEAD）。决策：

- 如果 `SOURCE_BRANCH == MAIN_HEAD` → 直接用 native tool（head 模式）
- 如果 `SOURCE_BRANCH == origin/<default-branch>` 且 native tool 支持 fresh → 用 native tool（fresh 模式）
- 否则 → fallback 到 Step 1b（git worktree add 可显式指定任意 base）

注意：默认 native tool 行为可能不匹配 `SOURCE_BRANCH`。如果创建后发现 worktree HEAD 不是预期，应立即 `git reset --hard "$SOURCE_BRANCH"` 同步（或重新走 Step 1b）。

### 1b. Git Worktree Fallback

**Only use this if Step 1a does not apply** — you have no native worktree tool available. Create a worktree manually using git.

#### Directory Selection

Follow this priority order. Explicit user preference always beats observed filesystem state.

1. **Check your instructions for a declared worktree directory preference.** If the user has already specified one, use it without asking.

2. **Check for an existing project-local worktree directory:**
   ```bash
   ls -d .worktrees 2>/dev/null     # Preferred (hidden)
   ls -d worktrees 2>/dev/null      # Alternative
   ```
   If found, use it. If both exist, `.worktrees` wins.

3. **Check for an existing global directory:**
   ```bash
   project=$(basename "$(git rev-parse --show-toplevel)")
   ls -d ~/.config/superpowers-pro/worktrees/$project 2>/dev/null
   ```
   If found, use it (backward compatibility with legacy global path).

4. **If there is no other guidance available**, default to `.worktrees/` at the project root.

#### Safety Verification (project-local directories only)

**MUST verify directory is ignored before creating worktree:**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**If NOT ignored:** Add to .gitignore, commit the change, then proceed.

**Why critical:** Prevents accidentally committing worktree contents to repository.

Global directories (`~/.config/superpowers-pro/worktrees/`) need no verification.

#### Create the Worktree

```bash
project=$(basename "$(git rev-parse --show-toplevel)")

# Determine path based on chosen location
# For project-local: path="$LOCATION/$BRANCH_NAME"
# For global: path="~/.config/superpowers-pro/worktrees/$project/$BRANCH_NAME"

# 第三个位置参数显式指定 $SOURCE_BRANCH 作为 base，强制基于该分支创建（不依赖主仓库 HEAD）
git worktree add -b "$BRANCH_NAME" "$path" "$SOURCE_BRANCH"
cd "$path"
```

**Sandbox fallback:** If `git worktree add` fails with a permission error (sandbox denial), tell the user the sandbox blocked worktree creation and you're working in the current directory instead. Then run setup and baseline tests in place.

## Step 2.5: Record Source Branch Metadata

把 Step 0.5 确认的 `SOURCE_BRANCH` 写入 worktree-local config，供 `finishing-a-development-branch` skill 在 finish 时使用。

**跳过场景**：Step 0 检测到"已在 worktree 内"时跳过本步（保留现有元数据；老 worktree 由 finish 端 fallback 处理）。

```bash
GIT_VERSION_MAJOR=$(git --version | awk '{print $3}' | cut -d. -f1)
GIT_VERSION_MINOR=$(git --version | awk '{print $3}' | cut -d. -f2)

if [ "$GIT_VERSION_MAJOR" -gt 2 ] || \
   ([ "$GIT_VERSION_MAJOR" -eq 2 ] && [ "$GIT_VERSION_MINOR" -ge 20 ]); then
  git config extensions.worktreeConfig true
  git config --worktree superpowers.sourceBranch "$SOURCE_BRANCH"
  git config --worktree superpowers.sourceCommit "$(git rev-parse "$SOURCE_BRANCH")"
else
  echo "$SOURCE_BRANCH" > "$(git rev-parse --git-path superpowers-source)"
  git rev-parse "$SOURCE_BRANCH" > "$(git rev-parse --git-path superpowers-source-commit)"
fi
```

**为什么必须先启用 `extensions.worktreeConfig=true`**：默认情况下 git 把所有 worktree 的 config 当作共享 config。启用扩展后 `--worktree` 写入才会真正落到 per-worktree 的 `config.worktree` 文件，实现元数据隔离。

## Step 3: Project Setup

Auto-detect and run appropriate setup:

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

## Step 4: Verify Clean Baseline

Run tests to ensure workspace starts clean:

```bash
# Use project-appropriate command
npm test / cargo test / pytest / go test ./...
```

**If tests fail:** Report failures, ask whether to proceed or investigate.

**If tests pass:** Report ready.

### Report

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| Already in linked worktree | Skip creation (Step 0) |
| In a submodule | Treat as normal repo (Step 0 guard) |
| Native worktree tool available | Use it (Step 1a) |
| No native tool | Git worktree fallback (Step 1b) |
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check instruction file, then default `.worktrees/` |
| Global path exists | Use it (backward compat) |
| Directory not ignored | Add to .gitignore + commit |
| Permission error on create | Sandbox fallback, work in place |
| Tests fail during baseline | Report failures + ask |
| No package.json/Cargo.toml | Skip dependency install |
| New worktree created | Confirm source branch (Step 0.5) -> use as base (Step 1) -> record metadata (Step 2.5) |
| EXPLICIT_SOURCE_BRANCH set | Skip menu, use directly (Step 0.5 priority 1) |
| git < 2.20 | Fallback to file in .git/worktrees/<name>/superpowers-source |

## Common Mistakes

### Fighting the harness

- **Problem:** Using `git worktree add` when the platform already provides isolation
- **Fix:** Step 0 detects existing isolation. Step 1a defers to native tools.

### Skipping detection

- **Problem:** Creating a nested worktree inside an existing one
- **Fix:** Always run Step 0 before creating anything

### Skipping ignore verification

- **Problem:** Worktree contents get tracked, pollute git status
- **Fix:** Always use `git check-ignore` before creating project-local worktree

### Assuming directory location

- **Problem:** Creates inconsistency, violates project conventions
- **Fix:** Follow priority: existing > global legacy > instruction file > default

### Proceeding with failing tests

- **Problem:** Can't distinguish new bugs from pre-existing issues
- **Fix:** Report failures, get explicit permission to proceed

### Silently using main repo HEAD as source

- **Problem:** main repo HEAD may be on branch X while user wants worktree for branch Y; silent inference leads to wrong source
- **Fix:** Step 0.5 explicitly confirms source branch (menu) before creating worktree

### Forgetting to record source branch

- **Problem:** finish-a-development-branch falls back to inference and may merge to the wrong branch
- **Fix:** Step 2.5 records source branch metadata when worktree is newly created

## Red Flags

**Never:**
- Create a worktree when Step 0 detects existing isolation
- Use `git worktree add` when you have a native worktree tool (e.g., `EnterWorktree`). This is the #1 mistake — if you have it, use it.
- Skip Step 1a by jumping straight to Step 1b's git commands
- Create worktree without verifying it's ignored (project-local)
- Skip baseline test verification
- Proceed with failing tests without asking
- Skip Step 0.5 confirmation (causes silent reliance on main repo HEAD)
- Skip Step 2.5 for newly created worktrees (causes finish to merge to wrong branch)
- Use `git worktree add` without explicit source branch argument (Step 1b must pass `$SOURCE_BRANCH`)

**Always:**
- Run Step 0 detection first
- Prefer native tools over git fallback
- Follow directory priority: existing > global legacy > instruction file > default
- Verify directory is ignored for project-local
- Auto-detect and run project setup
- Verify clean test baseline
- Confirm source branch before creating worktree (Step 0.5)
- Pass `$SOURCE_BRANCH` as explicit base when calling `git worktree add` (Step 1b)
- Record source branch metadata when creating a new worktree (Step 2.5)
