# `persist-change-delivery-evidence` 交付证据

## 1. 基本信息

- Change：`persist-change-delivery-evidence`
- 当前结论：`PASS`（治理验证完成，Spec Review 无阻断项）
- 最后更新：`2026-07-27 10:03 +08:00`
- 影响仓库：`root`
- 实现或检查范围：
  - `AGENTS.md`、`README.md`
  - `.codex/agents/`、`.codex/rules/`
  - `scripts/check-agent-governance.sh`、custom agent 校验与失败夹具
  - `docs/templates/`、`docs/plans/`
  - `openspec/changes/persist-change-delivery-evidence/`
- 范围排除：
  - `docs/plans/openspec-change-approval-backlog.md` 及 `docs/plans/README.md` 中对应“待评估事项”导航来自本 change 创建前用户单独要求的文档任务，不属于本 change 实现；当前工作区继续保留，不回退、不计为超纲实现。

## 2. 自动化验证

| 时间 | 仓库 | 执行角色 | 命令 | 状态 | 关键输出摘要 |
| --- | --- | --- | --- | --- | --- |
| `2026-07-27 本轮，早于 09:43；准确分钟未记录` | `root` | `main_agent` | `python3 scripts/validate-custom-agents.py` | `FAIL`（预期 RED） | 因 `qa_engineer.toml` 缺少交付证据合同内容 `evidence.md` 而失败 |
| `2026-07-27 本轮，早于 09:43；准确分钟未记录` | `root` | `main_agent` | `./scripts/check-agent-governance.sh` | `FAIL`（预期 RED） | 因缺少 `docs/templates/openspec-change-evidence.md` 而失败 |
| `2026-07-27 09:43` | `root` | `main_agent` | `python3 scripts/test-custom-agents.py` | `PASS` | 16 个 custom agent 失败夹具全部生效 |
| `2026-07-27 09:43` | `root` | `main_agent` | `./scripts/check-agent-governance.sh` | `PASS` | 七个 Agent、前后端入口与集中治理结构通过 |
| `2026-07-27 09:43` | `root` | `main_agent` | `./scripts/check-harness.sh` | `PASS` | Harness、submodule 与 Agents/Rules/Skills 治理结构完整 |
| `2026-07-27 09:43` | `root` | `main_agent` | `openspec validate --all --strict` | `PASS` | 10 items passed，0 failed |
| `2026-07-27 09:43` | `root` | `main_agent` | `git diff --check` | `PASS` | exit 0，无空白错误 |
| `2026-07-27 09:52` | `root` | `main_agent` | `bash -n scripts/check-agent-governance.sh` | `PASS` | exit 0，Shell 语法有效 |
| `2026-07-27 09:52` | `root` | `main_agent` | `bash -n scripts/check-harness.sh` | `PASS` | exit 0，Shell 语法有效 |
| `2026-07-27 09:52` | `root` | `main_agent` | `python3 scripts/test-custom-agents.py` | `PASS` | 最终范围下 16 个失败夹具全部生效 |
| `2026-07-27 09:52` | `root` | `main_agent` | `./scripts/check-agent-governance.sh` | `PASS` | 最终范围下根、前端和后端治理结构通过 |
| `2026-07-27 09:52` | `root` | `main_agent` | `./scripts/check-harness.sh` | `PASS` | 最终范围下 Harness 通过 |
| `2026-07-27 09:52` | `root` | `main_agent` | `openspec validate --all --strict` | `PASS` | 10 items passed，0 failed |
| `2026-07-27 09:52` | `root` | `main_agent` | `git diff --check` | `PASS` | exit 0，无空白错误 |
| `2026-07-27 10:03` | `root` | `main_agent` | `python3 scripts/test-custom-agents.py` | `PASS` | delta specs 同步到 main specs 后，16 个失败夹具全部生效 |
| `2026-07-27 10:03` | `root` | `main_agent` | `./scripts/check-agent-governance.sh` | `PASS` | 规格同步后七个 Agent、前后端入口与集中治理结构通过 |
| `2026-07-27 10:03` | `root` | `main_agent` | `./scripts/check-harness.sh` | `PASS` | 规格同步后 Harness 与 submodule 治理结构通过 |
| `2026-07-27 10:03` | `root` | `main_agent` | `openspec validate --all --strict` | `PASS` | 2 个 change 的 delta specs 已同步；10 个 main specs 与 2 个活动 change 共 12 items passed，0 failed |
| `2026-07-27 10:03` | `root` | `main_agent` | `git diff --check` | `PASS` | exit 0，无空白错误 |

## 3. 手工或真实场景验证

| 场景 | 环境 | 操作 | 期望 | 实际 | 状态 | 证据 |
| --- | --- | --- | --- | --- | --- | --- |
| 治理门禁 RED | 本地根仓库 | 在模板和 Agent 证据合同尚未补齐时运行校验 | 因目标缺失项失败 | 分别因缺少模板和 QA `evidence.md` 合同失败；准确分钟未保留，已在自动化验证表如实标注 | `PASS` | 本轮真实命令与失败摘要 |
| 新失败夹具有效 | Python 临时目录 | 删除 QA、Spec Reviewer、Experience Reviewer 的证据合同内容 | 校验器准确拒绝 | 三个新增夹具均被拒绝 | `PASS` | `scripts/test-custom-agents.py` 输出 |

## 4. QA 结论

- 是否执行：是，由主 Agent 执行治理自动化测试。
- 验收范围：Agent TOML 证据合同、模板存在性、根入口路由、Harness 回归。
- 通过项：16 个失败夹具、正式 Agent 校验、前后端入口检查、根 Harness、两项 Shell 语法检查、OpenSpec strict validate 和 `git diff --check`；最终范围已在 09:52 从头重跑。
- 失败项：第一次运行新增 QA 夹具时，`replace_once` 未移除第二处 `evidence.md`，导致夹具未失败；已改为 `replace_all` 并从头重跑通过。
- 未验证项：未运行前端 lint/typecheck/test/E2E、后端 Maven 测试或真实页面验证，因为本变更未修改应用源码、测试逻辑、API、数据库或运行时依赖。
- 已知缺陷：无未关闭自动化缺陷。
- 残余风险：Markdown 证据仍依赖主 Agent 如实汇总，第一版不提供自动时效判断或防篡改能力。

## 5. Spec 合规审查

- 是否执行：是，已完成初审、范围澄清和最终复审。
- 完整报告：[`reviews/spec-review.md`](./reviews/spec-review.md)。
- 正向覆盖率：最终复审 61/65 = 93.8%；四个 ⚠️ 均为报告保存、evidence 回填和 task 勾选的职责内闭环项，现已完成。
- 反向超纲项：0；本 change 前的用户独立待办文档已按真实范围排除。
- 阻断问题：无 P0/P1，无实现缺口或反向超纲功能。
- 最终结论：`PASS_WITH_ISSUES`；报告中的 P2/P3 交接 Action Items 已由主 Agent 完成，无未关闭阻断项。
- 归档前时效复核：main specs 同步只把已审查的 delta requirements 合并到领域规格，未修改治理实现、测试或 change delta；已在 10:03 重跑治理、Harness、strict validate 和差异检查，因此原 Spec Review 结论继续有效。

## 6. 体验走查

- 是否执行：不适用。
- 完整报告：未创建。
- 已检查页面或流程：无。
- P0/P1 问题：不适用。
- P2/P3 问题：不适用。
- 未验证设备或流程：无应用页面变更。
- 不适用原因：本 change 仅修改根治理、模板、校验脚本和 OpenSpec artifacts，不包含可运行 UI。

## 7. 未验证项与残余风险

| 项目 | 状态 | 原因 | 影响 | 后续处理 |
| --- | --- | --- | --- | --- |
| Spec 合规复审 | `PASS` | 最终复审为 `PASS_WITH_ISSUES`，无 P0/P1；职责内落盘项和 delta spec 同步均已完成 | 不阻塞交付 | 归档后随 change 长期保留 evidence |
| 前端业务验证 | `NOT_RUN` | 无前端应用改动 | 不影响本次治理交付结论 | 不需要运行无关 build/test |
| 后端业务验证 | `NOT_RUN` | 无后端应用改动 | 不影响本次治理交付结论 | 不需要运行无关 build/test |
| 自动时效与防篡改 | `NOT_RUN` | 明确属于第一版非目标 | 证据依赖人工维护 | 试运行两到三个 change 后再评估 |

## 8. 最终交付结论

- tasks 是否全部完成：是。
- 前端验证：不适用。
- 后端验证：不适用。
- Harness：`PASS`
- OpenSpec strict validate：`PASS`
- Spec Review：`PASS_WITH_ISSUES`，无未关闭阻断项。
- Experience Review：不适用。
- 是否建议归档：是；delta specs 已同步，归档前复核已通过。
- 结论依据：治理实现、16 个失败夹具、Agent 治理、Harness、两项 Shell 语法、OpenSpec strict validate 和 `git diff --check` 均通过；10:03 在 main specs 同步后再次验证 12 items 全部通过；Spec Review 无 P0/P1、反向超纲为 0，Experience Review 因无 UI 变更不适用。
