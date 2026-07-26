# 三仓库边界

## RULE-REPO-001：主仓库和应用仓库各自拥有文件

- 主仓库负责 Harness、OpenSpec、跨项目文档、环境模板、Compose 和 submodule gitlink。
- `frontend/` 与 `backend/` 是独立 Git 仓库，应用内部文件只能由对应仓库跟踪；主仓库只记录模式 `160000` 的 gitlink。
- 前端和后端的技术 Rules 与 Skills 跟随对应 submodule，不在主仓库维护第二份规范源。

## RULE-REPO-002：修改 submodule 前确认局部上下文

- 先进入目标目录运行 `git status --short --branch`，读取局部 `AGENTS.md`、README 和任务相关规则。
- submodule 可能处于 detached HEAD；需要提交时必须先切换到明确工作分支。
- 跨仓库 OpenSpec tasks 分别列出每个仓库的实现、验证、授权后交付和 gitlink 更新。

## RULE-REPO-003：gitlink 只引用远端可达提交

- 交付顺序为子仓库验证 → 获得授权后提交和推送 → `git ls-remote` 核对远端 SHA → 主仓库更新 gitlink → 重新验证 → 获得授权后提交主仓库。
- 任一子仓库提交尚未远端可达时，不得更新并交付主仓库 gitlink，也不得声称递归 clone 可复现。
