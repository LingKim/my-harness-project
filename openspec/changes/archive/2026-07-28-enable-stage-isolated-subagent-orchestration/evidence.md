# `enable-stage-isolated-subagent-orchestration` 交付证据

> 本文件只记录实际发生的验证与审查。状态统一使用 `PASS`、`FAIL`、`BLOCKED`、`NOT_RUN`；不根据计划或 task checkbox 推测结果。

## 1. 基本信息

- Change：`enable-stage-isolated-subagent-orchestration`
- 当前结论：`PASS`；两个终审 P1 已修复并由原 `spec_reviewer` 复核为 `RESOLVED`
- 最后更新：`2026-07-28 19:36 +08:00`
- 影响仓库：`root`
- 机器验证清单：未生成；本 change 直接使用治理测试、Harness 与 handoff validator 输出
- 实现或检查范围：根 `.codex/agents/`、`.codex/rules/`、`chinamate-fullstack-delivery` Skill、根治理测试/validator/manifest/Skill lock/入口文档，以及当前 change 的 artifacts、`handoffs/` 与本证据

## 2. 结构化交接事实

- 本 change 的初始产品规划发生在合同能力生效前，属于 pre-capability structured assignment；规划阶段合同持久化为 `NOT_APPLICABLE`，未追溯补造 bootstrap request/result。
- 规格更新由 `PRODUCT_SPEC/product_manager` 合同 `spec-update-control-plane-001` 完成并经用户确认。无现有 specialist 拥有根控制面实现文件，因此剩余治理实现使用已确认的受限 `CONTROL_PLANE_IMPLEMENTATION + main_agent + CONTROL_PLANE` 分支。
- fresh `qa_engineer` 通过 `control-plane-red-tests-001` 建立控制面 RED 夹具；`control-plane-implementation-001` 的真实 Result 随后由 fresh QA 和 fresh Spec Review 复核通过。
- 最终全 change Spec Review 首轮发现 `FINAL-SPEC-ROLE-BOUNDARY-001` 与 `FINAL-SPEC-FINDING-LINK-002` 两个 P1。fresh `qa_engineer` 在 `final-spec-findings-red-001` 中增加 6 个预期 RED 反例；主 Agent使用独立且不扩大历史授权的 `final-spec-findings-fix-001` 控制面合同，只修改 validator 与 Skill lock。
- fresh `qa_engineer` 对修复 Result 返回无 finding 的 `PASS_WITH_ISSUES`；原 `spec_reviewer` 以相同 `reviewRole` 和原 `resultFingerprint` 将两个 P1 复核为 `RESOLVED`，并单独审查新的修复 Result，无新增 finding。
- 当前 `handoffs/` 共 `21` 个 JSON 快照。两个历史 RED request 因测试/validator 随后按授权发生变化而准确返回 `STALE`；它们仅作为历史失败证据保留，不被静默改写为当前 fingerprint，也不构成当前修复失败。

## 3. 自动化验证

| 时间 | 仓库 | 执行角色 | 命令 | 状态 | 关键输出摘要 |
| --- | --- | --- | --- | --- | --- |
| `2026-07-28 19:26` | `root` | `qa_engineer` | `python3 -B scripts/test-handoff-contracts.py` | `PASS` | `22/22` tests passed；两个 P1 的 6 个反例全部转绿 |
| `2026-07-28 19:26` | `root` | `qa_engineer` | `python3 -B scripts/test-ai-delivery-governance.py` | `PASS` | `14/14` tests passed；Skill hash 与 lock 一致 |
| `2026-07-28 19:26` | `root` | `qa_engineer` | `python3 -B scripts/test-custom-agents.py` | `PASS` | `25` 个失败夹具全部生效 |
| `2026-07-28 19:26` | `root` | `qa_engineer` | `python3 -B scripts/validate-custom-agents.py` | `PASS` | 七个 custom agents 结构、引用与权限边界有效 |
| `2026-07-28 19:26` | `root` | `qa_engineer` | `git diff --check` | `PASS` | 无 whitespace 错误 |
| `2026-07-28 19:26` | `root` | `qa_engineer` | 当前修复链合同审计（validator 输出分类） | `PASS` | 当前修复链无结构、关联、范围或 freshness 失败；全量 CLI 另以退出码 `2` 准确报告两个已被后续工作包取代的历史 RED request 为 `STALE` |
| `2026-07-28 18:55` | `root` | `main_agent` | `./scripts/check-agent-governance.sh` | `PASS` | custom agents、合同、治理、collector 与 safety 测试通过 |
| `2026-07-28 18:55` | `root` | `main_agent` | `./scripts/check-harness.sh` | `PASS` | Harness、submodule 与集中治理结构完整 |
| `2026-07-28 18:55` | `root` | `main_agent` | `openspec validate enable-stage-isolated-subagent-orchestration --strict` | `PASS` | Change valid |
| `2026-07-28 18:55` | `root` | `main_agent` | `openspec validate --all --strict` | `PASS` | `14 passed, 0 failed` |

## 4. 手工与审查结果

| 场景 | 期望 | 实际 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| 七角色边界 | 仍恰好七个 custom agents | 七角色保持不变，`main_agent` 未登记为第八角色 | `PASS` | `.codex/manifest.json`、`references/role-routing.md` |
| 非口头交接 | 下游只消费结构化合同 | 产品更新、两轮 RED、两份控制面 Result、fresh QA、Spec Review 与 finding 复核均已落盘 | `PASS` | `handoffs/` |
| specialist 结果范围 | modifiedFiles 同时受 request allowlist、forbidden paths 和角色根约束 | 三个独立反例由 RED 转为 GREEN，生产 validator 已实现三重检查 | `PASS` | `final-spec-findings-fix-001`、`scripts/test-handoff-contracts.py` |
| finding 绑定 | correction 只能引用所指 ReviewResult 的 OPEN finding，RESOLVED 保持原 role/result | 三个独立反例由 RED 转为 GREEN；两个原 P1 由相同 `spec_reviewer + resultFingerprint` 复核关闭 | `PASS` | `final-spec-review-resolved.json` |
| 应用仓库隔离 | frontend/backend 不被治理 change 修改 | 两个 submodule 均为 clean `main...origin/main` | `PASS` | 最终 Git 状态输出 |

## 5. QA 结论

- 是否执行：是，fresh `qa_engineer`
- 验收范围：最终修复 ResultContract、两个 P1、6 个失败夹具、合同 schema/validator、治理引用、Skill hash 与七角色结构
- 通过项：合同测试 `22/22`、治理测试 `14/14`、custom-agent 失败夹具 `25` 个、七角色结构校验与 diff 检查
- 失败项：无
- 已知缺陷：无未解决的 OPEN finding；两个历史 RED request 按设计保持 `STALE`
- 残余风险：机器门禁不能替代自然语言语义审查；历史快照不得被当作当前输入继续使用

## 6. Spec 合规审查

- 是否执行：是，控制面局部审查和最终全 change 双向审查均已完成
- 完整报告：首轮 OPEN 结果见 `handoffs/final-spec-review-001/reviews/final-spec-review-open.json`，关闭结果见同目录 `final-spec-review-resolved.json`，新修复 Result 审查见 `handoffs/final-spec-findings-fix-001/reviews/final-fix-spec-review-001.json`
- 正向覆盖率：首轮完整覆盖 `50/61`，11 项部分覆盖由两个 P1 解释；修复后两个 P1 对应生产逻辑、6 个夹具与 Skill lock 均复核通过
- 反向超纲项：未发现业务超纲；新增改动仅位于已确认根治理、OpenSpec、测试与文档范围
- 阻断问题：两个 P1 均为 `RESOLVED`，无 OPEN P0/P1
- 当前结论：`PASS`

## 7. 体验走查

- 是否执行：不适用
- 原因：本 change 仅调整 AI Coding 治理、合同与文档，不改变可运行页面、交互流程、文案、响应式或可访问性体验

## 8. 未验证项与残余风险

| 项目 | 状态 | 原因 | 影响 | 后续处理 |
| --- | --- | --- | --- | --- |
| 历史 RED request freshness | `NOT_RUN` | 后续授权工作包有意改变其测试或 validator 输入，历史快照因此为 `STALE` | 不影响当前 GREEN 修复；不得复用为当前输入 | 保留历史 fingerprint，由当前 QA/Spec Review 新合同承接结论 |
| 前端/后端业务测试与 build | `NOT_RUN` | 两个 submodule 无业务修改 | 不影响本治理 change 结论 | 不运行无关 build |
| Git commit/push | `NOT_RUN` | 用户未授权 | 改动仅在本地工作区 | 如需提交由用户另行授权 |
| OpenSpec sync/归档 | `NOT_RUN` | 用户未授权 | change 保持 active | 最终门禁后只提出建议，不自动执行 |

## 9. 最终交付结论

- tasks 是否全部完成：是，`18/18`
- 前端验证：不适用
- 后端验证：不适用
- Harness：`PASS`
- OpenSpec strict validate：`PASS`
- Spec Review：`PASS`；两个 P1 已由原 `spec_reviewer` 复核为 `RESOLVED`
- Experience Review：不适用
- 是否建议归档：最终门禁通过后可建议 sync/归档，但本轮不自动执行
- 结论依据：真实自动化输出、fresh QA、原 `spec_reviewer` 的结构化关闭回执、当前 Git/submodule 状态与 OpenSpec strict validate；未把 task checkbox 或聊天声明当作验证证据。

## 记录边界

- 未保存完整终端日志、凭据、token、Cookie、缓存或隐私数据。
- 未执行 commit、push、gitlink 更新、sync 或 archive。
