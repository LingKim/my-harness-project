# Plans

这里存放需要脱离单个 OpenSpec change 长期保留的执行计划。

通常情况下，任务拆解应直接维护在 `openspec/changes/<change-name>/tasks.md`。只有跨多个 change 的路线图或迁移计划才放在这里。

## 当前计划

- [ChinaMate MVP 单人开发计划](./chinamate-mvp-development-plan.md)：基于 PRD v1.2，按“1 名开发者 + AI Coding”编排的 20 周开发路线、模块状态看板和可持续勾选任务清单。

## 待评估事项

- [OpenSpec Change 用户确认状态持久化待办](./openspec-change-approval-backlog.md)：记录确认状态跨会话持久化的风险、候选方向和重新评估触发条件；当前不实施。

## 治理参考

- [OpenSpec Change 交付证据模板](../templates/openspec-change-evidence.md)：业务、行为、跨仓库、API、数据库、安全、架构和治理 change 的验证与审查证据入口；纯文案、机械格式化和只读探索可以豁免并说明原因。
- [单人全栈交付 Skill](../../.codex/skills/chinamate-fullstack-delivery/SKILL.md)：产品、交互、前后端、测试与验收由一人承担时的阶段恢复和最短路径入口。
- [Rule 控制矩阵](../../.codex/skills/chinamate-fullstack-delivery/references/control-matrix.md)：Critical Rule 的责任、硬关卡与证据位置。
- [跨栈系统地图](../architecture/system-map.md)与[领域术语桥](../standards/domain-glossary.md)：业务到页面、API、模块、数据和测试的轻量知识入口。
- [验证 Profiles](../../.codex/skills/chinamate-fullstack-delivery/references/verification-profiles.md)：固定命令采集 machine manifest 并检查输入时效；机器结果不替代 QA、Spec Review 或体验验收。

编排不会自动执行 commit、push、gitlink 更新或 OpenSpec 归档。只有达到 Skill 中记录的量化升级触发条件时，才另开 change 评估逐模块 Wiki 或更重的知识基线。
