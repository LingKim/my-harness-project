## Context

根目录当前是尚无提交的 Git 仓库，`frontend/` 与 `backend/` 都不是独立 Git 仓库，全部文件处于根仓库未跟踪状态。三个用户指定的 GitHub 仓库经过 `git ls-remote --symref <url> HEAD` 只读核对，当前均未返回引用，可按空仓库处理。

目标结构是一个 AIWorkSpace：主仓库保存 Harness、OpenSpec、跨项目文档、Compose 和环境模板；前端、后端各自拥有独立历史，并由主仓库通过 Git submodule 固定具体提交。迁移会涉及三个首个提交和三次首次推送，任何一步失败都不能把现有代码置于不可恢复状态。

## Goals / Non-Goals

**Goals:**

- 完整保留现有前端、后端工作树内容和文件权限。
- 让前端、后端的首个提交先在各自 GitHub 远端可达，再由主仓库记录 gitlink。
- 让全新检出和已有检出都可以通过标准 submodule 命令恢复完整工作区。
- 在根级 `AGENTS.md` 中明确三个仓库的职责、上下文加载顺序和提交边界。
- 通过 Harness 和 Git plumbing 命令验证 `.gitmodules`、URL、gitlink 模式与提交可达性。

**Non-Goals:**

- 不改变应用源码、依赖、API 或数据库行为。
- 不使用 `git subtree`、monorepo 编排器或自定义依赖同步脚本。
- 不自动配置 GitHub 仓库设置、CI/CD 或分支保护。
- 不在未获得用户确认前提交或推送。

## Decisions

### 1. 主仓库只编排，应用代码由 submodule 独立管理

`my-harness-project` 作为 AIWorkSpace 主仓库，只直接跟踪根级 Harness、OpenSpec、文档、基础设施文件、`.gitmodules` 以及两个 gitlink。`frontend/` 指向 `my-harness-frontend`，`backend/` 指向用户提供的 `my-harness-backtend`。

选择 submodule 是因为用户明确要求独立仓库和固定版本引用。`git subtree` 会把应用历史复制进主仓库，不符合独立版本边界；普通目录则无法独立发布和授权。

### 2. 在现有目录原地建立独立仓库

分别在 `frontend/` 和 `backend/` 中执行 `git init -b main`、配置 `origin`、创建首个提交并推送。随后在根仓库使用现有本地仓库注册 submodule，并运行 `git submodule absorbgitdirs`，把嵌套仓库的 Git 元数据统一吸收到根仓库 `.git/modules/`。

该方案避免复制或临时删除体积约 674MB 的前端目录。替代方案是把目录移动到临时位置后重新 clone，但移动和回填会增加中断期间的风险与耗时。

### 3. 提交与推送严格按依赖顺序执行

顺序固定为：

1. 检查忽略文件与敏感信息，确认不会提交 `.env`、构建产物或依赖目录。
2. 创建并推送前端首个提交。
3. 创建并推送后端首个提交。
4. 在根仓库配置 `origin`，注册两个 submodule，更新根级文档与 Harness。
5. 验证 gitlink 指向的提交在对应远端可达。
6. 创建并推送主仓库首个提交。

主仓库不能先推送一个引用远端不可达 submodule commit 的提交，否则其他开发者无法检出完整工作区。

### 4. 使用 `main` 作为三个仓库的初始分支

三个空仓库都以 `main` 创建首个分支。`.gitmodules` 记录 URL，不依赖开发者本机的绝对路径；主仓库仍通过 gitlink 固定具体 SHA。是否在 `.gitmodules` 中增加 `branch = main` 只影响 `git submodule update --remote` 的默认跟踪分支，不改变固定 SHA 语义，本次不增加该配置以保持最小行为。

### 5. 根级规则明确 submodule 操作边界

`AGENTS.md` 将补充：

- 根仓库负责跨项目规格和编排，不直接记录前后端内部文件。
- 修改应用前先进入对应 submodule，读取其中的 `AGENTS.md`（如果存在）并确认当前分支，避免在 detached HEAD 上遗留提交。
- 应用提交、推送先在子仓库完成，再回到根仓库更新 gitlink。
- 根级 OpenSpec 涉及跨仓库变更时，tasks 必须分别列出子仓库实现、验证和 gitlink 更新。

### 6. Harness 验证 Git 结构而非只验证路径存在

`scripts/check-harness.sh` 除原有文件检查外，还必须验证：`.gitmodules` 存在；两个 path/url 精确匹配；根索引中两条记录的模式为 `160000`；submodule 工作树可解析；在人类可读输出中指出缺失初始化、URL 漂移或 gitlink 错误。

仅检查 `frontend/`、`backend/` 目录存在无法区分普通目录、未初始化 submodule 和正确 gitlink，因此不足以作为迁移验收。

## Risks / Trade-offs

- **GitHub 认证或写权限不可用** → 在任何目录替换前先验证认证；每次推送失败立即停止，不创建主仓库 gitlink 提交。
- **忽略规则遗漏导致依赖、密钥或构建产物进入首个提交** → 提交前分别检查 `git status --short --ignored`、敏感信息模式和实际暂存清单。
- **submodule 默认 detached HEAD 导致提交丢失** → 文档要求修改前切换 `main` 或工作分支，并在提交后验证远端可达。
- **主仓库与子仓库更新不是原子事务** → 始终先推子仓库，再更新主仓库 gitlink；回滚时主仓库可退回前一个 gitlink。
- **后端仓库名称存在 `backtend` 拼写** → 精确使用用户提供 URL，不擅自纠正。
- **三个仓库首次提交会让后续审查范围较大** → 首次提交只包含当前基线，不混入业务修改，并分别输出暂存文件统计。

## Migration Plan

1. 在三个工作树中执行只读状态、忽略规则、敏感信息和远端空仓库检查。
2. 在 `frontend/` 原地初始化 `main`，提交现有前端基线，推送到 `my-harness-frontend` 并验证远端 SHA。
3. 在 `backend/` 原地初始化 `main`，提交现有后端基线，推送到 `my-harness-backtend` 并验证远端 SHA。
4. 为根仓库配置 `my-harness-project` origin，把现有两个独立仓库注册为 submodule，并吸收 Git 元数据。
5. 更新 `.gitmodules`、`AGENTS.md`、`README.md`、OpenSpec context 和 Harness 检查。
6. 运行 Harness、OpenSpec 严格校验、`git ls-files --stage`、`git submodule status` 与远端可达性验证。
7. 创建并推送主仓库首个提交，最后用临时目录执行一次 `git clone --recurse-submodules` 验证可复现检出。

回滚策略：主仓库提交前，前后端目录仍保留完整工作树，可移除根级 submodule 元数据并恢复为独立仓库；主仓库提交后，通过回退主仓库 gitlink 或重新检出目标 SHA 恢复，不删除已推送的子仓库提交。

## Open Questions

无阻塞性设计问题。提交和推送属于外部持久化操作，只有在用户确认本提案并执行 `/opsx:apply` 后进行。
