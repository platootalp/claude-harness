# self-evolution 插件迁移 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-pro:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 claude-self-evolution 插件完全迁移到 claude-harness/plugins/self-evolution/，注册到 marketplace，验证构建和测试通过。

**Architecture:** 直接复制 self-evolution 源码到 harness 插件目录，保留独立 package.json 和构建流程。在 marketplace.json 注册插件，更新 CLAUDE.md 文档和 .gitignore。

**Tech Stack:** TypeScript, esbuild, vitest, rsync

---

### Task 1: 复制 self-evolution 源码到 harness

**Files:**
- Create: `plugins/self-evolution/` (整个目录树)

- [ ] **Step 1: 执行 rsync 复制**

```bash
mkdir -p plugins/self-evolution

rsync -av \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='.idea' \
  --exclude='docs' \
  /Users/lijunyi/road/claude-self-evolution/ \
  plugins/self-evolution/
```

- [ ] **Step 2: 验证关键文件存在**

```bash
ls plugins/self-evolution/src/runtime.ts && \
ls plugins/self-evolution/.claude-plugin/plugin.json && \
ls plugins/self-evolution/hooks/hooks.json && \
ls plugins/self-evolution/skills/evolve-skill-writer/SKILL.md && \
ls plugins/self-evolution/agents/skill-reviewer.md && \
ls plugins/self-evolution/commands/evolve-review.md && \
ls plugins/self-evolution/prompts/review-prompt.md && \
ls plugins/self-evolution/esbuild.config.mjs && \
ls plugins/self-evolution/package.json && \
echo "ALL KEY FILES PRESENT"
```

Expected: `ALL KEY FILES PRESENT`

- [ ] **Step 3: 验证排除文件不存在**

```bash
test ! -d plugins/self-evolution/node_modules && \
test ! -d plugins/self-evolution/.git && \
test ! -d plugins/self-evolution/.idea && \
test ! -d plugins/self-evolution/docs && \
echo "EXCLUDED FILES ABSENT"
```

Expected: `EXCLUDED FILES ABSENT`

- [ ] **Step 4: Commit**

```bash
git add plugins/self-evolution/
git commit -m "feat(self-evolution): copy plugin source from standalone repo

Copy claude-self-evolution v0.12.0 source into plugins/self-evolution/.
Excludes node_modules, .git, .idea, docs. dist/ will be added after build."
```

---

### Task 2: 安装依赖并构建

**Files:**
- Create: `plugins/self-evolution/dist/runtime.mjs` (构建产物)
- Create: `plugins/self-evolution/node_modules/` (依赖，gitignore)

- [ ] **Step 1: 安装依赖**

```bash
cd plugins/self-evolution && npm install
```

Expected: `added N packages` 无错误

- [ ] **Step 2: 构建**

```bash
cd plugins/self-evolution && npm run build
```

Expected: `dist/runtime.mjs` 生成，无错误

- [ ] **Step 3: 运行测试**

```bash
cd plugins/self-evolution && npm test
```

Expected: 所有测试通过

- [ ] **Step 4: 验证 dist/runtime.mjs 存在且非空**

```bash
test -s plugins/self-evolution/dist/runtime.mjs && echo "BUILD ARTIFACT OK" || echo "BUILD ARTIFACT MISSING"
```

Expected: `BUILD ARTIFACT OK`

- [ ] **Step 5: Commit dist 产物**

```bash
git add plugins/self-evolution/dist/
git commit -m "build(self-evolution): add dist/runtime.mjs build artifact"
```

---

### Task 3: 注册到 marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: 添加 self-evolution 到 marketplace.json**

在 `marketplace.json` 的 `plugins` 数组末尾添加：

```json
{
  "name": "self-evolution",
  "source": "./plugins/self-evolution",
  "description": "自动从对话中提取可复用工作流并生成 skill — companion-mode 后台审查、安全门控、元技能驱动内容生成"
}
```

完整文件应为：

```json
{
  "name": "harness-marketplace",
  "description": "Spec-driven development plugin marketplace for Claude Code",
  "owner": {
    "name": "platootalp"
  },
  "plugins": [
    {
      "name": "superpowers-pro",
      "source": "./plugins/superpowers-pro",
      "description": "Structured development workflows for coding agents — feature development, debugging, code review, and more"
    },
    {
      "name": "kb",
      "source": "./plugins/kb",
      "description": "知识库管理插件 — 从代码仓库提取、转化、加载和呈现知识"
    },
    {
      "name": "self-evolution",
      "source": "./plugins/self-evolution",
      "description": "自动从对话中提取可复用工作流并生成 skill — companion-mode 后台审查、安全门控、元技能驱动内容生成"
    }
  ]
}
```

- [ ] **Step 2: 验证 JSON 有效**

```bash
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))" && echo "JSON VALID"
```

Expected: `JSON VALID`

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat(marketplace): register self-evolution plugin"
```

---

### Task 4: 更新 .gitignore

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: 添加 self-evolution 的 node_modules 忽略规则**

在 `.gitignore` 末尾添加：

```
# self-evolution plugin dependencies
plugins/self-evolution/node_modules/
```

注意：`dist/` 不忽略，因为 hooks 依赖 `dist/runtime.mjs`。

- [ ] **Step 2: 验证 node_modules 被忽略**

```bash
git check-ignore -q plugins/self-evolution/node_modules/ && echo "IGNORED" || echo "NOT IGNORED"
```

Expected: `IGNORED`

- [ ] **Step 3: 验证 dist 不被忽略**

```bash
git check-ignore -q plugins/self-evolution/dist/runtime.mjs && echo "IGNORED (BAD)" || echo "NOT IGNORED (GOOD)"
```

Expected: `NOT IGNORED (GOOD)`

- [ ] **Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: add self-evolution node_modules to gitignore"
```

---

### Task 5: 创建 self-evolution CHANGELOG.md

**Files:**
- Create: `plugins/self-evolution/CHANGELOG.md`

- [ ] **Step 1: 创建 CHANGELOG.md**

```markdown
# Changelog

## [0.12.0] - 2026-06-04

### Added
- 迁移到 harness-marketplace 插件市场
- 保留完整 TypeScript 运行时、多平台支持、安全扫描
```

- [ ] **Step 2: Commit**

```bash
git add plugins/self-evolution/CHANGELOG.md
git commit -m "docs(self-evolution): add CHANGELOG.md for migration"
```

---

### Task 6: 更新 harness CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 在 CLAUDE.md 的 Marketplace Registry 表格后添加 self-evolution 插件说明**

在 `## Active Plugin: kb` 段落之后，添加以下内容：

```markdown
## Active Plugin: self-evolution

`plugins/self-evolution/` — 自动从对话中提取可复用工作流并生成 skill 的插件 v0.12.0。Companion-mode 后台审查 + 安全门控 + 元技能驱动内容生成。

### 构建和测试

```bash
cd plugins/self-evolution
npm install        # 安装依赖
npm run build      # esbuild bundle → dist/runtime.mjs
npm test           # vitest run (所有测试)
```

### 组件清单

| 类型 | 数量 | 路径 |
|------|------|------|
| Skills | 1 | `skills/evolve-skill-writer/` |
| Agents | 2 | `agents/skill-reviewer.md`, `agents/config-agent.md` |
| Commands | 4 | `commands/evolve-review.md`, `evolve-config.md`, `evolve-status.md`, `evolve-delete-skill.md` |
| Hooks | 3 | `hooks/hooks.json` (Claude Code), `hooks/hooks.codex.json`, `hooks/hooks.cursor.json` |
| Prompts | 4 | `prompts/review-prompt.md`, `review-prompt-skill.md`, `review-prompt-update.md`, `review-prompt-combined.md` |

### 架构

TypeScript 运行时（`src/` → `dist/runtime.mjs`）处理 12 个命令，hooks 通过 `node "${CLAUDE_PLUGIN_ROOT}/dist/runtime.mjs" <command>` 调用。Companion-mode：Stop hook 触发后台 `claude -p` 进程执行 skill-reviewer pipeline。

### 数据位置

- Plugin data: `~/.claude/plugins/data/self-evolution-self-evolution-marketplace/`
- Sessions: `~/.claude/plugins/data/.../sessions/`
- Stats: `~/.claude/plugins/data/.../stats.json`

### 版本管理

self-evolution 保持独立版本号，更新时修改 `plugins/self-evolution/.claude-plugin/plugin.json` 中的 `version` 并在 `CHANGELOG.md` 记录。
```

- [ ] **Step 2: 更新 Marketplace Registry 表格**

在 CLAUDE.md 的 Marketplace Registry 表格中添加 self-evolution 行：

| **self-evolution** | `./plugins/self-evolution` | 活跃 |

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add self-evolution plugin to CLAUDE.md"
```

---

### Task 7: 复制 spec 文档到 worktree 并提交

**Files:**
- Create: `docs/superpowers-pro/specs/2026-06-04-self-evolution-migration-design.md`

- [ ] **Step 1: 复制 spec 文档**

```bash
mkdir -p docs/superpowers-pro/specs
cp /Users/lijunyi/road/claude-harness/docs/superpowers-pro/specs/2026-06-04-self-evolution-migration-design.md \
   docs/superpowers-pro/specs/
```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers-pro/specs/2026-06-04-self-evolution-migration-design.md
git commit -m "docs: add self-evolution migration spec"
```

---

### Task 8: 端到端验证

**Files:** 无修改

- [ ] **Step 1: 验证构建**

```bash
cd plugins/self-evolution && npm run build && echo "BUILD OK"
```

Expected: `BUILD OK`

- [ ] **Step 2: 验证测试**

```bash
cd plugins/self-evolution && npm test && echo "TESTS OK"
```

Expected: `TESTS OK`

- [ ] **Step 3: 验证 marketplace.json 完整性**

```bash
python3 -c "
import json
m = json.load(open('.claude-plugin/marketplace.json'))
names = [p['name'] for p in m['plugins']]
assert 'self-evolution' in names, 'self-evolution not in marketplace'
assert 'superpowers-pro' in names, 'superpowers-pro missing'
assert 'kb' in names, 'kb missing'
print(f'MARKETPLACE OK: {names}')
"
```

Expected: `MARKETPLACE OK: ['superpowers-pro', 'kb', 'self-evolution']`

- [ ] **Step 4: 验证 hooks.json 引用正确**

```bash
python3 -c "
import json
h = json.load(open('plugins/self-evolution/hooks/hooks.json'))
cmd = h['hooks']['SessionStart'][0]['hooks'][0]['command']
assert 'CLAUDE_PLUGIN_ROOT' in cmd, 'CLAUDE_PLUGIN_ROOT not in hook command'
assert 'dist/runtime.mjs' in cmd, 'dist/runtime.mjs not in hook command'
print(f'HOOKS OK: {cmd[:60]}...')
"
```

Expected: `HOOKS OK: node "${CLAUDE_PLUGIN_ROOT}/dist/runtime.mjs" session-start...`

- [ ] **Step 5: 验证 plugin.json 版本**

```bash
python3 -c "
import json
p = json.load(open('plugins/self-evolution/.claude-plugin/plugin.json'))
assert p['version'] == '0.12.0', f'Wrong version: {p[\"version\"]}'
print(f'VERSION OK: {p[\"version\"]}')
"
```

Expected: `VERSION OK: 0.12.0`

- [ ] **Step 6: 验证 .gitignore 规则**

```bash
git check-ignore -q plugins/self-evolution/node_modules/ && echo "node_modules IGNORED" || echo "node_modules NOT IGNORED"
git check-ignore -q plugins/self-evolution/dist/runtime.mjs && echo "dist IGNORED (BAD)" || echo "dist NOT IGNORED (GOOD)"
```

Expected: `node_modules IGNORED` + `dist NOT IGNORED (GOOD)`
