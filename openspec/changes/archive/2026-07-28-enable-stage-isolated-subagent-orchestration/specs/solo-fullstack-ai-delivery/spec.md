## ADDED Requirements

### Requirement: 单人模式按阶段创建隔离角色执行上下文
系统 SHALL 由主 Agent 作为控制面，根据阶段和独立工作包选择最少必要的现有 specialist，并为每个新的独立工作包创建 fresh subagent。适用 specialist 能力可用时，主 Agent MUST NOT 静默模拟角色完成非平凡产品规格、交互、实现、QA 或审查阶段；系统 MUST NOT 要求七个角色常驻或每次全部启动。

#### Scenario: 非平凡阶段存在适用 specialist
- **WHEN** 当前 change 已达到某个非平凡阶段，且对应 custom agent 可用
- **THEN** 主 Agent 签发该阶段的 `TaskContract` 并创建最少必要的 fresh subagent
- **AND** 主 Agent 只承担阶段恢复、合同签发与验收、用户/Git 硬关卡和证据汇总，不在同一上下文中冒充该 specialist 完成交付

#### Scenario: 同一合同被审查退回修复
- **WHEN** QA 或 reviewer 对仍处于打开状态的合同返回需要修复的 finding
- **THEN** 主 Agent MAY 向原执行 subagent 签发 `CorrectionContract` 并复用该 subagent 修复
- **AND** 修复结果仍须通过原合同的验收条件与适用复核

#### Scenario: 已关闭合同后出现新工作包
- **WHEN** 一个合同已经关闭，随后产生不属于原 correction 闭环的新任务或新阶段
- **THEN** 主 Agent MUST 签发新的 `contractId` 并创建 fresh subagent
- **AND** 不得把旧 subagent 的上下文当作新工作包的权威输入

### Requirement: 无 specialist 归属的控制面实现使用受限主 Agent合同
系统 SHALL 允许已确认治理 change 中没有现有 specialist 归属的根控制面实现使用受限的主 Agent合同分支。该分支 MUST 仅使用 `stage = CONTROL_PLANE_IMPLEMENTATION`、`role = main_agent` 和 `executionMode = CONTROL_PLANE` 的组合，且只适用于根 `.codex/` 治理定义、当前编排 Skill、治理 validator/测试及其根入口或导航文件；`main_agent` MUST 只是合同中的控制面执行者标记，不得登记为 specialist `role`、第八个 custom agent 或可委派阶段。该分支 MUST NOT 用于业务、产品规格、交互、前端、后端、QA、review、体验审查、运行时基础设施或 Git 写操作。

#### Scenario: 已确认治理change需要实现根控制面
- **WHEN** 用户已确认的治理 change 包含根控制面实现任务，现有七个 specialist 均不拥有其目标文件，且 `TaskContract` 列出的全部精确文件均落在控制面 allowlist
- **THEN** 主 Agent MAY 签发并执行 `CONTROL_PLANE_IMPLEMENTATION` 合同，再返回与该 request fingerprint 关联的真实 `ResultContract`
- **AND** 该合同的规格确认 gate 必须为 `SATISFIED` 并含真实证据引用，Git gate 仍按当前授权独立判定

#### Scenario: 控制面合同尝试扩大到其他职责
- **WHEN** 控制面合同使用目录级 `.codex/`、`scripts/`、`docs/` 或项目根授权，包含 allowlist 外文件，或把 stage/role/executionMode 的任一控制标记与 specialist 标记混用
- **THEN** validator MUST 拒绝该合同并指出越界字段或不合法组合
- **AND** 主 Agent不得用该例外执行产品规格、交互、业务实现、前后端、QA 或任何 review 工作

#### Scenario: QA和Spec Review复核控制面实现
- **WHEN** 受限控制面 `ResultContract` 已返回且输入保持 fresh
- **THEN** 主 Agent分别向现有 `qa_engineer` 和 `spec_reviewer` 签发适用的 specialist 合同，其 `ReviewResult.resultFingerprint` 必须引用该真实控制面结果
- **AND** reviewer 仍使用 `QA` 或 `SPEC_REVIEW` stage，不得使用 `CONTROL_PLANE_IMPLEMENTATION`、冒充 `main_agent` 或获得写权限

### Requirement: 阶段交接使用结构化 JSON 合同
系统 SHALL 为阶段交接提供 `TaskContract`、`ResultContract`、`ReviewResult` 和 `CorrectionContract` 的版本化 JSON Schema。所有合同 MUST 包含 `schemaVersion`、`contractId`、`change`、`stage`、`role` 和 `taskIds`；各合同还 MUST 按类型包含权威输入路径及 fingerprint、依赖、允许与禁止写入范围、预期输出、验收条件、验证计划或摘要、用户与 Git gates、结果状态、修改文件、偏差、阻塞、未运行项、残余风险以及 reviewer finding 所需的 `findingId`。Schema MUST 把七个可委派 stage/role 组合与受限控制面组合建模为互斥分支，并保持 `ReviewResult` 仅属于现有 QA 或 reviewer。

#### Scenario: 签发可执行工作包
- **WHEN** 主 Agent 向 specialist 签发 `TaskContract`
- **THEN** validator 接受的合同包含可解析的权威输入、依赖、路径边界、预期输出、验收条件、验证以及用户/Git gate 状态
- **AND** 下游执行者无需读取聊天摘要或上游思考过程即可确定任务边界

#### Scenario: 合同缺少必填字段或使用未知枚举
- **WHEN** 任一合同缺少对应 schema 的必填字段、使用未知 `stage`、`role`、结果状态或 gate 状态
- **THEN** validator 返回失败并指出字段位置
- **AND** 主 Agent不得把该合同标记为已签发、已验收或可进入下一阶段

#### Scenario: bootstrap派工时tasks尚未创建
- **WHEN** 主 Agent为尚未创建 tasks 的新 change 签发首个 `PRODUCT_SPEC` bootstrap 合同
- **THEN** `TaskContract` 与对应 `ResultContract` 的 `taskIds` MUST 使用稳定保留值 `BOOTSTRAP-PRODUCT-SPEC`
- **AND** `taskIds` 不得为空，也不得伪造尚不存在的数字 task ID

#### Scenario: 控制面结果与request身份不一致
- **WHEN** `CONTROL_PLANE_IMPLEMENTATION` 结果没有关联同目录 request，或其 change、taskIds、stage、role 与 request 不一致
- **THEN** validator MUST 拒绝该结果，不能把它作为 `ReviewResult.resultFingerprint` 的有效目标
- **AND** 不得通过事后构造结果替代真实的控制面执行链

### Requirement: 主 Agent独占合同授权与验收
主 Agent SHALL 是 `TaskContract` 和 `CorrectionContract` 的唯一签发者，也是 `ResultContract` 与 `ReviewResult` 的唯一验收者及 change 根 `handoffs/` 的唯一持久化写入者。subagent MUST 只返回结构化 payload，MUST NOT 直接写入 `handoffs/`、生成用户确认、扩大用户或 Git 授权、自行派发下一角色，或把下一角色建议当作已授权合同。

#### Scenario: subagent建议下一角色
- **WHEN** specialist 在结果中建议由 QA、开发者或 reviewer 继续处理
- **THEN** 该建议只作为 `ResultContract` 的建议或阻塞信息返回主 Agent
- **AND** 在主 Agent签发新合同前不得视为已派工

#### Scenario: 用户确认门禁尚未满足
- **WHEN** 合同需要规格确认、外部写入或 Git 授权，但没有可追溯的真实用户消息
- **THEN** gate 保持 `PENDING`
- **AND** subagent 与主 Agent均不得自行生成确认或进入受限动作

#### Scenario: reviewer返回结构化审查结果
- **WHEN** QA、`spec_reviewer` 或 `experience_reviewer` 完成审查
- **THEN** reviewer 只向主 Agent返回符合 `ReviewResult` schema 的结构化 payload
- **AND** 只有主 Agent校验 payload、权限边界和输入 freshness 后才能把它保存到 change 根 `handoffs/`

### Requirement: 合同快照保持可审计且不成为第二事实源
重要 change SHALL 在自身 `handoffs/<contractId>/` 中持久化 request、result、review 和 correction JSON 执行快照。合同快照 MUST NOT 建立第二套 change 生命周期：OpenSpec 决定应做什么，Git 决定实际修改，测试决定验证事实，`evidence.md` 决定交付结论。

#### Scenario: 下游阶段读取上游结果
- **WHEN** 主 Agent准备为下游阶段签发合同
- **THEN** 下游只读取已验收合同、合同引用的权威 artifacts、当前真实源码/Git 和测试结果
- **AND** 不得把聊天摘要、上游思考过程、task checkbox 或口头完成声明作为唯一输入

#### Scenario: 权威输入在合同签发后变化
- **WHEN** 任一权威输入的当前 fingerprint 与合同记录不一致
- **THEN** validator 将合同判定为 `STALE`
- **AND** 主 Agent必须重签合同，或基于当前输入明确重新验收后才能进入下一阶段

#### Scenario: 非重要 change 使用最短路径
- **WHEN** 当前任务按现有 Rule 可豁免持久化交付证据
- **THEN** 系统 MAY 不创建 `handoffs/` 快照
- **AND** 仍须报告所选执行模式、真实输入与实际结果，不得伪造合同文件

#### Scenario: PRODUCT_SPEC派工时change尚未创建
- **WHEN** 主 Agent需要委派首个 `PRODUCT_SPEC` 工作包，但目标 change 目录尚不存在
- **THEN** 主 Agent先在当前会话中签发符合 schema 的 bootstrap `TaskContract`，而不是使用自由文本交接
- **AND** product manager 创建 change 后，主 Agent必须立即校验并将 request/result 快照持久化到该 change 的 `handoffs/<contractId>/`

#### Scenario: 合同能力尚未实现时已经完成本能力的规划
- **WHEN** 引入合同能力的治理 change 在 schema 与 validator 可用前已经完成 `PRODUCT_SPEC` 规划
- **THEN** 主 Agent将该规划阶段记录为 pre-capability structured assignment，并把 schema 合同持久化适用性标记为 `NOT_APPLICABLE`
- **AND** 不得追溯生成或伪造 schema-valid request/result；首批真实快照只能来自 schema 与 validator 通过后的后续阶段

### Requirement: 阶段路由和并行执行受合同依赖约束
系统 SHALL 使用角色路由矩阵把任务类型、阶段、适用角色、进入条件、退出条件、可并行关系和执行模式关联起来。前端与后端写入工作仅在合同已冻结、依赖满足且写入范围不冲突时 MAY 并行；QA MUST 在待验收实现稳定后执行；`spec_reviewer` 与 `experience_reviewer` 仅在各自输入完整且只读边界不冲突时 MAY 按适用性并行。

#### Scenario: 前后端工作包可以安全并行
- **WHEN** API、数据和错误合同已冻结，前后端依赖均满足，且两个 `TaskContract` 的允许写入范围不重叠
- **THEN** 主 Agent MAY 并行创建 `frontend_engineer` 与 `backend_engineer` fresh subagent
- **AND** 任一输入或路径边界发生冲突时必须改为串行或重新签发合同

#### Scenario: QA尝试验收仍在变化的实现
- **WHEN** 实现合同尚未返回结果、存在未接收修复或输入 fingerprint 持续变化
- **THEN** 主 Agent不得签发把该实现视为稳定基线的 QA 合同
- **AND** QA 阶段保持等待或由主 Agent重新划定稳定验收范围

#### Scenario: 两个只读 reviewer均适用
- **WHEN** 实现已稳定，Spec 合规审查和真实体验走查的各自前置输入均完整
- **THEN** 主 Agent MAY 并行创建 `spec_reviewer` 与 `experience_reviewer` subagent
- **AND** 两个 reviewer 均不得获得代码、规格、测试或外部系统写权限

#### Scenario: 进入证据与归档控制阶段
- **WHEN** 七个 specialist 阶段已经按适用性完成，准备汇总 evidence 或提出归档建议
- **THEN** `EVIDENCE_AND_ARCHIVE` 只作为主 Agent控制的交付状态，不属于可委派合同 `stage` 枚举
- **AND** 主 Agent不得为该状态伪造 specialist `role`、`TaskContract` 或第八个 custom agent

### Requirement: Review finding通过 correction合同闭环
每个 `ReviewResult` finding SHALL 包含稳定且在当前合同内唯一的 `findingId`、严重级别、状态、证据、责任角色和所需复验。主 Agent MUST 为需要修复的 finding 签发引用原合同和 `findingId` 的 `CorrectionContract`；实现结果本身不得自动关闭 finding，只有适用 reviewer 或 QA 的复核结果才能将其标记为已解决或由真实授权明确豁免。

#### Scenario: 阻断 finding尚未关闭
- **WHEN** `ReviewResult` 含有状态为 `OPEN` 的阻断 finding
- **THEN** 主 Agent拒绝验收原结果并签发最小范围 `CorrectionContract`
- **AND** 合同不得关闭、进入下一阶段或写成有效交付证据

#### Scenario: correction修复后复核通过
- **WHEN** 原执行 subagent 返回引用对应 `findingId` 的修复结果，且适用 reviewer 或 QA 复核通过
- **THEN** review 快照将 finding 标记为 `RESOLVED`
- **AND** 主 Agent MAY 在其他验收条件也满足后验收并关闭合同

#### Scenario: 控制面实现finding需要修复
- **WHEN** QA 或 `spec_reviewer` 针对控制面结果返回 `OPEN` finding
- **THEN** finding 的 `ownerRole` MAY 使用控制面执行者标记 `main_agent`，且主 Agent只能签发保持 `CONTROL_PLANE_IMPLEMENTATION + main_agent` 身份和原精确文件边界的 `CorrectionContract`
- **AND** `main_agent` 不得成为 reviewer，修复结果也不得自行关闭 finding，仍须由原 QA 或 `spec_reviewer` 复核为 `RESOLVED`

### Requirement: 共享工作区拒收语义与物理隔离边界明确
共享工作区中的“未接收脏代码” SHALL 表示主 Agent不得进入下一阶段、勾选对应 task、把结果写成有效 evidence 或关闭合同；该表述 MUST NOT 被解释为文件对其他 Agent物理不可见。只有当前授权、仓库边界和 cleanup 规则均允许时，系统才 MAY 使用 worktree 提供物理隔离。

#### Scenario: subagent返回未通过验收的共享工作区改动
- **WHEN** 执行结果存在失败、阻断 finding、越界文件或未满足验收条件
- **THEN** 主 Agent将结果标记为拒收并停止下游阶段
- **AND** 不得勾选完成、写成有效 evidence 或声称工作区已经物理回滚

#### Scenario: 计划使用worktree隔离
- **WHEN** 主 Agent判断任务需要物理隔离
- **THEN** 必须先满足 worktree、分支、临时路径和 cleanup 所需的用户授权与安全规则
- **AND** 未满足时回退为共享工作区串行执行或报告阻塞，不得绕过权限创建或清理资源

### Requirement: 治理门禁验证可判定结构而不伪装语义理解
项目 SHALL 提供自动化测试和 validator，覆盖角色路由矩阵、四类 JSON Schema、必填字段与枚举、路径边界、输入 freshness、review finding/correction 闭环，以及 Skill、Rule、Agents、README 和 manifest 的引用一致性。机器门禁 MUST 只声明其实际验证的结构、路径、fingerprint 和引用结果，不得声称已经理解自然语言需求、代码质量或用户意图。

#### Scenario: 治理结构和合同均有效
- **WHEN** 运行项目 AI delivery governance 检查
- **THEN** 有效路由、schema、合同夹具、freshness、finding 闭环和引用一致性全部通过
- **AND** 输出明确区分机器可判定结果与仍需 reviewer、主 Agent或用户判断的语义事项

#### Scenario: 路径越界或finding闭环断裂
- **WHEN** 合同允许角色写入其授权根外路径，或 correction 引用不存在、重复或已关闭的 `findingId`
- **THEN** validator 返回失败并指出合同与字段
- **AND** 不得进入执行或把该 finding 标记为解决

#### Scenario: 控制面身份或文件边界不合法
- **WHEN** 合同把 `main_agent` 当作 specialist、把 `CONTROL_PLANE` 用于七个委派阶段、把控制面 stage 用于 `ReviewResult`，或控制面允许写入范围不是 allowlist 内的精确文件
- **THEN** 治理测试与 validator 返回失败
- **AND** 输出明确该分支只证明受限根治理实现边界，不证明业务实现、QA 或 review 已完成

### Requirement: 例外任务使用最短路径或显式受控降级
简单任务、纯文案、紧密依赖前序运行时输出或全局重构 SHALL 根据风险选择最短路径、串行执行或显式受控降级，而不是为形式完整创建全部角色。subagent 能力不可用时，系统 MUST 报告实际执行模式、原因、未运行的角色阶段和证据限制，且 MUST NOT 伪装成多 Agent交付。

#### Scenario: 简单纯文案任务
- **WHEN** 任务没有行为变化且可由一个角色在短时间内独立完成
- **THEN** 主 Agent MAY 选择单角色最短路径并说明持久化合同是否不适用
- **AND** 不要求启动七角色或运行无关验证

#### Scenario: subagent能力不可用
- **WHEN** 当前运行环境无法创建所需 specialist subagent
- **THEN** 主 Agent标记执行模式为 `DEGRADED` 或返回 `BLOCKED`
- **AND** 不得生成虚假的 subagent 身份、合同结果、独立审查或用户确认

## REMOVED Requirements

### Requirement: 单人模式按角色视角串行切换
**Reason**: 已确认的编排模式改为“主 Agent 控制面 + 按阶段或独立工作包创建最少必要 fresh subagent”，原要求允许主 Agent在同一上下文中串行模拟全部职责，不再满足阶段隔离和结构化交接目标。

**Migration**: 使用“单人模式按阶段创建隔离角色执行上下文”及本 delta 中的结构化合同、路由、review/correction 和受控降级要求；现有七个 custom agents 保持不变，不新增 `code_reviewer`。
