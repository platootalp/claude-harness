# finishing-a-development-branch 源分支安全改进设计

**日期**：2026-06-04
**作者**：platootalp + Claude
**状态**：草案
**影响范围**：`plugins/superpowers-pro/skills/finishing-a-development-branch/`、`plugins/superpowers-pro/skills/using-git-worktrees/`

---

## 1. 问题陈述

### 1.1 用户报告

> 现在 finishing-a-development-branch 的自动流程很容易合并到我不想合并的分支，因为本地我有多个分支，容易切来切去，然后合并到了不想合并的分支。同时现在的开发模式基本是多个远程 feature 分支并行开发，然后本地有多个 feature，每个 feature 多个工作树，这样我本地不能切来切去了，是否需要优化。

### 1.2 现状分析

当前 `finishing-a-development-branch` 在 auto 模式下的合并目标推断逻辑：

```bash
# Step 3: Determine Base Branch
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null

# Step 4 (auto): Execute Finish
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
git checkout <base-branch>
git pull
git merge <feature-branch>
```

存在两个根本缺陷：

1. **base branch 推断不准**：`git merge-base HEAD main/master` 只能找到与 main/master 的共同祖先，无法识别"从 feature-A 拉出的 worktree 应该合并回 feature-A"。
2. **依赖主仓库 HEAD**：`cd $MAIN_ROOT && git checkout <base-branch>` 会切换主仓库分支，污染用户在主仓库的当前工作；同时若主仓库 HEAD 被切到其他分支，整个流程的"初始分支"判断会跑偏。

### 1.3 新工作模式约束

用户报告的实际工作模式：

- 远程多个 feature 分支并行（`origin/feature-A`, `origin/feature-B`）
- 本地每个 feature 多个 worktree（`.worktrees/feature-A-task1`, `.worktrees/feature-A-task2`, ...）
- 主仓库 HEAD **保持固定**（不再频繁切换分支）
- 期望：每个 worktree finish → 合并回**它创建时所基于的源分支**

---

## 2. 设计目标

| ID | 目标 | 验证标准 |
|----|------|---------|
| G1 | 源分支绑定 worktree | finish 读取的源分支与创建时一致，与主仓库 HEAD 无关 |
| G2 | 主仓库零打扰 | finish 全流程不修改主仓库 HEAD/working tree |
| G3 | 多 worktree 并行安全 | 同源 feature-A 的两个 worktree 串行 finish 不串扰 |
| G4 | 冲突显式处理 | 本地 merge 冲突时暂停，用户解决后回复"继续"再进行 |
| G5 | 兼容老 worktree | 缺少元数据时有 fallback，不卡死流水线 |
| G6 | auto 模式无人值守 | 顺利路径全程无需人工确认（冲突除外） |

---

## 3. 关键决策（澄清结果）

| 决策点 | 选项 | 选择 |
|--------|------|------|
| 默认目标分支 | 源分支 / PR / 用户确认 / 按工作流分流 | **worktree 创建时所基于的源分支** |
| push 策略 | merge+push / 仅本地 merge / 仅 push 分支 | **本地 merge → 解决冲突 → push 远程** |
| source 形态 | active worktree / 仅 ref / 两种都有 | **两种都有，自动检测** |

---

## 4. 架构改动

### 4.1 修改文件清单

| 文件 | 改动类型 |
|------|---------|
| `skills/using-git-worktrees/SKILL.md` | 新增 Step 2.5：写入源分支元数据 |
| `skills/finishing-a-development-branch/SKILL.md` | 重写 Step 3（Determine Source Branch）+ Step 4 auto 子流程 |
| `skills/finishing-a-development-branch/references/source-resolution.md` | 新增：源分支解析与 merge 路径决策详细规则 |
| `commands/feat.md`, `commands/fix.md`, `commands/refactor.md`, `commands/init.md` | 同步更新 Step 8 检查点描述（"合并到源分支"而非"初始分支"） |

### 4.2 元数据持久化机制

使用 git 原生 per-worktree config（需要 git 2.20+）：

```bash
# 一次性启用（仓库级，幂等）
git config extensions.worktreeConfig true

# 写入 per-worktree config
git config --worktree superpowers.sourceBranch <source-branch>
git config --worktree superpowers.sourceCommit <sha-when-created>
```

**注意**：必须先启用 `extensions.worktreeConfig=true`，否则 `--worktree` 写入会落到共享 config，被所有 worktree 看到（破坏元数据隔离）。`using-git-worktrees` Step 2.5 应在写入前检查并启用此扩展。

**选用理由**：

- git 原生支持，worktree 移除时自动失效，无需手动清理
- 不污染 working tree（不会被误提交）
- `git worktree move` 后自动跟随
- 命名空间 `superpowers.*` 避免与项目 config 冲突

**回退兼容**：

仓库 git 版本 < 2.20 不支持 `--worktree`，fallback 到文件：

```bash
echo "$SOURCE_BRANCH" > "$(git rev-parse --git-path superpowers-source)"
```

`git rev-parse --git-path` 在 worktree 内会解析到 `.git/worktrees/<name>/superpowers-source`，自动跟随 worktree。

### 4.3 using-git-worktrees 新增逻辑

在现有 Step 1（Create Isolated Workspace）之后、Step 3（Project Setup）之前，新增 Step 2.5：

```markdown
### Step 2.5: Record Source Branch Metadata

记录 worktree 的"源分支"，供 finishing-a-development-branch 使用。

```bash
# SOURCE_BRANCH 获取顺序：
# 1. 调用方显式参数（如 skill 调用 source-branch=feature-A）
# 2. worktree 创建时 git checkout -b 的 base（通常是主仓库当时的 HEAD）
# 3. detached HEAD → 询问用户

SOURCE_BRANCH="${SOURCE_BRANCH:-$(git -C "$MAIN_ROOT" symbolic-ref --short HEAD 2>/dev/null)}"

if [ -z "$SOURCE_BRANCH" ] || [ "$SOURCE_BRANCH" = "HEAD" ]; then
  # detached HEAD or unclear, ask user
  echo "Cannot determine source branch automatically. Please specify."
  exit 1
fi

# 写入 worktree-local config
GIT_VERSION_MAJOR=$(git --version | awk '{print $3}' | cut -d. -f1)
GIT_VERSION_MINOR=$(git --version | awk '{print $3}' | cut -d. -f2)

if [ "$GIT_VERSION_MAJOR" -gt 2 ] || \
   ([ "$GIT_VERSION_MAJOR" -eq 2 ] && [ "$GIT_VERSION_MINOR" -ge 20 ]); then
  # 启用 per-worktree config 扩展（幂等）
  git config extensions.worktreeConfig true
  git config --worktree superpowers.sourceBranch "$SOURCE_BRANCH"
  git config --worktree superpowers.sourceCommit "$(git rev-parse "$SOURCE_BRANCH")"
else
  # Fallback for old git
  echo "$SOURCE_BRANCH" > "$(git rev-parse --git-path superpowers-source)"
  git rev-parse "$SOURCE_BRANCH" > "$(git rev-parse --git-path superpowers-source-commit)"
fi
```

**对已存在的 worktree（Step 0 检测到已在 worktree 内）**：跳过元数据写入（保持现状），由 finishing-a-development-branch 的 fallback 处理。

### 4.4 finishing-a-development-branch 重写

#### Step 3 重写：Determine Source Branch

替换原"Determine Base Branch"为：

```markdown
### Step 3: Determine Source Branch

读取 worktree 元数据，决定合并目标。

```bash
# 1. 优先读取 worktree-local config
SOURCE=$(git config --worktree superpowers.sourceBranch 2>/dev/null)

# 2. fallback 到文件
if [ -z "$SOURCE" ]; then
  SOURCE_FILE="$(git rev-parse --git-path superpowers-source)"
  [ -f "$SOURCE_FILE" ] && SOURCE=$(cat "$SOURCE_FILE")
fi

# 3. 仍空 → 暂停询问用户
if [ -z "$SOURCE" ]; then
  # 提供推断候选
  CANDIDATE=$(git merge-base --octopus HEAD main 2>/dev/null \
              || git merge-base HEAD master 2>/dev/null \
              || echo "未知")
  echo "未找到此 worktree 的源分支元数据（可能是手动 git worktree add 创建）。"
  echo "候选源分支：$CANDIDATE"
  echo "请确认源分支名（或输入 'pr' 跳过本地 merge 走 PR 路径）："
  read SOURCE
fi
```

**fallback 输入 `pr` 的处理**：当 SOURCE 为字面值 `pr` 时，Step 4 跳过 auto merge 子流程，转而执行 interactive Option 2 的逻辑（push 当前分支 + `gh pr create`），完成后保留 worktree（用户后续需迭代 PR）。
```

#### Step 4 重写：Execute Finish (auto mode)

完整替换 auto 模式子流程：

```markdown
#### auto mode (rewritten)

确定性流水线，源分支感知，主仓库零打扰。

```bash
SOURCE_BRANCH="$SOURCE"  # 来自 Step 3
WT_BRANCH=$(git branch --show-current)
WT_PATH=$(git rev-parse --show-toplevel)

# 特殊情况：worktree branch == source branch（如 /init 首次提交，无父分支）
if [ "$WT_BRANCH" = "$SOURCE_BRANCH" ] || [ -z "$SOURCE_BRANCH" ]; then
  # Push only 路径
  git push -u origin "$WT_BRANCH"
  # cleanup worktree (Step 5)
  exit 0
fi

# 特殊情况：worktree 无新提交
if [ "$(git rev-parse HEAD)" = "$(git rev-parse "$SOURCE_BRANCH" 2>/dev/null)" ]; then
  echo "Worktree branch == source branch HEAD, nothing to merge. Skipping."
  # 仍执行 cleanup
  exit 0
fi

# 1. 检测 source branch 形态
SOURCE_WT=$(git worktree list --porcelain | \
  awk -v src="refs/heads/$SOURCE_BRANCH" '
    /^worktree / { wt=$2 }
    /^branch / { if ($2 == src) print wt }
  ')

# 2. 分支决策
if [ -n "$SOURCE_WT" ]; then
  # 2a. source 在 active worktree → cd 进去 merge
  
  # 检查 source worktree 是否干净
  if ! git -C "$SOURCE_WT" diff --quiet || ! git -C "$SOURCE_WT" diff --cached --quiet; then
    echo "Source worktree at $SOURCE_WT has uncommitted changes."
    echo "Please commit or stash them, then reply 'continue'."
    exit 1
  fi
  
  cd "$SOURCE_WT"
  if ! git merge --no-ff "$WT_BRANCH" -m "Merge $WT_BRANCH into $SOURCE_BRANCH"; then
    echo "Merge conflict detected. Conflicted files:"
    git diff --name-only --diff-filter=U
    echo "Please resolve conflicts and commit, then reply 'continue'."
    exit 1
  fi
  cd "$WT_PATH"
  
elif git fetch . "$WT_BRANCH:$SOURCE_BRANCH" 2>/dev/null; then
  # 2b. source 仅 ref + worktree 已 fast-forward source → 直接更新 ref
  echo "Fast-forwarded $SOURCE_BRANCH to $WT_BRANCH HEAD"
  
else
  # 2c. source 仅 ref + 非 ff → 临时 worktree 处理
  TMP_WT=$(mktemp -d -t superpowers-merge-XXXXXX)
  trap "git worktree remove --force '$TMP_WT' 2>/dev/null; rm -rf '$TMP_WT'" EXIT
  
  git worktree add "$TMP_WT" "$SOURCE_BRANCH"
  cd "$TMP_WT"
  if ! git merge --no-ff "$WT_BRANCH" -m "Merge $WT_BRANCH into $SOURCE_BRANCH"; then
    echo "Merge conflict in temporary worktree."
    echo "This case is rare (non-ff with no active source worktree)."
    echo "Please cd to $TMP_WT to resolve, then reply 'continue'."
    exit 1
  fi
  cd "$WT_PATH"
  git worktree remove "$TMP_WT"
  trap - EXIT
fi

# 3. 运行测试（在 source 所在位置）
RUN_DIR="${SOURCE_WT:-$MAIN_ROOT}"
cd "$RUN_DIR"
<test command>  # npm test / cargo test / pytest / etc.
TEST_EXIT=$?
cd "$WT_PATH"

if [ $TEST_EXIT -ne 0 ]; then
  echo "Tests failed after merge. Rolling back merge commit."
  (cd "$RUN_DIR" && git reset --hard HEAD~1)
  exit 1
fi

# 4. push 远程 source branch
if ! git push origin "$SOURCE_BRANCH"; then
  echo "Push rejected (likely non-ff: origin/$SOURCE_BRANCH has new commits)."
  echo "Please pull and resolve, then reply 'continue'."
  exit 1
fi

# 5. cleanup worktree (Step 5 既有逻辑)
# 6. 删除 worktree branch
```
```

#### 关键不变量

| 不变量 | 实现保证 |
|--------|---------|
| 主仓库 HEAD 永不被切换 | 全流程移除所有 `cd $MAIN_ROOT && git checkout` |
| 源分支决策不看主仓库状态 | 全程基于 worktree-local config / 文件 fallback |
| 冲突可被人工处理 | 冲突时输出明确消息 + exit，等待用户解决并回复"继续" |
| auto 流水线无人值守 | 顺利路径全自动 |

#### 4.4.1 测试与回滚位置矩阵

merge 后是否要再跑测试 + 失败如何回滚，因 source 形态不同而异：

| 分支 | 测试位置（RUN_DIR） | 是否需要 merge 后测试 | 失败回滚动作 |
|------|---------------------|----------------------|-------------|
| 2a（source 在 active worktree） | `$SOURCE_WT` | 是（merge 产生新代码组合） | `(cd $SOURCE_WT && git reset --hard HEAD~1)` |
| 2b（source 仅 ref + fast-forward） | 无需（fast-forward 等同于已验证） | 否 | 不适用：未产生新组合，无需回滚 |
| 2c（source 仅 ref + 非 ff） | `$TMP_WT`（remove 前在临时 worktree 内跑） | 是 | `(cd $TMP_WT && git reset --hard HEAD~1)` + 不更新 source ref |

**约束**：测试必须在 trap-cleanup 触发**之前**完成。2c 的临时 worktree remove 应在测试通过 + push 成功之后才执行。

### 4.5 /init 工作流的特殊处理

`/init` 是首次提交，无源分支：

- `using-git-worktrees`: SOURCE_BRANCH 为空 → 跳过元数据写入
- `finishing-a-development-branch`: Step 3 检测无源分支 → Step 4 走"push only"路径（仅推送当前分支，不做 merge）

---

## 5. 数据流图

```
┌──────────────────────────────────────────────────────────────┐
│ /feat 启动 (主仓库 HEAD = master 或任意分支)                  │
└──────────────────┬───────────────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────────────┐
│ Step 3 ISOLATE → using-git-worktrees                         │
│  1. 创建 worktree at .worktrees/feature-A-task1              │
│     based on feature-A                                       │
│  2. 写入 git config --worktree superpowers.sourceBranch=     │
│     feature-A                                                │
└──────────────────┬───────────────────────────────────────────┘
                   ↓
        ... Plan / Implement / Review / Verify ...
                   ↓
┌──────────────────────────────────────────────────────────────┐
│ Step 8 FINISH → finishing-a-development-branch (auto)        │
│  1. 读 git config --worktree superpowers.sourceBranch        │
│     → feature-A (即使主仓库 HEAD ≠ feature-A)                 │
│  2. git worktree list 找 feature-A 的 active worktree         │
│  3. 分支决策                                                   │
│     - 有 active wt → cd 进去 git merge --no-ff                │
│     - 无 active wt + ff → git fetch . HEAD:feature-A          │
│     - 无 active wt + 非 ff → 临时 worktree merge              │
│  4. 冲突？暂停等待用户                                          │
│  5. 测试 → 失败则 reset --hard HEAD~1                          │
│  6. push origin/feature-A                                    │
│  7. cleanup .worktrees/feature-A-task1                       │
│  8. 删除 task1 branch                                         │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. 边界场景与错误处理

| 场景 | 处理 |
|------|------|
| worktree 元数据缺失（老 worktree 或手动创建） | Step 3 fallback：候选用 `git merge-base` 推断 + 暂停问用户确认 |
| source branch 已被删除 | Step 4 报错暂停，提示用户：选 PR 路径或手动指定新源 |
| source branch 远程领先（push 时非 ff） | 拒绝 push，暂停提示："origin/<source> 有新提交，请 pull 后回复'继续'" |
| merge 冲突 | 暂停 + 列出冲突文件 + 提示"解决后回复'继续'" |
| source 在 active worktree 但该 worktree 工作树脏 | 拒绝 merge，暂停："source worktree 有未提交改动，请处理后回复'继续'" |
| worktree branch == source branch（无新提交） | 跳过 merge，直接 cleanup |
| worktree 与 source HEAD 一致（已合并） | 跳过 merge，直接 cleanup |
| 跨 git 版本（< 2.20，无 --worktree config 支持） | fallback 到 `.git/worktrees/<name>/superpowers-source` 文件 |
| /init 工作流（无源分支） | "push only"路径：push 当前分支，不做 merge |
| detached HEAD worktree（externally managed） | 维持现有逻辑：interactive 3 选项菜单 |

---

## 7. 测试策略

### 7.1 单元行为测试

在 `skills/finishing-a-development-branch/references/test-scenarios.md` 中描述每个场景的 setup / action / expect。

测试场景清单：

1. **基础路径**：feature-A worktree active + 子任务 worktree → finish → 合并回 feature-A
2. **主仓库 HEAD 不同**：主仓库在 master，feature-A 在另一 worktree，子任务 finish → 仍合并到 feature-A（验证 G1, G2）
3. **source 无 active worktree**：手动 `git branch feature-A`，子任务 finish → fast-forward
4. **冲突**：两个子任务都改同一文件 → 第二个 finish 时冲突 → 暂停 → 解决继续
5. **老 worktree fallback**：手动 `git worktree add` 创建 → finish → 提示用户确认源分支
6. **/init 路径**：首次提交 → finish 走 push only
7. **push 拒绝**：模拟 origin/<source> 有新提交 → finish push 失败 → 暂停
8. **source 脏工作树**：feature-A worktree 有未提交改动 → 子任务 finish → 暂停
9. **测试失败回滚**：merge 后测试失败 → 自动 reset --hard HEAD~1
10. **git 版本兼容**：模拟 git < 2.20 → 走文件 fallback

### 7.2 集成测试

在 `evals/` 下放置可重放的 shell 脚本，每个场景独立 sandbox repo。

每个脚本结构：

```bash
#!/bin/bash
set -e
# Setup
TMP=$(mktemp -d)
cd "$TMP"
git init && git commit --allow-empty -m init
# Action
... 模拟用户操作 ...
# Assert
... 检查 git state ...
# Cleanup
rm -rf "$TMP"
```

---

## 8. 实施清单（高层）

| Phase | 内容 | 影响 |
|-------|------|------|
| Phase 1 | `using-git-worktrees` 新增 Step 2.5 | 向前兼容（老 worktree 不受影响） |
| Phase 2 | `finishing-a-development-branch` Step 3 改读元数据 + fallback | 向前兼容（fallback 处理老 worktree） |
| Phase 3 | `finishing-a-development-branch` Step 4 auto 子流程重写 | 核心改动 |
| Phase 4 | `references/source-resolution.md` 详细规则文档 | 新增文档 |
| Phase 5 | `references/test-scenarios.md` + `evals/*.sh` 测试脚本 | 新增测试 |
| Phase 6 | 4 个命令（feat/fix/refactor/init）Step 8 检查点描述同步 | 文档同步 |

---

## 9. 不做的事（YAGNI）

- **不**改 interactive 模式（保留现有 4 选项菜单作为逃生口）
- **不**改 push 时机为"批量"（用户答案是"修复冲突后 push"，每次 finish 都尝试 push 即可）
- **不**支持"跨远程"合并（仅 origin）
- **不**自动 rebase（避免重写历史，merge 更可控）
- **不**修改 marketplace.json 或其他 plugin 元信息
- **不**引入新的 variable（不增加 finish-mode 之外的配置项）
- **不**自动 pull source branch（保持显式：push 失败时让用户处理）

---

## 10. 风险与缓解

| 风险 | 缓解 |
|------|------|
| git config --worktree 在 git < 2.20 不支持 | 已设计文件 fallback；在 SKILL.md 中注明 git 版本要求 |
| 临时 worktree 路径泄漏（mktemp 失败） | trap EXIT 确保清理；失败时报错而非静默 |
| 用户对"暂停等继续"指令理解不一致 | 在暂停消息中明确："请解决冲突后回复 '继续' 或 'continue'" |
| 现有 4 个命令的 Step 8 检查点描述与新行为不一致 | Phase 6 同步更新："合并到源分支" 而非 "合并到初始分支" |
| 测试失败回滚（reset --hard HEAD~1）破坏 source worktree 已有工作 | 测试在 RUN_DIR 执行，仅 reset merge 提交；merge 前已校验 source worktree 干净 |
| /init 首次提交无远程时 push 失败 | push only 路径需检测：若无远程则提示用户 `git remote add` |

---

## 11. 验收标准

| ID | 验收点 | 验证方式 |
|----|--------|---------|
| A1 | 主仓库 HEAD 在任意分支时，finish 都合并到 worktree 创建时的源分支 | 测试场景 2 |
| A2 | finish 全流程不修改主仓库 working tree | 测试脚本前后对比 `git -C $MAIN_ROOT status` |
| A3 | 同源 feature-A 的两个 worktree 串行 finish，第二个冲突时正确暂停 | 测试场景 4 |
| A4 | 老 worktree（无元数据）finish 时有 fallback 提示 | 测试场景 5 |
| A5 | /init 工作流 finish 不报错 | 测试场景 6 |
| A6 | git < 2.20 仓库 finish 正常工作（走文件 fallback） | 测试场景 10 |

---

## 12. 参考

- 当前 SKILL：`plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md`
- 关联 SKILL：`plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md`
- 调用方命令：`plugins/superpowers-pro/commands/{feat,fix,refactor,init}.md`
- git worktree config 文档：`git help config`（搜索 `extensions.worktreeConfig`）
- git 2.20 release notes（per-worktree config 引入）
