## Context

主仓库负责三个 Git 仓库共用的 AI Coding Harness，根目录 `AGENTS.md` 是统一规则入口；`frontend/` 另有局部 `AGENTS.md`，并明确要求为当前 Next.js 版本读取 `node_modules/next/dist/docs/`。目前项目级 `.agents/skills/` 只有 OpenSpec 工作流 Skill，React/Next.js 最佳实践来自代理各自的全局环境，不能保证其他机器或其他代理得到相同规则。

经 Skills CLI 和公开仓库核对，`vercel-labs/agent-skills@vercel-react-best-practices` 由 Vercel 官方维护，同时覆盖 React 与 Next.js，安装量和仓库信誉显著高于候选第三方 Skill。候选 `wshobson/agents@nextjs-app-router-patterns` 面向 Next.js 14+，部分通用表述可能无法反映 Next.js 16 的最新行为，因此不纳入本次基线。

## Goals / Non-Goals

**Goals:**

- 将 React/Next.js 最佳实践作为主仓库可版本化、可追踪的项目级 Skill。
- 让所有针对 `frontend/` 的相关 AI 编码、评审和重构任务明确触发该 Skill。
- 当 Skill 与 Next.js 16 当前版本文档冲突时，提供唯一且明确的事实优先级。
- 通过 Harness 检查防止 Skill、锁记录或规则引用在后续变更中静默丢失。

**Non-Goals:**

- 不用 Skill 替代 ESLint、TypeScript、测试或运行时验证。
- 不在本次变更中重构前端业务代码或修改前端 submodule。
- 不引入通用 Next.js 14+ 第三方 Skill，也不扩展到 UI 设计、部署、React Native、Java 或 MySQL。

## Decisions

### 1. 使用一个 Vercel 官方 Skill 同时覆盖 React 与 Next.js

选择 `vercel-react-best-practices`，因为其规则明确涵盖 React 组件、Next.js 页面、Server Actions、服务端缓存、数据串行化、bundle、数据获取和渲染性能。一个统一 Skill 可以减少规则重叠和冲突。

备选方案是同时安装 `nextjs-app-router-patterns`。该 Skill 的安装量和仓库信誉合格，但其定位是 Next.js 14+ 通用模式，不是 Vercel 官方维护；当前项目又使用 Next.js 16.2.10，因此本次不采用。

### 2. 采用项目级 `.agents/skills/` 和 `skills-lock.json`

Skill 完整内容放入主仓库 `.agents/skills/vercel-react-best-practices/`，来源与内容哈希记录在根目录 `skills-lock.json`。这样普通 clone 即可得到相同 Skill，且不依赖开发者主目录中的全局安装。

备选方案是只在用户级全局安装。该方式不会进入 Git，无法保证 CI、其他开发者或其他 AI Harness 使用同一版本，因此不采用。

### 3. 根级 `AGENTS.md` 负责强制触发，前端局部规则负责版本事实

根级规则增加明确的触发范围和“必须使用”措辞，使 React/Next.js 任务统一加载 Skill。现有 `frontend/AGENTS.md` 继续要求读取安装版本的 Next.js 文档；若两者冲突，优先级为：当前 OpenSpec 规格与已确认 change → `frontend/AGENTS.md` 和本地 Next.js 16 文档 → Vercel Skill 通用建议。

备选方案是在 `frontend/AGENTS.md` 中单独引用 Skill。由于 `frontend/` 是独立 submodule，这会扩大为跨仓库改动并要求更新 gitlink，而根级统一入口已经可以覆盖当前需求，因此不采用。

### 4. Harness 使用可扩展的批准清单检查结构契约

`scripts/check-harness.sh` 维护项目显式批准的 Skill 名称清单，并检查 Skill 入口、规则目录、锁文件中的目标来源与哈希以及根级 `AGENTS.md` 引用。当前清单只有 `vercel-react-best-practices`；后续 Java、MySQL 等独立 change 可以在完成来源审查后扩展该清单。Harness 必须拒绝锁文件中的未批准 Skill，但不得把“当前只有一个”固化为永久数量限制。它不尝试判断每一条最佳实践是否被业务代码遵守；具体代码质量仍由任务内 Skill 使用、lint、测试和评审共同保证。

## Risks / Trade-offs

- [Skill 更新后规则发生变化] → 保留 `skills-lock.json` 的来源和哈希，更新时必须显式复核差异并重新运行 Harness。
- [通用规则与 Next.js 16 行为冲突] → 明确本地版本文档优先，不把 Skill 视为框架 API 的最终事实源。
- [项目级 Skill 增加仓库文件数量] → 只保留经过独立 change 明确批准的 Skill，拒绝安装同仓库的其他 8 个无关 Skill。
- [文字规则不能完全强制代码质量] → Harness 只保证规则可发现；后续具体前端变更仍须运行 `pnpm lint` 和相关测试。

## Migration Plan

1. 确认本 change 只新增 `vercel-react-best-practices`，锁文件不包含未经项目 change 批准的其他 Skill。
2. 修改根级 `AGENTS.md`，增加触发范围、使用要求和事实冲突优先级。
3. 先为 Harness 补充预期失败检查，再保留完整 Skill 与引用使检查通过。
4. 将 Harness 中的固定单项判断改为显式批准清单，并运行 Shell 语法检查、Harness 检查、OpenSpec 严格校验和差异检查；本变更不运行无关 build。

回滚时删除新增 Skill 目录和锁记录，撤销 `AGENTS.md` 与 Harness 对应规则即可；不涉及前端应用代码、数据库或数据迁移。

## Open Questions

无。Java 与 MySQL Skill 将分别通过后续独立 change 评估和引入。
