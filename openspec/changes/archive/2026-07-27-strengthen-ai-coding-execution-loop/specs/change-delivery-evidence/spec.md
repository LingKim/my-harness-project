## ADDED Requirements

### Requirement: 验证采集器只执行受控验证配置
项目 SHALL 提供确定性验证采集器，根据明确选择的根、前端、后端或跨栈 profile 运行项目登记的验证命令并记录开始时间、结束时间、仓库、完整命令、退出码和状态。采集器 MUST NOT 接受任意 Shell 字符串作为隐式执行入口，也不得执行 build、外部写入、Git 写操作或未登记命令。

#### Scenario: 运行前端验证 profile
- **WHEN** 主 Agent 为一个前端 change 选择前端基础验证 profile
- **THEN** 采集器只运行 profile 登记的 lint、typecheck 和测试命令
- **AND** 每条命令的实际退出码分别记录，不因后续命令通过而覆盖前序失败

#### Scenario: 请求未登记命令
- **WHEN** 调用者要求采集器执行不在批准 profile 中的命令或包含 Shell 控制操作符的参数
- **THEN** 采集器拒绝执行并返回失败状态
- **AND** 不创建虚假的验证成功记录

### Requirement: 机器验证清单与人工交付结论分离
采集器 SHALL 生成不含完整原始日志和敏感信息的机器验证清单，保存命令、状态、关键安全摘要、仓库 HEAD 和输入指纹。`evidence.md` MUST 继续作为人工可读交付结论，由主 Agent复核后引用或汇总机器清单；采集器不得自行填写 QA、Spec Review、体验结论或归档建议。

#### Scenario: 验证命令全部通过
- **WHEN** 批准 profile 中所有命令实际退出码为零
- **THEN** 机器清单逐项记录 `PASS` 和对应退出码
- **AND** `evidence.md` 仍需由主 Agent 根据实际范围填写未验证项、审查和最终结论

#### Scenario: 输出包含疑似敏感信息
- **WHEN** 验证输出包含 token、Cookie、凭据或隐私数据模式
- **THEN** 机器清单不得保存原始敏感内容
- **AND** 只记录已脱敏摘要、阻塞说明或安全错误类别

### Requirement: 验证后输入变化会使机器证据失效
机器验证清单 MUST 记录与验证范围相关的 change artifacts、仓库 HEAD、工作树差异或显式输入文件指纹。归档前的时效检查发现这些输入在验证后变化时 MUST 将对应结果判为失效，并列出需要重新运行的 profile；不得继续沿用旧 `PASS`。

#### Scenario: Spec Review 后修改实现
- **WHEN** 机器清单生成后相关生产代码、测试或规格发生变化
- **THEN** 时效检查报告旧结果失效及受影响仓库
- **AND** 主 Agent重新运行相关验证或在 evidence 中记录不重跑的具体依据

#### Scenario: 只修改无关文档
- **WHEN** 验证后仅修改明确不在清单输入范围内的无关文档
- **THEN** 时效检查不应将应用测试结果自动判为失效
- **AND** 文档自身仍执行对应文档或治理验证
