## MODIFIED Requirements

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

### Requirement: 项目技术栈覆盖通用 JPA 建议

`java-springboot` Skill MUST 将按业务域组织、构造器注入、不可变依赖、明确 DTO、Bean Validation、统一异常、短事务、参数化日志和分层测试作为项目默认实践，并 MUST 将 MyBatis-Plus 与 Flyway 作为持久化和 schema 管理路径。Skill MUST NOT 推荐新增 JPA entity、Spring Data repository、JPA Criteria API、`@DataJpaTest` 或相关 starter。

#### Scenario: AI 使用 Java Skill 实现持久化用例

- **WHEN** AI 代理依据 `java-springboot` Skill 编写包含数据库访问的后端代码
- **THEN** Skill 必须将其路由到 MyBatis-Plus、数据库 Rules 和 Flyway 契约
- **AND** 不得提供 JPA 作为无需额外决策的默认实现

#### Scenario: 实现包含多步数据库写入

- **WHEN** 一个应用用例需要完成多个必须原子成功的数据库写操作
- **THEN** Skill 必须要求在最小必要应用用例边界明确事务策略并验证失败回滚
- **AND** 不得把外部网络、模型、文件或对象存储 I/O 放入数据库事务

### Requirement: Harness 校验 Java Skill 接入

后端局部检查与主仓库 Harness MUST 自动校验后端入口、`backend-conventions.md`、Java Skill 批准清单项、入口文件、项目来源锁记录、Skill 路径和内容哈希；检查 MUST NOT 继续要求第三方 GitHub 来源，也不得把包含 JPA 默认建议的旧 Skill 描述为当前批准内容。

#### Scenario: 第一方 Java Skill 接入完整

- **WHEN** 执行后端局部治理检查或 `./scripts/check-harness.sh`
- **THEN** 后端入口、conventions、第一方 Java Skill、项目来源锁记录和路由检查全部通过

#### Scenario: 锁文件仍声明旧第三方来源

- **WHEN** Skill 内容已迁移为项目维护版本但批准清单或锁文件仍声明旧 GitHub 第三方来源
- **THEN** 治理检查必须失败并指出来源或哈希不一致
