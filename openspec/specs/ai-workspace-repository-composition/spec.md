## Purpose

定义 AIWorkSpace 主仓库与前后端 submodule 的仓库组成、可复现检出、远端可达性和跨仓库交付顺序，确保三个独立 Git 仓库能够被正确协作和恢复。

## Requirements

### Requirement: AIWorkSpace 由三个独立 Git 仓库组成
系统 SHALL 使用主仓库承载跨项目 Harness、OpenSpec 与开发编排，并通过 Git submodule 在 `frontend/` 和 `backend/` 固定两个独立应用仓库的具体提交。

#### Scenario: 检查主仓库索引
- **WHEN** 开发者检查主仓库的已跟踪文件模式
- **THEN** `frontend` 和 `backend` 均以模式 `160000` 存在
- **AND** 主仓库不直接跟踪两个 submodule 内部的应用文件

#### Scenario: 检查 submodule URL
- **WHEN** 开发者读取 `.gitmodules`
- **THEN** `frontend` 的 URL 为 `https://github.com/LingKim/my-harness-frontend`
- **AND** `backend` 的 URL 为 `https://github.com/LingKim/my-harness-backtend`

### Requirement: 完整工作区可以被可复现检出
系统 SHALL 确保主仓库引用的每个 submodule 提交都在相应 GitHub 远端可达，并支持使用标准 Git submodule 命令恢复完整代码。

#### Scenario: 全新递归检出
- **WHEN** 开发者执行 `git clone --recurse-submodules` 检出主仓库
- **THEN** 根级 Harness 文件、前端工程和后端工程均可用
- **AND** 两个 submodule 的 HEAD 与主仓库记录的 gitlink SHA 一致

#### Scenario: 已有检出初始化 submodule
- **WHEN** 开发者在未初始化 submodule 的主仓库中执行 `git submodule update --init --recursive`
- **THEN** `frontend/` 和 `backend/` 被检出到主仓库固定的提交

### Requirement: 子仓库更新遵循可达性顺序
开发流程 MUST 先把前端或后端的新提交推送到对应远端，再更新并推送主仓库中的 gitlink。

#### Scenario: 更新前端引用
- **WHEN** 开发者完成前端修改并准备更新 AIWorkSpace
- **THEN** 前端提交先在 `my-harness-frontend` 远端可达
- **AND** 主仓库随后记录该前端提交的 SHA

#### Scenario: 子仓库提交尚未推送
- **WHEN** 主仓库 gitlink 指向的子仓库提交在对应远端不可达
- **THEN** 迁移或交付验证失败
- **AND** 主仓库不得宣称可以被完整复现检出

### Requirement: AI 代理理解三个仓库的操作边界
根级 `AGENTS.md` SHALL 使用中文说明主仓库、`frontend/` 和 `backend/` 的职责、上下文加载顺序、分支注意事项以及提交和推送顺序。

#### Scenario: AI 修改应用代码
- **WHEN** AI 代理准备修改 `frontend/` 或 `backend/` 中的文件
- **THEN** 先进入对应 submodule 检查状态、当前分支和该仓库自己的规则
- **AND** 不把子仓库内部文件当作主仓库普通文件提交

#### Scenario: AI 完成跨仓库变更
- **WHEN** 一个 OpenSpec change 同时影响主仓库和应用仓库
- **THEN** 任务与验证记录分别覆盖每个受影响仓库
- **AND** 子仓库提交远端可达后才更新主仓库 gitlink
