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
  awk -v src="refs/heads/$SOURCE_BRANCH" '/^worktree / { wt=$0; sub(/^worktree /, "", wt) } /^branch / { if ($2 == src) print wt }')

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
