## Context

主仓库通过根级 `AGENTS.md`、项目级 `.agents/skills/`、`skills-lock.json` 和 `scripts/check-harness.sh` 统一 AI Coding 行为。项目已固定 MySQL 8.4、Docker Compose、MyBatis-Plus 3.5.17 与 Flyway-only，但尚无覆盖 schema、索引、SQL、事务锁和安全迁移的专用 Skill。

当前候选中，`planetscale/database-skills@mysql` 面向 MySQL/InnoDB，覆盖表结构、数据类型、索引、执行计划、事务锁、在线 DDL 和连接管理，并把详细规则拆分为按需加载的参考文件。`github/awesome-copilot@sql-code-review` 虽来自 GitHub 官方仓库，但面向多种数据库，部分 JOIN、子查询和索引建议过度概括；`mindrally/skills@mysql-best-practices` 则包含 MyISAM、旧复制命令和过时参数，不适合 MySQL 8.4 强制基线。

PlanetScale Skill 同样不是 MySQL 官方规范：它包含托管产品偏好，以及对主键、collation、时间类型、分区阈值和在线 DDL 的默认建议。因此接入必须保留项目与版本事实优先级，不能把 Skill 全文无条件转成项目规范。

## Goals / Non-Goals

**Goals:**

- 将 `mysql` 作为可版本化、可追踪的项目级 MySQL 数据库与 SQL 最佳实践 Skill。
- 让 MySQL schema、Flyway migration、MyBatis SQL、索引、查询、事务锁和运维任务明确触发该 Skill。
- 通过项目覆盖规则保留 Docker Compose、MySQL 8.4、InnoDB、MyBatis-Plus 与 Flyway-only 契约。
- 建立参数安全、显式列、证据化索引和破坏性操作审批等最低 SQL 门禁。
- 扩展 Harness，验证 Skill 来源、文件、锁记录、批准清单和根级关键规则。

**Non-Goals:**

- 不修改 backend submodule、现有 migration、SQL、业务表、数据或 gitlink。
- 不把数据库迁移到 PlanetScale、Vitess 或其他托管平台。
- 不安装 `sql-code-review`、`mysql-best-practices` 或其他重叠 Skill。
- 不引入 SQLFluff、Testcontainers、数据库代理或新的 Maven/运行时依赖。
- 不在缺少业务模型和工作负载时预先规定所有表、字段、主键或索引模板。

## Decisions

### 1. 采用 PlanetScale 的 MySQL 专用 Skill

使用 `planetscale/database-skills@mysql`，因为它聚焦 MySQL/InnoDB，规则覆盖范围与本项目数据库任务一致，并提供可按主题加载的详细参考文件。

备选 `github/awesome-copilot@sql-code-review` 是跨数据库审查清单，容易把其他方言或概括性建议带入 MySQL；备选 `mindrally/skills@mysql-best-practices` 含过时内容。两者均不作为强制基线。

### 2. 项目级精确安装并锁定完整参考文件

使用 Skills CLI 只把 `mysql` 安装到 `.agents/skills/mysql/`。`skills-lock.json` 记录 `planetscale/database-skills`、`skills/mysql/SKILL.md` 与内容哈希，Harness 批准清单增加 `mysql`，并检查入口和代表性参考文件，避免只留下入口而缺失实际规则。

全局安装无法保证其他开发者、CI 或代理得到相同内容，因此不采用。安装整个仓库的全部 Skills 会扩大未经审查的规则面，也不采用。

### 3. 根级规则按数据库任务触发并按需加载参考文件

涉及 `compose.yaml` 的 MySQL 配置、`backend/src/main/resources/db/migration/`、MyBatis XML/注解 SQL、表结构、字段类型、约束、索引、查询、事务锁、连接或数据库运维时，必须先完整读取 `mysql/SKILL.md`，再读取与任务直接相关的 `references/` 文件。

事实优先级固定为：当前 OpenSpec 与活动 change → `backend/` 局部规则、实际 schema、SQL、依赖和测试 → MySQL 8.4 当前官方文档与安全环境中的执行计划证据 → `mysql` Skill → 代理既有知识。

### 4. 用项目契约覆盖托管偏好和绝对化建议

当前环境继续使用 Docker Compose MySQL 8.4 与 InnoDB，不采用 Skill 的 PlanetScale 托管推荐或 Vitess 特有假设。`BIGINT UNSIGNED AUTO_INCREMENT`、`utf8mb4_0900_ai_ci`、`DATETIME`、分区阈值和 `ALGORITHM=INPLACE` 等只能作为候选，需要根据业务标识、比较语义、时区语义、数据量、MySQL 8.4 能力与真实变更计划决定。

数据库结构继续只由 Flyway migration 修改。应用查询默认显式列；索引必须由查询模式支撑，性能优化使用 `EXPLAIN` 或在安全、非生产环境对只读语句使用 `EXPLAIN ANALYZE`。由于 `EXPLAIN ANALYZE` 会实际执行语句，不得对写入或破坏性 SQL 直接使用。

MyBatis 值参数必须使用 `#{}`。`${}` 只能用于无法参数化的标识符或 SQL 片段，且输入必须来自服务端封闭白名单，禁止拼接用户输入。`DROP`、`TRUNCATE`、无条件 `DELETE`/`UPDATE`、不可逆字段或索引删除等操作必须在执行前获得明确人工批准，并提供备份、兼容发布、回滚和部署后验证方案。

### 5. Harness 只验证确定性接入契约

Harness 检查 Skill 入口、代表性参考文件、批准清单、锁记录来源和哈希，以及 `AGENTS.md` 中的触发、Flyway-only、MyBatis 参数安全、版本优先级和破坏性操作审批引用。它不尝试静态证明每条业务 SQL 的性能或安全，也不替代 migration 测试、执行计划和真实环境验证。

## Risks / Trade-offs

- [Skill 带有 PlanetScale 产品偏好] → 根级规则明确继续使用现有 Docker Compose MySQL 8.4，并排除托管与 Vitess 假设。
- [绝对化类型、collation、分区或 DDL 建议误导设计] → 要求结合业务语义、MySQL 8.4 官方文档、真实数据量和执行证据逐项决策。
- [`EXPLAIN ANALYZE` 会实际执行语句] → 仅允许在安全环境对确认只读的 SQL 使用，写操作使用 `EXPLAIN` 或专门测试方案。
- [MyBatis `${}` 造成 SQL 注入] → 默认使用 `#{}`，`${}` 必须是服务端封闭白名单且不得接受用户输入。
- [Skill 更新导致内容漂移] → 锁定哈希，更新必须显式执行、审查差异并重新验证。
- [Harness 文本断言不能保证所有 SQL 合规] → Harness 只做接入门禁，具体变更仍需 migration 测试、代码评审和执行计划证据。

## Migration Plan

1. 使用精确 Skill 标识安装 `mysql`，复核入口、参考文件和 `skills-lock.json`，确认没有附带其他 Skill。
2. 先扩展 Harness 的批准清单、文件、锁记录和根级引用断言，在规则尚未加入时得到预期失败。
3. 修改根级 `AGENTS.md`，加入触发范围、事实优先级、项目覆盖、SQL 参数安全和破坏性操作审批规则，恢复 Harness 通过。
4. 验证两个 submodule 与 gitlink 未变化，运行 Shell 语法、Harness、差异和 OpenSpec 严格检查；不运行无关 build。

回滚时从批准清单、锁文件、根级规则和项目级 Skills 目录移除 `mysql` 即可，不涉及应用代码、数据库结构或数据迁移。

## Open Questions

无。SQLFluff、Testcontainers、统一 schema 命名模板或数据库 CI 将在出现对应业务需求时单独提案。
