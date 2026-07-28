# AIWorkSpace

这是一个基于 Harness Engineering、OpenSpec 和 Superpowers 方法论的 AI 全栈开发工作区。主仓库负责规格、AI Coding 规则与本地环境编排，前端和后端通过 Git submodule 引入并保持独立版本历史。

## 仓库组成

| 仓库 | 本地路径 | 职责 |
| --- | --- | --- |
| [my-harness-project](https://github.com/LingKim/my-harness-project) | `.` | AIWorkSpace 主仓库，负责 Harness、OpenSpec、Compose、环境模板和 submodule 版本 |
| [my-harness-frontend](https://github.com/LingKim/my-harness-frontend) | `frontend/` | Next.js 前端独立仓库 |
| [my-harness-backtend](https://github.com/LingKim/my-harness-backtend) | `backend/` | Spring Boot 后端独立仓库；`backtend` 是既定远端名称 |

## 技术栈

### 前端

- Next.js 16.2.10
- React 19.2.7
- TypeScript 5
- Tailwind CSS 4.3.3
- Vitest 4 + Testing Library
- pnpm 10

### 后端

- Java 21 LTS
- Spring Boot 4.1.0
- Spring AI 2.0.0
- MyBatis-Plus Spring Boot 4 Starter 3.5.17
- Flyway + MySQL Connector/J
- Maven Wrapper 3.9.16

### 本地基础设施

- MySQL 8.4
- Docker Compose

## 目录结构

```text
.
├── frontend/                   # my-harness-frontend submodule
├── backend/                    # my-harness-backtend submodule
├── .gitmodules                # submodule 路径与远端地址
├── compose.yaml                # MySQL 本地开发服务
├── .env.example                # 不含真实凭据的环境变量模板
├── AGENTS.md                   # Codex 自动发现的薄入口
├── .codex/                     # 集中的 Codex Agents、Rules、Skills 与治理清单
├── openspec/                   # 当前规格和变更 artifacts
├── docs/                       # 跨变更设计与计划
└── scripts/check-harness.sh    # 仓库结构自检
```

## 环境要求

- Node.js 22 或更高版本
- pnpm 10
- Java 21
- Docker Desktop 或兼容的 Docker Engine + Compose v2

本机当前验证环境为 Node.js 22.12.0、pnpm 10.13.1、Java 21.0.8、Maven 3.9.16 和 Docker Compose 2.40.3。

## 检出完整工作区

推荐在首次检出时直接初始化 submodule：

```bash
git clone --recurse-submodules https://github.com/LingKim/my-harness-project
cd my-harness-project
```

如果已经普通 clone 了主仓库，再执行：

```bash
git submodule update --init --recursive
```

确认两个 submodule 已落在主仓库记录的提交：

```bash
git submodule status
```

## 初始化本地环境

复制环境变量模板，并把占位密码替换为仅供本机使用的值：

```bash
cp .env.example .env
```

启动 MySQL：

```bash
docker compose up -d mysql
docker compose ps
```

停止服务：

```bash
docker compose down
```

只有明确需要删除本地数据库数据时，才执行 `docker compose down -v`。

## 一键启动前后端

在项目根目录执行以下任一命令，同时启动 Next.js 前端和 Spring Boot 后端：

```bash
make
# 或
make dev
```

脚本会在根目录 `.env` 存在时自动加载它；不存在时使用前后端默认配置。按 `Ctrl+C` 会同时停止两个进程。

也可以单独启动：

```bash
make frontend
make backend
```

查看全部 Make 命令：

```bash
make help
```

## 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

访问 [http://localhost:3000](http://localhost:3000)。前端只读取 `NEXT_PUBLIC_API_BASE_URL` 这一公开配置；数据库密码和 AI Key 不得放入前端环境文件。

前端验证命令：

```bash
cd frontend
pnpm lint
pnpm typecheck
pnpm test
```

## 启动后端

先在一个 shell 中加载根目录 `.env`，再启动后端：

```bash
cd backend
set -a
source ../.env
set +a
./mvnw spring-boot:run
```

后端端口默认为 `8080`：

- 应用健康检查：[http://localhost:8080/api/health](http://localhost:8080/api/health)
- Actuator 健康检查：[http://localhost:8080/actuator/health](http://localhost:8080/actuator/health)

后端验证命令：

```bash
cd backend
./mvnw test
```

## 数据库约定

- `DATABASE_ENABLED=false` 或未设置时，基础后端和测试不连接 MySQL。
- 本地完整运行时，从 `.env` 加载 `DATABASE_ENABLED=true` 和数据源变量。
- 数据库结构只通过 `backend/src/main/resources/db/migration/` 中的 Flyway 脚本修改。
- MyBatis-Plus XML 放在 `backend/src/main/resources/mapper/` 的业务子目录中。
- 常规业务持久化默认通过所属业务模块的 MyBatis-Plus Mapper/适配器完成；真实 Mapper 可以按需继承 `BaseMapper<T>`，但数据库结构仍只能由 Flyway 修改。
- 新增或实质修改的自定义 SQL 必须使用 Mapper XML；`BaseMapper<T>` 自动 CRUD 不重复编写 XML，存量注解 statement 在后续实质修改时迁入 XML。
- 直接使用 Spring JDBC 必须有已确认 design 依据，限定在所属模块 `infrastructure`，说明替代方案取舍并提供等价测试。
- 不使用 JPA/Hibernate 自动建表。

## OpenAI-compatible 配置

AI 默认关闭，不配置 API Key 也能启动基础后端：

```dotenv
AI_ENABLED=false
AI_BASE_URL=https://api.openai.com
AI_API_KEY=
AI_MODEL=gpt-4.1-mini
```

需要启用时，把 `AI_ENABLED` 改为 `true`，并提供当前供应商兼容的基础地址、API Key 和模型名称。配置缺失会在启动阶段明确失败。本次基线没有暴露模型调用接口，因此不会主动产生模型调用或费用。

## Agent、Rules、Skills 治理

项目以 Codex 为准，所有治理内容集中在主仓库根 `.codex/`：

- `AGENTS.md`：Codex 自动入口，只说明作用域、事实优先级、权限边界和任务路由。
- `.codex/agents/`：七个项目级研发角色及其职责、交付格式、限制和 Tools 授权。
- `.codex/rules/`：集中保存通用、前端、后端和数据库项目约束。
- `.codex/skills/`：集中保存 OpenSpec、React、Java 与 MySQL 任务方法。

其中 `java-springboot` 是与 ChinaMate Java 21、Spring Boot 4.1、模块化单体、MyBatis-Plus 和 Flyway 对齐的项目维护 Skill；Vercel React 与 MySQL Skills 保持第三方来源并由项目 Rules 提供覆盖和例外。

同一名开发者承担产品、交互、前端、后端、测试和验收时，统一从 [ChinaMate 单人全栈交付 Skill](.codex/skills/chinamate-fullstack-delivery/SKILL.md) 进入。它从 OpenSpec、Git、测试与 `evidence.md` 推导阶段，按任务选择最短安全路径，并把七个角色作为串行职责视角；不会建立第二套状态，也不会自动 commit、push、更新 gitlink 或归档。

配套入口：

- [Rule 控制矩阵](.codex/skills/chinamate-fullstack-delivery/references/control-matrix.md)：明确 Critical Rule 的责任、控制类型、阻断条件和证据位置。
- [验证 Profiles](.codex/skills/chinamate-fullstack-delivery/references/verification-profiles.md)：以固定参数数组运行根、前端或后端门禁，并生成脱敏的 machine manifest。
- [交付安全预检与清理复核](.codex/skills/chinamate-fullstack-delivery/references/verification-profiles.md#环境预检)：识别 worktree 依赖和 Java/Mockito 风险，要求分页等真实场景跨越边界两侧，并用声明式 cleanup manifest 只读证明临时数据库、端口、worktree、分支和路径零残留。
- [跨栈系统地图](docs/architecture/system-map.md)：以 `CURRENT`/`PLANNED` 区分真实路径与计划能力。
- [领域术语桥](docs/standards/domain-glossary.md)：把产品语言映射到工程含义和权威来源。

当前只维护上述轻量知识入口。只有单模块真实文件超过 50 个、同一定位问题重复三次、发生两次已确认地图漂移，或同一需求出现三个以上专用外部收料通道时，才另建 OpenSpec change 评估重型知识库。

项目只在根 `.codex/agents/` 维护 `product_manager`、`interaction_designer`、`frontend_engineer`、`backend_engineer`、`qa_engineer`、只读 `spec_reviewer` 与只读 `experience_reviewer`；不在子仓库复制 `.codex/`，也不维护 `.agents/`、`.claude/` 或 `CLAUDE.md`。登记清单见 [`.codex/manifest.json`](.codex/manifest.json)，角色索引见 [`.codex/agents/README.md`](.codex/agents/README.md)，规则索引见 [`.codex/rules/README.md`](.codex/rules/README.md)。

治理结构验证：

```bash
./scripts/check-agent-governance.sh
```

## OpenSpec 工作流

项目接口设计与开发前先阅读：

- [ChinaMate 接口开发规范](docs/standards/api-development-guidelines.md)

需求还不明确时：

```text
/opsx:explore
```

创建完整变更提案：

```text
/opsx:propose <change-name>
```

规格确认后实现：

```text
/opsx:apply
```

完成并验证后归档：

```text
/opsx:archive
```

业务功能、行为变化、跨仓库、API、数据库、安全、架构和治理行为 change 在自身根目录维护 `evidence.md`，使用 [OpenSpec Change 交付证据模板](docs/templates/openspec-change-evidence.md) 记录真实命令、QA、Spec Review、Experience Review、未验证项和归档建议。纯文案、机械格式化和只读探索可以豁免，但必须如实说明；完整原始日志和敏感信息不得写入证据。

跨仓库变更必须在根级 OpenSpec tasks 中分别记录前端、后端和主仓库工作。应用提交必须先推送到对应远端，再由主仓库更新 gitlink。

## 日常更新 submodule

拉取主仓库已经固定的新版本：

```bash
git pull
git submodule update --init --recursive
```

修改某个应用前，先进入对应目录并确认分支。新 clone 的 submodule 通常处于 detached HEAD，不能直接遗留提交：

```bash
cd frontend  # 或 backend
git status --short --branch
git switch main
git pull --ff-only
```

完成应用修改后，先在子仓库测试、提交并推送；然后回到主仓库记录新的 gitlink：

```bash
cd frontend
pnpm lint && pnpm test
git add -A
git commit
git push

cd ..
git add frontend
git commit
git push
```

后端遵循相同顺序，并把验证命令替换为 `./mvnw test`。未经明确授权，不执行上述提交或推送命令。

## Harness 自检

```bash
./scripts/check-harness.sh
```

该命令验证仓库编排、关键工程入口以及 Agent/Rules/Skills 接入；它不替代前端 lint/typecheck/test、后端测试、数据库证据或真实运行验证。第三方 Skills 保持供应商内容原样，项目覆盖规则只写入所属仓库 conventions。
