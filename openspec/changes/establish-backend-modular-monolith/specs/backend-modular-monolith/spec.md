## ADDED Requirements

### Requirement: 后端保持单部署单元的模块化单体
后端 SHALL 保持一个 Maven module、一个 Spring Boot 应用入口和一个可执行产物，并 SHALL 通过 Java 顶层 package 而不是独立进程表达业务模块边界。

#### Scenario: 开发者构建后端
- **WHEN** 开发者使用 Maven 构建后端
- **THEN** 构建只生成一个 Spring Boot 应用产物
- **AND** 不需要启动模块间网络通信或额外运行时基础设施

#### Scenario: 开发者识别业务能力
- **WHEN** 开发者或 AI 代理查看 `com.heness.project` 下的业务代码
- **THEN** 可以按 `account`、`guide`、`assistant`、`community`、`support`、`moderation`、`notification` 和 `media` 顶层 package 定位所属业务能力

### Requirement: 业务模块按职责层次组织
每个业务模块 SHALL 按需使用 `api`、`application`、`domain` 和 `infrastructure` package 表达协议入口、用例编排、业务规则和外部适配器；系统 MUST NOT 为尚无真实类型的层次批量创建无业务内容的占位类。

#### Scenario: 新增 HTTP 用例
- **WHEN** 后续 change 新增一个 HTTP 业务用例
- **THEN** HTTP Request、Response、校验和 Controller 位于所属模块的 `api` 范围
- **AND** 用例编排与事务边界位于所属模块的 `application` 范围
- **AND** 业务状态与业务不变量位于所属模块的 `domain` 范围
- **AND** MyBatis、模型服务或对象存储实现位于所属模块的 `infrastructure` 范围

#### Scenario: 模块尚无某层实现
- **WHEN** 业务模块当前没有某个职责层次的真实类型
- **THEN** 系统不要求创建对应的空 Service、接口、实现类或占位配置

### Requirement: 模块内部依赖方向受约束
业务模块 SHALL 遵循 `api → application → domain` 的主要依赖方向，`infrastructure` SHALL 通过应用层或领域层声明的端口提供外部实现；领域层 MUST NOT 依赖 API、应用编排或基础设施实现。

#### Scenario: Controller 调用业务能力
- **WHEN** Controller 处理一个有效请求
- **THEN** Controller 通过所属模块的应用用例执行业务
- **AND** Controller 不直接调用 MyBatis Mapper、数据库行对象或 Spring AI `ChatModel`

#### Scenario: 领域规则被测试
- **WHEN** 自动化测试加载领域对象和领域规则
- **THEN** 领域规则无需启动 Spring MVC、MyBatis、Spring AI 或外部服务即可执行

#### Scenario: 基础设施实现外部端口
- **WHEN** MyBatis、模型服务或对象存储适配器接入应用
- **THEN** 适配器实现应用层或领域层定义的明确端口
- **AND** 应用层不依赖具体适配器类型

### Requirement: 跨模块协作只使用公开应用契约
一个业务模块 MUST 只通过目标模块公开的应用契约进行跨模块同步协作，并 MUST NOT 直接依赖目标模块的 API、领域内部、基础设施、Mapper 或数据库行对象。

#### Scenario: AI 会话转为社区草稿
- **WHEN** 后续 `support` 用例需要把 AI 会话转换为社区问题草稿
- **THEN** `support` 通过 `assistant` 的应用契约取得允许公开的会话摘要
- **AND** 通过 `community` 的应用契约创建草稿
- **AND** 不直接查询 AI 消息表或调用社区 Mapper

#### Scenario: 检测到模块循环依赖
- **WHEN** 自动化架构测试发现两个业务模块相互依赖内部实现或形成不允许的依赖环
- **THEN** 后端测试失败并指出涉及的模块依赖

### Requirement: 共享能力保持最小且不包含业务归属
`shared` 范围 SHALL 只保存至少被两个模块以相同语义复用且没有单一业务归属的技术能力；业务对象、业务枚举、业务 DTO、仓储、Mapper、`BaseService`、`BaseController` 和无明确语义的万能工具类 MUST NOT 放入 `shared`。

#### Scenario: 单个模块首次需要辅助能力
- **WHEN** 一个辅助类只被单个业务模块使用
- **THEN** 该类保留在所属业务模块
- **AND** 不因未来可能复用而提前移入 `shared`

#### Scenario: 多个模块复用技术能力
- **WHEN** 两个以上模块以相同语义使用统一错误、认证上下文、可观测性、时间或标识能力
- **THEN** 该技术能力可以进入有明确子 package 名称的 `shared` 范围
- **AND** 其中不包含任一模块的业务规则或持久化实现

### Requirement: 持久化与资源按业务模块定位
MyBatis XML SHALL 放置在 `src/main/resources/mapper/<module>/`，模块 Prompt SHALL 放置在 `src/main/resources/prompts/<module>/`；数据库结构 MUST 继续只由受版本管理的新 Flyway migration 修改。

#### Scenario: 新增模块 SQL 映射
- **WHEN** 后续业务模块需要 MyBatis XML
- **THEN** XML 位于该业务模块对应的 mapper 子目录
- **AND** SQL 使用受控参数绑定且不绕过 Flyway 修改数据库结构

#### Scenario: 新增 AI Prompt
- **WHEN** 后续 AI 用例需要可维护的 Prompt 模板
- **THEN** Prompt 位于 `prompts/assistant/` 或明确归属的模块子目录
- **AND** 不以大段字符串散落在 Controller 中

### Requirement: 架构边界具有自动化门禁
后端测试套件 SHALL 包含自动化架构检查，至少验证业务模块层次方向、跨模块入口、API 与持久化隔离、领域层框架隔离和项目的非 JPA 技术栈约束。

#### Scenario: 代码遵守模块边界
- **WHEN** 开发者运行 `./mvnw test`
- **THEN** 架构测试通过
- **AND** 现有业务行为测试同时通过

#### Scenario: Controller 直接依赖 Mapper
- **WHEN** 新增代码使任一业务 Controller 直接依赖 MyBatis Mapper
- **THEN** 架构测试失败并给出可定位的违规依赖

#### Scenario: 引入 JPA 模式
- **WHEN** 后端代码引入 JPA entity、Spring Data JPA Repository 或 JPA 专用测试模式
- **THEN** 架构测试或 Harness 门禁失败

### Requirement: 独立后端仓库包含架构上下文
后端仓库 SHALL 包含局部 `AGENTS.md` 和中文架构文档，使从 `backend/` 独立进入的开发者或 AI 代理能够发现模块边界、技术约束和验证命令。

#### Scenario: AI 代理从后端仓库开始任务
- **WHEN** AI 代理直接以 `backend/` 为工作目录处理 Java 或 Spring Boot 任务
- **THEN** 可以从 `backend/AGENTS.md` 读取模块边界、MyBatis-Plus/Flyway 约束和验证要求
- **AND** 可以从后端 README 定位完整中文架构文档

#### Scenario: 根级与局部规则同时生效
- **WHEN** AI 代理从主仓库处理后端 submodule 任务
- **THEN** 根级跨仓库规则与后端局部架构规则共同生效
- **AND** 后端局部规则不降低根级安全、OpenSpec 或验证要求

### Requirement: 现有基础行为保持兼容
架构整理 MUST 保持现有 `/api/health` 契约、默认数据库关闭、默认 AI 关闭和 AI 必填配置校验行为不变，并 MUST NOT 在基础测试中访问外部模型服务。

#### Scenario: 默认运行后端测试
- **WHEN** 开发者没有启动 MySQL且没有配置 AI API Key时运行默认测试
- **THEN** 后端测试通过
- **AND** Spring 容器不创建会访问外部模型服务的 `ChatModel`

#### Scenario: 调用应用健康检查
- **WHEN** 客户端请求 `GET /api/health`
- **THEN** 接口继续返回成功状态和既有服务标识

#### Scenario: AI 配置归位后启用配置不完整
- **WHEN** AI 配置类移动到所属模块后，应用显式启用 AI 但缺少基础地址、API Key 或模型名称
- **THEN** 应用仍在发起模型请求前启动失败
- **AND** 错误信息不泄露真实凭据
