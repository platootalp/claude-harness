# self-evolution 插件迁移到 harness marketplace

## 背景

`claude-self-evolution` 是一个独立仓库的 Claude Code 插件，提供自动从对话中提取可复用工作流并生成 skill 的能力。现需将其完全迁移到 `claude-harness` 插件市场中，原独立仓库废弃。

## 迁移策略

**方案 A：直接复制 + 注册**

把 `claude-self-evolution/` 整个目录复制到 `claude-harness/plugins/self-evolution/`，在 `marketplace.json` 中注册，更新文档。原仓库归档。

## 迁移范围

### 源文件清单

| 源路径（claude-self-evolution/） | 目标路径（claude-harness/plugins/self-evolution/） | 说明 |
|---|---|---|
| `src/` | `src/` | TypeScript 运行时源码（12 命令 + 6 lib 模块） |
| `esbuild.config.mjs` | `esbuild.config.mjs` | 构建配置 |
| `tsconfig.json` | `tsconfig.json` | TypeScript 配置 |
| `vitest.config.ts` | `vitest.config.ts` | 测试配置 |
| `package.json` | `package.json` | 独立依赖管理 |
| `package-lock.json` | `package-lock.json` | 锁文件 |
| `config.default.json` | `config.default.json` | 默认配置 |
| `scripts/` | `scripts/` | 打包脚本 |
| `skills/evolve-skill-writer/` | `skills/evolve-skill-writer/` | 1 个 skill |
| `agents/` | `agents/` | 2 个 agent（skill-reviewer.md, config-agent.md） |
| `commands/` | `commands/` | 4 个 command |
| `hooks/` | `hooks/` | 3 个 hooks.json（claude-code, codex, cursor） |
| `prompts/` | `prompts/` | 4 个 companion prompt 模板 |
| `.claude-plugin/plugin.json` | `.claude-plugin/plugin.json` | 插件 manifest |
| `.cursor-plugin/` | `.cursor-plugin/` | Cursor 平台 manifest |
| `.codex-plugin/` | `.codex-plugin/` | Codex 平台 manifest |
| `LICENSE` | `LICENSE` | MIT 许可证 |
| `README.md` | `README.md` | 项目说明 |
| `README.zh.md` | `README.zh.md` | 中文说明 |

### 排除文件

| 路径 | 原因 |
|---|---|
| `node_modules/` | 依赖目录，迁移后重新 npm install |
| `.git/` | 原仓库 git 历史，不带入 harness |
| `.idea/` | IDE 配置 |
| `docs/` | 原仓库内部文档，harness 有自己的 docs 体系 |

**注意**：`dist/` 目录**需要保留并 git track**，因为 hooks 依赖 `dist/runtime.mjs`，用户安装插件时需要预构建产物。

## 迁移步骤

### 1. 复制文件

```bash
# 创建目标目录
mkdir -p claude-harness/plugins/self-evolution

# 复制源码和配置（排除 node_modules, dist, .git, .idea, docs）
rsync -av --exclude='node_modules' --exclude='dist' --exclude='.git' --exclude='.idea' --exclude='docs' \
  claude-self-evolution/ claude-harness/plugins/self-evolution/
```

### 2. 安装依赖并构建

```bash
cd claude-harness/plugins/self-evolution
npm install
npm run build
npm test
```

### 3. 注册到 marketplace

在 `claude-harness/.claude-plugin/marketplace.json` 的 `plugins` 数组中添加：

```json
{
  "name": "self-evolution",
  "source": "./plugins/self-evolution",
  "description": "自动从对话中提取可复用工作流并生成 skill — companion-mode 后台审查、安全门控、元技能驱动内容生成"
}
```

### 4. 更新 harness CLAUDE.md

在 CLAUDE.md 中添加 self-evolution 插件说明，包括：
- 插件概述和架构
- 构建和测试命令
- 组件清单（skills/agents/commands/hooks）
- 数据位置
- 版本管理说明

### 5. 更新 harness .gitignore

确保 `plugins/self-evolution/node_modules/` 被忽略。`dist/` 需要提交到 git（hooks 依赖预构建产物）。

### 6. 版本管理

- self-evolution 在 harness 中保持独立版本号（当前 0.12.0）
- 在 `plugins/self-evolution/` 下创建 `CHANGELOG.md`，记录迁移事件
- 后续版本更新只修改 `plugins/self-evolution/.claude-plugin/plugin.json` 中的 version

## 验证标准

1. `npm run build` 成功生成 `dist/runtime.mjs`
2. `npm test` 全部通过
3. `claude plugin validate .` 在 harness 根目录通过
4. hooks.json 中的 `${CLAUDE_PLUGIN_ROOT}` 路径在新位置下正确解析
5. `/evolve-review`、`/evolve-config`、`/evolve-status`、`/evolve-delete-skill` 命令可用
6. skill-reviewer agent 能正确调用 `runtime.mjs` 的 security-scan / validate-skill / verify-skill 命令

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}` 路径变化导致 hooks 失效 | Claude Code 的 `CLAUDE_PLUGIN_ROOT` 环境变量由插件系统自动设置，指向插件安装目录，与源码位置无关。验证时确认路径解析正确。 |
| harness 仓库体积增大 | .gitignore 排除 node_modules，实际增加的是源码 + dist 产物，约 200KB |
| 原仓库 git 历史丢失 | 迁移前在原仓库打 tag `v0.12.0-pre-migration`，归档后仍可查阅历史 |
| 多平台 hooks 路径 | hooks.json 使用 `${CLAUDE_PLUGIN_ROOT}` 相对路径，不受仓库位置影响 |

## 迁移后原仓库处理

1. 在 `claude-self-evolution` 仓库打 tag `v0.12.0-pre-migration`
2. 更新 README 指向 harness 仓库
3. 设置 GitHub 仓库为 Archived 状态
