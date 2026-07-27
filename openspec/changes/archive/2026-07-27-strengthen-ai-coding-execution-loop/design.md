## Context

ChinaMate 是一个由同一名开发者配合 AI 完成产品、交互、前端、后端、测试与验收的全栈项目。当前已经具备七个按交付物切分的 custom agents、40 条稳定 Rule、OpenSpec 六类 Skills、前后端技术 Skills、Harness、架构测试、Playwright 和重要 change 的 `evidence.md`，但使用者仍需在这些入口之间手工判断阶段、角色和验证命令。

文章《AI代码生成率94%：我们用一个 Skill 跑通需求开发全流程》的可复用价值是把需求开发显式建模、让判断与确定性脚本分工、设置人机硬关卡并以落盘证据实现跨会话接力。ChinaMate 不应照搬其 iOS、TAPD、Figma 或逐文件 wiki 结构，而应以现有 OpenSpec 和集中治理为事实源建立适合单人开发的薄编排层。

当前还存在一处已证实的治理漂移：`.codex/rules/repository-boundaries.md` 声称技术 Rules 与 Skills 跟随 submodule，但已确认规格、Manifest、根入口和实际目录要求统一由根 `.codex/` 拥有。本 change 必须先消除该冲突。

## Goals / Non-Goals

**Goals:**

- 让单人开发者从一个 Skill 入口完成阶段识别、最短路径选择、角色视角切换、验证与恢复。
- 用控制矩阵把 Critical Rule 的责任和门禁显式化。
- 用固定 profile 的脚本采集真实验证结果和输入指纹。
- 建立当前规模足够使用的跨栈地图、术语桥和需求来源追溯。
- 对编排资源、知识引用和证据时效执行轻量漂移检查。

**Non-Goals:**

- 不建立第二套任务状态、确认状态或 `TECH_SPEC.md`。
- 不让自动化脚本替代用户确认、QA、Spec Review 或体验判断。
- 不自动 commit、push、更新 gitlink、归档或调用外部服务。
- 不把全部 Rules 转为可执行代码，不建立逐文件 wiki。
- 不修改业务页面、API、数据库或运行时行为。

## Decisions

### 1. 采用一个薄编排 Skill，不建立“超级 Agent”

新增 `.codex/skills/chinamate-fullstack-delivery/`，只负责选择路径、加载已有 Rules/Skills、设置阶段退出条件和组织交接。它不复制七角色合同，也不替代主 Agent。Skill 结构计划为：

```text
.codex/skills/chinamate-fullstack-delivery/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── stage-routing.md
│   ├── control-matrix.md
│   ├── knowledge-routing.md
│   └── verification-profiles.md
└── scripts/
    ├── collect_verification.py
    └── check_verification_freshness.py
```

`SKILL.md` 保持在 500 行以内，只保存核心流程和按需加载说明；详细阶段、矩阵和格式放在一级 references。创建时使用 Skill Creator 的 `init_skill.py`，并生成与 `SKILL.md` 一致的 `agents/openai.yaml`。

备选方案是新增第八个“全栈 Agent”。不采用，因为单人模式需要的是主 Agent 的流程编排，不是另一个拥有模糊写入边界的执行角色。

### 2. 角色是串行职责视角，而不是并行虚拟团队

默认阶段为：

```text
收口需求 → OpenSpec 合同 → 交互/跨栈契约 → 实现 → QA → Spec Review → Experience Review → evidence/归档建议
```

每个任务根据风险选择短路径。例如纯后端修复可以省略交互和体验，纯 UI change 可以省略数据库，纯文档可以豁免 evidence。Skill 每次切换视角时输出上游输入、当前交付物、退出条件和下一交接，不要求真的生成七个并行会话。

备选方案是固定跑完整七角色流水线。不采用，因为会增加单人开发的上下文切换和形式成本，也违反“选择最少必要角色”的现有规格。

### 3. 阶段状态从 OpenSpec、Git 和 evidence 推导

不新增 `state.json` 或 `subtasks.json`。恢复时读取：

1. `openspec status` 和 artifacts；
2. tasks checkbox，但不把 checkbox 当验证证据；
3. 根、frontend、backend Git 状态与 submodule SHA；
4. evidence 中的 PASS/FAIL/BLOCKED/NOT_RUN、审查和残余风险；
5. 当前规格和实现差异。

备选方案是维护独立状态文件。拒绝该方案，因为它会与 OpenSpec tasks 和 evidence 形成三方漂移。

### 4. Rule 控制矩阵采用 Markdown 表格和稳定字段

控制矩阵作为 Skill reference 保存，每行至少包含：

```text
Rule ID | 作用域 | 风险 | 主要责任 | 控制类型 | 执行入口 | 阻断条件 | 证据位置
```

控制类型限定为 `SCRIPT`、`TEST`、`REVIEW`、`MAIN_AGENT`、`USER_CONFIRMATION`。治理脚本只验证 ID、枚举、引用和 Critical 覆盖，不解释 Rule 自然语言。

备选方案是新增红线 YAML。拒绝该方案，因为现有 Markdown Rules 已是单一规范源，YAML 会形成重复规则正文。

### 5. 验证采集使用固定 profile 和机器清单

采集器使用 Python 标准库实现，profile 在 `verification-profiles.md` 和脚本登记表中一一对应。首批 profile：

- `root-governance`：治理检查、Harness、OpenSpec strict validate、`git diff --check`。
- `frontend-static`：lint、typecheck、Vitest。
- `frontend-e2e`：Playwright，必须显式选择。
- `backend-architecture`：架构规则测试。
- `backend-test`：后端完整测试，必须按风险选择。
- `fullstack-governance`：组合根级与受影响仓库的非 build 门禁。

脚本不接受任意 Shell 字符串；命令用参数数组执行，不通过 shell。结果写入 change 的 `reviews/verification-manifest.json`，只包含命令、时间、退出码、状态、裁剪摘要、repo HEAD、dirty diff hash、相关 artifacts hash和工具版本，不保存完整日志。主 Agent把必要摘要写入 `evidence.md`。

如果 profile 中间失败，采集器继续或停止由 profile 明确声明，但不得覆盖已经记录的失败。任何 Git 写操作、build、外部写入和未登记命令均拒绝。

### 6. 使用输入指纹判断证据时效

机器清单对以下输入计算 SHA-256：

- change 的 proposal、specs、design、tasks；
- profile 声明的相关源码、测试和配置文件内容或 Git diff；
- 根与相关 submodule HEAD。

时效检查使用相同 scope 重新计算。相关输入变化则输出 `STALE` 和需重跑 profile；无关文档不触发应用 profile 失效。`evidence.md` 记录机器清单路径和最后时效检查结论。

该设计不试图证明功能正确，只证明“当前 PASS 对应的输入是否仍然相同”。

### 7. 跨栈知识保持两份人类文档

新增：

- `docs/architecture/system-map.md`：产品模块 → 前端 → API → 后端 → 数据 → 测试。
- `docs/standards/domain-glossary.md`：产品术语、工程含义、容易混淆项和权威来源。

当前已实现路径必须真实存在；未来能力统一标记 `PLANNED`。治理脚本验证 `CURRENT` 路径，忽略 `PLANNED` 的不存在路径。业务 change 在 proposal/spec/design 中引用 PRD ID、设计节点、用户原话或已有 Spec，不额外创建重复的需求数据库。

### 8. P2 只做轻量漂移检查和升级触发器

扩展 `check-agent-governance.sh` 或新增其调用的专用校验脚本，检查：

- 编排 Skill 结构与锁定哈希；
- 控制矩阵 Rule ID 和路径；
- 系统地图 `CURRENT` 路径；
- 根集中治理声明一致性；
- verification manifest schema 与时效状态。

只有满足任一条件才提出后续重型知识库 change：单模块真实文件超过 50 个、同一定位问题重复三次、两次地图漂移事故、或出现三个以上需要专用收料的外部需求源。

### 9. 先修正规范源冲突

把 `.codex/rules/repository-boundaries.md` 修正为应用文件由 submodule 拥有，但 Agents、Rules、Skills 由完整 AIWorkSpace 根 `.codex/` 统一拥有。治理脚本增加稳定字段或路径检查，避免再次出现相反描述。

### 10. 对临时 worktree 执行只读环境预检

新增 `scripts/check_delivery_environment.py`，在安装依赖、启动服务或运行完整后端测试前只读检查：

- frontend `node_modules` 若为指向当前 worktree 外部的软链接，报告 `BLOCKED`，建议在当前 worktree 使用 pnpm store 执行 `pnpm install --offline`；不得把 Turbopack filesystem-root panic 归因于业务代码。
- Java 版本为 21 或更高、后端测试使用 Mockito 且 Maven 配置没有显式 agent 时，报告 `REVIEW_REQUIRED`；先运行最小 Mockito 测试确认环境，失败时记录基础设施阻塞或采用项目级 surefire agent 配置，不静默跳过测试。
- 预检只输出结构化结论，不安装依赖、不修改 POM、不启动服务，也不扩大沙箱或网络授权。

### 11. 真实场景必须覆盖边界两侧

验证 profiles 继续只执行固定命令；涉及分页、阈值、排序、重试或幂等边界时，`verification-profiles.md` 额外要求 change-local fixture 覆盖边界两侧。分页至少准备 `pageSize + 1` 条记录，并证明第一页数量、下一页数量、`hasNext` 和稳定 tie-breaker。单条 CRUD smoke test 只能证明基本连通，不能把分页标记为 `PASS`。

### 12. 零残留清理由声明式 manifest 复核

新增 `scripts/check_delivery_cleanup.py`，读取 change-local `reviews/cleanup-manifest.json`，仅支持固定资源类型：临时路径、Git 分支、Git worktree、TCP 端口和 MySQL 专用数据库。脚本只做只读检查，校验 repo/path/database/port 范围并拒绝任意 Shell；凭据只能从环境变量传递，manifest 和输出不得保存密码。

cleanup manifest 记录目标资源和期望终态，不授予删除权限。主 Agent仍须在用户明确授权后执行停止、删除和移除动作，再运行 checker；全部资源达到 `ABSENT`/`CLOSED` 才可声明零残留。临时演练若要求不保留文档，先采集结论到聊天，再删除 manifest 和 change 文件。

## Risks / Trade-offs

- [风险] 单人编排 Skill 变成重复 Rules 的长文档 → [缓解] SKILL.md 只路由稳定 ID 和 references，不复制 Rule 正文，并限制 500 行。
- [风险] 固定 profile 不能覆盖所有针对性测试 → [缓解] profile 只覆盖公共门禁，业务定向测试仍由 tasks 和 QA 明确执行并写入 evidence。
- [风险] 机器清单被误认为完整验收 → [缓解] manifest 不包含最终结论，evidence 仍要求 QA、Spec Review、体验和残余风险判断。
- [风险] 输入指纹 scope 过宽导致频繁失效 → [缓解] profile 显式声明受影响文件组，无关文档不参与应用指纹。
- [风险] 知识地图过早膨胀 → [缓解] 只维护模块级关系和真实路径，以量化触发条件决定是否升级。
- [风险] 新增 first-party Skill 与第三方锁定结构不兼容 → [缓解] 在实现前先用测试定义 Manifest/lock schema，再扩展校验器，不手改第三方 Skill 内容。

## Migration Plan

1. 先补治理测试，暴露集中归属冲突和新 Skill/矩阵缺失。
2. 修正规范源冲突并建立控制矩阵、系统地图和术语桥。
3. 使用 Skill Creator 初始化项目 Skill，补 references、scripts 和 UI metadata。
4. 以失败测试驱动验证采集器、清单 schema 和时效检查。
5. 扩展 Manifest、skills lock、治理脚本、Harness 和 README 路由。
6. 使用当前 change 自举运行新编排和验证 profile，把真实结果写入 `evidence.md`。
7. 执行 Spec Review；本 change 不含可运行产品体验变化，Experience Review 标记不适用并说明。
8. 使用已完成的 TodoList 隔离演练反馈补充环境预检、分页边界与 cleanup checker 的 RED/GREEN 测试，重新生成 Skill lock、机器 manifest、evidence 和 Spec Review。

回滚时可以移除新 Skill、控制矩阵、知识入口和采集器，并恢复 Manifest/lock/Harness 路由；不得回退其他已确认治理能力。规范源冲突修正应保留，因为它本身是对当前已确认规格的纠偏。

## Open Questions

- 用户是否确认本次将 P0、P1 最小版本和 P2 轻量检查作为同一个治理 change 实现。
- verification manifest 是否固定存放在 `reviews/verification-manifest.json`，还是按多轮验证保留带时间戳的历史文件；建议 MVP 固定一个当前文件，旧结果失效时由 Git 历史追踪，避免目录膨胀。
- `backend-test` 是否默认包含在跨栈 profile；建议由风险显式选择，不让根级治理变更运行无关完整后端测试。
