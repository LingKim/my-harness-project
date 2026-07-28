# 阶段路由

## 0. 合同与执行上下文

主Agent先依据`role-routing.md`选择最少必要specialist，再签发已通过结构校验和freshness检查的`TaskContract`：

- `PRODUCT_SPEC` → `product_manager`
- `INTERACTION_DESIGN` → `interaction_designer`
- `FRONTEND_IMPLEMENTATION` → `frontend_engineer`
- `BACKEND_IMPLEMENTATION` → `backend_engineer`
- `QA` → `qa_engineer`
- `SPEC_REVIEW` → `spec_reviewer`
- `EXPERIENCE_REVIEW` → `experience_reviewer`

`FRONTEND_IMPLEMENTATION`与`BACKEND_IMPLEMENTATION`只有在合同冻结、依赖满足且写入根不冲突时并行。`QA`必须等待待验收实现稳定；`SPEC_REVIEW`和`EXPERIENCE_REVIEW`可在输入完整时并行只读执行。`EVIDENCE_AND_ARCHIVE`只由主Agent控制，不签发specialist合同。

`CONTROL_PLANE_IMPLEMENTATION + main_agent + CONTROL_PLANE`是独立的受限self-hosting分支，不属于上述七个specialist阶段。它只允许已确认治理change中的精确allowlist文件；控制面`ResultContract`返回后，必须让`QA/qa_engineer`和`SPEC_REVIEW/spec_reviewer`的`ReviewResult.resultFingerprint`引用该结果。`EXPERIENCE_REVIEW`不得审查控制面结果，主Agent也不得同时充当QA或Spec Reviewer。

新合同使用fresh subagent；同一合同的finding修复使用`CorrectionContract`复用原执行subagent。结果未被主Agent验收前属于流程拒收状态，不得进入下游、勾选task或写成有效evidence。

## 1. 判断任务路径

| 任务类型 | 必经阶段 | 按需阶段 |
| --- | --- | --- |
| 只读探索 | 需求收口、事实核查 | 不创建 evidence，不进入实现 |
| 纯文案或机械格式化 | 作用域确认、差异验证 | OpenSpec/evidence 可豁免并说明 |
| 单仓库行为修复 | 复现、规格、测试与实现、QA、Spec Review | 无 UI 时 Experience Review 不适用 |
| UI 或交互 change | 规格、交互、前端实现、QA、Spec Review、Experience Review | 后端/数据库按实际影响加入 |
| API、数据库或跨栈功能 | 规格、跨栈契约、依赖顺序实现、QA、Spec Review | 有可运行页面时 Experience Review |
| 安全、AI、架构或治理 | 规格、风险设计、实现、专项验证、Spec Review、evidence | 体验按可观察产品影响判断 |

## 2. 阶段与退出条件

1. **需求收口**：明确目标、非目标、来源、用户价值、边界和验收口径。
2. **OpenSpec 合同**：proposal、specs、design、tasks 完整且当前版本获得用户确认。
3. **交互与跨栈契约**：页面状态、API、数据、权限、错误和测试边界冻结；不适用时记录原因。
4. **实现**：按已验收`TaskContract`和tasks依赖顺序小步推进，能测试的行为先RED再GREEN；specialist返回`ResultContract`payload。
5. **QA**：实现输入稳定后签发`QA`合同；先关闭环境预检的`BLOCKED`/`REVIEW_REQUIRED`，再运行与风险相称的实际命令并返回`ReviewResult`。
6. **Spec Review**：fresh `spec_reviewer`逐条执行Spec→代码与代码→Spec双向对账，finding使用稳定`findingId`。
7. **Experience Review**：对真实可运行流程检查交互、文案、响应式、a11y和视觉；无产品体验变化时明确不适用。
8. **证据与归档建议**：进入`EVIDENCE_AND_ARCHIVE`主Agent控制状态，复核evidence、handoffs、manifest时效、失败和残余风险；Git与归档动作仍需授权。
9. **临时资源清理**：清理动作必须有用户授权和精确目标；执行后用 cleanup manifest 只读复核全部资源终态。

## 3. 跨会话恢复

按顺序读取：

1. `openspec status --change <name> --json` 与 apply instructions；
2. proposal、specs、design、tasks；
3. 根与相关 submodule Git 状态、HEAD、diff；
4. `evidence.md`、verification manifest 和 reviews；
5. 已验收handoff快照及其fingerprint；
6. 当前源码、测试和真实命令输出。

恢复摘要必须把“task 已勾选”和“验证已通过”分开。若 evidence 后输入变化，先检查 freshness，再决定是否沿用结果。

## 4. 硬关卡

- **HK-SPEC**：当前版本规格未经用户确认，停止生产实现。
- **HK-SCOPE**：新增行为缺少需求来源，作为待确认或非目标。
- **HK-QUALITY**：存在未解决 FAIL、阻断偏差或 P0/P1，回到修复/验证。
- **HK-ENV**：外部 `node_modules` 软链接等环境风险为 `BLOCKED` 时停止重型验证；Java 21+/Mockito 为 `REVIEW_REQUIRED` 时先运行最小测试。
- **HK-RUNTIME**：分页等边界行为没有覆盖边界两侧的 fixture，不得把 smoke test 升格为真实场景 PASS。
- **HK-GIT**：未经当轮明确授权，不暂存、提交、推送或更新 gitlink。
- **HK-CLEANUP**：未经授权不删除；清理后 checker 未全部返回 `ABSENT`/`CLOSED` 时不得声称零残留。
- **HK-ARCHIVE**：tasks、规格同步、证据时效和残余风险未满足，不建议归档。
