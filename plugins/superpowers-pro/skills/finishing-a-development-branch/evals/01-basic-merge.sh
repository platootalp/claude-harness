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
    /^worktree / { wt=$0; sub(/^worktree /, "", wt) }
    /^branch / { if ($2 == src) print wt }
  ')

[ -n "$SOURCE_WT" ] || { echo "FAIL: source worktree not found"; exit 1; }

pushd "$SOURCE_WT" > /dev/null
git merge --no-ff "$WT_BRANCH" -m "Merge $WT_BRANCH into $SOURCE_BRANCH"
popd > /dev/null

# cleanup
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
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
