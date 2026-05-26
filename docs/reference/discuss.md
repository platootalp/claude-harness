已思考若干秒

可以把它设计成一套**“先识别仓库类型，再按需生成文档”的文档工厂**。不要一上来就固定所有文档，否则会出现两个问题：一是很多仓库不需要那么多文档，二是同一套结构套在不同仓库上会显得很空。

我建议你的整体设计分成四层。

一、总体设计思路
1）先做仓库分析，再决定生成什么

先扫描代码库，识别这些信息：

技术栈：Java / Spring Boot / 前端 / Python / Go / 单体 / 微服务
仓库类型：业务服务、基础库、SDK、工具脚本、前端项目、平台型项目
代码组织方式：分层架构、DDD、Clean Architecture、模块化单体、微服务
关键资产：API、数据库表、消息队列、任务调度、配置、权限、插件、工作流
复杂度信号：模块数量、包深度、入口数量、调用链长度、外部依赖数量

这个阶段的输出不是文档，而是分析结果画像。
有了画像，后面才知道生成哪些文档。

2）再确定文档集合，而不是固定文档清单

文档分成两类：

通用文档：任何仓库都应该有。
类型文档：根据仓库类型动态生成。

这样你就不会把“SDK 仓库”硬生成成“业务系统文档”，也不会把“前端仓库”强行写数据库设计。

二、分析什么内容

建议把代码库分析内容分成 8 类。

1. 仓库基本信息

回答这个仓库是什么：

项目名称
项目目标
所属业务
主要语言和框架
启动入口
构建方式
发布方式
2. 结构信息

回答仓库怎么组织：

目录树
模块划分
包/目录职责
各层边界
核心入口
核心依赖
3. 架构信息

回答系统怎么运转：

分层方式
模块依赖关系
调用链路
数据流
外部依赖
扩展点
4. 业务/领域信息

回答系统在做什么业务：

核心领域对象
核心状态
业务流程
规则与约束
事件流转
聚合边界
5. 接口信息

回答系统怎么被调用：

HTTP 接口
RPC 接口
消息消费
定时任务
事件订阅
CLI 命令
6. 数据信息

回答数据怎么存：

表结构
字段含义
索引
缓存
文件存储
数据流转路径
7. 运行与运维信息

回答系统怎么部署和排障：

配置项
环境变量
启动流程
健康检查
日志
监控
灰度与回滚
8. 风险与演进信息

回答系统哪里最脆弱：

高风险模块
强耦合点
代码异味
技术债
待确认项
修改建议
三、文档目录结构怎么设计

建议采用“总览 + 专题 + 附录”的目录方式。
目录不要按代码目录来排，而要按“读者理解顺序”来排。

一个比较稳的目录结构如下：

01-项目总览.md
02-仓库结构.md
03-架构设计.md
04-领域与业务.md
05-核心流程.md
06-接口设计.md
07-数据设计.md
08-配置与运行.md
09-部署与运维.md
10-测试与质量.md
11-风险与技术债.md
12-术语表.md

如果仓库比较小，可以只保留前 6～8 份。
如果仓库比较大，可以再拆成二级目录：

docs/
  overview/
  architecture/
  domain/
  api/
  data/
  ops/
  quality/
  appendix/
四、每个文档结构怎么写

下面是我建议的统一模板。
你后续所有文档最好都遵循这个骨架，这样可读性会稳定很多。

1）项目总览

适合所有仓库，必须生成。

结构建议：

文档目的
项目简介
解决的问题
核心能力
技术栈
启动入口
阅读路径
相关文档
2）仓库结构

适合所有仓库，必须生成。

结构建议：

目录树
目录职责说明
关键入口文件
核心模块位置
依赖边界
不建议随意修改的区域
3）架构设计

适合大多数中大型仓库。

结构建议：

架构目标
分层方式
模块划分
模块依赖关系
调用链路
数据流
关键设计决策
架构约束
4）领域与业务

适合业务系统、平台系统、DDD 项目。

结构建议：

业务背景
核心领域对象
状态流转
业务规则
领域边界
领域事件
典型业务场景
5）核心流程

适合任何有主链路的仓库。

结构建议：

流程目标
前置条件
主流程步骤
分支流程
异常处理
关键类与函数
时序图 / 调用图
6）接口设计

适合有对外 API 的仓库。

结构建议：

接口分类
请求方式
入参 / 出参
鉴权方式
错误码
幂等与重试
调用示例
7）数据设计

适合有数据库、缓存、文件、消息的仓库。

结构建议：

数据存储概览
表/集合/Key 设计
字段说明
索引与约束
数据生命周期
读写路径
一致性与容灾
8）配置与运行

适合所有可部署项目。

结构建议：

配置项总览
环境划分
本地启动
测试环境
生产环境
常见配置问题
排障入口
9）部署与运维

适合服务型仓库。

结构建议：

部署架构
启动顺序
健康检查
发布流程
回滚策略
告警与监控
常见故障定位
10）测试与质量

适合工程化程度较高的仓库。

结构建议：

测试分层
单测范围
集成测试范围
Mock 策略
覆盖盲区
风险测试点
CI 质量门禁
11）风险与技术债

这个文档非常适合 AI 自动生成。

结构建议：

高风险模块
强耦合依赖
复杂调用链
重复代码
可改造点
已知问题
待确认事项
12）术语表

适合领域词很多的项目。

结构建议：

业务术语
技术术语
缩写解释
同义词映射
歧义说明
五、是否需要根据不同仓库生成不同文档

结论很明确：必须要分。
但不是完全定制，而是采用“基础文档 + 类型文档”的组合。

1）所有仓库都生成的基础文档

这部分可以固定：

项目总览
仓库结构
风险与技术债
术语表
2）按仓库类型生成的文档

按类型动态选择：

后端业务服务

架构设计
领域与业务
核心流程
接口设计
数据设计
配置与运行
部署与运维

前端项目

架构设计
页面/路由结构
状态管理
组件体系
接口依赖
构建与发布

SDK / 基础库

API 设计
使用示例
扩展点
兼容性
版本变更
测试与发布

工具脚本 / 自动化任务

输入输出
执行流程
参数说明
失败处理
调度方式
运行环境

平台型项目

架构设计
多租户/权限
插件机制
工作流
配置中心
数据模型
运维体系
六、最适合你的实现方式

你的 Claude Code 插件不要直接“生成文档”，而是先生成一个文档计划。

第一步：仓库画像

输出一个结构化结果，例如：

repo_type: backend_service
arch_style: layered
has_api: true
has_db: true
has_queue: false
has_frontend: false
complexity_level: high
第二步：文档清单规划

基于画像决定输出哪些文档：

必出
选出
跳过
第三步：文档模板填充

每份文档走统一模板，只替换内容块。

第四步：交叉引用

文档之间互相链接：

总览 -> 架构
架构 -> 模块
模块 -> 流程
流程 -> 接口 / 数据
风险 -> 相关模块
七、最实用的落地原则

你可以直接把这个原则写进产品设计里：

原则 1：先分析，再生成。
原则 2：先通用，再类型化。
原则 3：文档结构统一，内容按仓库变化。
原则 4：小仓库少生成，大仓库多生成。
原则 5：以“帮助理解和修改代码”为目标，而不是堆文档。

八、给你的最终建议

如果你现在要开始做产品，我建议先定成这套默认策略：

必生成 4 份

项目总览
仓库结构
风险与技术债
术语表

按条件生成 6 份

架构设计
领域与业务
核心流程
接口设计
数据设计
配置与运行

按场景生成 2 份

部署与运维
测试与质量

这样既不会太重，也能覆盖大部分真实需求。

我可以下一步直接
帮你整理成一份Claude Code 插件可落地的“文档生成规范”，包括：仓库分析字段、文档生成决策树、每类文档模板、以及最终的目录树格式。

帮我整理成一份Claude Code插件可落地的文档生成规范
Claude Code 插件 — 代码库文档生成规范（V1）

目标：自动分析代码仓库，生成结构化、可阅读、可维护、可持续更新的工程文档体系。
核心原则：先分析，再规划，再生成。
适用于：后端服务、前端项目、平台型项目、SDK、工具仓库、Agent 项目、RAG 系统等。

一、总体架构设计

整体流程建议拆成四阶段：

代码扫描
   ↓
仓库画像分析
   ↓
文档规划（决定生成什么）
   ↓
文档生成（统一模板）

完整流程：

Repo
 ├── 文件结构扫描
 ├── AST/语义分析
 ├── 配置分析
 ├── 依赖分析
 ├── 调用链分析
 ├── 框架识别
 └── README分析
          ↓
Repository Profile（仓库画像）
          ↓
Documentation Planner（文档规划器）
          ↓
Template Renderer（模板渲染器）
          ↓
Markdown Docs
二、仓库画像规范（Repository Profile）

这是整个系统最核心的数据结构。

插件不要直接生成文档。
先生成“仓库画像”。

1. 基础结构

建议统一 JSON Schema：

{
  "repo_name": "",
  "repo_type": "",
  "primary_language": "",
  "frameworks": [],
  "architecture_style": "",
  "complexity_level": "",
  "entry_points": [],
  "build_tools": [],
  "deployment_type": "",
  "modules": [],
  "capabilities": [],
  "storage": [],
  "communication": [],
  "has_api": false,
  "has_database": false,
  "has_message_queue": false,
  "has_scheduler": false,
  "has_frontend": false,
  "has_auth": false,
  "has_plugin_system": false,
  "has_workflow_engine": false,
  "has_ai_capability": false
}
三、仓库分类体系（Repo Type）

这是决定生成哪些文档的核心。

1. backend_service（后端服务）

识别特征：

Spring Boot
Controller
Service
Repository
MyBatis/JPA
API 接口

生成重点：

架构
API
数据
核心流程
配置运行
2. frontend_app（前端应用）

识别特征：

React/Vue
Router
Store
Components
Vite/Webpack

生成重点：

页面结构
路由
状态管理
组件体系
接口依赖
3. sdk_library（SDK/基础库）

识别特征：

export API
util package
client package
builder/factory

生成重点：

API
使用示例
扩展点
兼容性
4. platform_system（平台型系统）

识别特征：

多模块
权限体系
工作流
插件机制
配置中心

生成重点：

架构
领域模型
权限
插件机制
工作流
5. ai_agent_system（AI Agent系统）

识别特征：

Agent
Tool
Workflow
Prompt
Memory
RAG
Planning

生成重点：

Agent架构
Tool体系
Prompt体系
Workflow
Memory
RAG链路
6. tool_script（工具/脚本）

识别特征：

CLI
shell/python scripts
cron
automation

生成重点：

输入输出
执行流程
参数说明
调度方式
四、文档生成决策树（Documentation Planner）
1. 所有仓库必须生成
01-项目总览.md
02-仓库结构.md
11-风险与技术债.md
12-术语表.md
2. 条件生成规则
生成架构设计

条件：

模块数量 > 3
OR
存在分层结构
OR
存在多服务调用

生成：

03-架构设计.md
生成领域文档

条件：

存在DDD特征
OR
存在复杂业务状态
OR
存在多个聚合

生成：

04-领域与业务.md
生成核心流程

条件：

存在复杂调用链
OR
存在工作流
OR
存在任务执行链

生成：

05-核心流程.md
生成接口设计

条件：

存在Controller
OR
OpenAPI
OR
RPC
OR
消息消费

生成：

06-接口设计.md
生成数据设计

条件：

存在数据库
OR
Redis
OR
ES
OR
对象存储

生成：

07-数据设计.md
生成配置与运行

条件：

存在application.yml
OR
.env
OR
docker-compose

生成：

08-配置与运行.md
生成部署运维

条件：

存在Docker/K8S
OR
CI/CD
OR
Helm

生成：

09-部署与运维.md
生成测试文档

条件：

存在测试目录
OR
CI测试
OR
Mock框架

生成：

10-测试与质量.md
五、文档目录结构规范

建议统一：

docs/
├── overview/
│   ├── 01-项目总览.md
│   └── 02-仓库结构.md
│
├── architecture/
│   ├── 03-架构设计.md
│   ├── 04-领域与业务.md
│   └── 05-核心流程.md
│
├── api/
│   └── 06-接口设计.md
│
├── data/
│   └── 07-数据设计.md
│
├── ops/
│   ├── 08-配置与运行.md
│   └── 09-部署与运维.md
│
├── quality/
│   ├── 10-测试与质量.md
│   └── 11-风险与技术债.md
│
└── appendix/
    └── 12-术语表.md
六、统一文档模板规范

所有文档统一结构。

标准骨架
# 文档标题

## 1. 文档目的

## 2. 适用范围

## 3. 核心结论

## 4. 结构说明

## 5. 详细分析

## 6. 典型场景

## 7. 风险与限制

## 8. 相关文档
七、各文档详细模板
01-项目总览.md
# 项目总览

## 项目简介

## 系统目标

## 核心能力

## 技术栈

## 核心模块

## 启动方式

## 阅读路径

## 相关文档
02-仓库结构.md
# 仓库结构

## 目录树

## 目录职责

## 核心入口

## 核心模块

## 依赖边界

## 关键配置

## 风险区域
03-架构设计.md
# 架构设计

## 架构目标

## 分层架构

## 模块划分

## 模块依赖关系

## 调用链路

## 数据流

## 核心设计决策

## 架构约束
04-领域与业务.md
# 领域与业务

## 业务背景

## 核心领域对象

## 聚合划分

## 状态流转

## 业务规则

## 领域事件

## 边界上下文
05-核心流程.md
# 核心流程

## 流程列表

## 主流程

## 分支流程

## 异常流程

## 时序分析

## 关键类与方法

## 风险点
06-接口设计.md
# 接口设计

## 接口分类

## HTTP接口

## RPC接口

## 消息消费

## 鉴权机制

## 错误码

## 幂等与重试
07-数据设计.md
# 数据设计

## 数据存储概览

## 表结构

## 索引设计

## Redis设计

## 文件存储

## 数据流转

## 一致性策略
08-配置与运行.md
# 配置与运行

## 配置结构

## 环境变量

## 本地运行

## 测试环境

## 生产环境

## 常见问题
09-部署与运维.md
# 部署与运维

## 部署架构

## 容器化部署

## CI/CD流程

## 发布流程

## 回滚策略

## 监控与告警

## 故障排查
10-测试与质量.md
# 测试与质量

## 测试结构

## 单元测试

## 集成测试

## Mock策略

## CI质量门禁

## 覆盖率分析
11-风险与技术债.md
# 风险与技术债

## 高复杂度模块

## 强耦合模块

## 重复代码

## 潜在Bug风险

## 技术债

## 待确认项

## 改造建议
12-术语表.md
# 术语表

## 业务术语

## 技术术语

## 缩写说明

## 同义词映射
八、分析器设计建议（最关键）

你真正的核心竞争力不在“生成 markdown”。

而在：

代码理解能力
=
结构分析
+
依赖分析
+
调用链分析
+
语义抽取
+
领域识别

建议分析器拆成：

1. 文件结构分析器

负责：

目录树
模块划分
包结构
2. AST分析器

负责：

类
方法
注解
继承
调用关系

Java建议：

JavaParser
Spoon

TypeScript建议：

ts-morph

Python建议：

ast
libcst
3. 框架识别器

识别：

Spring Boot
MyBatis
Vue
React
LangChain
FastAPI
Celery
4. 调用链分析器

负责：

Controller → Service → Repository
Workflow链路
Agent执行链
5. 领域识别器

负责：

Entity
Aggregate
Domain Service
Event
State Machine
6. AI语义增强层

LLM只负责：

总结
命名
提炼
风险分析

不要让LLM直接“瞎猜结构”。

九、Agent化设计（非常重要）

建议插件内部采用 Agent Pipeline：

Repo Scan Agent
    ↓
Architecture Agent
    ↓
Domain Agent
    ↓
Flow Agent
    ↓
Risk Agent
    ↓
Doc Writer Agent

不要一个 Prompt 全做完。

十、推荐的最终输出形式

建议最终不仅输出 markdown。

还输出：

1. graph.json

用于：

依赖图
调用图
模块图
2. repo-profile.json

用于：

后续增量分析
文档更新
RAG
3. semantic-index.json

用于：

AI检索
代码问答
智能导航
十一、最推荐的V1落地范围

第一版不要做太大。

建议只支持：

Java Spring Boot
TypeScript Node
Vue/React

只生成：

项目总览
仓库结构
架构设计
核心流程
接口设计
风险与技术债

这样最容易真正落地。

现在有很多项目是个大项目，甚至是claude 插件，coding agent，typescript , 按照你的分类, 要是什么结构呢

对，你现在遇到的是一个非常关键的问题：

“大型 TypeScript monorepo / Claude Code 插件 / Coding Agent 系统，到底该归类成什么结构？”

实际上，你前面那套“backend_service / frontend_app”分类，已经不够了。
因为现在很多 AI 工程项目是：

Monorepo
多语言
多Agent
插件化
Workflow驱动
Tool生态
Prompt体系
MCP集成
Hook机制
Runtime orchestration

这类项目本质上已经不是“普通业务系统”。

它们更接近：

“AI Agent Platform / Agentic Runtime System”

所以你需要升级分类体系。

一、你现在真正需要的是“三维分类体系”

不要只按“项目类型”分类。

应该同时分析：

1. 仓库组织形态
2. 系统运行形态
3. 能力形态
二、新的仓库分类模型（推荐）

建议改成：

Repository Classification
├── Organization Shape（组织形态）
├── Runtime Shape（运行形态）
├── Capability Shape（能力形态）
└── Domain Shape（业务领域）
三、第一维：组织形态（最重要）

这是文档结构生成的核心。

1. single_app（单应用）

典型：

Spring Boot
Next.js
Flask

特点：

单入口
单部署单元
单上下文

文档重点：

分层
API
数据
配置
2. modular_monolith（模块化单体）

典型：

DDD 单体
多模块 Maven
NestJS modules

特点：

单仓库
多业务模块
强领域边界

文档重点：

模块边界
领域模型
模块依赖
3. monorepo（大型Monorepo）

现在大量 AI 项目属于这个。

典型结构：

apps/
packages/
services/
agents/
tools/
infra/

例如：

Claude Code
OpenHands
Continue
Copilot Workspace
Dify
LangChain monorepo

特点：

多应用
多package
多runtime
多语言
多入口

这里必须引入：

“Workspace Architecture 文档”

而不是普通架构文档。

四、Monorepo 应该生成什么文档

这是重点。

Monorepo 文档体系（核心）
01. Workspace 总览

必须有。

回答：

monorepo 为什么存在
apps/packages 如何划分
workspace 依赖原则
package 分类

结构：

workspace/
├── apps/
├── packages/
├── tooling/
├── infra/
└── docs/
02. Package Dependency Graph

必须有。

这是 monorepo 最重要文档之一。

分析：

package 依赖关系
循环依赖
核心基础包
shared package
runtime package

输出：

graph.json
mermaid graph
dependency risk
03. Runtime Architecture

尤其适合 Agent 系统。

分析：

CLI Runtime
Agent Runtime
Tool Runtime
Workflow Runtime
Plugin Runtime

Claude Code 本质上是：

CLI Runtime
    ↓
Agent Runtime
    ↓
Tool Runtime
    ↓
Plugin Runtime
    ↓
External Systems
04. Extension System（扩展系统）

Claude 插件系统非常重要。

需要分析：

Skills
Hooks
MCP
Agents
Commands
Monitors

结构：

Plugin System
├── skills/
├── agents/
├── hooks/
├── commands/
├── monitors/
└── MCP
05. Agent Architecture（AI项目核心）

AI Agent 项目必须有。

分析：

Planner
Executor
Tool Router
Memory
Context Manager
Workflow
Multi-agent
Sub-agent delegation

Claude Code 类项目通常具有：

工具调用循环
多agent orchestration
worktree isolation
task delegation
五、你应该新增一种仓库类型

非常关键。

建议新增：

agentic_platform
六、什么叫 agentic_platform

典型项目：

Claude Code
OpenHands
Continue
RooCode
Cursor extensions
Devin-like systems
AutoGen systems
CrewAI platforms
AI IDE plugins
七、agentic_platform 的本质结构

它不是 MVC。

而是：

Agentic Runtime Architecture
├── Context Layer
├── Planning Layer
├── Execution Layer
├── Tool Layer
├── Memory Layer
├── Workflow Layer
├── Plugin Layer
├── Safety Layer
└── Runtime Layer
八、你插件需要识别的核心结构

对于 Claude 插件 / Coding Agent 项目。

你真正应该分析的是：

1. Context System

分析：

CLAUDE.md
Prompt loading
Context injection
Memory
Semantic retrieval

大型项目里：

root CLAUDE.md
package CLAUDE.md
layered context
2. Agent System

分析：

planner
executor
reviewer
orchestrator
sub-agents
3. Tool System

分析：

Tool registry
Tool router
Permission system
Shell/file/web tools

Claude Code 本身有大量 tool system。

4. Workflow System

分析：

task graph
dependency graph
pipeline
async execution
5. Plugin System

Claude 官方插件结构：

skills/
agents/
hooks/
commands/
.mcp.json
.lsp.json

这个必须生成专门文档。

6. Workspace System

分析：

pnpm workspace
turbo
nx
shared packages
build graph
九、所以你的文档体系应该升级

原来的：

架构设计
接口设计
数据库设计

太传统了。

现在 AI Agent 项目需要：

AI Agent / Claude Plugin 专用文档体系
01-workspace-overview.md

分析：

monorepo结构
apps/packages
workspace boundaries
02-runtime-architecture.md

分析：

runtime loop
agent runtime
task execution
03-agent-system.md

分析：

planner
executor
reviewer
multi-agent
04-tool-system.md

分析：

tool registry
tool routing
permissions
external tools
05-plugin-system.md

分析：

skills
hooks
MCP
commands
monitors
06-context-system.md

分析：

CLAUDE.md
memory
prompt hierarchy
semantic retrieval
07-workflow-system.md

分析：

workflow graph
task orchestration
pipelines
08-package-dependencies.md

分析：

package graph
shared libs
dependency risks
09-devex-and-tooling.md

分析：

turbo
nx
lint
build
CI/CD
10-risk-and-tech-debt.md

分析：

coupling
giant packages
runtime complexity
prompt drift
context overload
十、最终：你的“文档生成器”应该是动态架构

你不应该：

repo_type -> 固定文档

而应该：

repo_features -> capability detection -> document planning

例如：

{
  "is_monorepo": true,
  "has_agent_runtime": true,
  "has_tools": true,
  "has_plugin_system": true,
  "has_workflow_engine": true,
  "has_context_management": true
}

然后生成：

workspace docs
+
agent docs
+
plugin docs
+
workflow docs

而不是传统 CRUD 文档。

十一、最终建议（很重要）

你现在做的东西，本质上不是：

“代码文档生成器”

而是：

“Repository Intelligence System”

它最终应该具备：

Repository Understanding
+
Architecture Intelligence
+
Agent Runtime Analysis
+
Dependency Intelligence
+
Change Impact Analysis
+
Knowledge Extraction

这才是 Claude Code / Cursor / Devin / OpenHands 这一代系统真正的方向。