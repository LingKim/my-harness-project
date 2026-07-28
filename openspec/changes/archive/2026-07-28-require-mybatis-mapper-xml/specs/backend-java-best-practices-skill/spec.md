## MODIFIED Requirements

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
