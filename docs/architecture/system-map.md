# ChinaMate 跨栈系统地图

本地图用于缩小 AI 定位范围，不代替当前 OpenSpec、源码、测试和真实输出。`CURRENT` 路径必须真实存在；`PLANNED` 表示经 PRD 或计划识别、尚未实现的能力。

## 机器校验路径

| 状态 | 能力 | 路径 | 说明 |
| --- | --- | --- | --- |
| CURRENT | 双语应用路由 | `frontend/src/app/[locale]` | 当前页面路由根 |
| CURRENT | 全局页面框架 | `frontend/src/components/site-header.tsx` | 导航入口 |
| CURRENT | 双语资源 | `frontend/src/i18n` | 中英文字典与 locale 工具 |
| CURRENT | 前端单元测试 | `frontend/src/components/product-shell.test.tsx` | 产品壳层行为 |
| CURRENT | 前端 E2E | `frontend/e2e` | 双语、导航、视口和状态验收 |
| CURRENT | 后端账号边界 | `backend/src/main/java/com/heness/project/account` | 仅模块边界，业务尚未实现 |
| CURRENT | 后端攻略边界 | `backend/src/main/java/com/heness/project/guide` | 仅模块边界，业务尚未实现 |
| CURRENT | 后端 AI 边界 | `backend/src/main/java/com/heness/project/assistant` | 当前含 AI 配置，业务尚未实现 |
| CURRENT | 后端社区边界 | `backend/src/main/java/com/heness/project/community` | 仅模块边界，业务尚未实现 |
| CURRENT | 后端架构测试 | `backend/src/test/java/com/heness/project/architecture/ArchitectureRulesTests.java` | 模块与分层约束 |
| CURRENT | API 开发规范 | `docs/standards/api-development-guidelines.md` | 跨栈 HTTP 合同基线 |
| PLANNED | 账号 API | `backend/src/main/java/com/heness/project/account/api` | M03 change 冻结合同后创建 |
| PLANNED | 攻略 API | `backend/src/main/java/com/heness/project/guide/api` | M04 change 冻结合同后创建 |
| PLANNED | AI 会话 API | `backend/src/main/java/com/heness/project/assistant/api` | M05 change 冻结合同后创建 |
| PLANNED | 社区 API | `backend/src/main/java/com/heness/project/community/api` | M06 change 冻结合同后创建 |

## 业务关系总览

| 产品模块 | 前端 | API | 后端 | 数据归属 | 主要测试 | 当前状态 |
| --- | --- | --- | --- | --- | --- | --- |
| M02 官网与双语基础 | `/[locale]`、全局组件、i18n | 无业务 API | 无业务模块 | locale Cookie，无服务端业务表 | Vitest、Playwright | CURRENT |
| M03 账号与旅行上下文 | `/[locale]/account` 当前为占位 | 待 change 确认 | `account` | 账号、凭据、会话、旅行上下文 | API、领域、持久化、E2E | PLANNED |
| M04 结构化攻略 | `/[locale]/guides` 当前为占位 | 待 change 确认 | `guide` | 攻略、双语版本、来源、收藏、反馈 | 查询、状态机、数据库、E2E | PLANNED |
| M05 AI 实时助手 | `/[locale]/ask-ai` 当前为占位 | 待 change 确认 | `assistant` | 会话、消息、引用、调用与反馈 | 假模型、风险、引用、E2E、评测 | PLANNED |
| M06 任务型社区 | `/[locale]/community` 当前为占位 | 待 change 确认 | `community` | 问题、回答、评论、解决状态 | 权限、状态、事务、E2E | PLANNED |

后端详细依赖与模块职责以 `backend/docs/architecture.md` 为准；业务可观察行为以 `openspec/specs/` 和当前 change 为准。
