## 1. 迁移前安全检查

- [x] 1.1 在根目录、`frontend/` 和 `backend/` 检查实际文件、忽略规则、敏感信息模式与待提交清单，确认 `.env`、`node_modules/`、`.next/`、`target/` 等本地或生成内容不会进入任何首个提交。
- [x] 1.2 使用 `git ls-remote` 再次验证三个 GitHub 仓库仍为空，并使用非写入式认证检查确认当前凭据对三个仓库具备预期访问能力；若远端状态已变化则停止迁移并更新设计。

## 2. 建立独立前端仓库

- [x] 2.1 在现有 `frontend/` 原地初始化 `main` 分支，配置 `origin=https://github.com/LingKim/my-harness-frontend`，暂存后复核文件清单与敏感信息检查结果。
- [x] 2.2 创建前端基线提交并推送 `origin/main`，使用本地 SHA 与 `git ls-remote` 验证该提交在远端可达，不修改前端应用代码。

## 3. 建立独立后端仓库

- [x] 3.1 在现有 `backend/` 原地初始化 `main` 分支，配置 `origin=https://github.com/LingKim/my-harness-backtend`，暂存后复核文件清单与敏感信息检查结果。
- [x] 3.2 创建后端基线提交并推送 `origin/main`，使用本地 SHA 与 `git ls-remote` 验证该提交在远端可达，不修改后端应用代码。

## 4. 将根仓库升级为 AIWorkSpace

- [x] 4.1 先扩展 `scripts/check-harness.sh` 的 submodule 断言，并在普通目录状态下运行得到预期失败，覆盖 `.gitmodules`、精确 URL、模式 `160000` 的 gitlink 和已初始化工作树。
- [x] 4.2 为根仓库配置 `origin=https://github.com/LingKim/my-harness-project`，将现有 `frontend/`、`backend/` 独立仓库注册到 `.gitmodules`，运行 `git submodule absorbgitdirs` 并确认工作树内容未发生丢失。
- [x] 4.3 使用中文更新根目录 `AGENTS.md`，补充 AIWorkSpace 定位、主仓库职责、`frontend/` 与 `backend/` submodule 说明、规则加载顺序、分支注意事项以及“先推子仓库、再更新 gitlink”的提交边界。
- [x] 4.4 使用中文更新根目录 `README.md` 与 `openspec/config.yaml`，说明三个仓库的地址、递归 clone、已有检出初始化、submodule 日常更新和跨仓库开发命令。

## 5. 验证与首次交付

- [x] 5.1 运行 `bash -n scripts/check-harness.sh`、`./scripts/check-harness.sh`、OpenSpec 严格校验、`git submodule status`、`git ls-files --stage frontend backend` 和远端 SHA 可达性检查，记录实际结果；本次不运行无关的前后端 build。
- [x] 5.2 在根仓库创建包含 AIWorkSpace 基线与两个 gitlink 的首个提交并推送 `origin/main`，确认 GitHub 远端 HEAD 指向该提交。
- [x] 5.3 在临时目录执行 `git clone --recurse-submodules https://github.com/LingKim/my-harness-project`，验证根级 Harness、`frontend/package.json`、`backend/pom.xml` 和两个 submodule SHA；删除临时验证目录后更新任务状态并推送最终的 OpenSpec 完成记录。
