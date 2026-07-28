## ADDED Requirements

### Requirement: 业务持久化默认使用 MyBatis-Plus

后端业务表的常规 CRUD、条件查询和分页 MUST 默认通过所属业务模块 `infrastructure` 中的 MyBatis-Plus Mapper 或其适配器完成。复杂 SQL SHALL 使用同一 Mapper 边界内的 XML 或注解 SQL，并继续遵守安全参数绑定、显式查询列、数据库对象不越过应用边界和 Flyway-only schema 管理规则。仅在已确认设计证明 MyBatis-Plus 无法合理表达、既有基础设施明确要求或其他可验证约束存在时，才可直接使用 Spring JDBC。

#### Scenario: 新增常规业务持久化
- **WHEN** 后端 change 新增业务表的创建、读取、更新、删除、条件查询或分页能力
- **THEN** 实现必须默认提供所属模块的 MyBatis-Plus Mapper，并由 `infrastructure` 适配器向 application/domain 端口提供能力
- **AND** Controller、domain 和跨模块调用不得直接依赖 Mapper 或数据库对象

#### Scenario: 复杂查询不能由通用 CRUD 合理表达
- **WHEN** 业务需要多表查询、聚合、锁定读取或其他复杂 SQL
- **THEN** 实现必须优先在所属 Mapper 的 XML 或注解 SQL 中显式表达查询和参数绑定
- **AND** 不得仅为避免建立 Mapper 而改用内联 JDBC SQL

#### Scenario: 直接使用 Spring JDBC
- **WHEN** 已确认设计决定使用 `JdbcTemplate`、`NamedParameterJdbcTemplate` 或其他 Spring JDBC API
- **THEN** 设计和完成报告必须说明 MyBatis-Plus 不适用的具体原因、限定文件范围、替代方案取舍和等价测试
- **AND** 直接 JDBC 访问只能位于所属模块 `infrastructure`，不得成为未记录的默认持久化路径

#### Scenario: 缺少例外依据的 JDBC 实现
- **WHEN** 实现直接使用 Spring JDBC 且 proposal、design、tasks 或项目架构决策没有对应依据
- **THEN** `backend_engineer`、`qa_engineer` 或 `spec_reviewer` 必须将其标记为阻断级工程实践偏差
- **AND** 不得以 SQL 使用了占位参数为由判定整体持久化方案合规
