---
name: git-workflow
description: Essential Git commands, GitHub CLI (gh) operations, and version control workflows for branching, collaboration, CI checks, and API queries. Use when working with git, GitHub, PRs, CI, or version control.
---

# Git Workflow

Git CLI and GitHub CLI (gh) reference for version control and collaboration.

## Git CLI

### Initial Setup

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git init
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git custom-name
```

### Basic Workflow

```bash
git status
git add file.txt
git add .
git add -A
git commit -m "Commit message"
git commit -am "Message"
git commit --amend -m "New message"
git commit --amend --no-edit
```

### Viewing Changes

```bash
git diff
git diff --staged
git diff file.txt
git diff commit1 commit2
```

### Branching & Merging

```bash
git branch
git branch -a
git branch feature-name
git checkout feature-name
git switch feature-name
git checkout -b feature-name
git switch -c feature-name
git branch -d branch-name
git branch -D branch-name
git branch -m old-name new-name
git merge feature-name
git merge --no-ff feature-name
git merge --abort
git diff --name-only --diff-filter=U
```

### Remote Operations

```bash
git remote -v
git remote add origin https://github.com/user/repo.git
git remote set-url origin https://github.com/user/new-repo.git
git remote remove origin
git fetch origin
git pull
git pull --rebase
git push
git push -u origin branch-name
git push --force-with-lease
```

### History & Logs

```bash
git log
git log --oneline
git log --graph --oneline --all
git log -5
git log --author="Name"
git log --since="2 weeks ago"
git log -- file.txt
git log --grep="bug fix"
git log -S "function_name"
git blame file.txt
git bisect start
git bisect bad
git bisect good commit-hash
```

### Undoing Changes

```bash
git restore file.txt
git restore .
git restore --staged file.txt
git reset
git reset --soft HEAD~1
git reset --hard HEAD~1
git revert commit-hash
git reset --hard commit-hash
```

### Stashing

```bash
git stash
git stash save "Work in progress"
git stash list
git stash apply
git stash pop
git stash apply stash@{2}
git stash drop stash@{0}
git stash clear
```

### Rebasing

```bash
git rebase main
git rebase -i HEAD~3
git rebase --continue
git rebase --skip
git rebase --abort
```

### Tags

```bash
git tag
git tag v1.0.0
git tag -a v1.0.0 -m "Version 1.0.0"
git tag v1.0.0 commit-hash
git push origin v1.0.0
git push --tags
git tag -d v1.0.0
git push origin --delete v1.0.0
```

### Advanced Operations

```bash
git cherry-pick commit-hash
git cherry-pick -n commit-hash
git submodule add https://github.com/user/repo.git path/
git submodule init
git submodule update
git clone --recursive https://github.com/user/repo.git
git clean -n
git clean -f
git clean -fd
git clean -fdx
```

## GitHub CLI (gh)

### Pull Requests & CI

```bash
gh pr checks 55 --repo owner/repo
gh run list --repo owner/repo --limit 10
gh run view <run-id> --repo owner/repo
gh run view <run-id> --repo owner/repo --log-failed
```

### API for Advanced Queries

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

### JSON Output

```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

## Common Workflows

**Feature branch:**
```bash
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature"
git push -u origin feature/new-feature
# Create PR, then after merge:
git checkout main && git pull && git branch -d feature/new-feature
```

**Hotfix:**
```bash
git checkout main && git pull
git checkout -b hotfix/critical-bug
git commit -am "Fix critical bug"
git push -u origin hotfix/critical-bug
```

**Syncing fork:**
```bash
git remote add upstream https://github.com/original/repo.git
git fetch upstream
git checkout main && git merge upstream/main && git push origin main
```

## Tips

- Commit often, perfect later (interactive rebase)
- Write meaningful commit messages
- Never force push to shared branches
- Use `--force-with-lease` instead of `--force`
- Use feature branches, not main

## Documentation

Official docs: https://git-scm.com/doc
Pro Git book: https://git-scm.com/book