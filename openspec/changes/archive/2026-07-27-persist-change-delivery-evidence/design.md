## Context

当前 `.codex/rules/quality-gates.md` 要求验证结果可追溯，QA、Spec Reviewer 与 Experience Reviewer 也都定义了结构化报告，但报告默认返回主 Agent 或用户，没有项目内的持久化位置。OpenSpec change 归档后可以保留 proposal、design、specs 和 tasks，却无法稳定回答每项验证何时执行、是否通过、哪些审查未运行以及最终为什么允许归档。

本变更只建立最小的 Markdown 证据层。它不尝试把 OpenSpec 改造成审计系统，也不替代测试、CI、Git 历史或 Agent 的实时完成报告。

## Goals / Non-Goals

**Goals:**

- 让重要 change 的实际验证和审查结论随 change 长期保留。
- 使用一个人类可读的统一入口，明确区分通过、失败、阻塞、未运行和不适用。
- 保持 QA、Spec Reviewer、Experience Reviewer 与主 Agent 的现有权限边界。
- 控制证据体积和敏感信息风险，不堆积完整日志与临时产物。
- 用本变更作为第一份试运行证据，验证维护成本后再决定是否自动化。

**Non-Goals:**

- 不新增 OpenSpec schema artifact 或修改 OpenSpec 1.6.0 生成文件。
- 不使用 JSON/YAML 状态机、数据库、规格指纹、Git SHA 绑定或密码学签名。
- 不自动抓取终端日志、测试报告、浏览器数据或聊天记录。
- 不接入新的 CI 工作流，不自动判定证据是否过期。
- 不要求纯文案、机械格式化和只读探索创建证据文件。
- 不修改业务源码、API、数据库 schema、测试逻辑或应用依赖。

## Decisions

### 1. 每个适用 change 使用一份根级 `evidence.md`

`evidence.md` 与 proposal、design 和 tasks 同级，作为该 change 的证据索引和最终交付摘要。选择单文件而不是每次固定创建多个报告文件，是为了让简单 change 只维护一个入口，并随整个 change 一起归档。

模板固定八部分：基本信息、自动化验证、手工/真实场景、QA、Spec Review、Experience Review、未验证项与风险、最终交付结论。自动化验证使用表格记录时间、仓库、角色、命令、状态和摘要。

备选方案是把每次测试保存为独立 JSON 或日志文件；它更便于机器处理，但会增加格式、生成器和清理成本，第一版不采用。

### 2. 长报告和截图按需拆分

`reviews/spec-review.md`、`reviews/experience-review.md` 与 `assets/` 均为可选。只有完整报告或截图确实需要长期保留时才创建，`evidence.md` 始终保存结论、未验证项和相对链接。

这避免所有 change 预先创建空目录，也避免把数百行双向对账表塞进主摘要。

### 3. 主 Agent 是唯一证据汇总者

Frontend、Backend 和 QA 角色返回实际命令、结果、文件和风险；Spec Reviewer 与 Experience Reviewer 返回只读报告。主 Agent 将这些输出转录到 change，并负责区分已执行、未运行和受阻。

不让只读 Reviewer 获得写权限，可以保持审查独立性。代价是证据文件的落盘仍依赖主 Agent 如实汇总，因此本方案提供可追溯性，不提供防篡改保证。

### 4. 只保存可复核摘要，不保存完整原始日志

命令必须完整保留，例如 `./mvnw -Dtest=ArchitectureRulesTests test`；结果摘要只保存 exit code、测试数量、失败数量、关键错误或页面观察。完整 Maven/pnpm 输出、浏览器网络导出、覆盖率站点和缓存不进入 change。

若证据来自外部 CI，可记录稳定 URL 和结论；若包含账号、Cookie、token、隐私或原始异常敏感信息，必须脱敏或放弃保存。

### 5. 第一版采用人工时效检查

审查后实现发生变化时，主 Agent 在 `evidence.md` 中把旧记录标记为“已失效”或追加新的验证记录。归档前人工检查最新记录是否覆盖最终实现。

备选方案是对实现或 diff 计算哈希并自动失效；用户已决定第一版控制复杂度，因此暂不采用。试运行两到三个真实 change 后再评估自动化价值。

### 6. 模板与治理接入集中在主仓库

新增 `docs/templates/openspec-change-evidence.md` 作为唯一模板。长期强制边界写入 workflow、quality-gates 和 documentation Rules；Agent TOML 只增加角色特有的交付与汇总责任，不复制完整模板正文。

Harness 只检查模板、Rule 路由和相关 Agent 合同存在，不检查每个活动 change 是否必须有证据；具体适用性和归档判断由主 Agent 按 change 范围负责。

## Risks / Trade-offs

- [主 Agent 可以漏记或误记结果] → 要求每条记录包含实际角色、命令、状态和摘要，并由 Spec Reviewer 检查证据与实现范围是否一致。
- [证据在后续修改后过期] → 第一版要求人工标记失效并重跑受影响验证，试运行后再决定是否增加自动时效校验。
- [Markdown 变成长日志仓库] → 禁止保存完整原始日志和缓存，长审查报告只按需拆分。
- [敏感信息进入仓库] → 模板明确脱敏字段，无法安全脱敏的证据不保存。
- [简单任务流程负担上升] → 只对业务、行为、跨仓库、API、数据库、安全、架构和治理行为 change 强制，纯文案与探索豁免。
- [额外文件不被 OpenSpec 状态识别] → 第一版接受它是项目治理扩展，通过 Rule、Agent 合同和归档检查接入，不改 OpenSpec schema。

## Migration Plan

1. 新增 `change-delivery-evidence` delta spec 和 Markdown 模板。
2. 先更新治理校验的失败夹具，使缺少模板或 Agent/Rule 路由时能够失败。
3. 更新 workflow、quality-gates、documentation 和相关 Agent 合同，明确适用范围、记录责任和归档门禁。
4. 运行治理检查、Harness、`git diff --check` 和 OpenSpec strict validate。
5. 在本 change 的实现阶段创建首份 `evidence.md`，记录本变更的实际验证与审查结果。
6. 本规则生效前已经完成的历史 change 不补写或推测证据；后续新 change 按适用范围执行。

回滚时删除模板与对应路由，恢复 Agent 合同和 Rules；已经归档的历史 `evidence.md` 作为事实记录保留，不删除。

## Open Questions

- 试运行两到三个真实 change 后，是否需要增加归档前自动检查或 CI 链接采集，由后续独立决策确定，不阻塞第一版。
