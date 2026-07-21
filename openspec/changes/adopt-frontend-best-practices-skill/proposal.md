## Why

当前项目仅在 `AGENTS.md` 和 `frontend/AGENTS.md` 中保留少量 React、Next.js 原则，尚未把成熟的最佳实践 Skill 纳入统一 AI Coding 入口，导致不同代理在编写、评审和重构前端代码时缺少一致且可复用的规则集。现在引入经过验证的官方 Skill，可以在不重复维护大篇幅自定义规范的前提下，为后续前端开发建立稳定基线。

## What Changes

- 在主仓库项目级 Skills 目录引入 Vercel 官方 `vercel-react-best-practices`，同时覆盖 React 与 Next.js 的性能、数据获取、渲染、bundle 和服务端边界实践。
- 在根目录 `AGENTS.md` 中明确触发条件：凡涉及 `frontend/` 内 React 组件、Next.js 页面、数据获取、Server/Client Component、bundle 或性能的编写、评审和重构，必须使用该 Skill。
- 明确事实冲突优先级：Next.js 16.2.10 的本地版本文档和现有 `frontend/AGENTS.md` 高于 Skill 中面向通用版本的建议，避免旧版本模式覆盖当前框架行为。
- 扩展 Harness 检查，验证 Skill 入口文件、来源锁文件、项目显式批准的 Skill 清单以及 `AGENTS.md` 引用存在，防止后续 clone 或更新时规范静默丢失。
- 目标：让前端相关 AI 任务能够自动发现并应用同一份 React/Next.js 最佳实践，同时保留来源和版本追踪能力。
- 非目标：本变更不批量重构现有前端代码，不新增第三方 Next.js Skill，不改变 ESLint、TypeScript、Vitest 配置，也不处理 Java 或 MySQL 规范。
- 验收结果：项目级 Skill 文件完整、锁文件包含目标 Skill 且不包含未经项目 change 批准的 Skill、根级规则包含明确触发范围和冲突优先级，并且 Harness 检查能够对缺失、来源错误、未批准项或错误引用给出失败结果。
- 主要风险：Skill 的通用建议可能落后于 Next.js 16；通过本地版本文档优先和锁定来源降低风险。外部 Skill 更新也可能带来规则变化，因此更新必须显式执行并复核差异。

## Capabilities

### New Capabilities

- `frontend-best-practices-skill`: 规定项目如何引入、触发、校验和更新 React/Next.js 最佳实践 Skill。

### Modified Capabilities

无。

## Impact

- 主仓库：`.agents/skills/vercel-react-best-practices/`、`skills-lock.json`、`AGENTS.md`、`scripts/check-harness.sh`。
- 前端 submodule：本变更不修改 `frontend/` 内部文件或 gitlink，但后续针对该目录的 AI 编码任务会受到新增规则约束。
- 外部来源：`vercel-labs/agent-skills@vercel-react-best-practices`。
- API、运行时依赖与数据库：无影响。
