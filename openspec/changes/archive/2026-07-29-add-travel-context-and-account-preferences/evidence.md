# `add-travel-context-and-account-preferences` 交付证据

> 本文件只记录实际发生的验证与审查。状态统一使用 `PASS`、`FAIL`、`BLOCKED`、`NOT_RUN`；不适用时写明原因，不根据计划或 task checkbox 推测结果。

## 1. 基本信息

- Change：`add-travel-context-and-account-preferences`
- 当前结论：`PASS_WITH_RESIDUAL_RISKS`（实现、QA、Spec Review、Experience Review、main specs 同步和子仓库远端交付均通过；仅保留已披露的最终 Playwright 重跑阻塞）
- 最后更新：`2026-07-29 19:23 +08:00`
- 影响仓库：`root / frontend / backend`
- 机器验证清单：`未生成`
- 机器清单时效：`NOT_CHECKED`
- 实现或检查范围：
  - `docs/designs/chinamate-auth.pen`
  - `openspec/changes/add-travel-context-and-account-preferences/`
  - `frontend/` 账号设置、国际化、内存草稿与测试
  - `backend/` account API、application、domain、MyBatis-Plus、Flyway 与测试

## 2. 自动化验证

| 时间 | 仓库 | 执行角色 | 命令 | 状态 | 关键输出摘要 |
| --- | --- | --- | --- | --- | --- |
| `2026-07-29` | `frontend` | `frontend_engineer` | `pnpm lint` | `PASS` | 修复后 lint 通过 |
| `2026-07-29` | `frontend` | `frontend_engineer` | `pnpm typecheck` | `PASS` | 修复后 TypeScript 检查通过 |
| `2026-07-29` | `frontend` | `frontend_engineer` | `pnpm test` | `PASS` | Vitest 12 个文件、53 个测试全部通过 |
| `2026-07-29` | `frontend` | `frontend_engineer` | 最终 5 项 `account-settings.spec.ts` Playwright 重跑 | `BLOCKED` | 沙箱外审批被 Codex usage limit 拒绝；没有绕过，也未把该轮记为 PASS |
| `2026-07-29` | `backend` | `backend_engineer` | `./mvnw -Dtest=AccountPreferencesApiTests,TravelContextTests test` | `PASS` | 目标测试 16/16 |
| `2026-07-29` | `backend` | `backend_engineer` | `./mvnw -Dtest=ArchitectureRulesTests test` | `PASS` | 架构测试 10/10 |
| `2026-07-29` | `backend` | `backend_engineer` | `./mvnw test` | `PASS` | 113 项，0 failure、0 error；22 项数据库条件测试在无数据库环境时跳过 |
| `2026-07-29` | `backend/MySQL` | `backend_engineer` | 加载根 `.env` 后运行 MySQL 8.4 专项测试 | `PASS` | 19/19；覆盖注册初始化、旅行上下文与会话副作用 |
| `2026-07-29` | `frontend/backend/MySQL` | `qa_engineer` | 隔离后端 8180、真实 MySQL 8.4、Chromium 跨栈 `account-settings.spec.ts` | `PASS` | 先前稳定实现上 6/6；覆盖账号隔离、旅行保存/清空、语言恢复、三类 Cookie 轮换、旧 access/refresh 401、其他会话撤销、当前会话保持及绝对期限不延长 |
| `2026-07-29 19:13` | `root` | `main_agent` | `python3 .codex/skills/chinamate-fullstack-delivery/scripts/validate_handoff_contract.py --change add-travel-context-and-account-preferences --all` | `PASS` | 27 个阶段交接合同结构、路径、当前 fingerprint 与引用有效；6 个审查 finding 均有原 reviewer 的 `RESOLVED` 复核 |
| `2026-07-29 19:16` | `root` | `main_agent` | `openspec validate add-travel-context-and-account-preferences --strict` | `PASS` | 当前 change 严格校验有效 |
| `2026-07-29 19:16` | `root` | `main_agent` | `./scripts/check-agent-governance.sh` | `PASS` | 七角色结构与治理测试通过；合同测试 22/22、治理测试 14/14、验证收集器 5/5、交付安全 5/5 |
| `2026-07-29 19:16` | `root` | `main_agent` | `./scripts/check-harness.sh` | `PASS` | AIWorkSpace Harness、submodule 与集中 Agents/Rules/Skills 治理结构完整 |
| `2026-07-29 19:16` | `root/frontend/backend` | `main_agent` | `git diff --check` | `PASS` | 三个仓库已跟踪差异均无空白错误 |
| `2026-07-29 19:16` | `root` | `main_agent` | `lsof -nP -iTCP:3000 -sTCP:LISTEN`、`lsof -nP -iTCP:8180 -sTCP:LISTEN` | `PASS` | 本轮前端与后端服务已正常停止，两个端口均无 listener |
| `2026-07-29 19:23` | `backend` | `main_agent` | `git push origin main`、`git ls-remote origin refs/heads/main` | `PASS` | 远端 `main` 与本地一致：`a692c1afa69794f6aac3c3298664077ff4f0c409` |
| `2026-07-29 19:23` | `frontend` | `main_agent` | `git push origin main`、`git ls-remote origin refs/heads/main` | `PASS` | 远端 `main` 与本地一致：`46016fd55e6a58a81f726217614f9531bb9ab83e` |
| `2026-07-29 19:23` | `root` | `main_agent` | 同步 4 份 delta specs 后运行 `openspec validate --all --strict` | `PASS` | 16 个 change/spec 全部严格有效；两个新 capability 已创建，两个认证 capability 已合并新增要求 |

## 3. 手工或真实场景验证

| 场景 | 环境 | 操作 | 期望 | 实际 | 状态 | 证据 |
| --- | --- | --- | --- | --- | --- | --- |
| Pen 设置页面设计 | Pen，1920×1080 | 检查旅行上下文、账号安全、修改密码中英文节点 | 六个节点无新增裁切、溢出或破版 | 六个节点通过 `problemsOnly` 与截图检查；既有装饰圆保留刻意裁切 | `PASS` | `docs/designs/chinamate-auth.pen` |
| 新注册账号默认偏好 | MySQL 8.4、后端 8180、前端 3000、真实 Chromium | 注册并进入旅行上下文与账号安全页 | 旅行 GET 200 空表示，安全页保持有效登录 | 空标量、空 `dietaryRestrictions`、`version=0`；安全页未误判匿名 | `PASS` | `handoffs/travel-context-experience-review-008/reviews/travel-context-experience-review-003.json` |
| 旅行页语言同步失败恢复 | 真实 Chromium | 双向切换 `zh-CN`/`en` 并模拟账号偏好 PATCH 失败 | 保持目标语言、route/query/hash、六类草稿、错误提示与 Retry | 双向全部符合，未把草稿写入 URL 或 Web Storage | `PASS` | `handoffs/travel-context-experience-review-008/reviews/travel-context-experience-review-003.json` |
| 修改密码草稿生命周期 | 真实 Chromium | 双向 locale 软导航、模拟请求失败、重新填写后 reload | 同一 Document 跨 locale 保留；失败和新 Document 清空；敏感值不落盘 | 双向字段长度保持 `[14,14,14]`；失败后 `[0,0,0]` 并聚焦当前密码；reload 后 `[0,0,0]`；URL、Web Storage、console 和 browser events 未发现测试值 | `PASS` | `handoffs/travel-context-experience-review-008/reviews/travel-context-experience-review-003.json` |

## 4. QA 结论

- 是否执行：是
- 验收范围：前端静态/单元、后端目标/架构/完整/MySQL 8.4、跨栈 Chromium、认证与会话安全、敏感日志边界。
- 通过项：前端 53/53；后端目标 16/16、架构 10/10、完整 113、MySQL 19/19；先前跨栈 Chromium 6/6。
- 失败项：初次 QA 的 3 个 finding 均经 correction 后由原 QA 标记 `RESOLVED`。
- 未验证项：最终前端 correction 新增的 5 项 Playwright 自动化因 Codex usage limit 未重跑；相同受影响流程已由最终 clean live 真实走查通过。
- 已知缺陷：无 OPEN QA finding。
- 残余风险：自动化与最终真实走查不是同一次 Playwright 执行；本地测试账号未获清理授权。

## 5. Spec 合规审查

- 是否执行：是
- 完整报告：[`handoffs/travel-context-spec-review-007/reviews/travel-context-spec-review-002.json`](./handoffs/travel-context-spec-review-007/reviews/travel-context-spec-review-002.json)
- 正向覆盖率：初次按 77 个 requirement/scenario 条目完成双向审查；后续针对 4 个 OPEN finding 逐项复核并全部关闭。
- 反向超纲项：最终未发现阻断性超纲行为。
- 阻断问题：无；`SPEC-BE-DELETE-BODY-CHUNKED-001`、`SPEC-BE-UNICODE-CASEFOLD-001`、`SPEC-BE-INTERNAL-ERROR-CODE-001`、`SPEC-BE-SAFE-LOG-BOUNDARY-001` 均为 `RESOLVED`。
- 最终结论：`PASS`
- 技术基线：Java 21、Spring Boot 4.1、MyBatis-Plus、Mapper XML-only 自定义 SQL、Flyway-only schema 变更、事务与安全日志边界通过独立复核。

## 6. 体验走查

- 是否执行：是
- 完整报告：[`handoffs/travel-context-experience-review-008/reviews/travel-context-experience-review-003.json`](./handoffs/travel-context-experience-review-008/reviews/travel-context-experience-review-003.json)
- 已检查页面或流程：六个 Pencil 节点对应路径、新账号旅行空状态、账号安全、旅行页双向 locale 失败恢复、改密页双向 locale、请求失败清空、reload 清空与敏感值不落盘。
- P0/P1 问题：初次 2 个 P1 finding 均为 `RESOLVED`。
- P2/P3 问题：无 OPEN finding。
- 未验证设备或流程：本轮只读复核未点击真实语言 Retry、未执行真实改密成功写入；由既有自动化和 QA 跨栈证据承接。
- 最终结论：`PASS`

## 7. 未验证项与残余风险

| 项目 | 状态 | 原因 | 影响 | 后续处理 |
| --- | --- | --- | --- | --- |
| 最终 5 项 Playwright 自动化重跑 | `BLOCKED` | Codex usage limit 拒绝所需沙箱外审批 | 不能声称最终 correction 后的这 5 项自动化本轮 PASS | 已用 clean live 覆盖受影响流程；后续额度可用时补跑 |
| Git/submodule 交付 | `PASS` | 用户已授权归档、提交和推送 | backend/frontend 远端 SHA 已核验；root gitlink 与归档由本次根提交交付 | 最终回执报告 root 远端 SHA |
| main specs 同步与归档 | `PASS` | 4 份 delta specs 已同步并通过 16/16 strict validate | 当前规格与已实现能力一致 | 归档到日期命名目录 |
| 本地测试账号 | `NOT_RUN` | 未获破坏性清理授权 | MySQL 保留 QA/体验账号，包括 `ExpFix729A01`、`ExpFix729E01` | 如需清理，先确认精确账号清单 |
| 根级 `.playwright-mcp/` | `NOT_RUN` | reviewer 工具自动生成且未获删除授权 | 根工作区保留未跟踪目录 | 如需清理，另行授权精确路径 |

## 8. 最终交付结论

- tasks 是否全部完成：是。
- 前端验证：`PASS_WITH_BLOCKED_RERUN`（lint/typecheck/Vitest 53/53 与 clean live 通过；最终 5 项 Playwright 自动化重跑受 usage limit 阻塞）
- 后端验证：`PASS`（目标 16/16、架构 10/10、完整 113、MySQL 19/19）
- Harness：`PASS`
- OpenSpec strict validate：`PASS`
- Handoff contracts：`PASS`（27 个）
- Spec Review：`PASS`
- Experience Review：`PASS`
- 机器验证清单时效：`NOT_CHECKED`
- 是否建议归档：是
- 结论依据：实现、QA、Spec、真实体验、main specs 同步、严格门禁与子仓库远端交付已经闭环；最终自动化 Playwright 重跑的环境阻塞已披露，并由相同受影响流程的 clean live 结果承接。

## 记录边界

- 只保存完整命令、关键输出摘要、测试数量、失败数量、可复现步骤和相对路径，不粘贴完整终端日志或缓存。
- `reviews/verification-manifest.json` 只保存受控 profile 的命令、退出码、脱敏摘要、仓库状态和输入指纹；它不替代 QA、Spec Review、体验结论或归档判断。
- 凭据、token、Cookie、隐私数据和敏感日志必须脱敏；无法安全脱敏时不得保存。
- 审查或最终验证后又修改覆盖范围内的实现、测试或规格时，把旧记录标记为“已失效”，并追加新的验证记录或不重跑依据。
