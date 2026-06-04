# finishing-skill source-branch safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-pro:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 改造 `finishing-a-development-branch` + `using-git-worktrees` 两个 skill，使 worktree finish 时合并回创建时所基于的源分支（不依赖主仓库 HEAD），并把 PR/MR 创建路径改成多平台通用方案（GitHub + GitLab，不依赖 `gh` CLI）。

**Architecture:** worktree 创建时把"源分支"持久化到 per-worktree git config（`git config --worktree superpowers.sourceBranch`）；finish 时读取它，根据 source 形态（active worktree / 仅 ref）自动选择 merge 路径，主仓库 HEAD 全程不变。PR/MR 创建路径用 `git push -u origin` + 平台 URL 推导，不调用任何 CLI。

**Tech Stack:** Bash + Markdown（Claude Code skill 文件）+ git 2.20+

**Spec 引用:** `docs/superpowers-pro/specs/2026-06-04-finishing-skill-source-branch-safety-design.md`

---

## File Structure

| 文件 | 操作 | 责任 |
|------|------|------|
| `plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md` | 修改 | 新增 Step 2.5：写入源分支元数据 |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md` | 修改 | 重写 Step 3 + Step 4 auto；改造 interactive Option 2 |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/references/source-resolution.md` | 创建 | 源分支解析与 merge 路径决策详细规则 |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/references/pr-mr-creation.md` | 创建 | PR/MR 创建多平台通用方案 |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/references/test-scenarios.md` | 创建 | 13 个测试场景的 setup/action/expect |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/01-basic-merge.sh` | 创建 | 场景 1 端到端 bash 测试 |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/02-main-repo-on-other-branch.sh` | 创建 | 场景 2：主仓库 HEAD 不同 |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/05-old-worktree-fallback.sh` | 创建 | 场景 5：老 worktree fallback |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/11-github-pr-url.sh` | 创建 | 场景 11：GitHub PR URL 推导 |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/12-gitlab-mr-url.sh` | 创建 | 场景 12：GitLab MR URL 推导 |
| `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/13-unknown-platform.sh` | 创建 | 场景 13：未识别平台 fallback |
| `plugins/superpowers-pro/commands/feat.md` | 修改 | Step 8 检查点描述同步 |
| `plugins/superpowers-pro/commands/fix.md` | 修改 | Step 8 检查点描述同步 |
| `plugins/superpowers-pro/commands/refactor.md` | 修改 | Step 8 检查点描述同步 |
| `plugins/superpowers-pro/commands/init.md` | 修改 | Step 8 检查点描述同步 |
| `plugins/superpowers-pro/.claude-plugin/plugin.json` | 修改 | version bump（minor，新增源分支感知能力） |
| `plugins/superpowers-pro/CHANGELOG.md` | 修改 | Unreleased 条目 |

---

## Task 1: using-git-worktrees Step 2.5 — 写入源分支元数据

**Files:**
- Modify: `plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md`

**目标:** 在现有 Step 1（Create Isolated Workspace）和 Step 3（Project Setup）之间插入 Step 2.5，写入源分支元数据；同步更新 Quick Reference。

- [ ] **Step 1: 在 SKILL.md Step 1b 末尾后、Step 3 前插入 Step 2.5**

打开 `plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md`，在 "## Step 3: Project Setup" 行之前插入：

```markdown
## Step 2.5: Record Source Branch Metadata

记录 worktree 的"源分支"，供 `finishing-a-development-branch` skill 在 finish 时使用，避免依赖主仓库 HEAD。

**仅在新建 worktree 时执行**（Step 0 检测到"已在 worktree 内"时跳过）。

```bash
# SOURCE_BRANCH 获取顺序：
# 1. 调用方显式参数（如 skill 调用 source-branch=feature-A）
# 2. worktree 创建时 git checkout -b 的 base（通常是主仓库当时的 HEAD symbolic ref）
# 3. detached HEAD → 询问用户

MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
SOURCE_BRANCH="${SOURCE_BRANCH:-$(git -C "$MAIN_ROOT" symbolic-ref --short HEAD 2>/dev/null)}"

if [ -z "$SOURCE_BRANCH" ] || [ "$SOURCE_BRANCH" = "HEAD" ]; then
  echo "Cannot determine source branch automatically (detached HEAD or unclear)."
  echo "Please specify the source branch name:"
  read SOURCE_BRANCH
fi

# 写入 worktree-local config
GIT_VERSION_MAJOR=$(git --version | awk '{print $3}' | cut -d. -f1)
GIT_VERSION_MINOR=$(git --version | awk '{print $3}' | cut -d. -f2)

if [ "$GIT_VERSION_MAJOR" -gt 2 ] || \
   ([ "$GIT_VERSION_MAJOR" -eq 2 ] && [ "$GIT_VERSION_MINOR" -ge 20 ]); then
  # 启用 per-worktree config 扩展（幂等；写一次仓库级 config）
  git config extensions.worktreeConfig true
  git config --worktree superpowers.sourceBranch "$SOURCE_BRANCH"
  git config --worktree superpowers.sourceCommit "$(git rev-parse "$SOURCE_BRANCH")"
else
  # Fallback for git < 2.20
  echo "$SOURCE_BRANCH" > "$(git rev-parse --git-path superpowers-source)"
  git rev-parse "$SOURCE_BRANCH" > "$(git rev-parse --git-path superpowers-source-commit)"
fi
```

**为什么必须先启用 `extensions.worktreeConfig=true`**：默认情况下 git 把所有 worktree 的 config 当作共享 config。启用扩展后 `--worktree` 写入才会真正落到 per-worktree 的 `config.worktree` 文件，实现元数据隔离。

**Skip 场景**：如果 Step 0 检测到"已在 worktree 内"，跳过本步（保留现有元数据；老 worktree 由 finish 端 fallback 处理）。

```

- [ ] **Step 2: 更新 Quick Reference 表（在现有表末尾新增 2 行）**

定位到 `## Quick Reference` 章节，在最后一行 "No package.json/Cargo.toml" 之后新增：

```markdown
| New worktree created | Record source branch metadata (Step 2.5) |
| git < 2.20 | Fallback to file in `.git/worktrees/<name>/superpowers-source` |
```

- [ ] **Step 3: 更新 Common Mistakes 章节，新增 1 项**

在 `## Common Mistakes` 末尾新增：

```markdown
### Forgetting to record source branch

- **Problem:** finish-a-development-branch falls back to inference and may merge to the wrong branch
- **Fix:** Step 2.5 records source branch metadata when worktree is newly created
```

- [ ] **Step 4: 更新 Red Flags 章节**

定位到 `## Red Flags` → `**Never:**` 列表末尾新增：

```markdown
- Skip Step 2.5 for newly created worktrees (causes finish to merge to wrong branch)
```

并在 `**Always:**` 列表末尾新增：

```markdown
- Record source branch metadata when creating a new worktree (Step 2.5)
```

- [ ] **Step 5: 自查 — grep 验证关键词存在**

Run:
```bash
grep -c "Step 2.5" plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md
grep -c "superpowers.sourceBranch" plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md
grep -c "extensions.worktreeConfig" plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md
```
Expected: 每行 >= 2（出现在多处：标题 + 引用 + Quick Ref）

- [ ] **Step 6: Commit**

```bash
git add plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md
git commit -m "feat(using-git-worktrees): record source branch metadata in worktree config"
```

---

## Task 2: finishing-a-development-branch Step 3 — Determine Source Branch（替换 Determine Base Branch）

**Files:**
- Modify: `plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md`

**目标:** 把现有 Step 3 "Determine Base Branch"（用 git merge-base 推断）替换为 "Determine Source Branch"（读 worktree 元数据 + fallback）。

- [ ] **Step 1: 定位现有 Step 3 边界**

Run:
```bash
grep -n "^### Step 3:" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
grep -n "^### Step 4:" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
```
Expected: 两行行号，确定要替换的区间。

- [ ] **Step 2: 替换整段 Step 3**

将 `### Step 3: Determine Base Branch` 章节（含其下 3 行 `git merge-base` 代码）替换为：

```markdown
### Step 3: Determine Source Branch

读取 worktree 元数据，决定合并目标。**不依赖主仓库 HEAD**。

```bash
# 1. 优先读取 worktree-local config（git 2.20+）
SOURCE=$(git config --worktree superpowers.sourceBranch 2>/dev/null)

# 2. fallback 到文件
if [ -z "$SOURCE" ]; then
  SOURCE_FILE="$(git rev-parse --git-path superpowers-source)"
  [ -f "$SOURCE_FILE" ] && SOURCE=$(cat "$SOURCE_FILE")
fi

# 3. 仍空 → 暂停询问用户（老 worktree / 手动 git worktree add）
if [ -z "$SOURCE" ]; then
  CANDIDATE=$(git merge-base HEAD main 2>/dev/null \
              || git merge-base HEAD master 2>/dev/null \
              || echo "未知")
  echo "未找到此 worktree 的源分支元数据（可能是手动 git worktree add 创建）。"
  echo "候选源分支推断：$CANDIDATE"
  echo "请确认源分支名（或输入 'pr' 跳过本地 merge 走 PR/MR 路径）："
  read SOURCE
fi
```

**特殊值**：
- `SOURCE = pr`：跳过 auto merge 子流程，转走 PR/MR 创建路径（见 `references/pr-mr-creation.md`）。
- `SOURCE` 为空且非交互（无 stdin）：报错退出，提示用户手动 finish。

详见 `references/source-resolution.md`。
```

- [ ] **Step 3: 同步 Quick Reference 表中的"base branch"措辞**

Run:
```bash
grep -n "base branch\|base-branch" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
```
Expected: 列出所有"base"引用。把表格中 `<base-branch>` 字面替换为 `<source-branch>`，把表头/说明中"base"也改成"source"。

- [ ] **Step 4: 自查**

Run:
```bash
grep -c "Determine Source Branch" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
grep -c "superpowers.sourceBranch" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
grep -c "Determine Base Branch" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
```
Expected: 第 1 行 >= 1，第 2 行 >= 1，第 3 行 == 0（已完全替换）

- [ ] **Step 5: Commit**

```bash
git add plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
git commit -m "feat(finishing): rewrite Step 3 to read source branch from worktree metadata"
```

---

## Task 3: finishing Step 4 auto — 基础架构与 source 形态检测

**Files:**
- Modify: `plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md`

**目标:** 重写 Step 4 auto 模式开头部分 — 特殊情况短路（push only / 无新提交）+ source 形态检测（active worktree vs 仅 ref）。

- [ ] **Step 1: 定位 auto 模式 6 步流程**

Run:
```bash
grep -n "^#### auto mode" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
grep -n "^#### interactive mode" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
```
Expected: 两行行号，确定 auto 段落区间。

- [ ] **Step 2: 替换 auto mode 整段开头（保留 "确定性管道，源分支感知，主仓库零打扰" 总述 + 特殊情况短路）**

把 `#### auto mode` 章节下、`#### interactive mode` 之前的内容替换为：

````markdown
#### auto mode

源分支感知的确定性流水线，**主仓库 HEAD 全程不变**。

```bash
SOURCE_BRANCH="$SOURCE"  # 来自 Step 3
WT_BRANCH=$(git branch --show-current)
WT_PATH=$(git rev-parse --show-toplevel)

# === 特殊路径短路 ===

# A. SOURCE == "pr" → 走 PR/MR 创建路径
if [ "$SOURCE_BRANCH" = "pr" ]; then
  # 跳到 PR/MR 创建路径（见下方 4.6 / pr-mr-creation.md）
  goto_pr_mr_path=true
fi

# B. /init 工作流（无源分支或源==当前分支）→ push only
if [ "$WT_BRANCH" = "$SOURCE_BRANCH" ] || [ -z "$SOURCE_BRANCH" ]; then
  git push -u origin "$WT_BRANCH"
  # cleanup worktree (Step 5)
  exit 0
fi

# C. worktree HEAD == source HEAD（无新提交，已合并）→ skip merge
if [ "$(git rev-parse HEAD)" = "$(git rev-parse "$SOURCE_BRANCH" 2>/dev/null)" ]; then
  echo "Worktree branch HEAD == source branch HEAD, nothing to merge. Skipping."
  # 仍执行 cleanup（Step 5）
  exit 0
fi

# === Source 形态检测 ===

# 查找 source branch 是否在 active worktree 中 active
SOURCE_WT=$(git worktree list --porcelain | \
  awk -v src="refs/heads/$SOURCE_BRANCH" '
    /^worktree / { wt=$2 }
    /^branch / { if ($2 == src) print wt }
  ')

# SOURCE_WT 非空 → source 在某个 worktree 内 active
# SOURCE_WT 空 → source 仅为 ref，无 active worktree
```

后续按 source 形态分支处理，详见 Task 4。
````

- [ ] **Step 3: 自查**

Run:
```bash
grep -c "Source 形态检测\|SOURCE_WT" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
grep -c "git worktree list --porcelain" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
```
Expected: 第 1 行 >= 2，第 2 行 >= 1

- [ ] **Step 4: Commit**

```bash
git add plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
git commit -m "feat(finishing): rewrite Step 4 auto preamble — short-circuits and source detection"
```

---

## Task 4: finishing Step 4 — 三种 merge 路径 + 测试与 push

**Files:**
- Modify: `plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md`

**目标:** 在 Task 3 添加的 source 检测后追加 2a/2b/2c 三种 merge 路径 + 测试 + push + 回滚。

- [ ] **Step 1: 在 Task 3 添加的代码块之后追加完整 merge 路径**

在 "后续按 source 形态分支处理，详见 Task 4。" 这一行替换为：

````markdown
**Merge 路径决策**：

```bash
if [ -n "$SOURCE_WT" ]; then
  # === 2a: source 在 active worktree → cd 进去 merge ===
  
  # 校验 source worktree 干净
  if ! git -C "$SOURCE_WT" diff --quiet || ! git -C "$SOURCE_WT" diff --cached --quiet; then
    echo "Source worktree at $SOURCE_WT has uncommitted changes."
    echo "Please commit or stash them, then reply 'continue' or 'continue' to resume finish."
    exit 1
  fi
  
  pushd "$SOURCE_WT" > /dev/null
  if ! git merge --no-ff "$WT_BRANCH" -m "Merge $WT_BRANCH into $SOURCE_BRANCH"; then
    echo "Merge conflict detected. Conflicted files:"
    git diff --name-only --diff-filter=U
    echo "Please resolve conflicts and commit, then reply 'continue' to resume finish."
    popd > /dev/null
    exit 1
  fi
  RUN_DIR="$SOURCE_WT"
  popd > /dev/null
  
elif git fetch . "$WT_BRANCH:$SOURCE_BRANCH" 2>/dev/null; then
  # === 2b: source 仅 ref + worktree 已 fast-forward source → 直接更新 ref ===
  echo "Fast-forwarded $SOURCE_BRANCH to $WT_BRANCH HEAD"
  RUN_DIR="$WT_PATH"  # 当前 worktree 即为 ff 后等价代码
  SKIP_MERGE_TEST=true  # ff 等同已验证，无需 merge 后测试
  
else
  # === 2c: source 仅 ref + 非 ff → 临时 worktree 处理 ===
  TMP_WT=$(mktemp -d -t superpowers-merge-XXXXXX)
  trap "git worktree remove --force '$TMP_WT' 2>/dev/null; rm -rf '$TMP_WT'" EXIT
  
  git worktree add "$TMP_WT" "$SOURCE_BRANCH"
  pushd "$TMP_WT" > /dev/null
  if ! git merge --no-ff "$WT_BRANCH" -m "Merge $WT_BRANCH into $SOURCE_BRANCH"; then
    echo "Merge conflict in temporary worktree at $TMP_WT."
    echo "This is rare (non-ff with no active source worktree)."
    echo "Please cd to $TMP_WT to resolve, then reply 'continue' to resume finish."
    popd > /dev/null
    exit 1
  fi
  RUN_DIR="$TMP_WT"
  popd > /dev/null
fi

# === 运行测试（merge 结果）===
if [ "${SKIP_MERGE_TEST:-false}" != "true" ]; then
  pushd "$RUN_DIR" > /dev/null
  <test command>  # npm test / cargo test / pytest / go test ./...
  TEST_EXIT=$?
  popd > /dev/null
  
  if [ $TEST_EXIT -ne 0 ]; then
    echo "Tests failed after merge. Rolling back merge commit."
    (cd "$RUN_DIR" && git reset --hard HEAD~1)
    # 2c 情况下，trap 会清理临时 worktree
    exit 1
  fi
fi

# === Push 远程 source branch ===
pushd "$RUN_DIR" > /dev/null
if ! git push origin "$SOURCE_BRANCH"; then
  echo "Push rejected (likely non-ff: origin/$SOURCE_BRANCH has new commits)."
  echo "Please pull and resolve in $RUN_DIR, then reply 'continue' to resume finish."
  popd > /dev/null
  exit 1
fi
popd > /dev/null

# === 清理临时 worktree（仅 2c）===
if [ -n "${TMP_WT:-}" ] && [ -d "$TMP_WT" ]; then
  git worktree remove "$TMP_WT"
  trap - EXIT
fi

# === 清理当前 worktree（Step 5 既有逻辑）+ 删除分支 ===
```

**关键不变量**：
- 全流程**不执行** `cd $MAIN_ROOT && git checkout`
- 冲突 / push 失败时退出，等待用户回复 "continue" 后再调用 skill 续跑
- 2b（fast-forward）跳过 merge 后测试，因为代码组合与 worktree 已完全等价
````

- [ ] **Step 2: 自查**

Run:
```bash
grep -c "=== 2a:\|=== 2b:\|=== 2c:" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
grep -c "SKIP_MERGE_TEST" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
grep -c "trap.*EXIT" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
```
Expected: 第 1 行 >= 3，第 2 行 >= 2，第 3 行 >= 2

- [ ] **Step 3: Commit**

```bash
git add plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
git commit -m "feat(finishing): implement 3 merge paths (2a/2b/2c) with test + push + rollback"
```

---

## Task 5: references/source-resolution.md（新文件）

**Files:**
- Create: `plugins/superpowers-pro/skills/finishing-a-development-branch/references/source-resolution.md`

**目标:** 把 Task 2-4 的实现细节汇总成参考文档，让人能从 SKILL.md 跳转过来快速理解源分支解析与 3 种 merge 路径的设计原理。

- [ ] **Step 1: 创建文件，写入完整内容**

Create `plugins/superpowers-pro/skills/finishing-a-development-branch/references/source-resolution.md`:

````markdown
# Source Branch Resolution & Merge Path Decision

本文档详细说明 `finishing-a-development-branch` skill 在 auto 模式下如何决策合并目标和 merge 执行路径。

## 1. Source Branch 持久化机制

worktree 创建时由 `using-git-worktrees` skill Step 2.5 写入：

```bash
git config extensions.worktreeConfig true  # 一次性启用
git config --worktree superpowers.sourceBranch <branch>
git config --worktree superpowers.sourceCommit <sha>
```

**注意**：`extensions.worktreeConfig=true` 必须先启用，否则 `--worktree` 写入会落到共享 config，破坏元数据隔离。

**Fallback for git < 2.20**：写到 `.git/worktrees/<name>/superpowers-source` 文件（也跟随 worktree）。

## 2. 解析顺序（Step 3）

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | `git config --worktree superpowers.sourceBranch` | 标准路径 |
| 2 | `cat $(git rev-parse --git-path superpowers-source)` | git < 2.20 fallback |
| 3 | 暂停询问用户 | 老 worktree / 手动 git worktree add 创建 |

特殊值 `pr`：用户在 fallback 提示中输入 `pr`，表示放弃本地 merge，走 PR/MR 创建路径（详见 `pr-mr-creation.md`）。

## 3. Source 形态检测（Step 4 开头）

```bash
SOURCE_WT=$(git worktree list --porcelain | \
  awk -v src="refs/heads/$SOURCE_BRANCH" '
    /^worktree / { wt=$2 }
    /^branch / { if ($2 == src) print wt }
  ')
```

- `SOURCE_WT` 非空：source branch 在某个 worktree 内 active
- `SOURCE_WT` 空：source branch 仅是本地 ref，无 active worktree

## 4. 三种 Merge 路径

### 4.1 路径 2a：source 在 active worktree

**前提**：`SOURCE_WT` 非空

**逻辑**：
1. 校验 source worktree working tree 干净（否则暂停）
2. `pushd $SOURCE_WT`
3. `git merge --no-ff $WT_BRANCH`（失败 → 暂停等冲突解决）
4. `RUN_DIR=$SOURCE_WT`

**为什么**：被 checkout 的分支不能直接 `git update-ref` 或 `git push . HEAD:branch`，必须在该 worktree 内 merge。

### 4.2 路径 2b：source 仅 ref + worktree 已 fast-forward source

**前提**：`SOURCE_WT` 空，且 `git fetch . $WT_BRANCH:$SOURCE_BRANCH` 成功

**逻辑**：
1. `git fetch . $WT_BRANCH:$SOURCE_BRANCH` 直接更新 ref
2. `RUN_DIR=$WT_PATH`（worktree 自身即等价代码）
3. `SKIP_MERGE_TEST=true`（无新代码组合，跳过 merge 后测试）

**为什么**：fast-forward 不产生新 commit，source 与 worktree 完全等价；测试在 Step 1 已跑过。

**关于 `git fetch . src:dst`**：把当前仓库自己当成 remote，把 src 这条 ref 推送给 dst。当且仅当 dst 可以 fast-forward 到 src 时成功；否则失败（转走 2c）。

### 4.3 路径 2c：source 仅 ref + 非 ff

**前提**：`SOURCE_WT` 空，且 2b 的 fetch 失败

**逻辑**：
1. `mktemp -d` 创建临时目录
2. `trap` 注册 EXIT 时强制 cleanup
3. `git worktree add $TMP_WT $SOURCE_BRANCH`
4. `pushd $TMP_WT && git merge --no-ff $WT_BRANCH`（冲突 → 暂停）
5. `RUN_DIR=$TMP_WT`
6. 测试通过 + push 完成后 → `git worktree remove $TMP_WT` + 解除 trap

**为什么**：非 ff 必须真正执行 merge 产生 merge commit；source 没有 active worktree 时，必须借助一个工作树执行 merge。临时 worktree 比"在当前 worktree 切到 source"安全（不会污染当前 worktree 状态）。

## 5. 测试与回滚位置矩阵

| 路径 | RUN_DIR | merge 后测试 | 失败回滚 |
|------|---------|--------------|---------|
| 2a | `$SOURCE_WT` | 必须 | `git reset --hard HEAD~1` in `$SOURCE_WT` |
| 2b | `$WT_PATH` | 跳过 | 不适用（ref 更新可重做） |
| 2c | `$TMP_WT` | 必须 | `git reset --hard HEAD~1` in `$TMP_WT` + trap 清理 |

## 6. Push 行为

`git push origin $SOURCE_BRANCH`：

- 成功：进入 cleanup 阶段
- 失败（非 ff）：暂停，提示用户在 `$RUN_DIR` 中 `git pull` 解决后回复 "continue"

## 7. 关键不变量

| 不变量 | 实现 |
|--------|------|
| 主仓库 HEAD 永不被切换 | 不执行任何 `cd $MAIN_ROOT && git checkout` |
| 源分支决策不看主仓库状态 | 全程基于 worktree-local config |
| 冲突可被人工处理 | 暂停 + 明确提示 + 等待"continue" |
| 多 worktree 并行安全 | 每个 worktree 自带 source 元数据 |
````

- [ ] **Step 2: 自查 — 验证文件可被 SKILL.md 引用**

Run:
```bash
grep -c "references/source-resolution.md" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
wc -l plugins/superpowers-pro/skills/finishing-a-development-branch/references/source-resolution.md
```
Expected: 第 1 行 >= 1（SKILL.md 至少引用一次），第 2 行 > 80（内容完整）

- [ ] **Step 3: Commit**

```bash
git add plugins/superpowers-pro/skills/finishing-a-development-branch/references/source-resolution.md
git commit -m "docs(finishing): add source-resolution.md reference"
```

---

## Task 6: references/pr-mr-creation.md（新文件）

**Files:**
- Create: `plugins/superpowers-pro/skills/finishing-a-development-branch/references/pr-mr-creation.md`

**目标:** 文档化 PR/MR 创建的多平台通用方案（GitHub + GitLab），不依赖 `gh` / `glab` CLI。

- [ ] **Step 1: 创建文件，写入完整内容**

Create `plugins/superpowers-pro/skills/finishing-a-development-branch/references/pr-mr-creation.md`:

````markdown
# PR/MR Creation — Multi-Platform Strategy

`finishing-a-development-branch` skill 不调用任何 platform CLI（`gh` / `glab`），统一用 `git push` + URL 推导实现 GitHub Pull Request 和 GitLab Merge Request 的创建入口。

## 1. 适用位置

- **Step 3 fallback**：用户在源分支询问中输入 `pr` 时
- **Interactive Option 2**：用户选择 "Push and create a PR/MR" 时

## 2. 实现伪代码

```bash
# 1. 推送分支
git push -u origin "$BRANCH"

# 2. 解析 origin URL 规范化为 https
REMOTE_URL=$(git remote get-url origin)
WEB_URL=$(echo "$REMOTE_URL" | sed -E '
  s#^git@([^:]+):#https://\1/#;
  s#\.git$##;
')

# 3. 平台检测与 URL 拼接
case "$WEB_URL" in
  *github.com*|*github*)
    CREATE_URL="${WEB_URL}/compare/${BRANCH}?expand=1"
    PLATFORM="GitHub Pull Request"
    ;;
  *gitlab*)
    CREATE_URL="${WEB_URL}/-/merge_requests/new?merge_request[source_branch]=${BRANCH}"
    PLATFORM="GitLab Merge Request"
    ;;
  *)
    CREATE_URL=""
    PLATFORM="未知平台"
    ;;
esac

# 4. 输出
echo "Branch pushed: $BRANCH"
if [ -n "$CREATE_URL" ]; then
  echo "Create $PLATFORM at: $CREATE_URL"
else
  echo "Detected non-GitHub/GitLab remote. Please create PR/MR manually."
  echo "Remote URL: $REMOTE_URL"
fi
```

## 3. URL 推导规则

| 输入 origin URL | 输出 CREATE_URL |
|-----------------|----------------|
| `git@github.com:owner/repo.git` | `https://github.com/owner/repo/compare/<branch>?expand=1` |
| `https://github.com/owner/repo.git` | `https://github.com/owner/repo/compare/<branch>?expand=1` |
| `git@gitlab.com:group/repo.git` | `https://gitlab.com/group/repo/-/merge_requests/new?merge_request[source_branch]=<branch>` |
| `git@gitlab.company.com:team/repo.git` | `https://gitlab.company.com/team/repo/-/merge_requests/new?merge_request[source_branch]=<branch>` |
| `git@bitbucket.org:owner/repo.git` | （无识别）提示用户手动创建，显示原始 URL |

## 4. 取舍

| 维度 | 用 CLI（`gh` / `glab`） | 仅 push + URL（本方案） |
|------|------------------------|------------------------|
| PR/MR title/body 自动填 | 支持 | 不支持，用户在 Web UI 填 |
| 平台覆盖 | 需各装一个 CLI | 全平台统一（仅需 git） |
| 用户环境依赖 | gh/glab 安装 + 认证 | 仅 git remote 配置 |
| 失败模式 | CLI 调用失败需排查 | push 失败即报错，定位简单 |

**取舍结论**：用户在 Web UI 中填 title/body 是常见做法，不构成重大体验损失；换来跨平台一致性和零外部依赖。

## 5. 未来扩展（暂不实现）

若未来需要自动填 title/body，可在第 4 步末尾加 opportunistic 探测：

```bash
if command -v gh >/dev/null 2>&1 && [[ "$WEB_URL" == *github.com* ]]; then
  # 调用 gh pr create --fill 等
fi
```

当前 spec **不实现**此扩展（YAGNI）。

## 6. 测试场景

参见 `test-scenarios.md` 场景 11、12、13。
````

- [ ] **Step 2: 自查**

Run:
```bash
wc -l plugins/superpowers-pro/skills/finishing-a-development-branch/references/pr-mr-creation.md
grep -c "compare/\|merge_requests/new" plugins/superpowers-pro/skills/finishing-a-development-branch/references/pr-mr-creation.md
```
Expected: 第 1 行 > 60，第 2 行 >= 2

- [ ] **Step 3: Commit**

```bash
git add plugins/superpowers-pro/skills/finishing-a-development-branch/references/pr-mr-creation.md
git commit -m "docs(finishing): add pr-mr-creation.md multi-platform reference"
```

---

## Task 7: finishing Interactive Option 2 改造（去 `gh` 依赖）

**Files:**
- Modify: `plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md`

**目标:** interactive 模式 Option 2 "Push and Create PR" 改成通用 push + URL 输出，不依赖 `gh`。

- [ ] **Step 1: 定位现有 Option 2 代码块**

Run:
```bash
grep -n "Option 2: Push and Create PR\|gh pr create" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
```
Expected: 显示行号。

- [ ] **Step 2: 替换整段 Option 2**

将 "**Option 2: Push and Create PR**" 标题下的 12 行（含 gh pr create heredoc）替换为：

````markdown
**Option 2: Push and Create PR/MR**

通用方案，不依赖 `gh` / `glab` CLI。详见 `references/pr-mr-creation.md`。

```bash
git push -u origin "$WT_BRANCH"

REMOTE_URL=$(git remote get-url origin)
WEB_URL=$(echo "$REMOTE_URL" | sed -E 's#^git@([^:]+):#https://\1/#; s#\.git$##;')

case "$WEB_URL" in
  *github.com*|*github*)
    CREATE_URL="${WEB_URL}/compare/${WT_BRANCH}?expand=1"
    PLATFORM="GitHub Pull Request"
    ;;
  *gitlab*)
    CREATE_URL="${WEB_URL}/-/merge_requests/new?merge_request[source_branch]=${WT_BRANCH}"
    PLATFORM="GitLab Merge Request"
    ;;
  *)
    CREATE_URL=""
    PLATFORM="未识别平台"
    ;;
esac

echo "Branch pushed: $WT_BRANCH"
if [ -n "$CREATE_URL" ]; then
  echo "Create $PLATFORM at: $CREATE_URL"
else
  echo "Detected non-GitHub/GitLab remote. Please create PR/MR manually."
  echo "Remote URL: $REMOTE_URL"
fi
```

**Do NOT cleanup worktree** — user needs it for PR/MR iteration.
````

- [ ] **Step 3: 自查**

Run:
```bash
grep -c "gh pr create" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
grep -c "compare/.*expand=1" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
grep -c "merge_requests/new" plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
```
Expected: 第 1 行 == 0（已移除），第 2 行 >= 1，第 3 行 >= 1

- [ ] **Step 4: Commit**

```bash
git add plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
git commit -m "feat(finishing): replace gh pr create with multi-platform URL derivation"
```

---

## Task 8: references/test-scenarios.md（新文件）

**Files:**
- Create: `plugins/superpowers-pro/skills/finishing-a-development-branch/references/test-scenarios.md`

**目标:** 列出 spec 7.1 中 13 个测试场景的 setup / action / expected，作为手动验证清单和 evals/*.sh 的依据。

- [ ] **Step 1: 创建文件**

Create `plugins/superpowers-pro/skills/finishing-a-development-branch/references/test-scenarios.md`:

````markdown
# Test Scenarios for finishing-a-development-branch

13 个端到端场景，覆盖 spec 验收标准 A1-A9。每个场景给出 setup（如何构造 sandbox repo）、action（执行什么）、expected（验证 git state）。

对应的可执行 bash 脚本见 `../evals/*.sh`。

## 场景 1：基础路径

**Setup**：feature-A worktree active + 子任务 worktree from feature-A，子任务有 1 个新 commit

**Action**：在子任务 worktree 内执行 finish (auto mode)

**Expected**：
- feature-A worktree HEAD 多一个 merge commit
- 子任务分支被删除
- 子任务 worktree 目录被移除
- 主仓库 HEAD 不变
- origin/feature-A 被 push 更新

## 场景 2：主仓库 HEAD 不同（验收 A1, A2）

**Setup**：主仓库 checkout 在 master；feature-A 在 worktree-fA 中 active；子任务 worktree 从 feature-A 创建

**Action**：在子任务 worktree 内执行 finish (auto mode)

**Expected**：
- merge 结果落在 worktree-fA（feature-A），不是 master
- 主仓库 HEAD 仍是 master（验证 A2）
- 主仓库 working tree 与 finish 前 byte-for-byte 一致

## 场景 3：source 无 active worktree（fast-forward）

**Setup**：仅 `git branch feature-A` 创建 ref（无 worktree）；子任务 worktree 从 feature-A 创建

**Action**：在子任务 worktree 内执行 finish (auto mode)

**Expected**：
- 走路径 2b：`git fetch . $WT_BRANCH:$SOURCE_BRANCH` 成功
- feature-A ref 移到子任务 HEAD
- 跳过 merge 后测试
- 子任务 worktree cleanup

## 场景 4：两个子任务冲突（验收 A3）

**Setup**：feature-A worktree + 子任务1（改 file.txt 第 1 行）+ 子任务2（改 file.txt 第 1 行）

**Action**：依次 finish 子任务1（成功），然后 finish 子任务2

**Expected**：
- 子任务2 在 feature-A worktree 内 merge 时冲突
- 输出包含 "Merge conflict detected" + 冲突文件列表 + "reply 'continue'"
- 退出码 != 0
- feature-A worktree 处于 unmerged 状态（用户可以解决）

## 场景 5：老 worktree fallback（验收 A4）

**Setup**：手动 `git worktree add` 创建 worktree（没有 Step 2.5 元数据）

**Action**：在该 worktree 内执行 finish (auto mode)

**Expected**：
- Step 3 读不到 worktree config
- 输出 "未找到此 worktree 的源分支元数据" + 候选推断
- 暂停等待用户输入

## 场景 6：/init 路径（验收 A5）

**Setup**：新仓库 + 1 个 commit，无源分支

**Action**：执行 finish (auto mode)

**Expected**：
- Step 4 检测 SOURCE_BRANCH 为空 → push only 路径
- `git push -u origin <branch>` 执行
- 不报错

## 场景 7：push 拒绝（非 ff）

**Setup**：feature-A worktree + 子任务 worktree，origin/feature-A 远程领先 1 个 commit

**Action**：finish 子任务

**Expected**：
- 本地 merge 成功
- push 失败，输出 "Push rejected" + "请 pull 后回复 'continue'"
- 退出码 != 0

## 场景 8：source 脏工作树

**Setup**：feature-A worktree 有未提交改动 + 子任务 worktree

**Action**：finish 子任务

**Expected**：
- 输出 "Source worktree at ... has uncommitted changes"
- 不执行 merge
- 退出码 != 0

## 场景 9：测试失败回滚

**Setup**：feature-A worktree + 子任务有改动 + 项目有可跑测试，且 merge 后测试会失败

**Action**：finish 子任务

**Expected**：
- merge 完成
- 测试失败
- 输出 "Tests failed after merge. Rolling back merge commit."
- feature-A worktree HEAD 回到 merge 前
- 退出码 != 0

## 场景 10：git < 2.20 fallback（验收 A6）

**Setup**：模拟 git < 2.20（如用 docker 或重命名 git 实现）+ 走 Step 2.5

**Action**：创建 worktree + finish

**Expected**：
- Step 2.5 落到 `.git/worktrees/<name>/superpowers-source` 文件
- finish Step 3 从文件读 source

## 场景 11：GitHub PR URL（验收 A7）

**Setup**：origin 为 `git@github.com:owner/repo.git`

**Action**：fallback 输入 `pr` 或 interactive Option 2

**Expected**：
- 输出包含 `https://github.com/owner/repo/compare/<branch>?expand=1`

## 场景 12：GitLab MR URL（验收 A8）

**Setup**：origin 为 `git@gitlab.com:group/repo.git`

**Action**：同 11

**Expected**：
- 输出包含 `https://gitlab.com/group/repo/-/merge_requests/new?merge_request[source_branch]=<branch>`

## 场景 13：未识别平台 fallback（验收 A9）

**Setup**：origin 为 `git@bitbucket.org:owner/repo.git`

**Action**：同 11

**Expected**：
- 输出包含 "non-GitHub/GitLab remote. Please create PR/MR manually."
- 输出原始 Remote URL
- 不阻塞 push（push 已成功）
````

- [ ] **Step 2: 自查**

Run:
```bash
grep -c "^## 场景" plugins/superpowers-pro/skills/finishing-a-development-branch/references/test-scenarios.md
```
Expected: == 13

- [ ] **Step 3: Commit**

```bash
git add plugins/superpowers-pro/skills/finishing-a-development-branch/references/test-scenarios.md
git commit -m "docs(finishing): add test-scenarios.md (13 scenarios)"
```

---

## Task 9: evals/*.sh — 关键场景的端到端 bash 测试

**Files:**
- Create: `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/01-basic-merge.sh`
- Create: `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/02-main-repo-on-other-branch.sh`
- Create: `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/05-old-worktree-fallback.sh`
- Create: `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/11-github-pr-url.sh`
- Create: `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/12-gitlab-mr-url.sh`
- Create: `plugins/superpowers-pro/skills/finishing-a-development-branch/evals/13-unknown-platform.sh`

**目标:** 6 个 bash 脚本覆盖最关键的验收标准（A1, A2, A4, A7, A8, A9）。每个脚本是独立 sandbox + 可重复执行。

**说明:** evals 脚本不是 SKILL.md 的直接执行（SKILL.md 是给 agent 看的指令），而是把 SKILL.md 中描述的 bash 命令提取为可独立运行的脚本，用 git plumbing 验证关键 git state。

- [ ] **Step 1: 写 01-basic-merge.sh（场景 1，基础路径）**

Create `evals/01-basic-merge.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Scenario 1: 基础路径
# Setup: feature-A worktree active + 子任务 worktree from feature-A，子任务有 1 个新 commit
# Expected: feature-A 收到 merge commit；子任务 worktree/branch cleanup；主仓库 HEAD 不变

TMP=$(mktemp -d -t fin-test-01-XXXX)
trap "rm -rf $TMP" EXIT
cd "$TMP"

# === Setup remote (bare repo) ===
git init --bare remote.git
git clone remote.git main
cd main
git checkout -b master 2>/dev/null || true
echo "init" > README.md
git add . && git commit -m "init"
git push -u origin master

# 创建 feature-A 分支 + 远程推送
git checkout -b feature-A
echo "feature-A base" >> README.md
git commit -am "feature-A base"
git push -u origin feature-A

# 切回 master 保持主仓库在 master
git checkout master

# 在 .worktrees/feature-A 拉出 feature-A worktree
git worktree add ../wt-feature-A feature-A

# 模拟 Step 2.5: 在子任务 worktree 写元数据
git worktree add -b task-1 ../wt-task-1 feature-A
cd ../wt-task-1
git config extensions.worktreeConfig true
git config --worktree superpowers.sourceBranch feature-A
git config --worktree superpowers.sourceCommit "$(git rev-parse feature-A)"

# 子任务做 1 个 commit
echo "task-1 work" >> README.md
git commit -am "task-1: do work"

# === Action: 执行 auto finish 流程的核心逻辑 ===
SOURCE_BRANCH=$(git config --worktree superpowers.sourceBranch)
WT_BRANCH=$(git branch --show-current)

SOURCE_WT=$(git worktree list --porcelain | \
  awk -v src="refs/heads/$SOURCE_BRANCH" '
    /^worktree / { wt=$2 }
    /^branch / { if ($2 == src) print wt }
  ')

[ -n "$SOURCE_WT" ] || { echo "FAIL: source worktree not found"; exit 1; }

pushd "$SOURCE_WT" > /dev/null
git merge --no-ff "$WT_BRANCH" -m "Merge $WT_BRANCH into $SOURCE_BRANCH"
popd > /dev/null

# cleanup
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
git worktree remove "$SOURCE_WT/../wt-task-1" 2>/dev/null || \
  git worktree remove "../wt-task-1"
git branch -D task-1

# === Assert ===
# A. feature-A worktree HEAD 是 merge commit
cd ../wt-feature-A
HEAD_MSG=$(git log -1 --pretty=%s)
echo "$HEAD_MSG" | grep -q "Merge task-1 into feature-A" || \
  { echo "FAIL: feature-A HEAD is not merge commit, got: $HEAD_MSG"; exit 1; }

# B. 主仓库 HEAD 仍是 master
cd "$MAIN_ROOT"
[ "$(git branch --show-current)" = "master" ] || \
  { echo "FAIL: main repo HEAD changed"; exit 1; }

# C. task-1 worktree 被移除
[ ! -d ../wt-task-1 ] || { echo "FAIL: task-1 worktree not removed"; exit 1; }

echo "PASS: 01-basic-merge"
```

- [ ] **Step 2: 跑 01 验证脚本本身能跑通**

Run:
```bash
chmod +x plugins/superpowers-pro/skills/finishing-a-development-branch/evals/01-basic-merge.sh
bash plugins/superpowers-pro/skills/finishing-a-development-branch/evals/01-basic-merge.sh
```
Expected: 最后一行 "PASS: 01-basic-merge"，退出码 0

- [ ] **Step 3: 写 02-main-repo-on-other-branch.sh（场景 2，关键验收 A1+A2）**

Create `evals/02-main-repo-on-other-branch.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Scenario 2: 主仓库 HEAD ≠ source branch（验收 A1 + A2）
# Setup: 主仓库在 master；feature-A 在 wt-feature-A 中；子任务 worktree 从 feature-A 创建
# Expected: merge 落在 feature-A；主仓库 HEAD/working tree 完全不变

TMP=$(mktemp -d -t fin-test-02-XXXX)
trap "rm -rf $TMP" EXIT
cd "$TMP"

git init --bare remote.git
git clone remote.git main
cd main
echo "init" > README.md
git add . && git commit -m "init"
git push -u origin master 2>/dev/null || { git checkout -b master; git push -u origin master; }

git checkout -b feature-A
echo "base" >> README.md
git commit -am "feature-A base"
git push -u origin feature-A

git checkout master  # 主仓库停在 master

git worktree add ../wt-feature-A feature-A
git worktree add -b task-1 ../wt-task-1 feature-A
cd ../wt-task-1
git config extensions.worktreeConfig true
git config --worktree superpowers.sourceBranch feature-A

echo "task work" >> README.md
git commit -am "task-1 work"

# 记录主仓库快照
MAIN_HEAD_BEFORE=$(git -C ../main rev-parse HEAD)
MAIN_BRANCH_BEFORE=$(git -C ../main branch --show-current)
MAIN_TREE_BEFORE=$(cd ../main && git ls-files -s | sort | shasum)

# === Action ===
SOURCE_BRANCH=$(git config --worktree superpowers.sourceBranch)
SOURCE_WT=$(git worktree list --porcelain | \
  awk -v src="refs/heads/$SOURCE_BRANCH" '/^worktree / { wt=$2 } /^branch / { if ($2 == src) print wt }')

pushd "$SOURCE_WT" > /dev/null
git merge --no-ff task-1 -m "Merge"
popd > /dev/null

# === Assert ===
# A1: feature-A HEAD 是 merge commit
[ "$(git -C ../wt-feature-A log -1 --pretty=%s)" = "Merge" ] || \
  { echo "FAIL A1: feature-A HEAD wrong"; exit 1; }

# A2: 主仓库不变
MAIN_HEAD_AFTER=$(git -C ../main rev-parse HEAD)
MAIN_BRANCH_AFTER=$(git -C ../main branch --show-current)
MAIN_TREE_AFTER=$(cd ../main && git ls-files -s | sort | shasum)

[ "$MAIN_HEAD_BEFORE" = "$MAIN_HEAD_AFTER" ] || { echo "FAIL A2: main HEAD changed"; exit 1; }
[ "$MAIN_BRANCH_BEFORE" = "$MAIN_BRANCH_AFTER" ] || { echo "FAIL A2: main branch changed"; exit 1; }
[ "$MAIN_TREE_BEFORE" = "$MAIN_TREE_AFTER" ] || { echo "FAIL A2: main tree changed"; exit 1; }

echo "PASS: 02-main-repo-on-other-branch"
```

- [ ] **Step 4: 跑 02 验证**

Run:
```bash
chmod +x plugins/superpowers-pro/skills/finishing-a-development-branch/evals/02-main-repo-on-other-branch.sh
bash plugins/superpowers-pro/skills/finishing-a-development-branch/evals/02-main-repo-on-other-branch.sh
```
Expected: "PASS: 02-main-repo-on-other-branch"

- [ ] **Step 5: 写 05-old-worktree-fallback.sh（场景 5，验收 A4）**

Create `evals/05-old-worktree-fallback.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Scenario 5: 老 worktree fallback（无元数据）
# Setup: 手动 git worktree add 创建（无 Step 2.5 元数据）
# Expected: Step 3 读不到 config → 触发 fallback 提示

TMP=$(mktemp -d -t fin-test-05-XXXX)
trap "rm -rf $TMP" EXIT
cd "$TMP"

git init main
cd main
echo "init" > README.md
git add . && git commit -m "init"
git checkout -b master 2>/dev/null || true
git checkout -b feature-A
echo "base" >> README.md
git commit -am "feature-A base"
git checkout master

# 手动 worktree add（不写元数据）
git worktree add -b legacy-task ../wt-legacy feature-A
cd ../wt-legacy
echo "work" >> README.md
git commit -am "legacy task work"

# === Action: 执行 Step 3 读取逻辑 ===
SOURCE=$(git config --worktree superpowers.sourceBranch 2>/dev/null || echo "")
if [ -z "$SOURCE" ]; then
  SOURCE_FILE="$(git rev-parse --git-path superpowers-source)"
  [ -f "$SOURCE_FILE" ] && SOURCE=$(cat "$SOURCE_FILE")
fi

# === Assert: SOURCE 为空，说明 fallback 会触发 ===
[ -z "$SOURCE" ] || { echo "FAIL: SOURCE should be empty, got: $SOURCE"; exit 1; }

# 候选推断 (mimic Step 3 fallback)
CANDIDATE=$(git merge-base HEAD main 2>/dev/null \
            || git merge-base HEAD master 2>/dev/null \
            || echo "未知")

[ -n "$CANDIDATE" ] && [ "$CANDIDATE" != "未知" ] || \
  { echo "FAIL: no candidate inferred"; exit 1; }

echo "PASS: 05-old-worktree-fallback (SOURCE empty, candidate=$CANDIDATE)"
```

- [ ] **Step 6: 跑 05 验证**

Run:
```bash
chmod +x plugins/superpowers-pro/skills/finishing-a-development-branch/evals/05-old-worktree-fallback.sh
bash plugins/superpowers-pro/skills/finishing-a-development-branch/evals/05-old-worktree-fallback.sh
```
Expected: "PASS: 05-old-worktree-fallback (SOURCE empty, candidate=...)"

- [ ] **Step 7: 写 11-github-pr-url.sh（场景 11）**

Create `evals/11-github-pr-url.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Scenario 11: GitHub PR URL（验收 A7）
# Setup: origin = git@github.com:owner/repo.git
# Expected: 输出 https://github.com/owner/repo/compare/<branch>?expand=1

TMP=$(mktemp -d -t fin-test-11-XXXX)
trap "rm -rf $TMP" EXIT
cd "$TMP"

git init repo
cd repo
git remote add origin git@github.com:owner/repo.git
BRANCH="feature-x"
git checkout -b "$BRANCH" 2>/dev/null || true

# === Action: 执行 4.6 PR/MR URL 推导 ===
REMOTE_URL=$(git remote get-url origin)
WEB_URL=$(echo "$REMOTE_URL" | sed -E 's#^git@([^:]+):#https://\1/#; s#\.git$##;')

case "$WEB_URL" in
  *github.com*|*github*)
    CREATE_URL="${WEB_URL}/compare/${BRANCH}?expand=1"
    ;;
  *) CREATE_URL=""; ;;
esac

# === Assert ===
EXPECTED="https://github.com/owner/repo/compare/feature-x?expand=1"
[ "$CREATE_URL" = "$EXPECTED" ] || \
  { echo "FAIL: expected '$EXPECTED', got '$CREATE_URL'"; exit 1; }

echo "PASS: 11-github-pr-url ($CREATE_URL)"
```

- [ ] **Step 8: 跑 11 验证**

Run:
```bash
chmod +x plugins/superpowers-pro/skills/finishing-a-development-branch/evals/11-github-pr-url.sh
bash plugins/superpowers-pro/skills/finishing-a-development-branch/evals/11-github-pr-url.sh
```
Expected: "PASS: 11-github-pr-url (https://github.com/owner/repo/compare/feature-x?expand=1)"

- [ ] **Step 9: 写 12-gitlab-mr-url.sh（场景 12）**

Create `evals/12-gitlab-mr-url.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Scenario 12: GitLab MR URL（验收 A8）
# Setup: origin = git@gitlab.com:group/repo.git
# Expected: 输出 https://gitlab.com/group/repo/-/merge_requests/new?merge_request[source_branch]=<branch>

TMP=$(mktemp -d -t fin-test-12-XXXX)
trap "rm -rf $TMP" EXIT
cd "$TMP"

git init repo
cd repo
git remote add origin git@gitlab.com:group/repo.git
BRANCH="feature-y"
git checkout -b "$BRANCH" 2>/dev/null || true

REMOTE_URL=$(git remote get-url origin)
WEB_URL=$(echo "$REMOTE_URL" | sed -E 's#^git@([^:]+):#https://\1/#; s#\.git$##;')

case "$WEB_URL" in
  *gitlab*)
    CREATE_URL="${WEB_URL}/-/merge_requests/new?merge_request[source_branch]=${BRANCH}"
    ;;
  *) CREATE_URL=""; ;;
esac

EXPECTED="https://gitlab.com/group/repo/-/merge_requests/new?merge_request[source_branch]=feature-y"
[ "$CREATE_URL" = "$EXPECTED" ] || \
  { echo "FAIL: expected '$EXPECTED', got '$CREATE_URL'"; exit 1; }

echo "PASS: 12-gitlab-mr-url ($CREATE_URL)"
```

- [ ] **Step 10: 跑 12 验证**

Run:
```bash
chmod +x plugins/superpowers-pro/skills/finishing-a-development-branch/evals/12-gitlab-mr-url.sh
bash plugins/superpowers-pro/skills/finishing-a-development-branch/evals/12-gitlab-mr-url.sh
```
Expected: "PASS: 12-gitlab-mr-url (...)"

- [ ] **Step 11: 写 13-unknown-platform.sh（场景 13）**

Create `evals/13-unknown-platform.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Scenario 13: 未识别平台 fallback（验收 A9）
# Setup: origin = git@bitbucket.org:owner/repo.git
# Expected: CREATE_URL 为空，触发 fallback 提示

TMP=$(mktemp -d -t fin-test-13-XXXX)
trap "rm -rf $TMP" EXIT
cd "$TMP"

git init repo
cd repo
git remote add origin git@bitbucket.org:owner/repo.git
BRANCH="feature-z"
git checkout -b "$BRANCH" 2>/dev/null || true

REMOTE_URL=$(git remote get-url origin)
WEB_URL=$(echo "$REMOTE_URL" | sed -E 's#^git@([^:]+):#https://\1/#; s#\.git$##;')

case "$WEB_URL" in
  *github.com*|*github*)
    CREATE_URL="${WEB_URL}/compare/${BRANCH}?expand=1"
    ;;
  *gitlab*)
    CREATE_URL="${WEB_URL}/-/merge_requests/new?merge_request[source_branch]=${BRANCH}"
    ;;
  *) CREATE_URL=""; ;;
esac

[ -z "$CREATE_URL" ] || \
  { echo "FAIL: expected empty CREATE_URL, got '$CREATE_URL'"; exit 1; }

echo "PASS: 13-unknown-platform (CREATE_URL empty, REMOTE_URL=$REMOTE_URL)"
```

- [ ] **Step 12: 跑 13 验证**

Run:
```bash
chmod +x plugins/superpowers-pro/skills/finishing-a-development-branch/evals/13-unknown-platform.sh
bash plugins/superpowers-pro/skills/finishing-a-development-branch/evals/13-unknown-platform.sh
```
Expected: "PASS: 13-unknown-platform (CREATE_URL empty, REMOTE_URL=git@bitbucket.org:owner/repo.git)"

- [ ] **Step 13: Commit 全部 evals**

```bash
git add plugins/superpowers-pro/skills/finishing-a-development-branch/evals/
git commit -m "test(finishing): add 6 eval scripts covering A1/A2/A4/A7/A8/A9"
```

---

## Task 10: 4 个命令 Step 8 描述同步

**Files:**
- Modify: `plugins/superpowers-pro/commands/feat.md`
- Modify: `plugins/superpowers-pro/commands/fix.md`
- Modify: `plugins/superpowers-pro/commands/refactor.md`
- Modify: `plugins/superpowers-pro/commands/init.md`

**目标:** 把 4 个命令文件中 Step 8 FINISH 部分的"合并到 <初始分支>"措辞改成"合并到 <源分支>"，并在进度总览也同步。

- [ ] **Step 1: feat.md 修改**

定位行：
```bash
grep -n "初始分支\|<初始分支>" plugins/superpowers-pro/commands/feat.md
```

把两处出现：
- 进度总览 Step 8 描述 `Step 8/8  FINISH        □  合并到初始分支 + 推送 + 清理`
- Step 8/8 末尾 `━━━ [✓] Step 8/8: FINISH — 已合并到 <初始分支> 并推送`

改成"源分支"和 `<源分支>`。

- [ ] **Step 2: 同样修改 fix.md / refactor.md / init.md**

对 fix.md、refactor.md、init.md 重复 Step 1。注意：
- init.md 的 Step 8 描述是 `初始提交 + 推送`，不涉及"初始分支"，**保持不变**。但要检查它的进度总览有无"初始分支"措辞。

Run:
```bash
grep -n "初始分支" plugins/superpowers-pro/commands/init.md
```
Expected: 若 0，跳过 init.md；否则同样替换。

- [ ] **Step 3: 自查**

Run:
```bash
grep -rn "初始分支" plugins/superpowers-pro/commands/
```
Expected: 0（全部已替换）

- [ ] **Step 4: Commit**

```bash
git add plugins/superpowers-pro/commands/feat.md plugins/superpowers-pro/commands/fix.md plugins/superpowers-pro/commands/refactor.md plugins/superpowers-pro/commands/init.md
git commit -m "docs(commands): sync Step 8 description 'initial branch' -> 'source branch'"
```

---

## Task 11: 版本号 + CHANGELOG

**Files:**
- Modify: `plugins/superpowers-pro/.claude-plugin/plugin.json`
- Modify: `plugins/superpowers-pro/CHANGELOG.md`

**目标:** SemVer minor bump（新增源分支感知能力是功能增强），CHANGELOG 添加条目。

- [ ] **Step 1: 读取当前版本**

Run:
```bash
cat plugins/superpowers-pro/.claude-plugin/plugin.json | grep version
```

记录当前版本号（例如 0.11.0）。

- [ ] **Step 2: bump 到 0.12.0**

修改 `plugins/superpowers-pro/.claude-plugin/plugin.json` 中的 `"version"` 字段，从 `"0.11.0"` 改为 `"0.12.0"`（如果当前版本不是 0.11.0，bump 对应的 minor 位 +1）。

- [ ] **Step 3: 更新 CHANGELOG.md**

在 `plugins/superpowers-pro/CHANGELOG.md` 的 `## [Unreleased]` 章节下加入：

```markdown
### Added
- `using-git-worktrees` Step 2.5：worktree 创建时持久化源分支元数据到 per-worktree git config
- `finishing-a-development-branch` 源分支感知 merge：自动检测 source branch 形态（active worktree / 仅 ref），选择正确的 merge 路径，主仓库 HEAD 全程不变
- `finishing-a-development-branch` PR/MR 创建支持 GitHub + GitLab（去 `gh` 硬依赖）
- `references/source-resolution.md` 源分支解析详细规则
- `references/pr-mr-creation.md` PR/MR 多平台方案
- `references/test-scenarios.md` + `evals/*.sh` 13 个测试场景

### Changed
- `finishing-a-development-branch` Step 3："Determine Base Branch"（git merge-base 推断）→ "Determine Source Branch"（读 worktree 元数据）
- `finishing-a-development-branch` Step 4 auto：移除所有 `cd $MAIN_ROOT && git checkout`
- Interactive Option 2："gh pr create" → 通用 push + URL 输出
- `/feat`、`/fix`、`/refactor` 命令 Step 8 描述："合并到初始分支" → "合并到源分支"
```

- [ ] **Step 4: 自查**

Run:
```bash
grep version plugins/superpowers-pro/.claude-plugin/plugin.json
grep "源分支感知\|source-resolution" plugins/superpowers-pro/CHANGELOG.md
```
Expected: 版本号已 bump；CHANGELOG 包含新条目

- [ ] **Step 5: Commit**

```bash
git add plugins/superpowers-pro/.claude-plugin/plugin.json plugins/superpowers-pro/CHANGELOG.md
git commit -m "chore(superpowers-pro): bump to 0.12.0 with source-branch-safe finish"
```

---

## Self-Review

**1. Spec 覆盖检查**：

| Spec 章节 | Task 覆盖 |
|----------|----------|
| 4.3 using-git-worktrees Step 2.5 | Task 1 ✓ |
| 4.4 finishing Step 3 重写 | Task 2 ✓ |
| 4.4 finishing Step 4 auto 重写 | Task 3 + Task 4 ✓ |
| 4.4.1 测试与回滚位置矩阵 | Task 4 step 1 实现 + Task 5 文档化 ✓ |
| 4.5 /init 工作流 | Task 3 Step 2 中 "B. /init 工作流" 路径 ✓ |
| 4.6 PR/MR 多平台方案 | Task 6 + Task 7 ✓ |
| 7.1 测试场景 1-13 | Task 8（全部 13 个）+ Task 9（6 个 eval 脚本覆盖关键的 A1/A2/A4/A7/A8/A9）✓ |
| 8. 实施清单 Phase 1-7 | Task 1-10 完整覆盖 ✓ |
| 11. 验收标准 A1-A9 | evals 覆盖 A1/A2/A4/A7/A8/A9（核心 6 项）；A3/A5/A6/A8 由 test-scenarios.md 手动验证清单覆盖 |

**2. Placeholder 扫描**：未发现 "TBD"/"TODO"/"implement later"。所有 bash 代码块包含完整可运行内容。

**3. 类型/命名一致性**：
- `superpowers.sourceBranch` 和 `superpowers.sourceCommit` 在 Task 1/2/5 中一致
- `SOURCE_BRANCH` / `SOURCE_WT` / `WT_BRANCH` / `WT_PATH` / `RUN_DIR` / `TMP_WT` 在 Task 3/4/5 中一致
- 文件路径 `references/source-resolution.md` / `references/pr-mr-creation.md` / `references/test-scenarios.md` / `evals/*.sh` 在 File Structure / 各 task / Self-Review 中一致

**4. 已知 gap**：
- 验收 A3（多 worktree 串行冲突）/ A5（/init 路径）/ A6（git < 2.20）由 test-scenarios.md 描述 + 手动执行覆盖，未自动化 eval 脚本。理由：A3 需要交互冲突解决，A6 需要 git 版本切换环境，自动化收益低 ROI 低。
- evals 脚本是"独立 sandbox 验证 git plumbing 行为"，不直接执行 SKILL.md。SKILL.md 改动的端到端验证仍需手动按 test-scenarios.md 走一遍。

---

## Execution Handoff

Plan complete and saved to `docs/superpowers-pro/plans/2026-06-04-finishing-skill-source-branch-safety.md`. Execute using superpowers-pro:subagent-driven-development.
