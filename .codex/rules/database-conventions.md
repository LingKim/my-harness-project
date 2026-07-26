# ChinaMate 数据库开发约定

本文是 MySQL、MyBatis-Plus 和 Flyway 稳定约束的唯一规范源。PlanetScale `mysql` Skill 提供候选方法，不代表项目采用 PlanetScale、Vitess 或其中所有默认值。

## RULE-DB-001：保持当前数据库架构

- 当前环境使用 Docker Compose MySQL 8.4、InnoDB、MyBatis-Plus 3.5.17 和 Flyway；不得仅因 Skill 建议改变托管方式或引入 JPA/Hibernate。
- 数据库设计以业务标识、比较语义、时区语义、数据规模、并发模型、MySQL 8.4 官方行为和真实证据为依据。
- `BIGINT UNSIGNED AUTO_INCREMENT`、`utf8mb4_0900_ai_ci`、`DATETIME`、分区阈值、隔离级别和 DDL 算法都只能作为候选，不能无条件固化。

## RULE-DB-002：数据库结构只由 Flyway 管理

- 新增或修改表、字段、约束和索引必须创建 `src/main/resources/db/migration/` 中新的受版本管理 migration。
- 禁止通过 JPA/Hibernate 自动建表、启动脚本或未受版本管理的手工 DDL 绕过 Flyway。
- migration 必须按风险说明兼容发布、验证和回滚；不可逆变更必须取得明确授权。

## RULE-DB-003：Schema 选择必须表达业务语义

- 设计必须说明主键、字段类型与长度、NULL 语义、默认值、约束、字符比较语义和索引依据。
- 金额、时间、外部标识、JSON、ENUM/字典表等选择必须根据业务范围和当前 MySQL 行为决定，不能复制 Skill 的通用默认值。
- 应用查询默认显式列出所需字段，不使用缺乏业务证据的 `SELECT *`、反范式或预防性索引。

## RULE-DB-004：MyBatis 参数绑定必须安全

- SQL 业务值必须使用 `#{}` 参数绑定，禁止把用户输入通过字符串拼接或 `${}` 注入 SQL 文本。
- `${}` 只允许 JDBC 无法参数化的标识符或受控 SQL 片段，输入必须来自服务端封闭枚举到固定 SQL 的映射。
- 动态排序、表名或列名若无法避免，必须先证明需求并测试白名单边界；原始或间接用户输入不得进入 `${}`。

## RULE-DB-005：索引和优化以查询证据为前提

- 修改索引或声称查询需要优化前，先收集查询模式、数据量、选择性、现有索引和 `EXPLAIN` 等证据。
- 组合索引顺序、覆盖索引、分页和查询重写根据实际谓词与排序决定，不把 `Using filesort`、`Using temporary` 或 `type: ALL` 单独视为必然错误。
- `EXPLAIN ANALYZE` 会实际执行 SQL，只能在确认安全的非生产环境用于只读语句；禁止对写入或破坏性语句使用。

## RULE-DB-006：事务与锁必须基于已确认并发行为

- 事务保持短小，外部 I/O 放在事务外，并保持一致的行访问和加锁顺序。
- InnoDB 的范围锁、gap/next-key lock、缺失索引造成的广泛行锁和不存在记录的锁行为必须按当前隔离级别与执行计划判断。
- 不默认把隔离级别改成 `READ COMMITTED`，也不预设死锁重试；策略必须来自已确认并发模型、幂等性和监控证据。

## RULE-DB-007：DDL 与运维变更必须安全发布

- 在线 DDL 的 `INSTANT`、`INPLACE`、`COPY` 和锁级别以 MySQL 8.4 对具体操作的官方行为与安全环境验证为准，不照搬 Skill 中旧版本边界。
- 大表 DDL 必须评估 metadata lock、长事务、复制延迟、磁盘和回滚；工具选择必须匹配当前自托管架构。
- 连接池、复制、分区和运维参数只在存在真实容量或故障证据时调整。

## RULE-DB-008：破坏性操作需要人工批准和恢复方案

- 执行 `DROP`、`TRUNCATE`、无条件 `DELETE`/`UPDATE`、不可逆字段/索引删除或其他难以恢复的操作前，必须解析精确目标并获得用户明确批准。
- 执行前说明影响范围、备份或恢复方式、兼容发布、回滚和部署后验证；目标不清楚时停止操作。
- 审查发现危险 SQL 时将其标为阻断问题，但未经授权不得执行；`EXPLAIN ANALYZE` 不能用来规避此限制。
