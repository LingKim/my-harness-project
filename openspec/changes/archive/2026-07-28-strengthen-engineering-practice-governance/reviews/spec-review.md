# `strengthen-engineering-practice-governance` Spec 与项目 Rule 合规审查

## 检查范围

- OpenSpec：`proposal.md`、`design.md`、`tasks.md` 和三个 delta specs。
- 实现：根 `.codex/agents/`、`.codex/rules/`、`.codex/skills/`、Manifest/锁文件、治理脚本与说明文档；frontend/backend 仅检查治理入口和说明。
- 验证：RED 失败输出、19 个 custom agent 失败夹具、AI delivery governance tests、Agent governance、Harness、OpenSpec strict validate、旧 Java 持久化建议搜索和 `git diff --check`。

## 一、正向对账表（Spec → 代码）

| # | Spec 来源 | 要求摘要 | 状态 | 代码位置 / 说明 |
| --- | --- | --- | --- | --- |
| 1 | `agent-skill-rule-governance` ADDED | backend、QA、Reviewer 形成实现/验证/审查责任链 | ✅ | `.codex/agents/backend_engineer.toml:13-38`、`qa_engineer.toml:15-48`、`spec_reviewer.toml:11-81` |
| 2 | `agent-skill-rule-governance` MODIFIED | Reviewer 同时执行 Spec 双向对账和项目 Rule/技术基线对账 | ✅ | `.codex/agents/spec_reviewer.toml:14-41,69-81` |
| 3 | `backend-java-best-practices-skill` MODIFIED | `java-springboot` 迁移为可追踪第一方 Skill | ✅ | `.codex/manifest.json`、`.codex/skills-lock.json`、`scripts/test-ai-delivery-governance.py:71-88` |
| 4 | `backend-java-best-practices-skill` MODIFIED | Skill 与 Java 21、Spring Boot 4.1、模块化单体、MyBatis-Plus/Flyway 一致 | ✅ | `.codex/skills/java-springboot/SKILL.md:1-79`；旧持久化建议搜索无匹配 |
| 5 | `backend-java-best-practices-skill` MODIFIED | Harness 校验第一方来源、路径与哈希 | ✅ | `scripts/check-harness.sh`、`scripts/check-agent-governance.sh`、`backend/scripts/check-agent-governance.sh`；Harness PASS |
| 6 | `mysql-database-sql-best-practices-skill` ADDED | 常规持久化默认 MyBatis-Plus，Spring JDBC 仅为受控例外 | ✅ | `.codex/rules/database-conventions.md:53-58`、`.codex/skills/java-springboot/SKILL.md:48-54`、`backend/AGENTS.md` |
| 7 | `tasks.md 1.1-1.2` | 先建立角色合同与第一方来源 RED 测试 | ✅ | 初始执行分别因未拒绝新夹具、Manifest 缺少 Java Skill 而失败；实现后相关测试 PASS |
| 8 | `tasks.md 2-4` | Skill、Rules、角色、锁、入口和 evidence 同步 | ✅ | 对应文件均已修改；未修改任何业务源码或运行时依赖 |
| 9 | `tasks.md 5.1-5.2` | 治理/Harness/OpenSpec/差异与旧建议搜索 | ✅ | 规定命令均 PASS；Skill 专用 `quick_validate.py` 已使用 uv 隔离环境补齐 `PyYAML 6.0.3` 并输出 `Skill is valid!` |

## 二、反向对账表（代码 → Spec）

| # | 代码位置 | 实现内容 | 状态 | Spec 依据 |
| --- | --- | --- | --- | --- |
| 1 | `.codex/skills/java-springboot/SKILL.md` | 第一方 Java/Spring Boot 工作流 | ✅ | Java Skill MODIFIED requirements、design 决策 1 |
| 2 | `.codex/rules/backend-conventions.md` | 事务失败回滚与工程实践报告 | ✅ | Java Skill requirement、Agent 责任链 requirement |
| 3 | `.codex/rules/database-conventions.md` | `RULE-DB-009` | ✅ | MySQL ADDED requirement、design 决策 2 |
| 4 | `.codex/skills/chinamate-fullstack-delivery/references/control-matrix.md` | 为 `RULE-DB-009` 指定 REVIEW 责任 | ✅ | design 决策 3、既有控制矩阵规范 |
| 5 | 三个 Agent TOML | 实现、QA、Reviewer 技术合同 | ✅ | Agent 责任链 requirement |
| 6 | `scripts/validate-custom-agents.py` 与测试 | 对关键合同文本做结构校验 | ✅ | tasks 1.1、3.4；未扫描业务源码 |
| 7 | Manifest、Skills 锁和治理脚本 | Java Skill 从第三方分区迁移到项目分区 | ✅ | Java Skill 来源与 Harness requirements |
| 8 | frontend/backend 治理脚本与说明 | 同步新的锁结构和后端入口 | ✅ | proposal Impact、tasks 2.2、4.1 |
| 9 | README 与索引 | 说明第一方 Skill、默认持久化和责任链 | ✅ | proposal Impact、documentation Rule |
| 10 | `reviews/spec-review.md` | 持久化本次只读审查 | ✅ | tasks 5.3、交付证据 Rule |

## 二-A、代码 → 项目 Rules/技术基线

| # | Rule / 技术基线 | 状态 | 代码与验证证据 | 结论 |
| --- | --- | --- | --- | --- |
| 1 | `RULE-WF-001/002` | ✅ | 用户确认后实施；RED → GREEN；tasks 随完成更新 | 合规 |
| 2 | `RULE-DOC-001/002` | ✅ | 人类可读内容为中文，入口、README、Manifest 和锁同步 | 合规 |
| 3 | `RULE-BE-007/009` | ✅ | Skill 和后端 Rule 明确事务原子性、失败回滚和完成清单 | 合规 |
| 4 | `RULE-DB-009` | ✅ | Skill、Rule、backend Agent/入口使用相同默认路径与例外条件 | 合规 |
| 5 | `RULE-QA-003/004` | ⚠️ | 本轮命令结果可追溯；未生成 machine manifest，治理 change 不需要应用构建 | 不阻断；evidence 记录 NOT_CHECKED |
| 6 | `RULE-REPO-*` | ✅ | frontend/backend 只修改治理入口/说明，未改业务代码；各仓状态已单独检查 | 合规 |
| 7 | `RULE-GIT-001` | ✅ | 未执行 stage、commit、push 或 gitlink 更新 | 合规 |

## 三、状态说明

| 标记 | 含义 |
| --- | --- |
| ✅ | 已覆盖且有实现与验证证据 |
| ❌ | 未覆盖或无依据超纲 |
| ⚠️ | 已覆盖但存在非阻断未验证项或环境限制 |

## 四、覆盖率统计

```text
正向覆盖率：9 / 9 = 100%
反向超纲项：0
项目 Rule 合规：6 条完整合规，1 条非阻断未生成 machine manifest
```

| 来源 | 总条数 | ✅ | ❌ | ⚠️ | 覆盖率 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Agent governance delta | 2 | 2 | 0 | 0 | 100% |
| Java Skill delta | 3 | 3 | 0 | 0 | 100% |
| MySQL delta | 1 | 1 | 0 | 0 | 100% |
| Tasks/验证 | 3 | 3 | 0 | 0 | 100% |

## 五、修复 Action Items

无。原 P3 已通过 `uv run --offline --no-project --with pyyaml==6.0.3` 补跑关闭，且未污染系统 Python、Codex bundled runtime 或项目依赖。

## 最终结论

`PASS`：没有 P0/P1、阻断级 Spec 偏差或无依据超纲实现。专用 Skill validator 已取得 PASS，原环境依赖 P3 已关闭。
