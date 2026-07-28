# 阶段交接合同

Agent之间不依赖口头交代。主 Agent从OpenSpec、Git、测试和`evidence.md`构造合同，specialist只消费已验收输入并返回结构化payload；主 Agent是`handoffs/`的唯一持久化写入者。

## 合同类型

- `TaskContract`：派工目标、权威输入、依赖、角色、写入边界、验收条件、验证计划和用户/Git gate。
- `ResultContract`：实际修改、输出引用、验证摘要、偏差、阻塞、未运行项、风险与建议。
- `ReviewResult`：QA或reviewer的验证结果及带稳定`findingId`的finding。
- `CorrectionContract`：主 Agent引用原合同、review fingerprint和finding签发的最小修复工作包。

schema位于`../schemas/`，版本`1.0`；validator入口：

```bash
python3 .codex/skills/chinamate-fullstack-delivery/scripts/validate_handoff_contract.py \
  --change <change-name> --all
```

最小派工示例（仅演示字段形状，fingerprint必须按真实文件重算）：

```json
{
  "schemaVersion": "1.0",
  "contractId": "account-backend-001",
  "change": "add-account",
  "stage": "BACKEND_IMPLEMENTATION",
  "role": "backend_engineer",
  "taskIds": ["2.1"],
  "executionMode": "SUBAGENT",
  "authoritativeInputs": [
    {
      "path": "openspec/changes/add-account/design.md",
      "fingerprint": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "dependencies": [],
  "allowedWritePaths": ["backend/"],
  "forbiddenWritePaths": ["frontend/", "openspec/changes/add-account/handoffs/"],
  "expectedOutputs": ["后端实现与测试"],
  "acceptanceCriteria": ["目标测试通过且没有越界修改"],
  "verificationPlan": ["./mvnw test"],
  "userGates": [{"name": "SPEC_CONFIRMATION", "status": "SATISFIED", "evidenceRefs": ["user-message"]}],
  "gitGates": [{"name": "GIT_WRITE", "status": "NOT_APPLICABLE", "evidenceRefs": []}],
  "status": "ISSUED",
  "persistedBy": "main_agent"
}
```

## 持久化布局

```text
openspec/changes/<change>/handoffs/<contractId>/
├── request.json
├── result.json
├── reviews/<review-id>.json
└── corrections/<correction-id>.json
```

subagent无论是否具有应用代码写权限，都不得直接写入上述目录。它只向主 Agent返回与schema同构的payload；主 Agent校验字段、输入freshness、路径边界和gate后再保存。

## Bootstrap与迁移边界

未来新change尚未创建时，主 Agent在会话中先构造完整`PRODUCT_SPEC` JSON合同，`taskIds`使用保留值`BOOTSTRAP-PRODUCT-SPEC`。change创建后立即按相同`contractId`保存request/result并重新计算可用输入fingerprint。

本能力change的产品规划早于schema和validator生效，属于pre-capability structured assignment，合同持久化为`NOT_APPLICABLE`。不得根据聊天或事后文件追溯伪造规划阶段合同；首批真实快照从能力生效后的后续阶段开始。

## 受限控制面合同

没有现有specialist拥有目标文件的已确认根治理实现，可以使用`CONTROL_PLANE_IMPLEMENTATION + main_agent + CONTROL_PLANE`。三个标记必须联合出现，只允许`TaskContract`、`ResultContract`和对应`CorrectionContract`；`main_agent`不是第八个custom agent，`ReviewResult`不得使用控制面身份。

- request必须包含`UPDATED_SPEC_CONFIRMATION = SATISFIED`及真实用户证据。
- `allowedWritePaths`必须逐项列出validator固定allowlist内的精确文件，不能使用`.codex/`、`scripts/`、`docs/`或项目根等目录授权。
- result必须关联同目录request fingerprint，并保持`contractId`、change、taskIds、stage、role一致；`modifiedFiles`只能是request精确范围的子集。
- 控制面result通过`resultFingerprint`交给现有`QA/qa_engineer`和`SPEC_REVIEW/spec_reviewer`，两者继续使用specialist身份；`EXPERIENCE_REVIEW`不适用。
- 控制面finding的`ownerRole`可以是`main_agent`。主Agent只能签发不扩大原精确范围的correction，并由产生finding的原QA或Spec Reviewer复核为`RESOLVED`。
- 不得把合同签发前已完成的文件追溯包装为控制面Result，也不得把该例外用于业务、产品、交互、前后端、QA、review、基础设施或Git写操作。

## Freshness与事实源

- 输入内容、关联result/review或验证基线变化后，旧合同为`STALE`。
- 主 Agent必须重签或基于当前事实显式重新验收，不能静默沿用。
- OpenSpec决定应做什么；Git决定实际修改；测试决定验证事实；`evidence.md`决定交付结论。
- `handoffs/`只记录谁在什么输入和权限边界下返回了什么，不决定task完成或change归档。

## Review闭环

`OPEN`阻断finding必须由主 Agent签发`CorrectionContract`。实现结果不能自行关闭finding；只有原QA/reviewer或适用复核返回`RESOLVED`，或真实用户/设计依据支持`WAIVED`后，主 Agent才能验收。

共享工作区中的“拒收”表示不进入下游、不勾选task、不写成有效证据、不关闭合同，不表示文件物理不可见或已经自动回滚。
