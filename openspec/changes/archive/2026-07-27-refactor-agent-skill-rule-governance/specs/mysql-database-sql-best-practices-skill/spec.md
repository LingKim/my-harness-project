## MODIFIED Requirements

### Requirement: 项目提供可追踪的 MySQL 最佳实践 Skill

主仓库根 `.codex/skills/` MUST 提供 `planetscale/database-skills@mysql` 的完整入口与参考文件，并 MUST 通过根 `.codex/skills-lock.json` 记录来源、Skill 路径和内容哈希；该 Skill MUST 出现在根批准清单中，后端子仓库不得维护第二份规范副本。

#### Scenario: 完整检出项目

- **WHEN** 开发者或 AI 代理递归检出完整 AIWorkSpace
- **THEN** 无需依赖用户级全局安装即可从根目录读取 `mysql` 入口和相关参考文件
- **AND** 根统一锁文件包含来源、正确 Skill 路径和有效内容哈希

#### Scenario: 安装命令附带无关 Skill

- **WHEN** 根 `.codex/skills` 或统一锁文件出现未经过独立 change 批准的其他应用 Skill
- **THEN** 后端局部检查或根 Harness 必须失败并指出未批准的 Skill 名称

### Requirement: 数据库和 SQL 任务强制触发 MySQL Skill

后端 `AGENTS.md` MUST 规定：涉及 MySQL 配置、Flyway migration、MyBatis XML 或注解 SQL、表结构、字段类型、约束、索引、查询、事务锁、连接或数据库运维的编写、评审和重构任务必须先读取 `../.codex/rules/database-conventions.md`，再完整读取 `../.codex/skills/mysql/SKILL.md` 和任务直接相关的参考文件。

#### Scenario: AI 开始数据库相关任务

- **WHEN** AI 代理准备编写、评审或重构上述数据库与 SQL 范围内的内容
- **THEN** 代理必须加载 `database-conventions.md`、`mysql` Skill 及任务直接相关的参考文件
- **AND** 只应用不与当前项目事实冲突的建议

#### Scenario: 非数据库任务

- **WHEN** 任务不涉及 MySQL、schema、migration、SQL、事务锁或数据库运维
- **THEN** 数据库 Rule 与 `mysql` Skill 不因本规则被强制加载

### Requirement: MySQL 8.4 与项目数据库架构优先

根 `.codex/rules/database-conventions.md` MUST 使用统一事实优先级：已确认 OpenSpec；当前 schema、SQL、依赖、migration、测试与安全环境执行证据；项目 Rule；MySQL 8.4 官方文档；通用 Skill 建议。项目 MUST 继续使用 Docker Compose MySQL 8.4、InnoDB、MyBatis-Plus 与 Flyway-only 架构。

#### Scenario: Skill 推荐 PlanetScale 托管

- **WHEN** Skill 推荐 PlanetScale、Vitess 或其他不同于当前项目的托管架构
- **THEN** 代理必须保留当前 Docker Compose MySQL 8.4 架构
- **AND** 不得仅因 Skill 建议改变数据库托管方式

#### Scenario: Skill 给出绝对化数据库规则

- **WHEN** Skill 对主键类型、collation、时间类型、分区阈值或在线 DDL 算法给出通用默认值
- **THEN** 代理必须根据业务语义、MySQL 8.4 官方行为、真实数据量和变更风险进行验证
- **AND** 不得把通用默认值无条件固化为项目规则

### Requirement: Harness 校验 MySQL Skill 接入

后端局部检查与主仓库 Harness MUST 自动校验后端入口、`database-conventions.md`、MySQL Skill 批准清单项、入口、代表性参考文件、锁记录来源、Skill 路径、哈希以及 Flyway-only、MyBatis 参数安全、MySQL 8.4 优先级和破坏性操作审批 Rule；校验 MUST NOT 要求这些规则正文位于根 `AGENTS.md`。

#### Scenario: MySQL Skill 接入完整

- **WHEN** 执行后端局部治理检查或 `./scripts/check-harness.sh`
- **THEN** 后端入口、database conventions、MySQL Skill、锁记录和路由检查全部通过

#### Scenario: 参数安全或 Flyway 规则被移除

- **WHEN** Skill 文件仍存在但 `database-conventions.md` 不再保留参数绑定或 Flyway-only Rule
- **THEN** 检查必须失败并指出缺失的数据库安全约束
