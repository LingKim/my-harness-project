# ChinaMate 前端开发约定

本文是前端稳定项目约束的唯一规范源。第三方 Skill 提供通用方法，不能覆盖当前规格、依赖、源码、测试、本文件或 Next.js 当前版本文档。

## RULE-FE-001：以当前版本事实为准

- 当前技术栈为 Next.js 16.2.10、React 19.2.7、TypeScript 5、Tailwind CSS 4.3.3 和 pnpm 10；版本变化以 `package.json`、lockfile 和真实安装结果为准。
- 涉及 Next.js API、约定、路由、缓存或构建行为时，先读取 `node_modules/next/dist/docs/` 的直接相关文档，不照搬旧教程。
- Skill 与当前版本证据冲突时采用当前版本证据，并在交付说明中指出冲突。

## RULE-FE-002：目录与组件保持最小边界

- App Router 页面和布局位于 `src/app/`，可复用视图位于 `src/components/`，国际化配置和字典位于 `src/i18n/`；新增目录必须由真实职责支撑。
- 默认按产品功能和路由组织代码，不为未来可能出现的需求提前建立空 domain、service、store 或通用 SDK。
- 不创建无业务语义的万能组件、Hooks 或 `utils` 回收站；少量重复优先于错误抽象。

## RULE-FE-003：默认使用 Server Component

- 页面、布局和数据读取默认保持 Server Component；只有浏览器 API、本地交互状态、事件处理或必须使用的客户端 Hook 才添加 `"use client"`。
- Client Component 保持在交互叶子，禁止为了复用一个小交互把整页或大段布局改成客户端组件。
- Server/Client 边界只传递客户端实际需要且可序列化的最小字段，不传完整数据库对象、内部权限字段或大字典。
- 服务端请求数据不得写入可变模块级状态；模块作用域按进程共享状态对待。

## RULE-FE-004：数据获取和变更避免瀑布与越权

- 独立异步操作并行启动，只有真实依赖关系才串行等待；优先通过组件结构和 Suspense 边界消除服务端瀑布。
- 在廉价同步条件确定不需要结果时，不提前执行或等待昂贵异步操作。
- Server Action、Route Handler 和其他服务端变更入口必须像公开 API 一样执行输入校验、认证和授权，不能只依赖 UI 隐藏或上层检查。
- 未经具体 OpenSpec change，不提前引入通用 API SDK、SWR、全局缓存或状态管理依赖。

## RULE-FE-005：控制 bundle、渲染和浏览器存储

- 优先使用可静态分析的 import；第三方 barrel import 是否优化必须以当前 Next.js 配置和包类型声明为准，不能盲目改成缺少类型的深层路径。
- 重型且非首屏组件只有在真实 bundle 或交互需求支撑时使用动态加载；不得为了通用建议过度拆分小组件。
- 不把 token、PII、内部权限或完整用户对象写入 `localStorage`；确需持久化的非敏感偏好必须使用版本化 key、最小字段和异常处理。
- 不为简单表达式滥用 memo；优化前优先定位真实瀑布、bundle 和重复渲染证据。

## RULE-FE-006：国际化、可访问性和响应式行为必须可验证

- 产品路由只接受 `en` 和 `zh-CN`，未知 locale 返回真实 404；不得静默回退成另一语言的成功页面。
- 文案字典默认只在 Server Component 加载，不把完整字典传入 Client Component。
- 交互使用语义化 HTML，键盘可达且具有可感知的焦点和状态；不得用无语义点击容器替代按钮或链接。
- 当前 PC 基线和小屏降级边界以已确认规格与 E2E 为准，不在没有需求时承诺完整移动端体验。

## RULE-FE-007：客户端只能读取公开配置

- 浏览器端只允许读取明确登记的 `NEXT_PUBLIC_` 变量；数据库密码、AI Key、服务端 token 和其他秘密不得进入前端环境文件、bundle、测试快照或日志。
- 配置缺失、URL 非法或跨域策略变化必须显式失败或按规格处理，不能静默拼接未知默认地址。
- Cookie、认证头和用户输入按敏感数据处理；日志和错误页面不得泄露秘密或内部实现细节。

## RULE-FE-008：验证与变更风险相称

- 修改可观察行为时先补充能因正确原因失败的 Vitest + Testing Library 或 Playwright 场景，再做最小实现。
- TypeScript、路由或组件签名变化至少运行 `pnpm typecheck`；代码风格与静态规则变化运行 `pnpm lint`；业务行为运行相关 `pnpm test`；真实路由、导航、404、语言或布局行为运行相关 `pnpm test:e2e`。
- 纯文档和 AI 治理变更运行 `bash scripts/check-agent-governance.sh` 与 `git diff --check`，默认不运行无关 build。
- 交付必须报告实际命令、结果和未验证项，不以“应该可以”代替证据。
