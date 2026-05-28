# 设计文档：命令瘦身 + 变量系统 + Skill 统一

## 背景

当前 4 个命令（/feature、/fix、/refactor、/init-system）的每个步骤都内联执行细节，导致：
- 命令与 skill 之间内容重复，容易不一致
- 修改 skill 时需要同步修改 4 个命令文件
- FINISH 步骤在命令中是确定性流程，但在 finishing-a-development-branch skill 中是交互菜单模式，语义冲突
- 参数控制（如 brainstorming 的 review-mode）缺乏统一机制

## 目标

1. 命令瘦身：有对应 skill 的步骤只委托调用，不写执行细节
2. 变量系统：统一管理 skill 的可配置参数，支持全局默认 + 命令覆盖 + 会话覆盖
3. FINISH 统一：所有命令最后一步统一调用 finishing-a-development-branch skill，确定性流程为主
4. 新增 skill：fix 和 refactor 各有独立的步骤 1 skill

## 设计

### 1. 全局变量配置文件

**路径：** `.claude-plugin/variables.json`

```json
{
  "finish-mode": {
    "default": "auto",
    "values": ["auto", "interactive"],
    "description": "auto = 确定性合并推送清理; interactive = 菜单选择模式"
  },
  "review-mode": {
    "default": "section-by-section",
    "values": ["section-by-section", "full"],
    "description": "section-by-section = 分节审批; full = 一次展示"
  }
}
```

**规则：**
- 变量定义的唯一真相源
- 新增变量只需在此文件加一条 + 在对应 skill frontmatter 引用
- 无需改 hook（hook 全量读取此文件注入）

### 2. Skill Variables 块规范

Skill frontmatter 中声明 `variables` 列表（引用变量名，不重复定义）：

```yaml
# finishing-a-development-branch SKILL.md
---
name: finishing-a-development-branch
description: "..."
variables: [finish-mode]
---
```

```yaml
# brainstorming SKILL.md
---
name: brainstorming
description: "..."
variables: [review-mode]
---
```

- `variables` 列表中的变量名必须存在于 variables.json
- Skill body 中条件分支引用变量：`if finish-mode: auto → 确定性流程; if finish-mode: interactive → 交互流程`
- 无 variables 的 skill 行为不受影响

### 3. 变量注入机制

**扩展 session-start hook：** 读取 variables.json，将所有变量默认值注入会话上下文。

**注入格式：** 在 using-superpowers 内容之后追加：

```
[superpowers-pro variables]
finish-mode: auto (可选: auto, interactive) — auto = 确定性合并推送清理; interactive = 菜单选择模式
review-mode: section-by-section (可选: section-by-section, full) — section-by-section = 分节审批; full = 一次展示
```

**变量解析优先级：**
1. 用户会话内自然语言覆盖（"用 interactive 模式"）
2. 命令调用时指定值（`调用 skill（finish-mode: auto）`）
3. variables.json 全局默认值（session-start hook 注入）

### 4. 命令瘦身规范

**瘦身规则：**
- 有对应 skill 的步骤：只保留调用行（含变量指定）+ 检查点 + 产出物
- 无对应 skill 的步骤：保留完整内联内容
- 检查点格式、进度总览格式不变

**瘦身后步骤模板：**
```markdown
## Step N/8: <NAME>

调用 `superpowers-pro:<skill-name>` skill（<variable>: <value>）。

检查点: `━━━ [✓] Step N/8: <NAME> — <一句话结果>`
产出物: <文件路径或状态>
```

**4 个命令的步骤与 skill 对应关系：**

| Step | /feature | /fix | /refactor | /init-system | Skill | 瘦身？ |
|------|----------|------|-----------|-------------|-------|--------|
| 1 | BRAINSTORM | DIAGNOSE | ASSESS | PRD | brainstorming / issue-scanning / refactor-assessment / prd-generation | 是 |
| 2 | SPEC_REVIEW | SPEC_REVIEW | SPEC_REVIEW | PRD_REVIEW | 无（人类审批） | 否 |
| 3 | ISOLATE | ISOLATE | ISOLATE | ARCHITECT | using-git-worktrees / system-architect | 是 |
| 4 | PLAN | PLAN | PLAN | ARCH_REVIEW | writing-plans | init 否，其余是 |
| 5 | IMPLEMENT | IMPLEMENT | IMPLEMENT | SKELETON | subagent-driven-development | init 否，其余是 |
| 6 | REVIEW | REVIEW | REVIEW | ROADMAP | requesting-code-review | init 否，其余是 |
| 7 | VERIFY | VERIFY | VERIFY | VERIFY | verification-before-completion | 是 |
| 8 | FINISH | FINISH | FINISH | FINISH | finishing-a-development-branch | 是 |

### 5. finishing-a-development-branch Skill 重写

**从交互菜单模式 → 确定性流程为主，interactive 作为变量控制的可选模式。**

**新流程：**

```
Step 1: Verify Tests         — 测试不通过则停止
Step 2: Detect Environment   — 检测 worktree / 普通 repo / detached HEAD
Step 3: Determine Base Branch — 确定目标合并分支
Step 4: Execute Finish       — 根据 finish-mode 分支
  ├─ auto:     确定性流程
  └─ interactive: 菜单选择模式（保留当前逻辑）
Step 5: Cleanup Workspace    — 仅 auto 模式或 interactive 选项 1/4 时执行
```

**auto 模式 Step 4 详细流程（与命令 FINISH 步骤对齐）：**

1. 记录初始分支名
2. 合并 worktree 分支到初始分支
3. 合并后运行测试验证 — 失败则自动回滚合并并报告
4. 推送初始分支到远端
5. 清理 worktree（provenance 校验：仅 `.worktrees/`、`worktrees/`、`~/.config/superpowers-pro/worktrees/` 下的）
6. 删除 impl 分支

**init-system 的特殊处理：**
- Step 2 检测到无 worktree 时，跳过合并/清理步骤
- 只执行 git 初始化（如需要）+ 推送
- 无分支合并概念，无 worktree 清理

**interactive 模式保留当前 skill 的完整菜单逻辑，作为 fallback。**

**Skill frontmatter：**
```yaml
---
name: finishing-a-development-branch
description: "..."
variables: [finish-mode]
---
```

**Skill body 中变量引用：**
```markdown
## 变量

本 skill 使用变量 `finish-mode`（定义见 variables.json）：
- auto（默认）: 确定性合并推送清理
- interactive: 菜单选择模式

命令调用时通常指定 finish-mode: auto。
用户可在会话中说 "用 interactive 模式" 覆盖。
```

### 6. 新 Skill：issue-scanning

**定位：** 系统性扫描指定领域的所有潜在问题，产出问题清单

**与 systematic-debugging 的区别：**
- systematic-debugging：诊断单个已知 bug 的根因（深度优先）
- issue-scanning：系统性发现所有潜在问题（广度优先）

**流程：**
1. 理解扫描范围（用户指定的模块/功能/领域）
2. 阅读相关代码、测试、配置、日志
3. 多维度扫描：
   - 功能缺陷（逻辑错误、边界条件、异常处理）
   - 性能问题（N+1、内存泄漏、不必要的计算）
   - 安全隐患（注入、权限、数据泄露）
   - 兼容性问题（API 变更、依赖版本）
4. 产出结构化问题文档至 `docs/superpowers-pro/issues/YYYY-MM-DD-<scope>-issues.md`

**产出格式：**
```markdown
# 问题扫描: <扫描范围>

## 扫描维度
<覆盖的维度列表>

## 问题清单

### P0 — 必须修复
- [ ] <问题描述> — <文件:行号> — <影响>
### P1 — 建议修复
- [ ] ...
### P2 — 改进建议
- [ ] ...

## 问题间依赖
<问题之间的因果/依赖关系>
```

**Frontmatter：**
```yaml
---
name: issue-scanning
description: "系统性扫描指定领域的所有潜在问题，产出问题清单"
---
```

暂无 variables 需求。

### 7. 新 Skill：refactor-assessment

**定位：** 评估代码结构/性能/可维护性，识别重构目标，产出 refactor 文档

**流程：**
1. 理解重构目标（用户指定的模块/功能/代码区域）
2. 阅读当前代码结构
3. 多维度评估：
   - 结构质量（模块划分、职责单一、耦合度）
   - 可维护性（可读性、复杂度、重复代码）
   - 性能（瓶颈、资源使用）
   - 可测试性（依赖注入、副作用隔离）
4. 确定重构后目标状态
5. 识别行为不变性（重构中必须保持不变的行为）
6. 产出 refactor 文档至 `docs/superpowers-pro/refactors/YYYY-MM-DD-<target>.md`

**产出格式：**
```markdown
# 重构评估: <目标>

## 当前问题
<为什么要重构>

## 重构目标
<重构后的目标状态>

## 行为不变性
<必须保持不变的行为>

## 影响范围
<受影响的文件/模块>

## 风险点
<重构可能破坏的东西>
```

**Frontmatter：**
```yaml
---
name: refactor-assessment
description: "评估代码结构/性能/可维护性，识别重构目标，产出 refactor 文档"
---
```

暂无 variables 需求。

### 8. brainstorming Skill 迁移

将现有的 `review-mode` frontmatter 自定义字段迁移为 variables 块引用。

**迁移前：**
```yaml
---
name: brainstorming
description: "..."
review-mode: section-by-section
---
```

**迁移后：**
```yaml
---
name: brainstorming
description: "..."
variables: [review-mode]
---
```

Skill body 中的条件分支逻辑不变，只是变量来源从 frontmatter 自定义字段变为 variables.json。

## 变更清单

| 操作 | 文件 | 说明 |
|------|------|------|
| 新增 | `.claude-plugin/variables.json` | 全局变量定义 |
| 修改 | `hooks/session-start` | 扩展：读取 variables.json 并注入会话上下文 |
| 重写 | `skills/finishing-a-development-branch/SKILL.md` | 确定性流程为主 + interactive 变量分支 |
| 修改 | `skills/brainstorming/SKILL.md` | frontmatter 迁移 review-mode 到 variables 块 |
| 新增 | `skills/issue-scanning/SKILL.md` | /fix 第一步：系统性问题扫描 |
| 新增 | `skills/refactor-assessment/SKILL.md` | /refactor 第一步：重构评估 |
| 瘦身 | `commands/feat.md` | 7 步委托 skill，1 步保留内联 |
| 瘦身 | `commands/fix.md` | 7 步委托 skill，1 步保留内联；Step 1 改调 issue-scanning |
| 瘦身 | `commands/refactor.md` | 7 步委托 skill，1 步保留内联；Step 1 改调 refactor-assessment |
| 瘦身 | `commands/init.md` | 5 步委托 skill，3 步保留内联 |
| 更新 | `.claude-plugin/plugin.json` | version bump（minor） |
| 更新 | `CHANGELOG.md` | 记录变更 |

## 实现顺序

1. variables.json + session-start hook 扩展（基础设施）
2. 两个新 skill（issue-scanning、refactor-assessment）
3. finishing-a-development-branch 重写
4. brainstorming frontmatter 迁移
5. 4 个命令瘦身
6. plugin.json version + CHANGELOG
