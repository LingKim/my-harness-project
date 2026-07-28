# `require-mybatis-mapper-xml` 交付证据

> 本文件只记录实际发生的验证与审查。状态统一使用 `PASS`、`FAIL`、`BLOCKED`、`NOT_RUN`；不适用时写明原因，不得根据计划或 task checkbox 推测结果。

## 1. 基本信息

- Change：`require-mybatis-mapper-xml`
- 当前结论：`PASS`
- 最后更新：`2026-07-28 08:59 +08:00`
- 影响仓库：`root / backend（仅入口与 Mapper 说明）`
- 机器验证清单：`未生成`
- 机器清单时效：`不适用`
- 实现或检查范围：
  - `.codex/rules/backend-conventions.md`
  - `.codex/rules/database-conventions.md`
  - `.codex/skills/java-springboot/SKILL.md`
  - `scripts/test-ai-delivery-governance.py`
  - `scripts/check-harness.sh`
  - `README.md`
  - `backend/AGENTS.md`
  - `backend/README.md`
  - `backend/src/main/resources/mapper/README.md`
  - `openspec/specs/agent-skill-rule-governance/spec.md`
  - `openspec/specs/backend-java-best-practices-skill/spec.md`
  - `openspec/specs/mysql-database-sql-best-practices-skill/spec.md`

## 2. 自动化验证

| 时间 | 仓库 | 执行角色 | 命令 | 状态 | 关键输出摘要 |
| --- | --- | --- | --- | --- | --- |
| `2026-07-28 08:49` | `root` | `main_agent` | `python3 -m unittest scripts/test-ai-delivery-governance.py` | `FAIL` | RED：新增 XML-only 治理测试因当前 Rule 缺少强制约束而失败，7 tests、1 failure |
| `2026-07-28 08:53` | `root` | `main_agent` | `python3 -m unittest scripts/test-ai-delivery-governance.py` | `PASS` | GREEN：7 tests、0 failures |
| `2026-07-28 08:53` | `root` | `main_agent` | `bash -n scripts/check-harness.sh` | `PASS` | Harness 脚本语法检查通过 |
| `2026-07-28 08:56` | `root` | `main_agent` | `bash scripts/check-agent-governance.sh` | `PASS` | 七角色、7 个 AI delivery tests、5 个 collector tests、5 个 safety tests及前后端入口治理检查全部通过 |
| `2026-07-28 08:56` | `root` | `main_agent` | `bash scripts/check-harness.sh` | `PASS` | AIWorkSpace Harness、submodule 与集中 Agents/Rules/Skills 治理结构通过 |
| `2026-07-28 08:59` | `root` | `main_agent` | `openspec validate require-mybatis-mapper-xml --strict` | `PASS` | change valid |
| `2026-07-28 08:59` | `root` | `main_agent` | `openspec validate --all --strict` | `PASS` | 15 items passed、0 failed |
| `2026-07-28 08:59` | `root / backend` | `main_agent` | `git diff --check` / `git -C backend diff --check` | `PASS` | 两个仓库均无空白错误 |

## 3. 手工或真实场景验证

| 场景 | 环境 | 操作 | 期望 | 实际 | 状态 | 证据 |
| --- | --- | --- | --- | --- | --- | --- |
| XML-only 合同一致性 | 本地 checkout | 搜索 Rules、Java Skill、后端入口和 Mapper 说明 | 不再把注解 SQL作为新增自定义 SQL路径，保留 `BaseMapper<T>` 自动 CRUD | Rules、Skill、入口和说明表述一致；主规格旧允许合同已被 XML-only requirement 替换 | `PASS` | task 4.2；`reviews/spec-review.md` |
| 存量兼容 | 本地 checkout | 检查 backend Mapper diff | 不迁移现有注解 SQL，不改变业务行为 | 当前未修改任何 `*Mapper.java` | `PASS` | `git -C backend diff -- src/main/java` 无业务 Mapper 差异 |

## 4. QA 结论

- 是否执行：`是`
- 验收范围：XML-only Rule、Skill、Harness 契约与存量兼容边界。
- 通过项：RED 已证明检查能捕获缺失合同；GREEN 已证明当前合同与 Skill 哈希一致。
- 失败项：无未解决失败。
- 未验证项：未运行 frontend/backend build 与业务测试，因为没有修改运行时代码。
- 已知缺陷：无。
- 残余风险：治理检查验证稳定文本合同，不扫描未来全部业务源码；后续 change 仍需由开发、QA 与 Spec Reviewer 检查实际 Mapper SQL 位置。

## 5. Spec 合规审查

- 是否执行：`是`
- 完整报告：[`reviews/spec-review.md`](./reviews/spec-review.md)
- 正向覆盖率：`11/11` 个 delta spec 场景，`100%`
- 反向超纲项：无
- 阻断问题：无
- 最终结论：`PASS`

## 6. 体验走查

- 是否执行：`不适用`
- 完整报告：`未单独保存`
- 已检查页面或流程：无 UI 或运行时行为变化。
- P0/P1 问题：不适用。
- P2/P3 问题：不适用。
- 未验证设备或流程：不适用。
- 不适用或未运行原因：本 change 只修改治理合同与说明。

## 7. 未验证项与残余风险

| 项目 | 状态 | 原因 | 影响 | 后续处理 |
| --- | --- | --- | --- | --- |
| 现有后端注解 SQL | `NOT_RUN` | 已确认规格明确本 change 不迁移存量 SQL | 当前 Mapper 继续使用注解 SQL，只有后续实质修改时触发迁移 | 后续涉及对应 statement 的 change 按 Rule 迁入 XML |
| 业务源码语义扫描 | `NOT_RUN` | 本 change 只建设稳定治理合同，不建设完整静态扫描器 | Harness 不能单独证明未来所有 Mapper 均合规 | 开发、QA 与 Spec Reviewer 在业务 change 中检查实际 diff |

## 8. 最终交付结论

- tasks 是否全部完成：`是，12/12`
- 前端验证：`不适用`
- 后端验证：`NOT_RUN`（不修改业务代码，默认不运行无关 build）
- Harness：`PASS`
- OpenSpec strict validate：`PASS`（change 单独校验及 `--all --strict` 15/15）
- Spec Review：`PASS`
- Experience Review：`不适用`
- 机器验证清单时效：`不适用`
- 是否建议归档：`是，但必须先按顺序处理前置的 strengthen-engineering-practice-governance change`
- 结论依据：12/12 tasks 完成，治理/Harness/OpenSpec/diff 门禁通过，主规格已同步，Spec Review 无阻断问题；未运行 build 符合纯治理变更范围。

## 记录边界

- `backend` 子仓库在本 change 开始前已有 `AGENTS.md`、`README.md` 和 `scripts/check-agent-governance.sh` 未提交修改；本 change 只对前两个相关段落做最小追加，并保留既有修改。
- 未执行 frontend/backend build 或业务测试，因为本 change 不修改运行时代码。
- 未执行 commit、push、archive 或破坏性操作。
