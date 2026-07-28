# 角色路由矩阵

主 Agent依据当前事实与下表签发最少必要的 `TaskContract`。矩阵只登记路由，不复制 Agent 或 Rule 正文。

| 任务类型 | stage | role | 进入条件 | 退出条件 | 默认 executionMode | 允许并行对象 | 写入根 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 产品规格 | `PRODUCT_SPEC` | `product_manager` | 需求来源明确或可收口 | artifacts 完整并等待用户确认 | `SUBAGENT` | 无 | `openspec/`、`docs/product/`、`docs/plans/` |
| 交互设计 | `INTERACTION_DESIGN` | `interaction_designer` | 产品规格已确认且存在体验影响 | 状态、流程和验收合同冻结 | `SUBAGENT` | 无 | `docs/designs/`、`docs/plans/`、当前 change |
| 前端实现 | `FRONTEND_IMPLEMENTATION` | `frontend_engineer` | 规格已确认且接口合同冻结 | 前端结果返回并通过实现自检 | `SUBAGENT` | `BACKEND_IMPLEMENTATION` | `frontend/` |
| 后端实现 | `BACKEND_IMPLEMENTATION` | `backend_engineer` | 规格已确认且数据/API合同冻结 | 后端结果返回并通过实现自检 | `SUBAGENT` | `FRONTEND_IMPLEMENTATION` | `backend/` |
| 质量验收 | `QA` | `qa_engineer` | 待验收实现已稳定且输入指纹固定 | 验证结果与 finding 完整返回 | `SUBAGENT` | 无 | 测试、夹具、测试配置和验证脚本 |
| Spec审查 | `SPEC_REVIEW` | `spec_reviewer` | 实现与验证证据完整 | 双向对账与 finding 完整返回 | `SUBAGENT` | `EXPERIENCE_REVIEW` | 只读，不写入 |
| 体验审查 | `EXPERIENCE_REVIEW` | `experience_reviewer` | 存在可运行用户体验 | 真实流程问题与 finding 完整返回 | `SUBAGENT` | `SPEC_REVIEW` | 只读，不写入 |
| 证据与归档控制 | `EVIDENCE_AND_ARCHIVE` | `MAIN_AGENT` | specialist阶段按适用性完成 | evidence复核完成并仅提出获授权动作 | `SINGLE_AGENT_FAST_PATH` | 无；不签发 specialist 合同 | change根证据与审查报告 |

## 主 Agent控制面执行例外

下表不属于specialist路由集合，也不登记第八个custom agent。

| 任务类型 | stage | role | executionMode | 进入 gate | 写入边界 | 必需下游复核 | 禁止职责 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 无specialist归属的根治理实现 | CONTROL_PLANE_IMPLEMENTATION | `main_agent` | `CONTROL_PLANE` | 已确认治理change且`UPDATED_SPEC_CONFIRMATION = SATISFIED` | validator allowlist内逐项列出的精确文件 | 控制面`ResultContract.resultFingerprint`分别交给`QA/qa_engineer`与`SPEC_REVIEW/spec_reviewer` | 业务、产品、交互、前后端、QA、review、`EXPERIENCE_REVIEW`、基础设施和Git写操作 |

## 路由纪律

- 前后端只有在合同冻结、依赖满足且写入根不冲突时并行。
- QA 不得把仍在变化的实现作为稳定输入。
- 同一合同 correction 可以复用原 subagent；新合同必须创建 fresh subagent。
- `EVIDENCE_AND_ARCHIVE` 是主 Agent控制状态，不属于可委派合同 `stage` 枚举，也不新增第八角色。
- 控制面例外不进入上方specialist表；三字段必须联合出现，结果未完成QA与Spec Review前不得验收。
- 简单任务可以使用 `SINGLE_AGENT_FAST_PATH`；能力缺失时标记 `DEGRADED` 或 `BLOCKED`，不得伪造 subagent。
