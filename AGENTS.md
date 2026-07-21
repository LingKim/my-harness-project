# AI Coding 项目约定

本仓库是 AIWorkSpace 主仓库，本文件是三个 Git 仓库共同协作时的 AI Coding Harness 统一入口。无论使用 Codex、Claude Code 或其他代理，都必须先遵守这里的约定，再读取具体工具生成的技能和目标 submodule 内的局部规则。

## 1. 核心原则

1. 事实优先：先读代码、配置、测试和真实输出，不根据猜测修改。
2. 规格先行：非平凡变更必须先形成 OpenSpec change，再开始实现。
3. 小步交付：把任务拆成可独立验证的小步骤，避免一次性大改。
4. 测试驱动：能测试的行为遵循 RED → GREEN → REFACTOR。
5. 系统调试：先复现、收集证据和定位根因，再修改代码。
6. 完成前验证：没有新的验证输出，不得声称“已修复”或“已完成”。
7. 控制复杂度：坚持 YAGNI、DRY 和最小可行改动，不做未被需求支撑的扩展。
8. 中文文档：仓库内新建或修改的人类可读文档默认使用中文，包括 README、OpenSpec artifacts、设计、计划、操作说明和代码注释；代码标识符、命令、文件路径、协议字段、依赖名称及没有稳定中文译名的技术术语保持原文。第三方工具自动生成且会被其更新命令覆盖的文件不强制翻译。

## 2. 标准工作流

### A. 探索

- 需求不清楚、方案存在明显分歧或风险未知时，使用 `/opsx:explore`。
- 先说明目标、用户价值、约束、非目标和验收口径。
- 不在探索阶段写业务代码。

### B. 提案

- 新功能、行为变化、架构调整、跨文件修复等非平凡工作，使用 `/opsx:propose <change-name>`。
- 提案必须包含 proposal、specs、design 和 tasks。
- 在规格得到用户确认前，不进入实现。
- 纯文案、注释、机械格式化等无行为变化的小改动可直接处理，但仍需验证。

### C. 实现

- 使用 `/opsx:apply` 按 tasks 顺序推进。
- 每个任务先明确预期行为和验证命令。
- 能自动化测试时先看到测试以正确原因失败，再写最少实现使其通过。
- 每完成一个任务，立即更新对应 tasks 状态，不把状态留在聊天记录里。
- 如果实现揭示规格错误，先更新 OpenSpec artifacts，再继续编码。

### D. 验证与评审

- 运行与变更风险相称的测试、静态检查或真实场景验证。
- 自查规格符合性、回归风险、安全性、可维护性和无关改动。
- 报告实际执行的命令、结果和未验证项；禁止用“应该可以”代替证据。

### E. 归档

- 只有实现完成、验证通过且规格同步后，才使用 `/opsx:archive`。
- 归档前检查 change 中没有未完成任务，必要时先 `/opsx:sync`。

## 3. AIWorkSpace 仓库边界

AIWorkSpace 由三个独立 Git 仓库组成：

- 主仓库：`https://github.com/LingKim/my-harness-project`，负责根级 Harness、OpenSpec、跨项目文档、环境变量模板、Docker Compose 和 submodule 版本编排。
- 前端 submodule：`frontend/`，远端为 `https://github.com/LingKim/my-harness-frontend`，负责 Next.js 前端源码、依赖、测试和前端文档。
- 后端 submodule：`backend/`，远端为 `https://github.com/LingKim/my-harness-backtend`，负责 Spring Boot 后端源码、依赖、测试、数据库迁移和后端文档。远端名称中的 `backtend` 是既定地址，不得擅自更正。

操作 `frontend/` 或 `backend/` 时必须遵守以下规则：

1. 先进入目标 submodule，执行 `git status --short --branch` 并读取该仓库自己的 `AGENTS.md`、`README.md` 或等价规则文件；局部规则与根级规则同时生效。
2. submodule 可能处于 detached HEAD。需要提交时必须先切换到明确的工作分支，不得把提交遗留在无法从远端分支到达的位置。
3. 前端和后端内部文件只能提交到各自仓库；主仓库只记录模式 `160000` 的 gitlink，不直接跟踪应用文件。
4. 更新顺序固定为：在子仓库完成修改与验证 → 提交并推送子仓库 → 回到主仓库更新 gitlink → 验证远端可达 → 提交主仓库。
5. 未经用户明确要求，不得提交或推送任何仓库；一次授权只覆盖明确说明的仓库和变更范围。
6. 跨仓库 OpenSpec change 的 tasks 必须分别列出每个受影响仓库的实现、验证、提交和 gitlink 更新，不能用一个笼统任务代替。

## 4. Harness 上下文加载顺序

开始任务时按顺序读取：

1. `AGENTS.md`（本文件）
2. `README.md`
3. `openspec/config.yaml`
4. `openspec/specs/` 中与任务相关的当前规格
5. `openspec/changes/` 中正在进行的变更
6. 如果任务涉及 submodule，读取目标目录内的 `AGENTS.md`、`README.md` 和仓库状态
7. 与任务直接相关的源代码、测试和运行配置

只加载与当前任务有关的内容，避免用大量无关文件污染上下文。

### React / Next.js 最佳实践 Skill

- 凡涉及 `frontend/` 内 React 组件、Next.js 页面、数据获取、Server Component、Client Component、Server Action、bundle、渲染或性能的编写、评审和重构，必须使用 `vercel-react-best-practices`。
- 使用该 Skill 时，先完整读取 `.agents/skills/vercel-react-best-practices/SKILL.md`，再按任务需要读取其 `rules/` 中直接相关的规则文件；不得为了节省上下文而跳过 Skill 入口说明。
- 事实优先级固定为：当前 `openspec/specs/` 与已确认的活动 change → `frontend/AGENTS.md` 和当前安装版本的 `frontend/node_modules/next/dist/docs/` → `vercel-react-best-practices` 通用建议 → 代理既有知识。
- 如果 Skill 建议与当前 Next.js 16 本地文档或前端局部规则冲突，采用当前版本文档或局部规则，并在交付说明中指出冲突；不得用通用 Skill 覆盖已验证的当前版本行为。
- Skill 只提供编码与评审基线，不替代 `pnpm lint`、相关自动化测试和真实运行验证，也不得仅因 Skill 提到某个库就在没有需求时新增依赖。
- 更新项目级 Skill 必须显式执行 Skills CLI、复核文件差异与 `skills-lock.json` 来源及哈希，并重新运行 `./scripts/check-harness.sh`；不得静默跟随外部仓库最新内容。
- `skills-lock.json` 只能包含通过独立 OpenSpec change 明确批准、并登记在 `scripts/check-harness.sh` 批准清单中的项目级 Skill；新增或移除 Skill 时必须同步更新来源校验和失败场景，不得把临时安装结果直接视为项目规范。

### Java / Spring Boot 最佳实践 Skill

- 凡涉及 `backend/` 内 Java、Spring Boot、Web、配置、事务、日志、测试或安全的编写、评审和重构，必须使用 `java-springboot`。
- 使用该 Skill 时，先完整读取 `.agents/skills/java-springboot/SKILL.md`，再应用与当前任务直接相关且不与项目事实冲突的规则；不得只根据 Skill 名称推测其内容。
- 事实优先级固定为：当前 `openspec/specs/` 与已确认的活动 change → `backend/` 局部规则、实际依赖、源码与测试 → Java 21 和 Spring Boot 4.1 当前官方文档 → `java-springboot` 通用建议 → 代理既有知识。
- 如果 Skill 的 starter、注解、API、测试方式或其他示例与当前 Spring Boot 4.1 依赖、源码、测试或官方文档冲突，采用当前项目事实，并在交付说明中指出冲突。
- 本项目数据访问继续使用 MyBatis-Plus 3.5.17，数据库结构继续只由 Flyway 管理；`java-springboot` 中涉及 Spring Data JPA、JPA entity、`JpaRepository`、`CrudRepository`、JPA Criteria API 和 `@DataJpaTest` 的建议默认不适用。
- 不得仅因 Skill 建议而新增 JPA、Lombok 或其他依赖，也不得创建 JPA entity、repository、starter 或 JPA 专用测试；只有已确认的独立 OpenSpec change 明确修改技术栈规格时才可改变该约束。
- Skill 只提供编码与评审基线，不替代 `./mvnw test`、静态检查和真实运行验证；针对具体变更仍须执行与风险相称的验证。

### MySQL 数据库与 SQL 最佳实践 Skill

- 凡涉及 `compose.yaml` 中的 MySQL 配置、`backend/src/main/resources/db/migration/`、MyBatis XML 或注解 SQL、schema、表、字段类型、约束、索引、查询、事务锁、连接或数据库运维的编写、评审和重构，必须使用 `mysql`。
- 使用该 Skill 时，先完整读取 `.agents/skills/mysql/SKILL.md`，再按任务需要读取 `.agents/skills/mysql/references/` 中直接相关的参考文件；不得一次性加载全部参考文件，也不得只根据入口摘要代替专项规则。
- 事实优先级固定为：当前 `openspec/specs/` 与已确认的活动 change → `backend/` 局部规则、实际 schema、SQL、依赖与测试 → MySQL 8.4 当前官方文档和安全环境中的执行证据 → `mysql` 通用建议 → 代理既有知识。
- 当前项目继续使用 Docker Compose MySQL 8.4 与 InnoDB，并通过 MyBatis-Plus 访问数据；忽略 Skill 的 PlanetScale 托管推荐和 Vitess 特有假设，不得仅因 Skill 建议改变数据库托管或运行架构。
- `BIGINT UNSIGNED AUTO_INCREMENT`、`utf8mb4_0900_ai_ci`、`DATETIME`、分区阈值、隔离级别和在线 DDL 算法都只能作为候选；必须根据业务标识、比较与时区语义、实际数据量、并发模型、MySQL 8.4 官方行为和真实变更风险逐项决定。
- 数据库结构继续只由 Flyway migration 管理；新增或修改表、字段、约束和索引必须创建新的受版本管理 migration，不得通过 JPA/Hibernate 自动建表、启动脚本或未受版本管理的手工 DDL 绕过 Flyway。
- 数据库设计必须说明主键、数据类型、长度、NULL 语义、默认值、约束、字符比较语义和索引依据；应用数据查询默认显式列出所需列，不得把无业务证据的索引、反范式设计或 `SELECT *` 当作通用优化。
- MyBatis SQL 的业务值必须使用 `#{}` 参数绑定；`${}` 只能用于 JDBC 无法参数化的标识符或受控 SQL 片段，输入必须来自服务端封闭白名单，原始或间接用户输入不得进入 `${}`，也不得通过字符串拼接构造 SQL。
- 索引与性能修改必须先收集查询模式、数据规模和 `EXPLAIN` 等证据；`EXPLAIN ANALYZE` 会实际执行 SQL，只能在确认安全的非生产环境用于只读语句，禁止用它直接分析写入或破坏性语句。
- 事务必须保持短小，并保持一致的加锁顺序；网络、文件或其他外部 I/O 不得放在数据库事务内。隔离级别、锁与死锁重试策略必须基于已确认的并发行为，不能把 Skill 默认值直接写入项目。
- 破坏性数据库操作必须在执行前获得用户明确批准，包括 `DROP`、`TRUNCATE`、无条件 `DELETE`/`UPDATE`、不可逆字段或索引删除；执行前必须解析精确目标，说明影响、备份或恢复方式、兼容发布、回滚和部署后验证方案。
- Skill 只提供设计与评审基线，不替代 Flyway migration 测试、数据库集成测试、执行计划、锁指标或真实环境验证；更新 Skill 必须显式执行 Skills CLI、审查差异和锁文件哈希，并重新运行 Harness。

## 5. 计划与执行纪律

- 计划中的每个任务应足够小，通常能在一次短迭代内完成。
- 任务描述必须包含精确文件位置、期望结果和验证方式。
- 多个互不依赖的任务才可并行；共享同一文件或有前后依赖的任务必须串行。
- 使用子代理时，每个子代理只承担一个边界明确的任务，主代理负责整体验收。
- Git worktree 仅在仓库已有基线提交后使用；一个变更对应一个分支或 worktree。
- 不擅自提交、推送、合并、删除分支或执行破坏性操作。

## 6. 质量门禁

完成一个变更至少满足：

- 规格中的验收场景都有对应实现。
- 新增或变更行为有自动化测试；无法自动化时说明原因并记录手工验证。
- 测试确实运行且通过，而不是只阅读代码。
- 没有遗留调试代码、占位实现、静默吞错或无关格式化。
- 文档、配置和实现保持一致。
- `./scripts/check-harness.sh` 通过。

## 7. 项目命令

```bash
# 检查 Harness / OpenSpec 基础结构
./scripts/check-harness.sh

# 一键启动前端和后端
make dev

# 普通 clone 后初始化前后端 submodule
git submodule update --init --recursive

# 检查主仓库记录的 submodule 提交
git submodule status

# 前端检查与测试
cd frontend && pnpm lint && pnpm test

# 后端测试
cd backend && ./mvnw test

# 验证 MySQL Compose 配置
docker compose --env-file .env.example config

# OpenSpec CLI（未全局安装时）
npx --yes --registry=https://registry.npmjs.org @fission-ai/openspec@1.6.0 status

# 项目升级 OpenSpec 后，刷新各 AI 工具指令
openspec update
```

项目采用由 `frontend/` 与 `backend/` 两个 Git submodule 组成的双工程结构。前端使用 Next.js 16、React 19、TypeScript 和 Tailwind CSS 4；后端使用 Java 21、Spring Boot 4.1、MyBatis-Plus 3.5.17、MySQL 8.4、Flyway 和 Spring AI 2。MyBatis-Plus 必须使用 Spring Boot 4 专用 starter；数据库结构仍只由 Flyway 管理。未经用户明确要求，修改代码后不运行 build，但必须运行与变更相关的测试或静态检查。
