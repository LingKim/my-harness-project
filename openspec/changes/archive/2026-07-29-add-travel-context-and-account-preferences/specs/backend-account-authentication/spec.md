## ADDED Requirements

### Requirement: 已登录用户能够验证当前密码并修改登录密码
后端 SHALL 通过 `POST /api/v1/accounts/me:change-password` 接受 `currentPassword`、`newPassword` 和 `confirmNewPassword`，仅允许有效登录会话执行，并 MUST 在修改摘要前验证当前密码。

#### Scenario: 修改密码请求字段合法
- **WHEN** 已认证用户提交正确当前密码、合法且不同于当前密码的新密码、一致确认值与有效 CSRF 证明
- **THEN** 系统以一个事务替换自适应单向密码摘要并返回 `204 No Content`
- **AND** 响应体、日志、异常、指标、审计事件和测试快照均不包含密码或密码摘要

#### Scenario: 匿名用户修改密码
- **WHEN** 请求没有有效认证会话
- **THEN** 系统返回 `401 application/problem+json` 和 `AUTHENTICATION_REQUIRED`
- **AND** 不执行密码校验或摘要修改

#### Scenario: 缺少 CSRF 证明
- **WHEN** 请求缺少匹配的 CSRF Header/Cookie 或来自未允许 Origin
- **THEN** 系统在验证密码前返回 `403 application/problem+json`

### Requirement: 修改密码复用既有密码规则并使用统一拒绝结果
后端 MUST 要求新密码为 8—64 字符且同时包含至少一个 ASCII 英文字母和一个数字，确认值必须一致，新密码不得与当前密码相同；当前密码错误或任一新密码规则失败 MUST 使用不可区分的公开结果。

#### Scenario: 当前密码错误
- **WHEN** 已认证用户提交错误的 `currentPassword`
- **THEN** 系统返回 `400 application/problem+json`、`PASSWORD_CHANGE_REJECTED` 和统一公开文案
- **AND** 不修改密码摘要或任何会话

#### Scenario: 新密码规则失败
- **WHEN** 新密码长度、字母、数字、确认值或不得复用当前密码任一规则失败
- **THEN** 系统返回与当前密码错误相同的状态、`code`、公开文案和响应结构
- **AND** 不通过 `fieldErrors`、时序分支或日志暴露具体服务端拒绝原因

#### Scenario: 修改密码持久化失败
- **WHEN** 新摘要保存、其他会话撤销或当前会话凭据轮换任一步失败
- **THEN** 事务回滚并返回 `500 application/problem+json`、`INTERNAL_SERVER_ERROR` 和不含内部异常的通用安全提示
- **AND** 原密码和原会话状态仍然有效

### Requirement: 修改密码成功后撤销其他会话并轮换当前会话
修改密码成功后，后端 MUST 在同一事务中撤销该账号除当前会话外的全部活动会话，并 MUST 轮换和保留当前会话的短 Token、长 Token 与 CSRF Cookie。旧 Token MUST 立即失效，轮换 MUST NOT 重新起算或延长当前会话原有的 7 天绝对期限。

#### Scenario: 修改密码成功后处理其他会话
- **WHEN** 已认证用户成功修改密码且该账号存在其他活动会话
- **THEN** 系统在同一事务中撤销除当前会话外的全部活动会话
- **AND** 其他会话持有的短 Token、长 Token 与 CSRF 凭据不能再用于认证或状态变更

#### Scenario: 修改密码成功后轮换并保留当前会话
- **WHEN** 已认证用户成功修改密码
- **THEN** 系统为当前会话重新签发短 Token、长 Token 与 CSRF Cookie，并立即作废轮换前的旧 Token
- **AND** 当前设备保持登录，轮换后的凭据沿用该会话改密前已经确定的绝对到期时间
- **AND** 系统不得重新起算或延长原 7 天绝对期限

#### Scenario: 会话副作用失败
- **WHEN** 其他会话撤销或当前会话任一凭据轮换失败
- **THEN** 密码摘要、其他会话状态和当前会话凭据变更全部回滚
- **AND** 原密码和原会话状态继续有效
