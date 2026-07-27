## 1. 先用测试固定治理与工具合同

- [x] 1.1 在 `scripts/test-ai-delivery-governance.py` 中为集中治理归属、Skill 必需结构、控制矩阵字段与 Rule ID、系统地图 `CURRENT/PLANNED` 路径语义编写失败测试，并在实现前运行确认测试以正确原因失败。
- [x] 1.2 在 `scripts/test-verification-collector.py` 中为固定 profile、参数数组执行、逐命令退出码、失败保留、任意命令拒绝、敏感摘要脱敏、manifest schema、输入指纹与 `STALE` 检测编写失败测试，并在实现前记录 RED 结果。

## 2. 修正规范源并建立 Rule 控制矩阵

- [x] 2.1 修正 `.codex/rules/repository-boundaries.md` 的治理归属冲突，明确应用代码由 submodule 拥有、Agents/Rules/Skills 由完整 AIWorkSpace 根 `.codex/` 集中拥有，并保持既有 Git/submodule 交付边界不变。
- [x] 2.2 在 `.codex/skills/chinamate-fullstack-delivery/references/control-matrix.md` 定义 Rule 控制矩阵，覆盖本次选定的 Critical Rules，并为每条记录风险、主要责任、控制类型、入口、阻断条件与证据位置；运行 1.1 的矩阵测试使其通过。

## 3. 创建单人全栈编排 Skill

- [x] 3.1 使用 Skill Creator 的 `init_skill.py` 在 `.codex/skills/` 初始化 `chinamate-fullstack-delivery`，生成 `SKILL.md` 与 `agents/openai.yaml`，只创建确实需要的 `references/` 和 `scripts/` 资源目录。
- [x] 3.2 编写 `.codex/skills/chinamate-fullstack-delivery/SKILL.md` 与 `references/stage-routing.md`，实现任务分类、最短路径、阶段推导、串行角色视角、硬关卡、跨会话恢复和失败/阻塞回退，不复制现有 Rule 或 Agent 正文。
- [x] 3.3 编写 `references/knowledge-routing.md` 与 `references/verification-profiles.md`，说明何时读取跨栈地图和术语桥、各验证 profile 的固定命令、适用风险与非目标；校验 Skill metadata 和 `agents/openai.yaml` 一致。
- [x] 3.4 更新 `.codex/manifest.json` 与 `.codex/skills-lock.json` 登记 first-party Skill 的来源、路径与内容哈希，并为锁定信息增加测试，确保第三方 Skill 内容不被修改。

## 4. 建立 P1 最小跨栈知识与来源追溯

- [x] 4.1 新建 `docs/architecture/system-map.md`，以当前真实 M02 前端底座和后端模块地图建立“产品模块 → 前端 → API → 后端 → 数据 → 测试”基线，未实现项统一标记为 `PLANNED`，不创建虚假路径。
- [x] 4.2 新建 `docs/standards/domain-glossary.md`，记录账号、旅行上下文、攻略、AI 会话、知识引用、社区解决状态和高风险升级等首批领域词的工程含义、易混淆项与权威来源。
- [x] 4.3 在编排 Skill 和 OpenSpec artifact 指引中增加需求来源追溯格式，要求重要触发点、拦截、权限和失败行为引用 PRD ID、设计节点、用户原话或已有 Spec，并把无依据的语义扩张留为待确认或非目标。
- [x] 4.4 运行 1.1 的地图与引用测试，确认 `CURRENT` 路径真实存在、`PLANNED` 路径不会被误判为缺失。

## 5. 实现 P0 验证采集和 P2 轻量时效检查

- [x] 5.1 在 `.codex/skills/chinamate-fullstack-delivery/scripts/collect_verification.py` 实现固定 profile 验证采集，使用参数数组而非 shell 执行，逐项保留命令、时间、退出码、状态、脱敏摘要、repo HEAD 与输入指纹，并拒绝 build、Git 写操作、外部写入和未登记命令。
- [x] 5.2 在 `.codex/skills/chinamate-fullstack-delivery/scripts/check_verification_freshness.py` 实现 manifest schema 与输入指纹复核；相关 change artifacts、源码、测试、配置或仓库 HEAD 变化时报告 `STALE` 和需重跑 profile，无关文档不使应用验证自动失效。
- [x] 5.3 使 `scripts/test-verification-collector.py` 全部通过，并验证成功、失败、拒绝、脱敏和失效结果均来自实际 fixture 命令或文件变化，不根据计划生成 `PASS`。
- [x] 5.4 更新 `docs/templates/openspec-change-evidence.md`，增加机器 manifest 相对路径与时效结论字段，保持 QA、Spec Review、体验和归档建议由主 Agent人工复核，不保存完整日志或敏感内容。

## 6. 接入治理、Harness 与文档导航

- [x] 6.1 扩展 `scripts/check-agent-governance.sh` 调用新的治理测试，校验集中归属、Skill/metadata/lock、控制矩阵、跨栈地图、术语桥和引用有效性；不得通过匹配完整中文句子解释 Rule 语义。
- [x] 6.2 更新 `scripts/check-harness.sh`、根 `AGENTS.md`、`.codex/agents/README.md`、`.codex/rules/README.md` 和相关角色路由，使业务和跨栈任务优先发现单人全栈编排 Skill，同时保留“最少必要角色”和子仓库边界。
- [x] 6.3 更新 `README.md`、`docs/plans/README.md` 与必要架构导航，说明单人全栈入口、控制矩阵、系统地图、术语桥、验证 profile、manifest 与重型知识库升级触发条件，明确当前不自动 commit、push 或归档。

## 7. 自举验证、证据与审查

- [x] 7.1 使用新 Skill 对本 change 执行一次跨会话恢复与阶段路由演练，确认能够从 OpenSpec、Git 和 evidence 推导状态且不会创建第二套状态文件。
- [x] 7.2 使用 `root-governance` profile 生成 `reviews/verification-manifest.json`，实际运行 `./scripts/check-agent-governance.sh`、`./scripts/check-harness.sh`、OpenSpec strict validate 和 `git diff --check`，再运行 freshness 检查并把真实摘要写入 change 根 `evidence.md`。
- [x] 7.3 运行 `scripts/test-custom-agents.py`、`scripts/test-ai-delivery-governance.py` 和 `scripts/test-verification-collector.py`，记录测试数量、状态、失败或未运行项；本治理 change 不运行无关前端、后端 build 或完整业务测试。
- [x] 7.4 由只读 `spec_reviewer` 对 proposal、design、tasks、三个 delta specs、实现 diff、测试与 manifest 执行双向逐条对账；主 Agent将完整报告保存到 `reviews/spec-review.md` 并更新 `evidence.md`。
- [x] 7.5 在 `evidence.md` 将 Experience Review 标记为不适用并说明本 change 不改变可运行产品体验；复核全部 `FAIL`、`BLOCKED`、`NOT_RUN`、残余风险和证据时效后，才建议同步与归档。
- [x] 7.6 确认本 change 未修改 `frontend/` 或 `backend/`；若实现揭示必须修改子仓库，先更新 proposal/design/tasks，分别执行子仓库状态检查、测试、授权后交付和主仓库 gitlink 更新，不在本任务中隐式扩展范围。

## 8. 吸收真实 TodoList 演练反馈

- [x] 8.1 在 `scripts/test-delivery-safety.py` 先编写失败测试，覆盖 frontend 外部 `node_modules` 软链接、Java 21+/Mockito 风险、分页 `pageSize + 1` 证据要求、cleanup manifest 安全校验与资源终态。
- [x] 8.2 在 Skill `scripts/` 实现只读 `check_delivery_environment.py` 和 `check_delivery_cleanup.py`，拒绝任意 Shell、越界路径、非回环主机、非法数据库名和明文凭据，不自动安装、启动或删除资源。
- [x] 8.3 更新 `SKILL.md`、`stage-routing.md` 与 `verification-profiles.md`，在 worktree 启动、后端测试、真实分页和清理硬关卡中路由新增脚本与代表性 fixture。
- [x] 8.4 更新治理测试、Skill lock 和必要导航，运行 Skill Creator `quick_validate.py`、专项测试、治理、Harness、OpenSpec strict validate 与 `git diff --check`。
- [x] 8.5 将既有 machine manifest 标记失效并重新生成，更新 `evidence.md` 与 Spec Review，确认四项演练反馈均有 Spec→实现和实现→Spec 证据且无未解决 P0/P1。
