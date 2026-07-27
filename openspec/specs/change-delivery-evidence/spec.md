## Purpose

定义重要 OpenSpec change 的持久化交付证据结构、真实性与安全边界、审查报告交接及归档前时效检查，确保验证和残余风险可长期追溯。
## Requirements
### Requirement: 重要 OpenSpec change 持久化交付证据

业务功能、行为变化、跨仓库、API、数据库、安全、架构或治理行为 change MUST 在自身 change 根目录维护 `evidence.md`，并在归档后继续保留。纯文案、机械格式化和只读探索 MAY 不创建该文件，但交付说明 MUST 如实说明适用性判断。

#### Scenario: 业务 change 准备归档

- **WHEN** 一个包含应用实现或可观察行为变化的 OpenSpec change 完成任务并准备归档
- **THEN** change 根目录必须存在 `evidence.md`
- **AND** 文件必须记录实际验证、审查结论、未验证项和是否建议归档

#### Scenario: 纯文案变更完成

- **WHEN** change 只修改人类可读文案或执行无行为变化的机械格式化
- **THEN** 可以不创建 `evidence.md`
- **AND** 不得把未执行的测试或审查描述为已完成

### Requirement: 交付证据使用统一且可读的最小结构

`evidence.md` MUST 使用中文 Markdown，并至少包含基本信息、自动化验证、手工或真实场景验证、QA 结论、Spec 合规审查、体验走查、未验证项与残余风险、最终交付结论。每项验证 MUST 区分 `PASS`、`FAIL`、`BLOCKED` 或 `NOT_RUN`，不适用的审查 MUST 明确标记原因。

#### Scenario: 自动化验证通过

- **WHEN** Agent 实际执行前端、后端或根级验证命令
- **THEN** 证据必须记录执行时间、仓库、执行角色、完整命令、结果状态和关键输出摘要
- **AND** 关键输出摘要必须足以说明成功或失败依据，但不要求保存完整终端日志

#### Scenario: 验证未运行或受阻

- **WHEN** 某项验证因环境、权限、网络、缺少账号或不适用而没有完成
- **THEN** 证据必须记录为 `BLOCKED` 或 `NOT_RUN`
- **AND** 必须说明原因、影响范围和建议的后续处理

### Requirement: 证据只记录真实且安全的验证结果

交付证据 MUST 来源于实际命令输出、测试报告、页面观察或审查报告，不得把计划、task checkbox 或推测记录为通过。证据 MUST NOT 保存凭据、token、Cookie、隐私数据、原始完整敏感日志、构建缓存或无关大体积产物；需要截图时必须脱敏并使用 change 内相对路径引用。

#### Scenario: Agent 汇总命令结果

- **WHEN** 开发或 QA 角色返回验证结果
- **THEN** 主 Agent 只能记录实际执行的命令、结果和可复核摘要
- **AND** 未执行项必须保持为 `NOT_RUN`，不得根据预期补写为 `PASS`

#### Scenario: 页面证据包含敏感信息

- **WHEN** 体验走查截图或日志包含账号、Cookie、token 或隐私数据
- **THEN** 敏感信息必须在保存前脱敏
- **AND** 无法安全脱敏的证据不得写入仓库

### Requirement: 主 Agent 持久化只读审查角色的报告

QA、开发和审查角色 MUST 返回结构化结果；主 Agent MUST 负责把交付证据写入 change。`spec_reviewer` 与 `experience_reviewer` MUST 继续保持只读，完整报告较长时由主 Agent 分别保存到 `reviews/spec-review.md` 和 `reviews/experience-review.md`，并从 `evidence.md` 链接；截图按需保存到 `assets/`。

#### Scenario: Spec Reviewer 完成审查

- **WHEN** `spec_reviewer` 返回双向对账、覆盖率和 Action Items
- **THEN** 主 Agent 必须在 `evidence.md` 记录审查是否执行、结论、覆盖率、阻断问题和未验证项
- **AND** 完整报告需要长期保留时保存到 `reviews/spec-review.md`
- **AND** 不得为保存报告扩大 `spec_reviewer` 的写入权限

#### Scenario: 未执行体验走查

- **WHEN** change 不包含可运行页面或本轮未获得体验走查条件
- **THEN** `evidence.md` 必须将体验走查标记为不适用、`BLOCKED` 或 `NOT_RUN`
- **AND** 必须说明原因，不得创建虚假的体验报告或截图

### Requirement: 归档结论检查证据完整性和时效

主 Agent MUST 在归档前检查 evidence 中所有 `FAIL`、`BLOCKED`、`NOT_RUN`、Spec 偏差、体验问题和残余风险。审查或最终验证后又修改了受影响的生产代码、测试或规格时，旧结论 MUST 标记为已失效，并重新执行受影响验证或明确说明不需要重跑的依据。

#### Scenario: 审查后实现再次变化

- **WHEN** Spec Review、QA 或体验走查完成后又修改其覆盖范围内的实现、测试或规格
- **THEN** 原证据必须标记为已失效或被后续记录取代
- **AND** 主 Agent 必须重新运行受影响验证或记录不重跑的具体依据

#### Scenario: 存在未关闭的阻断问题

- **WHEN** 归档前证据仍包含未解决的 `FAIL`、阻断级 Spec 偏差或 P0/P1 体验问题
- **THEN** 最终交付结论不得建议归档
- **AND** 必须列出责任角色、修复项和重新验证范围

### Requirement: 验证采集器只执行受控验证配置
项目 SHALL 提供确定性验证采集器，根据明确选择的根、前端、后端或跨栈 profile 运行项目登记的验证命令并记录开始时间、结束时间、仓库、完整命令、退出码和状态。采集器 MUST NOT 接受任意 Shell 字符串作为隐式执行入口，也不得执行 build、外部写入、Git 写操作或未登记命令。

#### Scenario: 运行前端验证 profile
- **WHEN** 主 Agent 为一个前端 change 选择前端基础验证 profile
- **THEN** 采集器只运行 profile 登记的 lint、typecheck 和测试命令
- **AND** 每条命令的实际退出码分别记录，不因后续命令通过而覆盖前序失败

#### Scenario: 请求未登记命令
- **WHEN** 调用者要求采集器执行不在批准 profile 中的命令或包含 Shell 控制操作符的参数
- **THEN** 采集器拒绝执行并返回失败状态
- **AND** 不创建虚假的验证成功记录

### Requirement: 机器验证清单与人工交付结论分离
采集器 SHALL 生成不含完整原始日志和敏感信息的机器验证清单，保存命令、状态、关键安全摘要、仓库 HEAD 和输入指纹。`evidence.md` MUST 继续作为人工可读交付结论，由主 Agent复核后引用或汇总机器清单；采集器不得自行填写 QA、Spec Review、体验结论或归档建议。

#### Scenario: 验证命令全部通过
- **WHEN** 批准 profile 中所有命令实际退出码为零
- **THEN** 机器清单逐项记录 `PASS` 和对应退出码
- **AND** `evidence.md` 仍需由主 Agent 根据实际范围填写未验证项、审查和最终结论

#### Scenario: 输出包含疑似敏感信息
- **WHEN** 验证输出包含 token、Cookie、凭据或隐私数据模式
- **THEN** 机器清单不得保存原始敏感内容
- **AND** 只记录已脱敏摘要、阻塞说明或安全错误类别

### Requirement: 验证后输入变化会使机器证据失效
机器验证清单 MUST 记录与验证范围相关的 change artifacts、仓库 HEAD、工作树差异或显式输入文件指纹。归档前的时效检查发现这些输入在验证后变化时 MUST 将对应结果判为失效，并列出需要重新运行的 profile；不得继续沿用旧 `PASS`。

#### Scenario: Spec Review 后修改实现
- **WHEN** 机器清单生成后相关生产代码、测试或规格发生变化
- **THEN** 时效检查报告旧结果失效及受影响仓库
- **AND** 主 Agent重新运行相关验证或在 evidence 中记录不重跑的具体依据

#### Scenario: 只修改无关文档
- **WHEN** 验证后仅修改明确不在清单输入范围内的无关文档
- **THEN** 时效检查不应将应用测试结果自动判为失效
- **AND** 文档自身仍执行对应文档或治理验证
