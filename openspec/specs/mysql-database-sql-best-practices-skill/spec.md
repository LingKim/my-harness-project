## Purpose

定义本项目引入、触发和约束 MySQL 数据库与 SQL 最佳实践 Skill 的稳定契约，确保后续 schema、Flyway migration、MyBatis SQL、索引、事务锁与数据库运维任务遵循 MySQL 8.4 项目事实、安全参数绑定和可验证变更原则。

## Requirements

### Requirement: 项目提供可追踪的 MySQL 最佳实践 Skill

主仓库 MUST 在项目级 Skills 目录中提供 `planetscale/database-skills@mysql` 的完整入口与参考文件，并 MUST 通过 `skills-lock.json` 记录来源、Skill 路径和内容哈希；该 Skill MUST 出现在 Harness 的显式批准清单中，且不得附带引入未批准 Skill。

#### Scenario: 完整检出项目

- **WHEN** 开发者或 AI 代理检出主仓库
- **THEN** 无需依赖用户级全局安装即可读取 `mysql` 入口和相关参考文件
- **AND** 锁文件包含 `planetscale/database-skills` 来源、正确 Skill 路径和有效内容哈希

#### Scenario: 安装命令附带无关 Skill

- **WHEN** 项目级目录或锁文件出现未经过独立 change 批准的其他 Skill
- **THEN** Harness 必须失败并指出未批准的 Skill 名称

### Requirement: 数据库和 SQL 任务强制触发 MySQL Skill

根目录 `AGENTS.md` MUST 规定：涉及 MySQL 配置、Flyway migration、MyBatis XML 或注解 SQL、表结构、字段类型、约束、索引、查询、事务锁、连接或数据库运维的编写、评审和重构任务必须使用 `mysql`，完整读取其 `SKILL.md`，并按任务需要读取直接相关的参考文件。

#### Scenario: AI 开始数据库相关任务

- **WHEN** AI 代理准备编写、评审或重构上述数据库与 SQL 范围内的内容
- **THEN** 代理必须加载 `mysql` Skill 及任务直接相关的参考文件
- **AND** 只应用不与当前项目事实冲突的规则

#### Scenario: 非数据库任务

- **WHEN** 任务不涉及 MySQL、schema、migration、SQL、事务锁或数据库运维
- **THEN** `mysql` Skill 不因本规则被强制加载

### Requirement: MySQL 8.4 与项目数据库架构优先

项目 MUST 把当前 OpenSpec、`backend/` 局部规则、实际 schema、SQL、依赖与测试、MySQL 8.4 官方文档和安全环境中的执行证据置于通用 Skill 建议之上，并 MUST 继续使用 Docker Compose MySQL 8.4、InnoDB、MyBatis-Plus 与 Flyway-only 架构。

#### Scenario: Skill 推荐 PlanetScale 托管

- **WHEN** Skill 推荐 PlanetScale、Vitess 或其他不同于当前项目的托管架构
- **THEN** 代理必须保留当前 Docker Compose MySQL 8.4 架构
- **AND** 不得仅因 Skill 建议改变数据库托管方式

#### Scenario: Skill 给出绝对化数据库规则

- **WHEN** Skill 对主键类型、collation、时间类型、分区阈值或在线 DDL 算法给出通用默认值
- **THEN** 代理必须根据业务语义、MySQL 8.4 官方行为、真实数据量和变更风险进行验证
- **AND** 不得把通用默认值无条件固化为项目规则

### Requirement: 数据库结构只通过 Flyway 管理

所有应用数据库结构变更 MUST 通过 `backend/src/main/resources/db/migration/` 中受版本管理的 Flyway migration 实施；代理不得通过 JPA/Hibernate 自动建表、启动脚本或未受版本管理的手工 DDL 绕过 Flyway。

#### Scenario: 创建或修改表结构

- **WHEN** 需求需要新增或修改表、字段、约束或索引
- **THEN** 变更必须落在新的 Flyway migration 中
- **AND** migration 必须包含与发布风险相称的兼容、验证和回滚说明

#### Scenario: Skill 建议直接执行 DDL

- **WHEN** Skill 示例建议直接对数据库执行结构变更
- **THEN** 代理必须先把变更转换为符合项目版本管理规则的 Flyway migration
- **AND** 不得绕过已确认的 OpenSpec 和部署流程

### Requirement: MyBatis SQL 使用安全参数绑定

MyBatis SQL 中的业务值 MUST 使用 `#{}` 参数绑定；`${}` 只能用于 JDBC 无法参数化的标识符或受控 SQL 片段，且输入 MUST 来自服务端封闭白名单，不得直接或间接接受用户输入。

#### Scenario: SQL 使用业务输入值

- **WHEN** 查询条件、写入值、分页值或其他 SQL 数据来自请求或业务对象
- **THEN** SQL 必须通过 `#{}` 绑定该值
- **AND** 不得通过字符串拼接或 `${}` 注入 SQL 文本

#### Scenario: 动态排序字段无法参数化

- **WHEN** SQL 必须动态选择排序字段或其他标识符
- **THEN** 服务端必须先把有限枚举映射为封闭白名单中的固定 SQL 片段
- **AND** 原始用户输入不得进入 `${}`

### Requirement: Schema、索引和查询以业务语义与证据为依据

数据库设计 MUST 明确关键字段的数据类型、长度、NULL 语义、默认值、约束、字符比较语义和索引理由；应用数据查询 MUST 默认显式列出所需列，索引与性能修改 MUST 由真实查询模式及执行计划证据支撑。

#### Scenario: 设计新表或字段

- **WHEN** 需求创建新的业务表或字段
- **THEN** 设计必须说明主键、数据类型、NULL、默认值、约束和字符比较选择与业务语义的对应关系
- **AND** 不得仅复制 Skill 的默认类型或 collation

#### Scenario: 优化查询或增加索引

- **WHEN** 需求声称查询缓慢或需要新增索引
- **THEN** 代理必须先收集查询、数据规模和 `EXPLAIN` 等证据
- **AND** 只有证据支持时才修改 SQL 或索引

#### Scenario: 使用 EXPLAIN ANALYZE

- **WHEN** 需要获取 `EXPLAIN ANALYZE` 的实际执行证据
- **THEN** 只能在确认安全的环境中对只读 SQL 使用
- **AND** 不得用它直接执行写入或破坏性语句

### Requirement: 破坏性数据库操作必须获得人工批准

执行 `DROP`、`TRUNCATE`、无条件 `DELETE`/`UPDATE`、不可逆字段或索引删除以及其他可能造成数据不可恢复的操作前，代理 MUST 解析精确目标、说明影响与恢复方式，并获得用户明确批准。

#### Scenario: 请求包含破坏性数据库操作

- **WHEN** 计划会删除或不可逆修改表、字段、索引或数据
- **THEN** 代理必须在执行前停止并请求明确批准
- **AND** 提供备份、兼容发布、回滚和部署后验证方案

#### Scenario: 只读审查发现危险 SQL

- **WHEN** 代理在审查中发现无条件写操作或未受保护的破坏性 DDL
- **THEN** 代理必须把它标记为阻断问题
- **AND** 不得在未获批准时执行该 SQL

### Requirement: Harness 校验 MySQL Skill 接入

主仓库 Harness MUST 自动校验 MySQL Skill 的批准清单项、入口、代表性参考文件、锁记录来源、Skill 路径、哈希以及根级 `AGENTS.md` 的触发、Flyway-only、MyBatis 参数安全、MySQL 8.4 优先级和破坏性操作审批引用。

#### Scenario: MySQL Skill 接入完整

- **WHEN** 执行 `./scripts/check-harness.sh`
- **THEN** MySQL Skill 的文件、锁记录、批准清单和根级规则引用检查全部通过

#### Scenario: 参数安全或 Flyway 规则被移除

- **WHEN** Skill 文件仍存在但根级 `AGENTS.md` 不再保留 `#{}`/`${}` 参数边界或 Flyway-only 规则
- **THEN** Harness 必须失败并指出缺失的数据库安全约束
