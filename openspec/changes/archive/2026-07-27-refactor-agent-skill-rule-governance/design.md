## Context

AIWorkSpace 由主仓库、前端 submodule 和后端 submodule 三个独立 Git 仓库组成。当前治理工作已把 Rules 与 Skills 集中到主仓库根 `.codex/`，并删除子仓库局部 `.codex`，但活动 change 又把根 `.codex/agents` 列为禁止路径。

用户现已确认恢复根项目级自定义 Agents，并以产品、交互、前端、后端、测试、Spec 合规审查、体验七类交付物建立研发团队。Codex 官方文档说明项目级自定义 Agent 使用 `.codex/agents/*.toml`，每个文件必须包含 `name`、`description` 和 `developer_instructions`；普通 `tools`、`skills`、`rules` YAML frontmatter 不能直接照搬为 Codex 配置字段。

ChinaMate 当前前端依赖为 Next.js 16、React 19、TypeScript、Tailwind CSS、Vitest、Testing Library 和 Playwright；没有 shadcn/ui、Zustand，也没有独立 `styling-conventions` 或 `coding-conventions` Rule。Agent 配置必须以当前 checkout 为事实来源。

## Goals / Non-Goals

**Goals:**

- 主仓库根 `.codex/` 是唯一治理根，并同时拥有 `agents/`、`rules/` 和 `skills/`。
- 建立七个职责单一、按交付物切分、接口清晰的 Codex custom agents。
- 每个 Agent 至少包含角色职责、输出格式、角色限制、Skills、Rules、Tools 授权和输出语言。
- 每个 Agent 的上游输入、下游交付物、允许写入范围和完成报告都可验证。
- Harness 校验官方 TOML 必填字段、角色名称、七部分正文、引用有效性和只读/写入边界。
- 主 Agent 保持最终协调权，只调用当前任务真正需要的角色。

**Non-Goals:**

- 不把课程中的 Claude/YAML Agent 格式伪装成 Codex 官方格式。
- 不为每个业务步骤都强制启动七个 Agent，也不默认并行写同一工作树。
- 不新增不存在的 Skills、Rules、前端库或目录约定。
- 不支持子仓库独立 clone 时自动获得完整治理包。
- 不修改业务源码、HTTP 契约、数据库 schema、运行时依赖或部署配置。
- 不自动提交、推送或更新 gitlink。

## Decisions

### 1. 根 `.codex` 集中 Agents、Rules 与 Skills

最终结构为：

```text
主仓库
├── AGENTS.md
├── .codex/
│   ├── agents/
│   │   ├── README.md
│   │   ├── product_manager.toml
│   │   ├── interaction_designer.toml
│   │   ├── frontend_engineer.toml
│   │   ├── backend_engineer.toml
│   │   ├── qa_engineer.toml
│   │   ├── spec_reviewer.toml
│   │   └── experience_reviewer.toml
│   ├── rules/
│   ├── skills/
│   ├── skills-lock.json
│   └── manifest.json
├── frontend/
│   └── AGENTS.md
└── backend/
    └── AGENTS.md
```

只在完整 AIWorkSpace 根维护 custom agents。`frontend/.codex` 与 `backend/.codex` 继续禁止，避免角色、Rules 和 Skills 出现第二份规范源。

### 2. 使用 Codex standalone TOML，不照搬 YAML frontmatter

每个 TOML 至少采用以下结构：

```toml
name = "frontend_engineer"
description = "说明何时使用该角色"
sandbox_mode = "workspace-write"
developer_instructions = """
# 角色定义
...

## 角色配置摘要
...

## 角色职责
...

## 输出格式
...

## 角色限制
...

## Skills
...

## Rules
...

## Tools 授权
...

## 输出语言
...
"""
```

`name` 是身份事实源，文件名与 `name` 保持一致。`description` 只描述何时调用，具体人设、任务、交付和限制进入 `developer_instructions`。模型与 reasoning effort 暂不固定，默认继承父任务，避免配置快速过期。

Codex custom agent schema 没有课程示例中的通用 `tools`、`skills`、`rules` 顶层数组。Tools 通过 `sandbox_mode`、继承的当前会话工具/MCP 和正文授权边界表达；Skills 与 Rules 通过正文列出项目真实路径和触发条件。Harness 必须拒绝未批准的未知顶层字段。

### 3. 七角色按交付物切分

| Agent | 核心职责 | 必需上游输入 | 标准交付物 | 写入边界 |
| --- | --- | --- | --- | --- |
| `product_manager` | 澄清问题、定义目标/非目标、形成 OpenSpec 合同 | 用户需求、PRD、当前 specs/change、真实代码证据 | proposal/spec/design/tasks 更新、决策与待确认项 | 仅根 `openspec/`、`docs/product/`、`docs/plans/` |
| `interaction_designer` | 把已确认规格转为页面流程、状态与体验约束 | 已确认 specs、PRD、现有原型与前端事实 | 页面流程、状态矩阵、交互/响应式/i18n/a11y 说明 | 仅设计与规划文档，不写应用代码 |
| `frontend_engineer` | 按规格和交互交付 Next.js/React 前端 | 已确认 specs、交互稿、稳定 API 契约 | 前端代码、测试、验证证据和完成报告 | 仅 `frontend/`，不修改后端和根规划 |
| `backend_engineer` | 按规格交付 Spring Boot 模块、API 与数据能力 | 已确认 specs、API 契约、数据模型 | 后端代码、migration/Mapper、测试和完成报告 | 仅 `backend/`，不修改前端和根规划 |
| `qa_engineer` | 将 WHEN/THEN 转为自动化验收并验证集成 | 已确认 specs、前后端实现、运行说明 | 测试矩阵、自动化测试/E2E、缺陷与证据 | 只写测试/夹具/测试配置，不代写生产修复 |
| `spec_reviewer` | 实现完成后对 Spec 与代码做双向合规对账 | proposal、design、tasks、相关领域 specs、实现 diff 与测试 | 正向/反向对账表、精确覆盖率、偏差与修复 Action Items | `read-only`，不改代码、规格或测试 |
| `experience_reviewer` | 在交付后做真实 UX 走查 | 可运行版本、已确认 specs、交互目标 | 按优先级排列的体验问题、复现步骤、截图和建议 | `read-only`，不改代码或规格 |

产品角色先建立合同并经过用户确认。交互与后端在合同确认后开展；前端等待交互交付物和稳定 API 契约。QA 在相关实现完成后验收，Spec Reviewer 在实现和测试完成后对 proposal/design/tasks/领域 specs 与代码做逐条双向对账，体验走查在可运行交付后介入。前后端只有在文件互不争用、契约已冻结时才能并行。

### 4. 每个角色使用统一七部分合同

每个 `developer_instructions` 必须完整描述：

1. **角色职责**：只承担一种交付责任，并说明必需输入。
2. **输出格式**：文件布局或报告模板，以及下游所需字段。
3. **角色限制**：必须做、禁止做、越界时如何返回主 Agent。
4. **Skills**：只列根 `.codex/skills/` 中真实存在且与角色相关的 Skill，并说明触发时必须完整读取。
5. **Rules**：列出 `.codex/rules/` 中适用文件；API 规范等普通文档单独列为事实来源，不伪装成 Rule。
6. **Tools 授权**：列出允许的读、搜、写、Shell、测试、浏览器或图片能力，并受 `sandbox_mode`、当前会话审批和用户授权约束。
7. **输出语言**：沟通、报告和人类可读文档默认中文；代码标识符、命令、路径、协议字段和依赖名保留原文；代码注释遵守项目文档规则；未经授权不生成 commit message 或提交。

所有角色完成时返回统一摘要：实际修改或检查的文件、验证命令和结果、遵循的 Specs/Rules/Skills、未验证项、风险以及建议的下一交接角色。没有新的验证输出不得声称完成。

### 5. Skills 与 Rules 配置矩阵

| Agent | Skills | Rules |
| --- | --- | --- |
| `product_manager` | `openspec-explore`、`openspec-propose`、`openspec-update-change` | `workflow.md`、`documentation.md`、`repository-boundaries.md` |
| `interaction_designer` | `openspec-explore`、`openspec-update-change` | `workflow.md`、`documentation.md`、`frontend-conventions.md`、`quality-gates.md` |
| `frontend_engineer` | `openspec-apply-change`、`vercel-react-best-practices` | `workflow.md`、`frontend-conventions.md`、`quality-gates.md`、`repository-boundaries.md`、`git-safety.md`、`documentation.md` |
| `backend_engineer` | `openspec-apply-change`、`java-springboot`、按需 `mysql` | `workflow.md`、`backend-conventions.md`、按需 `database-conventions.md`、`quality-gates.md`、`repository-boundaries.md`、`git-safety.md`、`documentation.md` |
| `qa_engineer` | `openspec-apply-change` | `workflow.md`、`quality-gates.md`、任务涉及的技术 conventions、`repository-boundaries.md`、`git-safety.md` |
| `spec_reviewer` | `openspec-explore` | `workflow.md`、`quality-gates.md`、`documentation.md`、`repository-boundaries.md`、任务涉及的技术 conventions |
| `experience_reviewer` | `openspec-explore` | `quality-gates.md`、`documentation.md`、`frontend-conventions.md` |

项目当前没有 `test-driven-development`、`executing-plans`、`subagent-driven-development`、`styling-conventions` 或 `coding-conventions` 独立规范源，所以不把这些示例名登记为现有 Skills/Rules。已有 OpenSpec workflow 与 quality gates 承担相应门禁；若未来要新增独立 Skill/Rule，应另行受控变更。

### 6. Tools 授权与写入冲突控制

- `product_manager`：允许读取、搜索、OpenSpec CLI 和规划文档写入；禁止应用源码、Git 提交与推送。
- `interaction_designer`：允许读取、搜索、图片查看、浏览器检查和设计文档写入；禁止前后端业务代码。
- `frontend_engineer`：允许在 `frontend/` 内读取、搜索、编辑和运行 pnpm/lint/typecheck/test/E2E；禁止 `backend/`、根规格和 Git 交付动作。
- `backend_engineer`：允许在 `backend/` 内读取、搜索、编辑和运行 Maven/相关数据库验证；禁止 `frontend/`、根规格和 Git 交付动作。
- `qa_engineer`：允许读取全栈实现、运行验证、控制测试浏览器并编辑测试文件；禁止生产实现和替开发角色修复缺陷。
- `spec_reviewer`：只允许读取、搜索、只读 Git diff/history 和输出报告，设置 `sandbox_mode = "read-only"`；禁止修改代码、规格、tasks 或测试。
- `experience_reviewer`：只允许读取、搜索、浏览器/图片检查和返回报告，设置 `sandbox_mode = "read-only"`。

所有 Agent 继承父任务的实时 sandbox 与审批约束。角色正文是职责边界，不扩大用户对提交、推送、网络、破坏性操作或外部系统写入的授权。

### 7. Harness 校验 custom agents

根治理检查和 Harness 必须校验：

- `.codex/agents/` 包含 README 与七个命名确定的 TOML 文件。
- 每个 TOML 可解析，`name`、`description`、`developer_instructions` 存在且非空，名称全局唯一并与文件名一致。
- 每个 `developer_instructions` 包含七个必需部分，不能只有笼统人设。
- Agent 引用的 Skill 目录、Rule 文件、项目路径和命令真实存在；示例技术不得被误报为当前依赖。
- `spec_reviewer` 与 `experience_reviewer` 为只读，其余写入角色明确限制范围；未知或不支持的顶层配置字段导致检查失败。
- 三个 `AGENTS.md` 仍能解析到根 Agents、Rules 与 Skills。
- `frontend/` 与 `backend/` 不存在 `.codex`、`.agents`、`.claude`、`CLAUDE.md`、局部 rules 或局部锁文件。
- 主仓库仍不存在 `.agents`、`.claude`、`CLAUDE.md` 和根级重复 rules 目录。

Harness 只校验结构化字段、标题、路径和允许清单，不绑定角色正文的完整中文句子，以允许不改变语义的维护性改写。

## Risks / Trade-offs

- [角色过多导致简单任务成本上升] → 主 Agent 默认选择最少必要角色，七角色不是固定全量流水线。
- [Spec Reviewer 与 QA 职责重叠] → QA 负责执行测试和产出验证证据；Spec Reviewer 只读消费证据并检查规格覆盖与超纲实现。
- [多个写入型 Agent 冲突] → 默认按交付依赖串行；只并行互不争用文件且合同已冻结的任务。
- [课程示例与 Codex schema 混淆] → 只使用官方 TOML 字段，七部分内容放入 `developer_instructions`。
- [Skill/Rule 名称漂移] → Harness 校验引用存在，角色不得引用未登记能力。
- [角色说明重复稳定 Rules] → Agent 只做路由和角色特有边界，强制约束正文仍以 `.codex/rules` 为唯一规范源。
- [子仓库独立 clone 缺少角色] → 明确只支持完整 AIWorkSpace 中的受治理多 Agent 开发。

## Migration Plan

1. 修订 proposal、design、delta specs 和 tasks，确认根 Agents/Rules/Skills 集中治理及七角色合同。
2. 先修改治理检查形成缺少/非法 Agent 时失败的 RED 证据。
3. 创建 `.codex/agents/README.md` 和七个 TOML，补齐七部分合同与角色边界。
4. 更新 Manifest、三个入口、README、规则索引、OpenSpec context 和 Harness 允许清单。
5. 运行 TOML 解析、治理检查、Harness、`git diff --check` 和 OpenSpec strict validate；本变更不运行无关业务 build。
6. 获得授权后再按既有三仓库交付顺序提交或推送。

回滚时删除七个 TOML 和 Agent README，恢复 Manifest/Harness/入口的原允许清单；不涉及业务代码、数据库或 gitlink。
