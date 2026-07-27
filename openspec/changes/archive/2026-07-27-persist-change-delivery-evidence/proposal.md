## Why

当前验证命令、QA 结论、Spec 合规审查和体验走查主要保留在 Agent 完成报告与对话中，change 跨会话或归档后难以稳定追溯“验证了什么、结果如何、还有什么未验证”。项目需要一个轻量、随 change 保存的交付证据入口，让完成与归档结论建立在可复核记录上，而不是依赖聊天记忆。

## What Changes

- 为需要实现或治理交付的 OpenSpec change 增加统一的 `evidence.md`，记录实现范围、自动化验证、真实场景、QA、审查结论、未验证项和最终归档建议。
- 提供一份中文 Markdown 模板；第一版由主 Agent 汇总各角色真实输出，不引入 JSON 状态机、内容哈希、数据库、自动日志采集或 CI 强制。
- 明确业务功能、行为变化、跨仓库、API、数据库、安全、架构和治理行为 change 必须保存证据；纯文案、机械格式化和只读探索可以不创建。
- Spec Reviewer 与 Experience Reviewer 继续保持只读，只返回报告；主 Agent按需把完整报告保存到 change 的 `reviews/`，并在 `evidence.md` 中建立摘要与链接。
- 明确原始完整日志、凭据、Cookie、隐私数据、构建缓存和无实际执行依据的结果不得写入证据。
- 在归档前要求检查 `evidence.md` 中的失败、阻塞、未运行和残余风险，并如实给出是否建议归档的结论。

目标：让重要 change 的验证与审查证据能够跨会话、随 OpenSpec 归档长期保留，并保持人工可读、维护成本低。

非目标：不自动判断证据是否过期；不绑定 Git SHA 或规格指纹；不保存完整终端日志；不为纯文档小改强制增加仪式；不修改业务功能、API、数据库 schema 或应用依赖。

验收结果：适用 change 能按模板生成可读的 `evidence.md`；记录明确区分 `PASS`、`FAIL`、`BLOCKED`、`NOT_RUN`；QA、Spec Review 和 Experience Review 的责任与落盘方式清晰；归档后仍可从 change 目录复核实际验证范围和残余风险。

主要风险：证据由主 Agent 汇总，仍依赖如实记录，不能提供密码学防篡改；Markdown 可能随大型 change 变长。第一版通过固定最小字段、禁止原始日志堆积、长报告按需拆到 `reviews/` 和先在真实 change 中试运行控制复杂度。

## Capabilities

### New Capabilities

- `change-delivery-evidence`: 定义 OpenSpec change 的交付证据文件、适用范围、最小记录字段、角色责任、敏感信息边界和归档前检查要求。

### Modified Capabilities

无。

## Impact

- 主仓库：新增证据模板，更新 `.codex/rules/workflow.md`、`.codex/rules/quality-gates.md`、`.codex/rules/documentation.md`、相关 Agent 合同、Agents/README 或项目说明。
- 活动 change：后续适用的业务或治理 change 在自身目录维护 `evidence.md`，长审查报告和截图按需放在 `reviews/` 与 `assets/`。
- Harness/OpenSpec：第一版只校验治理接入与模板存在，不把证据升级为新的 OpenSpec schema artifact，也不修改 OpenSpec 1.6.0 生成文件。
- 前端和后端：不修改业务源码、测试逻辑、运行时依赖、API 或数据库 schema。
