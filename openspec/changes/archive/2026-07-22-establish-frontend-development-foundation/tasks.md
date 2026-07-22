## 1. 固化前端验证工具

- [x] 1.1 在 `frontend/package.json`、`frontend/pnpm-lock.yaml` 和 `frontend/vitest.config.ts` 中新增 `typecheck`、Playwright Chromium E2E 依赖与脚本，并以独立开发端口配置 `frontend/playwright.config.ts`；验证脚本名称、端口和 webServer 生命周期可被本地重复执行。
- [x] 1.2 在 `frontend/src/app/page.test.tsx` 及后续测试中显式导入 Vitest API，先复现现有 `tsc --noEmit` 对测试全局变量的失败，再使 `pnpm typecheck` 通过且不向应用代码注入测试全局类型。

## 2. 以测试定义双语路由契约

- [x] 2.1 先在 `frontend/src/i18n/` 的单元测试中覆盖 `/en`、`/zh-CN` 校验、Cookie/浏览器语言/默认英文优先级、路径 locale 替换和中英文字典键一致性，并确认测试在实现前以正确原因失败。
- [x] 2.2 先在 `frontend/e2e/` 中编写根路径语言处理、双语 URL 直达、语言切换保留 path/query/hash、未知 locale 404 的 Playwright 场景，并确认现有页面不满足契约。
- [x] 2.3 在 `frontend/src/i18n/`、`frontend/src/proxy.ts` 和 `frontend/src/app/[locale]/` 中实现 locale 常量、类型守卫、非敏感偏好 Cookie、浏览器语言选择、服务端字典加载和双语路由，使第 2.1、2.2 项测试通过。

## 3. 建立全局产品页面框架

- [x] 3.1 先为全局导航、语言切换、页脚、通用状态和首页关键内容补充 Vitest + Testing Library 测试，覆盖语义标签、键盘可达、目标语言文案及未实现功能不得提交伪请求，并确认实现前失败。
- [x] 3.2 在 `frontend/src/app/[locale]/layout.tsx`、`frontend/src/components/` 和 `frontend/src/app/globals.css` 中实现服务端优先的根布局、品牌与导航、最小客户端语言切换器、页脚、1440px PC 容器、设计 token 和清晰焦点样式。
- [x] 3.3 在 `frontend/src/app/[locale]/page.tsx` 中实现双语首页最小产品壳层，展示产品定位、AI 入口、主要行动按钮、六类核心场景和可信度说明；AI 操作只导航到当前 locale 的开发中页面。
- [x] 3.4 在 `frontend/src/app/[locale]/guides/`、`ask-ai/`、`community/`、`account/` 及相关特殊文件中建立稳定占位路由和双语加载、空内容、错误、404、无权限、功能开发中状态，不连接后端或伪 API。
- [x] 3.5 运行第 3.1 项测试并进行最小重构，确认完整字典未传入 Client Component、公共组件没有 barrel export、业务占位路由未被误标为已完成功能。

## 4. 完成真实浏览器验收

- [x] 4.1 扩充 `frontend/e2e/`，覆盖全局导航、首页首屏、1920×1080 与 1440×900 无横向溢出/遮挡，以及低于 1280px 的基础可读和 PC 优先提示。
- [x] 4.2 仅安装 Playwright Chromium 运行时，执行 `pnpm test:e2e` 并记录服务自动启动/停止、无需后端以及所有浏览器场景的真实结果。

## 5. 文档、计划与最终门禁

- [x] 5.1 更新 `frontend/README.md`，记录双语 URL、`pnpm typecheck`、单元测试、Chromium 安装、E2E 命令、独立端口和本变更明确不包含的业务能力。
- [x] 5.2 按实际完成证据更新 `docs/plans/chinamate-mvp-development-plan.md` 中 M02 对应任务；账号、攻略、AI、社区和未实现的状态保留未勾选。
- [x] 5.3 在 `frontend/` 依次运行 `pnpm lint`、`pnpm typecheck`、`pnpm test`、`pnpm test:e2e`，并在主仓库运行 `./scripts/check-harness.sh`、`openspec validate establish-frontend-development-foundation --strict` 与 `git diff --check`。
- [x] 5.4 分别检查 `frontend/` 与主仓库 diff、状态和 submodule 边界，确认没有后端改动、凭据、构建产物、浏览器产物或无关格式化；未经用户明确授权不提交、不推送、不更新主仓库 gitlink。
