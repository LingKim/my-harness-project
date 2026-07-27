## MODIFIED Requirements

### Requirement: AI 代理理解三个仓库的操作边界
根级 `AGENTS.md` SHALL 使用中文说明主仓库、`frontend/` 和 `backend/` 的职责、统一事实优先级、上下文路由、角色选择、分支注意事项以及提交和推送顺序；前端和后端仓库 SHALL 分别使用本地 `AGENTS.md` 路由到主工作区根 `.codex/agents`、`.codex/rules` 和 `.codex/skills`，且子仓库不得保存 `.codex` 规范副本。

#### Scenario: AI 修改应用代码
- **WHEN** AI 代理准备修改 `frontend/` 或 `backend/` 中的文件
- **THEN** 先进入对应 submodule 检查状态、当前分支和该仓库自己的 `AGENTS.md`
- **AND** 按局部入口从根 `.codex` 只选择任务相关 Agents、Rules 和 Skills
- **AND** 不把子仓库内部文件当作主仓库普通文件提交

#### Scenario: AI 完成跨仓库变更
- **WHEN** 一个 OpenSpec change 同时影响主仓库和应用仓库
- **THEN** 任务与验证记录分别覆盖每个受影响仓库
- **AND** 主 Agent 只并行委派互不争用文件且契约已确认的角色任务
- **AND** 子仓库提交远端可达后才更新主仓库 gitlink

#### Scenario: 局部规则与根级规则职责重叠
- **WHEN** 某项约束只适用于前端或后端代码
- **THEN** 该约束必须由根 `.codex/rules` 中对应技术文件维护
- **AND** 根级和子仓库入口都只保留路由，不复制规则正文
