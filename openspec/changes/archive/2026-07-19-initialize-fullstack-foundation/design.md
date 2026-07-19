## Context

仓库当前只有 Harness、OpenSpec 及文档，没有应用源码。用户已经明确选择 Next.js + React + Tailwind CSS 作为前端，Spring Boot + MySQL + MyBatis-Plus + Spring AI 作为后端，并确认 AI 层采用 OpenAI-compatible 可配置接口、MySQL 通过 Docker Compose 提供。

本机具备 Node.js 22.12、Java 21.0.8 和 Maven 3.9.16。2026-07-19 核对的稳定版本是 Next.js 16.2.10、React 19.2.7、Tailwind CSS 4.3.3、Spring Boot 4.1.0、Spring AI 2.0.0、MyBatis-Plus Spring Boot 4 Starter 3.5.17。

## Goals / Non-Goals

**Goals:**

- 形成 `frontend/` 与 `backend/` 两个职责清楚、可独立工作的工程。
- 根目录提供一致的本地环境模板、MySQL Compose 配置和全栈启动说明。
- 前后端都有最小可观察行为与自动化测试，而不只是空脚手架。
- AI 配置兼容 OpenAI API 协议，并且没有密钥时基础应用仍可启动。
- 数据库结构由 Flyway 管理，MyBatis-Plus 只负责运行期数据访问。

**Non-Goals:**

- 不定义具体业务领域、业务表或业务接口。
- 不实现 AI 对话端点，不调用真实模型。
- 不引入 UI 组件库、ORM、缓存、消息队列或认证框架。
- 不把两个工程强行纳入同一种构建工具，也不增加无必要的 monorepo 编排器。

## Decisions

### 1. 使用简单的双工程单仓库结构

根目录使用 `frontend/`、`backend/` 和 `compose.yaml`。前端由 pnpm 管理，后端由 Maven Wrapper 管理，二者通过 HTTP/JSON 连接。

选择该方案是因为用户明确要求分别建立前后端文件夹，而且跨语言项目没有必要引入 Turborepo、Nx 或 Maven 多模块。替代方案 `apps/web` + `apps/api` 更适合已有多个应用的仓库，但当前只有一前一后，会增加命名层级而没有实际收益。

### 2. 前端采用 Next.js App Router 的最小严格基线

前端固定 Next.js 16.2.10、React 19.2.7、TypeScript、App Router、Tailwind CSS 4.3.3 和 ESLint。默认使用 Server Components；只有需要浏览器状态或事件的组件才添加 `"use client"`。

使用 pnpm 和 `pnpm-lock.yaml` 固定依赖。测试采用 Vitest、Testing Library 与 jsdom，至少覆盖首页可观察内容。暂不加入组件库和全局状态库，避免在没有产品需求时预设 UI 架构。

### 3. 后端采用 Java 21 + Spring Boot 4.1 的单体分层基线

后端使用 Maven Wrapper、Java 21、Spring Boot 4.1.0。基础依赖包括 Spring Web MVC、Validation、Actuator、MyBatis-Plus Spring Boot 4 Starter 3.5.17、MySQL Connector/J、Flyway MySQL 和 Spring AI BOM 2.0.0。

MyBatis-Plus 必须使用专门适配 Spring Boot 4 的 `com.baomidou:mybatis-plus-spring-boot4-starter`，不得误用 Boot 3 starter，也不再直接依赖原生 `mybatis-spring-boot-starter`。本次基线只建立配置能力，不在没有业务模型时创建 `BaseMapper`、实体类或分页插件。

包名采用 `com.heness.project`，初始只建立 application、common/config 和 health 等必要边界，不提前制造 controller/service/mapper/domain 的空目录。对外提供 `/api/health` 作为应用级最小契约，同时保留 `/actuator/health` 供基础设施探测。

后端测试使用 JUnit 5。普通上下文/HTTP 测试不得依赖本机 MySQL；数据库集成测试后续使用 Testcontainers，避免 H2 与 MySQL 方言不一致。

### 4. 使用 Flyway 管结构、MyBatis-Plus 管查询

MySQL 使用 `mysql:8.4`，Compose 提供健康检查与命名数据卷。后端 datasource 全部来自环境变量。Flyway migration 目录纳入版本控制，首个 migration 只建立迁移基线，不虚构业务表。

不使用 Hibernate/JPA 自动建表，避免出现 Flyway 与 ORM 双重管理 schema。MyBatis-Plus 的 mapper XML 固定在 `classpath:/mapper/**/*.xml`，Java mapper 通过 `@Mapper` 发现；通用 CRUD 只在真实业务 Mapper 中按需继承 `BaseMapper<T>`。

### 5. Spring AI 使用 OpenAI-compatible 配置边界

配置项统一映射为 `AI_BASE_URL`、`AI_API_KEY` 和 `AI_MODEL`，供应商差异不进入业务代码。AI 能力默认关闭或延迟装配，使未配置 API Key 的开发者仍能启动并验证基础后端；显式启用 AI 时必须校验必要配置并快速失败。

Spring AI 通过 BOM 管理版本，具体 OpenAI 模型模块不得单独漂移版本。本次只验证配置可以被绑定，不暴露会产生真实模型调用或费用的接口。

### 6. 配置与密钥采用模板化管理

根目录 `.env.example` 只包含无敏感值的变量说明，真实 `.env` 保持 Git 忽略。Compose 可从 `.env` 读取数据库值；后端也允许直接从 shell 环境读取。前端仅允许 `NEXT_PUBLIC_` 前缀变量进入浏览器，AI Key 和数据库密码绝不进入前端配置。

### 7. 反馈回路分层执行

- 前端：`pnpm lint`、`pnpm test`、`pnpm build`。
- 后端：`./mvnw test`、`./mvnw package`。
- 基础设施：`docker compose config`，有 Docker 时再运行 MySQL 健康检查。
- 仓库：`./scripts/check-harness.sh` 同时检查 Harness 和新工程关键文件。

初始化实现阶段会实际运行依赖安装和测试；若因网络、Docker 未安装或外部服务不可用而无法验证，必须报告准确阻塞点。

## Data Flow

```text
Browser
  │
  ▼
Next.js :3000
  │  HTTP/JSON (NEXT_PUBLIC_API_BASE_URL)
  ▼
Spring Boot :8080
  ├── /api/health
  ├── MyBatis-Plus ─────────▶ MySQL :3306
  └── Spring AI (disabled by default)
           └───────────────▶ OpenAI-compatible endpoint
```

## Risks / Trade-offs

- **新主版本组合可能存在生态兼容问题** → 依赖解析后运行真实测试；如果官方 starter 不兼容，不静默降级，先更新设计并说明证据。
- **OpenAI-compatible 并不代表所有供应商完全一致** → 首期只承诺 base URL、API key、model 三项通用配置，供应商扩展以后通过独立 change 增加。
- **数据库使本地启动多一个前置步骤** → 使用 Compose、健康检查和 `.env.example` 降低配置成本；基础后端测试与数据库解耦。
- **两个构建生态需要分别维护** → 在根 README 集中列出命令，但保留各工程原生工具，不引入额外编排框架。
- **固定最新稳定版带来较少社区案例** → 优先依据官方元数据与实际编译结果，不照搬旧版本教程。

## Migration / Rollback

这是 greenfield 初始化，没有线上迁移。实施顺序为基础设施配置、前端、后端、文档与 Harness 更新。若某个工程初始化失败，可只回退该目录及对应文档；不得删除现有 `openspec/`、`.codex/`、`.claude/` 或 Harness 文件。

## Open Questions

无阻塞性问题。具体业务域、首个 AI 用例、认证方式和生产部署策略留给后续独立变更。
