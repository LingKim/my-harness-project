## Context

`backend/` 当前是一个很小的 Java 21、Spring Boot 4.1 单 Maven module，包含健康检查、Web 配置、MyBatis-Plus/Flyway 基线和可选的 Spring AI OpenAI-compatible 配置。ChinaMate PRD 已经识别账号与旅行上下文、结构化攻略、AI 助手、任务型社区、问题升级、治理、通知和媒体等业务能力，但数据库结构与 API 契约尚未冻结。

开发主体是一个人配合 AI Coding。当前最主要的架构风险不是分布式容量，而是后续业务代码按全局 `controller/service/mapper` 堆积后形成巨型目录、巨型 Service、跨领域数据访问和难以控制的 AI 修改范围。本设计在不增加运行时部署复杂度的前提下，用 Java package、包可见性、文档和自动化测试建立模块边界。

本设计同时受以下事实约束：数据访问继续使用 MyBatis-Plus 3.5.17，数据库结构只由 Flyway 管理；不采纳 `java-springboot` Skill 中的 Spring Data JPA、JPA entity、`JpaRepository`、Criteria API 或 `@DataJpaTest` 建议；AI 默认关闭，基础测试不能访问外部模型服务。

## Goals / Non-Goals

**Goals:**

- 保持一个 Maven module、一个 Spring Boot 进程和一个可执行产物。
- 用业务能力而非技术类型划分顶层 package，缩小每次业务变更和 AI Coding 的上下文范围。
- 为模块内部建立轻量且一致的 `api`、`application`、`domain`、`infrastructure` 职责和依赖方向。
- 禁止模块直接访问其他模块的 Mapper、数据库行对象和基础设施实现。
- 通过测试范围的架构规则、包级说明和中文架构文档让边界可发现、可验证。
- 保持现有健康检查、默认数据库关闭和默认 AI 关闭行为不变。

**Non-Goals:**

- 不实现任何 ChinaMate 业务用例或创建业务数据表。
- 不确定 API URL、DTO、错误码和业务状态机。
- 不建立多 Maven module、微服务、独立数据库或消息基础设施。
- 不要求每个用例都创建接口和 `Impl`，也不预建没有真实类的四层空目录。
- 不使用 Spring Data JPA、Spring Modulith、Event Sourcing 或完整 CQRS。
- 不修改根包名；产品名确认后的重命名必须单独评估。

## Decisions

### 1. 使用单 Maven module 的模块化单体

后端继续只有一个 `pom.xml` 和一个 Spring Boot 启动类。业务边界由 `com.heness.project` 下的顶层 package 表达，而不是由 Maven module、Git 仓库或进程表达。

首批业务模块为：

| 模块 | 职责 |
| --- | --- |
| `account` | 账号、凭据、会话、用户偏好和旅行上下文 |
| `guide` | 结构化攻略、双语版本、来源、收藏和反馈 |
| `assistant` | AI 会话、消息、知识引用、风险、额度和解决反馈 |
| `community` | 社区问题、回答、单层评论、最佳回答和解决状态 |
| `support` | AI 转社区草稿、官方求助渠道和升级流程编排 |
| `moderation` | 举报、审核、内容处置、账号限制和审计记录 |
| `notification` | 站内通知和未读状态 |
| `media` | 图片校验、存储引用、保留期限和删除编排 |

`ProjectApplication`、`config` 和 `health` 保留为技术入口；`shared` 只有出现两个以上模块确实复用且没有业务归属的技术能力时才创建。现有 `config.ai` 将归入 `assistant.infrastructure`，因为它是 AI 模型外部适配器，而不是全局业务无关配置。

备选方案是全局 `controller/service/mapper` 分层。它初期文件少，但会把无关业务放进同一目录，使跨域依赖难以识别，因此不采用。多 Maven module 能提供更强编译隔离，但当前规模下会增加构建、依赖暴露和 AI 修改成本，暂不采用。

### 2. 模块内部按职责层次组织，但按需创建

每个业务模块允许以下 package：

```text
<module>/
├── api/             # HTTP 协议、校验、Request/Response 和身份上下文转换
├── application/     # 用例编排、事务边界、命令、查询、应用事件和端口
├── domain/          # 业务对象、值对象、状态转换、策略和仓储端口
└── infrastructure/  # MyBatis、Spring AI、对象存储及其他外部适配器
```

依赖方向为：

```text
api ───────▶ application ───────▶ domain
                    ▲                ▲
                    └─ infrastructure┘
```

- `domain` 不依赖本模块的 `api`、`application` 或 `infrastructure`，也不直接依赖 Spring MVC、MyBatis 或 Spring AI。
- `application` 可以依赖本模块 `domain`，但不依赖 `api` 或具体 `infrastructure`。
- `api` 通过应用用例工作，不直接访问 Mapper、数据库行对象或 `ChatModel`。
- `infrastructure` 实现应用层或领域层声明的端口，不依赖 `api`。
- API DTO、应用结果、领域对象和数据库行对象分离，禁止数据库对象直接作为 HTTP 契约。

这些 package 只在出现真实类时创建；顶层模块使用 `package-info.java` 记录职责，避免一次生成 32 个没有价值的空层次文件。

备选方案是完整 Clean Architecture，为每个操作创建输入端口、输出端口、接口和实现。它能强化隔离，但会给单人 MVP 带来大量样板代码，因此只在存在替换实现或外部边界时定义接口。

### 3. 跨模块只通过应用入口协作

一个模块可以依赖另一个模块公开的 `application` 契约，但不得依赖对方的 `api`、`domain`、`infrastructure`、Mapper 或数据库行对象。核心业务流程使用同步应用调用；通知、埋点等非核心副作用可以在事务成功后通过应用事件触发，但本变更不引入消息队列或跨进程事件系统。

例如 `support` 将来通过 `assistant.application` 读取可公开的会话摘要，通过 `community.application` 创建待确认问题草稿，而不是读取 AI 消息表或调用社区 Mapper。若某个流程需要跨模块原子修改，事务边界仍位于发起方应用用例中，并保持短事务。

备选方案是让模块共享数据库实体或直接调用 Mapper，代码更短但会绕过业务不变量并形成隐式耦合，因此禁止。立即使用异步消息则会引入最终一致性、重试和运维成本，当前没有证据支持。

### 4. `shared` 不是业务回收站

`shared` 仅允许统一 Web 错误、认证上下文、可观测性、时间和标识等确实跨模块的技术能力。业务枚举、业务 DTO、领域对象、仓储、Mapper、`BaseService`、`BaseController` 和无明确语义的 `Utils` 不得进入 `shared`。

复用代码在首次出现时保留在所属模块；只有至少两个模块存在相同语义且无法合理归属时才上移。该规则接受少量临时重复，以换取业务边界清晰。

### 5. 资源按模块定位，数据库仍由 Flyway 唯一管理

后续 MyBatis XML 使用 `src/main/resources/mapper/<module>/`，Prompt 使用 `src/main/resources/prompts/<module>/`，国际化消息使用标准 `messages` 资源。业务表结构只能通过新的 Flyway migration 创建或修改，不能通过 MyBatis、JPA、启动脚本或手工未版本化 DDL 管理。

本变更只建立资源放置规则，不新增业务 XML、Prompt 或 migration。

### 6. 使用测试范围的架构规则作为机器门禁

实现阶段在 `backend/pom.xml` 增加经过版本核对的 ArchUnit JUnit 5 测试依赖，仅用于测试，不进入运行时产物。架构测试至少覆盖：

- 业务模块的层次依赖方向。
- 跨模块依赖只能指向目标模块的应用契约。
- API 不得依赖 Mapper、数据库行对象或 Spring AI `ChatModel`。
- Domain 不得依赖 Spring MVC、MyBatis、Spring AI 或其他模块内部实现。
- 项目不得引入 JPA entity、Repository 或 JPA 测试模式。

ArchUnit 只能检查静态依赖，不能证明事务、安全或业务行为正确；它与包可见性、模块文档和常规测试共同构成门禁。备选方案是只靠文档评审，但单人 AI Coding 容易在后续会话中漂移，因此不采用。

### 7. 保持既有外部行为兼容

现有 `/api/health` 路径和响应保持不变；AI 配置移动 package 时，`app.ai` 配置前缀、启用条件和缺失配置失败行为保持不变；默认测试仍不得连接 MySQL 或创建会访问外部服务的 `ChatModel`。只做 package 和测试层面的迁移，不修改公开协议。

### 8. 后端独立仓库保留本地 AI Coding 上下文

`backend/` 是可独立检出的 Git 仓库，不能假设所有 AI 会话都从主仓库根目录进入。实现阶段新增 `backend/AGENTS.md`，记录模块边界、依赖规则、MyBatis-Plus/Flyway 技术约束、测试命令和事实优先级；`backend/docs/architecture.md` 保存面向开发者的完整模块地图，`backend/README.md` 链接该文档。

根级 `AGENTS.md` 继续负责三个仓库协作、OpenSpec 和 gitlink 流程，后端局部规则负责后端代码组织。两者同时存在时共同生效，局部规则不得降低根级安全与验证要求。

## Risks / Trade-offs

- [模块边界划分早于完整数据/API 设计，后续可能调整] → 顶层模块按 PRD 稳定业务能力划分，内部对象和接口按真实 change 逐步创建；边界调整必须更新本设计和架构测试。
- [四层结构被机械套用，产生大量样板代码] → 只在真实类型出现时创建子 package，不要求每个用例都有接口和 `Impl`。
- [跨模块应用依赖仍可能形成环] → 架构测试禁止循环；跨域编排优先放在 `support` 等明确的流程模块，而不是双向调用。
- [`shared` 逐渐膨胀] → 采用“至少两个模块、语义相同、无法归属”三项准入条件，并在架构文档中登记共享能力。
- [ArchUnit 新增测试依赖] → 固定并核对兼容 Java 21 的版本，仅使用 test scope；若依赖不可用，可以回滚该依赖和测试而不影响运行时。
- [移动 AI 配置导致组件扫描或测试失效] → 先建立能以正确原因失败的测试，再移动类，并运行现有 AI 配置和完整后端测试验证。
- [模块化单体未来无法满足独立扩缩容] → 保持外部能力端口和数据归属清晰；只有出现独立团队、发布、故障隔离或扩缩容证据时再提出拆分 change。

## Migration Plan

1. 记录主仓库及两个 submodule 的干净基线，确认后端位于可提交分支。
2. 先增加架构测试和必要的 test-scope 依赖，得到针对缺失模块声明或现有 AI 配置归属的预期失败。
3. 增加顶层业务模块 `package-info.java`，将现有 AI 配置归入 `assistant.infrastructure`，同步移动对应测试并保持配置契约。
4. 增加 `backend/AGENTS.md` 与 `backend/docs/architecture.md`，更新 `backend/README.md`，说明模块地图、层次、依赖、新增代码落点和独立仓库验证方式。
5. 运行后端测试、Harness、OpenSpec strict validate 和差异检查，复核前端没有变化。
6. 只有用户明确授权时，先提交并推送 `backend/`，验证远端提交可达，再更新和提交主仓库 gitlink。

回滚时恢复 AI 配置原 package，删除模块 `package-info.java`、架构测试、test-scope 依赖和文档更新即可；本变更没有数据库迁移、数据兼容或接口回滚问题。

## Open Questions

无。业务模块内部的实体、API、表结构和状态机由后续独立 OpenSpec change 决定。
