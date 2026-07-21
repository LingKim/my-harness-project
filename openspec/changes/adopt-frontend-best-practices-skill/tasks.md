## 1. 建立项目级 Skill 基线

- [x] 1.1 复核 `.agents/skills/vercel-react-best-practices/` 与 `skills-lock.json`，确认文件来自 `vercel-labs/agent-skills@vercel-react-best-practices`、锁文件只包含该 Skill，并使用文件清单和锁记录验证结果。
- [x] 1.2 先扩展 `scripts/check-harness.sh` 的前端 Skill 断言，覆盖 Skill 入口、规则文件、唯一锁记录和根级 `AGENTS.md` 引用；在尚未加入 AGENTS 引用时运行并确认检查因正确原因失败。

## 2. 启用 React 与 Next.js 最佳实践

- [x] 2.1 修改根目录 `AGENTS.md`，规定涉及 `frontend/` 的 React/Next.js 编写、评审和重构任务必须使用 `vercel-react-best-practices`，并注明 OpenSpec、前端局部规则和当前 Next.js 16 本地文档的优先级高于通用 Skill 建议。
- [x] 2.2 检查 `frontend/` 与 `backend/` submodule 状态，确认本次没有修改子仓库文件或主仓库 gitlink，也没有引入 Vercel 仓库中的其他无关 Skills。

## 3. 验证与交付说明

- [x] 3.1 运行 `bash -n scripts/check-harness.sh`、`./scripts/check-harness.sh` 和 `git diff --check`，确认 Skill 文件、锁记录和 AGENTS 触发规则通过门禁；本次不运行无关 build。
- [x] 3.2 使用固定版本 OpenSpec CLI 对 `adopt-frontend-best-practices-skill` 执行严格校验，复核实际变更清单，并记录 Skill 来源、适用范围、版本冲突处理和后续显式更新方式；未经用户授权不提交或推送。

## 4. 修正多 Skill 扩展能力

- [x] 4.1 修改 `scripts/check-harness.sh` 与根目录 `AGENTS.md`，把“锁文件永久只能包含一个 Skill”修正为“锁文件只能包含显式批准清单中的 Skill”，同时继续严格校验 `vercel-react-best-practices` 的来源、路径、哈希、文件和触发规则。
- [x] 4.2 先用临时未批准锁记录验证 Harness 因正确原因失败，再恢复真实锁文件并运行 `bash -n scripts/check-harness.sh`、`./scripts/check-harness.sh`、`git diff --check` 与 OpenSpec 严格校验；本任务不得引入新的业务 Skill、提交或推送。
