# `add-account-authentication` 体验走查报告

## 范围与环境

- 真实环境：MySQL 8.4（3307）、Spring Boot（8080）、Next.js 16（3000）、Chromium。
- 页面：`/zh-CN/account`、`/zh-CN/account/register`、`/en/account`、`/en/account/register`，以及合法返回后的 guides/home。
- 规格基线：前端认证 capability、Pencil 登录 `ay6XZ` / 注册 `kAJhd`、`RULE-FE-006`。
- 验证方式：真实中英文注册/自动登录/恢复/刷新/退出、双标签并发、DOM 可访问树、桌面截图、1920×1080 与 320×720 E2E、纯键盘 E2E。

## 已验证流程

| 流程 | 结果 | 观察证据 |
| --- | --- | --- |
| 中文注册→自动登录→合法返回→当前账号→退出 | `PASS` | 真实账号与 API/页面联调；退出后匿名导航 |
| 英文注册→自动登录→合法返回→刷新恢复→退出 | `PASS` | Header 立即显示账号，reload 后恢复，退出回首页 |
| access 到期后的双标签刷新 | `PASS` | 两个标签同时重新加载后均保持登录，无误退出 |
| 登录失败与限流反馈 | `PASS` | 统一错误不枚举账号；倒计时 E2E 可恢复提交 |
| 安全 `returnTo` | `PASS` | locale 内路径保留，外部 URL 回退当前语言首页 |
| 桌面与 320px | `PASS` | 标题、字段、主按钮可用，无横向溢出 |
| 键盘与语义 | `PASS` | label、button、checkbox、alert/live region 可识别，Enter 与焦点流程通过 |
| 双语切换 | `PASS` | 认证子路由和合法 `returnTo` 保留，文案完整切换 |

## 问题清单（P0/P1/P2/P3）

### P0 / P1

无。核心注册、登录、刷新、恢复和退出均可完成，没有数据损坏、安全绕过或不可恢复卡点。

### P2：已登录用户仍可看到登录表单

- 影响与依据：已登录用户直接访问 `/{locale}/account` 时，Header 显示当前账号和“退出”，正文仍展示登录表单，身份语义不一致，但不阻断其他流程。
- 复现步骤：登录成功后在第二个标签访问 `/en/account`。
- 期望 / 实际：期望跳回安全首页或显示“已登录”状态；实际仍显示“Continue your ChinaMate journey”表单。
- 证据：本轮真实双标签 DOM 快照；无敏感截图入库。
- 建议方向：后续产品确认后增加已认证路由收敛策略；本 change 未规定自动重定向，因此不作为 Spec 偏差或归档阻断。

### P3：开发服务器并行 E2E 曾出现一次瞬时 JSON 解析错误

- 影响与依据：五 worker 首次完整回归中，单个注册页被 Next dev runtime overlay 替代；未在单项复跑和第二次完整回归复现。
- 复现步骤：`pnpm test:e2e`，首次结果 20/21；随后单项 1/1、完整 21/21。
- 期望 / 实际：期望开发服务器稳定并行渲染；实际出现一次 `Unexpected end of JSON input`。
- 证据：Playwright 失败上下文和后续命令输出；临时 trace 不纳入仓库。
- 建议方向：若 CI 重复出现，固定 worker 或切换 production server profile 后另开测试稳定性修复；当前不修改产品代码。

## 未验证项

- 未使用 VoiceOver/NVDA 等真实屏幕阅读器软件朗读；已验证可访问树、语义控件、状态区域和纯键盘路径。
- 未覆盖 Safari、Firefox、真实移动设备和高延迟/断网恢复；当前验收基线为 Chromium、桌面与 320px。

## 总体风险与下一交接建议

- Experience Review：`PASS_WITH_ISSUES`。
- P0/P1：0；P2：1；P3：1。
- Pencil 核心层级、品牌、左右结构、表单密度与双语文案一致，桌面和窄屏核心操作可用。
- 建议主 Agent 收口证据并停在 Git 授权边界；P2 可作为后续小 change 的产品决策，不阻断当前认证 MVP。
