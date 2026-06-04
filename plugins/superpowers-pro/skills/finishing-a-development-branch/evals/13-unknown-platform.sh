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
echo "init" > README.md
git add . && git commit -m "init"
git checkout -b "$BRANCH"

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
