## 1. API 契约测试（RED）

- [x] 1.1 在 `backend/src/test/java/com/heness/project/shared/web/error/GlobalExceptionHandlerTests.java` 建立测试专用 Controller 与 Request fixture，覆盖请求体单字段、多字段、嵌套集合、查询参数约束、缺少必填参数、类型转换、非法 JSON 和未知异常；运行 `cd backend && ./mvnw -Dtest=GlobalExceptionHandlerTests test`，确认测试因统一错误能力尚不存在而以正确原因失败。
- [x] 1.2 在同一测试中断言 HTTP 状态、`application/problem+json`、`type/title/status/detail/instance/code/traceId`、`fieldErrors` 稳定顺序和不回显原始值，并保留 `backend/src/test/java/com/heness/project/health/HealthControllerTests.java` 对既有成功响应未包装的断言。

## 2. 统一错误实现（GREEN / REFACTOR）

- [x] 2.1 在 `backend/src/main/java/com/heness/project/shared/web/error/` 新增明确命名的通用错误码、字段错误值对象和 ProblemDetail 创建能力，输出稳定 URN、业务码、请求路径、traceId 与确定顺序的字段错误，且不保存或返回 rejected value。
- [x] 2.2 在 `backend/src/main/java/com/heness/project/shared/web/error/` 新增 `@RestControllerAdvice`，分别映射请求体 Bean Validation、Spring MVC 方法参数校验、必填参数缺失、类型转换失败和 JSON 解析失败，并运行 `cd backend && ./mvnw -Dtest=GlobalExceptionHandlerTests test` 验证所有 400 场景通过。
- [x] 2.3 在统一异常处理器中增加未知异常的安全 500 映射和参数化错误日志，确保日志与响应使用同一 traceId，且响应不包含异常类名、堆栈、SQL、密钥或请求原始值；运行对应 500 场景测试。
- [x] 2.4 复核 `backend/src/test/java/com/heness/project/architecture/ArchitectureRulesTests.java` 对 `shared.web.error` 的覆盖；仅在现有规则无法证明 shared 不依赖业务模块时补充最小架构断言，并运行 `cd backend && ./mvnw -Dtest=ArchitectureRulesTests test`。

## 3. 回归验证与文档一致性

- [x] 3.1 运行 `cd backend && ./mvnw test`，确认统一错误测试、健康检查、配置测试和架构测试全部通过，且默认不访问 MySQL 或外部 AI 服务。
- [x] 3.2 运行 `cd backend && git diff --check` 与根目录 `./scripts/check-harness.sh`，检查空白、冲突标记、submodule 和 OpenSpec/Harness 基础结构。
- [x] 3.3 对照 `docs/standards/api-development-guidelines.md` 与本 change 的 spec 自查成功/错误响应、状态码、字段安全和 `traceId` 契约；如实现揭示规格错误，先更新 `openspec/changes/add-api-error-handling-validation/` artifacts 再继续。

## 4. Submodule 交付与规格同步（需单独 Git 授权）

- [x] 4.1 获得用户明确授权后，在 `backend/` 确认 `main` 分支和 staged diff 只包含本变更，提交并推送后端仓库，再验证新提交可从 `origin/main` 到达。
- [x] 4.2 回到主仓库，将 `api-error-handling-validation` delta spec 同步到 `openspec/specs/`，确认 change 无未完成实现或验证任务，并运行 OpenSpec 校验。
- [x] 4.3 获得用户明确授权后，在主仓库仅暂存本 change artifacts、同步后的规格和 `backend` gitlink，提交并按用户要求决定是否推送；不得夹带现有无关修改。

## 5. 异常日志敏感信息回归修复

- [x] 5.1 在 `backend/src/test/java/com/heness/project/shared/web/error/GlobalExceptionHandlerTests.java` 增加日志安全断言：未知异常日志保留 `traceId` 和异常类型，但不得包含异常消息中的敏感值；运行对应测试并确认现有实现因泄露敏感值而失败。
- [x] 5.2 修改 `backend/src/main/java/com/heness/project/shared/web/error/GlobalExceptionHandler.java`，不再把原始异常消息写入生产日志，同时保留异常类型和脱敏调用栈用于定位。
- [x] 5.3 运行 `cd backend && ./mvnw -Dtest=GlobalExceptionHandlerTests test`、`cd backend && ./mvnw test`、两个仓库的 `git diff --check`、根级 Harness 与 OpenSpec 严格校验；未经单独 Git 授权不提交或推送。
