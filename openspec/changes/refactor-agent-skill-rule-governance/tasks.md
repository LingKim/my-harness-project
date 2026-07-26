## 1. 固定兼容性事实与失败门禁

- [x] 1.1 在主仓库记录 `.agents/`、`.codex/`、`.claude/` 当前文件清单、内容哈希和 OpenSpec 生成归属，执行固定版本 `openspec update --force` 的可恢复探针并得到实际生成物清单；验证方式为探针前后 `git diff --name-status`、哈希对比和工作区恢复检查。
- [x] 1.2 分别从主仓库、`frontend/` 和 `backend/` 作用域验证 Codex 对 `.agents/skills` 的真实发现与读取行为，并在可用环境验证 Claude Code 的发现/命令入口；把已证实必需的工具适配器及生成命令记录到设计或规则索引，不根据推测删除目录。
- [x] 1.3 先扩展 `scripts/check-harness.sh` 或新增治理检查测试夹具，使其期待根入口、三份 conventions、Rule ID、分仓库 Skill 锁、有效引用和适配器清单；在目标文件尚未建立时运行检查并确认因缺失三层结构而失败。

## 2. 建立前端局部 Rules 与 Skill 所有权

- [x] 2.1 在 `frontend/` 先建立局部治理检查的失败场景，覆盖缺少 `AGENTS.md` 路由、`rules/frontend-conventions.md`、前端 Skill、锁记录或出现重复规范源时失败，并运行检查确认 RED。
- [x] 2.2 重写 `frontend/AGENTS.md` 为薄入口，创建 `frontend/rules/frontend-conventions.md`，使用稳定前端 Rule ID 覆盖 Next.js/React 事实优先级、目录与组件边界、Server/Client 选择、数据获取、国际化、可访问性、环境变量和风险相称的 lint/typecheck/test/E2E 路由。
- [x] 2.3 使用可追踪方式把 `vercel-react-best-practices` 迁入 `frontend/.agents/skills/`，建立前端 `skills-lock.json` 或等价本地锁与批准清单，复核供应商内容未被项目规则修改，并确认主仓库不再拥有第二份规范源。
- [x] 2.4 更新 `frontend/README.md` 和必要的薄工具入口，运行前端局部治理检查、`git diff --check` 及与规则文件/脚本相关的静态检查；本任务不运行无关前端 build。

## 3. 建立后端局部 Rules 与 Skill 所有权

- [x] 3.1 在 `backend/` 先建立局部治理检查的失败场景，覆盖缺少入口路由、`backend-conventions.md`、`database-conventions.md`、Java/MySQL Skills、锁记录、JPA 排除或 Flyway/参数安全 Rule 时失败，并运行检查确认 RED。
- [x] 3.2 精简 `backend/AGENTS.md`，创建 `backend/rules/backend-conventions.md`，使用稳定后端 Rule ID 迁移 Java/Spring Boot、模块化单体、依赖方向、接口实现边界、安全、事务、日志和测试规则，并明确独立 clone 与完整 AIWorkSpace 的契约变更边界。
- [x] 3.3 创建 `backend/rules/database-conventions.md`，使用稳定数据库 Rule ID 迁移 MyBatis-Plus、Flyway-only、MySQL 8.4、`#{}`/`${}`、schema/索引证据、事务锁、`EXPLAIN ANALYZE` 和破坏性操作审批规则，确认与现有主规格逐项对应。
- [x] 3.4 使用可追踪方式把 `java-springboot` 与 `mysql` 迁入 `backend/.agents/skills/`，建立后端本地锁与批准清单，复核第三方内容和参考文件未被项目规则修改，并确认主仓库不再拥有第二份规范源。
- [x] 3.5 更新 `backend/README.md`、`backend/docs/architecture.md` 和必要的薄工具入口，运行后端局部治理检查、`git diff --check` 和 `./mvnw -Dtest=ArchitectureRulesTests test`；若只移动文档和 Skill 且架构源码未变，记录不运行完整 build 的边界。

## 4. 精简主仓库入口并重构 Harness

- [x] 4.1 创建根级 `rules/README.md`、`workflow.md`、`repository-boundaries.md`、`git-safety.md`、`quality-gates.md` 和 `documentation.md`，登记作用域、稳定 Rule ID、加载路由和三个仓库的规则所有权，逐项完成旧根规则到新 Rule 的迁移对照。
- [x] 4.2 将根 `AGENTS.md` 精简为跨仓库薄入口，只保留统一事实优先级、OpenSpec 门禁、仓库/权限边界、Rules/Skills 路由和最小命令入口；删除已由根 Rules 或子仓库 conventions 承载的重复正文。
- [x] 4.3 按兼容性探针结果清理主仓库 `.agents/skills/` 的应用专属 Skills，以及确认不必要的 `.codex/skills`、`.claude/skills`、`.agents/skills/source-command-opsx-*`；对仍需保留的工具适配器建立声明清单和一致性校验。
- [x] 4.4 重构 `scripts/check-harness.sh`，校验文件、链接、Rule ID、Skill 所有权/来源/哈希和适配器清单，移除对完整中文原句和固定重复目录数量的断言；运行第 1.3 的失败夹具和真实 Harness，确认错误均可定位。
- [x] 4.5 更新根 `README.md`、`CLAUDE.md`、`skills-lock.json`、`openspec/config.yaml` 和相关文档，使其只描述真实存在的三层结构、Skill 所有权、生成命令和完整工作区边界。

## 5. 跨仓库验证与规格一致性

- [x] 5.1 从根目录和两个 submodule 分别执行入口到 Rules/Skills 的链接解析、Rule ID 唯一性、锁文件哈希和重复规范源检查，并手工抽查前端、Java、数据库、纯文档和跨仓库任务各自只加载相关文件。
- [x] 5.2 运行 `bash -n scripts/check-harness.sh`、`./scripts/check-harness.sh`、三个仓库的 `git diff --check`、后端架构测试和固定版本 `@fission-ai/openspec@1.6.0 validate --all --strict`，记录实际结果与未验证的 Claude Code 能力；不以未执行的 build 或工具探针声称兼容。
- [x] 5.3 复核主仓库只包含 OpenSpec artifacts 和根级治理修改，前端/后端改动各自在对应仓库中，业务源码、API、schema 与运行时依赖未发生无关变化；同步本 change 的 tasks、设计和 delta specs 中由实现证据揭示的修正。

## 6. 授权后的三仓库交付

- [x] 6.1 在用户明确授权后，分别在 `frontend/` 和 `backend/` 的明确分支仅暂存本 change 文件，复核 staged diff 后提交；未经推送授权不得 push。
- [x] 6.2 在用户明确授权推送后，先推送前端和后端提交，并使用远端引用核验两个 SHA 可达；任一子仓库不可达时不得更新主仓库 gitlink。
- [x] 6.3 子仓库远端可达后更新主仓库 frontend/backend gitlink，重新运行 Harness 与 OpenSpec strict validate；仅在用户再次明确授权后提交或推送主仓库。

## 7. 修正为 Codex-first 治理目录

- [x] 7.1 根据用户纠正修订 proposal、design、delta specs 和 tasks，明确每个仓库以 `.codex/agents`、`.codex/rules`、`.codex/skills` 为唯一治理三层，根 `AGENTS.md` 只作为 Codex 自动入口。
- [x] 7.2 将根、前端和后端现有 Rules、Skills、锁文件迁入各自 `.codex/`，补充作用域明确的 Agent 文件，并更新所有入口、README、架构文档和 OpenSpec context 引用。
- [x] 7.3 删除项目内 `.agents/`、`.claude/`、根与前端 `CLAUDE.md`，把生成清单改成 Codex-only，并让治理检查拒绝这些兼容目录重新出现。
- [x] 7.4 重新执行三仓库治理检查、脚本语法、`git diff --check`、Harness、后端架构测试与 OpenSpec strict validate；确认没有业务源码、schema 或运行时依赖变化，且不运行无关 build。

## 8. 此前完成的过渡状态：集中根 Rules 与 Skills 并取消 Agent 文件

> 本节记录已经执行并验证过的过渡状态。用户随后确认恢复根项目级 custom agents，当前目标与后续工作以第 9 节为准。

- [x] 8.1 根据用户最终目录要求修订 proposal、design、delta specs 和 tasks，明确只有根 `.codex/rules` 与 `.codex/skills` 是规范源，三个 `AGENTS.md` 只负责入口，不保留 `.codex/agents`。
- [x] 8.2 将前端、后端和数据库 Rules 及 React、Java、MySQL Skills 移到根 `.codex`，把三个应用 Skill 锁记录合并到根 `.codex/skills-lock.json`。
- [x] 8.3 删除根 `.codex/agents`、`frontend/.codex` 和 `backend/.codex`，更新三个入口、README、架构文档和治理脚本，明确子仓库独立 clone 不再具备完整治理能力。
- [x] 8.4 运行三仓库治理检查、脚本语法、Harness、三仓库 `git diff --check`、后端架构测试和 OpenSpec strict validate，确认集中结构、哈希、禁止目录和业务零影响。

## 9. 建立六角色 Codex 开发团队

- [x] 9.1 根据用户确认修订 proposal、design、`agent-skill-rule-governance` delta spec 和 tasks，明确允许根 `.codex/agents`、六角色交付接口、七部分角色合同、真实 Skill/Rule 引用、Tools 授权和中文输出约定。
- [x] 9.2 先扩展 `scripts/check-agent-governance.sh` 与必要测试夹具，使其要求 `.codex/agents/README.md` 和六个 TOML，校验 TOML 可解析、官方必填字段、唯一名称、七个正文部分、引用存在、允许字段和 sandbox 边界；在角色文件尚未创建时运行并确认 RED。
- [x] 9.3 创建 `.codex/agents/product_manager.toml`、`interaction_designer.toml`、`frontend_engineer.toml`、`backend_engineer.toml`、`qa_engineer.toml`、`experience_reviewer.toml` 及 `README.md`，逐个写明职责、输入、输出格式、限制、Skills、Rules、Tools 授权、输出语言和统一完成报告；不固定模型，体验角色使用只读 sandbox。
- [x] 9.4 更新 `.codex/manifest.json`、根 `AGENTS.md`、`.codex/rules/README.md`、根 `README.md`、`openspec/config.yaml` 和 Harness 路由，允许并登记根 custom agents，同时继续拒绝子仓库 `.codex` 与其他工具兼容目录。
- [x] 9.5 使用非法 TOML、缺字段、重名、缺角色章节、虚假 Skill/Rule、越权 sandbox 和子仓库重复 Agent 等夹具验证治理检查能准确失败，再运行真实治理检查确认六角色配置通过。
- [x] 9.6 运行 `bash -n scripts/check-agent-governance.sh`、`bash -n scripts/check-harness.sh`、`./scripts/check-agent-governance.sh`、`./scripts/check-harness.sh`、`git diff --check` 和 OpenSpec strict validate；记录本变更未修改业务源码且未运行无关前后端 build。

## 10. 增加只读 Spec 合规审查角色

- [x] 10.1 根据用户确认修订 proposal、design、`agent-skill-rule-governance` delta spec 和 tasks，将当前团队扩展为七角色，并明确 `spec_reviewer` 与 QA、体验走查的职责差异、双向对账合同、精确覆盖率、Action Items 和只读边界。
- [x] 10.2 先扩展 custom agent 校验与 Harness 使其要求 `spec_reviewer.toml` 且只读，在文件尚未创建时取得 RED；随后创建角色文件并更新 Agent 索引、Manifest、根入口、README 与 OpenSpec context。
- [x] 10.3 增加 Spec Reviewer 缺失、sandbox 越权和合同章节缺失夹具，运行正式 Agent 校验、全部失败夹具、治理检查、Harness、三仓库 `git diff --check` 和 OpenSpec strict validate；不修改业务源码、不运行无关 build、不执行 commit 或 push。
