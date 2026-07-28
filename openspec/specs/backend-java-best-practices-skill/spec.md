## Purpose

定义项目级 Java/Spring Boot 最佳实践 Skill 的来源、强制触发范围、技术栈冲突覆盖和 Harness 校验契约，确保后端 AI Coding 与当前 Java 21、Spring Boot 4.1、MyBatis-Plus 和 Flyway 事实一致。

## Requirements

### Requirement: 项目提供可追踪的 Java Spring Boot 最佳实践 Skill

主仓库根 `.codex/skills/` MUST 提供项目维护的 `java-springboot` Skill，并 MUST 通过根 `.codex/skills-lock.json` 记录项目来源、Skill 路径与内容哈希；该 Skill MUST 出现在根批准清单中，后端子仓库不得维护第二份规范副本。Skill MUST 以 ChinaMate 当前 Java 21、Spring Boot 4.1、模块化单体、MyBatis-Plus 和 Flyway 技术基线为内容边界。

#### Scenario: 完整检出项目

- **WHEN** 开发者或 AI 代理递归检出完整 AIWorkSpace
- **THEN** 无需依赖用户级全局安装即可从根目录读取 `java-springboot` 入口文件
- **AND** 根统一锁文件包含项目来源、Skill 路径和有效内容哈希

#### Scenario: Skill 出现项目未采用的默认技术路径

- **WHEN** `java-springboot` Skill 把 Spring Data JPA、JPA entity、`JpaRepository`、Criteria API 或 `@DataJpaTest` 描述为项目默认实践
- **THEN** 后端局部检查或人工审查必须将 Skill 判定为与项目技术基线冲突
- **AND** 不得要求执行角色依靠同时读取相反 Rule 来消解该冲突
### Requirement: 后端任务强制触发 Java Spring Boot Skill

后端 `AGENTS.md` MUST 规定：涉及 Java、Spring Boot、Web、配置、事务、日志、测试或安全的编写、评审和重构任务必须先读取 `../.codex/rules/backend-conventions.md`，再完整读取 `../.codex/skills/java-springboot/SKILL.md`。

#### Scenario: AI 开始后端 Java 任务

- **WHEN** AI 代理准备编写、评审或重构上述范围内的后端代码
- **THEN** 代理必须加载 `backend-conventions.md` 和 `java-springboot`
- **AND** 应用与任务相关且不冲突的规则

#### Scenario: 非后端任务

- **WHEN** 任务只涉及前端、主仓库编排或与 Java/Spring Boot 无关的文件
- **THEN** 后端 Rule 与 Skill 不因本规则被强制加载
### Requirement: 项目技术栈覆盖通用 JPA 建议

`java-springboot` Skill MUST 将按业务域组织、构造器注入、不可变依赖、明确 DTO、Bean Validation、统一异常、短事务、参数化日志和分层测试作为项目默认实践，并 MUST 将 MyBatis-Plus 与 Flyway 作为持久化和 schema 管理路径。Skill MUST 要求新增或实质修改的自定义 SQL 使用 Mapper XML，MUST NOT 推荐 SQL 注解或 Provider 注解作为自定义 SQL 的实现方式，同时 MUST 保留 `BaseMapper<T>` 自动 CRUD。Skill MUST NOT 推荐新增 JPA entity、Spring Data repository、JPA Criteria API、`@DataJpaTest` 或相关 starter。

#### Scenario: AI 使用 Java Skill 实现持久化用例

- **WHEN** AI 代理依据 `java-springboot` Skill 编写包含数据库访问的后端代码
- **THEN** Skill 必须将其路由到 MyBatis-Plus、Mapper XML、数据库 Rules 和 Flyway 契约
- **AND** 不得提供注解 SQL、Provider 注解或 JPA 作为无需额外决策的默认实现

#### Scenario: AI 使用 BaseMapper 自动 CRUD

- **WHEN** 常规 CRUD 可以直接由 MyBatis-Plus `BaseMapper<T>` 提供
- **THEN** Skill 必须允许 Mapper 直接使用框架自动 CRUD
- **AND** 不得要求为同一操作重复创建 XML statement

#### Scenario: AI 新增自定义 SQL

- **WHEN** 后端 Mapper 需要新增自定义查询、写入、动态 SQL 或结果映射
- **THEN** Skill 必须要求 SQL 位于所属业务目录的 Mapper XML，并保持 `namespace` 和 statement ID 与 Java 接口对应
- **AND** Java Mapper 接口不得使用 SQL 注解或 Provider 注解承载该 SQL

#### Scenario: 实现包含多步数据库写入

- **WHEN** 一个应用用例需要完成多个必须原子成功的数据库写操作
- **THEN** Skill 必须要求在最小必要应用用例边界明确事务策略并验证失败回滚
- **AND** 不得把外部网络、模型、文件或对象存储 I/O 放入数据库事务

### Requirement: 当前 Java 与 Spring Boot 版本事实优先

根 `.codex/rules/backend-conventions.md` MUST 使用统一事实优先级：已确认 OpenSpec；当前依赖、源码、测试与真实输出；项目 Rule；Java 21 与 Spring Boot 4.1 当前官方文档；通用 Skill 建议。发现冲突时必须采用当前项目证据判断现状，并检查该现状是否违反规格或 Rule。

#### Scenario: Skill 建议与当前项目一致

- **WHEN** Skill 建议不与项目规格、`backend-conventions.md`、技术栈和当前版本行为冲突
- **THEN** 代理必须把该建议应用于相关实现或评审

#### Scenario: Skill 示例与 Spring Boot 4.1 不一致

- **WHEN** Skill 中的注解、starter、测试方式或 API 示例与当前 Spring Boot 4.1 依赖、源码或测试冲突
- **THEN** 代理必须采用当前项目证据或官方版本文档
- **AND** 不得用通用示例覆盖已验证的当前行为
### Requirement: Harness 校验 Java Skill 接入

后端局部检查与主仓库 Harness MUST 自动校验后端入口、`backend-conventions.md`、Java Skill 批准清单项、入口文件、项目来源锁记录、Skill 路径和内容哈希；检查 MUST NOT 继续要求第三方 GitHub 来源，也不得把包含 JPA 默认建议的旧 Skill 描述为当前批准内容。

#### Scenario: 第一方 Java Skill 接入完整

- **WHEN** 执行后端局部治理检查或 `./scripts/check-harness.sh`
- **THEN** 后端入口、conventions、第一方 Java Skill、项目来源锁记录和路由检查全部通过

#### Scenario: 锁文件仍声明旧第三方来源

- **WHEN** Skill 内容已迁移为项目维护版本但批准清单或锁文件仍声明旧 GitHub 第三方来源
- **THEN** 治理检查必须失败并指出来源或哈希不一致
