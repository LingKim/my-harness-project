## Why

当前七个 custom agents、技术 Rules 与治理脚本能够证明配置结构和引用存在，却不能证明角色实际采用项目指定的前端、Java/Spring Boot、MyBatis-Plus 与 MySQL 工程实践。现有 Java Skill 还直接推荐与项目技术栈冲突的 JPA 路径，而角色合同未要求开发、QA 和 Reviewer 分别执行、验证和审查工程实践合规，说明“提示性引用”尚未形成可执行的责任链。

## Goals

- 将 MyBatis-Plus 与 Java/Spring Boot 工程实践转化为角色必须执行、审查和报告的明确合同。
- 消除 `java-springboot` Skill 中与项目 MyBatis-Plus 技术栈冲突的 JPA 默认建议。
- 让开发、QA 和 Spec Review 在各自阶段检查技术 Rule 合规，而不是等到功能完成后只核对业务 Spec。
- 保持七角色、根 `.codex/` 集中治理和单人串行交付模型不变。

## Non-Goals

- 不新增第八个数据库 Agent，不把单人交付改造成必须并行的虚拟团队。
- 不在本 change 修改前端或后端业务实现，也不引入新的运行时依赖。
- 不在本 change 建设或扩展自动语义门禁；该事项留待用户决定是否继续后续整改。

## What Changes

- 重写项目 `java-springboot` Skill，使其以 Java 21、Spring Boot 4.1、模块化单体和 MyBatis-Plus 为项目默认路径，移除 JPA、`JpaRepository`、Criteria API 与 `@DataJpaTest` 建议。
- 明确 MyBatis-Plus 持久化合同：业务数据库访问默认通过所属模块的 Mapper/适配器完成；直接使用 Spring JDBC 必须有已确认设计依据、限定范围和等价验证，不能静默替换项目持久化方案。
- 强化 `backend_engineer`，要求实现前建立技术合规清单，实现中检查事务、Mapper、数据库对象边界和当前官方文档，完成时报告偏差与例外依据。
- 强化 `qa_engineer`，要求根据后端与数据库影响范围加载 Java 与 MySQL Skills，并验证技术栈、事务、持久化和相关 Rule，而不只验证业务场景。
- 强化 `spec_reviewer`，将既有 Spec 双向对账扩展为“Spec 合规 + 项目 Rule 合规”两条独立结论，阻断无依据的持久化技术替换。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `agent-skill-rule-governance`: 强化 `backend_engineer`、`qa_engineer` 和 `spec_reviewer` 的技术实践执行、验证与审查合同。
- `backend-java-best-practices-skill`: 将通用第三方 Java Skill 替换为与 ChinaMate Java 21、Spring Boot 4.1、模块化单体和 MyBatis-Plus 一致的项目级 Skill。
- `mysql-database-sql-best-practices-skill`: 明确 MyBatis-Plus 是业务持久化默认方案，并定义直接使用 Spring JDBC 的受控例外条件。

## Impact

- 主仓库：`.codex/agents/backend_engineer.toml`、`.codex/agents/qa_engineer.toml`、`.codex/agents/spec_reviewer.toml`、`.codex/rules/backend-conventions.md`、`.codex/rules/database-conventions.md`、`.codex/skills/java-springboot/`、Skill 登记与锁定信息。
- 子仓库：按需更新 `backend/AGENTS.md`、后端说明和前后端治理检查入口中的 Skill 锁定结构；不修改业务代码、前端角色、Vercel Skill 或运行时依赖。
- OpenSpec：修改三个既有治理 capability；后续业务 change 必须按新合同生成、实现和审查。
- 兼容性：角色输出合同会收紧；Java Skill 的来源和内容哈希会从第三方通用内容迁移为项目维护内容。
- 风险：规则过度刚性可能阻止合理的 Spring JDBC 例外，因此通过“已确认设计依据 + 限定范围 + 等价验证”保留受控例外。
