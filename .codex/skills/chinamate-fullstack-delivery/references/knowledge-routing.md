# 知识与需求来源路由

## 跨栈定位

涉及业务功能时先查：

1. `docs/architecture/system-map.md`：确认产品模块、当前/计划路径、API、后端和测试归属。
2. `docs/standards/domain-glossary.md`：把产品词汇翻译为工程含义，识别容易混淆的概念。
3. 当前 specs 和 change：确认本次可观察行为与边界。
4. 使用 `rg` 搜索真实代码并追踪调用链；地图只缩小范围，不替代源码确认。

## 需求来源格式

重要行为至少引用一种来源：

| 来源类型 | 记录格式 | 示例 |
| --- | --- | --- |
| PRD | `PRD:<requirement-id>` | `PRD:FR-AUTH-002` |
| 已有 Spec | `SPEC:<capability>#<requirement>` | `SPEC:frontend-development-foundation#产品页面使用稳定的双语 URL` |
| 设计稿 | `DESIGN:<file-or-node-id>` | `DESIGN:chinamate-auth.pen#login-form` |
| 用户原话 | `USER:<date>:<摘要>` | `USER:2026-07-27:单人优先编排全栈流程` |
| API 决策 | `API:<resource-or-section>` | `API:docs/standards/api-development-guidelines.md#错误响应` |

新增点击入口、拦截、权限、失败行为或相似功能时，若无法提供来源，标记为“待确认”或“非目标”，不得以“一致性”“同类功能”自行扩大范围。

## 知识库升级触发器

只有满足任一条件才提出新的知识库 change：

- 单个真实业务模块超过 50 个文件；
- 相同定位问题在已记录交付中重复三次；
- 系统地图发生两次已确认漂移事故；
- 同一需求需要三个以上专用外部收料通道。

未达到条件时只维护系统地图、术语桥、现有架构文档和 OpenSpec。
