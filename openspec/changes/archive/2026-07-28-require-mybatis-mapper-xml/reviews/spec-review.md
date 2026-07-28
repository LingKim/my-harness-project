# `require-mybatis-mapper-xml` Spec 合规审查

## 结论

- 审查结论：`PASS`
- 阻断问题：无
- P0/P1：无
- 正向覆盖率：`11/11` 个 delta spec 场景已覆盖（`100%`）
- 反向超纲项：无
- 兼容策略：backend 当前 14 处 SQL 注解属于已确认存量，本 change 未修改任何 `src/main/java` 文件；后续实质修改对应 statement 时必须迁入 XML。

## Spec → 实现正向对账

| Spec | 场景 | 状态 | 实现或证据 |
| --- | --- | --- | --- |
| `mysql-database-sql-best-practices-skill` | 新增常规业务持久化 | 已覆盖 | `.codex/rules/database-conventions.md` `RULE-DB-009`；`.codex/skills/java-springboot/SKILL.md` |
| 同上 | 使用 `BaseMapper` 自动 CRUD | 已覆盖 | `RULE-DB-009` 和 `RULE-BE-010` 明确保留自动 CRUD，不重复 XML |
| 同上 | 新增自定义 SQL | 已覆盖 | `RULE-DB-009` 强制业务目录 XML、全限定 `namespace` 和对应 statement ID |
| 同上 | 实质修改存量注解 SQL | 已覆盖 | 两个 Rules、Java Skill、backend 入口和 Mapper 说明均规定触及时迁移，纯格式修改不触发 |
| 同上 | 复杂查询不能由通用 CRUD 合理表达 | 已覆盖 | Rule/Skill 统一要求 Mapper XML，禁止 SQL/Provider 注解 |
| 同上 | 直接使用 Spring JDBC | 已覆盖 | `RULE-DB-009` 保留已确认 design、限定范围、取舍和等价测试条件 |
| 同上 | 缺少例外依据的 JDBC 实现 | 已覆盖 | `RULE-DB-009` 保留阻断级偏差结论 |
| `backend-java-best-practices-skill` | Java Skill 实现持久化用例 | 已覆盖 | Java Skill 路由 MyBatis-Plus、Mapper XML、数据库 Rules 和 Flyway |
| 同上 | Java Skill 使用 `BaseMapper` 自动 CRUD | 已覆盖 | Java Skill 明确保留自动 CRUD且无需重复 XML |
| 同上 | Java Skill 新增自定义 SQL | 已覆盖 | Java Skill 要求业务目录、`namespace`、statement ID 和安全绑定 |
| 同上 | 多步数据库写入 | 已覆盖 | Java Skill 既有事务边界与失败回滚规则保持不变 |

## 实现 → Spec 反向对账

| 实现 | Spec/任务依据 | 状态 |
| --- | --- | --- |
| 新增 `RULE-BE-010` | proposal Goals；tasks 2.2；backend Java delta spec | 有依据 |
| 收紧 `RULE-DB-009` | MySQL delta spec；tasks 2.1 | 有依据 |
| 更新 Java Skill 与 hash | backend Java delta spec；tasks 2.3 | 有依据 |
| 新增治理单测和 Harness 内容检查 | proposal Goals；design Decision 4；tasks 1.2、1.3 | 有依据 |
| 更新根/后端 README、入口和 Mapper 说明 | proposal Impact；tasks 3.1、3.2 | 有依据 |
| 同步前一治理 change 的三个主规格 | design Context/Migration Plan；tasks 1.1 | 有依据，属于本 change 实施前置条件 |
| 保留 backend 存量 SQL 注解 | proposal Non-Goals；design Decision 3；MySQL delta spec 存量场景 | 有依据 |

## 项目 Rules 与技术基线合规

- `RULE-WF-001`：先建立并由用户确认 OpenSpec，再实施，符合。
- `RULE-DB-009` / `RULE-BE-010`：XML-only、`BaseMapper<T>` 例外和存量触及时迁移表述一致。
- Skill 锁：`java-springboot` 的 `computedHash` 与 `contentHash` 已更新且治理单测通过。
- 子仓库边界：只修改 backend 的入口和 Mapper 说明，未修改业务 Mapper、依赖、migration 或运行时行为。
- Git 安全：未 commit、push、archive；保留 backend 开始前已有未提交修改。
- 质量门禁：治理单测、Agent governance、Harness、OpenSpec strict validate、根/backend `git diff --check` 均通过。

## Action Items

无阻断 Action Item。后续任何实质修改现有 14 处注解 statement 的 change，必须在同一 change 中迁入 Mapper XML，并运行相应数据库行为验证。
