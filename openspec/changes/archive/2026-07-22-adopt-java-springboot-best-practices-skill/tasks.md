## 1. 建立 Java Skill 项目级基线

- [x] 1.1 使用 Skills CLI 将精确标识 `github/awesome-copilot@java-springboot` 仅安装到 `.agents/skills/java-springboot/`，复核安装文件与 `skills-lock.json` 的来源、Skill 路径和内容哈希，并确认没有附带引入同仓库其他 Skill。
- [x] 1.2 记录安装前后的 `git status --short`、`git submodule status` 与两个 submodule 工作树状态，确认本变更不修改 `frontend/`、`backend/` 内部文件或主仓库 gitlink。

## 2. 先建立失败门禁

- [x] 2.1 先修改 `scripts/check-harness.sh`，将 `java-springboot` 加入显式批准清单，并增加对 `.agents/skills/java-springboot/SKILL.md`、锁记录来源 `github/awesome-copilot`、Skill 路径、有效哈希和根级规则引用的断言。
- [x] 2.2 在根级规则尚未加入时运行 `bash -n scripts/check-harness.sh` 与 `./scripts/check-harness.sh`，确认 Harness 因缺失 Java Skill 触发规则或 JPA 排除规则而按预期失败，并保留可定位的失败信息。

## 3. 启用后端最佳实践规则

- [x] 3.1 修改根目录 `AGENTS.md`，规定涉及 `backend/` 的 Java、Spring Boot、Web、配置、事务、日志、测试或安全的编写、评审和重构任务必须完整读取并使用 `java-springboot`。
- [x] 3.2 在 `AGENTS.md` 明确事实优先级和冲突覆盖：当前 OpenSpec、`backend/` 局部规则、实际依赖、源码与测试以及 Java 21、Spring Boot 4.1 当前文档高于通用 Skill；数据访问继续使用 MyBatis-Plus 3.5.17，数据库结构只由 Flyway 管理，默认禁止应用 Spring Data JPA、JPA entity、`JpaRepository`、`CrudRepository`、Criteria API、`@DataJpaTest` 或仅因 Skill 新增相关依赖。

## 4. 失败场景与最终验证

- [x] 4.1 使用可恢复的临时改动分别验证：移除 Java Skill 根级引用时 Harness 失败，以及向 `skills-lock.json` 加入未批准 Skill 时 Harness 失败；每次验证后立即恢复真实文件并确认没有遗留测试数据。
- [x] 4.2 运行 `bash -n scripts/check-harness.sh`、`./scripts/check-harness.sh`、`git diff --check` 和固定版本 OpenSpec strict validate，确认 Java Skill 接入、批准清单、JPA 排除规则和现有前端 Skill 门禁全部通过；本变更不运行无关 build。
- [x] 4.3 最终复核主仓库实际差异、两个 submodule 状态和 gitlink，交付说明中记录 Skill 来源、适用范围、版本冲突处理、未引入 Google Java Style Skill 的原因及后续显式更新方式；未经用户授权不提交或推送。
