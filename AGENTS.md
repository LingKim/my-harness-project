# AIWorkSpace AI Coding 入口

本仓库是 ChinaMate 主 AIWorkSpace，负责跨仓库 OpenSpec、Harness、文档、环境和 frontend/backend submodule 编排。本文件只负责 Codex 启动入口和路由；项目角色、稳定约束与任务方法分别集中在根 `.codex/agents/`、`.codex/rules/` 和 `.codex/skills/`。

## 事实优先级

1. `openspec/specs/` 中当前规格和已经确认的活动 change。
2. 当前依赖、源码、测试、migration、Git/submodule 状态和真实命令输出。
3. 任务作用域内的项目 Rules。
4. 当前版本官方文档。
5. 相关项目级 Skills。
6. 代理既有知识。

当前实现违反已确认规格或强制 Rule 时，必须报告差异并通过受控变更修正，不能把现状静默变成新规范。

## 开始任务

按顺序读取：

1. 本文件、[Agents 索引](.codex/agents/README.md)和 [Rules 索引](.codex/rules/README.md)。
2. `README.md` 与 `openspec/config.yaml`。
3. 任务相关的当前 specs 和活动 change artifacts。
4. 涉及前端时，进入 submodule 检查状态并读取 [frontend/AGENTS.md](frontend/AGENTS.md)。
5. 涉及后端或数据库时，进入 submodule 检查状态并读取 [backend/AGENTS.md](backend/AGENTS.md)。
6. 只加载路由要求的 Rules、Skills、源码、测试和版本文档。

## 任务路由

- 同一名开发者承担产品、交互、前端、后端、测试和验收的业务、跨栈、实现、验证或跨会话续作，优先读取 `.codex/skills/chinamate-fullstack-delivery/SKILL.md`，由主 Agent推导阶段、签发`TaskContract`并按工作包创建最少必要的 fresh subagent；简单任务不强制完整流水线。
- 根据交付物从 `.codex/agents/` 选择最少必要角色：产品规格、交互设计、前端、后端、QA、实现后的 Spec 合规审查或交付后体验走查；简单任务不得为了形式完整启动全部角色。
- 产品规格未经用户确认时，前端、后端和 QA 不得开始实现；只有合同已冻结且文件互不争用时，才并行委派写入角色。
- 需求不清、非平凡行为变化、实现、验证与归档：读取 `.codex/rules/workflow.md`，并使用 `.codex/skills/` 中对应 OpenSpec Skill。
- frontend/backend submodule、分支、提交顺序和 gitlink：读取 `.codex/rules/repository-boundaries.md` 与 `.codex/rules/git-safety.md`。
- 测试、静态检查、真实场景和完成声明：读取 `.codex/rules/quality-gates.md`。
- README、OpenSpec、设计、计划和代码注释：读取 `.codex/rules/documentation.md`。
- 业务、行为、跨仓库、API、数据库、安全、架构或治理 change：由主 Agent 使用 `docs/templates/openspec-change-evidence.md` 在 change 根目录维护 `evidence.md`；长审查报告按需保存到 `reviews/`。
- React/Next.js、Java/Spring Boot、MySQL/MyBatis/Flyway：根入口只路由到对应子仓库 `AGENTS.md`，不复制技术规则。

## 不可降低的边界

- 非平凡变更必须先形成 OpenSpec change，并在用户确认规格后才实现。
- 未经用户明确要求，不提交、推送、合并、删除分支或执行破坏性操作；一次授权不扩大到其他仓库或后续操作。
- 当前必需步骤因缺少用户授权、审批或必须由用户作出的决策而阻塞，且用户响应可以解除时，必须按 `RULE-WF-006` 立即申请最小必要授权或请示；不得静默卡住、绕过权限、降低质量或跳过必需步骤。
- 修改子仓库前先运行 `git status --short --branch`，保护用户已有改动并确认不是在 detached HEAD 上遗留提交。
- 没有新的验证输出不得声称完成；修改代码后默认不运行无关 build，但必须运行与风险相称的测试或静态检查。
- 适用 change 归档前必须复核 `evidence.md` 中的失败、阻塞、未运行和残余风险；纯文案、机械格式化和只读探索可以豁免并说明原因。

## 常用入口

```bash
./scripts/check-agent-governance.sh
./scripts/check-harness.sh
git submodule status
make dev
```

本项目只维护根 `.codex` 中的 Agents、Rules 与 Skills；项目级 custom agents 和 OpenSpec 1.6.0 允许生成的 Codex Skills 登记在 `.codex/manifest.json`。项目内不得保留子仓库 `.codex/`、`.agents/`、`.claude/` 或 `CLAUDE.md`。
