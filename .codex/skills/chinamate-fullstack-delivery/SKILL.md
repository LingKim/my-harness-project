---
name: chinamate-fullstack-delivery
description: 编排 ChinaMate 单人全栈 AI Coding 交付。用于同一名开发者需要从产品需求、交互与跨栈契约，推进到前端、后端、数据库、测试、Spec 合规审查、真实体验验收、交付证据和归档的业务功能、跨仓库 change、行为修复或跨会话续作；也用于判断当前阶段、选择最短安全路径、恢复未完成 change、运行受控验证 profile 或检查证据是否失效。
---

# ChinaMate 单人全栈交付

把七个项目角色当作同一名开发者按阶段切换的职责视角。保持主 Agent 统一协调，默认串行，不为形式完整启动全部角色。

## 开始

1. 读取根 `AGENTS.md`、Agents/Rules 索引、`README.md`、`openspec/config.yaml`。
2. 运行 `openspec list --json`，确定活动 change；续作时读取该 change 的全部 apply context。
3. 检查根仓库和受影响 submodule 的 `git status --short --branch`，保护已有改动。
4. 使用临时 worktree、准备依赖或运行完整后端测试前，读取 [验证 Profiles](references/verification-profiles.md) 并运行只读环境预检；`BLOCKED` 不得记为业务失败，`REVIEW_REQUIRED` 必须先关闭风险。
5. 从 OpenSpec、Git、测试和 `evidence.md` 推导阶段，不把聊天记录或 task checkbox 当作完成证据。
6. 读取 [阶段路由](references/stage-routing.md)，选择最短安全路径并报告：当前阶段、已确认事实、阻塞、下一动作、所需职责视角和硬关卡。

## 核心纪律

- 非平凡行为必须先有完整 OpenSpec，当前版本规格经用户确认后才实现。
- 默认按产品/规格 → 交互与契约 → 实现 → QA → Spec Review → Experience Review → evidence/归档建议串行推进；不适用阶段明确跳过原因。
- 每次职责视角切换都交接上游输入、实际产物、验证结果、未完成项和下一动作。
- 需求来源必须引用 PRD ID、设计节点、用户原话或已有 Spec；没有依据的相似行为列为待确认或非目标，不擅自扩张。
- `FAIL`、阻断级 Spec 偏差或 P0/P1 体验问题未关闭时回到修复/验证阶段，不建议归档。
- 分页、阈值、稳定排序、重试或幂等场景必须用跨越边界两侧的 fixture；单条 CRUD smoke test 不得证明分页通过。
- 临时数据库、服务、worktree、分支或路径需要清理时，先声明 cleanup manifest；只有只读 checker 证明全部目标为 `ABSENT`/`CLOSED` 才声称零残留。
- commit、push、gitlink 更新、归档和破坏性操作始终遵守用户授权，不由本 Skill 自动执行。

## 按需加载

- 需要判断阶段、短路径、恢复或交接时，读取 [阶段路由](references/stage-routing.md)。
- 需要检查 Rule 责任、硬门禁或完成条件时，读取 [控制矩阵](references/control-matrix.md)。
- 涉及业务术语、跨栈定位、API/数据归属或需求追溯时，读取 [知识路由](references/knowledge-routing.md)、`docs/architecture/system-map.md` 和 `docs/standards/domain-glossary.md`。
- 需要运行验证或生成机器清单时，读取 [验证 Profiles](references/verification-profiles.md)，再运行 `scripts/collect_verification.py`。
- 需要检查 worktree 依赖或 Java/Mockito 环境时，运行 `scripts/check_delivery_environment.py`；需要复核清理终态时，运行 `scripts/check_delivery_cleanup.py`。
- 验证后代码、测试、规格或配置发生变化时，运行 `scripts/check_verification_freshness.py`，旧结果为 `STALE` 时重跑受影响 profile。

## 输出当前状态

使用以下最小格式，避免长篇重复规则：

```markdown
## 单人全栈交付状态
- Change：
- 当前阶段：
- 已确认事实：
- 当前失败/阻塞/未验证项：
- 本轮职责视角：
- 下一动作与退出条件：
- 需要用户确认：
```

完成前把真实验证与审查结果汇总到 change 的 `evidence.md`；机器 manifest 只是命令事实，不代替 QA、Spec Review、体验与最终结论。
