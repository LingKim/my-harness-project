## Purpose

定义 ChinaMate 后端统一 API 错误响应、Bean Validation 参数失败映射、字段错误结构、traceId 和未知异常安全处理的稳定契约，使前端能够依据 HTTP 状态、业务错误码和字段路径可靠处理失败结果。

## Requirements

### Requirement: API 错误使用统一 ProblemDetail 契约
后端 SHALL 对受统一异常处理覆盖的 API 失败响应使用 `application/problem+json`，并 SHALL 至少返回 `type`、`title`、`status`、`detail`、`instance`、`code` 和非空 `traceId`；`status` MUST 与实际 HTTP 状态一致，`instance` MUST 标识当前请求路径，`code` MUST 是供前端稳定判断的大写 `SNAKE_CASE` 值。

#### Scenario: 前端收到统一错误响应
- **WHEN** API 请求触发一个已映射异常
- **THEN** 响应使用与异常语义对应的非 2xx HTTP 状态
- **AND** `Content-Type` 为 `application/problem+json`
- **AND** 响应包含完整的统一错误字段
- **AND** 前端无需解析 `title` 或 `detail` 文案即可通过 `code` 判断错误类型

#### Scenario: 错误实例对应当前请求
- **WHEN** 客户端在任意查询字符串下请求同一个 API 路径并触发错误
- **THEN** `instance` 返回不含查询字符串的请求路径
- **AND** 响应不回显完整请求 URL、认证信息或敏感查询值

### Requirement: Bean Validation 失败返回结构化字段错误
后端 SHALL 将请求体 Bean Validation、请求参数约束和路径参数约束失败统一映射为 `400 Bad Request` 与 `VALIDATION_FAILED`，并 SHALL 返回 `fieldErrors` 数组；每个字段错误 MUST 包含前端可定位的 `field`、稳定约束 `code` 和可展示 `message`，且 MUST NOT 返回被拒绝的原始值。

#### Scenario: 请求体存在一个非法字段
- **WHEN** Controller 使用 `@Valid` 接收请求体且一个字段违反 Bean Validation 约束
- **THEN** 响应状态为 `400`
- **AND** `code` 为 `VALIDATION_FAILED`
- **AND** `fieldErrors` 包含该字段的字段路径、约束码和校验消息

#### Scenario: 请求体存在多个非法字段
- **WHEN** 同一个请求体中多个字段同时违反约束
- **THEN** 响应一次性返回全部可确定的字段错误
- **AND** `fieldErrors` 按字段路径、约束码和消息稳定排序
- **AND** 重复发送相同请求时字段错误顺序保持一致

#### Scenario: 嵌套集合元素校验失败
- **WHEN** 请求体中的嵌套对象或集合元素违反约束
- **THEN** `field` 使用可定位到具体嵌套成员或集合下标的完整属性路径

#### Scenario: 查询参数违反方法约束
- **WHEN** Controller 的查询参数违反范围、长度或其他 Bean Validation 约束
- **THEN** 响应状态为 `400`
- **AND** `code` 为 `VALIDATION_FAILED`
- **AND** `fieldErrors` 标识发生错误的查询参数而不是 Java 方法内部名称

#### Scenario: 必填请求参数缺失
- **WHEN** Controller 声明的必填查询参数未提交
- **THEN** 响应状态为 `400`
- **AND** `code` 为 `VALIDATION_FAILED`
- **AND** `fieldErrors` 标识缺失参数并给出稳定约束码和安全消息

### Requirement: 无法进入 Bean Validation 的输入错误返回安全的客户端错误
后端 SHALL 将 JSON 无法解析、请求参数类型转换失败等无法形成正常 DTO 的客户端输入错误映射为 `400 Bad Request`，并 SHALL 使用稳定业务码区分请求格式错误与字段约束错误。

#### Scenario: JSON 请求体语法错误
- **WHEN** 客户端提交无法解析的 JSON 请求体
- **THEN** 响应状态为 `400`
- **AND** `code` 为 `MALFORMED_REQUEST`
- **AND** 响应不包含 Jackson 异常、Java 类型名、堆栈或原始请求体

#### Scenario: 参数类型转换失败
- **WHEN** 客户端为数字、日期、枚举或其他强类型参数提交无法转换的值
- **THEN** 响应状态为 `400`
- **AND** `code` 为 `VALIDATION_FAILED`
- **AND** `fieldErrors` 标识目标参数和类型转换约束
- **AND** 响应不回显客户端提交的原始值

### Requirement: 未识别异常失败关闭且可追踪
后端 SHALL 将未被更具体规则映射的异常统一转换为 `500 Internal Server Error` 与 `INTERNAL_SERVER_ERROR`，MUST 向客户端隐藏内部异常细节，并 SHALL 记录能够与响应 `traceId` 对应的安全服务端日志。

#### Scenario: Controller 抛出未识别异常
- **WHEN** API 处理过程中抛出未被具体异常映射覆盖的运行时异常
- **THEN** 响应状态为 `500`
- **AND** `code` 为 `INTERNAL_SERVER_ERROR`
- **AND** `detail` 只包含通用安全提示
- **AND** 响应不包含异常类名、堆栈、SQL、表名、密钥或内部供应商响应
- **AND** 服务端错误日志包含与响应一致的 `traceId`

### Requirement: 统一错误能力不改变既有成功契约
后端 SHALL 保持成功响应直接返回资源 Response，并 MUST NOT 因统一错误处理引入全局 `code/message/data` 成功包装；既有 `/api/health` 成功状态、媒体类型和响应字段 MUST 保持兼容。

#### Scenario: 调用应用健康检查
- **WHEN** 客户端请求 `GET /api/health`
- **THEN** 接口继续返回 `200 OK`
- **AND** JSON 响应继续包含既有 `status` 和 `service` 字段
- **AND** 响应不被统一错误处理器额外包装
