## Context

后端目前只有健康检查接口，`pom.xml` 已包含 Spring Boot Validation 与 Web MVC 能力，但源码中没有 `@RestControllerAdvice`、统一错误模型或参数校验失败测试。主仓库接口规范已经规定：成功响应直接返回资源 DTO；失败响应采用 Spring `ProblemDetail`、真实 HTTP 状态、稳定业务码、`traceId`，参数校验失败额外返回 `fieldErrors`。

这是跨业务模块共享的 HTTP 协议能力。它不属于 `account`、`guide` 等任一业务域，且会被所有后续 Controller 以相同语义复用，因此符合 `shared` 准入条件。实现必须兼容 Java 21、Spring Boot 4.1 和现有模块化单体架构，不引入 JPA、数据库迁移或前端改动。

## Goals / Non-Goals

**Goals:**

- 建立唯一的 API 异常到 `ProblemDetail` 映射入口。
- 让请求体、查询参数、路径参数校验失败向前端返回可定位、可稳定排序的字段错误。
- 为格式错误、类型转换错误和未知服务端异常提供安全且可测试的默认映射。
- 保持成功响应与 `/api/health` 兼容，并为未来业务异常扩展留下明确入口。

**Non-Goals:**

- 不在本次定义账号、攻略、社区等具体业务异常层次。
- 不实现认证、授权、限流、国际化消息切换或前端表单展示。
- 不引入全局成功包装、第三方异常处理库、数据库结构或新的运行时基础设施。
- 不把所有 `IllegalArgumentException` 粗略映射为 400；没有明确协议语义的异常继续按 500 失败关闭。

## Decisions

### 1. 使用 Spring ProblemDetail，不创建泛型 Result 包装

统一处理器使用 Spring MVC 原生 `ProblemDetail` 作为错误载体，通过扩展属性加入 `code`、`traceId` 和必要时的 `fieldErrors`。成功响应保持原样。

选择原因：这与已确认接口规范一致，能正确表达 HTTP 语义，并由 Spring 原生支持 `application/problem+json`。备选的 `Result<T>{code,message,data}` 会迫使成功与失败都被包装，也容易把真实错误藏在 HTTP 200 中，因此不采用。

### 2. 将跨模块错误能力放在 shared.web.error

计划在 `com.heness.project.shared.web.error` 下放置明确命名的错误处理器、错误码和字段错误值对象，不建立 `BaseController`、万能工具类或业务异常基类。业务模块未来只在自身 application/domain 中声明与 HTTP 解耦的业务失败，再由 API 边界增加显式映射。

选择原因：统一错误会被多个业务模块以相同语义复用，属于无单一业务归属的技术能力。放在全局 `config` 会混合配置与协议模型；复制到每个模块会导致契约漂移。

### 3. 按 Spring MVC 异常类别分别提取字段信息

统一处理器分别处理以下输入边界：

- 请求体 Bean Validation：从字段绑定错误提取完整字段路径、约束码和受控消息。
- 方法参数校验：从 Spring MVC 方法校验结果提取面向协议的参数名与约束信息。
- 缺少必填参数：构造该请求参数对应的字段错误。
- 类型转换失败：构造目标参数的 `typeMismatch` 字段错误，但不返回原始值。
- JSON 无法解析：返回 `MALFORMED_REQUEST`，不尝试从底层 Jackson 文本拼装不可靠字段错误。

所有 `fieldErrors` 在输出前按 `field`、`code`、`message` 排序；同一约束产生完全相同的重复项时去重。保留嵌套属性和集合下标，以便前端准确绑定表单项。

选择原因：这些异常携带的元数据不同，强行用一个模糊的 `Exception` 分支会丢失字段信息。直接返回 Spring 的 `BindingResult` 又会暴露被拒绝值和框架内部结构，因此只投影白名单字段。

### 4. 使用稳定错误码与稳定问题类型

第一阶段定义三个通用错误码：`VALIDATION_FAILED`、`MALFORMED_REQUEST`、`INTERNAL_SERVER_ERROR`。`type` 使用稳定的 ChinaMate URN（例如 `urn:chinamate:problem:validation-failed`），避免把尚未确定的生产域名写死为可解析 URL。`title`、`detail` 和校验消息使用中文默认文案，但前端逻辑只依赖 `code` 和字段路径。

选择原因：错误码必须可供程序判断，而文案将来可能国际化。使用 URN 既满足 ProblemDetail 的 URI 类型要求，也不需要新增环境配置或伪造文档地址。

### 5. traceId 在错误创建时解析或生成，并用于 500 日志关联

错误工厂优先读取当前日志上下文中已有的 traceId；不存在时生成随机 UUID 字符串。响应始终带非空 traceId。未知异常处理器以参数化日志记录请求方法、路径、traceId、异常类型和脱敏后的调用栈，但不直接记录原始异常对象或异常消息，避免异常消息携带 SQL、密码、密钥、请求参数值或认证信息进入日志。

选择原因：当前项目没有分布式追踪基础设施，单纯为本功能增加 Micrometer Tracing 超出范围。错误级 traceId 已能支持前端报错与后端日志关联；异常类型和脱敏调用栈保留定位价值，同时不信任第三方异常消息。未来接入真实链路追踪时可优先复用已有上下文而无需修改响应契约。

### 6. 用测试专用 Controller 验证协议，不新增演示业务接口

API 测试在测试源码中注册最小 Controller/Request fixture，分别触发请求体校验、方法参数校验、缺参、类型转换、JSON 解析和未知异常。生产源码只包含通用错误能力，不为测试或演示新增公开端点。既有健康检查测试继续验证成功契约未被包装。

选择原因：当前没有真实业务接口，测试夹具能先以 RED 证明缺失行为，同时避免污染生产 API。使用 MockMvc 检查状态、媒体类型、JSON 字段与敏感信息边界。

## Risks / Trade-offs

- [Spring Boot 4.1 方法校验异常结构与旧版示例不同] → 以当前依赖可编译 API 和 MockMvc 测试为准，不照搬旧版 `ConstraintViolationException` 教程。
- [校验消息可能由未来自定义注解拼入敏感值] → 通用层永不返回 rejected value；代码评审要求校验消息使用受控模板，测试覆盖响应不含原始输入。
- [捕获 `Exception` 可能掩盖开发期问题] → 只在 HTTP 边界失败关闭；500 保留异常类型、脱敏调用栈和 traceId，测试同时断言客户端响应与服务端日志不泄露异常消息中的敏感值。
- [测试专用 Controller 与真实业务注解组合存在差异] → 后续每个业务接口仍必须增加自身 API 测试；本变更只保证通用映射基线。

## Migration Plan

1. 在后端先添加 API 契约测试并确认因缺少统一处理器而失败。
2. 添加最小共享错误模型、工厂和 `@RestControllerAdvice`，使测试通过。
3. 运行相关 API 测试、架构测试、完整后端测试与根级 Harness 检查。
4. 本变更不改变成功契约和数据库，无数据迁移；如需回滚，可移除新增 advice 与共享类型，既有健康检查仍可独立运行。
5. 只有获得用户单独授权后，才提交/推送后端仓库并更新主仓库 gitlink。

## Open Questions

无。具体业务异常码、国际化语言选择和分布式追踪接入由后续独立业务 change 决定。
