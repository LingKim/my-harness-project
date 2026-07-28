## Context

当前 `chinamate-fullstack-delivery` 以主 Agent统一协调、串行切换七个职责视角为默认模式。OpenSpec、Git、测试与 `evidence.md` 已经提供需求、修改、验证和交付结论的事实源，七个 custom agents 也已经按交付物划分权限；缺口是角色上下文没有成为默认隔离执行单元，交接没有机器可校验的稳定格式，review 退回也缺少 finding 到修复再复核的结构化闭环。

本设计吸收参考 `subagent-driven-development` 的 fresh subagent 和分阶段 review 思路，但不采用其自由文本派发模板，也不引入当前不存在的 `code_reviewer`。ChinaMate 继续使用现有七角色，并让 QA、`spec_reviewer`、`experience_reviewer` 按现有职责覆盖自动化验证、Spec/技术基线审查和真实体验审查。

约束如下：

- 产品规格当前仍需用户确认后才能进入 apply；合同不能生成或替代用户确认。
- 主 Agent、subagent 共用同一工作区时，默认只有流程隔离，没有文件系统隔离。
- 本 change 只调整 AI Coding 治理，不修改前后端业务代码或运行时架构。
- 合同必须复用现有事实源，不形成另一套 OpenSpec 状态机。

## Goals / Non-Goals

**Goals:**

- 把主 Agent收口为控制面，并让适用 specialist 以阶段或独立工作包为单位在 fresh context 中执行。
- 用版本化 JSON 合同表达权威输入、权限边界、验收、验证、结果和 review/correction 闭环。
- 让输入变化、路径越权、finding 未关闭和引用漂移能够被自动化门禁阻断。
- 在不启动全部七角色的前提下，明确串行、并行、复用、最短路径和受控降级规则。

**Non-Goals:**

- 不新增 `code_reviewer` 或第八角色，不改变七个 TOML 角色的业务职责边界。
- 不创建外部调度服务、消息队列、数据库、常驻 Agent 池或第二套 change 生命周期。
- 不自动执行 Git 写操作、worktree 创建/清理、归档或任何需要用户授权的动作。
- 不让脚本判断自然语言需求是否正确、代码质量是否充分或用户是否真实同意。

## Decisions

### 1. 主 Agent作为唯一控制面，specialist 作为执行面

主 Agent默认只负责：从 OpenSpec/Git/测试/evidence 恢复阶段；选择最少必要角色；签发和验收合同；执行用户确认、Git、质量和归档硬关卡；汇总交付证据。非平凡阶段存在适用 custom agent 时，主 Agent必须创建 specialist subagent，不得在同一上下文中静默扮演该角色完成工作。唯一实现例外是本设计第 1A 节严格限定的根控制面自举治理实现；该例外不是 specialist 替代路径。

主 Agent同时是 change 根 `handoffs/` 的唯一持久化写入者。所有 specialist（包括 `frontend_engineer`、`backend_engineer`、QA 和只读 reviewer）只返回符合 schema 的结构化 payload；主 Agent校验 payload、输入 freshness、角色写入边界与 gate 后再保存 request/result/review/correction。该保存职责不会扩大 subagent 的 TOML 写入权限，尤其不会让只读 reviewer 获得落盘权限。

首个 `PRODUCT_SPEC` 派工存在 bootstrap 次序：目标 change 尚未创建时，主 Agent先在会话中构造并签发完整 JSON `TaskContract`，以预定 change name、bootstrap 权威输入和受限写入范围派给 `product_manager`；product manager 创建 change 后返回结构化 payload，主 Agent立即在新 change 的 `handoffs/<contractId>/` 持久化 request/result。bootstrap 只延迟落盘，不放宽 schema，也不得退化为自由文本交接或口头授权。

上述 bootstrap 规则从 schema 与 validator 实现并通过后生效。本能力自身的 `PRODUCT_SPEC` 工作发生在该能力可用之前，因此只能记录为 pre-capability structured assignment，合同持久化适用性为 `NOT_APPLICABLE`；不得根据聊天或事后 artifacts 追溯伪造 schema-valid request/result。本 change 的首批真实合同快照从 schema/validator 通过后的实现、QA 和 review 阶段开始。

选择这一模式是因为权限、责任和复核边界都能落到现有七角色合同；若继续由主 Agent串行模拟，fresh context 与独立结果无法证明。备选的“七角色全部常驻”会增加成本并制造无关交接，因此不采用。

### 1A. 无 specialist 归属的根控制面实现使用判别式合同分支

七个现有 specialist 分别拥有产品规格、交互、前端、后端、QA 和两类只读审查，但没有角色拥有根 `.codex` 控制面、编排 Skill 与治理 validator 的实现。若强行把这类实现归给任一现有角色会伪造职责；若不产生实现 `ResultContract`，后续 `ReviewResult.resultFingerprint` 又没有真实目标。因此在不新增 custom agent 的前提下，`TaskContract`、`ResultContract` 和适用的 `CorrectionContract` 增加一个互斥的控制面分支：

| 字段 | 控制面固定值 | 边界 |
| --- | --- | --- |
| `stage` | `CONTROL_PLANE_IMPLEMENTATION` | 不是七个可委派 stage，也不进入 specialist 路由集合 |
| `role` | `main_agent` | 仅为 schema 中的控制面执行者标记，不登记为 custom agent |
| `executionMode` | `CONTROL_PLANE` | 仅允许出现在控制面 `TaskContract`；不得与 `SUBAGENT`、fast path 或 specialist 身份混用 |

控制面 request 只有在以下条件全部满足时有效：当前 change 属于治理行为且更新后的规格确认 gate 为 `SATISFIED` 并有真实用户证据；task ID 在当前 `tasks.md` 中存在；不存在拥有目标文件的现有 specialist；`allowedWritePaths` 逐项列出精确文件而不是目录根；每个文件都位于 validator 固定登记的控制面 allowlist。首版 allowlist 只覆盖本 change 已声明的根治理表面：`.codex/agents/` 中的角色定义与索引、`.codex/rules/` 中的治理入口、`.codex/skills/chinamate-fullstack-delivery/`、`.codex/manifest.json`、`.codex/skills-lock.json`、本 change 列明的治理检查/validator/测试脚本、根 `AGENTS.md`、根 `README.md` 与明确列入 tasks 的治理导航文件。控制面合同不得用 `.codex/`、`scripts/`、`docs/` 或项目根作为宽泛授权；`frontend/`、`backend/`、`openspec/`、业务文档、运行时基础设施、应用测试和 Git 写操作不在 allowlist。主 Agent写入 `handoffs/` 是其既有持久化职责，不计入控制面实现的 `allowedWritePaths`。

Schema 与 validator 对该分支执行联合判定，而不是把 `CONTROL_PLANE_IMPLEMENTATION`、`main_agent` 或 `CONTROL_PLANE` 分别加入可自由组合的公共枚举：三个标记必须成组出现；specialist request/result 仍只能使用七个既有 stage/role 映射；控制面 result 必须通过 `requestFingerprint` 关联同目录 request，并与其 `change`、`taskIds`、`stage`、`role` 完全一致；`modifiedFiles` 必须是 request 精确允许文件的子集。控制面 correction 还必须引用针对该控制面结果的 QA 或 Spec Review finding，并保持原控制面身份与不扩大的精确文件范围。

QA 与 Spec Review 不使用控制面身份。主 Agent在受限控制面 result 返回并通过 freshness 检查后，分别向现有 `qa_engineer` 和 `spec_reviewer` 签发 specialist 合同；其 `ReviewResult` 继续使用 `QA/qa_engineer` 或 `SPEC_REVIEW/spec_reviewer`，但 `resultFingerprint` 可以且必须指向受验收的控制面 `ResultContract`。针对该结果的 finding 可用 `ownerRole = main_agent` 表示修复责任，但只有当被引用 result 是合法控制面结果时才允许；`EXPERIENCE_REVIEW` 不得把控制面 result 作为审查目标。原 QA 或 Spec Reviewer 负责把修复后的 finding 复核为 `RESOLVED`，主 Agent不能同时充当实现者与 reviewer。

本例外不得用于已完成工作的追溯包装。更新后的规格经用户确认后，主 Agent应先签发控制面 request，再执行为本分支补齐 schema、validator、治理测试与文档接入的真实剩余工作并返回 result；QA 与 Spec Review随后引用该 result。这样既形成真实 Result→Review 链，又不伪造本 change 已完成的 `PRODUCT_SPEC` 或合同签发前的实现历史。

备选的“把控制面实现伪装成 backend/frontend/product 任务”违反角色边界；新增第八 custom agent 超出本 change；新增第五类独立合同会复制 Task/Result/Correction 的公共约束。采用现有三类合同中的判别式分支，改动最小且能让 validator 机器判定。

### 2. fresh/reuse以独立工作包和合同关闭为边界

- 新 `contractId` 对应新的独立工作包和 fresh subagent。
- 同一合同被 QA/reviewer 退回时，主 Agent可把 `CorrectionContract` 发回原执行 subagent；这是带新权威输入的修复轮次，不是新工作包。
- 原合同关闭后产生的新阶段、新 task 集或范围扩张必须使用新 `contractId` 和 fresh subagent。
- reviewer 本身按适用阶段创建；只读 reviewer 不因需要保存报告而获得写权限。

这一边界保留了修复者对本工作包的必要上下文，也避免把旧上下文跨合同继承为隐形事实源。备选的“每次 correction 都 fresh”会丢失局部实现上下文；“同一角色永久复用”则会造成跨任务污染，均不采用。

### 3. 四类 JSON 合同共享版本、身份和可追溯字段

合同采用 JSON Schema Draft 2020-12，首版 `schemaVersion` 为 `1.0`，fingerprint 格式为 `sha256:<64 lowercase hex>`。所有路径均为项目根相对、规范化且不含 `..` 的路径或路径前缀；validator 在解析符号链接后检查其未逃逸授权根。

四类合同使用以下最小模型：

| 合同 | 签发/产生者 | 核心字段 |
| --- | --- | --- |
| `TaskContract` | 主 Agent签发 | `schemaVersion`、`contractId`、`change`、`stage`、`role`、`taskIds`、`executionMode`、`authoritativeInputs[{path,fingerprint}]`、`dependencies`、`allowedWritePaths`、`forbiddenWritePaths`、`expectedOutputs`、`acceptanceCriteria`、`verificationPlan`、`userGates`、`gitGates`、`status` |
| `ResultContract` | 执行 subagent 产生，主 Agent验收 | 公共身份字段、`requestFingerprint`、`status`、`modifiedFiles`、`outputReferences`、`verificationSummary`、`deviations`、`blockers`、`notRun`、`residualRisks`、`recommendations`、`acceptance` |
| `ReviewResult` | QA 或只读 reviewer 产生，主 Agent验收 | 公共身份字段、`resultFingerprint`、`reviewRole`、`status`、`findings[{findingId,severity,status,evidenceRefs,ownerRole,requiredVerification}]`、验证摘要、阻塞、未运行项与残余风险、`acceptance` |
| `CorrectionContract` | 主 Agent签发 | 公共身份字段、`parentContractId`、`reviewFingerprint`、`findingIds`、更新后的权威输入、写入边界、预期修复、验收条件、复验计划、用户/Git gates、`status` |

稳定枚举至少包括：

- 可委派合同 `stage`：`PRODUCT_SPEC`、`INTERACTION_DESIGN`、`FRONTEND_IMPLEMENTATION`、`BACKEND_IMPLEMENTATION`、`QA`、`SPEC_REVIEW`、`EXPERIENCE_REVIEW`，分别映射现有七个 specialist。
- `role`：现有七个 custom agent 名称；主 Agent不是第八个 specialist role。
- 受限控制面合同身份：仅 Task/Result/Correction 可使用第 1A 节的 `CONTROL_PLANE_IMPLEMENTATION + main_agent` 分支；`TaskContract.executionMode` 固定为 `CONTROL_PLANE`。这些标记不加入可委派 stage/role 集合，`ReviewResult` 不接受该身份。
- specialist `executionMode`：`SUBAGENT`、`SINGLE_AGENT_FAST_PATH`、`DEGRADED`；控制面分支只能使用 `CONTROL_PLANE`。
- 执行/审查结果：`PASS`、`PASS_WITH_ISSUES`、`FAIL`、`BLOCKED`、`NOT_RUN`。
- 合同状态：`DRAFT`、`ISSUED`、`IN_PROGRESS`、`RETURNED`、`ACCEPTED`、`STALE`、`CLOSED`。
- gate：`PENDING`、`SATISFIED`、`NOT_APPLICABLE`；finding：`OPEN`、`RESOLVED`、`WAIVED`，严重级别为 `P0` 至 `P3`。

`acceptance` 初始只能是 `PENDING`；只有主 Agent可改为 `ACCEPTED`、`REJECTED` 或 `STALE`，并记录依据引用。subagent 的“建议下一角色”只能进入 `recommendations`，不能改变合同或生成新合同。控制面 result 也先以 `PENDING` 返回，再由主 Agent按相同 freshness、验证和 gate 规则验收；执行者与验收控制者同为主 Agent不免除独立 QA 和 Spec Review。

`taskIds` 必须为非空数组。新 change 的 bootstrap `PRODUCT_SPEC` 发生在 `tasks.md` 创建前，必须使用稳定保留 ID `BOOTSTRAP-PRODUCT-SPEC`，并在对应 `ResultContract` 中保持相同值；不得使用空数组或虚构数字 task ID。`EVIDENCE_AND_ARCHIVE` 继续作为主 Agent控制的交付状态保留在阶段路由中，但不属于合同 `stage` 枚举，也不签发 specialist 合同。

备选的 Markdown/自由文本模板不能可靠校验枚举、路径、fingerprint 和 finding 引用，因此不采用。备选的单一巨大 schema 会弱化各合同的 required 字段，采用一个公共 definitions schema 加四个类型 schema。

### 4. handoffs是执行快照，freshness连接既有事实源

重要 change 使用以下布局：

```text
openspec/changes/<change>/handoffs/<contractId>/
├── request.json
├── result.json
├── reviews/
│   └── <review-id>.json
└── corrections/
    └── <correction-id>.json
```

request/result/review/correction 只保存签发或回执时的执行快照。权威输入 fingerprint 由文件内容计算；当文件、Git diff 基线、测试 manifest 或被引用合同变化时，validator 返回 `STALE`。主 Agent随后只能重签，或在读取当前事实后显式重新验收并更新 fingerprint；不得静默沿用旧结果。

目录中的全部 JSON 均由主 Agent在校验 subagent payload 后写入；subagent 无论其应用代码写入权限如何，都不得直接写 change 根 `handoffs/`。对于未来新 change 的 bootstrap `PRODUCT_SPEC` 合同，主 Agent在 change 创建前保留会话内 JSON，并使用 `BOOTSTRAP-PRODUCT-SPEC`，change 创建后立即按相同布局持久化并重新计算可用权威输入的 fingerprint。

本 change 是合同能力的迁移边界：其规划阶段只在 `evidence.md` 中记录 pre-capability structured assignment 与合同持久化 `NOT_APPLICABLE`，不创建追溯 request/result。schema 与 validator 验证通过后，后续实现、QA 和 review 合同才按真实签发时间保存首批快照。

事实优先级保持为：OpenSpec 决定应做什么；Git diff/HEAD 决定实际修改；测试与 verification manifest 决定执行事实；`evidence.md` 汇总交付结论。`handoffs/` 只回答“谁在什么输入和边界下返回了什么”，不决定 change 是否完成或可归档。

备选的中央合同数据库或根级队列会引入外部状态与恢复复杂度，且违反轻量治理目标，因此不采用。

### 5. 角色路由矩阵决定阶段、依赖与并行边界

在 `references/role-routing.md` 维护可校验矩阵，字段至少包含任务类型、阶段、角色、进入条件、退出条件、默认执行模式、允许并行对象和写入根。矩阵只登记路由，不复制 Agent/Rule 正文；其中七个可委派合同阶段映射七个 specialist，`EVIDENCE_AND_ARCHIVE` 单独登记为主 Agent控制状态且不产生 specialist 合同。

`CONTROL_PLANE_IMPLEMENTATION` 不加入上述 specialist 路由表；它在独立的“主 Agent控制面执行例外”表中仅登记第 1A 节的固定身份、进入 gate、精确文件规则和禁止职责。治理测试必须继续断言 specialist 数量恰为七，同时单独断言控制面分支不会与七阶段、QA/reviewer 或 `EVIDENCE_AND_ARCHIVE` 混用。

- 产品规格必须先完成并获得用户确认。
- 前后端仅在 API/数据/错误合同冻结、各自依赖满足、写入范围不重叠时并行；否则串行。
- QA 基于稳定的实现 result 执行，不能与仍在修改的同一范围并行。
- `spec_reviewer` 与 `experience_reviewer` 在输入完整且各自适用时可并行，因为二者只读。
- `experience_reviewer` 仅在存在可运行用户体验时适用；非 UI change 明确跳过原因。

备选的任意 DAG 调度器超出当前规模；当前矩阵与主 Agent判断足以表达所需依赖。

### 6. 现有七角色承担分阶段 review，不增加code_reviewer

实现者先按自身角色合同自检；QA 独立运行规格场景、回归和适用工程实践验证；`spec_reviewer` 只读进行 Spec→代码、代码→Spec 和代码→Rules/技术基线对账；有 UI 时 `experience_reviewer` 检查真实体验。主 Agent根据适用性验收这些 `ReviewResult`。

每个 finding 使用合同内唯一 `findingId`。`OPEN` 的阻断 finding 触发 `CorrectionContract`；修复 `ResultContract` 不能自行关闭 finding，必须由原 reviewer/QA 或适用的复核合同标记 `RESOLVED`。`WAIVED` 必须引用真实用户授权或已确认设计依据。

参考方案依赖不存在的 `code-reviewer`，直接照搬会形成无法路由的角色，因此本 change 不采用；若未来确有第八角色需求，必须另建 OpenSpec change。

### 7. 共享工作区采用流程拒收，worktree只作受控增强

“主上下文不接收脏代码”定义为：主 Agent不验收结果、不勾选 task、不进入下一阶段、不把结果写成有效 evidence，也不关闭合同。它不承诺共享工作区中的文件不可见或已经回滚。发现越界修改时主 Agent报告精确路径并停止，不自动删除或回滚用户/其他 Agent改动。

只有用户授权、repository boundary、分支安全、环境预检和 cleanup manifest 均满足时才使用 worktree。否则选择共享工作区串行执行或报告阻塞。这样避免把流程口号误写成物理隔离保证。

### 8. validator只校验结构事实并通过失败夹具证明边界

新增四类 schema、统一 validator 和失败夹具，并接入现有 `scripts/test-ai-delivery-governance.py`、`scripts/check-agent-governance.sh`。验证范围包括：

- 七角色路由矩阵角色名、阶段、进入/退出条件和路径根完整；
- schema 必填字段、枚举、`additionalProperties` 策略和交叉引用；
- 项目根相对路径、角色写入边界、禁止路径和 traversal/symlink escape；
- 控制面 stage/role/executionMode 联合判别、精确文件 allowlist、request/result 身份一致及 modifiedFiles 子集；
- 权威输入与 result/review fingerprint freshness；
- `findingId` 唯一性、控制面 result 到 QA/Spec Review fingerprint、correction 引用存在性和复核关闭条件；
- Skill、Rule、Agent README/TOML、根 README、manifest、lock 和脚本 required files 引用一致性。

validator 优先使用 Python 标准库实现本项目实际需要的 JSON Schema 关键字与可判定交叉检查，不新增 `jsonschema`、npm package 或其他未经批准的运行时依赖。若未来需要完整通用 JSON Schema 引擎，必须另行评估依赖与供应链风险并获得确认，不能在本 change 中静默安装。

机器门禁不判断“需求是否合理”“实现质量是否充分”“用户是否真的同意”。这些仍由 reviewer、主 Agent和用户负责，并在输出中明确为未自动验证的语义事项。

### 9. 例外路径必须显式记录执行模式

简单任务、纯文案可用 `SINGLE_AGENT_FAST_PATH`；严重依赖前序运行时输出或全局重构默认串行并缩小合同，不强行并发。subagent 能力不可用时使用 `DEGRADED` 或 `BLOCKED`，列出原因、未运行角色/阶段和证据限制；不得伪造 subagent 身份或独立 review。

这保留了现有“最短安全路径”优势，同时让降级不再隐形。备选的“一律阻塞所有简单任务”会产生不成比例的流程成本，因此不采用。

## Risks / Trade-offs

- [合同字段和快照增加维护成本] → 只对重要 change 持久化，简单任务走显式 fast path；公共 definitions 减少重复。
- [共享工作区并发导致竞态或覆盖] → 仅在依赖满足且写入根不冲突时并行；冲突后串行化并重签 stale 合同。
- [fingerprint 过于敏感导致频繁 STALE] → 只登记任务权威输入，不对整个仓库做全量哈希；重新验收必须说明影响范围。
- [schema通过被误当作语义正确] → 测试输出明确机器验证边界，保留 QA/reviewer/用户门禁。
- [review finding永久悬挂] → 每个 finding 必须有责任角色和 required verification；阻断 finding 未关闭时合同不能验收。
- [Agent平台能力差异] → 明确 `DEGRADED`/`BLOCKED`，不得用主 Agent模拟结果掩盖能力缺失。
- [控制面例外被滥用为通用主 Agent实现权] → 三字段固定组合、精确文件 allowlist、真实规格确认 gate、Result→QA/Spec Review fingerprint 和失败夹具共同阻断扩权。

## Migration Plan

1. 先增加治理失败夹具与 schema/validator，使缺字段、越权、stale 和 finding 断链可复现。
2. 增加合同与角色路由参考，更新 Skill、阶段路由、workflow Rule、Agents 索引/合同及 README/manifest/lock 引用。
3. 在用户确认本次规格更新后，先签发受限控制面 request，再实现对应 schema/validator/测试与治理入口增量，并生成真实控制面 result；随后由 QA 与 Spec Review 以该 result fingerprint 为输入完成独立复核。
4. 用最小有效合同和每类失败 fixture 运行治理测试，再运行 `check-agent-governance.sh`、Harness 与 OpenSpec strict validate。
5. 将本 change 的规划阶段记录为 pre-capability structured assignment/合同持久化 `NOT_APPLICABLE`；控制面分支通过后，从真实控制面实现、QA 和审查阶段生成首批 `handoffs/` 快照，不追溯包装合同签发前的实现。

回滚时恢复旧 Skill/Rule/Agents/README/manifest/lock 与治理脚本，并删除本 change 新增的 schema、validator、路由参考和测试；不涉及业务数据、API 或数据库迁移。已经保存的 `handoffs/` 作为历史审计快照保留或随对应未交付 change 一并回退，不据此改变 OpenSpec/evidence 结论。

## Open Questions

无阻断性的技术未决问题。当前 artifacts 完成后仍需用户明确确认本版规格，才能进入 apply；该确认状态不得由合同或 Agent自行生成。
