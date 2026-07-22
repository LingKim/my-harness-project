## Why

后端已经引入 Bean Validation 依赖并在接口规范中定义了 `ProblemDetail` 错误格式，但当前代码没有统一异常映射，也没有可验证的参数校验失败返回行为。业务接口继续增加前，需要先建立稳定的失败契约，让前端能够依据 HTTP 状态、业务错误码和字段错误列表准确提示用户，而不是解析不稳定的异常文案。

## What Changes

- 为后端建立基于 Spring `ProblemDetail` 和 `application/problem+json` 的统一错误响应能力。
- 对 `@Valid` 请求体、方法参数约束、类型转换失败、JSON 解析失败等客户端输入错误统一返回 `400 Bad Request`。
- 参数校验失败时返回稳定的 `VALIDATION_FAILED` 业务码和结构化 `fieldErrors`，供前端定位字段并展示提示。
- 对未识别的服务端异常统一返回不泄露内部信息的 `500 Internal Server Error`，并使用同一个 `traceId` 关联安全日志和响应。
- 增加最小验证用例与 API 自动化测试，证明校验触发、错误格式、媒体类型和敏感信息边界。
- 目标：所有后续业务 Controller 可以直接使用 Bean Validation，并自动获得一致、可供前端消费的错误响应。
- 非目标：本变更不新增具体业务接口，不定义认证、授权或各业务模块的领域异常，不改变成功响应格式，也不修改数据库结构或前端代码。
- 验收结果：自动化测试确认校验失败返回 HTTP 400、`application/problem+json`、`VALIDATION_FAILED`、请求路径、可用的 `traceId` 和确定顺序的字段错误；未知异常返回安全的 HTTP 500；既有 `/api/health` 契约保持不变。
- 主要风险：Spring MVC 不同异常类型携带的字段信息不同，若映射过度统一可能丢失诊断价值；通过分别覆盖请求体校验、方法参数、类型转换和 JSON 解析测试降低风险。异常消息可能携带 SQL、密码、密钥或客户端原始值，因此生产错误日志只记录必要请求上下文、异常类型和脱敏后的调用栈，不直接记录原始异常消息。

## Capabilities

### New Capabilities

- `api-error-handling-validation`: 定义后端统一错误响应、Bean Validation 参数失败映射、字段错误结构、traceId 与未知异常安全处理的可观察契约。

### Modified Capabilities

无。

## Impact

- 主仓库：新增本 change 的 proposal、spec、design 和 tasks；实现完成后增加对应主规格并更新 `backend` gitlink。
- 后端 submodule：预计新增明确命名的共享 Web 错误类型、`@RestControllerAdvice`、测试用验证端点或测试夹具，以及 API/架构测试；复用现有 Validation 依赖，不新增 JPA 或数据库能力。
- HTTP API：错误响应统一采用 `application/problem+json`；成功响应和既有健康检查保持兼容。
- 前端：本变更不修改前端，但为前端提供稳定的 `code` 与 `fieldErrors` 消费契约。
