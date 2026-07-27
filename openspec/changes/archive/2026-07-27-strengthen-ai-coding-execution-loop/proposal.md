## Why

ChinaMate 由同一名开发者承担产品、交互、前端、后端、测试与验收，现有七角色、Rules、OpenSpec Skills 和交付证据虽然边界完整，但仍需要开发者在多个入口之间手工选择、切换和汇总，跨会话时也缺少一个统一的阶段状态与恢复入口。现在需要把分散治理能力编排成适合单人全栈开发的轻量交付闭环，并把能够确定性检查的规则、验证结果和跨栈知识交给脚本与结构化文档，而不是继续依赖 AI 自觉记忆。

## Goals

- 以单人全栈交付为默认路径，按实际工作阶段调用最少必要角色能力，不要求形式化启动完整七角色团队。
- 提供一个项目级薄编排 Skill，复用既有 OpenSpec、Rules、Agents 和 evidence，不复制它们的正文或建立第二套状态系统。
- 建立 Rule 控制矩阵，明确每条关键 Rule 由脚本、自动化测试、只读审查、主 Agent 还是用户确认负责。
- 通过确定性脚本采集真实验证命令、时间、退出状态和摘要，生成可人工复核的证据片段，但不自行把未运行项标记为通过。
- 建立最小跨栈业务地图、领域术语桥和需求来源追溯，使产品语言能够定位到页面、API、后端模块、数据与测试。
- 对治理导航、跨栈地图和交付证据提供轻量漂移检查，并定义升级为重型知识库的客观触发条件。
- 把真实全栈演练暴露的 worktree 依赖隔离、JDK/Mockito 兼容、分页边界覆盖和零残留清理收敛为可重复执行的 Skill 防线。

## Non-Goals

- 不把一个人伪装成七个并行开发者，不强制简单任务走完整角色流水线。
- 不新增与 OpenSpec 重复的 `TECH_SPEC.md`、独立任务数据库或第二套 change 生命周期。
- 不把现有 Markdown Rules 复制成 YAML 红线，不让脚本解释任意自然语言规则。
- 不自动提交、推送、归档、写入用户确认状态或调用真实外部服务。
- 不为当前规模建立逐文件 project wiki、全量 SHA 知识库或复杂可视化平台。

## What Changes

- 新增根 `.codex/skills/chinamate-fullstack-delivery/`，以“需求收口 → 规格确认 → 交互/契约冻结 → 实现 → 验证 → Spec/体验审查 → 证据与归档建议”的阶段编排单人全栈交付。
- 新增 Rule 控制矩阵，区分机器门禁、测试、Reviewer、主 Agent 与用户硬确认；只为可确定性验证的 Critical Rule 增加脚本检查。
- 新增验证证据采集脚本及测试，以显式命令清单为输入，输出结构化结果；脚本不得执行未声明命令、修改 task checkbox、伪造 `PASS` 或自动归档。
- 新增跨栈系统地图与领域术语桥最小结构，并用现有 M02 前端底座和后端模块化单体事实建立首个可验证基线。
- 新增轻量漂移检查，验证治理入口、控制矩阵引用、业务地图路径和证据时效标记；文档规模达到明确阈值后才建议引入模块级 wiki 或 SHA 基线。
- 修正 `.codex/rules/repository-boundaries.md` 中“技术 Rules 与 Skills 跟随 submodule”的漂移表述，使其与已确认的根 `.codex/` 集中治理规格一致。
- 扩展治理 Manifest、锁定信息、Harness、README 和相关 OpenSpec 规格，使新增 Skill、脚本、知识入口和验证命令可发现且可复核。
- 新增只读交付环境预检与 cleanup manifest 检查器；要求分页等边界行为使用超过单个边界的代表性 fixture，清理完成后以机器可复核结果证明数据库、端口、worktree、分支和临时路径无残留。

## Acceptance Outcomes

- 一个新的业务 change 可以从单一 Skill 入口获得当前阶段、下一动作、所需最少角色能力、硬关卡和恢复说明。
- 简单的单仓库任务不会被迫执行无关角色或无关测试；跨栈任务在合同冻结后才进入前后端实现。
- 控制矩阵中的每条 Critical Rule 都有唯一 Rule ID、责任主体和可执行或人工门禁，不出现“无人负责”。
- 证据采集脚本的测试覆盖成功、失败、未运行、命令拒绝、敏感输出裁剪和旧证据失效场景。
- 跨栈地图中的页面、API、后端模块、数据归属和测试入口只能引用真实路径或明确标记为“计划中”。
- 临时 frontend worktree 不会因复用仓库外 `node_modules` 软链接而把 Turbopack panic 误判为应用缺陷；Java 21+ 且使用 Mockito 时会在完整测试前给出 agent attachment 风险提示。
- 分页 change 的真实场景至少使用 `pageSize + 1` 条 fixture 证明跨页边界；临时全栈演练结束后 cleanup checker 对声明的资源全部返回 `ABSENT` 或 `CLOSED`。
- `./scripts/check-agent-governance.sh`、`./scripts/check-harness.sh`、OpenSpec strict validate 和 `git diff --check` 通过。

## Capabilities

### New Capabilities

- `solo-fullstack-ai-delivery`: 定义单人承担产品、交互、前后端、测试和验收时的阶段编排、角色切换、控制矩阵、跨栈知识与轻量漂移门禁。

### Modified Capabilities

- `agent-skill-rule-governance`: 登记并校验项目级单人全栈编排 Skill、控制矩阵与根 `.codex/` 集中治理的一致性。
- `change-delivery-evidence`: 支持由受控脚本采集真实验证结果、拒绝伪造通过，并在验证后相关输入变化时识别证据失效。

## Impact

- 主要影响主仓库 `.codex/skills/`、`.codex/rules/`、`.codex/manifest.json`、`.codex/skills-lock.json`、`scripts/`、`docs/architecture/`、`docs/standards/`、`docs/templates/`、`README.md` 和 OpenSpec artifacts。
- `frontend/` 与 `backend/` 本轮原则上只作为地图事实和验证入口读取；若实现阶段确认必须修改局部治理检查或文档，必须分别列出子仓库任务、验证和 gitlink 交付步骤。
- 不改变前端页面、HTTP API、数据库 schema、运行时业务行为或外部服务配置。
- 主要风险是把单人流程做成重型官僚流程、Skill 与现有 Rules 重复、自动证据脚本误执行命令或把摘要误当完整证明；通过薄编排、显式命令白名单、真实退出状态、最小文档和渐进触发条件控制风险。
