## Context

ChinaMate 已通过根 `.codex/agents/`、`.codex/rules/` 和 `.codex/skills/` 建立七角色集中治理，并通过 `scripts/check-agent-governance.sh` 校验结构、引用和权限边界。当前治理仍有三个缺口：通用 `java-springboot` Skill 直接推荐 JPA；数据库约定只声明 MyBatis-Plus 是当前技术栈，没有规定业务持久化的默认路径和受控例外；开发、QA 与 Spec Reviewer 的合同没有分别要求实现、验证和审查工程实践合规。

本 change 只处理工程治理整改。自动识别 Spring JDBC、事务或 Mapper 结构的语义门禁属于后续可选整改，本 change 不实施。

## Goals / Non-Goals

**Goals:**

- 建立与项目技术栈一致、没有 JPA 默认建议的第一方 `java-springboot` Skill。
- 明确 MyBatis-Plus 业务持久化默认路径，以及直接使用 Spring JDBC 的最小例外合同。
- 让 `backend_engineer` 在实现阶段、`qa_engineer` 在验证阶段、`spec_reviewer` 在审查阶段分别承担工程实践合规职责。
- 保持现有七角色数量、集中治理目录和单人串行交付流程不变。

**Non-Goals:**

- 不创建数据库专用 Agent，也不改变现有角色写入边界。
- 不修改前端角色和 Vercel Skill。
- 不增加扫描源码语义的自动门禁，不修改业务源码。

## Decisions

### 1. 将 Java Skill 从第三方原文迁移为 ChinaMate 第一方 Skill

保留 `java-springboot` 名称和路径，重写 `SKILL.md`，以 Java 21、Spring Boot 4.1、模块化单体、MyBatis-Plus、Flyway 和当前项目测试方式为基线。Skill 登记与锁文件改为项目维护来源并更新内容哈希。

选择第一方 Skill，是因为当前第三方内容把 Spring Data JPA、`JpaRepository`、Criteria API 和 `@DataJpaTest` 作为默认最佳实践；仅在 Rule 中声明“忽略这些段落”会让执行角色同时接收冲突指令。备选方案是保留第三方原文再增加 wrapper，但这会形成两个 Java Skill 入口和额外优先级判断，不符合单一规范源原则。

### 2. MyBatis-Plus 是默认持久化方案，但保留受控 Spring JDBC 例外

业务表的常规 CRUD、条件查询和分页默认通过所属业务模块的 MyBatis-Plus Mapper 完成；复杂 SQL 可以使用 Mapper XML 或注解 SQL，并继续遵守参数绑定、显式列和数据库对象边界。

不绝对禁止 `JdbcTemplate` 或 `NamedParameterJdbcTemplate`。只有 MyBatis-Plus 无法合理表达、已有基础设施约束明确要求，或已确认设计记录了必要性时才能使用；例外必须限定在 `infrastructure`、说明替代方案与取舍，并具备等价测试。这样既防止静默绕过既定技术栈，也避免为了形式强行把不适合 Mapper 的底层操作塞进 MyBatis-Plus。

### 3. 三个角色形成实现、验证、审查的串行责任链

- `backend_engineer`：实现前列出适用技术基线和例外；实现中检查构造器注入、事务边界、分层、Mapper/数据库对象边界、Flyway 与参数绑定；完成报告给出实际遵循项和例外依据。
- `qa_engineer`：后端或数据库任务必须加载 Java/MySQL Skill 和相应 Rules，验证业务场景之外的事务原子性、持久化方案、migration 和数据库集成风险；发现生产偏差只报告，不越权修复。
- `spec_reviewer`：保留 Spec → 代码、代码 → Spec 双向对账，同时独立执行代码 → 项目 Rules/技术基线对账。即使业务 Spec 没有写明 MyBatis-Plus，违反稳定项目 Rule 仍必须被报告。

选择串行责任链而不是新增数据库 Agent，符合单人全栈 Skill 的角色视角模型，也避免多个写入角色争用后端文件。

### 4. 本 change 只收紧自然语言合同，不伪装成语义自动门禁

现有治理脚本继续验证结构、引用、权限和锁定信息。本 change 不宣称脚本能够理解事务是否正确或某段 Spring JDBC 是否合理。工程语义由开发角色自检、QA 验证和只读 Spec Reviewer 审查承担；是否新增 ArchUnit/静态扫描属于后续独立决策。

## Risks / Trade-offs

- [第一方 Skill 需要项目持续维护] → 在锁文件记录项目来源和内容哈希，版本变化通过独立 OpenSpec change 更新。
- [MyBatis-Plus 默认规则可能被误解为禁止所有 JDBC] → 在 Rule、Skill 和角色合同中使用一致的受控例外条件，并要求记录设计依据。
- [自然语言审查仍可能漏判] → 三阶段分别报告，降低单点遗漏；自动语义门禁明确留待后续，不虚报本 change 已解决。
- [角色报告变长] → 只要求列出任务直接相关的技术检查和例外，不复制完整 Rules 或 Skill 正文。

## Migration Plan

1. 更新三个 delta specs，并在用户确认后才进入实现。
2. 先重写 `java-springboot` Skill，再更新 Skill 登记、来源和内容哈希，避免角色指向中间冲突状态。
3. 更新后端与数据库 Rules，冻结 MyBatis-Plus 默认路径和 Spring JDBC 例外合同。
4. 按 `backend_engineer` → `qa_engineer` → `spec_reviewer` 顺序更新角色合同，保持既有写入边界。
5. 运行治理检查、OpenSpec strict validate 和 `git diff --check`，人工复核 Skill 不再包含 JPA 默认建议。
6. 回滚时整体恢复 Skill、锁文件、Rules 和三个 Agent 合同的前一版本；本 change 不涉及业务数据或运行时 migration。

## Open Questions

无。自动语义门禁、前端角色强化和数据库专用 Agent 均明确不属于本 change。
