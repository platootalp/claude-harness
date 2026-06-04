# PR/MR Creation — Multi-Platform Strategy

`finishing-a-development-branch` skill 不调用任何 platform CLI（`gh` / `glab`），统一用 `git push` + URL 推导实现 GitHub Pull Request 和 GitLab Merge Request 的创建入口。

## 1. 适用位置

- **Step 3 fallback**：用户在源分支询问中输入 `pr` 时
- **Interactive Option 2**：用户选择 "Push and create a PR/MR" 时

## 2. 实现伪代码

```bash
# 1. 推送分支
git push -u origin "$BRANCH"

# 2. 解析 origin URL 规范化为 https
REMOTE_URL=$(git remote get-url origin)
WEB_URL=$(echo "$REMOTE_URL" | sed -E '
  s#^git@([^:]+):#https://\1/#;
  s#\.git$##;
')

# 3. 平台检测与 URL 拼接
case "$WEB_URL" in
  *github.com*|*github*)
    CREATE_URL="${WEB_URL}/compare/${BRANCH}?expand=1"
    PLATFORM="GitHub Pull Request"
    ;;
  *gitlab*)
    CREATE_URL="${WEB_URL}/-/merge_requests/new?merge_request[source_branch]=${BRANCH}"
    PLATFORM="GitLab Merge Request"
    ;;
  *)
    CREATE_URL=""
    PLATFORM="未知平台"
    ;;
esac

# 4. 输出
echo "Branch pushed: $BRANCH"
if [ -n "$CREATE_URL" ]; then
  echo "Create $PLATFORM at: $CREATE_URL"
else
  echo "Detected non-GitHub/GitLab remote. Please create PR/MR manually."
  echo "Remote URL: $REMOTE_URL"
fi
```

## 3. URL 推导规则

| 输入 origin URL | 输出 CREATE_URL |
|-----------------|----------------|
| `git@github.com:owner/repo.git` | `https://github.com/owner/repo/compare/<branch>?expand=1` |
| `https://github.com/owner/repo.git` | `https://github.com/owner/repo/compare/<branch>?expand=1` |
| `git@gitlab.com:group/repo.git` | `https://gitlab.com/group/repo/-/merge_requests/new?merge_request[source_branch]=<branch>` |
| `git@gitlab.company.com:team/repo.git` | `https://gitlab.company.com/team/repo/-/merge_requests/new?merge_request[source_branch]=<branch>` |
| `git@bitbucket.org:owner/repo.git` | （无识别）提示用户手动创建，显示原始 URL |

## 4. 取舍

| 维度 | 用 CLI（`gh` / `glab`） | 仅 push + URL（本方案） |
|------|------------------------|------------------------|
| PR/MR title/body 自动填 | 支持 | 不支持，用户在 Web UI 填 |
| 平台覆盖 | 需各装一个 CLI | 全平台统一（仅需 git） |
| 用户环境依赖 | gh/glab 安装 + 认证 | 仅 git remote 配置 |
| 失败模式 | CLI 调用失败需排查 | push 失败即报错，定位简单 |

**取舍结论**：用户在 Web UI 中填 title/body 是常见做法，不构成重大体验损失；换来跨平台一致性和零外部依赖。

## 5. 未来扩展（暂不实现）

若未来需要自动填 title/body，可在第 4 步末尾加 opportunistic 探测：

```bash
if command -v gh >/dev/null 2>&1 && [[ "$WEB_URL" == *github.com* ]]; then
  # 调用 gh pr create --fill 等
fi
```

当前 spec **不实现**此扩展（YAGNI）。

## 6. 测试场景

参见 `test-scenarios.md` 场景 11、12、13。
