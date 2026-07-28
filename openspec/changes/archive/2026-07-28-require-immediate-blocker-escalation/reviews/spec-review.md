# `require-immediate-blocker-escalation` Spec 合规审查

## 1. 审查范围与结论

- 审查时间：`2026-07-28 10:06 +08:00`
- 审查范围：change 的 proposal、design、delta spec、tasks；根治理实现差异；主规格同步；自动化验证清单
- 正向覆盖率：Requirement `1/1`（`100%`）；Scenario `6/6`（`100%`）
- 反向超纲项：`0`
- P0/P1/P2/P3 Action Items：`0`
- 最终结论：`PASS`

## 2. 正向对账（Spec → 实现）

| Spec 条目 | 状态 | 实现与证据 |
| --- | --- | --- |
| 可由用户解除的当前必需步骤阻塞必须立即升级 | 已覆盖 | `AGENTS.md:43` 提供不可降低入口；`.codex/rules/workflow.md:34-40` 定义完整稳定合同 |
| 工具操作需要额外授权 | 已覆盖 | `.codex/rules/workflow.md:36-38` 要求同阶段正式审批、最小范围和禁止跳过；本轮 `quick_validate.py` 权限阻塞后实际即时申请并复跑通过 |
| 必须由用户作出决策 | 已覆盖 | `.codex/rules/workflow.md:36-38` 覆盖必须决策、请求内容与禁止擅自改变目标或范围 |
| 现有授权内存在等价安全路径 | 已覆盖 | `.codex/rules/workflow.md:39` 明确安全、可验证且不改变结果时自主继续 |
| 替代路径会降低交付质量 | 已覆盖 | `.codex/rules/workflow.md:39` 明确改变交付结果或降低证据时必须请示 |
| 用户拒绝授权或暂未响应 | 已覆盖 | `.codex/rules/workflow.md:40` 要求保护状态、记录影响并禁止重复无信息请求或伪造完成 |
| 外部故障不能由用户授权解除 | 已覆盖 | `.codex/rules/workflow.md:40` 要求继续安全诊断，不能错误包装为授权问题 |

控制与防回归证据：

- `.codex/skills/chinamate-fullstack-delivery/references/control-matrix.md:11` 将 `RULE-WF-006` 登记为三仓库 `CRITICAL`、主 Agent、`USER_CONFIRMATION` 控制。
- `scripts/test-ai-delivery-governance.py:53-77` 使用稳定 Rule ID 校验三处治理接入；`:84-118` 覆盖根入口、Rule 定义和控制矩阵缺失三类失败夹具。
- `.codex/skills-lock.json:4-9` 已同步项目 Skill 内容哈希；`quick_validate.py` 输出 `Skill is valid!`。
- `reviews/verification-manifest.json` 显示 Agent governance、Harness、OpenSpec strict validate 和 diff check 全部 `PASS`。

## 3. 反向对账（实现 → Spec）

| 实现差异 | Spec / Design 依据 | 状态 |
| --- | --- | --- |
| 根 `AGENTS.md` 增加薄入口 | proposal `What Changes`、design 的入口/稳定 Rule 分层决策 | 有依据 |
| 新增 `RULE-WF-006` | delta requirement 及 6 个 scenarios | 有依据 |
| 控制矩阵新增 Critical 控制 | proposal、design 决策与风险控制 | 有依据 |
| 新增治理基线与三类失败夹具 | tasks 1.1、2.4；design Migration Plan | 有依据 |
| 更新项目 Skill 锁哈希 | 现有集中治理规格要求 Skill 内容变化必须同步锁定信息 | 有依据 |
| 同步主规格、evidence 和验证清单 | tasks 3.1、3.2、4.1-4.4 与 `RULE-WF-003/004` | 有依据 |

未发现未经规格授权的业务、前端、后端、数据库、依赖或 submodule gitlink 改动。

## 4. 项目 Rules 与技术基线

- `RULE-WF-001`：规格已在用户回复“确认”后进入实现，符合。
- `RULE-WF-002`：先取得 RED，再完成 GREEN；tasks 按完成进度即时更新，符合。
- `RULE-WF-003/004`：主规格已同步，验证与 evidence 已维护，符合。
- `RULE-WF-006`：本轮真实权限阻塞已通过正式审批即时升级并继续，符合。
- `RULE-GIT-001`：本轮未执行暂存、提交、推送或归档，符合当前授权边界。
- 前端、后端、数据库技术 Rules：本 change 未修改对应实现，不适用。

## 5. Action Items

无。若审查后继续修改覆盖范围内的实现、测试或规格，应重新运行受影响的治理 profile 并更新 evidence。
