# `strengthen-engineering-practice-governance` 交付证据

> 本文件只记录实际发生的验证与审查。状态统一使用 `PASS`、`FAIL`、`BLOCKED`、`NOT_RUN`；不适用时写明原因，不得根据计划或 task checkbox 推测结果。

## 1. 基本信息

- Change：`strengthen-engineering-practice-governance`
- 当前结论：`PASS`
- 最后更新：`2026-07-28 09:50 +08:00`
- 影响仓库：`root`、`frontend`、`backend`
- 机器验证清单：`未生成`
- 机器清单时效：`NOT_CHECKED`
- 实现或检查范围：
  - `openspec/changes/strengthen-engineering-practice-governance/`
  - `.codex/agents/backend_engineer.toml`
  - `.codex/agents/qa_engineer.toml`
  - `.codex/agents/spec_reviewer.toml`
  - `.codex/rules/backend-conventions.md`
  - `.codex/rules/database-conventions.md`
  - `.codex/skills/java-springboot/`
  - `scripts/validate-custom-agents.py`
  - `scripts/test-custom-agents.py`
  - `scripts/test-ai-delivery-governance.py`
  - `frontend/scripts/check-agent-governance.sh`
  - `backend/AGENTS.md`
  - `backend/README.md`
  - `backend/scripts/check-agent-governance.sh`

## 2. 自动化验证

| 时间 | 仓库 | 执行角色 | 命令 | 状态 | 关键输出摘要 |
| --- | --- | --- | --- | --- | --- |
| `2026-07-27 17:00` | `root` | `main_agent` | `python3 scripts/test-custom-agents.py` | `PASS` | 19 个 custom agent 失败夹具全部生效 |
| `2026-07-27 17:00` | `root` | `main_agent` | `python3 scripts/test-ai-delivery-governance.py` | `PASS` | 6 个 AI delivery governance tests 全部通过 |
| `2026-07-27 17:00` | `root` | `main_agent` | `bash scripts/check-agent-governance.sh` | `PASS` | Agent、Rules、Skill 来源及锁定检查通过 |
| `2026-07-27 17:00` | `root` | `main_agent` | `bash scripts/check-harness.sh` | `PASS` | Harness 全部检查通过 |
| `2026-07-27 17:00` | `root` | `main_agent` | `openspec validate strengthen-engineering-practice-governance --strict` | `PASS` | `Change 'strengthen-engineering-practice-governance' is valid` |
| `2026-07-27 17:00` | `root` | `main_agent` | `git diff --check` | `PASS` | `exit 0`，无空白错误 |
| `2026-07-27 17:00` | `root` | `main_agent` | `skill-creator/scripts/quick_validate.py .codex/skills/java-springboot` | `BLOCKED` | 系统 Python 与 Codex bundled Python 均缺少 `yaml` 模块，报 `ModuleNotFoundError: No module named 'yaml'` |
| `2026-07-28 09:08` | `root` | `main_agent` | `/Users/lilin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /Users/lilin/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/java-springboot` | `BLOCKED` | 归档前补跑仍因 bundled Python 缺少 `yaml` 失败；保留原 P3，不记为 Skill 内容失败 |
| `2026-07-28 09:50` | `root` | `main_agent` | `uv run --offline --no-project --with pyyaml==6.0.3 python /Users/lilin/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/java-springboot` | `PASS` | 使用本机 uv 缓存创建临时隔离环境，输出 `Skill is valid!`；未修改系统 Python、bundled runtime 或项目依赖 |

## 3. 手工或真实场景验证

| 场景 | 环境 | 操作 | 期望 | 实际 | 状态 | 证据 |
| --- | --- | --- | --- | --- | --- | --- |
| Java Skill 旧建议清理 | 本地工作区 | 搜索 Spring Data JPA、JPA entity、`JpaRepository`、Criteria API、`@DataJpaTest` | 不再出现与项目技术栈冲突的默认建议 | 搜索无匹配；MyBatis-Plus 默认路径与 Spring JDBC 受控例外表述一致 | `PASS` | `.codex/skills/java-springboot/SKILL.md`、相关 Specs/Rules/Agents |
| 三角色责任链 | 本地工作区 | 检查 backend 实现自检、QA 独立技术验证、Reviewer 只读技术基线对账合同 | 三段责任明确且权限不扩大 | 19 个失败夹具全部生效；`spec_reviewer` 仍为 `read-only` | `PASS` | 三个 Agent TOML 与 `scripts/validate-custom-agents.py` |
| 第一方 Skill 来源与锁 | 本地工作区 | 核对 Manifest、Skills 锁、内容哈希及旧第三方来源拒绝场景 | `java-springboot` 以项目维护 Skill 登记且可检测漂移 | 来源、路径、哈希和拒绝场景均通过治理测试 | `PASS` | `.codex/manifest.json`、`.codex/skills-lock.json`、AI delivery governance tests |

## 4. QA 结论

- 是否执行：是
- 验收范围：Agent 合同、第一方 Java Skill 来源与内容、MyBatis-Plus/Flyway 持久化基线、治理脚本和文档同步。
- 通过项：19 个 Agent 失败夹具、6 个 AI delivery governance tests、Agent governance、Harness、OpenSpec strict validate、旧建议搜索、`git diff --check`。
- 失败项：无。
- 未验证项：未运行 frontend/backend 业务 build 或业务测试，因为本 change 未修改业务源码、运行时依赖或产品行为。
- 已知缺陷：无；`quick_validate.py` 的 `PyYAML` 环境缺口已通过 uv 临时隔离依赖解决并取得 PASS。
- 残余风险：本 change 明确不新增业务源码语义门禁，工程语义仍依赖开发、QA 和 Reviewer 的职责链。

## 5. Spec 合规审查

- 是否执行：是
- 完整报告：`reviews/spec-review.md`
- 正向覆盖率：`9 / 9 = 100%`
- 反向超纲项：`0`
- 阻断问题：无 P0/P1 或阻断级偏差。
- 最终结论：`PASS`；原 `quick_validate.py` 缺少 `PyYAML` 的 P3 已关闭。

## 6. 体验走查

- 是否执行：不适用
- 完整报告：`未单独保存`
- 已检查页面或流程：无。
- P0/P1 问题：不适用。
- P2/P3 问题：不适用。
- 未验证设备或流程：不适用。
- 不适用或未运行原因：本 change 只调整 AI Coding 治理，不改变产品页面体验。

## 7. 未验证项与残余风险

| 项目 | 状态 | 原因 | 影响 | 后续处理 |
| --- | --- | --- | --- | --- |
| Skill 专用快速校验 | `PASS` | 使用 `uv run --offline --no-project --with pyyaml==6.0.3` 提供隔离依赖 | `quick_validate.py` 已输出 `Skill is valid!` | 后续复核沿用同一 uv 命令，无需污染系统 Python |
| frontend/backend 业务 build 与测试 | `NOT_RUN` | 本 change 只调整治理入口和说明，不修改业务源码、依赖或产品行为 | 不提供业务运行回归证据 | 后续业务 change 按风险运行对应 profile |
| 自动业务源码语义门禁 | `NOT_RUN` | 明确不在本 change 范围内 | 无法机器识别所有事务和持久化语义偏差 | 继续由实现、QA、Reviewer 三段职责链控制；如需自动化，另立 change |

## 8. 最终交付结论

- tasks 是否全部完成：是（14 / 14）
- 前端验证：`不适用`
- 后端验证：`NOT_RUN`（无业务源码、依赖或产品行为变更）
- Harness：`PASS`
- OpenSpec strict validate：`PASS`
- Spec Review：`PASS`
- Experience Review：`不适用`
- 机器验证清单时效：`NOT_CHECKED`
- 是否建议归档：已归档；全部已知验证问题已关闭
- 结论依据：14 项任务全部完成，治理、Harness、OpenSpec、Agent 合同测试、来源/锁测试和双向审查均通过，正向覆盖率 100%、反向超纲为 0；专用 Skill validator 已通过 uv 隔离环境补齐 `PyYAML 6.0.3` 并取得 PASS。

## 记录边界

- 不保存完整终端日志、缓存、凭据或无关业务内容。
- 规格确认后若实现、测试或配置变化，必须追加新的实际验证记录。
