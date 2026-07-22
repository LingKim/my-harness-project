## Purpose

定义项目级 React/Next.js 最佳实践 Skill 的来源、触发范围、版本事实优先级和 Harness 校验契约，使前端 AI Coding 规则可追踪、可复现且不会覆盖当前 Next.js 版本事实。

## Requirements

### Requirement: 项目提供可追踪的前端最佳实践 Skill

主仓库 MUST 在项目级 Skills 目录中提供 Vercel 官方 `vercel-react-best-practices` 的完整内容，并 MUST 通过锁文件记录其公开来源与内容哈希；项目不得因本变更附带引入与 React/Next.js 规范无关的 Vercel Skills。

#### Scenario: 完整检出项目

- **WHEN** 开发者或 AI 代理检出主仓库
- **THEN** 无需依赖用户级全局安装即可读取 `vercel-react-best-practices` 的入口和规则文件
- **AND** 锁文件包含本变更选定的前端最佳实践 Skill
- **AND** 锁文件中的其他 Skill 均经过各自项目 change 明确批准

#### Scenario: Skill 文件缺失

- **WHEN** Skill 入口、规则目录或锁记录被删除或不一致
- **THEN** Harness 检查必须失败并指出缺失的前端最佳实践契约

### Requirement: 前端任务强制触发最佳实践 Skill

根目录 `AGENTS.md` MUST 规定：涉及 `frontend/` 中 React 组件、Next.js 页面、数据获取、Server/Client Component、Server Action、bundle、渲染或性能的编写、评审和重构任务必须使用 `vercel-react-best-practices`。

#### Scenario: AI 开始 React 或 Next.js 开发任务

- **WHEN** AI 代理准备编写、评审或重构上述范围内的前端代码
- **THEN** 代理必须先加载 `vercel-react-best-practices` 并遵循与任务相关的规则

#### Scenario: 非前端任务

- **WHEN** 任务只涉及后端、数据库或与 React/Next.js 无关的主仓库文件
- **THEN** 该 Skill 不因本规则被强制加载

### Requirement: 当前 Next.js 版本事实优先

项目 MUST 明确规定 Skill 是通用最佳实践来源，而不是当前 Next.js API 行为的最高事实源；当 Skill 与 Next.js 16.2.10 的本地文档或前端局部规则冲突时，代理必须采用当前版本文档和局部规则，并说明冲突。

#### Scenario: Skill 建议与当前版本一致

- **WHEN** Skill 建议不与当前 Next.js 文档和项目规格冲突
- **THEN** 代理必须把该建议应用于相关实现或评审

#### Scenario: Skill 建议与当前版本冲突

- **WHEN** Skill 中的通用建议与 `frontend/node_modules/next/dist/docs/` 或 `frontend/AGENTS.md` 冲突
- **THEN** 代理必须采用当前版本文档或局部规则
- **AND** 不得以 Skill 内容覆盖已经验证的当前版本行为

### Requirement: Harness 校验前端 Skill 接入

主仓库 Harness MUST 使用可扩展的项目批准清单，自动校验 Skill 入口、至少一个规则文件、目标锁记录的来源与哈希以及根级 `AGENTS.md` 的触发引用，且失败信息必须能够定位缺失项、来源错误或未批准项；Harness MUST NOT 把项目永久限制为只能安装一个 Skill。

#### Scenario: 前端 Skill 接入完整

- **WHEN** 执行 `./scripts/check-harness.sh`
- **THEN** 前端 Skill 的文件、锁记录、批准清单和规则引用检查全部通过

#### Scenario: 后续批准新的项目 Skill

- **WHEN** 后续独立 OpenSpec change 完成来源审查并批准 Java、MySQL 或其他项目 Skill
- **THEN** Harness 可以扩展批准清单并接受对应锁记录
- **AND** 现有前端 Skill 的来源、文件和触发规则仍必须通过检查

#### Scenario: 锁文件出现未批准 Skill

- **WHEN** `skills-lock.json` 包含未出现在项目批准清单中的 Skill
- **THEN** Harness 检查必须失败并指出未批准的 Skill 名称

#### Scenario: AGENTS 引用被移除

- **WHEN** Skill 文件仍存在但根级 `AGENTS.md` 不再包含强制触发规则
- **THEN** Harness 检查必须失败，不得把仅安装但未启用的 Skill 判定为接入成功
