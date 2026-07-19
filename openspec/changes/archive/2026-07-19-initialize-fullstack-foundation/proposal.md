## Why

当前仓库只有 AI Coding Harness 与 OpenSpec 工作流，还没有可运行的应用工程。需要建立一个版本明确、可独立启动和验证的前后端基础结构，作为后续业务需求与 AI 能力开发的稳定基线。

## Goals

- 在当前单仓库中分别初始化 Next.js 前端和 Spring Boot 后端。
- 固定已经核对过的稳定技术版本，并记录真实可执行的开发命令。
- 提供 MySQL 8.4 本地开发环境、Flyway 迁移基线和 OpenAI-compatible 配置边界。
- 建立最小健康检查与自动化测试，使 Harness 能验证前端、后端和数据库结构。

## Non-goals

- 不在本次初始化中实现用户、权限、聊天、RAG 等业务功能。
- 不接入特定 AI 供应商，不提交任何真实 API Key。
- 不引入组件库、状态管理库、API 代码生成或微服务拆分。
- 不建设生产部署、CI/CD、监控平台或云资源。

## Acceptance Outcomes

- `frontend/` 是可独立安装、检查、测试和启动的 Next.js 应用。
- `backend/` 是可独立测试、打包和启动的 Spring Boot 应用。
- 根目录 Docker Compose 可以启动 MySQL 8.4，并通过健康检查。
- 后端使用 MyBatis-Plus 与 Flyway，且敏感配置全部来自环境变量或本地未跟踪文件。
- Spring AI 使用 OpenAI-compatible 配置，并允许在没有 AI 密钥时启动基础应用。
- 项目文档和 Harness 检查包含新的目录、版本与验证命令。

## What Changes

- 新增 `frontend/`，使用 Next.js 16、React 19、TypeScript、App Router、Tailwind CSS 4、ESLint 和前端测试工具。
- 新增 `backend/`，使用 Java 21、Spring Boot 4.1、Maven、Spring Web MVC、Validation、Actuator、MyBatis-Plus、Flyway、MySQL 与 Spring AI 2。
- 新增根目录 `compose.yaml` 和 `.env.example`，提供 MySQL 8.4 本地基础设施与安全的配置模板。
- 新增最小前端页面、后端健康 API、数据库迁移基线和对应自动化测试。
- 更新仓库 README、AGENTS 与 OpenSpec context，记录真实命令和技术约束。

## Capabilities

### New Capabilities

- `fullstack-project-foundation`: 定义前后端工程、本地数据库、可配置 AI 接口和基础验证能力必须满足的行为。

### Modified Capabilities

无。

## Risks

- Spring Boot 4.1、Spring AI 2 与 MyBatis-Plus 3.5.17 的组合需要通过实际依赖解析和测试验证，而不能只依赖版本号判断。
- OpenAI-compatible 服务对路径、认证头和模型名的兼容程度不完全一致，配置必须集中管理并避免供应商特有逻辑泄漏到业务层。
- 同时初始化两个生态容易引入大量模板噪音，因此必须保持最小结构并删除无价值的默认内容。

## Impact

- 新增两个独立应用目录和根级本地基础设施配置。
- 新增 npm、Maven、Docker 与 MySQL 运行时依赖。
- 更新开发文档、环境变量约定、Git 忽略规则和 Harness 自检。
- 不修改现有 OpenSpec 生成技能的内容，也不产生业务 API 兼容性影响。
