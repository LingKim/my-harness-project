## Why

当前项目允许把自定义 SQL 同时写在 Mapper XML 或 `@Select`、`@Insert`、`@Update`、`@Delete` 等注解中，导致 SQL 与 Java 接口混排，后续复杂查询的维护位置不统一。项目需要把 Mapper XML 固化为今后自定义 SQL 的唯一默认承载方式，使 SQL 组织、审查和排查路径保持一致。

## Goals

- 明确今后新增或实质修改的自定义 SQL 必须写入 Mapper XML。
- 禁止新增 MyBatis 注解 SQL，同时保留 MyBatis-Plus `BaseMapper<T>` 自动 CRUD。
- 让后端 Rule、数据库 Rule、Java Skill 和治理检查对同一约束保持一致。

## Non-Goals

- 本 change 不迁移当前后端已有的注解 SQL，也不修改后端业务行为。
- 不要求为 `BaseMapper<T>` 自动生成的通用 CRUD 人工补写 XML。
- 不改变 Flyway-only schema 管理、参数绑定、显式列和模块边界规则。

## What Changes

- **BREAKING**：今后新增或实质修改的自定义 SQL 不再允许使用 `@Select`、`@Insert`、`@Update`、`@Delete` 或对应 Provider 注解，必须放入所属 Mapper 的 XML。
- 保留 `@Mapper`、`@Param` 等不承载 SQL 文本的注解，以及 MyBatis-Plus `BaseMapper<T>` 自动 CRUD。
- 将现有注解 SQL登记为存量实现；本 change 不强制一次性迁移，但后续实质修改对应 statement 时必须迁入 XML。
- 同步后端/数据库 Rules、`java-springboot` Skill 和治理校验，避免继续出现“XML 或注解 SQL”的冲突表述。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `mysql-database-sql-best-practices-skill`：把自定义 SQL 的默认承载方式由“XML 或注解 SQL”收紧为“必须使用 Mapper XML”，并明确 `BaseMapper` 与存量注解 SQL的边界。
- `backend-java-best-practices-skill`：要求 Java Skill 将自定义 SQL 路由到 Mapper XML，不再推荐注解 SQL。

## Impact

- 主仓库：`.codex/rules/backend-conventions.md`、`.codex/rules/database-conventions.md`、`.codex/skills/java-springboot/SKILL.md`、相关治理校验与说明。
- OpenSpec：修改两个既有治理 capability，覆盖新增 SQL、存量 SQL 修改和 `BaseMapper` 自动 CRUD 场景。
- 后端子仓库：本 change 不修改现有业务代码；后续后端 change 必须在 `src/main/resources/mapper/<业务>/` 中维护 XML，并保证 `namespace` 与 Mapper 接口全限定名一致。
- 风险：Rule 生效后，Java 接口与 XML 需要跨文件维护；通过固定目录、`namespace` 和 statement ID 对应关系降低定位成本。
