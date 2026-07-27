## ADDED Requirements

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
