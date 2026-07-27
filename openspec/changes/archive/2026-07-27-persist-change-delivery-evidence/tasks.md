## 1. 建立证据治理失败门禁

- [x] 1.1 扩展 `scripts/validate-custom-agents.py` 与 `scripts/test-custom-agents.py`，要求 QA、Spec Reviewer 和 Experience Reviewer 合同包含交付证据的返回或持久化交接责任，并增加删除相关合同内容时能够准确失败的夹具。
- [x] 1.2 扩展 `scripts/check-agent-governance.sh`，要求 `docs/templates/openspec-change-evidence.md` 和根入口中的证据路由存在；在模板与路由尚未建立时运行检查，确认因预期缺失项失败。

## 2. 建立 Markdown 证据模板与长期规则

- [x] 2.1 创建 `docs/templates/openspec-change-evidence.md`，包含基本信息、自动化验证、真实场景、QA、Spec Review、Experience Review、未验证项与风险、最终交付结论，并提供 `PASS`、`FAIL`、`BLOCKED`、`NOT_RUN` 示例。
- [x] 2.2 更新 `.codex/rules/workflow.md`、`.codex/rules/quality-gates.md` 和 `.codex/rules/documentation.md`，使用稳定 Rule ID 明确适用 change、真实证据最小字段、敏感信息边界、审查后变更的失效处理和归档门禁。
- [x] 2.3 更新 `AGENTS.md`、`.codex/agents/README.md`、`.codex/agents/qa_engineer.toml`、`.codex/agents/spec_reviewer.toml` 与 `.codex/agents/experience_reviewer.toml`，明确主 Agent 汇总、角色返回结构化结果、只读 Reviewer 不扩大写权限及长报告的可选路径。
- [x] 2.4 更新 `README.md` 与 `docs/plans/README.md` 的最小导航，说明 `evidence.md` 是重要 change 的交付证据入口，并明确纯文案与只读探索的豁免边界。

## 3. 试运行与验证

- [x] 3.1 运行 `python3 scripts/test-custom-agents.py`、`./scripts/check-agent-governance.sh` 与 `./scripts/check-harness.sh`，确认正式配置和新增失败夹具均通过。
- [x] 3.2 在本 change 根目录按模板创建 `evidence.md`，只记录本轮实际执行的治理检查、OpenSpec strict validate、`git diff --check`、未运行项与残余风险，不补写不存在的历史输出。
- [x] 3.3 完成只读 Spec 合规审查，由主 Agent 将完整报告保存到 `reviews/spec-review.md` 并在 `evidence.md` 中记录结论；本 change 不含可运行页面，将 Experience Review 明确标记为不适用。
- [x] 3.4 运行 `bash -n scripts/check-agent-governance.sh`、`bash -n scripts/check-harness.sh`、`openspec validate --all --strict` 和 `git diff --check`，复核只修改根治理、模板与本 change artifacts，且不运行无关前后端 build。
