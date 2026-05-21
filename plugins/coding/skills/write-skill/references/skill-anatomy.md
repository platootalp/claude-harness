# Skill 解剖学

## 目录结构

```
skill-name/
├── SKILL.md              # 主指令文件（必须）
│   ├── YAML frontmatter  # name + description（必须）
│   └── Markdown body     # 工作流和指令
└── Bundled Resources     # 支持文件（按需）
    ├── scripts/          # 可执行脚本
    ├── references/       # 参考文档
    └── assets/           # 模板、图标、字体
```

## Progressive Disclosure 三层加载

### 第 1 层：Metadata（始终加载，~100 词）
- name + description
- 在系统提示中始终可见
- Claude 据此决定是否加载 skill

### 第 2 层：SKILL.md body（触发时加载，< 500 行）
- 工作流、指令、快速参考
- skill 被触发后加载到对话中
- 加载后在整个会话中保持

### 第 3 层：Bundled resources（按需加载，无限制）
- scripts/ 可执行而不加载内容
- references/ 按需读取
- assets/ 作为输出模板使用

## 内容组织原则

### 何时拆分到 references/

- 重型参考文档 > 100 行
- 多域组织（不同框架/平台的变体）
- 条件性内容（仅在特定情况下需要）

### 何时放入 scripts/

- 可复用的可执行工具
- 确定性/重复性任务
- 验证和检查脚本

### 何时放入 assets/

- 输出模板
- 前端资源（图标、字体）
- HTML 模板

### 何时保持 inline

- 原则和概念
- < 50 行的代码模式
- 快速参考表

## 引用规则

### 一级深度

所有支持文件应从 SKILL.md 直接引用，不要嵌套引用。

```markdown
# ✅ 好的：一级引用
**完整 API 参考**：读取 `references/api.md`

# ❌ 坏的：嵌套引用
# SKILL.md → references/api.md → references/details.md
```

### 引用格式

```markdown
**描述**：读取 `references/file.md`
```

或

```markdown
**高级功能**：See [reference.md](reference.md) for complete guide
```

### 大型参考文件

> 100 行的参考文件需要在顶部添加目录：

```markdown
# API Reference

## 目录
- Authentication
- Core methods
- Error handling
```

## Skill 类型与结构

### 纪律执行型 (discipline)

```
Overview → Iron Law → Process Flow → Steps → Common Mistakes → Red Flags → Integration
```

特征：Iron Law + Rationalization Table + Red Flags

### 工作流型 (workflow)

```
Overview → Checklist → Process Flow → Steps → Key Principles → Integration
```

特征：Checklist + Flowchart + 逐步执行

### 技术型 (technique)

```
Overview → When to Use → Core Pattern → Quick Reference → Implementation → Common Mistakes
```

特征：代码示例 + 前后对比 + 快速参考

### 参考型 (reference)

```
Overview → Quick Reference → Detailed Sections → Common Mistakes
```

特征：表格 + 查找优化 + 领域组织

## 写作风格

### 解释 why

```markdown
# ❌ 坏的：只说 what
ALWAYS run tests before committing.

# ✅ 好的：解释 why
Run tests before committing — untested changes can break production without warning.
```

### 适度自由度

- 窄桥（只有一个正确路径）→ 低自由度，具体指令
- 开阔地（多种路径可通）→ 高自由度，给方向

### 避免过度 MUST

```markdown
# ❌ 坏的：过度强制
You MUST ALWAYS use the exact format. NEVER deviate.

# ✅ 好的：解释原因
Use this format because it ensures consistent parsing by downstream tools.
```

## 命名规范

- 动名词（-ing）：`writing-skills`, `systematic-debugging`
- 动作词：`deploy`, `analyze`
- 避免：`utils`, `helper`, `tools`（太模糊）
- kebab-case：`condition-based-waiting` 非 `conditionBasedWaiting`
- 语义化命名：`root-cause-tracing` 非 `debug-technique-3`
