## Context

当前前端 `src/app/[locale]/account/page.tsx` 仅渲染 `ComingSoonPage`，后端 `account` 只有模块包边界，尚未引入 Spring Security 或认证表。Pencil 文件 `docs/designs/chinamate-auth.pen` 已给出 1920×1080 登录节点 `ay6XZ` 和注册节点 `kAJhd`，并明确最少信息注册、注册后返回原操作、统一登录错误、失败等待时间、账号不可修改及公开身份分离。

本 change 横跨 Next.js 前端、Spring Boot 后端、MySQL/Flyway、HTTP 安全和真实浏览器体验。产品已确认本次范围为注册、登录、退出、当前账号和会话恢复，双 Token 时长为 30 分钟与 7 天，账号/IP 失败限制采用 proposal 中阈值；修改密码和找回密码不在本次范围。

## Goals / Non-Goals

**Goals:**

- 把 Pencil 两个节点转化为响应式、国际化、可访问且有完整状态的认证页面。
- 用不可被浏览器 JavaScript 读取的双 Token Cookie 实现 30 分钟短期访问和 7 天绝对会话。
- 保证 Token 可撤销、长 Token 单次使用并轮换、重放可检测，同时正确处理多标签页并发刷新。
- 以统一错误、恒定成本校验、账号/IP 双限流、CSRF/CORS 和安全日志降低枚举、暴力破解、开放重定向及 Token 泄露风险。
- 遵守模块化单体、MyBatis-Plus、Flyway、统一 ProblemDetail 和三个仓库交付边界。

**Non-Goals:**

- 邮箱、手机号、验证码、第三方登录、“记住我”、修改密码、未登录找回密码和账号名修改。
- 公开展示名称、账号资料页、管理员账号治理、全设备列表或远程撤销其他设备。
- OAuth 2.0/OIDC 授权服务器、向第三方客户端发放 Token 或把 Token 放入前端存储。
- Redis 分布式限流；首版使用 MySQL 形成多实例一致合同，若容量证据要求再另开 change。

## Decisions

### 1. 页面路由和设计追溯

- 保留现有账号入口 `/{locale}/account` 作为登录页，新增 `/{locale}/account/register`；两个页面之间保留经验证的 `returnTo`。
- 视觉和文案基准引用 Pencil 节点而不导出生成式 HTML。桌面保持左右叙事/表单结构；平板和手机优先表单，收拢叙事和导航，但保留品牌、页面目的、安全说明和切换入口。
- 表单使用语义化 label、原生输入语义、`aria-invalid`、错误关联、状态 live region、可见焦点和键盘可操作的密码显隐/条款控件。

备选方案是把登录和注册放在单一路由的客户端 Tab。未采用，因为独立 URL 更利于深链、浏览器历史、服务端元数据、E2E 和返回路径保持。

### 2. 双 Token 采用服务端可撤销的不透明 Token

- 短 Token 和长 Token 都使用密码学安全随机数，至少 256 位熵；客户端只获得 Cookie，数据库只保存带独立服务端 pepper 的 HMAC-SHA-256 摘要。
- 短 Token 30 分钟，长 Token 从会话创建起绝对 7 天；刷新只轮换 Token，不滑动延长 7 天终点。
- `account_auth_session` 保存会话、当前短 Token 摘要/到期时间、绝对到期时间、状态和审计时间；`account_refresh_token` 保存每代长 Token 摘要、状态、创建/轮换/到期时间并关联会话。已轮换记录保留到该会话绝对到期，用于重放检测，之后可机会式清理。
- 每个浏览器登录形成独立会话。退出只撤销当前会话；登录其他设备不挤下已有设备。

选择不透明 Token 而不是 JWT，是因为本模块当前只有一个模块化单体后端，需要即时撤销、重放检测和清晰的数据库事实；JWT 的离线验证优势不足以抵消撤销表、密钥轮换和残余有效期复杂度。

### 3. Cookie、CSRF 和 CORS

- 认证 Cookie 使用 `__Host-cm_access` 与 `__Host-cm_refresh`，均为 `Secure; HttpOnly; SameSite=Lax; Path=/`，不设置 `Domain`。本地 HTTP 测试通过独立 test profile 覆盖 Cookie 属性生成逻辑，不降低生产默认值。
- `cm_csrf` 是随机、非认证、可由 JavaScript 读取的 `Secure; SameSite=Lax; Path=/` Cookie。前端先请求 `GET /api/v1/auth-csrf-token`，再把同值放入 `X-CSRF-Token`；后端对所有认证状态写操作同时校验 Header/Cookie 和 `Origin`。
- CORS 从配置读取精确来源列表，凭据模式下回显匹配来源，禁止 `*`。生产推荐由反向代理提供同站点访问；开发默认只允许明确的本地前端 origin。

仅依赖 `SameSite=Lax` 的方案无法完整覆盖同站子域、浏览器差异和登录 CSRF，因此未采用。把认证 Token 返回 JSON 并存入 localStorage/sessionStorage 会扩大 XSS 窃取面，也未采用。

### 4. 刷新轮换、重放和多标签页并发

- `POST /api/v1/auth-sessions:refresh` 在单个事务中锁定长 Token/会话，校验状态和绝对到期，作废旧短 Token与长 Token，写入新一代摘要，再设置 Cookie。
- 前端对同一 JS 上下文的并发 `401` 使用 single-flight，只刷新一次且每个业务请求最多重放一次。
- 浏览器多标签页共享 Cookie，两个标签可能并发携带同一旧长 Token。首次刷新成功后 5 秒内再次使用该 Token返回 `409 AUTH_REFRESH_CONFLICT`，不撤销会话也不清 Cookie；后到标签使用已由首次响应更新的 Cookie 重试一次。
- 超过 5 秒再次使用已轮换 Token视为重放，撤销整个会话。该 5 秒窗口是并发可用性与重放敏感度之间的明确取舍，不延长 Token 有效期。

### 5. API 合同

| 方法与路径 | 成功 | 用途 |
| --- | --- | --- |
| `GET /api/v1/auth-csrf-token` | `204` | 设置/更新非认证 CSRF Cookie |
| `POST /api/v1/accounts` | `201` + 当前账号 | 注册并自动建立会话 |
| `POST /api/v1/auth-sessions` | `201` + 当前账号 | 登录并创建新设备会话 |
| `POST /api/v1/auth-sessions:refresh` | `204` | 轮换短 Token 与长 Token |
| `DELETE /api/v1/auth-sessions/current` | `204` | 幂等退出当前会话并清 Cookie |
| `GET /api/v1/accounts/me` | `200` + 当前账号 | 恢复当前身份 |

账号响应只包含不透明 `accountId`、注册时 `accountName` 显示值和 `createdAt`。认证错误使用统一 `application/problem+json`、稳定 `code` 和 `requestId`；限流额外使用标准 `Retry-After` 和数值 `retryAfterSeconds`。前端只按稳定 code 分支，不解析 detail。

### 6. 账号规范化、密码与注册并发

- 输入只允许 ASCII，因此规范化为 `Locale.ROOT` 小写；同时保存原始合法显示值和规范化值，后者建立唯一索引。数据库唯一约束是并发最终防线，应用层预检只优化错误路径。
- 密码使用 Spring Security `BCryptPasswordEncoder`，生产 cost 初值 12，并允许通过受约束配置提高但不得低于安全基线。不存在账号时使用固定虚拟摘要执行同等级校验，减少可利用时序差。
- Request/Response、应用 Command、领域模型和数据库行对象分别建模；任何对象的 `toString`、日志和 ProblemDetail 都不包含密码或摘要。

Argon2id 是安全上可行的备选，但当前会增加额外密码学 provider 和运行内存调优；首版选择 Spring Security 原生、成熟且可配置的 BCrypt，未来算法升级可依赖摘要前缀渐进迁移。

### 7. 账号/IP 双限流与可信代理

- `account_auth_failure_bucket` 使用 `(key_type, key_hash)` 唯一键保存窗口开始、计数与 `blocked_until`。账号键和 IP 键均使用独立 pepper 的 HMAC，避免原始账号/IP 进入限流表和日志。
- 每次失败在事务中原子更新两个 bucket；第 5 次账号失败或第 20 次 IP 失败即进入 15 分钟限制。账号成功只清账号 bucket，不清共享 IP bucket。
- 默认以直接连接地址为客户端 IP。只有来源命中显式可信代理 CIDR 时才解析受控转发头；配置为空时忽略所有转发头。
- 过期 bucket 由登录路径机会式重置，并由定时批量清理控制表体积；清理不影响可观察认证行为。

选择 MySQL 而不是单机内存，是为了在多实例时保持安全阈值一致；代价是失败路径增加数据库写入，后续只有在真实容量证据出现后才评估 Redis。

### 8. 后端模块边界与配置

- `account.api` 拥有 Controller、Request/Response；`account.application` 编排注册、登录、刷新、退出、当前账号；`account.domain` 保存账号和会话规则；`account.infrastructure` 拥有 MyBatis-Plus Mapper、Token/密码实现和持久化适配器。
- Spring Security 只负责 HTTP 安全边界和从 Cookie 解析当前身份；领域规则不依赖 Spring MVC、MyBatis 或 Security Context。
- 新增认证配置统一以 `APP_AUTH_*` 环境变量映射：Token pepper、失败键 pepper、允许 origin、可信代理、Cookie secure 和 BCrypt cost。生产缺少必要秘密时启动失败；秘密不得提供可提交默认值。
- `DATABASE_ENABLED=false` 时保持现有基础启动能力，但认证 bean/端点明确不可用；不创建内存生产账号库。

### 9. 安全返回由前端执行同源白名单

`returnTo` 只存在前端 URL 和内存中，不提交给认证 API。仅接受以单个 `/` 开头、属于当前 locale、不是认证路由且不含控制字符的相对路径；其他值回退当前语言首页。这样后端无需参与页面路由，也消除外部 URL 开放重定向。

## Risks / Trade-offs

- [每次认证需要数据库查询，吞吐低于离线 JWT] → 首版优先即时撤销与实现正确性；为 Token 摘要、会话状态和到期时间建立精确索引，容量证据出现后再评估缓存。
- [5 秒并发宽限允许极短时间内的旧长 Token 不触发撤销] → 宽限请求只返回冲突、不签发 Token；超过窗口即撤销整个会话并记录安全事件。
- [Cookie 跨 origin 的本地开发容易配置错误] → CORS 使用精确 allowlist，测试预检、实际请求和 Set-Cookie 属性，不为方便启用通配来源或非 HttpOnly Token。
- [BCrypt cost 影响测试和登录延迟] → 生产基线为 12；测试注入独立 PasswordEncoder，不通过生产配置降低安全值；验证不存在账号与错误密码路径均执行摘要校验。
- [MySQL 限流表可能成为攻击写热点] → 使用固定长度 HMAC key、唯一索引、短事务和过期清理；性能门禁以阈值附近并发 fixture 验证，不以单条 smoke test 替代。
- [Pencil 只有桌面视觉] → interaction 验收明确移动端信息层级和 320px 下限，Experience Review 同时走查桌面、移动、键盘和错误状态。

## Migration Plan

1. 先新增后端依赖、认证配置和 Flyway migration；数据库表均为新增，不改已有业务表。
2. 以测试先行顺序实现账号注册、会话、刷新、退出、当前账号、CSRF/CORS 和限流；在数据库关闭与开启两种 profile 下验证。
3. 前端先建立 API/错误合同测试，再替换账号占位页并实现注册路由、会话恢复和刷新 single-flight。
4. 运行后端专项测试、前端 lint/typecheck/test/E2E、跨栈真实浏览器流程、安全日志检查、Spec Review 和 Experience Review，并写入 `evidence.md`。
5. 获得授权后按 backend → frontend → 主仓库 gitlink 顺序交付；每个子仓库提交需先推送并核对远端 SHA。

回滚时先回滚前端认证入口，再回滚后端应用版本；新增表暂时保留以避免破坏账号和会话证据。删除表或数据只允许通过后续明确授权的 Flyway change，不能在本 change 回滚脚本中自动执行。

## Open Questions

无。上述双 Token 类型、Cookie/CSRF、刷新并发宽限、密码摘要和限流持久化属于本次规格确认的一部分；若用户调整，先更新本 change artifacts 再实现。
