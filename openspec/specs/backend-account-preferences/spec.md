# backend-account-preferences Specification

## Purpose
定义当前认证账号旅行上下文与界面语言偏好的查询、更新、完整替换、整组清空、账号隔离、乐观并发、持久化事务、CSRF 防护及安全日志边界。

## Requirements
### Requirement: 系统提供当前账号的旅行上下文表示
后端 SHALL 通过 `GET /api/v1/accounts/me/travel-context` 返回当前认证账号的 `countryOrRegion`、`city`、`tripStartDate`、`tripEndDate`、`dietaryRestrictions`、`assistanceNeeds` 和 `version`；身份 MUST 仅来自服务端认证上下文。

#### Scenario: 查询已保存的旅行上下文
- **WHEN** 已认证用户已经保存旅行上下文并携带有效短 Token 查询
- **THEN** 系统返回 `200 OK` 和该账号规范化后的完整旅行上下文
- **AND** 响应不包含其他账号数据、密码、Token、精确坐标或内部持久化字段

#### Scenario: 查询尚未保存或已清空的旅行上下文
- **WHEN** 已认证用户没有保存任何可选旅行字段
- **THEN** 系统返回 `200 OK`、空的可选字段、空的 `dietaryRestrictions` 和当前 `version`
- **AND** 不使用 `404` 表示空上下文

#### Scenario: 匿名查询旅行上下文
- **WHEN** 请求没有有效认证会话
- **THEN** 系统返回 `401 application/problem+json` 和 `AUTHENTICATION_REQUIRED`
- **AND** 不返回任何旅行上下文

### Requirement: 用户能够整体替换自己的可选旅行上下文
后端 SHALL 通过 `PUT /api/v1/accounts/me/travel-context` 完整替换当前认证账号的旅行上下文；除账号语言偏好外，全部旅行字段均可省略或清空，且服务器 SHALL 返回规范化后的最终表示。

#### Scenario: 保存完整旅行上下文
- **WHEN** 已认证用户提交合法字段、当前 `version` 和有效 CSRF 证明
- **THEN** 系统原子保存全部字段、返回 `200 OK` 与规范化资源并递增 `version`
- **AND** 后续查询返回同一账号保存的最新值

#### Scenario: 保存部分旅行上下文
- **WHEN** 请求只提交 `city` 和 `assistanceNeeds`，其他可选标量为 `null`、`dietaryRestrictions` 为空数组
- **THEN** 系统保存已提交值并清空该资源中其他可选字段
- **AND** 不要求用户填写国家/地区、日期、饮食限制或帮助需求

#### Scenario: 日期只有一端
- **WHEN** 请求只包含合法的 `tripStartDate` 或只包含合法的 `tripEndDate`
- **THEN** 系统接受该部分日期并保存

#### Scenario: 日期顺序非法
- **WHEN** `tripStartDate` 与 `tripEndDate` 同时存在且结束日期早于开始日期
- **THEN** 系统返回 `400 application/problem+json` 和 `VALIDATION_FAILED`
- **AND** 不修改原旅行上下文

#### Scenario: 字段边界非法
- **WHEN** 国家/地区或城市超过 100 字符、帮助需求超过 1000 字符、饮食限制超过 20 项、单项超过 80 字符、出现空字符串或日期不是 `YYYY-MM-DD`
- **THEN** 系统返回 `400 VALIDATION_FAILED` 和稳定字段错误
- **AND** 不进行部分保存

#### Scenario: 饮食限制规范化
- **WHEN** 请求包含首尾空白或 Unicode 大小写折叠后重复的饮食限制
- **THEN** 系统去除首尾空白、按规范化值去重并保留首次出现顺序
- **AND** 响应返回规范化后的列表

#### Scenario: 请求包含未知字段
- **WHEN** 旅行上下文请求包含合同未声明的 JSON 字段
- **THEN** 系统返回 `400 VALIDATION_FAILED` 且不忽略该字段继续保存

### Requirement: 用户能够幂等清空全部可选旅行上下文
后端 SHALL 通过 `DELETE /api/v1/accounts/me/travel-context?version=N` 原子清空当前认证账号的全部可选旅行字段；当前版本 MUST 通过必需的查询参数 `version` 传输，且请求 MUST NOT 携带 JSON 请求体；清空不得删除账号或修改 `preferredLanguage`。

#### Scenario: 清空已有旅行上下文
- **WHEN** 已认证用户通过查询参数携带当前 `version`、不发送 JSON 请求体并携带有效 CSRF 证明清空
- **THEN** 系统删除国家/地区、城市、旅行日期、饮食限制和帮助需求并返回 `204 No Content`
- **AND** 当前账号的语言偏好与认证会话保持不变

#### Scenario: 重复清空
- **WHEN** 当前账号的旅行上下文已经为空且用户再次携带当前 `version` 清空
- **THEN** 系统仍返回 `204 No Content`

### Requirement: 旅行上下文更新防止静默覆盖
后端 SHALL 为旅行上下文维护单调递增的 `version`，并 SHALL 对替换与清空执行乐观并发检查。

#### Scenario: 使用过期版本保存
- **WHEN** 另一个请求已更新资源，而客户端使用旧 `version` 执行 `PUT` 或 `DELETE`
- **THEN** 系统返回 `409 application/problem+json`、`TRAVEL_CONTEXT_VERSION_CONFLICT`，并通过 ProblemDetail 扩展字段 `latestVersion` 返回最新版本
- **AND** 不覆盖或清空已提交的新数据

#### Scenario: 旅行上下文事务失败
- **WHEN** 主上下文或任一饮食限制持久化步骤失败
- **THEN** 整个更新或清空事务回滚
- **AND** 查询仍返回事务开始前的完整版本

### Requirement: 登录用户的界面语言同步为账号偏好
后端 SHALL 在 `GET /api/v1/accounts/me` 的当前账号表示中返回 `preferredLanguage`，并 SHALL 通过 `PATCH /api/v1/accounts/me` 仅接受 `zh-CN` 或 `en` 作为当前认证账号的语言偏好。

#### Scenario: 更新语言偏好
- **WHEN** 已认证用户提交合法 `preferredLanguage` 和有效 CSRF 证明
- **THEN** 系统返回 `200 OK` 和更新后的当前账号表示
- **AND** 后续查询与重新登录恢复同一偏好

#### Scenario: 语言取值不受支持
- **WHEN** 请求提交 `zh-TW`、空字符串、显式 `null` 或其他不受支持取值
- **THEN** 系统返回 `400 VALIDATION_FAILED`
- **AND** 保留原账号语言偏好

#### Scenario: 新增偏好迁移
- **WHEN** 既有账号在迁移后首次查询当前账号
- **THEN** 系统为其提供确定的 `zh-CN` 默认偏好

### Requirement: 账号偏好数据受到认证、CSRF 与最小暴露保护
后端 MUST 对旅行上下文和语言偏好的所有状态变更执行现有 Cookie 会话、允许 Origin 与 CSRF Header/Cookie 校验，并 MUST 将数据访问限定在当前认证账号。

#### Scenario: 伪造账号标识
- **WHEN** 客户端在请求体、查询参数或普通请求头中提交其他 `accountId`
- **THEN** 系统不把该值作为身份来源并拒绝未知字段或忽略非合同身份载荷
- **AND** 其他账号数据不被读取或修改

#### Scenario: 缺少 CSRF 证明
- **WHEN** `PUT`、`DELETE` 或 `PATCH` 缺少匹配的 CSRF 证明或来自未允许 Origin
- **THEN** 系统在读取敏感请求体或修改数据前返回 `403 application/problem+json`

#### Scenario: 未预期偏好服务错误
- **WHEN** 旅行上下文或语言偏好处理过程中抛出未被更具体规则映射的异常
- **THEN** 系统返回 `500 application/problem+json` 和 `INTERNAL_SERVER_ERROR`
- **AND** 响应使用通用安全提示且不包含内部异常细节

#### Scenario: 安全记录失败
- **WHEN** 查询、更新或清空发生校验、权限、持久化或系统错误
- **THEN** 日志只记录 `traceId`、稳定结果码和不可逆主体键
- **AND** 不记录旅行限制原文、请求体、密码、Cookie、Token、SQL 或原始异常详情
