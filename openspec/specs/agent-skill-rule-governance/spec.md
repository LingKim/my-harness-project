## Purpose

定义 ChinaMate 在完整 AIWorkSpace 中使用 Agents、Rules、Skills 的分层治理结构、七个项目角色合同、集中规范源、事实优先级和自动化校验边界。
## Requirements
### Requirement: 项目采用 Agents、Rules、Skills 分层治理

系统 SHALL 使用三个 `AGENTS.md` 作为作用域入口，并将项目级自定义角色、声明式约束与任务方法分别集中到主仓库根 `.codex/agents/`、`.codex/rules/` 和 `.codex/skills/`。项目 MUST NOT 在 frontend 或 backend 子仓库维护局部 `.codex/`。

#### Scenario: AI 代理进入任一仓库

- **WHEN** AI 代理从主仓库、前端仓库或后端仓库开始任务
- **THEN** 可以先从该仓库的 `AGENTS.md` 确定需要使用的根 Agents、Rules 和 Skills
- **AND** 不需要默认加载或启动与当前任务无关的全部角色和技术栈规则

#### Scenario: 新增稳定项目约束

- **WHEN** 项目需要新增或修改长期有效的编码、安全或质量约束
- **THEN** 约束必须写入根 `.codex/rules` 中所属技术边界的文件并由入口和相关角色路由
- **AND** 不得复制到 Agent 正文、`.claude`、`.agents` 或根级重复规则目录形成第二份规范源

### Requirement: 项目提供七个职责单一的开发角色

项目 MUST 在根 `.codex/agents/` 提供 `product_manager`、`interaction_designer`、`frontend_engineer`、`backend_engineer`、`qa_engineer`、`spec_reviewer` 和 `experience_reviewer` 七个 standalone TOML Agent。每个角色 MUST 按交付物定义职责，不得仅按 React、CSS、Node、DB 等技术名词机械切分。

#### Scenario: Codex 发现项目角色

- **WHEN** Codex 在完整 AIWorkSpace 中加载项目级 custom agents
- **THEN** 七个角色都能从 `.codex/agents/<name>.toml` 被唯一识别
- **AND** TOML 中的 `name` 与文件名一致
- **AND** 每个角色的 `description` 能说明何时应调用该角色

#### Scenario: 简单任务不需要完整团队

- **WHEN** 一个任务只需要单一角色且不存在独立并行子问题
- **THEN** 主 Agent 必须只选择完成任务所需的最少角色
- **AND** 不得为了形式完整而启动七角色全流水线

### Requirement: 每个角色包含完整角色合同

每个 custom agent TOML MUST 定义非空的 `name`、`description` 和 `developer_instructions`。`developer_instructions` MUST 至少包含角色职责、输出格式、角色限制、Skills、Rules、Tools 授权和输出语言七个部分，并 MUST 说明上游输入、交付物、允许写入范围和完成报告。

#### Scenario: 角色配置完整

- **WHEN** Harness 校验任一 `.codex/agents/*.toml`
- **THEN** 文件必须能够按 TOML 解析
- **AND** `name`、`description`、`developer_instructions` 必须存在且非空
- **AND** 七个必需部分必须都能被结构化标题识别

#### Scenario: 角色配置缺少合同内容

- **WHEN** Agent 文件缺少职责、输出格式、限制、Skills、Rules、Tools 授权或输出语言中的任一部分
- **THEN** Harness 必须失败并指出缺失角色和缺失部分

### Requirement: 角色只引用真实 Skills、Rules 与项目事实

每个角色 MUST 只引用根 `.codex/skills/` 中真实存在的 Skill、根 `.codex/rules/` 中真实存在的 Rule 文件以及当前 checkout 已证实的依赖、目录和命令。Skill 触发时 MUST 完整读取对应 `SKILL.md`；已确认规格和项目 Rules MUST 优先于 Skill 示例与角色既有知识。

#### Scenario: 示例技术与当前项目不一致

- **WHEN** 角色参考内容包含 Wanderchina、shadcn/ui、Zustand、`styling-conventions`、`coding-conventions` 或其他当前项目未安装、未登记的能力
- **THEN** 角色配置不得把这些内容描述为 ChinaMate 当前事实
- **AND** Harness 必须对不存在的 Skill、Rule 或项目路径引用失败

#### Scenario: Skill 与 Rule 冲突

- **WHEN** 角色使用的第三方 Skill 建议与已确认规格或项目 Rule 不一致
- **THEN** 角色必须采用已确认规格和项目 Rule
- **AND** 不得修改第三方 Skill 来隐藏冲突

### Requirement: 角色 Tools 授权符合 Codex 配置模型

角色 MUST 使用 Codex standalone TOML 支持的配置字段。Tools 授权 MUST 通过 `sandbox_mode`、当前会话继承的工具或 MCP 以及 `developer_instructions` 中的允许/禁止边界共同表达，不得把非 Codex YAML frontmatter 的 `tools`、`skills` 或 `rules` 数组直接当成受支持的顶层配置字段。

#### Scenario: 写入型角色执行任务

- **WHEN** 产品、交互、前端、后端或测试角色获得写入任务
- **THEN** 角色只能在其合同明确允许的目录和文件类型内修改
- **AND** 当前会话 sandbox、审批模式与用户授权继续生效
- **AND** 角色合同不得扩大提交、推送、外部写入或破坏性操作权限

#### Scenario: 体验角色执行走查

- **WHEN** `experience_reviewer` 被用于交付后 UX 走查
- **THEN** 其配置必须使用 `sandbox_mode = "read-only"`
- **AND** 只允许读取、搜索、浏览器或图片检查并返回体验报告
- **AND** 不得修改代码、规格或测试

#### Scenario: Spec 合规角色执行审查

- **WHEN** `spec_reviewer` 在 change 实现完成后检查规格合规性
- **THEN** 其配置必须使用 `sandbox_mode = "read-only"`
- **AND** 只允许读取、搜索、只读 Git 检查和返回对账报告
- **AND** 不得修改代码、规格、tasks 或测试

#### Scenario: 出现未知顶层字段

- **WHEN** custom agent TOML 包含项目未批准或 Codex 未支持的顶层配置字段
- **THEN** Harness 必须失败并指出文件和字段

### Requirement: 角色交付接口清晰并由主 Agent 协调

产品角色的规格交付 MUST 经过用户确认后才能进入实现。交互、前端、后端、测试和体验角色 MUST 消费明确的上游交付物，并返回可供下一角色或主 Agent 使用的结构化完成报告。主 Agent MUST 负责最终汇总和冲突处理。

#### Scenario: 规格尚未确认

- **WHEN** 产品角色已经形成 proposal、specs、design 和 tasks 但用户尚未确认
- **THEN** 前端、后端和测试角色不得开始实现
- **AND** 主 Agent 必须等待确认或继续澄清规格

#### Scenario: 前后端并行开发

- **WHEN** 已确认规格和 API 契约允许前端与后端处理互不争用的文件
- **THEN** 主 Agent 可以并行委派两个角色
- **AND** 两个角色必须分别限制在 frontend 与 backend 子仓库
- **AND** 契约未冻结或文件存在争用时必须串行

#### Scenario: 角色完成交付

- **WHEN** 任一角色声明任务完成
- **THEN** 完成报告必须列出实际修改或检查的文件、验证命令和结果、遵循的 Specs/Rules/Skills、未验证项、风险和下一交接建议
- **AND** 没有新的验证输出不得声称完成

### Requirement: 后端开发、QA 与 Spec Reviewer 形成工程实践责任链

项目 MUST 分别通过 `backend_engineer`、`qa_engineer` 和 `spec_reviewer` 承担后端工程实践的实现、自主验证和只读审查责任。三个角色 MUST 根据任务影响范围加载 `backend-conventions.md`、`database-conventions.md`、`java-springboot` 与 `mysql` Skill，不得把仅列出文件路径视为已经遵循工程实践。

#### Scenario: 后端角色实现 Java 和数据库能力

- **WHEN** `backend_engineer` 实现同时涉及 Java/Spring Boot 与持久化的 change
- **THEN** 完成报告必须列出任务直接相关的 Java、事务、分层、MyBatis-Plus、Flyway 和数据库安全检查结果
- **AND** 任何偏离默认技术路径的实现必须给出已确认设计依据、限定范围、取舍和验证结果

#### Scenario: QA 验证后端数据库交付

- **WHEN** `qa_engineer` 验证涉及后端或数据库的实现
- **THEN** 必须加载相关 Java/MySQL Skills 与后端/数据库 Rules，并区分业务场景验证和工程实践验证
- **AND** 必须检查适用的事务原子性、持久化方案、migration、参数绑定和数据库集成风险
- **AND** 发现生产实现偏差时只返回缺陷，不得越权修改生产源码

#### Scenario: Spec Reviewer 审查已完成实现

- **WHEN** `spec_reviewer` 检查涉及后端或数据库的 change
- **THEN** 除 Spec 双向对账外还必须独立执行实现对项目 Rules 和技术基线的合规检查
- **AND** 即使业务 Spec 未重复写出稳定技术 Rule，违反该 Rule 的实现仍必须标记为偏差并提供文件位置

### Requirement: Spec Reviewer 执行双向逐条对账

`spec_reviewer` MUST 在实现完成后读取 change 的 `proposal.md`、`design.md`、`tasks.md`、相关领域 specs、任务适用的项目 Rules/Skills、实现 diff 和测试证据，执行 Spec → 代码正向对账、代码 → Spec 反向对账以及代码 → 项目 Rules/技术基线合规检查。报告 MUST 保留每条独立要求，不得主观合并或跳过，并为每个判断提供尽可能精确的文件路径和行号。

#### Scenario: 检查 Spec 要求覆盖情况

- **WHEN** Spec Reviewer 获得完整 change 和实现范围
- **THEN** 必须逐条标记已覆盖、未覆盖或部分覆盖/偏差
- **AND** 必须基于实际条目数计算正向覆盖率和按 Spec 来源分组的统计
- **AND** 未提供的输入必须明确标注为“未提供”，不得推测为已覆盖

#### Scenario: 检查超纲实现

- **WHEN** 实现 diff 中出现 proposal、design、tasks 或领域 spec 未要求的行为
- **THEN** 反向对账表必须列出代码位置、实现内容、状态和可追溯的 Spec 依据或“无 Spec 依据”
- **AND** 报告必须按优先级给出修复 Action Items，但不得直接修改任何文件

#### Scenario: 检查稳定项目 Rule 合规

- **WHEN** 实现采用了业务 Spec 未重复声明但项目 Rules 已明确约束的技术方案
- **THEN** Reviewer 必须独立判断实现是否符合适用 Rule 和技术基线
- **AND** 不得因为业务 Spec 没有重复 MyBatis-Plus、事务或分层规则而跳过对应检查

### Requirement: 角色输出语言遵循项目文档约定

七个角色 MUST 使用中文进行沟通、完成报告和人类可读项目文档输出；`spec_reviewer` 的报告语言 MUST 与被审查 Spec 的语言一致。代码标识符、命令、路径、协议字段、依赖名称和没有稳定中文译名的术语 MUST 保留原文。代码注释 MUST 遵守项目文档规则，未经用户授权角色不得提交代码或生成虚假的 commit 结果。

#### Scenario: 角色输出完成报告

- **WHEN** 任一角色返回任务结果
- **THEN** 报告正文必须使用中文
- **AND** 文件路径、命令、代码标识符和协议字段保持原文
- **AND** 未执行的测试、commit 或 push 不得写成已完成

### Requirement: 技术约束在根目录集中分文件存放

主仓库根 `.codex/rules/frontend-conventions.md` MUST 作为前端约束主文件；`.codex/rules/backend-conventions.md` 和 `.codex/rules/database-conventions.md` MUST 分别承载后端应用与数据库约束。集中目录同时保存跨仓库工作流、仓库边界、Git 安全、质量门禁和文档规则，但不同技术边界不得合并成重复正文。

#### Scenario: 处理前端任务

- **WHEN** 任务涉及前端 React、Next.js、TypeScript、样式、国际化、可访问性或前端测试
- **THEN** 前端入口和相关角色必须路由到 `frontend-conventions.md`
- **AND** 不要求加载后端或数据库 conventions

#### Scenario: 处理数据库任务

- **WHEN** 任务涉及 MySQL、Flyway、MyBatis SQL、schema、索引、事务锁或数据库运维
- **THEN** 后端入口和 `backend_engineer` 必须同时路由到 `database-conventions.md` 和 `mysql` Skill
- **AND** Java/Spring Boot 相关工作仍适用 `backend-conventions.md`

### Requirement: 项目使用统一事实优先级

三个仓库的入口和七个角色 MUST 使用一致的事实优先级：已确认 OpenSpec；当前依赖、源码、测试、migration 与真实输出；作用域内项目 Rules；当前版本官方文档；相关 Skills；代理既有知识。若当前实现违反已确认规格或 Rule，代理 MUST 报告差异并通过受控变更修正，不得静默把现状当成新规范。

#### Scenario: 描述性文档与测试输出冲突

- **WHEN** README、架构说明、角色示例或 Skill 示例与当前依赖、源码、测试或真实输出不一致
- **THEN** 代理必须以已验证项目事实为当前状态依据
- **AND** 同时检查该状态是否违反已确认规格或强制 Rule

### Requirement: Rules 可以渐进发现并稳定校验

每个仓库 SHALL 提供规则索引或入口路由，记录 Rule 文件、适用范围和稳定 Rule ID 前缀；Harness MUST 校验文件存在、引用有效和 Rule ID 唯一，但 MUST NOT 依赖完整自然语言句子或固定段落位置判断规则是否接入。

#### Scenario: 规则正文改写但语义和 ID 保持

- **WHEN** 维护者在不改变约束语义的情况下改写 Rule 正文
- **THEN** Harness 不得仅因中文措辞变化而失败
- **AND** 文件、路由、Rule ID 和适用范围仍必须通过检查

#### Scenario: 必需规则文件被删除

- **WHEN** conventions 文件、规则索引或入口引用缺失
- **THEN** Harness 必须失败并指出缺失文件或无效引用

### Requirement: Skills 集中存放并可追踪来源

前端、Java 与 MySQL Skills MUST 统一由主仓库根 `.codex/skills/` 拥有，并由根 `.codex/skills-lock.json` 记录批准名称、来源、路径和内容哈希。第三方 Skill 内容 MUST 保持供应商原样，项目覆盖规则 MUST 写入根 conventions。

#### Scenario: 完整工作区检出

- **WHEN** 开发者递归检出主仓库及两个 submodule
- **THEN** 七个角色和前后端无需依赖用户级全局安装即可从根目录读取相关 Skills
- **AND** 每个 Skill 均可从统一根锁文件验证来源和内容哈希

### Requirement: 项目只维护 Codex 治理目录

项目 MUST 将主仓库根 `.codex` 视为 Codex 治理唯一规范根，并允许其中的 `agents/`、`rules/`、`skills/`、锁文件和 Manifest。项目内 `frontend/.codex/`、`backend/.codex/`、`.agents/`、`.claude/` 与 `CLAUDE.md` MUST NOT 存在；OpenSpec 只允许保留根 `.codex/skills/openspec-*` 生成入口。

#### Scenario: Codex 读取规范源

- **WHEN** Codex 从完整工作区开始任务
- **THEN** `AGENTS.md` 必须路由到根 `.codex/agents`、`.codex/rules` 和 `.codex/skills`
- **AND** 项目不得在子仓库或其他工具目录维护相同内容的复制

#### Scenario: 出现其他工具入口

- **WHEN** 项目中出现 `.claude/`、`CLAUDE.md`、`.agents/`、`frontend/.codex/` 或 `backend/.codex/`
- **THEN** Harness 必须失败并指出不允许的兼容目录或局部治理副本

#### Scenario: OpenSpec 更新恢复重复目录

- **WHEN** 固定版本 `openspec update` 创建 `.agents/` 或 `.claude/`
- **THEN** Harness 必须失败并要求删除非 Codex 生成物
- **AND** 根 `.codex/agents/*.toml` 与 `.codex/skills/openspec-*` 仍是允许的 Codex 项目配置

### Requirement: 项目级单人全栈编排 Skill 受集中治理
主仓库根 `.codex/skills/` SHALL 提供 `chinamate-fullstack-delivery` 项目级 Skill，并由 Manifest、Skills 锁定信息、入口路由和治理检查登记。Skill MUST 保持 `SKILL.md` 精简，把控制矩阵、阶段细则和结构化格式放入直接引用的 references，把确定性操作放入 scripts。

#### Scenario: Codex 发现编排 Skill
- **WHEN** Codex 从完整 AIWorkSpace 处理业务、跨栈、实现、验证或验收任务
- **THEN** 可以从根入口和 Skill metadata 发现 `chinamate-fullstack-delivery`
- **AND** 不需要在 frontend 或 backend 复制 Skill

#### Scenario: 编排 Skill 内容发生变化
- **WHEN** 项目修改 Skill、references 或 scripts
- **THEN** Skills 锁定信息和治理检查必须识别批准来源与当前内容
- **AND** 未同步锁定信息或引用失效时治理检查失败

### Requirement: 集中治理声明保持单一且一致
根 AGENTS、Manifest、Rules、Skills 锁定信息和三个仓库入口 MUST 一致声明所有项目 Agents、Rules 与 Skills 由主仓库根 `.codex/` 拥有。子仓库只路由到根治理能力，不得出现“技术 Rules 或 Skills 跟随 submodule”的冲突声明。

#### Scenario: 治理文本出现冲突归属
- **WHEN** 任一强制 Rule 或入口把前端、后端技术 Rules 或 Skills 声明为由 submodule 自有
- **THEN** 治理检查失败并指出冲突文件
- **AND** 不得以当前目录偶然存在为理由忽略已确认的集中治理规格

### Requirement: 治理检查验证控制矩阵与知识入口结构
Harness SHALL 验证 Rule 控制矩阵、跨栈地图、领域术语桥、编排 Skill 及其必需 references/scripts 存在、引用有效且没有重复规范源。结构检查 MUST 使用稳定 ID、字段或路径，不得依赖整段中文措辞。

#### Scenario: 编排资源缺失
- **WHEN** Skill 必需 reference、控制矩阵或跨栈知识入口被删除
- **THEN** 治理检查失败并指出缺失路径

#### Scenario: Rule 正文在语义不变时改写
- **WHEN** Rule 保持 ID、作用域和控制矩阵关系但正文被等价改写
- **THEN** 治理检查不得仅因句子变化失败
