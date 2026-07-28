## 1. 冻结基线与建立失败检查

- [x] 1.1 在实施前确认 `strengthen-engineering-practice-governance` 已完成同步或归档，并复核其 MyBatis-Plus requirement 已成为本 change 的有效基线；未满足时停止修改 Rules。
- [x] 1.2 在 `scripts/test-ai-delivery-governance.py` 增加失败检查，证明 `database-conventions.md` 或 `java-springboot/SKILL.md` 缺少 Mapper XML 强制约束、错误允许注解 SQL或错误禁止 `BaseMapper<T>` 自动 CRUD 时必须失败；先确认检查对当前实现为红。
- [x] 1.3 按实际校验入口更新 `scripts/check-harness.sh` 或 `scripts/check-agent-governance.sh`，校验 XML-only 合同存在且不再接受“XML 或注解 SQL”的冲突表述；不得宣称该文本检查能够替代业务源码语义审查。

## 2. 收紧后端持久化治理合同

- [x] 2.1 更新 `.codex/rules/database-conventions.md` 的 `RULE-DB-009`，规定新增或实质修改的自定义 SQL 必须使用 Mapper XML，禁止 SQL 注解和 Provider 注解，保留 `BaseMapper<T>` 自动 CRUD及 `@Mapper`、`@Param`。
- [x] 2.2 更新 `.codex/rules/backend-conventions.md`，要求后端自定义 SQL 遵循 XML-only 路径和存量 statement 触及时迁移规则，且不把普通 Java 格式修改误判为迁移触发条件。
- [x] 2.3 更新 `.codex/skills/java-springboot/SKILL.md`，把复杂/自定义 SQL 的建议由“XML 或注解 SQL”改为强制 Mapper XML，并同步 `.codex/skills-lock.json` 中的真实内容哈希。

## 3. 同步入口与文档

- [x] 3.1 更新 `backend/src/main/resources/mapper/README.md`，明确业务子目录、XML `namespace`、statement ID、参数绑定、`BaseMapper` 例外和存量注解 SQL触及时迁移规则。
- [x] 3.2 按实际差异更新 `backend/AGENTS.md`、根 `README.md` 和必要的 Rules/Agents 索引说明，移除继续推荐新增注解 SQL的表述；不修改现有后端业务 Mapper。
- [x] 3.3 使用 `docs/templates/openspec-change-evidence.md` 创建并维护 `openspec/changes/require-mybatis-mapper-xml/evidence.md`，记录旧治理 change 基线、失败检查、实际修改、未迁移存量 SQL 和残余风险。

## 4. 验证与合规审查

- [x] 4.1 运行 `python3 -m unittest scripts/test-ai-delivery-governance.py`、`bash scripts/check-agent-governance.sh`、`bash scripts/check-harness.sh`、`openspec validate require-mybatis-mapper-xml --strict` 和 `git diff --check`，记录真实结果；默认不运行无关 frontend/backend build。
- [x] 4.2 搜索 `.codex/rules/`、`.codex/skills/java-springboot/`、`backend/AGENTS.md` 和 Mapper 说明，确认没有继续把注解 SQL作为新增自定义 SQL的允许路径，并确认 `BaseMapper<T>` 自动 CRUD 未被误禁。
- [x] 4.3 使用 `spec_reviewer` 视角逐条对账 proposal、design、两个 delta specs、tasks、Rules、Skill、校验和证据，单独报告“现有后端注解 SQL未迁移”的兼容策略；存在 P0/P1 或阻断偏差时不得建议归档。
