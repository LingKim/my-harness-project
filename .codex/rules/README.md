# AI Coding Rules 索引

Rules 是长期稳定、可审查的项目约束；`AGENTS.md` 负责启动路由，`.codex/agents/` 负责角色职责和交付边界，Skills 负责任务方法。目录存在不代表自动加载，代理必须根据入口只选择最少必要角色并读取任务直接相关的 Rule。

| Rule 文件 | ID 前缀 | 适用范围 | 何时加载 |
| --- | --- | --- | --- |
| [workflow.md](workflow.md) | `RULE-WF-*` | 三个仓库 | 探索、提案、实现、验证、归档 |
| [repository-boundaries.md](repository-boundaries.md) | `RULE-REPO-*` | 主仓库与 submodule | 修改 frontend/backend、跨仓库交付 |
| [git-safety.md](git-safety.md) | `RULE-GIT-*` | 三个仓库 | 分支、暂存、提交、推送、破坏性 Git |
| [quality-gates.md](quality-gates.md) | `RULE-QA-*` | 三个仓库 | 选择验证命令、声明完成 |
| [documentation.md](documentation.md) | `RULE-DOC-*` | 人类可读内容 | README、OpenSpec、设计、计划、注释 |
| [frontend-conventions.md](frontend-conventions.md) | `RULE-FE-*` | 前端代码 | React/Next.js/TypeScript/前端测试 |
| [backend-conventions.md](backend-conventions.md) | `RULE-BE-*` | 后端代码 | Java/Spring Boot/模块化单体 |
| [database-conventions.md](database-conventions.md) | `RULE-DB-*` | 后端与数据库 | MySQL/MyBatis/Flyway/SQL/运维 |

## 维护规则

- 每条强制约束必须有唯一、稳定的 Rule ID；语义不变时可以改写正文而不更换 ID。
- 所有 Rule 集中在根 `.codex/rules/`，按技术边界拆文件；不在子仓库或入口复制规则正文。
- Agent 只能引用本索引登记的 Rule；角色特有职责写入 `.codex/agents/*.toml`，长期项目约束仍只在 Rules 维护。
- 新增、删除或改变 Rule 语义属于治理行为变化，必须通过 OpenSpec change 并同步检查脚本。
- 第三方 Skill 保持供应商内容原样；项目覆盖、例外和版本事实写入所属 Rule。项目维护 Skill 通过独立 OpenSpec、Manifest 和 Skills 锁记录来源与内容哈希；当前 `java-springboot` 属于项目维护 Skill。

## 控制与编排入口

- 单人全栈阶段路由：[`chinamate-fullstack-delivery`](../skills/chinamate-fullstack-delivery/SKILL.md)。
- Critical Rule 的责任、控制类型、阻断条件和证据位置：[`control-matrix.md`](../skills/chinamate-fullstack-delivery/references/control-matrix.md)。矩阵只引用 Rule ID，不复制规则正文。
