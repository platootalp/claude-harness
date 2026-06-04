# Test Scenarios for finishing-a-development-branch

15 个端到端场景，覆盖 spec 验收标准 A1-A11。每个场景给出 setup（如何构造 sandbox repo）、action（执行什么）、expected（验证 git state）。

对应的可执行 bash 脚本见 `../evals/*.sh`（部分场景已自动化）。

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

## 场景 14：主仓库 HEAD ≠ 期望源分支（验收 A10）

**Setup**：主仓库 checkout 在 feature-A；用户启动 `using-git-worktrees` skill

**Action**：在 Step 0.5 菜单中选择 feature-B（非主仓库 HEAD）

**Expected**：
- worktree 创建后 HEAD 在 feature-B 上（基于 feature-B）
- `git config --worktree superpowers.sourceBranch` 返回 `feature-B`
- 主仓库 HEAD 仍是 feature-A（未改变）

## 场景 15：显式源分支参数（验收 A11）

**Setup**：调用方设置 `EXPLICIT_SOURCE_BRANCH=feature-B` 后调用 skill

**Expected**：
- Step 0.5 不弹菜单，直接使用 feature-B
- 输出包含 "Using explicit source branch: feature-B"
- worktree 基于 feature-B 创建
