---
name: java-springboot
description: 为 ChinaMate 编写、评审或重构 Java 21 与 Spring Boot 4.1 后端代码，覆盖模块化单体、HTTP API、配置、事务、日志、安全、MyBatis-Plus、Flyway 和分层测试。涉及 backend/ 中的 Java、Spring Boot、Web、持久化或测试任务时使用。
---

# ChinaMate Java 与 Spring Boot

以当前项目事实交付可维护、可测试的后端实现。不要把通用框架习惯覆盖到已确认 OpenSpec、项目 Rules 或当前依赖之上。

## 开始

1. 读取根 `AGENTS.md`、`backend/AGENTS.md`、已确认 OpenSpec、当前 `pom.xml`、相关源码和测试。
2. 完整读取 `.codex/rules/backend-conventions.md`；涉及数据库时再读取 `.codex/rules/database-conventions.md` 和 `.codex/skills/mysql/SKILL.md` 的直接相关内容。
3. 涉及 Spring Boot 4.1 API、starter、注解或测试行为时，优先查当前依赖与当前版本官方文档，不使用训练数据猜测。
4. 修改前检查 backend 分支和 dirty 状态，确认业务模块、依赖方向、接口合同与允许写入范围。
5. 可测试行为按 RED → GREEN → REFACTOR 推进；完成后运行与风险相称的目标测试和架构测试。

## 模块与分层

- 按业务域组织顶层模块，不建立全局 `controller`、`service`、`mapper` 或 `entity` 目录。
- 模块内按真实需要使用 `api`、`application`、`domain`、`infrastructure`，不批量创建空接口和实现类。
- 保持 `api → application → domain`；`infrastructure` 实现 application/domain 声明的端口且不依赖 `api`。
- `domain` 保持纯 Java，不依赖 Spring MVC、MyBatis-Plus、Spring AI 或基础设施类型。
- 跨模块只调用目标模块公开的 `application` 契约；数据库行对象、Mapper 和供应商 SDK 不跨模块泄露。

## Spring 组件与配置

- 必需依赖使用构造器注入并声明为 `private final`；服务默认无状态。
- 只在真实容器边界使用 `@Service`、`@Component`、`@Repository`、`@Configuration` 等 stereotype，不用注解掩盖不清晰的职责。
- 使用外部化配置和类型安全属性绑定；秘密不得硬编码、写入前端变量、测试快照、响应或日志。
- 不为通用建议新增依赖；新增 starter、库或测试基础设施必须来自已确认 change 和当前依赖证据。

## HTTP API

- 新增或改变 HTTP 行为时读取 `docs/standards/api-development-guidelines.md` 和已确认接口合同。
- Controller 只负责协议适配、Bean Validation、身份上下文和调用应用用例；不直接访问 Mapper、数据库对象或外部模型。
- Request/Response DTO、应用结果、领域对象和数据库持久化对象分别建模，只传递边界真正需要的字段。
- 统一错误响应使用项目既有 `ProblemDetail` 契约；同时验证客户端响应和服务端日志，禁止返回或记录原始异常 message。
- 认证、授权、分页、幂等、并发和状态转换以规格为准，不创建局部私有协议。

## 事务与外部能力

- 把事务放在最小必要的应用用例边界；多个必须原子成功的数据库写操作必须明确事务策略并测试失败回滚。
- 事务方法保持短小；模型、网络、文件、对象存储和其他外部 I/O 放在数据库事务之外。
- 不用宽泛类级事务掩盖读写差异；只读查询是否使用事务根据一致性需求和实际数据库行为决定。
- 并发更新必须先明确一致性、幂等和冲突策略，再选择唯一约束、条件更新、乐观控制或显式锁。

## MyBatis-Plus 与 Flyway

- 业务表的常规 CRUD、条件查询和分页默认通过所属模块 `infrastructure` 中的 MyBatis-Plus Mapper 或适配器完成。
- Mapper 可以按需继承 `BaseMapper<T>`；`BaseMapper<T>` 自动 CRUD 无需重复创建 XML statement。
- 新增或实质修改的自定义 SQL 必须写入 Mapper XML，禁止在 Java Mapper 接口使用 SQL 注解或 Provider 注解承载 SQL；XML 必须按业务目录存放，保持 `namespace`、statement ID 与 Mapper 接口对应，并显式列出字段、安全绑定参数。
- 后续 change 实质修改存量注解 statement 的 SQL 文本、参数、结果映射或数据库行为时，必须在同一 change 中迁入 Mapper XML；纯注释、格式或与 SQL 无关的 Java 修改不触发迁移。
- Controller、domain、跨模块调用和公开 application 结果不得暴露 Mapper 或数据库持久化对象。
- 数据库结构只通过新的受版本管理 Flyway migration 修改；Mapper、启动脚本和手工 DDL 不负责建表。
- 直接使用 `JdbcTemplate` 或 `NamedParameterJdbcTemplate` 必须有已确认设计依据，限定在所属模块 `infrastructure`，说明 MyBatis-Plus 不适用原因、替代方案取舍，并提供等价测试；不得把内联 JDBC SQL 作为未记录的默认路径。

## 日志、安全与异常

- 使用参数化日志，记录稳定业务上下文和安全 trace 标识；不拼接日志字符串。
- 不记录密码、摘要、token、Cookie、凭据、隐私数据或原始异常 message；只记录安全分类和必要上下文。
- 密码采用当前项目批准的自适应单向摘要器；输入校验不能替代认证、授权和数据库约束。
- SQL 业务值使用安全参数绑定；动态标识符必须来自服务端封闭枚举到固定 SQL 的映射。

## 测试

- 领域规则优先使用纯 JUnit 5 单元测试，不启动 Spring 上下文。
- 应用测试使用端口替身验证用例编排、事务结果和失败路径。
- API 测试覆盖请求校验、权限、状态码、错误契约和敏感数据最小化。
- Mapper、migration、唯一约束、锁和事务行为需要数据库证据时，使用与 MySQL 8.4 相符的受控集成环境。
- 模块或依赖边界变化运行 `./mvnw -Dtest=ArchitectureRulesTests test`；业务行为运行最接近改动的目标测试，默认不运行无关 build。

## 完成检查

报告以下实际结果，不以文件引用代替执行：

- 已确认 Spec、适用 Rules、Skills 与当前官方文档。
- 业务模块、依赖方向、DTO/领域/持久化对象边界。
- 构造器注入、事务原子性、异常、日志和安全处理。
- MyBatis-Plus Mapper、Flyway migration、参数绑定及任何 Spring JDBC 例外依据。
- 实际测试命令、结果、未验证项、残余风险和下一交接建议。
