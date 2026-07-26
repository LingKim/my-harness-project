## Why

当前根级与后端 `AGENTS.md` 同时承载入口、工作流、项目规则、编码规范和 Skill 使用细节，前端 `AGENTS.md` 又缺少项目级约束；同时 `.agents/`、`.codex/` 与 `.claude/` 曾保存重复治理内容，难以确认 Agents、Rules、Skills 的唯一规范源。

在 Rules 与 Skills 已集中到主仓库根 `.codex/` 后，项目还需要一组 Codex 可真实发现的研发角色 Agent，把产品、交互、前端、后端、测试、Spec 合规审查和体验走查拆成职责单一、交付接口清晰的协作角色，而不是仅依赖一个通用代理承担全部工作。

## What Changes

- 将根级 `AGENTS.md` 保持为跨仓库入口，保留事实优先级、OpenSpec 门禁、仓库边界、权限边界和按任务加载 Agent、Rule、Skill 的路由。
- 在主仓库 `.codex/rules/` 集中工作流、仓库边界、Git 安全、质量门禁、文档、前端、后端和数据库约束。
- 将 `vercel-react-best-practices`、`java-springboot`、`mysql` 与 OpenSpec Skills 集中到主仓库 `.codex/skills/`，由根锁文件和批准清单管理。
- 在主仓库 `.codex/agents/` 新建 `product_manager`、`interaction_designer`、`frontend_engineer`、`backend_engineer`、`qa_engineer`、`spec_reviewer` 和 `experience_reviewer` 七个项目级 Codex 自定义 Agent。
- 每个 Agent 使用官方 standalone TOML 格式，至少定义 `name`、`description`、`developer_instructions`；角色正文必须包含角色职责、输出格式、角色限制、Skills、Rules、Tools 授权和输出语言。
- 七个角色按交付物而不是按技术名词切分；主 Agent 负责选择最少必要角色、控制用户确认门禁、协调并行边界和汇总最终结果。
- 产品、交互、前端、后端和测试角色只在各自明确范围内写入；Spec 合规审查和体验走查角色保持只读，分别在实现完成后和可运行交付后介入。
- Agent 只能引用项目真实存在的依赖、Skills、Rules、目录和命令；不得把示例中的 Wanderchina、shadcn/ui、Zustand 或不存在的 conventions 写成 ChinaMate 当前能力。
- **BREAKING**：更新 Manifest 与 Harness，取消对根 `.codex/agents/` 的禁止，改为校验七个 Agent 文件、TOML 必填字段、唯一名称、角色正文七部分、引用有效性和权限边界。
- 继续禁止 `frontend/.codex/`、`backend/.codex/`、`.agents/`、`.claude/` 和 `CLAUDE.md`，不在子仓库复制 Agents、Rules 或 Skills。
- 明确子仓库独立 clone 的能力边界：受治理的多 Agent 开发必须在完整 AIWorkSpace 中进行。

目标：让 Agents、Rules、Skills 都只有一个根级规范源，并让七个开发角色的输入、输出、权限和交接标准可读、可验证、可被 Codex 加载。

非目标：不修改业务功能、HTTP 契约、数据库 schema、运行时依赖或应用分层；不引入 CrewAI；不让七个 Agent 对每个任务全部启动；不自动提交、推送或更新 gitlink；不为 Codex 之外的 AI Coding 工具提供兼容适配。

验收结果：完整工作区包含七个可解析的 `.codex/agents/*.toml`；每个文件具有官方必填字段和七部分角色契约；`spec_reviewer` 能输出逐条双向对账、覆盖率统计和修复 Action Items；Agent 引用的 Skill、Rule 和项目路径真实存在；Harness 能识别缺失、重复、越权或虚假引用；前后端子仓库仍无局部 `.codex`。

主要风险：多个写入型 Agent 同时修改相同文件会产生冲突，课程示例字段又不等于 Codex TOML schema；通过主 Agent 编排、默认串行交付、只并行互不争用的工作、官方 schema 校验和项目事实校验降低风险。

## Capabilities

### New Capabilities

- `agent-skill-rule-governance`: 定义 Codex Agent 入口、七个开发角色、Rules、Skills 的职责、作用域、发现方式、单一事实源和 Harness 校验契约。

### Modified Capabilities

- `ai-workspace-repository-composition`: 将三个仓库的 AI 约束调整为根 Agents/Rules/Skills 集中治理与三个作用域入口，并继续禁止子仓库局部治理副本。
- `frontend-best-practices-skill`: 将前端 Skill、触发入口和锁定校验集中到根 `.codex`，由 `frontend-conventions.md` 和前端角色共同路由。
- `backend-java-best-practices-skill`: 将 Java/Spring Boot Skill、触发入口和锁定校验集中到根 `.codex`，由 `backend-conventions.md` 和后端角色共同路由。
- `mysql-database-sql-best-practices-skill`: 将 MySQL Skill、触发入口和安全覆盖规则集中到根 `.codex`，由 `database-conventions.md` 和后端角色按需路由。
- `backend-modular-monolith`: 将后端架构约束从大型局部 `AGENTS.md` 下沉到 `backend-conventions.md`，同时明确后端角色的模块边界与完整工作区任务边界。

## Impact

- 主仓库：`AGENTS.md`、`.codex/agents/`、`.codex/rules/`、`.codex/skills/`、`.codex/skills-lock.json`、`.codex/manifest.json`、`scripts/check-agent-governance.sh`、`scripts/check-harness.sh`、`README.md`、`openspec/config.yaml` 和相关规格。
- 前端仓库：继续使用根 Agents/Rules/Skills；不新增 `frontend/.codex/`，不引入当前 `package.json` 不存在的依赖。
- 后端仓库：继续使用根 Agents/Rules/Skills；不新增 `backend/.codex/`，不改变 Java 运行时依赖。
- 工具集成：Codex 项目级 custom agents 与 OpenSpec 1.6.0 的 Codex Skills。
- 不影响业务 API、数据库数据、应用依赖和部署产物。
