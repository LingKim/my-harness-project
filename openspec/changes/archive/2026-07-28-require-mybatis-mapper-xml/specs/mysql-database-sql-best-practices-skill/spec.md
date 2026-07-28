## MODIFIED Requirements

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
