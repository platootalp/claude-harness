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
# 用 sub() 而非 $2，保留路径中的空格
SOURCE_WT=$(git worktree list --porcelain | \
  awk -v src="refs/heads/$SOURCE_BRANCH" '
    /^worktree / { wt=$0; sub(/^worktree /, "", wt) }
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
