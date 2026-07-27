## ADDED Requirements

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

## MODIFIED Requirements

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
