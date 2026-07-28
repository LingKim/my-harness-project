---
name: chinamate-fullstack-delivery
description: 编排 ChinaMate 阶段隔离的多 Agent 全栈 AI Coding 交付。用于由主 Agent控制阶段与硬关卡，并按独立工作包创建最少必要 fresh subagent，从产品需求、交互与跨栈契约推进到前后端、数据库、QA、Spec/体验审查、证据和归档；也用于结构化合同交接、跨会话恢复、受控验证或证据时效检查。
---

# ChinaMate 阶段隔离全栈交付

主 Agent作为控制面，按阶段或独立工作包创建最少必要的 fresh subagent。七个custom agents是独立执行或审查上下文，不是主Agent在同一上下文中模拟的职责视角；不为形式完整启动全部角色。

## 开始

1. 读取根 `AGENTS.md`、Agents/Rules 索引、`README.md`、`openspec/config.yaml`。
2. 运行 `openspec list --json`，确定活动 change；续作时读取该 change 的全部 apply context。
3. 检查根仓库和受影响 submodule 的 `git status --short --branch`，保护已有改动。
4. 使用临时 worktree、准备依赖或运行完整后端测试前，读取 [验证 Profiles](references/verification-profiles.md) 并运行只读环境预检；`BLOCKED` 不得记为业务失败，`REVIEW_REQUIRED` 必须先关闭风险。
5. 从 OpenSpec、Git、测试和 `evidence.md` 推导阶段，不把聊天记录或 task checkbox 当作完成证据。
6. 读取[角色路由](references/role-routing.md)与[阶段路由](references/stage-routing.md)，选择最短安全路径并报告：当前阶段、执行模式、已确认事实、阻塞、下一动作、所需specialist和硬关卡。
7. 重要change由主Agent按[阶段交接合同](references/handoff-contracts.md)签发`TaskContract`；合同通过validator后才创建对应fresh subagent。

## 核心纪律

- 非平凡行为必须先有完整 OpenSpec，当前版本规格经用户确认后才实现。
- 阶段依赖默认按产品/规格 → 交互与契约 → 实现 → QA → Spec Review → Experience Review → evidence/归档建议推进；前后端只在合同冻结、依赖满足且写入根不冲突时并行，两个只读reviewer按适用性并行。
- 新独立工作包创建fresh subagent；同一合同被QA/reviewer退回时可用`CorrectionContract`复用原subagent，合同关闭后的新工作包必须fresh。
- 主Agent是`TaskContract`/`CorrectionContract`唯一签发者、`ResultContract`/`ReviewResult`唯一验收者，也是change根`handoffs/`唯一持久化写入者。specialist不得生成用户确认、自行派工或直接写handoffs。
- 下游只消费已验收合同、权威artifacts、真实源码/Git/测试，不依赖聊天摘要、上游思考过程或口头完成声明。
- 需求来源必须引用 PRD ID、设计节点、用户原话或已有 Spec；没有依据的相似行为列为待确认或非目标，不擅自扩张。
- `FAIL`、阻断级 Spec 偏差或 P0/P1 体验问题未关闭时回到修复/验证阶段，不建议归档。
- 分页、阈值、稳定排序、重试或幂等场景必须用跨越边界两侧的 fixture；单条 CRUD smoke test 不得证明分页通过。
- 临时数据库、服务、worktree、分支或路径需要清理时，先声明 cleanup manifest；只有只读 checker 证明全部目标为 `ABSENT`/`CLOSED` 才声称零残留。
- commit、push、gitlink 更新、归档和破坏性操作始终遵守用户授权，不由本 Skill 自动执行。
- 简单任务可选择`SINGLE_AGENT_FAST_PATH`；subagent不可用时如实标记`DEGRADED`或`BLOCKED`，不得伪造多Agent交付。
- `EVIDENCE_AND_ARCHIVE`只由主Agent控制，不签发specialist合同，也不新增第八角色。
- 只有已确认的根治理 change 没有现有specialist归属时，主Agent才可使用`CONTROL_PLANE_IMPLEMENTATION + main_agent + CONTROL_PLANE`受限分支；`allowedWritePaths`必须逐项列出validator allowlist内的精确文件。控制面`ResultContract`必须通过`resultFingerprint`交给现有`QA/qa_engineer`与`SPEC_REVIEW/spec_reviewer`独立复核，`EXPERIENCE_REVIEW`不适用；该分支不得替代业务specialist、QA或review。

## 按需加载

- 需要选择角色、并行关系或写入根时，读取[角色路由](references/role-routing.md)。
- 需要判断阶段、短路径、恢复或交接时，读取[阶段路由](references/stage-routing.md)。
- 需要签发、验收、持久化或修复交接时，读取[阶段交接合同](references/handoff-contracts.md)，并运行`scripts/validate_handoff_contract.py`。
- 需要检查 Rule 责任、硬门禁或完成条件时，读取 [控制矩阵](references/control-matrix.md)。
- 涉及业务术语、跨栈定位、API/数据归属或需求追溯时，读取 [知识路由](references/knowledge-routing.md)、`docs/architecture/system-map.md` 和 `docs/standards/domain-glossary.md`。
- 需要运行验证或生成机器清单时，读取 [验证 Profiles](references/verification-profiles.md)，再运行 `scripts/collect_verification.py`。
- 需要检查 worktree 依赖或 Java/Mockito 环境时，运行 `scripts/check_delivery_environment.py`；需要复核清理终态时，运行 `scripts/check_delivery_cleanup.py`。
- 验证后代码、测试、规格或配置发生变化时，运行 `scripts/check_verification_freshness.py`，旧结果为 `STALE` 时重跑受影响 profile。

## 输出当前状态

使用以下最小格式，避免长篇重复规则：

```markdown
## 单人全栈交付状态
- Change：
- 当前阶段：
- 执行模式：SUBAGENT / CONTROL_PLANE / SINGLE_AGENT_FAST_PATH / DEGRADED / BLOCKED
- 已确认事实：
- 当前失败/阻塞/未验证项：
- 当前合同与specialist：
- 下一动作与退出条件：
- 需要用户确认：
```

未来新change的首个产品合同在tasks创建前使用`taskIds: ["BOOTSTRAP-PRODUCT-SPEC"]`；本能力rollout的规划阶段为pre-capability，不追溯伪造合同。完成前把真实验证与审查结果汇总到change的`evidence.md`；handoff和机器manifest只记录可判定事实，不代替QA、Spec Review、体验与最终结论。
