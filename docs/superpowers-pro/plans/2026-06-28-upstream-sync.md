# 上游同步 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-pro:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将上游 obra/superpowers 的全部改动同步到 superpowers-pro，同时保留二开定制

**Architecture:** 以上游版本为基准覆盖，然后重新应用二开定制（命名空间、变量系统、源分支确认）。纯 markdown 文件操作，无代码构建。

**Tech Stack:** Git、文件操作

## Global Constraints

- 保留 `superpowers-pro:` 命名空间（不使用 `superpowers:`）
- 保留 `docs/superpowers-pro/` 路径前缀
- 保留 `.superpowers-pro/` 目录前缀
- 采用上游通用化格式：`Subagent (general-purpose):`、`{PLACEHOLDER}`、通用 `todos`
- 保留二开功能：finish-mode 变量、review-mode 变量、源分支确认（Step 0.5）
- 排除 executing-plans skill
- 上游源码位于 `/tmp/obra-superpowers/skills/`
- 本地目标位于 `plugins/superpowers-pro/skills/`

---

### Task 1: 同步 using-superpowers（含多平台工具映射）

**Files:**
- Modify: `plugins/superpowers-pro/skills/using-superpowers/SKILL.md`
- Modify: `plugins/superpowers-pro/skills/using-superpowers/references/codex-tools.md`
- Modify: `plugins/superpowers-pro/skills/using-superpowers/references/copilot-tools.md`
- Modify: `plugins/superpowers-pro/skills/using-superpowers/references/gemini-tools.md`
- Create: `plugins/superpowers-pro/skills/using-superpowers/references/claude-code-tools.md`
- Create: `plugins/superpowers-pro/skills/using-superpowers/references/antigravity-tools.md`
- Create: `plugins/superpowers-pro/skills/using-superpowers/references/pi-tools.md`

- [ ] **Step 1: 覆盖 SKILL.md 为上游版本，替换命名空间**

```bash
cp /tmp/obra-superpowers/skills/using-superpowers/SKILL.md plugins/superpowers-pro/skills/using-superpowers/SKILL.md
sed -i 's/Superpowers skills/Superpowers-Pro skills/g' plugins/superpowers-pro/skills/using-superpowers/SKILL.md
sed -i 's/superpowers:/superpowers-pro:/g' plugins/superpowers-pro/skills/using-superpowers/SKILL.md
```

- [ ] **Step 2: 覆盖 codex-tools.md、copilot-tools.md、gemini-tools.md 为上游版本**

```bash
cp /tmp/obra-superpowers/skills/using-superpowers/references/codex-tools.md plugins/superpowers-pro/skills/using-superpowers/references/codex-tools.md
cp /tmp/obra-superpowers/skills/using-superpowers/references/copilot-tools.md plugins/superpowers-pro/skills/using-superpowers/references/copilot-tools.md
cp /tmp/obra-superpowers/skills/using-superpowers/references/gemini-tools.md plugins/superpowers-pro/skills/using-superpowers/references/gemini-tools.md
```

- [ ] **Step 3: 复制新增的 claude-code-tools.md、antigravity-tools.md、pi-tools.md**

```bash
cp /tmp/obra-superpowers/skills/using-superpowers/references/claude-code-tools.md plugins/superpowers-pro/skills/using-superpowers/references/claude-code-tools.md
cp /tmp/obra-superpowers/skills/using-superpowers/references/antigravity-tools.md plugins/superpowers-pro/skills/using-superpowers/references/antigravity-tools.md
cp /tmp/obra-superpowers/skills/using-superpowers/references/pi-tools.md plugins/superpowers-pro/skills/using-superpowers/references/pi-tools.md
```

- [ ] **Step 4: 验证 — diff 确认命名空间替换正确**

```bash
# 确认不存在未替换的 superpowers: 引用（排除 superpowers-pro:）
grep -n 'superpowers:' plugins/superpowers-pro/skills/using-superpowers/SKILL.md | grep -v 'superpowers-pro:'
# 应无输出
```

- [ ] **Step 5: 提交**

```bash
git add plugins/superpowers-pro/skills/using-superpowers/
git commit -m "feat: sync using-superpowers with upstream — add multi-platform tool mappings"
```

---

### Task 2: 同步 brainstorming（含 visual companion 改进）

**Files:**
- Modify: `plugins/superpowers-pro/skills/brainstorming/SKILL.md`
- Modify: `plugins/superpowers-pro/skills/brainstorming/visual-companion.md`
- Modify: `plugins/superpowers-pro/skills/brainstorming/spec-document-reviewer-prompt.md`
- Modify: `plugins/superpowers-pro/skills/brainstorming/scripts/frame-template.html`
- Modify: `plugins/superpowers-pro/skills/brainstorming/scripts/helper.js`
- Modify: `plugins/superpowers-pro/skills/brainstorming/scripts/server.cjs`
- Modify: `plugins/superpowers-pro/skills/brainstorming/scripts/start-server.sh`
- Modify: `plugins/superpowers-pro/skills/brainstorming/scripts/stop-server.sh`

- [ ] **Step 1: 覆盖 SKILL.md 为上游版本，重新应用二开定制**

```bash
cp /tmp/obra-superpowers/skills/brainstorming/SKILL.md plugins/superpowers-pro/skills/brainstorming/SKILL.md
```

然后在 SKILL.md frontmatter 中添加 `variables: [review-mode]`，并在 `## Anti-Pattern` 之前插入 `## Review Modes` 章节（section-by-section/full 双模式说明），将设计展示部分改为条件分支（review-mode 决定是否分节审批），替换 `docs/superpowers/specs/` → `docs/superpowers-pro/specs/`。

- [ ] **Step 2: 覆盖 visual-companion.md 为上游版本，替换路径**

```bash
cp /tmp/obra-superpowers/skills/brainstorming/visual-companion.md plugins/superpowers-pro/skills/brainstorming/visual-companion.md
sed -i 's/\.superpowers\//.superpowers-pro\//g' plugins/superpowers-pro/skills/brainstorming/visual-companion.md
```

- [ ] **Step 3: 覆盖 spec-document-reviewer-prompt.md 为上游版本，替换路径**

```bash
cp /tmp/obra-superpowers/skills/brainstorming/spec-document-reviewer-prompt.md plugins/superpowers-pro/skills/brainstorming/spec-document-reviewer-prompt.md
sed -i 's|docs/superpowers/specs/|docs/superpowers-pro/specs/|g' plugins/superpowers-pro/skills/brainstorming/spec-document-reviewer-prompt.md
```

- [ ] **Step 4: 覆盖 scripts/ 全部文件为上游版本，替换路径**

```bash
for f in frame-template.html helper.js server.cjs start-server.sh stop-server.sh; do
  cp "/tmp/obra-superpowers/skills/brainstorming/scripts/$f" "plugins/superpowers-pro/skills/brainstorming/scripts/$f"
done
sed -i 's/\.superpowers\//.superpowers-pro\//g' plugins/superpowers-pro/skills/brainstorming/scripts/start-server.sh
sed -i 's/\.superpowers\//.superpowers-pro\//g' plugins/superpowers-pro/skills/brainstorming/scripts/stop-server.sh
```

- [ ] **Step 5: 验证 — 检查路径替换**

```bash
grep -rn '\.superpowers/' plugins/superpowers-pro/skills/brainstorming/ | grep -v '.superpowers-pro/'
# 应无输出
grep -rn 'docs/superpowers/' plugins/superpowers-pro/skills/brainstorming/ | grep -v 'docs/superpowers-pro/'
# 应无输出
```

- [ ] **Step 6: 提交**

```bash
git add plugins/superpowers-pro/skills/brainstorming/
git commit -m "feat: sync brainstorming with upstream — visual companion improvements + review mode"
```

---

### Task 3: 同步 dispatching-parallel-agents

**Files:**
- Modify: `plugins/superpowers-pro/skills/dispatching-parallel-agents/SKILL.md`

- [ ] **Step 1: 覆盖为上游版本**

```bash
cp /tmp/obra-superpowers/skills/dispatching-parallel-agents/SKILL.md plugins/superpowers-pro/skills/dispatching-parallel-agents/SKILL.md
```

- [ ] **Step 2: 提交**

```bash
git add plugins/superpowers-pro/skills/dispatching-parallel-agents/SKILL.md
git commit -m "feat: sync dispatching-parallel-agents with upstream"
```

---

### Task 4: 同步 finishing-a-development-branch（保留 finish-mode 定制）

**Files:**
- Modify: `plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md`

- [ ] **Step 1: 覆盖为上游版本，重新应用二开定制**

```bash
cp /tmp/obra-superpowers/skills/finishing-a-development-branch/SKILL.md plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
```

重新应用二开定制：
1. frontmatter 添加 `variables: [finish-mode]`
2. description 替换为含 finish-mode 的版本
3. 在 Overview 后插入 `## Variable Resolution` 章节（finish-mode 解析优先级）
4. 将流程改为 auto/interactive 双模式（auto = 确定性合并推送清理，interactive = 菜单选择）
5. 添加源分支确认逻辑（auto 模式下优先使用 EXPLICIT_SOURCE_BRANCH）

- [ ] **Step 2: 验证 — 确认 finish-mode 变量声明存在**

```bash
grep -n 'finish-mode' plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md | head -5
# 应有至少 3 处匹配（frontmatter、Variable Resolution、auto 模式说明）
```

- [ ] **Step 3: 提交**

```bash
git add plugins/superpowers-pro/skills/finishing-a-development-branch/SKILL.md
git commit -m "feat: sync finishing-a-development-branch with upstream — preserve finish-mode customization"
```

---

### Task 5: 同步 receiving-code-review

**Files:**
- Modify: `plugins/superpowers-pro/skills/receiving-code-review/SKILL.md`

- [ ] **Step 1: 覆盖为上游版本**

```bash
cp /tmp/obra-superpowers/skills/receiving-code-review/SKILL.md plugins/superpowers-pro/skills/receiving-code-review/SKILL.md
```

- [ ] **Step 2: 提交**

```bash
git add plugins/superpowers-pro/skills/receiving-code-review/SKILL.md
git commit -m "feat: sync receiving-code-review with upstream"
```

---

### Task 6: 同步 requesting-code-review（含 code-reviewer.md）

**Files:**
- Modify: `plugins/superpowers-pro/skills/requesting-code-review/SKILL.md`
- Modify: `plugins/superpowers-pro/skills/requesting-code-review/code-reviewer.md`

- [ ] **Step 1: 覆盖 SKILL.md 为上游版本，替换路径**

```bash
cp /tmp/obra-superpowers/skills/requesting-code-review/SKILL.md plugins/superpowers-pro/skills/requesting-code-review/SKILL.md
sed -i 's|docs/superpowers/|docs/superpowers-pro/|g' plugins/superpowers-pro/skills/requesting-code-review/SKILL.md
```

- [ ] **Step 2: 覆盖 code-reviewer.md 为上游版本**

```bash
cp /tmp/obra-superpowers/skills/requesting-code-review/code-reviewer.md plugins/superpowers-pro/skills/requesting-code-review/code-reviewer.md
```

- [ ] **Step 3: 提交**

```bash
git add plugins/superpowers-pro/skills/requesting-code-review/
git commit -m "feat: sync requesting-code-review with upstream — add read-only review constraint"
```

---

### Task 7: 同步 subagent-driven-development（合并审查 + scripts + task-reviewer）

**Files:**
- Modify: `plugins/superpowers-pro/skills/subagent-driven-development/SKILL.md`
- Modify: `plugins/superpowers-pro/skills/subagent-driven-development/implementer-prompt.md`
- Create: `plugins/superpowers-pro/skills/subagent-driven-development/task-reviewer-prompt.md`
- Create: `plugins/superpowers-pro/skills/subagent-driven-development/scripts/review-package`
- Create: `plugins/superpowers-pro/skills/subagent-driven-development/scripts/sdd-workspace`
- Create: `plugins/superpowers-pro/skills/subagent-driven-development/scripts/task-brief`
- Delete: `plugins/superpowers-pro/skills/subagent-driven-development/spec-reviewer-prompt.md`
- Delete: `plugins/superpowers-pro/skills/subagent-driven-development/code-quality-reviewer-prompt.md`

- [ ] **Step 1: 覆盖 SKILL.md 为上游版本，替换命名空间**

```bash
cp /tmp/obra-superpowers/skills/subagent-driven-development/SKILL.md plugins/superpowers-pro/skills/subagent-driven-development/SKILL.md
sed -i 's/superpowers:/superpowers-pro:/g' plugins/superpowers-pro/skills/subagent-driven-development/SKILL.md
```

- [ ] **Step 2: 覆盖 implementer-prompt.md 为上游版本**

```bash
cp /tmp/obra-superpowers/skills/subagent-driven-development/implementer-prompt.md plugins/superpowers-pro/skills/subagent-driven-development/implementer-prompt.md
```

- [ ] **Step 3: 复制新增 task-reviewer-prompt.md，替换命名空间**

```bash
cp /tmp/obra-superpowers/skills/subagent-driven-development/task-reviewer-prompt.md plugins/superpowers-pro/skills/subagent-driven-development/task-reviewer-prompt.md
sed -i 's/superpowers:/superpowers-pro:/g' plugins/superpowers-pro/skills/subagent-driven-development/task-reviewer-prompt.md
```

- [ ] **Step 4: 复制新增 scripts/ 目录**

```bash
mkdir -p plugins/superpowers-pro/skills/subagent-driven-development/scripts
cp /tmp/obra-superpowers/skills/subagent-driven-development/scripts/review-package plugins/superpowers-pro/skills/subagent-driven-development/scripts/review-package
cp /tmp/obra-superpowers/skills/subagent-driven-development/scripts/sdd-workspace plugins/superpowers-pro/skills/subagent-driven-development/scripts/sdd-workspace
cp /tmp/obra-superpowers/skills/subagent-driven-development/scripts/task-brief plugins/superpowers-pro/skills/subagent-driven-development/scripts/task-brief
chmod +x plugins/superpowers-pro/skills/subagent-driven-development/scripts/*
```

- [ ] **Step 5: 删除已被上游合并的 spec-reviewer-prompt.md 和 code-quality-reviewer-prompt.md**

```bash
rm plugins/superpowers-pro/skills/subagent-driven-development/spec-reviewer-prompt.md
rm plugins/superpowers-pro/skills/subagent-driven-development/code-quality-reviewer-prompt.md
```

- [ ] **Step 6: 验证 — 确认命名空间和文件结构**

```bash
grep -rn 'superpowers:' plugins/superpowers-pro/skills/subagent-driven-development/ | grep -v 'superpowers-pro:'
# 应无输出
ls plugins/superpowers-pro/skills/subagent-driven-development/
# 应包含: SKILL.md implementer-prompt.md task-reviewer-prompt.md scripts/
# 不应包含: spec-reviewer-prompt.md code-quality-reviewer-prompt.md
```

- [ ] **Step 7: 提交**

```bash
git add plugins/superpowers-pro/skills/subagent-driven-development/
git commit -m "feat: sync subagent-driven-development — merge to task-reviewer + add scripts"
```

---

### Task 8: 同步 systematic-debugging

**Files:**
- Modify: `plugins/superpowers-pro/skills/systematic-debugging/SKILL.md`

- [ ] **Step 1: 覆盖为上游版本，替换命名空间**

```bash
cp /tmp/obra-superpowers/skills/systematic-debugging/SKILL.md plugins/superpowers-pro/skills/systematic-debugging/SKILL.md
sed -i 's/superpowers:/superpowers-pro:/g' plugins/superpowers-pro/skills/systematic-debugging/SKILL.md
```

- [ ] **Step 2: 提交**

```bash
git add plugins/superpowers-pro/skills/systematic-debugging/SKILL.md
git commit -m "feat: sync systematic-debugging with upstream"
```

---

### Task 9: 同步 test-driven-development

**Files:**
- Modify: `plugins/superpowers-pro/skills/test-driven-development/SKILL.md`

- [ ] **Step 1: 覆盖为上游版本**

```bash
cp /tmp/obra-superpowers/skills/test-driven-development/SKILL.md plugins/superpowers-pro/skills/test-driven-development/SKILL.md
```

- [ ] **Step 2: 提交**

```bash
git add plugins/superpowers-pro/skills/test-driven-development/SKILL.md
git commit -m "feat: sync test-driven-development with upstream"
```

---

### Task 10: 同步 using-git-worktrees（保留源分支确认）

**Files:**
- Modify: `plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md`

- [ ] **Step 1: 覆盖为上游版本，重新应用 Step 0.5 源分支确认**

```bash
cp /tmp/obra-superpowers/skills/using-git-worktrees/SKILL.md plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md
```

重新应用二开定制：在 Step 0 和 Step 1 之间插入 `## Step 0.5: Confirm Source Branch` 章节（中文版源分支确认逻辑，含优先级规则、bash 实现、分支选择菜单）。

- [ ] **Step 2: 验证 — 确认 Step 0.5 存在**

```bash
grep -n 'Step 0.5' plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md
# 应有匹配
```

- [ ] **Step 3: 提交**

```bash
git add plugins/superpowers-pro/skills/using-git-worktrees/SKILL.md
git commit -m "feat: sync using-git-worktrees with upstream — preserve source branch confirmation"
```

---

### Task 11: 同步 writing-plans（排除 executing-plans 选项）

**Files:**
- Modify: `plugins/superpowers-pro/skills/writing-plans/SKILL.md`
- Modify: `plugins/superpowers-pro/skills/writing-plans/plan-document-reviewer-prompt.md`

- [ ] **Step 1: 覆盖 SKILL.md 为上游版本，替换命名空间和路径，删除 executing-plans 引用**

```bash
cp /tmp/obra-superpowers/skills/writing-plans/SKILL.md plugins/superpowers-pro/skills/writing-plans/SKILL.md
sed -i 's/superpowers:/superpowers-pro:/g' plugins/superpowers-pro/skills/writing-plans/SKILL.md
sed -i 's|docs/superpowers/|docs/superpowers-pro/|g' plugins/superpowers-pro/skills/writing-plans/SKILL.md
```

手动删除 "Execution Handoff" 中的 executing-plans 选项（Inline Execution），只保留 Subagent-Driven 选项。将 plan header 中的 `superpowers:executing-plans` 引用删除。

- [ ] **Step 2: 覆盖 plan-document-reviewer-prompt.md 为上游版本**

```bash
cp /tmp/obra-superpowers/skills/writing-plans/plan-document-reviewer-prompt.md plugins/superpowers-pro/skills/writing-plans/plan-document-reviewer-prompt.md
```

- [ ] **Step 3: 验证 — 确认无 executing-plans 残留**

```bash
grep -n 'executing-plans' plugins/superpowers-pro/skills/writing-plans/SKILL.md
# 应无输出
grep -rn 'superpowers:' plugins/superpowers-pro/skills/writing-plans/ | grep -v 'superpowers-pro:'
# 应无输出
```

- [ ] **Step 4: 提交**

```bash
git add plugins/superpowers-pro/skills/writing-plans/
git commit -m "feat: sync writing-plans with upstream — exclude executing-plans option"
```

---

### Task 12: 同步 writing-skills

**Files:**
- Modify: `plugins/superpowers-pro/skills/writing-skills/SKILL.md`
- Modify: `plugins/superpowers-pro/skills/writing-skills/anthropic-best-practices.md`
- Modify: `plugins/superpowers-pro/skills/writing-skills/persuasion-principles.md`
- Modify: `plugins/superpowers-pro/skills/writing-skills/testing-skills-with-subagents.md`

- [ ] **Step 1: 覆盖全部文件为上游版本，替换命名空间**

```bash
cp /tmp/obra-superpowers/skills/writing-skills/SKILL.md plugins/superpowers-pro/skills/writing-skills/SKILL.md
cp /tmp/obra-superpowers/skills/writing-skills/anthropic-best-practices.md plugins/superpowers-pro/skills/writing-skills/anthropic-best-practices.md
cp /tmp/obra-superpowers/skills/writing-skills/persuasion-principles.md plugins/superpowers-pro/skills/writing-skills/persuasion-principles.md
cp /tmp/obra-superpowers/skills/writing-skills/testing-skills-with-subagents.md plugins/superpowers-pro/skills/writing-skills/testing-skills-with-subagents.md
sed -i 's/superpowers:/superpowers-pro:/g' plugins/superpowers-pro/skills/writing-skills/SKILL.md
sed -i 's/superpowers:/superpowers-pro:/g' plugins/superpowers-pro/skills/writing-skills/testing-skills-with-subagents.md
```

- [ ] **Step 2: 提交**

```bash
git add plugins/superpowers-pro/skills/writing-skills/
git commit -m "feat: sync writing-skills with upstream"
```

---

### Task 13: 版本号 + Changelog 更新

**Files:**
- Modify: `plugins/superpowers-pro/.claude-plugin/plugin.json`
- Modify: `plugins/superpowers-pro/CHANGELOG.md`

- [ ] **Step 1: 更新 plugin.json 版本号（minor bump）**

读取当前版本号，minor +1。

- [ ] **Step 2: 更新 CHANGELOG.md**

在 `[Unreleased]` 下添加条目，描述本次上游同步。

- [ ] **Step 3: 提交**

```bash
git add plugins/superpowers-pro/.claude-plugin/plugin.json plugins/superpowers-pro/CHANGELOG.md
git commit -m "chore(superpowers-pro): bump version for upstream sync"
```

---

### Task 14: 全量验证

**Files:**
- 无新增修改

- [ ] **Step 1: 验证命名空间一致性**

```bash
# 不应存在未替换的 superpowers: 引用（排除 superpowers-pro:）
grep -rn 'superpowers:' plugins/superpowers-pro/skills/ | grep -v 'superpowers-pro:' | grep -v 'executing-plans'
# 应无输出
```

- [ ] **Step 2: 验证路径一致性**

```bash
# 不应存在未替换的 docs/superpowers/ 路径
grep -rn 'docs/superpowers/' plugins/superpowers-pro/skills/ | grep -v 'docs/superpowers-pro/'
# 应无输出
# 不应存在未替换的 .superpowers/ 路径
grep -rn '\.superpowers/' plugins/superpowers-pro/skills/ | grep -v '\.superpowers-pro/'
# 应无输出
```

- [ ] **Step 3: 验证文件结构完整性**

```bash
# 确认新增文件存在
ls plugins/superpowers-pro/skills/using-superpowers/references/claude-code-tools.md
ls plugins/superpowers-pro/skills/using-superpowers/references/antigravity-tools.md
ls plugins/superpowers-pro/skills/using-superpowers/references/pi-tools.md
ls plugins/superpowers-pro/skills/subagent-driven-development/task-reviewer-prompt.md
ls plugins/superpowers-pro/skills/subagent-driven-development/scripts/review-package
ls plugins/superpowers-pro/skills/subagent-driven-development/scripts/sdd-workspace
ls plugins/superpowers-pro/skills/subagent-driven-development/scripts/task-brief

# 确认已删除文件不存在
! ls plugins/superpowers-pro/skills/subagent-driven-development/spec-reviewer-prompt.md 2>/dev/null
! ls plugins/superpowers-pro/skills/subagent-driven-development/code-quality-reviewer-prompt.md 2>/dev/null
! ls plugins/superpowers-pro/skills/executing-plans 2>/dev/null
```

- [ ] **Step 4: 验证插件结构**

```bash
claude plugin validate . 2>&1 || echo "validate command not available — skip"
```
