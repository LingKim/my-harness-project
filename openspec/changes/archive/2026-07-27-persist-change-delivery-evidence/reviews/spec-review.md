# `persist-change-delivery-evidence` Spec 合规审查报告

## 一、正向对账表（Spec → 代码）

| # | Spec 来源 | 要求摘要 | 状态 | 代码位置 / 说明 |
| --- | --- | --- | --- | --- |
| P1 | `proposal.md:7` | 适用 change 增加根级 `evidence.md`，覆盖实现范围、验证、QA、审查、风险和归档建议 | ✅ | `openspec/changes/persist-change-delivery-evidence/evidence.md` |
| P2 | `proposal.md:8` | 提供中文 Markdown 模板，由主 Agent 汇总真实结果 | ✅ | `docs/templates/openspec-change-evidence.md`；`.codex/agents/README.md` |
| P3 | `proposal.md:8` | 不引入 JSON 状态机、哈希、数据库、自动日志采集或 CI 强制 | ✅ | 冻结 diff 未发现上述实现 |
| P4 | `proposal.md:9` | 明确强制适用范围和纯文案、机械格式化、只读探索豁免 | ✅ | `.codex/rules/workflow.md`；`README.md` |
| P5 | `proposal.md:10` | Spec/Experience Reviewer 保持只读，报告由主 Agent 按需保存 | ✅ | `.codex/agents/spec_reviewer.toml`；`.codex/agents/experience_reviewer.toml` |
| P6 | `proposal.md:11` | 禁止原始日志、凭据、Cookie、隐私数据、缓存和推测结果进入证据 | ✅ | `.codex/rules/documentation.md`；证据模板 |
| P7 | `proposal.md:12` | 归档前检查失败、阻塞、未运行和残余风险 | ✅ | `.codex/rules/workflow.md`；`AGENTS.md` |
| P8 | `proposal.md:16` | 不自动判断证据是否过期 | ✅ | 仅实现人工失效规则 |
| P9 | `proposal.md:16` | 不绑定 Git SHA 或规格指纹 | ✅ | 模板和脚本均无相关字段或计算逻辑 |
| P10 | `proposal.md:16` | 不保存完整终端日志 | ✅ | `.codex/rules/documentation.md` |
| P11 | `proposal.md:16` | 不强制纯文档小改创建证据 | ✅ | `.codex/rules/workflow.md` |
| P12 | `proposal.md:16` | 不修改业务功能、API、schema 或应用依赖 | ✅ | frontend/backend 工作区 clean；根 diff 无应用实现改动 |
| P13 | `proposal.md:18` | 模板可生成可读 `evidence.md` | ✅ | 模板八部分完整，试运行文件已创建 |
| P14 | `proposal.md:18` | 明确区分四种验证状态 | ✅ | 模板和试运行证据均使用规定状态 |
| P15 | `proposal.md:18` | QA、Spec Review、Experience Review 的责任和落盘方式清晰 | ✅ | 三个角色合同及 Agent 索引 |
| P16 | `proposal.md:14,18` | 证据随 change 归档长期保留 | ✅ | 文件位于 change 根目录，未引入临时存储或归档排除逻辑 |
| D1 | `design.md:28-34` | 每个适用 change 使用一份根级 `evidence.md` | ✅ | 当前 change 已按此创建 |
| D2 | `design.md:32` | 模板固定八部分，自动化表包含六个最小字段 | ✅ | `docs/templates/openspec-change-evidence.md` |
| D3 | `design.md:36-40` | 长报告和截图按需拆分，不预建空目录 | ✅ | 当前未预建 `assets/` 空目录，`reviews/` 只在实际报告产生后创建 |
| D4 | `design.md:42-46` | 主 Agent 汇总，只读 Reviewer 不获得写权限 | ✅ | Reviewer TOML 均为 `read-only` |
| D5 | `design.md:48-52` | 保存完整命令和最小摘要，不保存完整日志 | ✅ | Rules、模板及试运行证据一致 |
| D6 | `design.md:52` | 外部证据允许稳定 URL，敏感内容须脱敏或放弃保存 | ✅ | 证据字段可承载链接，安全边界已进入模板和 Rule |
| D7 | `design.md:54-58` | 人工标记失效并重跑或记录不重跑依据 | ✅ | workflow Rule 与模板记录边界 |
| D8 | `design.md:54-58` | 不实现哈希或自动时效判断 | ✅ | 冻结 diff 无相关实现 |
| D9 | `design.md:60-64` | 唯一模板、长期 Rules、角色特有合同分层维护 | ✅ | 模板、三份 Rules、三个 Agent TOML 分工符合设计 |
| D10 | `design.md:64` | Harness 仅检查模板、路由和角色合同 | ✅ | governance script 与 agent validator |
| D11 | `design.md:77-79` | 先取得 RED，再补齐模板和治理合同 | ✅ | `evidence.md` 如实记录命令、角色、仓库、失败摘要及时间精度限制 |
| D12 | `design.md:80` | 运行治理、Harness、Shell 语法、strict validate 和 diff check | ✅ | `evidence.md` 记录 09:52 最终验证全部通过 |
| D13 | `design.md:81` | 本 change 创建首份完整试运行证据 | ⚠️ | 审查时证据和最终验证已完整，本报告当时尚待主 Agent 保存和回填 |
| D14 | `design.md:82` | 不为历史 change 补写或推测证据 | ✅ | 冻结 diff 未发现历史 change 证据补写 |
| D15 | `design.md:19-24` | 不改 OpenSpec schema、CI、业务源码、测试逻辑和应用依赖 | ✅ | 根治理范围符合，两个 submodule clean |
| T1 | `tasks.md:3` | 扩展角色合同校验器及三个失败夹具 | ✅ | validator 与 test fixtures 已实现并通过 |
| T2 | `tasks.md:4` | 检查模板和根路由，并取得预期 RED | ✅ | governance script 与 RED 证据 |
| T3 | `tasks.md:8` | 创建八部分模板并提供四种状态示例 | ✅ | 证据模板 |
| T4 | `tasks.md:9` | 更新三份 Rules | ✅ | workflow、quality-gates、documentation |
| T5 | `tasks.md:10` | 更新根入口、Agent 索引和三个角色合同 | ✅ | 对应文件均已更新 |
| T6 | `tasks.md:11` | 更新 README 和计划索引的最小导航 | ✅ | `README.md`；`docs/plans/README.md` |
| T7 | `tasks.md:15` | 运行三个治理/Harness 验证 | ✅ | `evidence.md` 中的命令和结果摘要 |
| T8 | `tasks.md:16` | 创建首份真实 `evidence.md` | ✅ | RED、GREEN、最终验证、未运行项和风险均有结构化记录 |
| T9 | `tasks.md:17` | 完成只读 Spec Review、保存报告并更新 evidence；Experience Review 标记不适用 | ⚠️ | 审查时 Experience Review 已正确标记不适用，本报告已完成但尚待主 Agent 保存和回填 |
| T10 | `tasks.md:18` | 执行最终验证并复核范围 | ✅ | task 已勾选，`evidence.md` 记录全部命令通过 |
| S1 | `spec.md:5` | 适用 change 在根目录维护 `evidence.md` | ✅ | 当前治理 change 已存在 |
| S2 | `spec.md:5` | `evidence.md` 归档后继续保留 | ✅ | 文件位于标准 change 目录，归档时随目录保留 |
| S3 | `spec.md:5,13-17` | 豁免 change 说明适用性且不得伪造验证 | ✅ | workflow、README 和模板均已约束 |
| S4 | `spec.md:7-11` | 准备归档时记录实际验证、审查、未验证项和归档建议 | ⚠️ | 审查时实际验证和未验证项完整，最终审查结论和归档建议尚待主 Agent 回填 |
| S5 | `spec.md:13-17` | 纯文案豁免不得把未执行测试描述为完成 | ✅ | quality-gates Rule |
| S6 | `spec.md:21` | 使用中文 Markdown | ✅ | 模板和试运行文件符合 |
| S7 | `spec.md:21` | 至少包含八个规定部分 | ✅ | `evidence.md` 符合 |
| S8 | `spec.md:21` | 验证项区分四种状态 | ✅ | 模板和试运行记录符合 |
| S9 | `spec.md:21,62-66` | 不适用审查必须说明原因 | ✅ | `evidence.md` 体验走查章节 |
| S10 | `spec.md:23-27` | 自动化验证记录时间、仓库、角色、完整命令、状态和摘要 | ✅ | 未知准确分钟已如实标注而非推测 |
| S11 | `spec.md:27` | 摘要足以复核但不保存完整日志 | ✅ | 记录 exit code、通过数和关键失败原因 |
| S12 | `spec.md:29-33` | 未运行或受阻项说明原因、影响和后续处理 | ✅ | `evidence.md` 未验证表 |
| S13 | `spec.md:35-43` | 只记录真实结果，不将计划或 checkbox 当成 PASS | ✅ | 每个 PASS/预期 FAIL 均有命令和摘要 |
| S14 | `spec.md:35-37` | 不保存敏感数据、完整日志、缓存或大体积产物 | ✅ | 模板、证据及冻结 diff 未发现违规内容 |
| S15 | `spec.md:37,45-49` | 截图须脱敏并使用 change 内相对路径 | ✅ | 规则和模板已实现，当前无截图 |
| S16 | `spec.md:51-53` | 角色返回结构化结果，主 Agent持久化 | ✅ | Agent 索引及角色完成报告合同满足 |
| S17 | `spec.md:53` | 两个 Reviewer 继续只读 | ✅ | 两个 TOML 均为 `sandbox_mode = "read-only"` |
| S18 | `spec.md:53` | 长报告和截图使用规定路径并从 evidence 链接 | ✅ | 模板和 Reviewer 合同定义路径 |
| S19 | `spec.md:55-60` | Spec Review 记录结论、覆盖率、阻断项和未验证项，并按需保存报告 | ⚠️ | 审查时本报告已产出完整内容，尚待主 Agent 保存和回填 |
| S20 | `spec.md:60` | 不扩大 Spec Reviewer 写权限 | ✅ | Reviewer 保持只读 |
| S21 | `spec.md:62-66` | 无页面时标记不适用并说明原因，不造假报告或截图 | ✅ | `evidence.md` 已正确处理 |
| S22 | `spec.md:68-70` | 归档前检查失败、阻塞、未运行、偏差、体验问题和风险 | ✅ | workflow、根入口和模板均实现 |
| S23 | `spec.md:70-76` | 审查后变化使旧证据失效，并重跑或说明依据 | ✅ | workflow 与模板已实现 |
| S24 | `spec.md:78-82` | 未关闭阻断问题时不得建议归档并列修复、责任和重验范围 | ✅ | workflow 和模板具备门禁，审查时无实现或验证阻断问题 |

## 二、反向对账表（代码 → Spec）

| # | 代码位置 | 实现内容 | 状态 | Spec 依据 |
| --- | --- | --- | --- | --- |
| R1 | `docs/templates/openspec-change-evidence.md` | 中文八部分证据模板 | ✅ | proposal 与 delta spec |
| R2 | `.codex/rules/workflow.md` | 适用范围、汇总责任、失效和归档门禁 | ✅ | design 与 delta spec |
| R3 | `.codex/rules/quality-gates.md` | 自动化与手工证据字段和真实性约束 | ✅ | delta spec |
| R4 | `.codex/rules/documentation.md` | 精简、安全和按需目录规则 | ✅ | proposal 与 delta spec |
| R5 | `AGENTS.md` | 根任务路由与归档复核边界 | ✅ | tasks 与 design |
| R6 | `.codex/agents/README.md` | 全角色结构化返回及主 Agent 汇总 | ✅ | delta spec |
| R7 | `.codex/agents/qa_engineer.toml` | QA 证据交接合同 | ✅ | tasks 与 delta spec |
| R8 | `.codex/agents/spec_reviewer.toml` | Spec Review 报告交接及只读边界 | ✅ | delta spec |
| R9 | `.codex/agents/experience_reviewer.toml` | 体验报告交接及只读边界 | ✅ | delta spec |
| R10 | `scripts/validate-custom-agents.py` | 校验三个角色的证据合同 | ✅ | tasks 与 design |
| R11 | `scripts/test-custom-agents.py` | 三个新增失败夹具 | ✅ | tasks |
| R12 | `scripts/check-agent-governance.sh` | 检查模板存在和根路由 | ✅ | tasks |
| R13 | `README.md` | 证据使用入口和豁免说明 | ✅ | tasks |
| R14 | `docs/plans/README.md` 治理参考 | 证据模板导航 | ✅ | tasks |
| R15 | `openspec/changes/persist-change-delivery-evidence/evidence.md` | 本 change 首份真实试运行证据 | ⚠️ | 审查时自动化部分完整，最终审查字段待主 Agent 回填 |

### 范围排除

- `docs/plans/openspec-change-approval-backlog.md`
- `docs/plans/README.md` 中的“待评估事项”

上述内容是本 change 创建前用户单独要求的前置文档改动，不属于本 change，不计入正向缺口或反向超纲项。

## 三、状态说明

| 标记 | 含义 |
| --- | --- |
| ✅ | 已覆盖：要求有完整实现和足够证据；反向项可追溯到明确 Spec |
| ❌ | 未覆盖，或代码存在无依据的超纲功能 |
| ⚠️ | 部分覆盖、实现偏差，或等待职责边界内闭环的交接项 |

最终审查结论：`PASS_WITH_ISSUES`。

冻结的治理实现、模板、Rules、角色合同、校验器和验证证据符合已确认的轻量范围；未发现 P0/P1、实现缺口或反向超纲功能。四个 ⚠️ 均源于同一个交接状态：只读 Reviewer 已返回本报告，但主 Agent 尚未保存报告、更新 `evidence.md` 和勾选 task 3.3。

## 四、覆盖率统计

```text
正向覆盖率：61 / 65 = 93.8%
反向超纲项：0
```

| 来源 | 总条数 | ✅ | ❌ | ⚠️ | 覆盖率 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `proposal.md` | 16 | 16 | 0 | 0 | 100.0% |
| `design.md` | 15 | 14 | 0 | 1 | 93.3% |
| `tasks.md` | 10 | 9 | 0 | 1 | 90.0% |
| `specs/change-delivery-evidence/spec.md` | 24 | 22 | 0 | 2 | 91.7% |
| **合计** | **65** | **61** | **0** | **4** | **93.8%** |

⚠️ 不计入完整覆盖。主 Agent完成报告落盘和证据回填后，这四项可在不修改治理实现的前提下闭环。

## 五、修复 Action Items

| 优先级 | Action Item | 关联 Spec | 建议操作 |
| --- | --- | --- | --- |
| P2 | 保存本报告并回填最终 Spec Review 结论 | `tasks.md:17`；Spec Review requirement | 由主 Agent创建本文件，在 `evidence.md` 记录 `PASS_WITH_ISSUES`、61/65、反向超纲 0、无 P0/P1，并更新最终归档建议 |
| P2 | 完成 task 3.3 状态闭环 | `tasks.md:17`；`RULE-WF-002` | 报告和 evidence 保存后勾选 task 3.3，不得由只读 Reviewer 修改 |
| P3 | 归档前同步 delta spec 并复核最终 evidence | `RULE-WF-003` | 使用 OpenSpec sync/archive 正常流程；若落盘后仅新增本报告和证据摘要，不需要重跑应用测试，但应刷新 strict validate 与 diff check |

## 检查范围

- change 全部 artifacts、`evidence.md` 和 `.openspec.yaml`
- 根 `AGENTS.md`、README、Agents 索引及相关 Agent TOML
- workflow、quality-gates、documentation、repository-boundaries Rules
- 证据模板
- custom agent 校验器、失败夹具和治理检查脚本
- 根仓库冻结 Git diff 与未跟踪文件清单
- frontend/backend submodule 状态和局部工作区状态
- `evidence.md` 中 09:52 最终验证记录

## 使用的 Specs / Rules / Skills

- Spec：`openspec/changes/persist-change-delivery-evidence/specs/change-delivery-evidence/spec.md`
- Rules：
  - `.codex/rules/workflow.md`
  - `.codex/rules/quality-gates.md`
  - `.codex/rules/documentation.md`
  - `.codex/rules/repository-boundaries.md`
- Skill：`.codex/skills/openspec-explore/SKILL.md`

未加载 frontend/backend/database conventions，因为本 change 不修改应用源码、数据库或 SQL。

## 未提供或未验证项

- 未保存完整原始终端日志，只保存命令、状态和关键摘要；这符合已确认规格。
- RED 命令的准确分钟未记录，证据已明确标注事实边界，没有推测时间；不影响 RED 结论。
- 未运行前端或后端业务测试；两个 submodule 无改动，因此不属于必要验证。
- Experience Review 因无可运行页面变更而不适用，已正确说明。
- 主领域 spec 尚未同步，应在归档流程闭环。
- 审查时本报告尚待主 Agent持久化，这是角色职责交接，不是治理实现阻断。

## 残余风险

- Markdown 证据依赖主 Agent如实汇总，不提供自动时效判断或防篡改能力；属于已确认的第一版取舍。
- 校验脚本验证合同关键文本存在，不能证明未来报告内容真实；真实性仍依赖实际命令输出和审查。
- 每个 change 是否适用由主 Agent人工判断，Harness 不自动遍历活动 change；属于明确设计边界。
- 保存本报告或更新 evidence 后，如同时修改治理实现、测试或规格，必须按失效规则重新审查受影响范围。

## 下一交接建议

主 Agent保存本报告、更新 `evidence.md` 和 task 3.3 后，本 change 无 Spec 合规阻断，可进入 delta spec 同步与归档前最终复核。
