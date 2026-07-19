## Why

当前仓库虽然已经包含可运行的前后端代码，但根仓库尚无首个提交，`frontend/` 与 `backend/` 也只是普通未跟踪目录，无法作为具有独立版本生命周期的工程协作。需要把根项目升级为 AIWorkSpace，由主仓库统一保存 Harness、OpenSpec 与环境编排，并通过 Git submodule 精确引用独立的前后端仓库。

## Goals

- 将主仓库关联到 `https://github.com/LingKim/my-harness-project`，并建立可复现的 AIWorkSpace 仓库结构。
- 完整保留现有 `frontend/` 与 `backend/` 代码，分别迁移到用户指定的独立 GitHub 仓库。
- 让主仓库通过 `.gitmodules` 和 gitlink 固定前后端提交，而不是继续直接跟踪其内部文件。
- 使用中文更新 `AGENTS.md`，明确根仓库与两个 submodule 的职责、初始化方式和 AI 修改边界。
- 提供可以验证新检出仓库及 submodule 状态的命令和 Harness 检查。

## Non-goals

- 不修改前端、后端业务行为、依赖版本或运行配置。
- 不重写三个仓库在本次迁移后产生的 Git 历史。
- 不引入 monorepo 构建工具，也不改变前后端之间的 HTTP/JSON 集成方式。
- 不配置 CI/CD、分支保护、GitHub Actions 或发布流程。

## Acceptance Outcomes

- 主仓库存在首个可推送提交，并将 `frontend/`、`backend/` 记录为模式 `160000` 的 gitlink。
- `.gitmodules` 中的两个 URL 分别为用户提供的前端与后端 GitHub 地址。
- 前端、后端远端各自存在包含当前代码的可检出提交，主仓库引用的提交在对应远端可达。
- 执行 `git clone --recurse-submodules` 或 `git submodule update --init --recursive` 可以恢复完整工作区。
- `AGENTS.md` 与 Harness 自检能够说明并验证 AIWorkSpace、主仓库和两个 submodule 的边界。

## What Changes

- **BREAKING**：`frontend/` 和 `backend/` 从主仓库普通目录变为 Git submodule，提交、分支切换和推送需要分别在三个仓库中进行。
- 为现有前端和后端代码分别建立独立 Git 历史，并关联 `my-harness-frontend` 与 `my-harness-backtend`。
- 为主仓库配置 `my-harness-project` 远端，创建 `.gitmodules` 并记录两个 submodule 的固定提交。
- 更新根目录 `AGENTS.md`、`README.md` 和 `scripts/check-harness.sh`，补充 AIWorkSpace 定位、submodule 使用说明和结构校验。

## Capabilities

### New Capabilities

- `ai-workspace-repository-composition`: 定义主仓库、前端 submodule、后端 submodule之间的仓库边界、可复现检出方式和提交可达性。

### Modified Capabilities

- `fullstack-project-foundation`: 将“前后端工程相互独立”的要求收紧为由主仓库通过 Git submodule 固定独立仓库提交，并扩展 Harness 对 submodule 元数据的验证。

## Risks

- 迁移需要创建并推送三个仓库的首个提交；如果 GitHub 认证或写权限不可用，主仓库无法引用远端可达的 submodule 提交。
- `backend` 远端地址按用户提供值保留为 `my-harness-backtend`，其中的拼写不能擅自更正，否则会指向不同仓库。
- 直接移动未提交目录存在丢失风险，因此迁移必须先建立可恢复备份或独立提交，再替换根目录中的工作树表示。
- submodule 默认处于 detached HEAD，开发者若未先切换分支就提交，可能产生难以发现的悬空提交。

## Impact

- 影响根仓库 Git 元数据、`frontend/`、`backend/`、`.gitmodules`、`AGENTS.md`、`README.md`、`scripts/check-harness.sh` 和 OpenSpec 规格。
- 需要对三个 GitHub 仓库执行首次推送，并要求本机具备对应的 GitHub 写权限。
- 不影响现有应用 API、数据库结构、环境变量契约和运行端口。
