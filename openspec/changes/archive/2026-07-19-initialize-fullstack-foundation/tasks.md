## 1. 根目录基础设施与配置

- [x] 1.1 在根目录新增 `.env.example`，提供不含敏感值的 MySQL、后端、前端及 OpenAI-compatible 环境变量；扩展 `.gitignore`，确保真实的本地环境文件不被 Git 跟踪。
- [x] 1.2 在根目录新增 `compose.yaml`，使用 `mysql:8.4`，配置环境变量替换、命名存储卷、端口映射和健康检查；本机 Docker 可用时使用 `docker compose config` 验证配置。

## 2. 前端工程

- [x] 2.1 使用 pnpm 初始化 `frontend/`，采用 Next.js 16.2.10、React 19.2.7、TypeScript、App Router、Tailwind CSS 4.3.3、ESLint 和 `src/` 目录，并提交依赖锁定文件。
- [x] 2.2 添加 Vitest、Testing Library 和 jsdom 配置；替换脚手架默认页面前，先创建一个会失败的首页行为测试。
- [x] 2.3 实现测试要求的最小响应式首页及页面元数据；API 基础地址只能通过允许公开的前端环境变量读取。
- [x] 2.4 运行前端 lint 和测试命令，记录准确结果，并明确说明有意暂缓的 build 验证。

## 3. 后端工程

- [x] 3.1 使用 Maven Wrapper、Java 21、Spring Boot 4.1.0 和包名 `com.heness.project` 初始化 `backend/`；加入 Web MVC、Validation、Actuator、MyBatis 4.1.0、MySQL、Flyway MySQL，并使用 Spring AI 2.0.0 管理 AI 依赖。
- [x] 3.2 添加服务端、数据源、MyBatis、Flyway、Actuator、CORS 和 OpenAI-compatible 环境配置，不提交任何真实凭据。
- [x] 3.3 先为 `GET /api/health` 创建一个会失败的 MockMvc 测试，再实现使其通过所需的最小健康检查控制器和响应。
- [x] 3.4 添加空的 Flyway 基线迁移和数据库映射约定，不虚构业务表，也不创建没有实际职责的应用分层目录。
- [x] 3.5 添加测试，证明默认应用上下文不依赖 MySQL、不需要 AI API Key，也不会发起外部模型调用。

## 4. OpenAI-compatible 配置边界

- [x] 4.1 添加测试，覆盖 AI 默认关闭，以及启用 AI 但基础地址、API Key 或模型配置不完整时校验失败的行为。
- [x] 4.2 使用 `AI_BASE_URL`、`AI_API_KEY` 和 `AI_MODEL` 实现条件化的 Spring AI OpenAI-compatible 配置；凭据只保留在服务端，本次不暴露模型调用接口。
- [x] 4.3 运行后端测试套件，以准确证据报告依赖或兼容性失败；不得静默降低已经确认的版本。

## 5. Harness 与文档

- [x] 5.1 使用中文更新根目录 `README.md`、`AGENTS.md` 和 `openspec/config.yaml`，记录已选技术栈、目录图、前置条件、端口、环境配置及真实的安装、测试和启动命令。
- [x] 5.2 扩展 `scripts/check-harness.sh`，在保留现有检查的同时验证前端、后端、Compose、环境变量模板和 OpenSpec 的关键文件。
- [x] 5.3 运行 `bash -n scripts/check-harness.sh`、`./scripts/check-harness.sh`、OpenSpec 校验和已跟踪文件的敏感信息模式检查；使用中文记录所有无法在本机验证的事项。

## 6. 将 MyBatis 替换为 MyBatis-Plus

- [x] 6.1 先添加后端上下文测试，验证 MyBatis-Plus 配置类能够在不连接 MySQL 的情况下加载，并观察测试在依赖尚未替换时失败。
- [x] 6.2 将 `backend/pom.xml` 中的原生 MyBatis starter 替换为 `mybatis-plus-spring-boot4-starter:3.5.17`，把配置前缀和 Mapper 中文约定同步调整为 MyBatis-Plus，不提前创建业务实体、`BaseMapper` 或插件。
- [x] 6.3 使用中文更新根目录及后端 README、`AGENTS.md`、`openspec/config.yaml` 和 Harness 版本检查；运行完整后端测试、Harness 与 OpenSpec 严格校验。
