## Purpose

定义项目级 Java/Spring Boot 最佳实践 Skill 的来源、强制触发范围、技术栈冲突覆盖和 Harness 校验契约，确保后端 AI Coding 与当前 Java 21、Spring Boot 4.1、MyBatis-Plus 和 Flyway 事实一致。

## Requirements

### Requirement: 项目提供可追踪的 Java Spring Boot 最佳实践 Skill

主仓库 MUST 在项目级 Skills 目录中提供 `github/awesome-copilot@java-springboot` 的完整 Skill 内容，并 MUST 通过 `skills-lock.json` 记录其来源与内容哈希；该 Skill MUST 出现在 Harness 的显式批准清单中，且不得因安装命令附带引入同仓库其他未批准 Skills。

#### Scenario: 完整检出项目

- **WHEN** 开发者或 AI 代理检出主仓库
- **THEN** 无需依赖用户级全局安装即可读取 `java-springboot` 入口文件
- **AND** 锁文件包含 GitHub 官方仓库来源、Skill 路径和有效内容哈希

#### Scenario: 安装命令附带无关 Skill

- **WHEN** 项目级目录或锁文件出现未经过独立 change 批准的其他 Skill
- **THEN** Harness 检查必须失败并指出未批准的 Skill 名称

### Requirement: 后端任务强制触发 Java Spring Boot Skill

根目录 `AGENTS.md` MUST 规定：涉及 `backend/` 的 Java、Spring Boot、Web、配置、事务、日志、测试或安全的编写、评审和重构任务必须使用 `java-springboot`，并在执行前完整读取其 `SKILL.md`。

#### Scenario: AI 开始后端 Java 任务

- **WHEN** AI 代理准备编写、评审或重构上述范围内的后端代码
- **THEN** 代理必须加载 `java-springboot` 并应用与任务相关且不冲突的规则

#### Scenario: 非后端任务

- **WHEN** 任务只涉及前端、主仓库编排或与 Java/Spring Boot 无关的文件
- **THEN** 该 Skill 不因本规则被强制加载

### Requirement: 项目技术栈覆盖通用 JPA 建议

项目 MUST 明确规定 MyBatis-Plus 3.5.17 与 Flyway 是当前数据访问和数据库结构管理方案；`java-springboot` 中的 Spring Data JPA、JPA entity、`JpaRepository`、`CrudRepository`、JPA Criteria API 和 `@DataJpaTest` 建议默认不得应用，也不得仅因 Skill 建议新增 JPA 或相关依赖。

#### Scenario: Skill 建议使用 JPA

- **WHEN** AI 代理在 Skill 中读到 Spring Data JPA 或 JPA 测试模式
- **THEN** 代理必须继续使用当前 MyBatis-Plus 与 Flyway 契约
- **AND** 不得新增 JPA entity、repository、starter 或 JPA 专用测试

#### Scenario: 未来明确改变技术栈

- **WHEN** 已确认的独立 OpenSpec change 明确要求引入 JPA 并修改现有数据访问规格
- **THEN** 代理按照新规格执行，而不是继续使用本规则的默认排除

### Requirement: 当前 Java 与 Spring Boot 版本事实优先

项目 MUST 把当前 OpenSpec、`backend/` 局部规则、实际依赖、源码与测试，以及 Java 21 和 Spring Boot 4.1 当前文档置于通用 Skill 建议之上；发现冲突时必须采用当前项目事实并说明冲突。

#### Scenario: Skill 建议与当前项目一致

- **WHEN** Skill 建议不与项目规格、技术栈和当前版本行为冲突
- **THEN** 代理必须把该建议应用于相关实现或评审

#### Scenario: Skill 示例与 Spring Boot 4.1 不一致

- **WHEN** Skill 中的注解、starter、测试方式或 API 示例与当前 Spring Boot 4.1 依赖和文档冲突
- **THEN** 代理必须采用当前项目依赖、测试证据或官方版本文档
- **AND** 不得用通用示例覆盖已验证的当前行为

### Requirement: Harness 校验 Java Skill 接入

主仓库 Harness MUST 自动校验 Java Skill 的批准清单项、入口文件、锁记录来源、Skill 路径、哈希以及根级 `AGENTS.md` 的触发和 JPA 排除引用，且失败信息必须能够定位缺失或错误项。

#### Scenario: Java Skill 接入完整

- **WHEN** 执行 `./scripts/check-harness.sh`
- **THEN** Java Skill 的文件、锁记录、批准清单和规则引用检查全部通过

#### Scenario: JPA 排除规则被移除

- **WHEN** Java Skill 文件仍存在但根级 `AGENTS.md` 不再保留 MyBatis-Plus/Flyway 优先和 JPA 排除规则
- **THEN** Harness 检查必须失败，不得把存在技术栈冲突的接入判定为成功
