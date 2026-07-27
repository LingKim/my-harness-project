## Purpose

定义项目级 React/Next.js 最佳实践 Skill 的来源、触发范围、版本事实优先级和 Harness 校验契约，使前端 AI Coding 规则可追踪、可复现且不会覆盖当前 Next.js 版本事实。

## Requirements

### Requirement: 项目提供可追踪的前端最佳实践 Skill

主仓库根 `.codex/skills/` MUST 提供 Vercel 官方 `vercel-react-best-practices` 的完整内容，并 MUST 通过根 `.codex/skills-lock.json` 记录其公开来源与内容哈希；项目不得附带引入无关 Vercel Skills，前端子仓库不得维护第二份规范副本。

#### Scenario: 完整检出项目

- **WHEN** 开发者或 AI 代理递归检出完整 AIWorkSpace
- **THEN** 无需依赖用户级全局安装即可从根目录读取 `vercel-react-best-practices` 的入口和规则文件
- **AND** 根统一锁文件包含本变更选定的 Skill
- **AND** 锁文件中的其他 Skill 均经过独立 change 明确批准

#### Scenario: Skill 文件缺失

- **WHEN** 前端 Skill 入口、规则目录或锁记录被删除或不一致
- **THEN** 前端局部检查或根 Harness 必须失败并指出缺失的前端最佳实践契约
### Requirement: 前端任务强制触发最佳实践 Skill

前端 `AGENTS.md` MUST 规定：涉及 React 组件、Next.js 页面、数据获取、Server/Client Component、Server Action、bundle、渲染或性能的编写、评审和重构任务必须先读取 `../.codex/rules/frontend-conventions.md`，再使用 `../.codex/skills/vercel-react-best-practices`。

#### Scenario: AI 开始 React 或 Next.js 开发任务

- **WHEN** AI 代理准备编写、评审或重构上述范围内的前端代码
- **THEN** 代理必须加载 `frontend-conventions.md` 和 `vercel-react-best-practices`
- **AND** 只应用与项目事实和任务范围一致的 Skill 规则

#### Scenario: 非前端任务

- **WHEN** 任务只涉及后端、数据库或与 React/Next.js 无关的主仓库文件
- **THEN** 前端 Rule 与 Skill 不因本规则被强制加载
### Requirement: 当前 Next.js 版本事实优先

根 `.codex/rules/frontend-conventions.md` MUST 明确 Skill 是通用最佳实践来源，而不是当前 Next.js API 行为的最高事实源；当 Skill 与当前安装版本的 `node_modules/next/dist/docs/`、实际依赖、源码或测试冲突时，代理必须采用已验证的当前项目事实，并检查是否需要更新规格或 Rule。

#### Scenario: Skill 建议与当前版本一致

- **WHEN** Skill 建议不与项目规格、`frontend-conventions.md`、当前 Next.js 文档和实际测试冲突
- **THEN** 代理必须把该建议应用于相关实现或评审

#### Scenario: Skill 建议与当前版本冲突

- **WHEN** Skill 中的通用建议与当前 Next.js 本地文档、依赖、源码或测试冲突
- **THEN** 代理必须采用当前版本证据并说明冲突
- **AND** 不得以 Skill 内容覆盖已经验证的当前行为
### Requirement: Harness 校验前端 Skill 接入

前端局部检查与主仓库 Harness MUST 自动校验前端 `AGENTS.md`、根 `frontend-conventions.md`、根 Skill 入口、至少一个规则文件、统一锁记录的来源与哈希及其相互引用；校验 MUST NOT 要求具体中文句子位于根 `AGENTS.md`。

#### Scenario: 前端 Skill 接入完整

- **WHEN** 执行前端局部治理检查或 `./scripts/check-harness.sh`
- **THEN** 前端入口、conventions、Skill 文件、锁记录和路由检查全部通过

#### Scenario: 后续批准新的前端 Skill

- **WHEN** 后续独立 OpenSpec change 完成来源审查并批准新的前端项目 Skill
- **THEN** 前端批准清单和锁文件可以扩展并接受对应记录
- **AND** 现有 Skill 的来源、文件和触发规则仍必须通过检查

#### Scenario: 统一锁文件出现未批准 Skill

- **WHEN** 根统一锁文件包含未出现在批准清单中的 Skill
- **THEN** 检查必须失败并指出未批准的 Skill 名称

#### Scenario: 前端路由引用被移除

- **WHEN** Skill 文件仍存在但前端 `AGENTS.md` 不再路由到 conventions 或 Skill
- **THEN** 检查必须失败，不得把仅安装但未启用的 Skill 判定为接入成功

#### Scenario: 前端子仓库出现 Skill 规范副本

- **WHEN** 前端子仓库重新出现完整前端 Skill 副本
- **THEN** Harness 必须失败并指出重复规范源
