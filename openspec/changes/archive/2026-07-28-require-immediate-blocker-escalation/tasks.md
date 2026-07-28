## 1. 治理测试先行

- [x] 1.1 在治理检查脚本中增加失败夹具，验证缺少根 `AGENTS.md` 阻塞升级入口、`RULE-WF-006` 或控制矩阵登记时检查必须失败
- [x] 1.2 运行新增失败夹具并记录 RED 证据，确认现有治理文本尚未满足新合同

## 2. 落地阻塞即时升级规则

- [x] 2.1 在根 `AGENTS.md` 的不可降低边界中增加简洁入口：可由用户授权或决策解除的当前流程阻塞必须立即申请，不得静默卡住或跳过必需步骤
- [x] 2.2 在 `.codex/rules/workflow.md` 新增 `RULE-WF-006`，明确触发条件、最小授权请求内容、安全等价替代路径以及拒绝或无法解除时的真实阻塞处理
- [x] 2.3 更新 `.codex/skills/chinamate-fullstack-delivery/references/control-matrix.md`，将 `RULE-WF-006` 登记为主 Agent 的关键流程控制
- [x] 2.4 更新治理检查脚本，使根入口、Workflow Rule 与控制矩阵合同完整时新增检查转绿

## 3. 规格同步与交付证据

- [x] 3.1 将本 change 的 delta spec 同步到 `openspec/specs/agent-skill-rule-governance/spec.md`，保持主规格与已实现治理合同一致
- [x] 3.2 使用 `docs/templates/openspec-change-evidence.md` 创建并维护 `openspec/changes/require-immediate-blocker-escalation/evidence.md`，记录 RED/GREEN、未运行项和残余风险

## 4. 验证与审查

- [x] 4.1 运行 Agent governance 检查及其失败夹具，确认新规则存在且防回归检查有效
- [x] 4.2 运行 Harness 检查、`openspec validate require-immediate-blocker-escalation --strict` 和 `git diff --check`，记录最新输出
- [x] 4.3 执行 Spec → 实现与实现 → Spec 双向只读审查，将结果写入 `openspec/changes/require-immediate-blocker-escalation/reviews/spec-review.md` 并修复阻断项
- [x] 4.4 复核 tasks、主规格和 `evidence.md`，确认无未解决的失败、阻塞或规格偏差后再进入归档流程
