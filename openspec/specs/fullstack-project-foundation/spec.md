## Purpose

定义本仓库前后端工程、本地数据库、OpenAI-compatible 集成以及 Harness 验证所必须满足的基础能力，作为后续业务功能开发的稳定基线。

## Requirements

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

### Requirement: 可运行的前端基线
前端 SHALL 提供使用 React 和 Tailwind CSS 的类型安全 Next.js App Router 应用，并配置 lint 和自动化测试。

#### Scenario: 验证前端基线
- **WHEN** 依赖安装完成并运行前端验证命令
- **THEN** lint 和自动化测试通过
- **AND** 应用可以渲染一个最小首页

#### Scenario: 检查浏览器端配置
- **WHEN** 前端环境变量被打包给浏览器使用
- **THEN** 客户端代码只能读取带有明确公开前缀的变量
- **AND** 前端配置模板不包含数据库或 AI 凭据

### Requirement: 可运行的后端基线
后端 SHALL 提供 Java 21 Spring Boot HTTP 应用，并由 Maven 管理 Validation、Actuator、MyBatis-Plus、Flyway、MySQL 和 Spring AI 依赖。

#### Scenario: 不依赖外部服务验证后端基线
- **WHEN** 开发者在没有 MySQL 和 AI API Key 的情况下运行默认后端测试套件
- **THEN** 应用测试通过且不会访问外部模型服务
- **AND** 应用级健康检查契约返回成功响应

#### Scenario: 构建后端
- **WHEN** 在启用测试的情况下运行 Maven package 命令
- **THEN** 生成使用 Java 21 的可执行 Spring Boot 产物

### Requirement: 受版本管理的本地数据库
仓库 SHALL 定义带持久化存储和健康检查的 MySQL 8.4 本地服务，并由 Flyway 唯一负责应用数据库结构迁移。

#### Scenario: 验证 Compose 配置
- **WHEN** Docker Compose 使用文档中说明的环境变量解析根目录配置
- **THEN** 配置包含 MySQL 8.4 服务、健康检查和命名持久化存储卷
- **AND** 配置中没有提交真实密码

#### Scenario: 后端连接健康数据库
- **WHEN** MySQL 状态健康且后端使用有效的数据源变量启动
- **THEN** Flyway 在数据库访问前执行受版本管理的迁移
- **AND** MyBatis-Plus 可以使用已配置的数据源

### Requirement: Spring Boot 4 专用 MyBatis-Plus 集成
后端 SHALL 使用 MyBatis-Plus 的 Spring Boot 4 专用 starter，并且不得同时直接依赖原生 MyBatis Spring Boot starter。

#### Scenario: 默认上下文加载数据访问配置
- **WHEN** 在不连接 MySQL 的情况下运行默认后端上下文测试
- **THEN** MyBatis-Plus 配置可以被 Spring 容器加载
- **AND** 不需要创建虚假的业务实体或 Mapper

#### Scenario: 后续业务 Mapper 使用通用能力
- **WHEN** 后续业务需求创建真实 Mapper 接口
- **THEN** 该接口可以按需继承 MyBatis-Plus 的 `BaseMapper<T>`
- **AND** 数据库结构仍只能由 Flyway migration 修改

### Requirement: 可配置的 OpenAI-compatible 集成
后端 SHALL 通过 OpenAI-compatible 基础地址、API Key 和模型配置建立 AI 连接，不硬编码特定供应商。

#### Scenario: 未配置 AI
- **WHEN** 没有提供 AI API Key 且没有显式启用 AI
- **THEN** 基础后端可以启动并提供健康检查契约
- **AND** 不会尝试发起外部模型请求

#### Scenario: 启用 AI 配置
- **WHEN** 使用非空的基础地址、API Key 和模型显式启用 AI
- **THEN** Spring AI 通过服务端配置接收这些值
- **AND** 应用接口和日志都不会返回 API Key

#### Scenario: AI 必填配置不完整
- **WHEN** 已显式启用 AI 但缺少必要配置
- **THEN** 应用在发起任何模型请求前启动失败，并给出清晰的配置错误

### Requirement: 安全且有文档说明的开发配置
仓库 SHALL 提供不含敏感信息的环境变量模板，以及准确的工程安装、测试、构建和启动命令。

#### Scenario: 新开发者遵循初始化文档
- **WHEN** 开发者从全新检出的仓库开始并遵循 README
- **THEN** 可以找到全部必要的本地工具、环境变量、端口和命令
- **AND** 已提交的示例中不存在可用凭据

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
