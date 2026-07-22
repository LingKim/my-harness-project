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
├── AGENTS.md                   # AI 代理统一开发约束
├── CLAUDE.md                   # Claude Code 项目入口
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
- 真实业务 Mapper 可以按需继承 `BaseMapper<T>`，但数据库结构仍只能由 Flyway 修改。
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

Superpowers 的实际插件属于用户级 Harness 配置，不把第三方插件源码复制进业务仓库。本 AIWorkSpace 通过 `AGENTS.md` 固化探索、TDD、系统调试、submodule 边界和完成前验证等核心纪律。
