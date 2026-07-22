# ChinaMate 接口开发规范

## 1. 文档定位

本文档是 ChinaMate 前后端共同遵守的 HTTP API 设计与开发基线，适用于用户端、运营端以及后续内部 HTTP 接口。

规范基于以下事实形成：

- 项目采用 Java 21、Spring Boot 4.1、MyBatis-Plus 3.5.17、MySQL 8.4 和模块化单体架构。
- 后端按 `account`、`guide`、`assistant`、`community`、`support`、`moderation`、`notification`、`media` 业务模块组织。
- 前端使用 Next.js 16、React 19 和 TypeScript。
- 产品要求覆盖认证、权限、统一错误、分页、状态机、AI 异步处理、国际化、安全与可观测性。

本文档规定通用默认值。具体业务接口仍必须先通过对应 OpenSpec change 明确请求、响应、权限、状态转换、幂等性和验收场景。如果业务规格与本文档冲突，必须先修改并确认规格或本规范，不能在代码中形成隐式例外。

## 2. 核心原则

### 2.1 资源优先，而不是函数优先

API 暴露的是业务资源以及资源之间的关系，不是 Java 方法名的远程映射。

```text
错误：POST /api/getGuideList
错误：POST /api/createQuestion
正确：GET  /api/v1/guides
正确：POST /api/v1/community-questions
```

设计接口前先回答：

1. 操作对象是什么资源？
2. 操作针对集合还是单个资源？
3. 标准 HTTP 方法能否准确表达意图？
4. 如果不能，这是状态转换、子资源创建，还是纯计算？

### 2.2 协议语义与业务语义同时准确

不能为了表面 RESTful，把退款、库存释放、通知、审核等复杂动作伪装成普通字段修改。接口既要正确使用 HTTP 方法，也要显式表达真实业务意图。

### 2.3 契约独立于内部模型

- API Request、API Response、应用层 Command/Query、领域对象和数据库行对象分别建模。
- 不直接向客户端暴露数据库行对象、MyBatis Mapper 参数对象或领域内部状态。
- 接口字段变化不能被数据库字段重命名意外带出。
- 密码、密码摘要、模型密钥、内部审核信息等敏感字段永远不进入普通响应。

### 2.4 一致性优先于个人偏好

新增接口应复用本规范中的命名、状态码、分页和错误格式。确有业务理由的例外必须写入对应 OpenSpec change，并说明取舍和兼容性。

## 3. URL 与资源命名

### 3.1 基础路径与版本

- 业务接口统一使用 `/api/v1` 前缀。
- `/actuator/**` 属于 Spring Boot 运维端点，不纳入业务 API 版本。
- 现有 `/api/health` 是已确认兼容契约，保留原路径，不为了形式统一强制迁移。
- 只有出现不兼容的公开契约变化时才增加主版本；禁止把每次字段调整都升级为新版本。

### 3.2 命名规则

- 集合使用英文复数名词：`guides`、`notifications`、`community-questions`。
- URL 使用小写 `kebab-case`；JSON 字段和查询参数使用 `camelCase`。
- URL 中不使用 `get`、`query`、`create`、`update`、`delete` 等 CRUD 动词。
- 路径参数使用有业务含义的名称，如 `{guideId}`、`{conversationId}`，不统一写成含义不明的 `{id}`。
- URL 不包含文件扩展名，不用下划线，不把数据库表名或 Java 类名直接暴露为协议名称。

```text
错误：GET /api/v1/get_user/{id}
错误：GET /api/v1/CommunityQuestion/{id}
正确：GET /api/v1/accounts/{accountId}
正确：GET /api/v1/community-questions/{questionId}
```

### 3.3 资源层级

- URL 应表达稳定的归属关系。
- 默认最多保留一层父子嵌套，避免超过两级资源集合。
- 能被独立标识、查询或授权的资源优先提升为顶层资源。
- 同一个资源不得同时出现多套等价地址。

```text
推荐：GET /api/v1/community-questions/{questionId}/answers
推荐：GET /api/v1/answers/{answerId}
避免：GET /api/v1/users/{userId}/questions/{questionId}/answers/{answerId}/comments
```

## 4. 标准方法与 HTTP 语义

| 目的 | HTTP 方法 | 路径 | 安全 | 幂等 | 默认成功状态 |
| --- | --- | --- | --- | --- | --- |
| 列出资源 | `GET` | `/resources` | 是 | 是 | `200 OK` |
| 获取资源 | `GET` | `/resources/{resourceId}` | 是 | 是 | `200 OK` |
| 创建资源 | `POST` | `/resources` | 否 | 否 | `201 Created` |
| 整体替换 | `PUT` | `/resources/{resourceId}` | 否 | 是 | `200 OK` 或 `204 No Content` |
| 局部更新 | `PATCH` | `/resources/{resourceId}` | 否 | 取决于定义 | `200 OK` |
| 删除资源 | `DELETE` | `/resources/{resourceId}` | 否 | 是 | `204 No Content` |

### 4.1 GET

- 只读，不改变业务状态。
- 不通过 GET 完成标记已读、生成内容、消耗额度等有副作用操作。
- GET 不接收请求体；简单条件使用 Query String。
- 结果可以缓存时，应在具体规格中定义 `Cache-Control`、`ETag` 或其他缓存策略。

### 4.2 POST

- 用于在集合中创建新资源，或者执行有副作用的自定义方法。
- 创建成功返回 `201 Created`，并通过 `Location` 响应头给出新资源地址。
- 可能重复扣费、重复发布、重复生成任务的 POST 必须在规格中定义幂等策略，不能只依赖前端按钮禁用。

### 4.3 PUT 与 PATCH

- `PUT` 表示整体替换。客户端必须提交资源完整的新状态；未提供字段可能被重置。
- ChinaMate 普通资料修改默认使用 `PATCH`，不把局部更新伪装成 `PUT`。
- `PATCH` 只允许修改请求 DTO 明确暴露的字段。服务端生成字段、权限字段和受状态机保护的字段不得出现在通用更新 DTO 中。
- 更新成功默认返回更新后的资源响应，便于前端获得规范化后的最终状态。

### 4.4 DELETE

- 立即删除或按业务定义完成软删除时，默认返回 `204 No Content`，响应体为空。
- 客户端重复删除已经不存在或已不可见的资源时返回 `404 Not Found`；资源最终状态仍满足“已删除”，因此不破坏 HTTP 方法的幂等性。
- “停用”“归档”“撤回”不是天然的删除，应根据业务语义设计为状态更新或自定义方法。
- 长耗时删除返回 `202 Accepted` 和可查询的任务/操作资源。

## 5. 非标准业务行为

标准 CRUD 无法准确表达时，按以下顺序选择方案。

### 5.1 简单字段修改

如果行为仅修改普通可编辑字段，没有专属权限、状态机或额外副作用，使用 `PATCH`。

```http
PATCH /api/v1/accounts/me
Content-Type: application/json

{
  "displayName": "Li"
}
```

### 5.2 创建子资源

如果行为会产生可独立记录、查询或审计的对象，将其建模为资源。

```text
POST /api/v1/guides/{guideId}/feedback
POST /api/v1/content-reports
POST /api/v1/assistant-conversations/{conversationId}/messages
```

收藏关系适合作为资源，并优先使用幂等方法：

```text
PUT    /api/v1/accounts/me/favorite-guides/{guideId}
DELETE /api/v1/accounts/me/favorite-guides/{guideId}
```

### 5.3 自定义方法

当操作包含状态机校验、专属权限或显著副作用，使用自定义方法：

```text
POST /api/v1/community-questions/{questionId}:select-best-answer
POST /api/v1/community-questions/{questionId}:close
POST /api/v1/guides/{guideId}:publish
POST /api/v1/content-reports/{reportId}:resolve
```

Spring MVC 可以用静态冒号后缀表达自定义方法，不需要采用 Gin 为路由参数妥协的斜杠写法：

```java
@PostMapping("/{questionId}:close")
public QuestionResponse closeQuestion(@PathVariable long questionId) {
    return closeQuestionHandler.handle(questionId);
}
```

要求：

- 动词使用小写 `kebab-case`，表达明确业务意图。
- 默认使用 `POST`；没有副作用的纯计算才可以考虑 `GET`。
- 状态转换规则必须位于领域层，Controller 不写业务状态机。
- 已处于目标状态的重复请求，若业务定义为幂等，应返回当前资源；与目标状态冲突时返回 `409 Conflict`。
- 不允许通过普通 PATCH 绕过自定义方法，例如 `UpdateQuestionRequest` 不得暴露 `status` 或 `bestAnswerId`。

### 5.4 纯计算与长耗时任务

- 简单、无副作用、参数较短的计算可以使用 `GET /resources:calculate-x?param=value`。
- 参数复杂、可能包含敏感内容或 URL 长度不可控时使用 `POST`，即使计算本身只读。
- AI 生成、图片处理等长耗时操作优先返回 `202 Accepted`，响应中提供任务或消息资源及状态查询地址。
- 事务内不得等待模型、对象存储、网络或文件 I/O。

## 6. Java Request、Response 与 PATCH 三态

### 6.1 DTO 规则

- Request 和 Response 放在所属模块的 `api` 范围。
- 简单不可变 DTO 优先使用 Java `record`。
- Request 使用 Bean Validation；Controller 参数使用 `@Valid`。
- DTO 名称按用例命名，如 `RegisterAccountRequest`、`UpdateTravelContextRequest`、`GuideResponse`。
- 禁止使用一个 `UserDTO` 同时承担创建、更新、数据库映射和响应。
- 不因多模块都有 CRUD 就创建全局泛型 `BaseController`。项目强调业务模块与用例边界，少量协议样板优于错误抽象。

```java
public record CreateQuestionRequest(
        @NotBlank @Size(max = 120) String title,
        @NotBlank @Size(max = 10_000) String content,
        @NotNull Long cityId,
        @NotNull QuestionCategory category) {
}
```

### 6.2 Java PATCH 的真实问题

Go 示例使用指针区分“未传字段”和“传入零值”。Java 中 `int`、`boolean` 等基本类型同样有默认值问题，因此 PATCH Request 禁止使用基本类型承载可选字段，应使用 `Integer`、`Boolean` 等包装类型。

但包装类型只能区分“有值”和 `null`，默认不能区分：

1. JSON 中没有该字段；
2. JSON 中显式传入 `null`；
3. JSON 中传入实际值。

项目按字段语义采用以下规则：

- 不允许为空的业务字段：`null` 表示未提交、不更新；显式 JSON `null` 必须在反序列化或协议校验阶段拒绝，不能被当作“未提交”静默忽略。
- 允许清空的业务字段：必须采用能表达三态的专用类型或单独的清空动作，并在对应 OpenSpec change 中确认；禁止只用普通 nullable 字段猜测客户端意图。
- 状态机字段：不进入普通 PATCH Request，通过自定义方法变更。

对于不允许显式 `null` 的 PATCH 字段，可使用 Jackson 的 null 处理约束；具体注解方式应由测试证明当前 Spring Boot/Jackson 版本行为：

```java
public record UpdateAccountProfileRequest(
        @JsonSetter(nulls = Nulls.FAIL)
        @Size(min = 1, max = 40)
        String displayName,

        @JsonSetter(nulls = Nulls.FAIL)
        SupportedLanguage preferredLanguage) {
}
```

应用层只更新非 `null` 字段，并测试以下场景：字段缺失、合法值、数值 `0`、布尔值 `false`、空字符串、显式 `null`、未知字段。

## 7. 请求约定

### 7.1 Content-Type 与编码

- JSON 请求使用 `Content-Type: application/json`，UTF-8 编码。
- 文件上传使用 `multipart/form-data`，并在 `media` 模块完成类型、大小、内容和权限校验。
- 不接受与接口契约无关的 Content-Type。

### 7.2 字段与时间

- JSON 字段统一使用 `camelCase`。
- 标识符在协议中作为不透明值，不要求前端理解数据库类型或生成规则。
- 金额使用最小货币单位的整数，例如 `amountInCents`；禁止使用浮点数表示金额。
- 时间点使用带时区的 ISO 8601 字符串，例如 `2026-07-22T10:30:00+08:00` 或 UTC `Z`。
- 仅表示日期时使用 `YYYY-MM-DD`，不要附加虚假时区。
- 枚举值使用稳定的大写 `SNAKE_CASE`，不能直接依赖 Java enum 的声明顺序。

### 7.3 校验

- 协议格式校验放在 API 层：必填、长度、范围、格式、集合大小。
- 业务不变量放在领域层：状态能否转换、是否允许选择最佳回答、攻略能否发布。
- 权限和用例编排放在应用层。
- 不把客户端输入原样拼接到 SQL、日志、错误信息、Prompt 或路径中。
- 默认拒绝未知 JSON 字段，避免客户端以为字段已生效但服务端实际忽略；兼容例外必须显式记录。

### 7.4 查询、过滤与排序

- 查询参数使用 `camelCase`。
- 一个参数只表达一个含义；同名参数的多值语义必须在规格中明确。
- 排序字段必须来自服务端封闭白名单，禁止把客户端字段名直接拼入 SQL `${}`。
- 文本搜索使用 `query`；精确筛选使用明确字段，如 `cityId`、`status`、`category`。
- 非法筛选值返回 `400 Bad Request`，不静默退回默认值。

## 8. 分页与列表响应

所有可能持续增长的集合必须分页，禁止一次返回全部社区内容、通知、AI 会话或审核记录。

### 8.1 普通列表默认分页

- `page`：从 `1` 开始，默认 `1`。
- `size`：默认 `20`，最大 `100`。
- `sort`：使用规格允许的字段和方向，例如 `createdAt,desc`。
- `total` 只有在产品确实需要总数时返回；昂贵的总数查询不能只为形式统一执行。

```json
{
  "items": [],
  "page": 1,
  "size": 20,
  "total": 0,
  "hasNext": false
}
```

### 8.2 时间流与高频变化列表

通知、消息、动态流等高频变化集合优先使用游标分页：

```json
{
  "items": [],
  "nextCursor": null,
  "hasNext": false
}
```

游标必须是不透明字符串。客户端不能构造、解析或修改游标；排序键必须稳定，并包含唯一标识作为最终排序条件。

## 9. 响应与状态码

### 9.1 成功响应

- 单资源成功时直接返回资源 Response，不额外套无信息量的 `code/message/data` 三层包装。
- 列表使用本规范的分页对象。
- `204 No Content` 的响应体必须为空。
- 服务端生成的字段、标准化结果和最终状态通过 Response 返回。

### 9.2 常用状态码

| 状态码 | 使用场景 |
| --- | --- |
| `200 OK` | 查询、局部更新、自定义方法同步完成 |
| `201 Created` | 资源创建成功 |
| `202 Accepted` | 已接受 AI、图片处理等异步任务 |
| `204 No Content` | 删除成功或无需返回内容 |
| `400 Bad Request` | JSON、参数格式或 Bean Validation 失败 |
| `401 Unauthorized` | 未认证或会话失效 |
| `403 Forbidden` | 已认证但没有执行权限 |
| `404 Not Found` | 资源不存在或按安全策略不可见 |
| `409 Conflict` | 状态机冲突、并发版本冲突、唯一性冲突 |
| `413 Payload Too Large` | 上传或请求体超过限制 |
| `415 Unsupported Media Type` | Content-Type 不受支持 |
| `422 Unprocessable Content` | 格式合法但组合语义无法处理；仅在规格明确时使用 |
| `429 Too Many Requests` | 登录、AI 额度或接口限流 |
| `500 Internal Server Error` | 未预期服务端错误 |
| `503 Service Unavailable` | AI、存储等能力暂时不可用且不能降级 |

禁止所有响应都返回 HTTP 200，再把真实错误藏在业务 `code` 中。

## 10. 统一错误契约

错误响应采用 Spring `ProblemDetail` 对应的 `application/problem+json` 结构，并在稳定字段上扩展业务错误码：

```json
{
  "type": "https://chinamate.example/problems/validation-failed",
  "title": "请求参数校验失败",
  "status": 400,
  "detail": "请检查提交的字段",
  "instance": "/api/v1/community-questions",
  "code": "VALIDATION_FAILED",
  "traceId": "01J...",
  "fieldErrors": [
    {
      "field": "title",
      "code": "Size",
      "message": "标题长度不能超过 120 个字符"
    }
  ]
}
```

要求：

- `code` 是前端稳定判断依据，使用大写 `SNAKE_CASE`；不能让前端解析 `detail`。
- `detail` 和字段消息支持中英文，但不得泄露堆栈、SQL、表名、密钥、密码摘要或内部供应商响应。
- `traceId` 用于关联服务端日志，不返回完整内部异常。
- 全局异常映射使用 `@RestControllerAdvice`；业务异常在应用/领域层保持与 HTTP 解耦，由 API 层映射状态码。
- 未识别异常统一返回 `500`，服务端记录带 traceId 的安全日志。

建议映射：

| 异常语义 | HTTP 状态 | 示例业务码 |
| --- | --- | --- |
| 参数非法 | `400` | `VALIDATION_FAILED` |
| 未登录 | `401` | `AUTHENTICATION_REQUIRED` |
| 无权限 | `403` | `ACCESS_DENIED` |
| 资源不存在 | `404` | `GUIDE_NOT_FOUND` |
| 状态冲突 | `409` | `QUESTION_ALREADY_CLOSED` |
| 登录尝试受限 | `429` | `LOGIN_RATE_LIMITED` |
| AI 未启用 | `503` | `AI_CAPABILITY_UNAVAILABLE` |

## 11. 认证、权限与安全

- 身份来自服务端认证上下文，不接受请求体中的 `userId` 作为当前用户身份。
- Controller 只完成身份上下文到应用用例的转换；授权规则在应用层明确执行。
- `401` 表示没有有效身份，`403` 表示身份有效但无权操作。
- 对可能导致资源枚举的个人资源，可按对应安全规格统一返回 `404`。
- 注册、登录错误不得暴露账号是否存在；重复注册可按已确认产品契约返回安全提示。
- 密码和密码摘要不得出现在 Response、日志、异常、埋点或测试快照中。
- AI API Key、数据库凭据和对象存储凭据只存在于服务端配置。
- 上传接口必须验证大小、MIME、实际内容、文件名、数量、所有权和生命周期。
- CORS、CSRF、Cookie 属性、会话过期和限流策略必须在认证 change 中明确，不能使用开发环境默认值代替生产设计。

## 12. 幂等、并发与状态机

### 12.1 幂等

- `GET`、`PUT`、`DELETE` 按 HTTP 语义保持幂等。
- 对重复发布、创建 AI 消息、上传确认等高风险 POST，在规格中定义 `Idempotency-Key`、业务唯一键或等效去重机制。
- 幂等键必须与认证主体、目标操作和有效期绑定；相同键但请求内容不同返回冲突。
- 前端防抖和按钮禁用只能改善体验，不能代替服务端幂等。

### 12.2 并发

- 可能发生覆盖的资源应使用版本号、更新时间或其他乐观并发控制。
- 版本冲突返回 `409 Conflict`，响应不能静默覆盖新数据。
- “选择最佳回答并将问题标记为已解决”等多数据变更必须在同一短事务内原子完成。
- 事务中不执行 AI、HTTP、对象存储或文件 I/O。

### 12.3 状态机

- 状态转换方法和不变量位于 `domain`。
- API Request 不能暴露任意 `status` 修改入口。
- 应用层编排事务、权限与副作用；Controller 不通过 `if/else` 复制状态规则。
- 非核心通知、埋点等副作用在事务成功后触发；失败策略由具体 change 规定。

## 13. Spring Boot 工程落地

### 13.1 模块职责

```text
com.heness.project.<module>/
├── api/             # Controller、Request、Response、HTTP 错误映射
├── application/     # Handler、Command、Query、事务与端口
├── domain/          # 领域对象、状态机、不变量、仓储端口
└── infrastructure/  # MyBatis、Spring AI、对象存储适配器
```

- Controller 只依赖本模块应用用例，不直接调用 Mapper、数据库行对象或 `ChatModel`。
- 必需依赖使用构造器注入和 `private final`。
- 服务保持无状态。
- 不机械创建 `Service`/`ServiceImpl`、统一 CRUD 接口或万能工具类。
- 跨模块只调用目标模块公开的 `application` 契约。

### 13.2 Controller 示例

```java
@RestController
@RequestMapping("/api/v1/community-questions")
final class CommunityQuestionController {

    private final CreateQuestionHandler createQuestionHandler;
    private final CloseQuestionHandler closeQuestionHandler;

    CommunityQuestionController(
            CreateQuestionHandler createQuestionHandler,
            CloseQuestionHandler closeQuestionHandler) {
        this.createQuestionHandler = createQuestionHandler;
        this.closeQuestionHandler = closeQuestionHandler;
    }

    @PostMapping
    ResponseEntity<QuestionResponse> create(
            @Valid @RequestBody CreateQuestionRequest request) {
        var response = createQuestionHandler.handle(request.toCommand());
        var location = URI.create("/api/v1/community-questions/" + response.id());
        return ResponseEntity.created(location).body(response);
    }

    @PostMapping("/{questionId}:close")
    QuestionResponse close(@PathVariable long questionId) {
        return closeQuestionHandler.handle(questionId);
    }
}
```

示例只表达协议边界。真实代码还必须传入认证主体、处理 ID 类型、错误映射和业务权限。

### 13.3 数据访问

- 数据库结构只通过新的 Flyway migration 修改。
- Mapper 与 XML 位于所属模块的 `infrastructure` 和 `resources/mapper/<module>/`。
- 查询显式列出字段，不使用 `SELECT *`。
- 业务值使用 `#{}` 参数绑定。
- 排序字段等无法参数化的标识符只能来自服务端封闭白名单；用户输入不得进入 `${}`。
- API 分页语义与 MyBatis-Plus 分页对象在适配层转换，不直接返回框架分页类型。

## 14. ChinaMate 接口建模示例

下表是命名和建模示例，不代表业务契约已经冻结；最终以各模块 OpenSpec change 为准。

| 业务能力 | 推荐建模 | 说明 |
| --- | --- | --- |
| 注册账号 | `POST /api/v1/accounts` | 创建账号资源 |
| 登录 | `POST /api/v1/sessions` | 创建会话资源 |
| 退出当前会话 | `DELETE /api/v1/sessions/current` | 删除当前会话 |
| 查询当前账号 | `GET /api/v1/accounts/me` | 认证上下文解析当前账号 |
| 修改个人资料 | `PATCH /api/v1/accounts/me` | 只开放普通可编辑字段 |
| 修改密码 | `POST /api/v1/accounts/me:change-password` | 需要校验旧密码并产生安全副作用 |
| 攻略列表 | `GET /api/v1/guides?page=1&size=20` | 分页、筛选、搜索 |
| 收藏攻略 | `PUT /api/v1/accounts/me/favorite-guides/{guideId}` | 收藏关系幂等创建 |
| 取消收藏 | `DELETE /api/v1/accounts/me/favorite-guides/{guideId}` | 收藏关系幂等删除 |
| 攻略反馈 | `POST /api/v1/guides/{guideId}/feedback` | 创建可审计反馈资源 |
| 创建 AI 会话 | `POST /api/v1/assistant-conversations` | 创建会话资源 |
| 发送问题 | `POST /api/v1/assistant-conversations/{conversationId}/messages` | 创建消息，必要时返回 `202` |
| AI 会话转社区草稿 | `POST /api/v1/assistant-conversations/{conversationId}:create-community-draft` | `support` 模块编排，不直接跨表访问 |
| 发布社区问题 | `POST /api/v1/community-questions` | 创建问题资源 |
| 发布回答 | `POST /api/v1/community-questions/{questionId}/answers` | 创建从属资源 |
| 选择最佳回答 | `POST /api/v1/community-questions/{questionId}:select-best-answer` | 原子状态转换 |
| 关闭问题 | `POST /api/v1/community-questions/{questionId}:close` | 显式业务状态转换 |
| 创建举报 | `POST /api/v1/content-reports` | 创建独立审计资源 |
| 通知列表 | `GET /api/v1/notifications?cursor=...` | 高频变化列表使用游标 |
| 标记单条已读 | `PATCH /api/v1/notifications/{notificationId}` | 简单字段修改，无额外副作用时使用 |
| 全部标记已读 | `POST /api/v1/notifications:mark-all-read` | 集合级自定义方法 |

## 15. 测试与验证

每个新增或变更接口至少覆盖与风险相称的测试。

### 15.1 Domain 测试

- 状态允许和禁止的转换。
- 业务不变量与边界值。
- 重复执行的幂等行为。
- 不启动 Spring、MyBatis 或外部服务。

### 15.2 Application 测试

- 权限、用例编排、端口调用和事务外副作用。
- 资源不存在、冲突、重复请求和外部能力失败。
- 跨模块只经过公开应用契约。

### 15.3 API 测试

- 正确 HTTP 方法、URL、状态码、响应头和 JSON 结构。
- Bean Validation、非法 JSON、未知字段和不支持的 Content-Type。
- `401`、`403`、`404`、`409`、`429` 等失败路径。
- PATCH 的字段缺失、`0`、`false`、空字符串、显式 `null` 和禁止字段。
- 错误响应不泄露内部异常和敏感信息。

### 15.4 持久化与集成测试

- Flyway 与 MyBatis 在真实 MySQL/Testcontainers 上的行为。
- 分页稳定性、唯一约束、并发更新和事务原子性。
- SQL 参数绑定与允许的排序白名单。

### 15.5 验证命令

```bash
cd backend
./mvnw -Dtest=ArchitectureRulesTests test
./mvnw test
git diff --check
```

根级文档或 Harness 变更还必须运行：

```bash
./scripts/check-harness.sh
```

## 16. 接口评审清单

设计评审时逐项确认：

- [ ] URL 表达资源而不是 Java 方法名，集合使用复数名词。
- [ ] HTTP 方法、安全性、幂等性和状态码一致。
- [ ] 嵌套层级合理，没有同一资源的多套等价 URL。
- [ ] 非标行为已在 PATCH、子资源、自定义方法之间作出有依据的选择。
- [ ] Request、Response、应用模型、领域模型和数据库模型没有混用。
- [ ] PATCH 已处理未传、零值、`false`、空字符串和显式 `null`。
- [ ] 状态机字段不能通过普通更新 DTO 绕过。
- [ ] 列表已分页，排序字段来自服务端白名单。
- [ ] 成功和错误响应遵循统一契约，前端不依赖错误文案做判断。
- [ ] 认证、授权、资源可见性和敏感信息边界明确。
- [ ] POST 重复提交、并发更新和事务原子性有明确策略。
- [ ] 外部 AI、网络、文件或对象存储 I/O 不在数据库事务内。
- [ ] OpenSpec 场景、自动化测试和实际验证命令齐全。

## 17. 从参考文章吸收与舍弃的内容

### 17.1 吸收

- 资源导向设计：URL 使用名词和层级，操作交给 HTTP 方法表达。
- 标准 CRUD 的安全性、幂等性和精准语义。
- 默认使用 PATCH 做局部更新，谨慎使用整体替换的 PUT。
- 复杂状态转换和副作用使用自定义方法，不滥用 PATCH。
- Request DTO 与内部实体分离，避免未提交字段覆盖真实数据。
- Controller 负责协议适配，业务规则下沉到业务层。

### 17.2 不直接照搬

- 原文 Gin 的 `/:id/action` 是框架妥协；Spring MVC 采用更明确的 `/{id}:action`。
- 原文 Go 指针 DTO 转换为 Java 包装类型、Jackson null 约束和必要时的三态类型。
- 原文泛型 `BaseController` 不进入本项目；它与模块化单体的用例边界及禁止共享万能基类的规则冲突。
- 原文内存 Map、Gin Context 和 Handler 结构不属于本项目实现方式。
- DELETE 重复调用、自定义动作幂等性等存在语境差异的观点，以本文档明确的项目规则为准。
