## 1. 合同与验证准备

- [x] 1.1 复核 `proposal.md`、`design.md`、两个 `spec.md` 与 Pencil 节点 `ay6XZ`/`kAJhd`，记录用户确认版本并运行 `openspec validate add-account-authentication --strict`。
- [x] 1.2 按验证 Profile 对根仓库、`frontend/`、`backend/` 执行只读环境预检，保护三个仓库既有改动，并在 `evidence.md` 记录 `PASS`、`BLOCKED` 或 `REVIEW_REQUIRED`。
- [x] 1.3 在 `backend/pom.xml`、`backend/src/main/resources/application.yml`、根 `.env.example` 和相关配置测试中先定义 Spring Security、Token pepper、失败键 pepper、允许 origin、可信代理、Cookie 与 BCrypt 配置合同，证明缺少生产秘密时明确失败且 `DATABASE_ENABLED=false` 仍可启动。

## 2. 后端测试先行

- [x] 2.1 在 `backend/src/test/java/com/heness/project/account/domain/` 先编写账号规范化、账号/密码规则、会话 30 分钟与 7 天边界、Token 状态转换和 5 秒重放宽限的失败测试。
- [x] 2.2 在 `backend/src/test/java/com/heness/project/account/application/` 先编写注册并发、等价凭据失败成本、登录成功、刷新轮换/冲突/重放、幂等退出和当前账号用例编排测试，并覆盖事务失败回滚。
- [x] 2.3 在 `backend/src/test/java/com/heness/project/account/api/` 先编写六个 HTTP 契约的 MockMvc 测试，覆盖 Bean Validation、ProblemDetail code、Cookie 属性、CSRF、CORS、`Retry-After`、匿名与已认证行为。
- [x] 2.4 在 `backend/src/test/java/com/heness/project/account/infrastructure/` 先编写密码摘要、Token HMAC、账号/IP HMAC、可信代理解析和 MyBatis-Plus 适配器测试，确保敏感值不出现在对象字符串与日志断言中。
- [x] 2.5 为 MySQL 8.4 准备真实数据库 fixture，先验证账号大小写唯一、Token 摘要唯一、刷新行锁/事务、账号阈值 4/5/6 与 IP 阈值 19/20/21 两侧行为以及过期 bucket 重置，不以单条 CRUD smoke test 代替。

## 3. 后端领域、持久化与安全实现

- [x] 3.1 新增 `backend/src/main/resources/db/migration/V2__add_account_authentication.sql`，创建账号、认证会话、长 Token 历史和失败 bucket 表及已证实查询所需约束/索引，并验证 Flyway 前向迁移与兼容回滚方案。
- [x] 3.2 在 `backend/src/main/java/com/heness/project/account/domain/` 实现账号、凭据规则、会话、Token 代际、失败限制和领域错误，不依赖 Spring MVC、Security 或 MyBatis。
- [x] 3.3 在 `backend/src/main/java/com/heness/project/account/application/` 实现注册、登录、刷新、退出和当前账号用例及持久化/密码/Token/时钟端口，给原子操作设置最小事务边界。
- [x] 3.4 在 `backend/src/main/java/com/heness/project/account/infrastructure/` 实现 BCrypt、随机 Token、HMAC 摘要、MyBatis-Plus Row/Mapper/适配器、可信代理与失败 bucket 清理，所有 SQL 使用安全参数绑定和显式列。
- [x] 3.5 在 `backend/src/main/java/com/heness/project/account/api/` 实现 Request/Response、六个 Controller 契约、Cookie 写入/清除与稳定错误映射，并扩展 `shared/web/error` 的认证错误 code 而不暴露原始异常。
- [x] 3.6 在 `backend/src/main/java/com/heness/project/config/` 和 account 安全边界实现 SecurityFilterChain、Cookie 身份解析、CSRF Header/Cookie、精确凭据 CORS 与 `DATABASE_ENABLED` 条件装配。
- [x] 3.7 运行 account 领域/应用/API/基础设施专项测试和 `./mvnw -Dtest=ArchitectureRulesTests test`，修复失败后记录测试数、失败数与工程实践合规清单。

## 4. 前端测试先行

- [x] 4.1 在 `frontend/src/components/account/` 相邻测试中先编写登录/注册表单 RED 场景，覆盖字段规则、确认密码、条款、密码显隐、忙碌、统一错误、限流倒计时和键盘/可访问性。
- [x] 4.2 在 `frontend/src/components/account/auth-client.test.ts` 先编写带凭据请求、CSRF 初始化、单上下文 single-flight、业务请求最多重放一次、`409` 刷新冲突重试和最终匿名收敛测试。
- [x] 4.3 扩展 `frontend/src/i18n/dictionaries.test.ts` 和路由测试，先覆盖 `zh-CN`/`en` 完整认证文案、`/{locale}/account/register`、未知 locale 404 和安全 `returnTo` 校验。
- [x] 4.4 在 `frontend/e2e/` 先编写登录、注册并继续、页面刷新恢复、短 Token 到期刷新、退出、阈值倒计时、恶意 `returnTo`、320px/桌面和纯键盘流程，并准备不会写入真实凭据的 fixture。

## 5. 前端页面与会话实现

- [x] 5.1 在 `frontend/src/components/account/` 实现可复用认证布局、登录表单、注册表单、字段、错误/倒计时和密码显隐交互，保持 Client Component 在表单交互叶子。
- [x] 5.2 在 `frontend/src/app/[locale]/account/page.tsx` 替换占位页并新增 `frontend/src/app/[locale]/account/register/page.tsx`，按 Pencil 桌面基准和已确认移动端信息层级实现响应式页面。
- [x] 5.3 实现最小认证客户端与内存状态：带凭据 API、CSRF、当前账号恢复、刷新 single-flight/冲突重试、幂等退出和合法 `returnTo`，禁止 localStorage/sessionStorage 保存 Token 或完整账号。
- [x] 5.4 更新 `frontend/src/components/site-header.tsx`、`frontend/src/proxy.ts`、`frontend/src/i18n/dictionary.ts` 及两个字典，使匿名入口、已认证退出、语言切换和认证子路由一致。
- [x] 5.5 运行认证相关 Vitest、`pnpm typecheck`、`pnpm lint` 和认证 Playwright；修复失败后记录命令、用例数、桌面/移动与无障碍结果。

## 6. 跨栈与安全验收

- [x] 6.1 使用 MySQL 8.4 和真实前后端运行注册→自动登录→合法返回→当前账号→30 分钟边界刷新→退出流程，分别验证 `zh-CN`、`en` 和刷新后的页面恢复。
- [x] 6.2 用边界 fixture 验证账号 4/5/6 次、IP 19/20/21 次、15 分钟窗口/限制到期、刷新 5 秒内并发冲突及 5 秒后重放撤销，并检查多标签页不会误登出。
- [x] 6.3 检查响应、浏览器存储、数据库、服务端日志、异常、ProblemDetail、测试快照和仓库 diff，确认不存在密码、密码摘要、原始 Token、Cookie、原始账号/IP 限流键或提交的真实秘密。
- [x] 6.4 运行受影响的后端测试、前端 lint/typecheck/test/E2E、根 Harness 和 OpenSpec strict profile，生成脱敏 `reviews/verification-manifest.json` 并检查 freshness。

## 7. 审查、证据与授权后交付

- [x] 7.1 QA 按两个 capability 的全部场景和适用工程 Rule 独立验收，把 PASS/FAIL/BLOCKED/NOT_RUN、缺陷与残余风险写入 `evidence.md`。
- [x] 7.2 Spec Reviewer 只读执行 Spec→代码与代码→Spec 双向对账及 Java/Spring/MySQL/Next.js 基线检查，将长报告保存为 `reviews/spec-review.md` 并关闭阻断 Action Items。
- [x] 7.3 Experience Reviewer 对真实登录/注册/恢复/限流/退出流程执行桌面、320px、键盘、读屏语义、双语和 Pencil 视觉走查，将 P0—P3 结果保存为 `reviews/experience-review.md`。
- [x] 7.4 主 Agent 复核 verification freshness、全部失败/阻塞/未运行和残余风险，更新 `evidence.md` 与 tasks；未经用户授权不提交、推送、更新 gitlink或归档。
- [x] 7.5 获得明确授权后依次交付 backend、frontend，核对远端 SHA，再更新并交付主仓库 gitlink；完成最终复验后另行请求归档授权。
