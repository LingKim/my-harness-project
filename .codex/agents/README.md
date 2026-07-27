# ChinaMate 项目级 Agents

本目录保存 Codex 可发现的项目级 custom agents。七个角色按交付物切分，主 Agent 应根据当前任务选择最少必要角色；只有契约已经确认且文件互不争用时，才并行委派写入任务。

| Agent | 何时使用 | 主要交付物 | 写入边界 |
| --- | --- | --- | --- |
| `product_manager` | 澄清需求、建立或更新 OpenSpec 合同 | proposal、specs、design、tasks、决策记录 | 根 `openspec/`、`docs/product/`、`docs/plans/` |
| `interaction_designer` | 把已确认规格转为页面流程和体验约束 | 流程、状态矩阵、响应式、i18n、a11y 说明 | 设计与规划文档 |
| `frontend_engineer` | 实现 Next.js/React 前端交付 | 前端代码、测试、验证报告 | `frontend/` |
| `backend_engineer` | 实现 Spring Boot/API/数据库交付 | 后端代码、migration、工程实践合规清单、验证报告 | `backend/` |
| `qa_engineer` | 从规格构建自动化验收并独立验证工程实践 | 测试矩阵、自动化测试、工程实践验证、缺陷报告 | 测试、夹具和测试配置 |
| `spec_reviewer` | 实现完成后检查 Spec 与项目 Rule 合规 | 双向对账、技术基线对账、精确覆盖率、修复 Action Items | 只读 |
| `experience_reviewer` | 可运行交付后的真实体验走查 | 分级问题、复现步骤、截图、建议 | 只读 |

## 使用原则

- 单人承担完整交付时，由主 Agent 使用 `../skills/chinamate-fullstack-delivery/SKILL.md` 串行切换角色视角并维护交接；角色不是必须并行启动的虚拟团队。
- 已确认 OpenSpec、当前源码与真实验证结果优先于角色示例和通用 Skill。
- Skills 与 Rules 只从根 `.codex/skills/` 和 `.codex/rules/` 加载，不在子仓库复制。
- 产品规格未经用户确认时，写入型开发角色不得开始实现。
- Agent 的 `sandbox_mode` 和正文授权不能扩大当前会话、用户授权或审批边界。
- 未经用户明确授权，不执行 commit、push、merge、分支删除或外部系统写入。
- 所有角色完成时必须报告实际文件、验证结果、未验证项、风险和下一交接建议。
- 后端或数据库交付按 `backend_engineer` 实现自检 → `qa_engineer` 独立验证 → `spec_reviewer` 只读对账串行交接；业务 Spec 未重复稳定 Rule 不代表可以跳过技术基线检查。
- 对需要持久化交付证据的 change，各角色返回结构化真实结果，主 Agent 使用 `docs/templates/openspec-change-evidence.md` 汇总到 change 根 `evidence.md`；只读 Reviewer 的长报告按需由主 Agent 保存到 `reviews/`。

结构校验入口：

```bash
./scripts/check-agent-governance.sh
```
