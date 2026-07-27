## ADDED Requirements

### Requirement: 系统仅使用最少凭据创建账号
后端 SHALL 通过 `POST /api/v1/accounts` 接受 `accountName`、`password`、`confirmPassword` 和 `termsAccepted`；账号为 4—20 位 ASCII 字母、数字或下划线，比较唯一性时忽略英文字母大小写，密码为 8—64 位且同时包含字母和数字。

#### Scenario: 成功注册并建立会话
- **WHEN** 请求字段合法、两次密码一致、条款已同意且规范化账号未被占用
- **THEN** 系统返回 `201 Created` 和不含敏感字段的当前账号表示
- **AND** 原子地创建账号与认证会话并设置 30 分钟短 Token、7 天长 Token 和 CSRF Cookie

#### Scenario: 注册字段非法
- **WHEN** 账号、密码、确认密码或条款任一不符合合同
- **THEN** 系统返回 `400 application/problem+json` 和稳定字段错误
- **AND** 不创建账号、会话或 Token

#### Scenario: 账号大小写冲突
- **WHEN** 已存在账号 `China_Travel` 后注册 `china_travel`
- **THEN** 系统拒绝请求且不创建第二个账号
- **AND** 对外错误不确认冲突账号是否存在

#### Scenario: 注册并发冲突
- **WHEN** 两个请求并发注册规范化后相同的账号
- **THEN** 数据库唯一约束保证最多创建一个账号
- **AND** 另一个请求返回与普通注册拒绝一致的稳定错误而非原始数据库异常

### Requirement: 系统使用自适应单向摘要保护密码
后端 SHALL 使用经配置和测试证明的自适应单向密码摘要保存密码，仅在认证边界短暂处理原始字符；密码和密码摘要 MUST NOT 出现在响应、日志、异常、指标标签、审计事件或测试快照中。

#### Scenario: 保存注册密码
- **WHEN** 账号注册成功
- **THEN** 数据库只保存带算法参数的密码摘要而不保存明文或可逆密文

#### Scenario: 记录认证失败
- **WHEN** 注册或登录处理中发生校验、认证或系统错误
- **THEN** 安全日志只记录请求追踪标识、结果代码和脱敏主体键
- **AND** 不记录请求体、原始账号、密码、Cookie 或 Token

### Requirement: 系统以统一结果校验登录凭据
后端 SHALL 通过 `POST /api/v1/auth-sessions` 校验账号和密码；不存在的账号与错误密码 MUST 采用不可区分的响应合同，并执行等价的密码校验成本。

#### Scenario: 登录成功
- **WHEN** 规范化账号存在、密码正确且账号与 IP 均未受限
- **THEN** 系统返回 `201 Created` 和当前账号表示
- **AND** 创建新的独立会话并设置短 Token、长 Token 和 CSRF Cookie

#### Scenario: 账号不存在或密码错误
- **WHEN** 账号不存在或密码不正确
- **THEN** 系统返回相同状态、错误代码、公开文案和响应结构
- **AND** 为账号键与 IP 键记录一次失败且不签发 Token

#### Scenario: 登录成功重置账号失败计数
- **WHEN** 用户在未触发限制前成功登录
- **THEN** 系统清除该规范化账号键当前窗口的失败状态
- **AND** 不清除该 IP 上其他账号产生的 IP 失败状态

### Requirement: 系统按账号和 IP 限制连续登录失败
后端 SHALL 对规范化账号的不可逆键和客户端 IP 的不可逆键分别计数：任一账号在滚动 15 分钟内失败 5 次或任一 IP 在滚动 15 分钟内失败 20 次后，相关登录尝试限制 15 分钟；不存在的账号也按相同规则计数。

#### Scenario: 账号达到失败阈值
- **WHEN** 同一规范化账号在 15 分钟内发生第 5 次失败
- **THEN** 当前及随后受限期内的登录返回 `429 application/problem+json`
- **AND** 响应包含向上取整的 `Retry-After` 秒数和 `retryAfterSeconds`，但不确认账号存在性

#### Scenario: IP 达到失败阈值
- **WHEN** 同一客户端 IP 在 15 分钟内跨账号累计第 20 次失败
- **THEN** 该 IP 的随后登录在 15 分钟受限期内返回相同的 `429` 合同

#### Scenario: 限制期限结束
- **WHEN** 当前时间达到 `blockedUntil`
- **THEN** 系统允许新的登录校验并开启新的失败窗口

#### Scenario: 代理地址不可信
- **WHEN** 请求携带转发地址头但来源不在显式可信代理配置中
- **THEN** 系统忽略转发头并使用直接连接地址计数

### Requirement: 系统签发可撤销的双 Token 会话
后端 SHALL 为每个登录设备创建独立会话，签发至少 256 位熵的随机不透明短 Token 与长 Token；短 Token 有效期固定为 30 分钟，长 Token 有效期固定为 7 天，服务端只保存 Token 的带密钥摘要。

#### Scenario: Cookie 安全属性
- **WHEN** 系统签发或轮换 Token
- **THEN** 短 Token 与长 Token 仅通过 `Secure`、`HttpOnly`、`SameSite=Lax`、`Path=/` 且不设置 `Domain` 的 Cookie 传递
- **AND** Cookie 名使用 `__Host-` 前缀，响应体不包含 Token

#### Scenario: 短 Token 有效
- **WHEN** 请求携带未过期、未撤销且属于活动会话的短 Token
- **THEN** 系统从服务端会话上下文建立当前账号身份
- **AND** 不接受请求体、查询参数或普通请求头中的 `accountId` 作为身份来源

#### Scenario: 短 Token 到期
- **WHEN** 请求只携带已过期短 Token
- **THEN** 受保护接口返回可识别但不泄露 Token 细节的 `401`
- **AND** 不自动延长会话

#### Scenario: 会话达到长 Token 期限
- **WHEN** 当前时间达到会话创建时确定的 7 天绝对期限
- **THEN** 长 Token 不再可刷新且用户必须重新登录

### Requirement: 长 Token 刷新时必须轮换并检测重放
后端 SHALL 通过 `POST /api/v1/auth-sessions:refresh` 原子校验活动长 Token、签发新的短 Token 与长 Token、作废旧 Token，并保持原会话 7 天绝对期限不延长。

#### Scenario: 正常刷新
- **WHEN** 请求携带有效活动长 Token 和有效 CSRF 证明
- **THEN** 系统返回 `204 No Content` 并原子设置新短 Token 与新长 Token
- **AND** 旧短 Token 与旧长 Token 立即不再用于普通认证或再次正常刷新

#### Scenario: 并发刷新使用刚轮换的长 Token
- **WHEN** 同一旧长 Token 在首次成功轮换后 5 秒内再次到达
- **THEN** 系统返回可重试的 `409` 刷新冲突且不撤销会话、不清除 Cookie
- **AND** 客户端可使用浏览器中已更新的长 Token 重试一次

#### Scenario: 重放已轮换长 Token
- **WHEN** 已轮换超过 5 秒的长 Token 被再次使用
- **THEN** 系统撤销该 Token 家族所属会话并返回 `401`
- **AND** 清除认证 Cookie且记录不含原始 Token 的安全事件

#### Scenario: 使用过期或已撤销长 Token
- **WHEN** 长 Token 已过期、会话已撤销或 Token 无法识别
- **THEN** 系统返回统一 `401` 并清除认证 Cookie

### Requirement: 系统提供当前账号身份
后端 SHALL 通过 `GET /api/v1/accounts/me` 返回当前认证账号的稳定标识、注册时账号显示值和创建时间，不返回密码摘要、Token、内部限流键或其他会话秘密。

#### Scenario: 已认证访问当前账号
- **WHEN** 请求携带有效短 Token
- **THEN** 系统返回 `200 OK` 和当前账号表示

#### Scenario: 匿名访问当前账号
- **WHEN** 请求没有有效短 Token
- **THEN** 系统返回 `401 application/problem+json`

### Requirement: 用户能够幂等退出当前会话
后端 SHALL 通过 `DELETE /api/v1/auth-sessions/current` 撤销当前会话并清除短 Token、长 Token 与会话绑定的 CSRF Cookie；退出 MUST 收敛为幂等结果。

#### Scenario: 退出活动会话
- **WHEN** 请求携带活动会话 Cookie 和有效 CSRF 证明
- **THEN** 系统撤销当前会话并返回 `204 No Content`
- **AND** 此会话的短 Token 与长 Token 均不能再次使用

#### Scenario: 重复退出
- **WHEN** 请求没有活动会话但具备合法来源和 CSRF 合同允许的退出证明
- **THEN** 系统仍返回 `204 No Content` 并发送过期 Cookie

### Requirement: Cookie 认证请求受到 CSRF 与 CORS 防护
后端 SHALL 通过 `GET /api/v1/auth-csrf-token` 签发非认证用 CSRF Cookie，并对注册、登录、刷新和退出要求匹配的自定义请求头以及允许的 `Origin`；凭据 CORS MUST 只允许显式配置的来源。

#### Scenario: 获取 CSRF Token
- **WHEN** 受支持前端获取 CSRF Token
- **THEN** 系统返回 `204 No Content` 并设置 `Secure`、`SameSite=Lax`、不可 `HttpOnly` 的随机 CSRF Cookie
- **AND** 该值不赋予账号身份或会话访问权

#### Scenario: 状态改变请求缺少 CSRF 证明
- **WHEN** 注册、登录、刷新或退出缺少匹配的 CSRF Header/Cookie 或来自未允许来源
- **THEN** 系统在执行凭据校验或数据修改前返回稳定的 `403 application/problem+json`

#### Scenario: 凭据跨域请求
- **WHEN** 请求来源在显式允许列表中
- **THEN** 系统返回该具体来源和 `Access-Control-Allow-Credentials: true`
- **AND** 永不把通配来源与凭据组合使用

### Requirement: 认证持久化保证一致性与最小暴露
后端 SHALL 使用 Flyway 创建账号、认证会话、长 Token 历史和失败限制结构；账号唯一性、Token 摘要唯一性、会话状态与时间边界由数据库约束和事务共同保证。

#### Scenario: 数据库功能关闭
- **WHEN** `DATABASE_ENABLED=false`
- **THEN** 现有非数据库基础应用仍可启动和通过既有测试
- **AND** 认证端点明确不可用而不是退化为内存生产认证

#### Scenario: 数据库功能开启
- **WHEN** 应用连接受支持的 MySQL 8.4 数据库
- **THEN** Flyway 按版本创建认证结构且 MyBatis-Plus 访问限定在 `account` 模块基础设施边界

#### Scenario: 认证事务失败
- **WHEN** 注册、刷新或退出的任一持久化步骤失败
- **THEN** 事务回滚，不产生部分账号、部分 Token 轮换或错误会话状态
