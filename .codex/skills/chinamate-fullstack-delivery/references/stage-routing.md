# 阶段路由

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
4. **实现**：按 tasks 和依赖顺序小步推进，能测试的行为先 RED 再 GREEN。
5. **QA**：先关闭环境预检的 `BLOCKED`/`REVIEW_REQUIRED`，再运行与风险相称的实际命令；边界行为必须用跨越边界两侧的 fixture，区分 PASS/FAIL/BLOCKED/NOT_RUN。
6. **Spec Review**：逐条执行 Spec → 代码与代码 → Spec 双向对账。
7. **Experience Review**：对真实可运行流程检查交互、文案、响应式、a11y 和视觉；无产品体验变化时明确不适用。
8. **证据与归档建议**：复核 evidence、manifest 时效、失败和残余风险；Git 与归档动作仍需授权。
9. **临时资源清理**：清理动作必须有用户授权和精确目标；执行后用 cleanup manifest 只读复核全部资源终态。

## 3. 跨会话恢复

按顺序读取：

1. `openspec status --change <name> --json` 与 apply instructions；
2. proposal、specs、design、tasks；
3. 根与相关 submodule Git 状态、HEAD、diff；
4. `evidence.md`、verification manifest 和 reviews；
5. 当前源码、测试和真实命令输出。

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
