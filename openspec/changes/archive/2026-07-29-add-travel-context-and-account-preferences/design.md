## Context

现有账号能力已经通过 `backend-account-authentication` 与 `frontend-account-authentication` 冻结注册、登录、双 Token Cookie 会话、CSRF、当前账号查询和退出。M03 仍缺少账号级旅行上下文、登录用户语言偏好与修改密码能力；当前系统地图将它们标记为 `account` 模块的 PLANNED 能力。

本设计以 PRD `FR-AUTH-003`、`FR-I18N-001`、登录状态修改密码规则，以及 Pencil 节点 `x09Kjg`、`hNTEF`、`O4byu2`、`Hk4TW`、`a8FkLf`、`G1HPz` 为输入。旅行上下文可能包含过敏原、饮食与无障碍需求，因此按账号私有数据处理；不将其解释为 HTTP Session、AI 会话或精确位置。所有状态变更沿用现有 Cookie 认证、可信 Origin 与 CSRF Header/Cookie 合同。

主要参与者是登录用户、`frontend/` 的账号设置与 locale 路由、`backend/` 的 `account` 模块及 MySQL 8.4。未来 `assistant` 模块只能通过 `account` 的公开 application 契约读取旅行上下文，不直接访问账号表；AI 使用个人限制的披露行为不在本 change 实现。

## Goals / Non-Goals

**Goals:**

- 以最小字段集合保存、查询、整体替换和整组清空当前账号的旅行上下文。
- 将登录用户主动选择的 `zh-CN` 或 `en` 作为账号偏好持久化，并在路由切换时保留页面、搜索参数和未提交表单。
- 提供需要当前密码的登录态修改密码操作，复用既有 8—64 位且同时包含英文字母和数字的密码规则。
- 冻结 API、持久化、账号隔离、权限、错误、事务、并发与测试边界。
- 忠实实现六个 Pencil 节点表达的桌面内容态、校验态和网络错误态，并补充窄屏与无障碍行为。

**Non-Goals:**

- 邮箱、手机号、验证码、第三方登录、头像、展示名称或社交资料。
- 未登录密码找回、多设备会话列表或逐设备会话管理。
- GPS、实时坐标、后台定位、访问轨迹或城市自动推断。
- AI 回答、Prompt 拼装或限制披露的具体实现。

## Decisions

### 1. 旅行上下文与语言偏好同属账号模块，但使用两个 API 资源

旅行上下文使用当前账号从属资源：

```text
GET    /api/v1/accounts/me/travel-context
PUT    /api/v1/accounts/me/travel-context
DELETE /api/v1/accounts/me/travel-context?version=N
```

`GET` 返回当前保存状态；尚未保存或已清空时仍返回 `200 OK` 与所有可选字段为空的稳定表示，不用 `404` 表达“空上下文”。`PUT` 是完整替换：请求必须携带当前 `version`，未提交的可选字段按清空处理，成功返回规范化后的资源并递增 `version`。`DELETE` 通过必需的查询参数 `version=N` 携带当前版本且不发送 JSON 请求体，原子清空全部可选旅行字段，重复清空仍返回 `204 No Content`；它不删除账号、不改变 `preferredLanguage`。

语言偏好属于普通账号字段，复用：

```text
PATCH /api/v1/accounts/me
```

请求仅开放 `preferredLanguage`，取值为 `zh-CN` 或 `en`；成功返回包含 `preferredLanguage` 的当前账号表示。标量语言选择采用最后一次成功写入为准，不引入独立版本冲突。当前账号 `GET` 同样返回该字段。

备选方案是把语言与旅行字段合并为一个 `preferences` DTO。未采用原因是“清空旅行上下文”不得清除必填语言偏好，而且语言切换发生在任意页面，若要求提交整份旅行表单会增加覆盖和隐私风险。

### 2. 冻结旅行字段、可选性与校验边界

旅行上下文表示包含：

| 字段 | 类型与限制 | 可选/清空语义 |
| --- | --- | --- |
| `countryOrRegion` | 去除首尾空白后的 Unicode 文本，1—100 字符 | 可缺省；`null` 表示清空 |
| `city` | 去除首尾空白后的 Unicode 文本，1—100 字符 | 可缺省；`null` 表示清空；不包含坐标 |
| `tripStartDate` | `YYYY-MM-DD` | 可缺省；`null` 表示清空 |
| `tripEndDate` | `YYYY-MM-DD` | 可缺省；`null` 表示清空 |
| `dietaryRestrictions` | 最多 20 项；每项去除首尾空白后 1—80 字符；按 Unicode 大小写折叠结果去重并保留首次顺序 | 可为空数组；空数组表示清空全部 |
| `assistanceNeeds` | 去除首尾空白后的 Unicode 文本，1—1000 字符 | 可缺省；`null` 表示清空 |
| `version` | 大于等于 0 的整数 | 查询返回，更新与清空时必需 |

开始和结束日期可以分别单独存在；两者同时存在时 `tripEndDate` 不得早于 `tripStartDate`。显式空字符串不是清空信号，返回 `400 VALIDATION_FAILED`；客户端应把用户清空后的字段转换为 `null`。未知 JSON 字段被拒绝。

国家/地区与城市先保存用户选择的规范化显示文本，不在 MVP 引入外部地理字典或地理编码依赖。备选的国家码、城市 ID 方案需要单独的权威目录、双语名称与迁移策略，超出本 change。

### 3. 持久化使用账号一对一主表与有序限制子表

Flyway 新增：

- `account_preferences.preferred_language` 或等价账号一对一偏好结构，账号 ID 唯一且非空，默认 `zh-CN`，仅允许 `zh-CN`、`en`。
- `account_travel_context`，以账号 ID 为唯一键，保存国家/地区、城市、开始/结束日期、帮助需求、`version` 与审计时间。
- `account_dietary_restriction`，保存账号 ID、稳定顺序和限制文本；账号内规范化文本唯一，删除主上下文时级联或在同一事务显式删除。

Mapper 仍位于 `account.infrastructure`，常规 CRUD 使用 MyBatis-Plus `BaseMapper<T>`；新增自定义 SQL 只放 Mapper XML。查询、替换、清空与语言更新全部从服务端认证上下文取得账号 ID，不接受客户端 `accountId`。数据库约束与应用事务共同保证一账号一份上下文、日期顺序、多值数量和版本更新一致。

备选的单列 JSON 数组会减少表数量，但弱化去重、数量约束和差异测试，因此不采用。

### 4. 旅行上下文更新采用乐观并发且整组事务提交

`PUT` 与 `DELETE` 使用 `version` 比较并交换；版本不匹配返回 `409 TRAVEL_CONTEXT_VERSION_CONFLICT`，并在 ProblemDetail 扩展字段 `latestVersion` 中返回最新版本。客户端保留草稿、重新读取后提示用户选择是否以当前草稿再次保存，不静默覆盖其他标签页的更新。主表与饮食限制子表必须在一个短事务内替换，任一步失败整体回滚。

备选的最后写入获胜实现更简单，但可能无提示覆盖另一标签页刚保存的过敏或无障碍需求，因此不采用。

### 5. 登录用户语言切换采用“先本地无损切换，后账号同步”

切换顺序：

1. 从当前 locale 路由构造同一业务页面的目标 locale 路由，原样保留合法路径、Query String 与 hash。
2. 当前页面内的表单状态留在 React 状态或受控草稿层，不通过把敏感字段写入 URL 或持久化浏览器存储来保持。
3. 立即切换全部可见 UI 文案，并继续保留搜索条件和未提交字段。
4. 已登录时发送 `PATCH /api/v1/accounts/me` 同步 `preferredLanguage`；未登录时沿用现有浏览器 locale Cookie。
5. 同步失败时保持已切换页面和草稿，显示可重试的本地化非阻断提示；不得回退首页或自动恢复旧语言。下一次加载已登录页面时，服务端账号偏好为权威值。

认证成功恢复账号状态后，以账号 `preferredLanguage` 为登录用户的默认 locale；匿名 Cookie 不覆盖既有账号偏好。备选的“服务端保存成功后再切换”会让网络失败妨碍本地界面切换，也增加表单丢失风险，因此不采用。

### 6. 设置页面与错误状态遵循 Pencil 合同

- `/{locale}/account/settings/travel-context` 对应 `x09Kjg` 中文内容态与 `hNTEF` 英文日期校验态。
- `/{locale}/account/settings/security` 对应 `O4byu2` 中文内容态与 `Hk4TW` 英文退出网络错误态。
- `/{locale}/account/settings/security/change-password` 对应 `a8FkLf` 中文表单态与 `G1HPz` 英文统一失败态。
- 账号资料只读显示现有账号名称、稳定账号标识、创建时间和语言偏好，不显示密码、密码摘要或 Token。
- 请求进行中阻止同一动作重复提交；校验失败聚焦第一个无效字段；异步成功或失败通过可感知状态区域宣布。
- 320—767px 窄屏下按操作优先级将侧栏收拢为可访问导航，表单、错误和主要按钮完整可见且无水平滚动。

网络失败只说明请求未完成并允许重试；退出失败必须保持已登录状态，旅行保存失败必须保留全部草稿，修改密码失败必须清空三个密码字段。服务端原始 `detail`、异常或内部状态不得直接展示。

### 7. 修改密码使用独立受保护命令与统一公开失败合同

端点：

```text
POST /api/v1/accounts/me:change-password
```

请求仅包含 `currentPassword`、`newPassword`、`confirmNewPassword`；三者必填。新密码沿用注册规则：8—64 字符，至少一个 ASCII 英文字母和一个数字，确认值必须一致。后端先验证当前密码，再完成新密码校验与摘要替换；对“当前密码错误、新密码不合规、确认不一致、新密码与当前密码相同”统一返回 `400 application/problem+json`、`PASSWORD_CHANGE_REJECTED` 和相同公开结构/文案，不返回 `fieldErrors` 来区分原因。匿名或失效会话仍返回 `401 AUTHENTICATION_REQUIRED`，CSRF/Origin 失败返回 `403`，未预期错误沿用统一错误合同，返回安全的 `500 INTERNAL_SERVER_ERROR`。

成功默认返回 `204 No Content`；响应、日志、异常、指标、审计事件和测试快照均不得出现原始密码或摘要。前端可以在发送前本地显示密码长度、字母、数字与确认匹配状态，但必须把服务端统一结果视为最终结论；服务端拒绝后清空三个密码字段并将焦点移回当前密码。

备选的普通 `PATCH /accounts/me` 无法表达当前密码验证和会话副作用，因此采用自定义方法。

### 8. 修改密码成功后撤销其他会话并轮换当前会话

密码摘要更新成功后，在同一事务中撤销该账号除当前会话外的全部活动会话；为当前会话轮换短 Token、长 Token 与 CSRF Cookie，并立即作废旧 Token。轮换后的当前会话继续使用改密前已经确定的绝对到期时间，不重新起算或延长原 7 天绝对期限。前端保持当前设备登录并明确提示“其他设备需要重新登录”。

理由是密码可能因泄露而被修改，撤销其他会话能缩短攻击窗口；保留并轮换已用当前密码重新验证的当前会话，可避免用户在完成受保护操作后立即中断。备选包括：

- 撤销全部会话并要求当前设备重新登录：止损最强，但用户刚验证当前密码后仍被中断。
- 所有会话保持不变：体验最连续，但旧设备或被盗 Token 在密码修改后仍可使用，不符合安全最小化。

该策略已经通过 `SPEC_CONFIRMATION`，后端、前端和相关测试必须共同验证其他会话撤销、当前会话三类凭据轮换、旧 Token 作废，以及绝对到期时间保持不变。

### 9. 错误、权限与日志边界统一

所有端点只允许有效登录会话访问；个人资源身份来自认证上下文。状态变更必须满足现有 CSRF Header/Cookie、可信 Origin 与凭据 CORS 合同。错误统一使用 `application/problem+json`，前端仅依据稳定 `code` 映射中英文文案：

| 情况 | HTTP / `code` |
| --- | --- |
| 字段格式或日期组合非法 | `400 VALIDATION_FAILED` |
| 修改密码统一拒绝 | `400 PASSWORD_CHANGE_REJECTED` |
| 未认证或会话失效 | `401 AUTHENTICATION_REQUIRED` |
| CSRF 或 Origin 不合法 | `403 ACCESS_DENIED` |
| 旅行上下文版本冲突 | `409 TRAVEL_CONTEXT_VERSION_CONFLICT` |
| 未预期错误 | `500 INTERNAL_SERVER_ERROR` |

跨账号访问不提供 `accountId` 路由，因此不存在合法枚举入口。安全日志只记录 `traceId`、结果码和不可逆主体键；不记录旅行限制原文、密码、Cookie、Token、请求体或数据库异常详情。

## Risks / Trade-offs

- [旅行限制属于敏感个人信息] → 最小字段、用户主动填写、账号级授权、日志排除原文、整组清空与删除测试。
- [语言切换时 React 子树重建可能丢失草稿] → 使用 locale 无关的草稿层或等价状态提升，并用跨 locale E2E 覆盖搜索与未提交表单。
- [多标签页覆盖旅行数据] → `version` 乐观并发、`409` 明示冲突、不得静默重试覆盖。
- [用户把自由文本当作紧急求助] → 帮助需求只作为偏好保存；UI 不承诺实时监控或紧急响应，后续 AI 风险处理另行规格化。
- [统一修改密码错误降低具体可操作性] → 发送前提供不涉及当前密码正确性的客户端规则提示，服务端失败仍保持不可区分。
- [会话撤销与当前会话轮换跨多项状态，部分成功会造成安全或可用性问题] → 密码摘要更新、其他会话撤销和当前会话轮换置于同一事务边界，并测试失败时完整回滚。
- [新增表迁移后回滚会丢失新数据] → 应用回滚为停止读写新表并回退代码；生产数据库采用前向修复，不自动执行破坏性 down migration。

## Migration Plan

1. 以已经通过 `SPEC_CONFIRMATION` 的规格和会话策略作为实现基线。
2. 先以 Flyway 增量创建偏好、旅行上下文与饮食限制结构，为已有账号补齐 `zh-CN` 默认偏好；不修改或删除既有认证表和 Token。
3. 后端先交付数据库、领域/API 测试和受保护端点，再交付前端设置路由、表单与语言同步。
4. 使用 MySQL 8.4 验证 migration、账号隔离、事务回滚、版本冲突与修改密码会话副作用；使用 Vitest/Playwright 验证中英文、状态保持、网络错误和窄屏。
5. 回滚应用时保留新增表但停止调用新端点；若需恢复能力，使用前向 migration 修复。不得通过自动回滚删除用户已保存的旅行上下文。
