# Rule 控制矩阵

本表只登记控制责任，不复制 Rule 正文。`CRITICAL` 表示违反后必须停止当前阶段。

| Rule ID | 作用域 | 风险 | 主要责任 | 控制类型 | 执行入口 | 阻断条件 | 证据位置 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RULE-WF-001 | 三仓库 | CRITICAL | 主 Agent | USER_CONFIRMATION | OpenSpec 当前版本确认 | 规格未确认即准备实现 | 用户消息与 change artifacts |
| RULE-WF-003 | 三仓库 | CRITICAL | 主 Agent | MAIN_AGENT | 归档前复核 | tasks、验证或 specs 同步不完整 | evidence.md |
| RULE-WF-004 | 重要 change | CRITICAL | 主 Agent | SCRIPT | check-agent-governance.sh | 适用 change 缺少 evidence | change evidence.md |
| RULE-WF-005 | 单人全栈 | CRITICAL | 主 Agent | MAIN_AGENT | chinamate-fullstack-delivery | 未推导阶段即跨阶段执行 | OpenSpec、Git 与 evidence 恢复摘要 |
| RULE-QA-003 | 三仓库 | CRITICAL | QA | REVIEW | 完成声明检查 | 没有本轮新验证输出 | evidence.md 自动化验证表 |
| RULE-QA-004 | 三仓库 | CRITICAL | QA | SCRIPT | collect_verification.py | 命令状态或摘要不可追溯 | reviews/verification-manifest.json |
| RULE-REPO-003 | 三仓库 | CRITICAL | 主 Agent | SCRIPT | check-harness.sh | gitlink 指向不可复现状态 | submodule 与远端检查摘要 |
| RULE-GIT-001 | 三仓库 | CRITICAL | 用户 | USER_CONFIRMATION | Git 写操作前 | 缺少当前范围明确授权 | 当前用户消息 |
| RULE-DOC-003 | 主仓库 | CRITICAL | 主 Agent | REVIEW | evidence 复核 | 证据含敏感或完整原始日志 | evidence.md 与 reviews |
| RULE-FE-007 | frontend | CRITICAL | 前端职责视角 | TEST | frontend-static profile | 客户端读取非公开配置 | 前端测试结果 |
| RULE-BE-006 | backend | CRITICAL | 后端职责视角 | REVIEW | 后端安全审查 | 配置、日志或异常泄露敏感信息 | 后端测试与 Spec Review |
| RULE-DB-002 | backend | CRITICAL | 后端职责视角 | REVIEW | 数据库变更审查 | schema 变化不来自 Flyway | migration 与 Spec Review |
| RULE-DB-009 | backend | CRITICAL | 后端职责视角 | REVIEW | 工程实践责任链 | 无依据直接使用 Spring JDBC 或绕过 MyBatis-Plus 默认路径 | 后端完成报告、QA 与 Spec Review |

控制类型只允许 `SCRIPT`、`TEST`、`REVIEW`、`MAIN_AGENT`、`USER_CONFIRMATION`。脚本只校验稳定字段和引用，不解释 Rule 自然语言。
