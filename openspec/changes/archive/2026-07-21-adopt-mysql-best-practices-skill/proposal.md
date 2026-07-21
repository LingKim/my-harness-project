## Why

当前项目虽然已固定 MySQL 8.4、MyBatis-Plus 与 Flyway，但还没有覆盖表结构、数据类型、索引、SQL、事务锁和安全迁移的项目级最佳实践 Skill。仅依赖代理通用知识容易产生版本过时、跨数据库方言混用、无证据加索引或绕过 Flyway 修改结构等不一致行为。

## What Changes

- 在主仓库项目级 Skills 目录引入 `planetscale/database-skills@mysql`，作为 MySQL/InnoDB 表结构、索引、查询优化、事务锁和数据库变更任务的通用最佳实践来源。
- 在根目录 `AGENTS.md` 中明确触发范围：涉及 MySQL、Flyway migration、MyBatis SQL、表结构、索引、查询、事务锁或数据库运维的编写、评审和重构任务必须使用 `mysql` Skill。
- 明确事实优先级：当前 OpenSpec、`backend/` 局部规则、实际 schema 与 SQL、MySQL 8.4 官方文档和执行计划证据高于 Skill 的通用建议。
- 明确项目覆盖规则：继续使用 Docker Compose MySQL 8.4、InnoDB、MyBatis-Plus 与 Flyway-only；忽略 Skill 的 PlanetScale 托管偏好，且不得把主键类型、collation、时间类型、分区阈值或在线 DDL 算法等建议无条件固化。
- 建立项目 SQL 安全与可验证性基线：MyBatis 用户输入使用 `#{}` 参数绑定，`${}` 只能用于经过白名单控制且无法参数化的标识符；禁止无证据索引、默认 `SELECT *` 和未经人工批准的破坏性数据库操作。
- 扩展 `skills-lock.json` 与 Harness 批准清单，校验 MySQL Skill 的来源、入口、参考文件、哈希和 `AGENTS.md` 关键约束，同时继续拒绝未批准 Skill。
- 目标：让数据库设计和 SQL 变更采用一致、版本明确、可追踪且以证据验证的 MySQL 8.4 基线。
- 非目标：本变更不创建或修改业务表，不改写现有 SQL，不修改 backend submodule 或 gitlink，不改变数据库托管方式，不引入 SQLFluff、Testcontainers 或新的运行时/构建依赖，也不安装通用多数据库 `sql-code-review` Skill。
- 验收结果：项目检出后可读取完整 `mysql` Skill 及参考文件；锁文件和批准清单包含正确记录；根级规则强制触发并保留 Flyway、MyBatis 参数安全、MySQL 8.4 和破坏性操作审批约束；Harness 对缺失、错误来源、未批准项或关键规则缺失给出失败结果。
- 主要风险：Skill 带有 PlanetScale 产品偏好，并包含对主键、collation、时间类型、分区和 DDL 的概括性建议；通过项目事实优先级、显式覆盖项和真实执行计划验证降低风险。

## Capabilities

### New Capabilities

- `mysql-database-sql-best-practices-skill`: 规定项目如何引入、触发、约束、校验和更新 MySQL 数据库设计与 SQL 最佳实践 Skill。

### Modified Capabilities

无。

## Impact

- 主仓库：`.agents/skills/mysql/`、`skills-lock.json`、`AGENTS.md`、`scripts/check-harness.sh`。
- 后端 submodule：本变更不修改 `backend/` 内部文件或 gitlink；后续 Flyway migration、MyBatis XML/注解 SQL 和数据库相关 Java 任务会受到新增规则约束。
- 外部来源：`planetscale/database-skills@mysql`。
- API、运行时依赖、现有数据库结构、数据和生产部署：无影响。
