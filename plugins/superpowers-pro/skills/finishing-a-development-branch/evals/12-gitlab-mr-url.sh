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
echo "init" > README.md
git add . && git commit -m "init"
git checkout -b "$BRANCH"

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
