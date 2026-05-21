---
name: skill-discovery
description: Discover and install agent skills — both Anthropic official skills and community skills. Use when looking for skills to extend capabilities, searching for specific functionality, or installing new skills.
---

# Skill Discovery

Find and install agent skills from Anthropic's official collection and the community marketplace.

## Anthropic Official Skills

Anthropic官方维护的技能仓库，专业场景首选。稳定性与兼容性有保障，与Claude模型深度适配。

### 文档处理类
```bash
npx skills add anthropics/skills@pdf -g -y      # PDF处理
npx skills add anthropics/skills@pptx -g -y     # PPT处理
npx skills add anthropics/skills@docx -g -y     # Word处理
```

### 创意创作类
```bash
npx skills add anthropics/skills@image-generate -g -y  # 图片生成
```

### 开发工具类
```bash
npx skills add anthropics/skills@web-artifacts-builder -g -y  # Web构建
```

**核心优势**: 官方维护质量可靠、与Claude完美集成、持续更新迭代、社区广泛验证

**适用场景**: 专业文档处理、企业级应用、高质量内容创作

## Community Skills

### How to Search
```bash
npx skills find [query]
```

Browse available skills at: https://skills.sh/

### Common Categories
- Dev Tools
- Data & APIs
- Security
- Automation
- Productivity

## Verification Before Recommending

Always verify before installing:
- Check install count
- Verify source reputation
- Check GitHub stars

## Installing Skills

```bash
npx skills add <package> -g -y
```