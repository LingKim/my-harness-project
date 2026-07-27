# 验证 Profiles

`collect_verification.py` 只运行脚本内登记的参数数组，不接受任意 Shell 命令。

| Profile | 用途 | 固定验证 |
| --- | --- | --- |
| `root-governance` | 根治理与 OpenSpec change | governance、Harness、strict validate、diff check |
| `frontend-static` | 前端静态与单元行为 | lint、typecheck、Vitest |
| `frontend-e2e` | 真实浏览器路径 | Playwright；必须显式选择 |
| `backend-architecture` | 后端模块与分层 | ArchitectureRulesTests |
| `backend-test` | 后端完整测试 | Maven test；按风险显式选择 |
| `fullstack-governance` | 跨栈治理门禁 | 根治理加前后端局部治理检查，不运行 build |

## 环境预检

使用临时 worktree、安装依赖、启动前端或运行完整后端测试前执行：

```bash
python3 .codex/skills/chinamate-fullstack-delivery/scripts/check_delivery_environment.py \
  --repo-root <aiworkspace-root>
```

- `BLOCKED`：先修复环境，不记为业务回归。frontend 仓库外 `node_modules` 软链接必须移除，并在当前 worktree 优先使用 `pnpm install --offline`。
- `REVIEW_REQUIRED`：先做最小验证。Java 21+ 且使用 Mockito、未配置显式 test agent 时，先运行最小 Mockito 测试；动态 attach 失败不得通过跳过断言处理。

## 真实场景边界

固定 profile 只证明公共命令。涉及分页、阈值、稳定排序、重试或幂等时，tasks 和 `evidence.md` 还必须记录跨越边界两侧的 change-local fixture。

分页至少使用 `pageSize + 1` 条记录，并证明：第一页数量、下一页数量、`hasNext`、相同主排序值下的 stable tie-breaker。单条 CRUD smoke test 只能证明连通和基本持久化，不能证明分页 PASS。

## Cleanup manifest

需要清理临时资源时，在 change 的 `reviews/cleanup-manifest.json` 声明精确目标。manifest 不授予删除权限；完成用户已授权的清理后运行：

```bash
MYSQL_PWD=<通过环境变量提供> \
python3 .codex/skills/chinamate-fullstack-delivery/scripts/check_delivery_cleanup.py \
  --project-root <aiworkspace-root> \
  --manifest openspec/changes/<change-name>/reviews/cleanup-manifest.json
```

支持的资源类型与期望终态：

```json
{
  "schema": "chinamate-cleanup-manifest/v1",
  "resources": [
    {"type": "path", "path": "/private/tmp/example", "expected": "ABSENT"},
    {"type": "gitBranch", "repo": ".", "name": "codex/example", "expected": "ABSENT"},
    {"type": "gitWorktree", "repo": ".", "path": "/private/tmp/example", "expected": "ABSENT"},
    {"type": "tcpPort", "host": "127.0.0.1", "port": 3100, "expected": "CLOSED"},
    {"type": "mysqlDatabase", "host": "127.0.0.1", "port": 3306, "user": "root", "passwordEnv": "MYSQL_PWD", "name": "example_test", "expected": "ABSENT"}
  ]
}
```

checker 只读并拒绝任意命令、仓库外 Git 目标、非临时 worktree/path、非回环端口、非 `*_test` 数据库和明文密码。只有全部资源为 `ABSENT`/`CLOSED` 才可声明零残留。

## 运行

```bash
python3 .codex/skills/chinamate-fullstack-delivery/scripts/collect_verification.py \
  --profile root-governance \
  --change <change-name> \
  --output openspec/changes/<change-name>/reviews/verification-manifest.json
```

验证输入变化后：

```bash
python3 .codex/skills/chinamate-fullstack-delivery/scripts/check_verification_freshness.py \
  --manifest openspec/changes/<change-name>/reviews/verification-manifest.json
```

manifest 只证明命令与输入事实。主 Agent仍需在 `evidence.md` 记录未验证项、QA、Spec Review、体验、残余风险和归档建议。
