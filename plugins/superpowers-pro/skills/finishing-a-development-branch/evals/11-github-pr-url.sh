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
# 创建一个 commit 以便 checkout -b 成功
echo "init" > README.md
git add . && git commit -m "init"
git checkout -b "$BRANCH"

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
