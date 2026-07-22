## Context

`frontend/` 当前只有根首页、根布局、全局样式和一个静态渲染测试。`pnpm lint`、`pnpm test` 已通过，但 `pnpm exec tsc --noEmit` 因测试文件没有显式导入 Vitest API 而失败；工程也没有独立 `typecheck` 命令、双语路由、产品级布局、通用状态或浏览器 E2E。

本变更服务于 ChinaMate PC 官网的后续功能开发。PRD 已确定简体中文和英文同版本首发、1920×1080 为核心验收视口、1440×900 为兼容视口，并要求语言切换保留当前页面。当前 Next.js 16.2.10 本地文档推荐使用 locale 子路径和 `proxy.ts` 完成语言路由，App Router 页面默认是 Server Component；项目级 Vercel Skill 进一步要求控制 Client Component 边界和 RSC 序列化数据量。

## Goals / Non-Goals

**Goals:**

- 建立能独立运行的 lint、类型检查、单元测试和浏览器 E2E 门禁。
- 提供稳定、可直达、可切换的 `/en` 与 `/zh-CN` 双语 URL。
- 提供后续业务页面共同使用的导航、页脚、PC 容器、设计 token 和通用页面状态。
- 以最小首页内容验证布局、双语、可访问性和目标视口，不连接业务 API。
- 保持 Server Component 默认策略，把必须访问浏览器状态的逻辑限制在小型客户端组件内。

**Non-Goals:**

- 不定义或实现认证、授权、API 请求、缓存、全局业务状态和表单架构。
- 不为攻略、AI、社区或账号创建伪数据接口或可提交业务交互。
- 不引入大型 UI 组件库、全局状态库或完整设计系统。
- 不实现完整移动端布局，也不改变后端、数据库或部署拓扑。

## Decisions

### 1. locale 使用 URL 子路径，固定为 `/en` 与 `/zh-CN`

所有产品页面放在 `app/[locale]/` 下，稳定路由至少包括首页、`guides`、`ask-ai`、`community` 和 `account`。根路径和缺少 locale 的产品路径由 Next.js 16 的 `proxy.ts` 补全 locale；不使用已经在 Next.js 16 更名的 `middleware.ts`。

优先级为：用户主动选择后写入的非敏感 locale Cookie → `Accept-Language` 中是否偏好中文 → 默认英文。默认英文符合外国游客为核心用户的产品定位；只识别中文与英文可以使用项目内小型解析函数，无需为两个 locale 引入通用国际化路由依赖。未知 locale 必须进入 404，而不能静默回退造成错误语言 URL 被搜索引擎收录。

备选方案是域名级语言或仅把语言保存在客户端状态。域名级语言增加部署与本地开发成本；纯客户端状态不利于直达、SSR、SEO 和刷新保持，因此不采用。

### 2. 文案字典在服务端按 locale 动态加载

中英文文案分别维护，并由带 `server-only` 约束的字典加载器按 locale 动态导入。页面和布局保持 Server Component，只把渲染所需的最小字符串传给语言切换器等客户端组件，避免把整份字典序列化进客户端包。

语言切换器是小型 Client Component：替换 URL 第一段、保留其余 pathname、query 和 hash，并写入 locale Cookie。当前变更不包含业务筛选和表单；后续页面若存在未提交状态，必须在对应功能 change 中补充保存与恢复契约，不能由本底座虚构通用序列化机制。

备选方案是立即引入完整 i18n 框架。当前只有两种语言且需求集中在路由和静态文案，先使用 Next.js 原生能力更小、更透明；如果后续出现复杂复数规则、富文本翻译或翻译平台接入，再通过独立 change 评估迁移。

### 3. 全局布局保持服务端，交互作为叶子组件

`[locale]/layout.tsx` 负责 `<html lang>`、metadata、全局导航、页脚和主内容结构。导航链接、品牌区和页脚默认是 Server Component；只有语言切换和以后确实需要浏览器状态的局部交互使用 `"use client"`。禁止为了语言或认证预留把整个根布局改成 Client Component。

首页提供产品定位、AI 提问入口、主要行动按钮、六类核心场景以及可信度说明的最小静态壳层；攻略、AI、社区和账号路由只提供明确的“功能开发中”状态，不连接伪 API。这样可以稳定导航契约，同时不冒充业务功能已完成。

### 4. 使用 Tailwind CSS 4 token 和少量公共组件，不引入组件库

在全局样式中定义颜色、字体、内容宽度、间距和焦点外观等项目 token；建立链接/按钮外观、页面容器和状态展示等少量公共组件。组件以真实复用需求为边界，不建立包罗万象的 `ui/` 抽象，也不创建 barrel export。

字体继续使用 Next.js 自带字体优化，但中英文 fallback 必须明确；公共内容容器最大宽度为 1440px。英文长文案、键盘焦点、语义标签和颜色非唯一表达纳入单元测试或浏览器验收。

### 5. 类型检查使用显式 Vitest 导入

新增 `pnpm typecheck`，按 Next.js 16 本地官方文档先执行 `next typegen` 刷新 App Router 类型，再执行 `tsc --noEmit`。测试文件显式从 `vitest` 导入 `describe`、`it` 和 `expect`，并关闭不必要的全局测试 API，避免把测试全局类型泄漏到应用代码。

备选方案是在主 `tsconfig.json` 中全局加入 `vitest/globals`。该方案改动更少，但会让全部应用文件都看见测试全局变量，边界较差，因此不采用。

### 6. 使用 Playwright 建立真实浏览器门禁

新增 Playwright 开发依赖、配置和 `test:e2e` 脚本，通过 `webServer` 启动独立前端开发端口。E2E 至少覆盖根路径语言选择、两种语言直达、语言切换保留路径、未知 locale 404、导航可达、首页首屏以及两个目标 PC 视口无横向溢出。另设一个小屏用例验证明确的降级提示，而非宣称完整移动适配。

单元测试继续使用 Vitest + Testing Library，负责字典、locale 工具和组件行为；Playwright 只承担跨路由与真实布局行为，避免重复覆盖。

### 7. 跨仓库交付遵循 submodule 顺序

实现修改 `frontend/`，并同步主仓库中的 OpenSpec、计划文件和 `scripts/check-harness.sh` 前端门禁入口。完成后先在前端仓库验证，再由用户明确授权后提交并推送前端；只有远端可达后，主仓库才能更新 gitlink。未经用户明确要求，本 change 不自动提交或推送。

### 8. 未匹配路由使用 Next.js 16 Global Not Found

由于根布局位于顶层动态 `[locale]` 段，且普通 `notFound()` 在流式响应开始后只能返回 `200 + noindex`，未匹配路由启用 Next.js 16 的实验性 `globalNotFound`。Proxy 对受支持 locale 仅向上游转发内部 locale 请求头，`global-not-found.tsx` 据此选择最小双语 404 文案并在路由层直接返回 HTTP 404；该内部请求头不发送给浏览器。locale 内的 `not-found.tsx` 继续作为后续已匹配业务路由主动触发 `notFound()` 时的通用状态。

## Risks / Trade-offs

- [自建双 locale 解析能力未来不足] → 将 locale、Cookie 名和路由替换封装在独立模块；出现复杂国际化需求时通过独立 change 迁移。
- [Proxy 匹配静态资源或内部路径造成重定向] → matcher 明确排除 `_next`、静态文件和 API 路径，并用 E2E 覆盖。
- [语言切换丢失功能页临时状态] → 本变更只保证 URL path/query/hash；具体业务表单在所属 change 中定义状态恢复并补测试。
- [占位路由被误认作功能完成] → 页面明确显示“功能开发中”，开发计划中的业务任务保持未完成。
- [Playwright 浏览器安装增加本地体积] → 只安装 Chromium；把安装命令和未安装时的错误处理写入 README。
- [根布局客户端化导致包体膨胀] → 服务端布局与最小叶子 Client Component 作为评审门禁，并只传递使用到的字段。

## Migration Plan

1. 先修复类型检查并用失败/通过输出建立门禁证据。
2. 建立 locale 工具、字典、Proxy 和 `[locale]` 路由，迁移现有根布局与首页。
3. 增加全局布局、token、公共状态和占位路由，补齐单元测试。
4. 增加 Playwright 配置与 E2E，用两个 PC 视口和小屏降级完成真实浏览器验证。
5. 更新前端 README、开发计划和 OpenSpec tasks，运行前端门禁与根 Harness。

若需要回滚，前端 submodule 可回退到变更前 gitlink；本变更不迁移数据，也不改变后端契约。

## Open Questions

无阻塞问题。当前提案采用 `/en` 与 `/zh-CN`，并以英文作为非中文浏览器的默认语言；若产品后续调整 locale 标识或默认语言，应先更新本 change 的规格和设计再实现。
