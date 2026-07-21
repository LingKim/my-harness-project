## Why

当前项目尚未把 Java 21 与 Spring Boot 后端最佳实践纳入项目级 Skill，不同 AI 代理在编写、评审和重构 `backend/` 代码时可能采用不一致的分层、依赖注入、配置、事务、日志、测试和安全模式。引入经过审查的 GitHub 官方仓库 Skill，并以项目当前技术栈覆盖其通用建议，可以复用成熟规则且避免误引入 JPA 等冲突方案。

## What Changes

- 在主仓库项目级 Skills 目录引入 `github/awesome-copilot@java-springboot`，作为 Java/Spring Boot 编写、评审和重构任务的通用最佳实践来源。
- 在根目录 `AGENTS.md` 中明确触发范围：涉及 `backend/` 的 Java、Spring Boot、Web、配置、事务、日志、测试或安全任务必须使用 `java-springboot`。
- 明确事实优先级：OpenSpec、`backend/` 局部规则、Java 21、Spring Boot 4.1 本地依赖与当前项目代码高于 Skill 的通用建议。
- 明确冲突覆盖：项目继续使用 MyBatis-Plus 3.5.17 与 Flyway，Skill 中的 Spring Data JPA、`JpaRepository`、`@DataJpaTest` 和 JPA entity 建议不得应用，除非未来独立 change 明确改变技术栈。
- 扩展 `skills-lock.json` 与 Harness 批准清单，校验 Java Skill 的来源、路径、哈希、入口文件和 `AGENTS.md` 引用，同时继续拒绝未批准 Skill。
- 目标：为后端 AI 开发建立一致、可追踪、可更新的 Java/Spring Boot 最佳实践基线。
- 非目标：本变更不批量重构后端代码，不修改 backend submodule 或 gitlink，不新增 JPA、Lombok、Checkstyle、Spotless 或其他运行时/构建依赖，也不处理 MySQL 规范。
- 验收结果：项目检出后可读取目标 Skill，锁文件和批准清单包含正确记录，根级规则能够强制触发并阻止 JPA 冲突建议，Harness 对缺失、错误来源、未批准项或引用缺失给出失败结果。
- 主要风险：Skill 面向通用 Spring Boot 项目，部分内容以 JPA 和旧版测试注解为例；通过项目技术栈优先级和显式排除清单降低风险。

## Capabilities

### New Capabilities

- `backend-java-best-practices-skill`: 规定项目如何引入、触发、约束、校验和更新 Java/Spring Boot 最佳实践 Skill。

### Modified Capabilities

无。

## Impact

- 主仓库：`.agents/skills/java-springboot/`、`skills-lock.json`、`AGENTS.md`、`scripts/check-harness.sh`。
- 后端 submodule：本变更不修改 `backend/` 内部文件或 gitlink，但后续针对该目录的 AI 编码任务会受到新增规则约束。
- 外部来源：`github/awesome-copilot@java-springboot`。
- API、运行时依赖、数据库结构与生产部署：无影响。
