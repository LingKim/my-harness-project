## Purpose

定义项目级 Java/Spring Boot 最佳实践 Skill 的来源、强制触发范围、技术栈冲突覆盖和 Harness 校验契约，确保后端 AI Coding 与当前 Java 21、Spring Boot 4.1、MyBatis-Plus 和 Flyway 事实一致。

## Requirements

### Requirement: 项目提供可追踪的 Java Spring Boot 最佳实践 Skill

主仓库根 `.codex/skills/` MUST 提供 `github/awesome-copilot@java-springboot` 的完整 Skill 内容，并 MUST 通过根 `.codex/skills-lock.json` 记录其来源与内容哈希；该 Skill MUST 出现在根批准清单中，后端子仓库不得维护第二份规范副本。

#### Scenario: 完整检出项目

- **WHEN** 开发者或 AI 代理递归检出完整 AIWorkSpace
- **THEN** 无需依赖用户级全局安装即可从根目录读取 `java-springboot` 入口文件
- **AND** 根统一锁文件包含 GitHub 来源、Skill 路径和有效内容哈希

#### Scenario: 安装命令附带无关 Skill

- **WHEN** 根 `.codex/skills` 或统一锁文件出现未经过独立 change 批准的其他应用 Skill
- **THEN** 后端局部检查或根 Harness 必须失败并指出未批准的 Skill 名称
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

项目 MUST 明确规定 MyBatis-Plus 3.5.17 与 Flyway 是当前数据访问和数据库结构管理方案；`java-springboot` 中的 Spring Data JPA、JPA entity、`JpaRepository`、`CrudRepository`、JPA Criteria API 和 `@DataJpaTest` 建议默认不得应用，也不得仅因 Skill 建议新增 JPA 或相关依赖。

#### Scenario: Skill 建议使用 JPA

- **WHEN** AI 代理在 Skill 中读到 Spring Data JPA 或 JPA 测试模式
- **THEN** 代理必须继续使用当前 MyBatis-Plus 与 Flyway 契约
- **AND** 不得新增 JPA entity、repository、starter 或 JPA 专用测试

#### Scenario: 未来明确改变技术栈

- **WHEN** 已确认的独立 OpenSpec change 明确要求引入 JPA 并修改现有数据访问规格
- **THEN** 代理按照新规格执行，而不是继续使用本规则的默认排除

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

后端局部检查与主仓库 Harness MUST 自动校验后端入口、`backend-conventions.md`、Java Skill 批准清单项、入口文件、锁记录来源、Skill 路径、哈希以及 JPA 排除 Rule；校验 MUST NOT 要求这些规则正文位于根 `AGENTS.md`。

#### Scenario: Java Skill 接入完整

- **WHEN** 执行后端局部治理检查或 `./scripts/check-harness.sh`
- **THEN** 后端入口、conventions、Java Skill、锁记录和路由检查全部通过

#### Scenario: JPA 排除规则被移除

- **WHEN** Java Skill 文件仍存在但 `backend-conventions.md` 不再保留 MyBatis-Plus/Flyway 优先和 JPA 排除 Rule
- **THEN** 检查必须失败，不得把存在技术栈冲突的接入判定为成功
