## 1. 规格确认与实施门禁

- [x] 1.1 由主 Agent 向用户确认 `proposal.md`、`design.md` 与 4 份 delta specs，并在 `SPEC_CONFIRMATION` gate 持久化真实确认依据；用户已明确采用所列会话策略并要求继续实现。
- [x] 1.2 用户已选择修改密码成功后撤销其他全部活动会话，轮换并保留当前会话的短 Token、长 Token 与 CSRF Cookie，旧 Token 作废，且不延长当前会话原 7 天绝对期限；该决策已同步到 `proposal.md`、`design.md`、两个认证 delta specs 与后续验收预期。
- [x] 1.3 主 Agent 基于确认后的 artifacts 签发互不争用的后端、前端与 QA `TaskContract`，重新校验权威输入 fingerprint 和各子仓库 `git status --short --branch`。

## 2. 后端 RED 测试与数据库合同

- [x] 2.1 在 `backend/src/test/java/com/heness/project/account/` 先增加旅行上下文领域/API RED 测试，覆盖空表示、完整/部分替换、整组清空、字段边界、日期顺序、饮食限制去重、未知字段、账号隔离、CSRF、`401/403/409` 与统一 ProblemDetail。
- [x] 2.2 在 `backend/src/test/java/com/heness/project/account/` 先增加语言偏好 RED 测试，覆盖 `GET/PATCH /api/v1/accounts/me`、`zh-CN`/`en`、非法/空值、既有账号默认值、跨账号伪造与事务失败。
- [x] 2.3 在 `backend/src/test/java/com/heness/project/account/` 先增加修改密码 RED 测试，覆盖当前密码验证、8—64 位/字母/数字/确认/不得复用、统一 `PASSWORD_CHANGE_REJECTED`、密码日志排除、CSRF、事务回滚及用户已确认的当前/其他会话策略。
- [x] 2.4 在 `backend/src/test/` 的 MySQL 集成测试中先定义 Flyway、唯一/外键/日期/数量/版本约束、主从表原子替换与清空、并发版本冲突、改密摘要和会话副作用的 RED 场景。

## 3. 后端持久化与领域实现

- [x] 3.1 在 `backend/src/main/resources/db/migration/` 新增仅前向 Flyway migration，创建账号语言偏好、`account_travel_context` 与有序饮食限制结构，为既有账号补齐 `zh-CN`，且不修改或删除既有认证 Token 数据。
- [x] 3.2 在 `backend/src/main/java/com/heness/project/account/domain/` 实现旅行字段规范化、日期不变量、饮食限制边界/去重、`version` 乐观并发和语言枚举，不引入精确定位或额外账号资料。
- [x] 3.3 在 `backend/src/main/java/com/heness/project/account/infrastructure/` 与 `backend/src/main/resources/mapper/account/` 实现 MyBatis-Plus 持久化；常规 CRUD 保留 `BaseMapper<T>`，新增自定义 SQL 仅写 Mapper XML，显式列出字段并使用参数绑定。
- [x] 3.4 在 `backend/src/main/java/com/heness/project/account/application/` 实现当前账号旅行上下文查询、完整替换、幂等清空和语言偏好更新用例，以认证主体限定账号并在短事务中保持主从表一致。

## 4. 后端 API 与密码安全实现

- [x] 4.1 在 `backend/src/main/java/com/heness/project/account/api/` 实现 `GET/PUT/DELETE /api/v1/accounts/me/travel-context` DTO、Bean Validation、CSRF/Origin 保护、`version` 冲突和规范化响应。
- [x] 4.2 扩展 `GET/PATCH /api/v1/accounts/me` 的 `preferredLanguage` 合同，只开放 `zh-CN` 与 `en`，默认拒绝未知字段且不接受客户端 `accountId` 作为身份。
- [x] 4.3 在 `account` 模块实现 `POST /api/v1/accounts/me:change-password`，使用自适应单向摘要、统一安全拒绝和用户已确认的原子会话策略，不在任何响应或遥测中暴露密码材料。
- [x] 4.4 扩展全局/账号错误映射与安全日志测试，稳定返回 `VALIDATION_FAILED`、`PASSWORD_CHANGE_REJECTED`、`AUTHENTICATION_REQUIRED`、`ACCESS_DENIED`、`TRAVEL_CONTEXT_VERSION_CONFLICT`，并验证不记录旅行限制原文或原始异常。
- [x] 4.5 运行 `cd backend && ./mvnw test`，再加载根 `.env` 运行项目确认的 MySQL 8.4 集成验证；记录测试数量、失败、未运行项与清理结果，不以仅内存测试替代数据库证据。

## 5. 前端 RED 测试

- [x] 5.1 在 `frontend/src/` 对应账号设置测试中先增加旅行上下文页面 RED 用例，覆盖 Pencil 中英文状态、空/内容回显、字段校验、保存、清空、版本冲突、网络失败、草稿保留、键盘和 320—767px 行为。
- [x] 5.2 在前端 locale/导航测试中先增加登录用户语言同步 RED 用例，覆盖同一路由、Query String、hash、搜索条件、未提交表单、同步失败非阻断、刷新与重新登录恢复。
- [x] 5.3 在前端认证测试中先增加账号与安全、修改密码 RED 用例，覆盖只读账号信息、退出网络失败、三个密码字段、客户端规则、统一服务端失败、字段清空、焦点、其他会话退出提示和当前会话保持登录。
- [x] 5.4 在 `frontend/e2e/` 先增加中英文跨栈 E2E，覆盖账号 A/B 隔离、旅行上下文保存/清空、语言切换草稿保持、重新登录偏好、修改密码后旧密码失败/新密码成功、其他会话撤销、当前会话三类凭据轮换、旧 Token 作废及原 7 天绝对期限不延长。

## 6. 前端账号设置实现

- [x] 6.1 在 `frontend/src/app/[locale]/account/settings/` 实现旅行上下文、账号与安全、修改密码路由与共享设置导航，桌面忠实对应六个 Pencil 节点并提供窄屏收拢布局。
- [x] 6.2 在 `frontend/src/` 账号 API 客户端与表单组件中实现旅行上下文加载、完整替换、整组清空、`version` 冲突恢复、重复提交保护和安全的本地化 ProblemDetail 映射。
- [x] 6.3 扩展 `frontend/src/i18n/` 与 locale 切换状态管理，使登录用户切换语言时保留业务子路由、查询、hash、搜索和内存草稿，并在账号同步失败时保持目标语言与可重试状态。
- [x] 6.4 实现账号与安全只读资料、旅行摘要、退出失败保持登录，以及修改密码的显隐、规则、统一失败、成功反馈、当前设备保持登录和其他设备需重新登录提示；不得把密码写入 URL、持久化存储、日志或分析事件。
- [x] 6.5 运行 `cd frontend && pnpm lint`、`pnpm typecheck`、`pnpm test` 与项目确认的 `pnpm test:e2e`，记录真实测试数量、浏览器/视口、失败与未运行项。

## 7. 跨栈验收与审查

- [x] 7.1 QA 使用真实 MySQL 与可运行前后端验证旅行上下文字段边界、查询/替换/清空、账号 A/B 隔离、事务/并发、CSRF、统一异常和敏感日志排除，并返回结构化证据。
- [x] 7.2 QA 验证中文与英文页面、日期校验态、退出网络错误态、修改密码统一错误态、任意 P0 页面语言切换、搜索/草稿保持、刷新/重新登录与窄屏/键盘路径。
- [x] 7.3 Spec Reviewer 只读执行 4 份 delta specs 与实现/测试双向对账，逐条计算覆盖并检查 Java 21、Spring Boot 4.1、MyBatis-Plus、Mapper XML、Flyway 和项目 Rules 合规。
- [x] 7.4 Experience Reviewer 在可运行交付上走查六个 Pencil 节点对应路径、状态文案、焦点、响应式和错误恢复；阻断或高严重度问题修复后重跑受影响验证。

## 8. 证据、文档与受控交付

- [x] 8.1 主 Agent 使用 `docs/templates/openspec-change-evidence.md` 更新 change 根 `evidence.md`，汇总真实开发、QA、Spec/Experience Review、测试数量、未运行项、失败、残余风险和清理证据。
- [x] 8.2 若实际 API、模块路径或状态与 `docs/architecture/system-map.md`、`docs/standards/domain-glossary.md`、API 文档存在变化，在其所属规范源同步 CURRENT/PLANNED 状态，不复制规则正文。
- [x] 8.3 在获得逐仓库 Git 授权后，按后端/前端局部验证、精确暂存、提交、推送、远端 SHA 核验、主仓库 gitlink 更新与根验证顺序交付；未获授权时保持工作区改动，不执行 Git 写操作。
- [x] 8.4 归档前运行 `openspec validate add-travel-context-and-account-preferences --strict`、handoff 合同校验与 `git diff --check`，复核 tasks、`evidence.md`、失败、未运行项及 main specs 同步状态；存在未解决的阻断问题时不得归档。
