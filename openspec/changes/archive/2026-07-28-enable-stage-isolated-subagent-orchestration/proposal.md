## Why

当前单人全栈交付把七个角色主要当作主 Agent 串行切换的职责视角，非平凡阶段可能仍由同一上下文静默模拟，交接也容易退化为聊天摘要或口头完成声明。这削弱了阶段隔离、独立复核、跨会话恢复和责任追溯；现在需要把已经确认的第三种方案固化为“主 Agent 控制面 + 按阶段或独立工作包创建最少必要 fresh subagent”，并用可验证的结构化合同替代口头交代。

## What Changes

- **BREAKING**：把单人全栈默认编排从“主 Agent 串行模拟七种角色视角”改为“主 Agent 签发/验收合同，适用 specialist 按阶段或独立工作包以 fresh subagent 执行”；不要求七个角色常驻或全部启动。
- 建立 `TaskContract`、`ResultContract`、`ReviewResult` 和 `CorrectionContract` JSON 合同及其 freshness、状态、路径边界、验证与用户/Git gate 约束。
- 规定主 Agent 是唯一合同签发者与验收者；subagent 不得生成用户确认、擅自派工，或把推荐的下一角色当作已授权任务。
- 为重要 change 在自身 `handoffs/` 保存 request/result/review/correction 执行快照与审计回执，同时保持 OpenSpec、Git、测试和 `evidence.md` 各自的既有事实源地位。
- 固化 fresh/reuse 规则：新独立工作包创建 fresh subagent；同一合同被 review/QA 退回时可复用原 subagent 修复；合同关闭后新工作包重新创建 fresh subagent。
- 固化并行与阶段门禁：前后端仅在合同冻结、依赖满足且写范围不冲突时并行；QA 在实现稳定后；`spec_reviewer` 与 `experience_reviewer` 可按适用性并行执行只读审查。
- 增加角色路由矩阵、JSON Schema/validator、freshness、路径边界、finding 修复闭环和治理引用一致性的自动化门禁；脚本只验证可判定的结构和引用，不声称理解自然语言语义。
- 保留简单任务、纯文案、紧密依赖运行时输出和全局重构的最短路径或受控降级；subagent 能力不可用时必须如实标记执行模式，不得伪装成多 Agent 交付。

### 目标

- 让每个非平凡阶段或独立工作包都有明确角色、权威输入、写入边界、验收条件和可审计结果。
- 让下游 Agent 只依赖已验收合同、权威 artifacts、真实源码/Git/测试，而不依赖聊天摘要、上游思考过程或口头完成声明。
- 在共享工作区中把“未接收脏代码”定义为流程拒收，并仅在授权与 cleanup 规则允许时使用 worktree 提供物理隔离。

### 非目标

- 不修改 `frontend/` 或 `backend/` 业务实现。
- 不增加第八个角色或新增 `code_reviewer`；当前仍保持七个 custom agents。
- 不建立外部队列、数据库或服务，也不要求每次运行全部七角色。
- 不自动执行 commit、push、gitlink 更新或归档。
- 不把 `handoffs/` 合同变成第二套 OpenSpec 生命周期或新的事实源。

### 可衡量的验收结果

- 治理测试覆盖角色路由、合同 schema/必填字段/枚举、路径边界、输入 fingerprint freshness、review finding 到 correction 的闭环，以及 Skill/Rule/README/manifest 引用一致性。
- 重要 change 的有效合同能被 validator 接受；输入变化后的旧合同被判为 `STALE`，必须重签或显式重新验收后才能进入下游阶段。
- reviewer finding 均有稳定 `findingId`，阻断 finding 未关闭时合同不能被验收或进入下一阶段。
- 没有 specialist 能力时输出明确的降级模式与未执行项，不产生虚假的 subagent 结果或用户授权。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `solo-fullstack-ai-delivery`：将串行角色视角改为阶段隔离的最少必要 subagent 编排，并增加结构化合同、freshness、review/correction 闭环、并行边界和受控降级要求。

## Impact

- 受影响的治理入口：根 `AGENTS.md`、`.codex/agents/`、`.codex/rules/`、`.codex/skills/chinamate-fullstack-delivery/`、`.codex/manifest.json`、`README.md`。
- 受影响的验证能力：根 `scripts/` 下 Agent/AI delivery 治理 validator、JSON Schema 与失败夹具。
- 受影响的 OpenSpec 规范：`openspec/specs/solo-fullstack-ai-delivery/spec.md`；重要 change 后续可新增 `handoffs/` 审计快照。
- 不改变业务 API、数据库结构、前后端运行时依赖或部署架构。

### 风险

- 合同字段过多可能增加简单任务成本；通过路由矩阵、最短路径和显式降级模式控制。
- 共享工作区可能出现并发写冲突；通过合同写入白名单、依赖检查和冲突时串行化控制，而不是承诺不存在物理脏状态。
- 合同快照可能漂移或成为第二事实源；通过输入 fingerprint、`STALE` 状态和既有事实源优先级控制。
- 机器门禁可能被误解为语义审查；validator 仅声明结构、路径、fingerprint 和引用层面的可判定结论，自然语言判断仍由 reviewer、主 Agent 或用户承担。
