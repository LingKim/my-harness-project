## ADDED Requirements

### Requirement: 单人全栈交付使用一个阶段编排入口
系统 SHALL 提供项目级 `chinamate-fullstack-delivery` Skill，为同一名开发者依次承担产品、交互、前端、后端、测试和验收提供统一入口。Skill MUST 复用现有 OpenSpec、Agents、Rules 和交付证据，不得创建独立 change 生命周期或复制强制规则正文。

#### Scenario: 开始新的跨栈业务功能
- **WHEN** 开发者要求实现同时影响产品合同、页面、API 和后端行为的新功能
- **THEN** Skill 先进入需求与规格阶段并列出当前阶段、下一动作、所需最少角色能力和用户硬关卡
- **AND** 在规格获得用户确认前不得进入生产实现

#### Scenario: 处理简单单仓库任务
- **WHEN** 任务只影响一个仓库且不需要独立产品、交互或跨栈合同
- **THEN** Skill 选择满足风险的最短路径
- **AND** 不得为了形式完整而要求启动全部七个角色或运行无关验证

### Requirement: 编排状态从现有事实推导并可跨会话恢复
Skill MUST 从活动 OpenSpec artifacts、tasks、Git/submodule 状态、测试事实和 `evidence.md` 推导当前阶段，不得使用聊天记录作为唯一状态源。恢复结果 MUST 区分已确认事实、未完成任务、失败、阻塞、未验证项和建议下一步。

#### Scenario: 新会话继续未完成 change
- **WHEN** 开发者在新会话要求继续一个活动 change
- **THEN** Skill 读取 change 状态、相关规格、tasks、工作树和已有证据后报告恢复摘要
- **AND** 不得仅根据已勾选 task 或旧聊天结论声称实现或验证已经完成

#### Scenario: 证据包含未解决失败
- **WHEN** 当前 change 的证据仍有未解决 `FAIL`、阻断级偏差或 P0/P1 体验问题
- **THEN** Skill 将阶段保持在修复或重新验证
- **AND** 不得建议同步或归档

### Requirement: 单人模式按角色视角串行切换
Skill SHALL 把七个项目角色视为同一开发者在不同交付阶段采用的职责视角，并默认串行完成合同、设计、实现、QA 和验收。只有用户明确要求委派、合同已经冻结且文件互不争用时，才 MAY 使用并行子任务。

#### Scenario: 同一人完成前后端功能
- **WHEN** 已确认 change 同时包含前端和后端任务
- **THEN** 编排先冻结 API、数据和错误合同，再按 tasks 依赖顺序进入前端和后端实现
- **AND** 每次角色视角切换都明确输入、输出、未完成项和下一交接点

### Requirement: 关键阶段具有人机硬关卡
编排 MUST 在规格确认、不可逆或外部 Git 动作、存在未解决质量问题以及最终归档建议前执行相应硬关卡。用户确认 MUST 来自真实用户消息，不得由 Agent 自行生成、补写或从旧版本规格推测。

#### Scenario: 用户尚未确认规格
- **WHEN** proposal、specs、design 和 tasks 已完整但当前版本没有用户确认
- **THEN** Skill 停止在实现门禁并请求确认
- **AND** 不得修改生产代码

#### Scenario: 准备提交或推送
- **WHEN** 实现和验证完成但用户没有在当前授权范围内要求 Git 写操作
- **THEN** Skill只报告建议操作和受影响仓库
- **AND** 不得执行暂存、提交、推送、更新 gitlink 或归档

### Requirement: Rule 控制矩阵定义唯一责任和门禁
项目 SHALL 提供 Rule 控制矩阵，为纳入范围的 Rule ID 记录作用域、风险级别、责任主体、控制类型、执行入口、阻断条件和证据位置。每条 Critical Rule MUST 有且只有一个主要责任主体，并至少配置一个机器门禁、自动化测试、只读审查、主 Agent 检查或用户确认。

#### Scenario: 治理检查扫描控制矩阵
- **WHEN** 运行 AI 交付治理检查
- **THEN** 所有矩阵 Rule ID 必须真实存在且唯一
- **AND** Critical Rule 缺少责任主体、控制方式或证据位置时检查失败并指出对应 ID

#### Scenario: 自然语言 Rule 无法机器判断
- **WHEN** 一条 Rule 依赖产品判断、风险判断或用户授权
- **THEN** 控制矩阵将其标记为 Reviewer、主 Agent 或用户门禁
- **AND** 脚本不得伪装成能够理解并自动证明该自然语言语义

### Requirement: 跨栈知识使用最小地图和领域术语桥
项目 SHALL 提供可渐进维护的跨栈系统地图与领域术语桥，关联真实产品模块、前端路由或组件、API、后端模块、数据归属和测试入口。尚未实现的能力 MUST 标记为计划中，不得创建不存在的代码路径或把计划描述为当前事实。

#### Scenario: 首个业务 change 进行代码定位
- **WHEN** 产品需求使用业务术语描述账号、攻略、AI 助手或社区行为
- **THEN** Agent 可以通过术语桥和系统地图定位候选前端、API、后端模块、数据与测试范围
- **AND** 最终改动点仍必须通过源码搜索和实现证据确认

#### Scenario: 地图引用的路径发生变化
- **WHEN** 治理检查发现系统地图中的当前路径不存在或模块状态与登记不一致
- **THEN** 检查失败并指出漂移条目
- **AND** 计划中路径不因为尚未创建而失败

### Requirement: 需求来源可追溯且禁止语义扩张
重要业务 change MUST 在 proposal、spec、design 或编排产物中记录需求来源标识，来源可以是 PRD 编号、设计稿节点、API 决策、用户原话或已有 Spec。新增触发点、拦截点、权限或失败行为 MUST 能追溯到明确来源，不得仅以“保持一致”或“看起来属于同类”为依据扩大范围。

#### Scenario: AI 建议增加未要求的相似行为
- **WHEN** 实现阶段发现另一个看似相似但没有需求来源的入口
- **THEN** Skill 将其记录为待确认或非目标
- **AND** 不得直接纳入本次实现

### Requirement: 重型知识库按客观触发条件升级
项目 MUST 保持知识体系与当前规模相称；只有达到文档规定的文件规模、重复定位、漂移事故或多源物料复杂度阈值时，才建议新增模块级 wiki、SHA 基线或专用收料脚本。

#### Scenario: 当前项目尚未达到升级阈值
- **WHEN** 跨栈地图和现有架构文档足以定位业务代码且没有重复漂移证据
- **THEN** 项目继续维护轻量地图和术语桥
- **AND** 不得提前建立逐文件 wiki 或全量知识索引

### Requirement: 临时交付环境在重型验证前执行兼容性预检
Skill SHALL 提供只读环境预检，识别 frontend worktree 的仓库外 `node_modules` 软链接，以及 Java 21+、Mockito 与 agent attachment 配置的已知组合风险。预检 MUST 区分应用失败、环境阻塞和需要人工复核的风险，不得自行安装依赖、修改构建配置或扩大授权。

#### Scenario: worktree 复用外部 node_modules
- **WHEN** 临时 frontend worktree 的 `node_modules` 是指向该 worktree 外部的软链接
- **THEN** 预检报告 `BLOCKED` 并说明 Turbopack filesystem-root 风险
- **AND** 建议在当前 worktree 使用 pnpm store 离线安装或明确采用已验证的 fallback，不得把该错误记录为业务回归

#### Scenario: Java 21 以上运行 Mockito 测试
- **WHEN** 后端测试使用 Mockito、Java 主版本不低于 21 且构建未显式配置测试 agent
- **THEN** 预检报告 `REVIEW_REQUIRED` 并要求先运行最小 Mockito 测试
- **AND** 不得因动态 attach 失败而跳过断言或伪造测试通过

### Requirement: 真实场景验证覆盖行为边界两侧
涉及分页、阈值、稳定排序、重试或幂等边界的 change MUST 使用能够跨越边界的 fixture。分页验收至少使用 `pageSize + 1` 条记录，并记录第一页、下一页、`hasNext` 与稳定 tie-breaker；单条 CRUD smoke test MUST NOT 作为分页通过证据。

#### Scenario: 验证分页实现
- **WHEN** change 声称分页行为已通过真实数据库验收
- **THEN** evidence 记录至少 `pageSize + 1` 条 fixture 的两页结果
- **AND** 同排序值记录仍按已冻结的次级排序键稳定返回

### Requirement: 临时交付使用声明式 cleanup manifest 证明零残留
需要删除临时数据库、服务、worktree、分支或文件的演练 SHALL 在清理前声明精确资源与期望终态。cleanup checker MUST 只执行固定的只读检查、拒绝任意 Shell 和越界目标，并从环境变量读取数据库凭据。只有全部声明资源达到 `ABSENT` 或 `CLOSED`，Skill 才可声明零残留。

#### Scenario: 清理全栈演练
- **WHEN** 用户已授权删除专用数据库、临时 worktree 和测试分支
- **THEN** 主 Agent按精确目标清理后运行 cleanup checker
- **AND** checker 证明数据库、监听端口、临时路径、Git worktree 与分支均不存在

#### Scenario: manifest 包含不安全目标
- **WHEN** cleanup manifest 声明仓库根、文件系统根、非回环端口主机、非法数据库名或任意命令
- **THEN** checker 拒绝执行并指出不安全字段
- **AND** 不对该目标执行删除或外部写操作
