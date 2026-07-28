# ChinaMate 后端开发约定

本文是 Java、Spring Boot 和模块化单体稳定约束的唯一规范源。第三方 Skill 只提供通用方法；其中 Spring Data JPA 示例不适用于本项目。

## RULE-BE-001：以项目事实和当前版本为准

- 当前技术栈为 Java 21、Spring Boot 4.1、Spring AI 2.0 和 Maven；准确版本以 `pom.xml`、Wrapper 和真实依赖树为准。
- 当前依赖、源码、测试和真实输出描述“现在是什么”，已确认 OpenSpec 与强制 Rule 描述“必须是什么”；二者冲突时报告并受控修正。
- Spring Boot API、starter、测试方式或注解行为必须以当前依赖和当前版本官方文档为准，不照搬旧教程或 Skill 示例。

## RULE-BE-002：保持按业务域划分的模块化单体

- 项目保持一个 Maven module、一个 Spring Boot 进程和一个可执行产物，不提前拆微服务或模块间网络通信。
- 顶层业务模块为 `account`、`guide`、`assistant`、`community`、`support`、`moderation`、`notification` 和 `media`；`ProjectApplication`、`config` 与 `health` 是技术入口。
- 禁止建立全局 `controller/`、`service/`、`mapper/` 或 `entity/` 目录；新增代码先确定唯一业务归属。

## RULE-BE-003：模块内部按真实职责分层

- 模块内按需使用 `api`、`application`、`domain`、`infrastructure`，不批量创建空 Service、接口或实现类。
- 主要依赖方向为 `api → application → domain`；`infrastructure` 实现 application/domain 声明的端口并且不依赖 `api`。
- `domain` 不依赖 Spring MVC、MyBatis、Spring AI、`api`、`application` 或 `infrastructure`。
- Controller 只调用应用用例，不直接调用 Mapper、数据库行对象或 `ChatModel`；API DTO、应用结果、领域对象和数据库行对象分别建模。

## RULE-BE-004：跨模块与 shared 边界保持单向和最小

- 跨模块同步调用只能使用目标模块公开的 `application` 契约，禁止访问其他模块的 `api`、领域内部、基础设施、Mapper 或数据库行对象。
- 禁止模块双向依赖；跨域流程由具有明确职责的编排模块发起，不因未来可能需要而引入消息队列。
- `shared` 只接受至少两个模块以相同语义复用且无单一业务归属的技术能力；禁止放入业务 DTO、Mapper、仓储、BaseService、BaseController 或万能 Utils。

## RULE-BE-005：HTTP 接口遵循完整工作区契约

- 新增、修改、评审或排查 HTTP 接口时，必须在完整 AIWorkSpace 读取已确认 OpenSpec 和 `docs/standards/api-development-guidelines.md`。
- Controller 使用明确 Request/Response DTO 和 Bean Validation，不暴露数据库行对象，不创建全局泛型 BaseController，不以普通 PATCH 绕过状态机。
- 错误响应、分页、认证、授权、幂等、并发与状态转换不得凭个人偏好另起一套契约。
- 后端独立 clone 可以处理不改变跨栈契约的局部维护；缺少根级规格时不得新增或改变 HTTP 契约。

## RULE-BE-006：配置、安全和日志默认保守

- 必需依赖使用构造器注入和 `private final`，服务默认无状态；配置使用当前项目的外部化配置方式，秘密不得硬编码或写入代码、测试、文档、接口和日志。
- 密码必须使用业界认可的自适应单向哈希，禁止保存、返回或记录明文密码和密码摘要。
- 日志使用参数化消息，记录稳定业务上下文和安全 trace 标识；禁止记录凭据、token、隐私数据、原始异常 message 或把异常对象无条件传入日志。
- 不因 Skill 推荐新增 JPA、Lombok、Vault、Testcontainers 或其他依赖；新增依赖必须由已确认需求和独立 change 支撑。

## RULE-BE-007：事务和外部能力边界明确

- 事务放在最小必要的应用用例边界并保持短小；多个必须原子成功的数据库写操作必须明确事务策略并以失败回滚测试证明原子性，不能依赖调用者碰巧开启事务。
- 模型调用、网络、文件、对象存储和其他外部 I/O 不得放在数据库事务内；并发更新先明确一致性、幂等和冲突策略，再选择数据库控制方式。
- Spring AI、对象存储和持久化通过所属模块 `infrastructure` 适配器接入，不把大段 Prompt 或供应商 SDK 调用散落在 Controller。
- 只有真实替换边界才定义接口，不机械创建 `XxxService`/`XxxServiceImpl` 成对样板。

## RULE-BE-008：测试与文档共同保护架构

- 可测试的业务变化遵循 RED → GREEN → REFACTOR；领域规则优先纯单元测试，应用用例测试端口编排，API 测试覆盖校验、权限、状态码和错误契约。
- 模块或依赖边界变化运行 `./mvnw -Dtest=ArchitectureRulesTests test`，业务行为运行相关测试；数据库行为按 `database-conventions.md` 选择真实集成验证。
- 新增模块或修改边界时同步更新 `docs/architecture.md` 和架构测试。
- 纯文档和 AI 治理变更运行 `bash scripts/check-agent-governance.sh` 与 `git diff --check`；默认不运行无关 build，并明确记录未验证项。

## RULE-BE-009：后端交付报告工程实践合规

- 后端实现前必须识别任务适用的 Java、Spring Boot、事务、分层、持久化、Flyway、日志和安全约束，不得把只列出 Rule/Skill 路径视为已遵循。
- 完成报告必须列出任务直接相关的工程实践检查结果、实际验证与未验证项；偏离默认技术路径时必须给出已确认设计依据、限定范围、替代方案取舍和验证结果。
- QA 必须独立验证适用工程实践；Spec Reviewer 必须把代码对项目 Rules/技术基线的结论与业务 Spec 对账分开报告。

## RULE-BE-010：自定义 SQL 统一使用 Mapper XML

- 新增或实质修改的 MyBatis 自定义 SQL 必须遵循 `database-conventions.md` 的 Mapper XML 约束；Java Mapper 接口只保留方法签名和不承载 SQL 文本的注解，不新增 SQL 注解或 Provider 注解。
- MyBatis-Plus `BaseMapper<T>` 自动 CRUD 继续允许，不得为了形式统一重复编写等价 XML statement。
- 后续 change 修改存量注解 statement 的 SQL 文本、参数、结果映射或数据库行为时，必须同步迁入 XML；只修改注释、格式或与 SQL 无关的 Java 内容不触发迁移。
