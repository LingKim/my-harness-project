## 1. 建立 MySQL Skill 项目级基线

- [x] 1.1 使用 Skills CLI 将精确标识 `planetscale/database-skills@mysql` 仅安装到 `.agents/skills/mysql/`，复核 `SKILL.md`、`references/` 与 `skills-lock.json` 的来源、Skill 路径和内容哈希，并确认没有附带引入其他 Skill。
- [x] 1.2 记录安装前后的 `git status --short`、`git submodule status` 与两个 submodule 工作树状态，确认本变更不修改 `frontend/`、`backend/` 内部文件、现有 Flyway migration 或主仓库 gitlink。

## 2. 先建立失败门禁

- [x] 2.1 先修改 `scripts/check-harness.sh`，将 `mysql` 加入显式批准清单，并增加对 `.agents/skills/mysql/SKILL.md`、代表性 `references/` 文件、锁记录来源 `planetscale/database-skills`、Skill 路径、有效哈希和根级规则引用的断言。
- [x] 2.2 在根级 MySQL 规则尚未加入时运行 `bash -n scripts/check-harness.sh` 与 `./scripts/check-harness.sh`，确认 Harness 因缺失 MySQL Skill 触发或数据库安全规则而按预期失败，并保留可定位的失败信息。

## 3. 启用数据库与 SQL 最佳实践规则

- [x] 3.1 修改根目录 `AGENTS.md`，规定涉及 MySQL 配置、Flyway migration、MyBatis XML/注解 SQL、schema、字段类型、约束、索引、查询、事务锁、连接或数据库运维的编写、评审和重构任务必须完整读取 `mysql/SKILL.md`，并按任务读取直接相关参考文件。
- [x] 3.2 在 `AGENTS.md` 明确事实优先级与项目覆盖：保留 Docker Compose MySQL 8.4、InnoDB、MyBatis-Plus 和 Flyway-only；忽略 PlanetScale/Vitess 托管偏好；主键、collation、时间类型、分区与 DDL 算法必须按业务语义、官方文档和真实证据决定。
- [x] 3.3 在 `AGENTS.md` 增加 SQL 安全与验证规则：业务值使用 `#{}`，`${}` 仅接受服务端封闭白名单；应用查询默认显式列；索引和优化由查询模式及 `EXPLAIN` 支撑；`EXPLAIN ANALYZE` 仅在安全环境用于只读 SQL；破坏性操作执行前必须获得明确人工批准并提供恢复方案。

## 4. 失败场景与最终验证

- [x] 4.1 使用可恢复的临时改动验证：移除 MySQL Skill 强制触发规则、移除 Flyway/MyBatis 参数安全规则或向 `skills-lock.json` 加入未批准 Skill 时，Harness 均因正确原因失败；每次验证后立即恢复真实文件并确认没有遗留测试数据。
- [x] 4.2 运行 `bash -n scripts/check-harness.sh`、`./scripts/check-harness.sh`、`git diff --check` 和固定版本 OpenSpec strict validate，确认 MySQL Skill、现有 Java/React Skill、批准清单和数据库安全规则全部通过；本变更不运行无关 build 或连接数据库执行 SQL。
- [x] 4.3 最终复核主仓库实际差异、两个 submodule 状态和 gitlink，交付说明中记录 Skill 来源、适用范围、PlanetScale 偏好覆盖、未安装通用 `sql-code-review` 的原因、风险边界和后续显式更新方式；未经用户授权不提交或推送。
