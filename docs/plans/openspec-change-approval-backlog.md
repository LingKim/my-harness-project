# OpenSpec Change 用户确认状态持久化待办

## 状态

- 当前状态：待评估
- 当前决定：暂不实施
- 记录日期：2026-07-27
- 适用范围：AIWorkSpace 根仓库中的 OpenSpec change

## 背景

当前工作流要求非平凡变更在 proposal、specs、design 和 tasks 完整并经过用户确认后，才能进入实现。现阶段确认事实主要保留在 Codex 对话上下文中，尚未作为可跨会话检查的项目状态持久化。

这可能在以下情况下产生风险：

- 新会话无法准确判断用户确认过哪一版规格。
- 规格确认后再次修改，但原确认仍被误认为有效。
- 多个 Agent 或多个活动 change 并行时，主 Agent 难以稳定判断实现门禁。
- 归档前缺少可追溯的确认依据。

## 候选方向

后续如决定实施，可评估“确认记录 + 规格版本绑定 + Apply 前检查”的轻量方案：

1. 在 change 目录中保存独立确认记录，不修改 OpenSpec 自身生成的元数据格式。
2. 将确认记录绑定到 proposal、specs、design 和 tasks 的具体版本。
3. 规格内容变化后，将原确认视为失效并要求重新确认。
4. 在进入实现或归档前增加统一的 change-ready 检查。

以上仅为候选方向，不代表已经确认的设计；文件格式、指纹算法、命令和 CI 接入方式均未确定。

## 暂不实施的内容

本待办当前不授权以下工作：

- 不创建 `approval.json` 或其他确认状态文件。
- 不新增 `change-approval`、`check-change-ready` 等脚本。
- 不修改现有 Agents、Rules、Skills 或 Harness。
- 不创建新的 OpenSpec change。
- 不为历史 change 补写或推测用户确认记录。

## 重新评估的触发条件

满足以下任一条件时，再决定是否启动正式 OpenSpec change：

- 实际发生跨会话后无法判断规格是否确认的问题。
- 实际发生规格修改后仍按旧确认继续实现的问题。
- 同时维护多个活动 change，出现范围或确认状态混淆。
- 开始通过 CI、PR 或多人协作强制执行 OpenSpec 门禁。
- 现有对话确认方式已经明显影响交付效率或审计追溯。

## 后续需要回答的问题

- 是否确实需要机器强制，还是保持主 Agent 的人工门禁即可。
- 最小可用方案能否只记录确认摘要和规格版本，避免引入复杂状态机。
- 确认记录应放在 change 目录、独立治理目录还是外部系统。
- tasks checkbox 更新是否应影响确认有效性。
- 如何避免 Agent 自行写入“用户已确认”造成伪确认。
- 是否只对高风险或跨仓库 change 启用，而不是所有 change 强制启用。

## 关联规范

- [OpenSpec 与实现工作流](../../.codex/rules/workflow.md)
- [质量门禁](../../.codex/rules/quality-gates.md)
- [项目级 Agents](../../.codex/agents/README.md)
