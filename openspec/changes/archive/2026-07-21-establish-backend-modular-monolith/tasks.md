## 1. 建立后端变更基线

- [x] 1.1 在主仓库及 `frontend/`、`backend/` 分别记录 `git status --short --branch`，在主仓库记录 `git submodule status`，确认只修改本 change 和目标后端 submodule，且后端位于可提交的明确分支。
- [x] 1.2 在 `backend/` 运行现有 `./mvnw test`，确认健康检查、MyBatis-Plus 基线和 AI 默认关闭测试在架构调整前通过；若失败，先记录并处理基线问题，不把既有失败归因于本变更。

## 2. 先建立失败的架构门禁

- [x] 2.1 核对兼容 Java 21 与当前 JUnit 5 的 ArchUnit 版本，在 `backend/pom.xml` 仅增加 test scope 依赖；不得增加 Spring Data JPA、Spring Modulith 或运行时架构依赖。
- [x] 2.2 新增 `backend/src/test/java/com/heness/project/architecture/ArchitectureRulesTests.java`，覆盖层次依赖、跨模块入口、Controller 与 Mapper/`ChatModel` 隔离、Domain 框架隔离、循环依赖及非 JPA 约束。
- [x] 2.3 在移动现有 AI 配置前运行架构测试，确认测试因 `com.heness.project.config.ai` 未归入 `assistant.infrastructure` 等目标归属规则而以正确原因失败，并保留可定位的失败输出。

## 3. 建立模块边界并恢复测试

- [x] 3.1 在 `backend/src/main/java/com/heness/project/` 下为 `account`、`guide`、`assistant`、`community`、`support`、`moderation`、`notification` 和 `media` 新增顶层 `package-info.java`，分别记录职责与禁止职责；不批量创建空 Controller、Service、接口或实现类。
- [x] 3.2 将 `backend/src/main/java/com/heness/project/config/ai/AiConfiguration.java` 和 `AiProperties.java` 移入 `assistant/infrastructure/ai/`，同步移动 `AiConfigurationTests.java`，保持 `app.ai` 配置前缀、启用条件、缺失配置失败和默认不创建 `ChatModel` 的行为不变。
- [x] 3.3 完善架构规则对 `api → application → domain`、基础设施端口、跨模块仅访问应用契约及 `shared` 禁止业务类型的检查，运行目标架构测试确认由 RED 恢复为 GREEN。

## 4. 固化独立后端仓库的开发上下文

- [x] 4.1 新增 `backend/AGENTS.md`，记录后端事实优先级、模块地图、四类职责、跨模块依赖、MyBatis-Plus/Flyway、Spring AI、安全、测试和中文文档约束，并声明与主仓库根级规则共同生效。
- [x] 4.2 新增 `backend/docs/architecture.md`，用中文说明模块职责表、目录模板、依赖图、跨模块示例、资源路径、测试分层、禁止模式和未来拆分触发条件。
- [x] 4.3 更新 `backend/README.md`，链接架构文档和局部 `AGENTS.md`，说明新增代码如何选择模块以及运行架构测试和完整测试。
- [x] 4.4 先确认 `scripts/check-harness.sh` 因旧 `config/ai` 必要路径而失败，再更新门禁以检查新的 AI 基础设施路径、后端局部规则、架构文档、ArchUnit 依赖和架构测试入口。

## 5. 后端验证与主仓库验收

- [x] 5.1 在 `backend/` 运行目标架构测试和完整 `./mvnw test`，确认 `/api/health`、默认数据库关闭、默认 AI 关闭及 AI 配置失败路径没有回归，并运行 `git diff --check`。
- [x] 5.2 回到主仓库运行固定版本 OpenSpec strict validate、`./scripts/check-harness.sh` 和 `git diff --check`，复核 `frontend/` 工作树及 gitlink 未变化，并记录所有实际结果和未验证项。
- [x] 5.3 评审后端实际差异，确认没有业务实体、API、Flyway migration、JPA、消息队列、空层次样板或无关格式化进入本变更。

## 6. 经授权后完成跨仓库版本编排

- [x] 6.1 仅在用户明确授权提交与推送后，在 `backend/` 的明确工作分支提交并推送本变更，确认提交可从 `https://github.com/LingKim/my-harness-backtend` 远端到达。
- [x] 6.2 回到主仓库更新 `backend` gitlink，同步 `backend-modular-monolith` delta spec 到主规格，重新运行 OpenSpec strict validate 与 `./scripts/check-harness.sh`，再经用户明确授权提交并推送主仓库；不得修改或提交 `frontend` gitlink。
