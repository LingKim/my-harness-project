## Context

主仓库通过根级 `AGENTS.md` 和项目级 `.agents/skills/` 统一三个仓库的 AI Coding 行为。当前前端已经采用项目级 Skill、`skills-lock.json` 和 Harness 批准清单，但 `backend/` 的 Java/Spring Boot 开发仍只依赖少量静态规则，缺少可复用的最佳实践 Skill。

Skills 生态搜索显示，直接命中 Google Java Style 的候选 `testdino-hq/google-styleguides-skills@java` 只有 27 次安装、5 stars，且其示例与宣称的缩进规则自相矛盾，不适合作为强制基线。`github/awesome-copilot@java-springboot` 来自 GitHub 官方公开仓库，安装量和仓库信誉更高，覆盖 Spring Boot 项目结构、依赖注入、配置、Web、Service、事务、日志、测试与安全；但其中数据层示例默认采用 Spring Data JPA，与本项目 MyBatis-Plus 技术栈冲突。

## Goals / Non-Goals

**Goals:**

- 将 `java-springboot` 作为可版本化、可追踪的项目级后端最佳实践 Skill。
- 让涉及 `backend/` 的 Java/Spring Boot 编写、评审和重构任务明确触发该 Skill。
- 通过项目事实优先级和显式排除项，阻止 JPA 等冲突建议进入当前代码库。
- 扩展现有 Harness 批准清单，校验 Skill 来源、文件、锁记录和规则引用。

**Non-Goals:**

- 不把低信誉的第三方 Google Java Style Skill 引入项目。
- 不在本次变更中增加 Spotless、google-java-format、Checkstyle 或修改 Java 格式。
- 不修改 backend submodule、业务代码、依赖、测试或 gitlink。
- 不改变 MyBatis-Plus、Flyway、Java 21、Spring Boot 4.1 或 Spring AI 2.0 技术选型。

## Decisions

### 1. 采用 GitHub 官方仓库的 `java-springboot`

使用 `github/awesome-copilot@java-springboot`，因为其来源、安装量和覆盖范围优于其他候选，且内容以 Spring Boot 工程实践为中心。

备选方案是 `testdino-hq/google-styleguides-skills@java`。该 Skill 来源不是 Google 官方、采用量低且内容存在内部矛盾，因此拒绝采用。Google Java Style 的格式化强制将来应通过官方 formatter 或成熟 Maven 插件单独提案，不能借低质量 Skill 替代。

### 2. 项目级安装并扩展批准清单

使用 Skills CLI 仅安装 `java-springboot` 到 `.agents/skills/java-springboot/`，避免把 `github/awesome-copilot` 仓库中的其他 Skills 一并引入。`skills-lock.json` 记录来源与哈希，`scripts/check-harness.sh` 的 `approved_skill_names` 增加该名称并校验对应元数据。

备选方案是全局安装，但无法保证其他开发者、CI 或代理得到同一内容，因此不采用。

### 3. 根级规则强制触发并覆盖 JPA 建议

根级 `AGENTS.md` 增加后端 Skill 触发范围和使用方法。事实优先级固定为：当前 OpenSpec 与活动 change → `backend/` 局部规则、实际依赖、源码和测试 → Java 21 与 Spring Boot 4.1 当前文档 → `java-springboot` 通用建议 → 代理既有知识。

Skill 中涉及 Spring Data JPA、JPA entity、`JpaRepository`、`CrudRepository`、JPA Criteria API 和 `@DataJpaTest` 的内容默认不适用。本项目数据访问继续使用 MyBatis-Plus，数据库结构继续只由 Flyway 管理。若未来需要 JPA，必须通过独立 change 修改技术栈规格。

### 4. Harness 只验证可确定的接入契约

Harness 检查 Skill 入口文件、锁记录、批准清单、GitHub 来源、哈希格式和 `AGENTS.md` 引用，并验证 Java Skill 缺失或出现未批准 Skill 时失败。它不把 Skill 的每条自然语言建议转化为静态规则，也不替代后端测试。

## Risks / Trade-offs

- [Skill 是社区贡献内容而非 Spring 官方规范] → GitHub 官方仓库提供来源信誉，但项目规则和当前版本文档始终优先。
- [JPA 建议误导实现] → 在 `AGENTS.md` 和 Harness 引用中显式列出禁止采用的 JPA 模式与当前 MyBatis-Plus/Flyway 契约。
- [Spring Boot 版本差异] → 当前 Spring Boot 4.1 的依赖、测试 starter、实际 API 和官方文档高于 Skill 示例。
- [Skill 更新导致内容漂移] → 锁定哈希，更新必须显式执行、审查差异并重新验证。

## Migration Plan

1. 使用精确 Skill 标识安装 `java-springboot`，复核新增文件和 `skills-lock.json`，清理任何非目标 Skill。
2. 先扩展 Harness 对批准清单、Java Skill 元数据和 `AGENTS.md` 引用的断言，并在规则尚未加入时得到预期失败。
3. 修改根级 `AGENTS.md`，加入触发范围、事实优先级和 JPA 冲突覆盖，恢复 Harness 通过。
4. 验证两个 submodule 未变化，运行 Shell 语法、Harness、差异和 OpenSpec 严格检查；本变更不运行无关 build。

回滚时从批准清单、锁文件、根级规则和项目级 Skills 目录移除 Java Skill 即可，不涉及应用代码或数据迁移。

## Open Questions

无。Google Java Style 的机器格式化工具是否引入，将在有明确格式化需求时单独提案。
