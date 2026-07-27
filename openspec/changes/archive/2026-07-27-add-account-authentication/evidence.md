# `add-account-authentication` 交付证据

> 本文件只记录实际发生的验证与审查。状态使用 `PASS`、`FAIL`、`BLOCKED`、`NOT_RUN`；不保存凭据、Token、Cookie 或完整原始日志。

## 1. 基本信息

- Change：`add-account-authentication`
- 当前结论：`PASS`（实现、QA、审查、三仓库 Git 交付和 OpenSpec 归档完成）
- 最后更新：`2026-07-27 20:30 +08:00`
- 影响仓库：`root / frontend / backend`
- 机器验证清单：[`reviews/verification-manifest.json`](./reviews/verification-manifest.json)
- 机器清单时效：归档前 `FRESH`（无 changedInputs / changedRepositories）；归档移动后原 active change 路径按预期失效，以归档后 `openspec validate --all --strict` 为终态验证
- 实现或检查范围：认证 OpenSpec、Pencil 两节点、前端认证页面/会话协作、后端 account/Flyway/安全、MySQL 8.4 真实流程。

## 2. 自动化验证

| 时间 | 仓库 | 执行角色 | 命令 | 状态 | 关键输出摘要 |
| --- | --- | --- | --- | --- | --- |
| `20:24` | `frontend` | `qa_engineer` | `pnpm lint` | `PASS` | ESLint exit 0 |
| `20:24` | `frontend` | `qa_engineer` | `pnpm typecheck` | `PASS` | Next typegen 与 `tsc --noEmit` 通过 |
| `20:24` | `frontend` | `qa_engineer` | `pnpm test` | `PASS` | 6 files、23 tests |
| `20:24` | `backend` | `qa_engineer` | 加载 `.env` 后直接 `./mvnw test` | `BLOCKED` | 沙箱禁止连接 3307，且全局环境污染隔离配置测试；81 tests 中 1 failure、23 errors，不记业务失败 |
| `20:25` | `backend` | `qa_engineer` | `./mvnw test` | `PASS` | 81 tests，0 failures/errors，12 个需真实库场景按合同 skipped |
| `20:25` | `frontend` | `qa_engineer` | `pnpm test:e2e`（沙箱内） | `BLOCKED` | 监听 3100 返回 `EPERM` |
| `20:25` | `frontend` | `qa_engineer` | `pnpm test:e2e`（沙箱外，3000 仍运行） | `BLOCKED` | 现有 Next dev 占用同一 `.next` 锁；安全停止自有服务后复测 |
| `20:26` | `backend` | `qa_engineer` | `./mvnw -Dtest='MySqlAuthenticationPersistenceTests,MySqlAuthenticationServiceTests,AccountAuthenticationServiceTests,ArchitectureRulesTests' test` | `PASS` | MySQL 8.4，28/28；Flyway v2、事务、阈值、轮换/重放、架构通过 |
| `20:27` | `frontend` | `qa_engineer` | `pnpm test:e2e` | `FAIL` | 20/21；Next dev 单页瞬时 `Unexpected end of JSON input` |
| `20:28` | `frontend` | `qa_engineer` | `pnpm test:e2e e2e/auth.spec.ts --grep '1920px'` | `PASS` | 失败场景隔离复跑 1/1 |
| `20:28` | `frontend` | `qa_engineer` | `pnpm test:e2e` | `PASS` | 完整 Chromium 21/21 |
| `20:29` | `root/frontend/backend` | `main_agent` | 三个仓库 `./scripts/check-agent-governance.sh` | `PASS` | 集中治理、角色、Rules、Skills 与局部入口均通过 |
| `20:30` | `root` | `main_agent` | `collect_verification.py --profile root-governance ...` | `PASS` | governance、Harness、OpenSpec strict、diff check；清单在最终文档更新后重生成 |

## 3. 手工或真实场景验证

| 场景 | 环境 | 操作与实际 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| 中文完整流程 | MySQL 8.4 + Spring Boot + Next.js + Chromium | 注册、自动登录、合法返回、当前账号、页面恢复、退出均成功 | `PASS` | 浏览器 DOM 与真实 API 行为 |
| 英文完整流程 | 同上 | 注册后 Header 即时显示账号，reload 恢复，退出后匿名导航 | `PASS` | 浏览器 DOM 与真实 API 行为 |
| 30 分钟边界与多标签 | 同上 | 精确把测试会话 access 置为过期，两个标签并发重载后均保持登录 | `PASS` | 数据库精确更新 1 行；双标签 DOM |
| 4/5/6、19/20/21、窗口与重放 | MySQL 8.4 fixture | 阈值两侧、窗口重置、4 秒冲突、6 秒重放撤销均通过 | `PASS` | 两组真实 MySQL 测试 12/12 |
| 安全泄漏检查 | 响应、源码、日志、数据库、diff | 统一错误；无新增敏感日志；Token/限流键为 64 字符摘要；`.env` ignored 且未跟踪 | `PASS` | 聚合查询、源码搜索、浏览器错误态、Git 只读检查 |
| Pencil/响应式/可访问语义 | 桌面、1920×1080、320×720 | 双语页面、无横向溢出、键盘与可访问树通过 | `PASS` | E2E、最终桌面截图观察、DOM snapshot |

## 4. QA 结论

- 是否执行：是。
- 规格矩阵：后端 10 requirements / 31 scenarios，前端 7 requirements / 21 scenarios，全部具备实现与自动化或真实场景证据。
- 后端工程实践：模块分层、最小事务、`noRollbackFor` 安全状态提交、MyBatis-Plus/Flyway、参数绑定、行锁与失败回滚均通过。
- 失败项：最终无未关闭业务失败；中途环境阻塞和一次 E2E 瞬时失败均保留记录并已复验。
- 已知缺陷：无 P0/P1；体验 P2/P3 见体验报告。
- 残余风险：未覆盖真实屏幕阅读器、Safari/Firefox、真实移动设备；Next dev 并行瞬时错误若在 CI 重现需单独治理。

## 5. Spec 合规审查

- 是否执行：是。
- 完整报告：[`reviews/spec-review.md`](./reviews/spec-review.md)
- 正向覆盖率：30/30 = 100%；场景追溯 52/52。
- 反向超纲项：0。
- 阻断问题：0。
- 最终结论：`PASS`。

## 6. 体验走查

- 是否执行：是。
- 完整报告：[`reviews/experience-review.md`](./reviews/experience-review.md)
- 已检查：登录/注册/恢复/刷新/限流/退出、双语、桌面、320px、键盘、语义 DOM、Pencil 视觉。
- P0/P1：0。
- P2/P3：P2 已登录访问认证路由仍显示表单；P3 Next dev 并行 E2E 一次瞬时 JSON 错误。
- 最终结论：`PASS_WITH_ISSUES`，均不阻断认证 MVP。

## 7. 未验证项与残余风险

| 项目 | 状态 | 原因 | 影响 | 后续处理 |
| --- | --- | --- | --- | --- |
| VoiceOver/NVDA 实际朗读 | `NOT_RUN` | 当前使用 DOM 语义和键盘 E2E | 可能遗漏特定读屏器播报差异 | 后续无障碍专项 |
| Safari/Firefox/真实手机 | `NOT_RUN` | 当前基线为 Chromium + 320px | 浏览器特有 Cookie/布局差异 | 发布前设备矩阵 |
| Git 提交、推送、gitlink | `PASS` | 用户已明确授权 | 三仓库提交均远端可达 | backend `d6f3d9b`；frontend `74d1d19`；root gitlink `b92d28f` |

## 8. 最终交付结论

- tasks：33/33。
- 前端验证：`PASS`。
- 后端验证：`PASS`（隔离 81 tests + MySQL 专项 28 tests）。
- Harness / OpenSpec strict：`PASS`。
- Spec Review：`PASS`。
- Experience Review：`PASS_WITH_ISSUES`。
- 机器清单时效：`FRESH`。
- 是否建议归档：已归档至 `openspec/changes/archive/2026-07-27-add-account-authentication/`。
- 结论依据：实现、真实数据库、双语完整栈、安全、QA、双向审查、三仓库远端交付与 17 条 requirements 主规格同步均已完成；归档后 OpenSpec strict 14/14 通过。

## 记录边界

- 只保存命令、摘要、数量、复现步骤和相对路径；不保存完整日志或敏感值。
- `.env`、凭据、原始 Token、Cookie 和测试账号密码均未写入证据或 Git。
- 最终文档与 tasks 更新后必须重生成 manifest 并运行 freshness，旧清单不能直接作为完成证据。
