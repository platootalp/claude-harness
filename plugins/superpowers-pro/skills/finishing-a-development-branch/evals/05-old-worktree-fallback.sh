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
