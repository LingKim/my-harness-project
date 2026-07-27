# `add-account-authentication` Spec 合规审查

## 检查范围

- OpenSpec：`proposal.md`、`design.md`、两个 capability `spec.md`、`tasks.md`。
- 实现：`frontend/src/app/[locale]/account/`、`frontend/src/components/account/`、`frontend/e2e/`、`backend/src/main/java/com/heness/project/account/`、Flyway V2 与对应测试。
- 基线：`RULE-FE-*`、`RULE-BE-*`、`RULE-DB-*`、接口开发规范、Java/Spring Boot/MySQL/React Skills。
- 验证：前端 lint/typecheck/Vitest/Playwright、后端隔离测试与 MySQL 8.4 专项、真实中英文跨栈与双标签流程、三仓库治理和 OpenSpec strict。

## 一、正向对账表（Spec → 代码）

| # | Spec 来源 | 要求摘要 | 状态 | 代码位置 / 说明 |
| --- | --- | --- | --- | --- |
| 1 | `proposal.md` | 最少凭据注册、自动登录、安全返回、会话恢复与退出 | ✅ | `AccountAuthenticationService.java:44`；`register-form.tsx`；真实中英文流程 |
| 2 | `proposal.md` | 30 分钟 access、7 天绝对 refresh、轮换与重放撤销 | ✅ | `AuthSessionWindow.java`；`AccountAuthenticationService.java:104`；真实 MySQL 服务测试 |
| 3 | `proposal.md` | 账号 5 次、IP 20 次、15 分钟窗口与统一错误 | ✅ | `LoginFailureBucket.java`；`MybatisLoginFailureStore.java`；4/5/6、19/20/21 fixture |
| 4 | `proposal.md` | 双语、响应式、键盘、无敏感数据泄漏 | ✅ | 两个字典、认证表单、21 项 E2E、安全泄漏检查 |
| 5 | `design.md §1` | 独立登录/注册路由和 Pencil 信息层级 | ✅ | `account/page.tsx`、`account/register/page.tsx`、`auth-layout.tsx` |
| 6 | `design.md §2` | 服务端可撤销不透明双 Token，数据库只存摘要 | ✅ | `OpaqueTokenService.java`、Flyway V2、摘要长度聚合检查 |
| 7 | `design.md §3` | `__Host-` Cookie、CSRF 双提交与精确 CORS | ✅ | `AuthCookieWriter.java`、`AuthCsrfFilter.java`、`SecurityConfiguration.java`、API tests |
| 8 | `design.md §4` | refresh 行锁、5 秒冲突宽限、超过窗口撤销 | ✅ | `RefreshTokenMapper.java:13`、`AccountAuthenticationService.java:104`、并发/重放测试 |
| 9 | `design.md §5` | 六个 HTTP 契约与稳定 ProblemDetail | ✅ | account/api Controllers、`AccountAuthExceptionHandler.java`、8 项 MockMvc |
| 10 | `design.md §6` | 规范化唯一、BCrypt、等价失败成本 | ✅ | `AccountName.java`、`BcryptPasswordService.java`、唯一约束与安全测试 |
| 11 | `design.md §7` | 账号/IP HMAC 限流与可信代理 | ✅ | `HmacFailureKeyService.java`、`ClientIpResolver.java`、真实 bucket 摘要检查 |
| 12 | `design.md §8` | 模块分层、条件装配、外部化秘密 | ✅ | account 四层目录、`AuthConfiguration.java`、`application.yml` 配置测试 |
| 13 | `design.md §9` | 同源 `returnTo` 白名单 | ✅ | `return-to.ts` 与相邻测试、恶意返回 E2E |
| 14 | 后端 Spec Req 1—4 | 注册、密码、统一登录、失败阈值共 13 个场景 | ✅ | domain/application/API/MySQL 测试与真实错误流程 |
| 15 | 后端 Spec Req 5—7 | 双 Token、轮换重放、当前账号共 12 个场景 | ✅ | session/refresh Mapper、服务测试、真实刷新和恢复 |
| 16 | 后端 Spec Req 8—10 | 幂等退出、CSRF/CORS、持久化共 6 个场景 | ✅ | Controller/Security/Flyway、MockMvc 与真实 MySQL |
| 17 | 前端 Spec Req 1—3 | 视觉、表单校验、错误状态共 10 个场景 | ✅ | auth components、Vitest、桌面/320px E2E |
| 18 | 前端 Spec Req 4—7 | 安全返回、会话协作、退出、i18n/a11y 共 11 个场景 | ✅ | auth client/returnTo/navigation、Vitest、E2E 与真实双标签流程 |

场景级追溯：后端 `31/31`、前端 `21/21` 均有实现以及自动化或真实场景证据。

## 二、反向对账表（代码 → Spec）

| # | 代码位置 | 实现内容 | 状态 | Spec 依据 |
| --- | --- | --- | --- | --- |
| 1 | `backend/.../account/domain/` | 账号、密码、会话、失败窗口规则 | ✅ | 后端 Req 1、3、4、5 |
| 2 | `backend/.../AccountAuthenticationService.java` | 注册、登录、刷新、退出、当前账号和事务 | ✅ | 后端 Req 1、3、5—8；design §4 |
| 3 | `backend/.../persistence/` 与 Flyway V2 | 四表、MyBatis-Plus Mapper、行锁和摘要 | ✅ | 后端 Req 4—6、10；design §2、§7、§8 |
| 4 | `backend/.../account/api/` 与 `SecurityConfiguration.java` | 六接口、Cookie、CSRF、CORS、身份过滤 | ✅ | 后端 Req 5、7—9；design §3、§5 |
| 5 | `frontend/.../account/` | 双语认证页面与交互叶子 | ✅ | 前端 Req 1—4、7 |
| 6 | `frontend/.../auth-client.ts` | credential fetch、single-flight、409 重试、内存认证广播 | ✅ | 前端 Req 5、6；design §4 |
| 7 | `frontend/.../return-to.ts` | locale 内同源返回白名单 | ✅ | 前端 Req 4；design §9 |
| 8 | `frontend/e2e/auth.spec.ts` | 认证、限流、响应式、键盘回归 fixture | ✅ | 前端全部 requirement 的验收任务 |

未发现无 Spec 依据的生产功能；即时内存认证广播属于“认证前后导航一致”的必要修复，不是新增业务范围。

## 二-A、代码 → 项目 Rules/技术基线

| # | Rule / 技术基线 | 状态 | 代码与验证证据 | 结论 |
| --- | --- | --- | --- | --- |
| 1 | `RULE-FE-002/003` | ✅ | 页面保持 Server Component，交互位于 account Client 叶子 | 合规 |
| 2 | `RULE-FE-005/007` | ✅ | 无 localStorage/sessionStorage Token；仅公开 API base URL | 合规 |
| 3 | `RULE-FE-006/008` | ✅ | 双语、语义 DOM、键盘、320px/桌面 E2E | 合规 |
| 4 | `RULE-BE-002/003/004` | ✅ | account 业务域四层；架构测试 10/10 | 合规 |
| 5 | `RULE-BE-005` | ✅ | DTO、稳定 ProblemDetail、六个接口测试 | 合规 |
| 6 | `RULE-BE-006` | ✅ | BCrypt、HMAC、redacted `toString`、无原始异常 message | 合规 |
| 7 | `RULE-BE-007` | ✅ | 最小应用事务；安全状态异常使用精确 `noRollbackFor` | 合规 |
| 8 | `RULE-DB-002` | ✅ | schema 仅来自 `V2__add_account_authentication.sql` | 合规 |
| 9 | `RULE-DB-003/004` | ✅ | 显式列、`#{}` 绑定、约束与索引有查询依据 | 合规 |
| 10 | `RULE-DB-006` | ✅ | refresh/bucket `FOR UPDATE`，真实并发阻塞与回滚测试 | 合规 |
| 11 | `RULE-DB-009` | ✅ | 常规 CRUD 与复杂 SQL 均在 MyBatis-Plus Mapper 边界 | 合规，无 Spring JDBC 例外 |
| 12 | `RULE-QA-001—004` | ✅ | 分层命令、边界 fixture、真实场景和脱敏 manifest | 合规 |

## 三、状态说明

| 标记 | 含义 |
| --- | --- |
| ✅ | 已覆盖：要求有完整实现和足够证据；反向项可追溯到明确 Spec |
| ❌ | 未覆盖，或代码存在无依据的超纲功能 |
| ⚠️ | 部分覆盖、实现偏差，或需要确认的合理增强 |

## 四、覆盖率统计

```text
proposal 可验收承诺：4 / 4 = 100%
design 关键决策：9 / 9 = 100%
backend requirements：10 / 10 = 100%（31 / 31 scenarios）
frontend requirements：7 / 7 = 100%（21 / 21 scenarios）
正向要求合计：30 / 30 = 100%
反向超纲项：0
```

流程任务为 `32/33`；唯一未完成的 7.5 是 Git 交付授权任务，不是产品实现或 Spec 覆盖缺口。

## 五、修复 Action Items

| 优先级 | Action Item | 关联 Spec | 建议操作 |
| --- | --- | --- | --- |
| — | 无阻断或非阻断 Spec 修复项 | — | 进入主 Agent 证据收口；Git 操作等待用户授权 |

## 结论

- Spec Review：`PASS`。
- 未提供或未验证项：未执行真实屏幕阅读器软件输出；语义 DOM、标签、live region 和纯键盘由浏览器快照与 E2E 覆盖。
- 残余风险：Next dev 在一次五 worker E2E 中出现不可复现的 JSON 解析瞬时错误；单项与完整回归复跑均通过，不构成 Spec 偏差。
- 下一交接：Experience Review 与主 Agent 收口；未经授权不执行 task 7.5。
