## Why

ChinaMate 即将从全栈基础工程进入账号、攻略、AI 助手和社区等真实业务开发；如果继续按全局技术分层或让业务代码自由互相依赖，一个人配合 AI Coding 时很容易出现上下文膨胀、跨域误改和巨型 Service。现在需要在首个业务模块落地前建立可执行的模块化单体边界，同时保持单一 Spring Boot 部署单元和较低运维成本。

## What Changes

- 在 `backend/` 建立按业务能力组织的模块化单体约定，首批模块边界为 `account`、`guide`、`assistant`、`community`、`support`、`moderation`、`notification` 和 `media`。
- 统一每个业务模块的内部职责层次：`api`、`application`、`domain`、`infrastructure`，并定义允许的依赖方向和跨模块协作方式。
- 限制 `shared` 只承载跨模块技术能力，禁止业务对象、业务状态和万能工具类进入共享区。
- 为现有后端基础代码确定归属，保持 `/api/health`、MyBatis-Plus、Flyway 和 OpenAI-compatible 默认关闭等既有可观察行为不变。
- 增加中文后端架构说明、包级说明和自动化架构测试，使 AI 生成代码时能够发现违反模块边界的依赖。
- 保持单一 Maven module、单一 Spring Boot 运行产物和单一 MySQL 数据源，不引入微服务、Spring Data JPA、消息队列或新的运行时基础设施。

## Goals

- 让一个业务变更主要在一个领域模块内完成，并能通过明确入口进行跨模块协作。
- 让 Controller、应用用例、领域规则和外部适配器之间的职责与依赖方向可检查。
- 让未来业务模块的目录、命名、测试和资源位置有统一模板，降低 AI Coding 的检索范围和误改风险。
- 在不拆分部署单元的前提下，为未来有真实证据时独立拆出 AI 或媒体处理能力保留边界。

## Non-Goals

- 不在本变更中实现注册登录、攻略、AI 问答、社区或运营后台业务。
- 不冻结数据库表结构、API URL、请求响应字段或错误码。
- 不修改产品名称或当前根包名 `com.heness.project`。
- 不拆分 Maven module、Git 仓库、数据库或部署单元。
- 不引入 Spring Modulith、事件总线、消息队列、Event Sourcing 或完整 CQRS。
- 不修改 `frontend/` 内部代码。

## Acceptance Outcomes

- 后端存在一份与 PRD 领域一致的中文模块地图，并明确各模块负责和禁止负责的内容。
- 新增业务代码有明确的 `api → application → domain` 依赖方向，基础设施通过端口连接应用或领域层。
- 跨模块不得直接访问对方的 Mapper、数据库行对象或内部实现，并由自动化测试覆盖可静态检查的边界。
- `./mvnw test`、`./scripts/check-harness.sh`、OpenSpec strict validate 和 `git diff --check` 均通过。
- 现有 `/api/health` 契约、默认不连接 MySQL、默认不创建 `ChatModel` 的行为保持不变。

## Capabilities

### New Capabilities

- `backend-modular-monolith`: 定义后端业务模块、模块内职责层次、依赖方向、共享能力边界、资源组织和架构验证要求。

### Modified Capabilities

无。

## Impact

- 主仓库：新增本 change 的 proposal、spec、design 和 tasks；实现阶段按需补充跨项目架构文档与 Harness 检查。
- `backend/` submodule：新增模块骨架、包级说明和架构测试，并对现有基础代码进行保持行为不变的归位整理。
- `frontend/` submodule：不修改。
- API 与数据：不新增业务接口，不创建或修改业务表，不改变现有健康检查契约。
- 依赖：允许在设计确认后增加仅测试范围的架构约束依赖；不新增运行时基础设施依赖。

主要风险是目录和层次过度设计，导致首个业务功能需要创建大量样板代码；通过只建立顶层模块边界、按实际用例逐步创建内部类、禁止机械生成接口与 `Impl` 来控制。另一个风险是自动化架构检查覆盖不完整；文档、包可见性、代码评审和测试共同作为边界门禁，不把单一工具视为完整证明。
