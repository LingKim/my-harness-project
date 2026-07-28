## 1. 先建立治理合同测试

- [x] 1.1 在 `scripts/test-custom-agents.py` 增加失败夹具，证明 `backend_engineer` 缺少工程实践清单、`qa_engineer` 缺少 Java/MySQL 技术验证职责、`spec_reviewer` 缺少项目 Rule 合规审查时必须失败；先确认夹具能因现有校验器未覆盖而失败。
- [x] 1.2 在 `scripts/test-ai-delivery-governance.py` 或现有 Skill 锁定测试中增加第一方 `java-springboot` 来源、路径、内容哈希和旧第三方来源拒绝场景；不得把该检查扩张为业务源码语义扫描。

## 2. 重写 Java Skill 与持久化 Rules

- [x] 2.1 重写 `.codex/skills/java-springboot/SKILL.md`，覆盖 Java 21、Spring Boot 4.1、模块化单体、构造器注入、DTO/校验/异常、事务、日志、MyBatis-Plus/Flyway 和分层测试，并删除 JPA、`JpaRepository`、Criteria API 与 `@DataJpaTest` 默认建议。
- [x] 2.2 更新 `.codex/skills-lock.json`、`.codex/manifest.json` 及相关批准清单/说明，把 `java-springboot` 登记为项目维护来源并同步真实内容哈希。
- [x] 2.3 更新 `.codex/rules/backend-conventions.md` 和 `.codex/rules/database-conventions.md`，明确多步写入事务责任、MyBatis-Plus 默认持久化路径、Mapper/适配器边界以及 Spring JDBC 受控例外条件；不复制 Skill 正文。

## 3. 强化三个角色合同

- [x] 3.1 更新 `.codex/agents/backend_engineer.toml`，要求实现前识别技术基线与例外，实现后报告 Java、事务、分层、MyBatis-Plus、Flyway 和数据库安全检查结果。
- [x] 3.2 更新 `.codex/agents/qa_engineer.toml`，要求后端/数据库验证加载 `java-springboot`、`mysql` 与相关 Rules，独立验证事务原子性、持久化方案、migration 和数据库集成风险。
- [x] 3.3 更新 `.codex/agents/spec_reviewer.toml`，在既有 Spec 双向对账之外增加代码 → 项目 Rules/技术基线的独立合规结论，并保持 `read-only`。
- [x] 3.4 更新 `scripts/validate-custom-agents.py` 使三个角色缺失上述合同内容时失败，并让第 1.1 的失败夹具转绿；不得增加生产源码扫描或扩大任何角色权限。

## 4. 同步入口与交付证据

- [x] 4.1 按实际差异更新 `.codex/agents/README.md`、`.codex/rules/README.md`、`backend/AGENTS.md` 和根 `README.md` 中的来源、触发与角色交接说明；不修改前端业务或前端角色合同。
- [x] 4.2 使用 `docs/templates/openspec-change-evidence.md` 维护本 change 的 `evidence.md`，记录 Skill 冲突消除、角色合同检查、未运行项和“未新增业务源码语义门禁”的残余风险。

## 5. 验证与审查

- [x] 5.1 运行 `bash scripts/check-agent-governance.sh`、`bash scripts/check-harness.sh`、`openspec validate strengthen-engineering-practice-governance --strict` 和 `git diff --check`，记录真实结果；默认不运行无关 frontend/backend build。
- [x] 5.2 人工搜索 `.codex/skills/java-springboot/`，确认不再把 Spring Data JPA、JPA entity、`JpaRepository`、Criteria API 或 `@DataJpaTest` 作为项目建议，并确认 MyBatis-Plus 与 Spring JDBC 例外表述和 Specs/Rules/Agents 一致。
- [x] 5.3 使用 `spec_reviewer` 视角对 proposal、design、三个 delta specs、tasks 与实现做双向对账及项目 Rule 合规检查；P0/P1 或阻断偏差关闭前不得建议归档。
