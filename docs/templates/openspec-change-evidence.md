# `<change-name>` 交付证据

> 本文件只记录实际发生的验证与审查。状态统一使用 `PASS`、`FAIL`、`BLOCKED`、`NOT_RUN`；不适用时写明原因，不得根据计划或 task checkbox 推测结果。

## 1. 基本信息

- Change：`<change-name>`
- 当前结论：`PASS / FAIL / BLOCKED`
- 最后更新：`YYYY-MM-DD HH:mm +08:00`
- 影响仓库：`root / frontend / backend`
- 机器验证清单：[`reviews/verification-manifest.json`](./reviews/verification-manifest.json) / `未生成`
- 机器清单时效：`FRESH / STALE / NOT_CHECKED / 不适用`
- 实现或检查范围：
  - `<path-or-component>`

## 2. 自动化验证

| 时间 | 仓库 | 执行角色 | 命令 | 状态 | 关键输出摘要 |
| --- | --- | --- | --- | --- | --- |
| `YYYY-MM-DD HH:mm` | `frontend` | `frontend_engineer` | `pnpm typecheck` | `PASS` | `exit 0` |
| `YYYY-MM-DD HH:mm` | `backend` | `qa_engineer` | `./mvnw test` | `FAIL` | `24 tests, 1 failure` |
| `YYYY-MM-DD HH:mm` | `root` | `main_agent` | `openspec validate --all --strict` | `BLOCKED` | `网络或环境阻塞说明` |
| `YYYY-MM-DD HH:mm` | `root` | `main_agent` | `<未执行命令>` | `NOT_RUN` | `未运行原因与影响` |

## 3. 手工或真实场景验证

| 场景 | 环境 | 操作 | 期望 | 实际 | 状态 | 证据 |
| --- | --- | --- | --- | --- | --- | --- |
| `<场景>` | `<环境>` | `<步骤>` | `<期望>` | `<实际>` | `PASS / FAIL / BLOCKED / NOT_RUN` | `<相对路径或观察摘要>` |

## 4. QA 结论

- 是否执行：`是 / 否 / 不适用`
- 验收范围：
- 通过项：
- 失败项：
- 未验证项：
- 已知缺陷：
- 残余风险：

## 5. Spec 合规审查

- 是否执行：`是 / 否 / 不适用`
- 完整报告：[`reviews/spec-review.md`](./reviews/spec-review.md) / `未单独保存`
- 正向覆盖率：
- 反向超纲项：
- 阻断问题：
- 最终结论：`PASS / PASS_WITH_ISSUES / FAIL / NOT_RUN`

## 6. 体验走查

- 是否执行：`是 / 否 / 不适用`
- 完整报告：[`reviews/experience-review.md`](./reviews/experience-review.md) / `未单独保存`
- 已检查页面或流程：
- P0/P1 问题：
- P2/P3 问题：
- 未验证设备或流程：
- 不适用或未运行原因：

## 7. 未验证项与残余风险

| 项目 | 状态 | 原因 | 影响 | 后续处理 |
| --- | --- | --- | --- | --- |
| `<未验证项>` | `BLOCKED / NOT_RUN` | `<原因>` | `<影响范围>` | `<责任角色和建议>` |

## 8. 最终交付结论

- tasks 是否全部完成：`是 / 否`
- 前端验证：`PASS / FAIL / BLOCKED / NOT_RUN / 不适用`
- 后端验证：`PASS / FAIL / BLOCKED / NOT_RUN / 不适用`
- Harness：`PASS / FAIL / BLOCKED / NOT_RUN`
- OpenSpec strict validate：`PASS / FAIL / BLOCKED / NOT_RUN`
- Spec Review：`PASS / PASS_WITH_ISSUES / FAIL / NOT_RUN`
- Experience Review：`PASS / PASS_WITH_ISSUES / FAIL / NOT_RUN / 不适用`
- 机器验证清单时效：`FRESH / STALE / NOT_CHECKED / 不适用`
- 是否建议归档：`是 / 否`
- 结论依据：

## 记录边界

- 只保存完整命令、关键输出摘要、测试数量、失败数量、可复现步骤和相对路径，不粘贴完整终端日志或缓存。
- `reviews/verification-manifest.json` 只保存受控 profile 的命令、退出码、脱敏摘要、仓库状态和输入指纹；它不替代 QA、Spec Review、体验结论或归档判断。
- 凭据、token、Cookie、隐私数据和敏感日志必须脱敏；无法安全脱敏时不得保存。
- 审查或最终验证后又修改覆盖范围内的实现、测试或规格时，把旧记录标记为“已失效”，并追加新的验证记录或不重跑依据。
