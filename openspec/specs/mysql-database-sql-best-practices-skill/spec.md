## Purpose

定义本项目引入、触发和约束 MySQL 数据库与 SQL 最佳实践 Skill 的稳定契约，确保后续 schema、Flyway migration、MyBatis SQL、索引、事务锁与数据库运维任务遵循 MySQL 8.4 项目事实、安全参数绑定和可验证变更原则。

## Requirements

### Requirement: 项目提供可追踪的 MySQL 最佳实践 Skill

主仓库根 `.codex/skills/` MUST 提供 `planetscale/database-skills@mysql` 的完整入口与参考文件，并 MUST 通过根 `.codex/skills-lock.json` 记录来源、Skill 路径和内容哈希；该 Skill MUST 出现在根批准清单中，后端子仓库不得维护第二份规范副本。

#### Scenario: 完整检出项目

- **WHEN** 开发者或 AI 代理递归检出完整 AIWorkSpace
- **THEN** 无需依赖用户级全局安装即可从根目录读取 `mysql` 入口和相关参考文件
- **AND** 根统一锁文件包含来源、正确 Skill 路径和有效内容哈希

#### Scenario: 安装命令附带无关 Skill

- **WHEN** 根 `.codex/skills` 或统一锁文件出现未经过独立 change 批准的其他应用 Skill
- **THEN** 后端局部检查或根 Harness 必须失败并指出未批准的 Skill 名称
### Requirement: 数据库和 SQL 任务强制触发 MySQL Skill

后端 `AGENTS.md` MUST 规定：涉及 MySQL 配置、Flyway migration、MyBatis XML 或注解 SQL、表结构、字段类型、约束、索引、查询、事务锁、连接或数据库运维的编写、评审和重构任务必须先读取 `../.codex/rules/database-conventions.md`，再完整读取 `../.codex/skills/mysql/SKILL.md` 和任务直接相关的参考文件。

#### Scenario: AI 开始数据库相关任务

- **WHEN** AI 代理准备编写、评审或重构上述数据库与 SQL 范围内的内容
- **THEN** 代理必须加载 `database-conventions.md`、`mysql` Skill 及任务直接相关的参考文件
- **AND** 只应用不与当前项目事实冲突的建议

#### Scenario: 非数据库任务

- **WHEN** 任务不涉及 MySQL、schema、migration、SQL、事务锁或数据库运维
- **THEN** 数据库 Rule 与 `mysql` Skill 不因本规则被强制加载
### Requirement: MySQL 8.4 与项目数据库架构优先

根 `.codex/rules/database-conventions.md` MUST 使用统一事实优先级：已确认 OpenSpec；当前 schema、SQL、依赖、migration、测试与安全环境执行证据；项目 Rule；MySQL 8.4 官方文档；通用 Skill 建议。项目 MUST 继续使用 Docker Compose MySQL 8.4、InnoDB、MyBatis-Plus 与 Flyway-only 架构。

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

### Requirement: 业务持久化默认使用 MyBatis-Plus

后端业务表的常规 CRUD、条件查询和分页 MUST 默认通过所属业务模块 `infrastructure` 中的 MyBatis-Plus Mapper 或其适配器完成。新增或实质修改的自定义 SQL MUST 使用同一 Mapper 边界内的 XML，MUST NOT 使用 `@Select`、`@Insert`、`@Update`、`@Delete` 或对应 Provider 注解承载 SQL，并 MUST 继续遵守安全参数绑定、显式查询列、数据库对象不越过应用边界和 Flyway-only schema 管理规则。MyBatis-Plus `BaseMapper<T>` 自动提供的通用 CRUD，以及不承载 SQL 文本的 `@Mapper`、`@Param`，不受 XML 强制规则限制。仅在已确认设计证明 MyBatis-Plus 无法合理表达、既有基础设施明确要求或其他可验证约束存在时，才可直接使用 Spring JDBC。

#### Scenario: 新增常规业务持久化

- **WHEN** 后端 change 新增业务表的创建、读取、更新、删除、条件查询或分页能力
- **THEN** 实现必须默认提供所属模块的 MyBatis-Plus Mapper，并由 `infrastructure` 适配器向 application/domain 端口提供能力
- **AND** Controller、domain 和跨模块调用不得直接依赖 Mapper 或数据库对象

#### Scenario: 使用 BaseMapper 自动 CRUD

- **WHEN** Mapper 继承 `BaseMapper<T>` 并直接使用框架自动提供的通用 CRUD
- **THEN** 实现无需为同一通用 CRUD 重复编写 Mapper XML statement
- **AND** 不得以 XML 强制规则为由复制框架已提供的等价 SQL

#### Scenario: 新增自定义 SQL

- **WHEN** 业务新增不能由 `BaseMapper<T>` 自动 CRUD 直接提供的查询或写入 statement
- **THEN** SQL 必须写入 `src/main/resources/mapper/<业务>/` 下的 Mapper XML
- **AND** XML `namespace` 必须等于 Java Mapper 接口全限定名，statement ID 必须与接口方法对应
- **AND** Java Mapper 接口不得使用 SQL 注解或 Provider 注解承载该 statement

#### Scenario: 实质修改存量注解 SQL

- **WHEN** 后续 change 修改现有注解 statement 的 SQL 文本、参数、结果映射或数据库行为
- **THEN** 该 statement 必须在同一 change 中迁移到 Mapper XML
- **AND** 仅修改注释、格式或与 SQL 无关的 Java 内容不触发迁移

#### Scenario: 复杂查询不能由通用 CRUD 合理表达

- **WHEN** 业务需要多表查询、聚合、锁定读取、动态条件或其他复杂 SQL
- **THEN** 实现必须在所属 Mapper 的 XML 中显式表达查询、参数绑定和必要的结果映射
- **AND** 不得改用注解 SQL、Provider 注解或仅为避免建立 Mapper 而使用内联 JDBC SQL

#### Scenario: 直接使用 Spring JDBC

- **WHEN** 已确认设计决定使用 `JdbcTemplate`、`NamedParameterJdbcTemplate` 或其他 Spring JDBC API
- **THEN** 设计和完成报告必须说明 MyBatis-Plus 不适用的具体原因、限定文件范围、替代方案取舍和等价测试
- **AND** 直接 JDBC 访问只能位于所属模块 `infrastructure`，不得成为未记录的默认持久化路径

#### Scenario: 缺少例外依据的 JDBC 实现

- **WHEN** 实现直接使用 Spring JDBC 且 proposal、design、tasks 或项目架构决策没有对应依据
- **THEN** `backend_engineer`、`qa_engineer` 或 `spec_reviewer` 必须将其标记为阻断级工程实践偏差
- **AND** 不得以 SQL 使用了占位参数为由判定整体持久化方案合规

### Requirement: Harness 校验 MySQL Skill 接入

后端局部检查与主仓库 Harness MUST 自动校验后端入口、`database-conventions.md`、MySQL Skill 批准清单项、入口、代表性参考文件、锁记录来源、Skill 路径、哈希以及 Flyway-only、MyBatis 参数安全、MySQL 8.4 优先级和破坏性操作审批 Rule；校验 MUST NOT 要求这些规则正文位于根 `AGENTS.md`。

#### Scenario: MySQL Skill 接入完整

- **WHEN** 执行后端局部治理检查或 `./scripts/check-harness.sh`
- **THEN** 后端入口、database conventions、MySQL Skill、锁记录和路由检查全部通过

#### Scenario: 参数安全或 Flyway 规则被移除

- **WHEN** Skill 文件仍存在但 `database-conventions.md` 不再保留参数绑定或 Flyway-only Rule
- **THEN** 检查必须失败并指出缺失的数据库安全约束
