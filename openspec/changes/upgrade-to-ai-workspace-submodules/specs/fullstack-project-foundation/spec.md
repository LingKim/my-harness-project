## MODIFIED Requirements

### Requirement: 前后端工程相互独立
仓库 SHALL 包含由 Git submodule 引入的 `frontend/` 和 `backend/` 独立工程；每个工程分别使用所属技术生态的依赖清单、锁定文件或 Wrapper、源码结构、验证命令和独立 Git 历史，主仓库通过 gitlink 固定其具体提交。

#### Scenario: 开发者检查仓库结构
- **WHEN** 开发者递归检出仓库
- **THEN** 可以在 `frontend/` 中识别并操作独立前端仓库
- **AND** 可以在 `backend/` 中识别并操作独立后端仓库
- **AND** 任一工程都不依赖另一工程的构建工具
- **AND** 主仓库通过 `.gitmodules` 和模式 `160000` 的 gitlink 记录两个工程

#### Scenario: submodule 尚未初始化
- **WHEN** 开发者普通检出主仓库但尚未初始化 submodule
- **THEN** 文档提供 `git submodule update --init --recursive` 恢复两个工程

### Requirement: Harness 验证初始化基线
仓库 Harness 检查 SHALL 检测前端、后端、基础设施、OpenSpec 和 Git submodule 关键元数据是否缺失或漂移。

#### Scenario: 基线结构完整
- **WHEN** 在初始化后的仓库中运行 `./scripts/check-harness.sh`
- **THEN** 只有必要的全栈基线、现有 Harness 结构、`.gitmodules`、正确的 submodule URL 和模式 `160000` 的 gitlink 都存在时才报告成功

#### Scenario: 关键工程文件缺失
- **WHEN** 必要的依赖清单或基础设施配置不存在
- **THEN** Harness 检查以失败状态退出并指出缺失路径

#### Scenario: submodule 元数据错误
- **WHEN** `.gitmodules` 缺失、URL 与约定不一致或根索引没有记录正确 gitlink
- **THEN** Harness 检查以失败状态退出并指出对应的 Git 结构问题
