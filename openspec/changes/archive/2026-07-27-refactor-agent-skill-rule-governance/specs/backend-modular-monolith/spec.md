## MODIFIED Requirements

### Requirement: 后端治理依赖完整 AIWorkSpace
后端仓库 SHALL 包含薄 `AGENTS.md` 和中文架构文档，但 MUST NOT 包含局部 `.codex`；受治理的 Java、Spring Boot 或数据库任务必须从完整 AIWorkSpace 读取根 `.codex/rules` 与 `.codex/skills`。

#### Scenario: AI 代理从后端仓库开始局部任务
- **WHEN** AI 代理在完整 AIWorkSpace 中进入 `backend/` 处理 Java、Spring Boot 或数据库任务
- **THEN** 可以从后端 `AGENTS.md` 定位根 conventions、Skills 和验证命令
- **AND** 可以从后端 README 定位完整中文架构文档

#### Scenario: 独立检出时请求修改 HTTP 契约
- **WHEN** 后端独立检出缺少主仓库 `.codex`、OpenSpec 或跨栈接口规范
- **THEN** 代理必须停止受治理的实现或评审并要求回到完整 AIWorkSpace
- **AND** 不得复制或推测根级 Rules、Skills 与契约

#### Scenario: 根级与局部规则同时生效
- **WHEN** AI 代理从主仓库处理后端 submodule 任务
- **THEN** 根级跨仓库 Rules 与根 `backend-conventions.md`、`database-conventions.md` 共同生效
- **AND** 技术 conventions 不降低根级安全、OpenSpec、Git 或验证要求
