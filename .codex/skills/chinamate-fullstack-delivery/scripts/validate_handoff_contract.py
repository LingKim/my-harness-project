#!/usr/bin/env python3
"""使用标准库校验 ChinaMate 阶段交接合同及可判定的跨文件关系。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SKILL_ROOT = SCRIPT_PATH.parent.parent
SCHEMA_ROOT = SKILL_ROOT / "schemas"
PRE_CAPABILITY_CHANGE = "enable-stage-isolated-subagent-orchestration"
BOOTSTRAP_TASK_ID = "BOOTSTRAP-PRODUCT-SPEC"
STAGE_ROLES = {
    "PRODUCT_SPEC": "product_manager",
    "INTERACTION_DESIGN": "interaction_designer",
    "FRONTEND_IMPLEMENTATION": "frontend_engineer",
    "BACKEND_IMPLEMENTATION": "backend_engineer",
    "QA": "qa_engineer",
    "SPEC_REVIEW": "spec_reviewer",
    "EXPERIENCE_REVIEW": "experience_reviewer",
}
CONTROL_PLANE_STAGE = "CONTROL_PLANE_IMPLEMENTATION"
CONTROL_PLANE_ROLE = "main_agent"
CONTROL_PLANE_MODE = "CONTROL_PLANE"
CONTROL_PLANE_ALLOWED_FILES = frozenset(
    {
        ".codex/agents/README.md",
        ".codex/agents/product_manager.toml",
        ".codex/agents/interaction_designer.toml",
        ".codex/agents/frontend_engineer.toml",
        ".codex/agents/backend_engineer.toml",
        ".codex/agents/qa_engineer.toml",
        ".codex/agents/spec_reviewer.toml",
        ".codex/agents/experience_reviewer.toml",
        ".codex/manifest.json",
        ".codex/rules/README.md",
        ".codex/rules/workflow.md",
        ".codex/skills-lock.json",
        ".codex/skills/chinamate-fullstack-delivery/SKILL.md",
        ".codex/skills/chinamate-fullstack-delivery/agents/openai.yaml",
        ".codex/skills/chinamate-fullstack-delivery/references/control-matrix.md",
        ".codex/skills/chinamate-fullstack-delivery/references/handoff-contracts.md",
        ".codex/skills/chinamate-fullstack-delivery/references/role-routing.md",
        ".codex/skills/chinamate-fullstack-delivery/references/stage-routing.md",
        ".codex/skills/chinamate-fullstack-delivery/schemas/common.schema.json",
        ".codex/skills/chinamate-fullstack-delivery/schemas/task-contract.schema.json",
        ".codex/skills/chinamate-fullstack-delivery/schemas/result-contract.schema.json",
        ".codex/skills/chinamate-fullstack-delivery/schemas/review-result.schema.json",
        ".codex/skills/chinamate-fullstack-delivery/schemas/correction-contract.schema.json",
        ".codex/skills/chinamate-fullstack-delivery/scripts/validate_handoff_contract.py",
        "AGENTS.md",
        "README.md",
        "docs/plans/README.md",
        "scripts/check-agent-governance.sh",
        "scripts/check-harness.sh",
        "scripts/test-ai-delivery-governance.py",
        "scripts/test-custom-agents.py",
        "scripts/test-handoff-contracts.py",
        "scripts/validate-custom-agents.py",
    }
)
ROLE_WRITE_ROOTS = {
    "product_manager": ("openspec/", "docs/product/", "docs/plans/"),
    "interaction_designer": ("openspec/changes/", "docs/designs/", "docs/plans/"),
    "frontend_engineer": ("frontend/",),
    "backend_engineer": ("backend/",),
    "qa_engineer": ("frontend/", "backend/", "scripts/"),
    "spec_reviewer": (),
    "experience_reviewer": (),
}
SCHEMA_BY_KIND = {
    "request": "task-contract.schema.json",
    "result": "result-contract.schema.json",
    "review": "review-result.schema.json",
    "correction": "correction-contract.schema.json",
}


@dataclass(frozen=True)
class Contract:
    kind: str
    path: Path
    payload: dict[str, Any]


def fingerprint(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors.append(f"{path}: JSON 无效：{error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: 合同顶层必须是 object")
        return None
    return value


def resolve_ref(rule: dict[str, Any], common: dict[str, Any]) -> dict[str, Any]:
    reference = rule.get("$ref")
    prefix = "common.schema.json#/$defs/"
    if isinstance(reference, str) and reference.startswith(prefix):
        name = reference.removeprefix(prefix)
        resolved = common.get("$defs", {}).get(name)
        if isinstance(resolved, dict):
            return resolved
    return rule


def validate_value(
    value: Any,
    rule: dict[str, Any],
    field: str,
    common: dict[str, Any],
    errors: list[str],
) -> None:
    rule = resolve_ref(rule, common)
    if "const" in rule and value != rule["const"]:
        errors.append(f"{field}: 必须等于 {rule['const']!r}")
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{field}: 未知枚举 {value!r}")

    expected = rule.get("type")
    matches = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }
    if expected in matches and not matches[expected]:
        errors.append(f"{field}: 类型必须是 {expected}")
        return

    if isinstance(value, str):
        if len(value) < int(rule.get("minLength", 0)):
            errors.append(f"{field}: 字符串不能为空")
        pattern = rule.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, value) is None:
            errors.append(f"{field}: 格式不符合 {pattern}")

    if isinstance(value, list):
        if len(value) < int(rule.get("minItems", 0)):
            errors.append(f"{field}: 数组元素不足")
        if rule.get("uniqueItems"):
            normalized = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(normalized) != len(set(normalized)):
                errors.append(f"{field}: 数组元素必须唯一")
        item_rule = rule.get("items")
        if isinstance(item_rule, dict):
            for index, item in enumerate(value):
                validate_value(item, item_rule, f"{field}[{index}]", common, errors)

    if isinstance(value, dict):
        validate_object(value, rule, field, common, errors)


def validate_object(
    payload: dict[str, Any],
    schema: dict[str, Any],
    prefix: str,
    common: dict[str, Any],
    errors: list[str],
) -> None:
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    for field in required:
        if field not in payload:
            errors.append(f"{prefix}.{field}: 缺少必填字段")
    if schema.get("additionalProperties") is False:
        for field in sorted(set(payload) - set(properties)):
            errors.append(f"{prefix}.{field}: 未知字段")
    for field, value in payload.items():
        rule = properties.get(field)
        if isinstance(rule, dict):
            validate_value(value, rule, f"{prefix}.{field}", common, errors)


def contract_kind(path: Path) -> str | None:
    if path.name == "request.json":
        return "request"
    if path.name == "result.json":
        return "result"
    if "reviews" in path.parts:
        return "review"
    if "corrections" in path.parts:
        return "correction"
    return None


def is_safe_relative_path(raw: str) -> bool:
    if not raw or "\\" in raw:
        return False
    path = PurePosixPath(raw)
    return not path.is_absolute() and ".." not in path.parts and "." not in path.parts


def resolve_inside(root: Path, raw: str) -> Path | None:
    if not is_safe_relative_path(raw):
        return None
    resolved_root = root.resolve()
    resolved = (root / raw).resolve(strict=False)
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        return None
    return resolved


def path_matches_scope(path: str, scope: str) -> bool:
    """Return whether a file path is contained by an exact file or directory scope."""
    return path == scope or (scope.endswith("/") and path.startswith(scope))


def has_control_identity(payload: dict[str, Any]) -> bool:
    return payload.get("stage") == CONTROL_PLANE_STAGE or payload.get("role") == CONTROL_PLANE_ROLE


def validate_identity_branch(contract: Contract, errors: list[str]) -> None:
    payload = contract.payload
    stage = payload.get("stage")
    role = payload.get("role")
    if contract.kind == "request":
        mode = payload.get("executionMode")
        control_values = (
            stage == CONTROL_PLANE_STAGE,
            role == CONTROL_PLANE_ROLE,
            mode == CONTROL_PLANE_MODE,
        )
        if any(control_values) and not all(control_values):
            if stage != CONTROL_PLANE_STAGE:
                errors.append(f"{contract.path}:stage 必须与控制面 role/executionMode 联合使用")
            if role != CONTROL_PLANE_ROLE:
                errors.append(f"{contract.path}:role 必须与控制面 stage/executionMode 联合使用")
            if mode != CONTROL_PLANE_MODE:
                errors.append(f"{contract.path}:executionMode 必须是 {CONTROL_PLANE_MODE}")
        elif not any(control_values) and mode == CONTROL_PLANE_MODE:
            errors.append(f"{contract.path}:executionMode 不得用于 specialist 合同")
    elif contract.kind in {"result", "correction"}:
        if (stage == CONTROL_PLANE_STAGE) != (role == CONTROL_PLANE_ROLE):
            field = "role" if stage == CONTROL_PLANE_STAGE else "stage"
            errors.append(f"{contract.path}:{field} 必须保持控制面联合身份")

    if stage in STAGE_ROLES and STAGE_ROLES[stage] != role:
        errors.append(f"{contract.path}:role {role!r} 与 stage {stage!r} 不匹配")


def task_ids_in_change(root: Path, change: str) -> set[str]:
    tasks_path = root / "openspec/changes" / change / "tasks.md"
    if not tasks_path.is_file():
        return set()
    return set(
        re.findall(r"^\s*-\s*\[[ xX]\]\s+(\d+(?:\.\d+)*)\b", tasks_path.read_text(encoding="utf-8"), re.MULTILINE)
    )


def validate_control_request(contract: Contract, root: Path, errors: list[str]) -> None:
    if contract.kind != "request" or not has_control_identity(contract.payload):
        return
    payload = contract.payload
    gates = payload.get("userGates", [])
    confirmation = next(
        (item for item in gates if isinstance(item, dict) and item.get("name") == "UPDATED_SPEC_CONFIRMATION"),
        None,
    )
    if (
        confirmation is None
        or confirmation.get("status") != "SATISFIED"
        or not confirmation.get("evidenceRefs")
    ):
        errors.append(
            f"{contract.path}:userGates UPDATED_SPEC_CONFIRMATION 必须 SATISFIED 且包含 evidenceRefs"
        )

    available_task_ids = task_ids_in_change(root, str(payload.get("change", "")))
    for task_id in payload.get("taskIds", []):
        if task_id not in available_task_ids:
            errors.append(f"{contract.path}:taskIds 不存在于当前 tasks.md：{task_id}")


def validate_contract_paths(
    contract: Contract,
    root: Path,
    errors: list[str],
    stale: list[str],
) -> None:
    payload = contract.payload
    role = payload.get("role")
    write_roots = ROLE_WRITE_ROOTS.get(role, ())
    control_contract = contract.kind in {"request", "correction"} and has_control_identity(payload)
    for field in ("allowedWritePaths", "forbiddenWritePaths", "modifiedFiles", "outputReferences"):
        values = payload.get(field, [])
        if not isinstance(values, list):
            continue
        for index, raw in enumerate(values):
            if not isinstance(raw, str) or resolve_inside(root, raw) is None:
                errors.append(f"{contract.path}:{field}[{index}]: 路径必须是项目根相对路径：{raw!r}")
                continue
            if field == "allowedWritePaths":
                if control_contract:
                    if raw.endswith("/") or raw not in CONTROL_PLANE_ALLOWED_FILES:
                        errors.append(
                            f"{contract.path}:{field}[{index}]: 控制面只允许精确 allowlist 文件，拒绝 {raw!r}"
                        )
                elif "/handoffs/" in f"/{raw}" or not any(raw.startswith(item) for item in write_roots):
                    errors.append(
                        f"{contract.path}:{field}[{index}]: {role} 不允许写入 {raw!r}"
                    )

    inputs = payload.get("authoritativeInputs", [])
    if not isinstance(inputs, list):
        return
    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            continue
        raw = item.get("path")
        expected = item.get("fingerprint")
        if not isinstance(raw, str):
            continue
        resolved = resolve_inside(root, raw)
        if resolved is None or not resolved.is_file():
            errors.append(
                f"{contract.path}:authoritativeInputs[{index}]: 路径无效或越界：{raw}"
            )
            continue
        actual = fingerprint(resolved)
        if expected != actual:
            stale.append(
                f"{contract.path}:authoritativeInputs[{index}] {raw} fingerprint 已变化"
            )

    validate_control_request(contract, root, errors)


def find_by_fingerprint(contracts: list[Contract], kind: str) -> dict[str, Contract]:
    return {fingerprint(contract.path): contract for contract in contracts if contract.kind == kind}


def validate_cross_links(contracts: list[Contract], errors: list[str]) -> None:
    results = find_by_fingerprint(contracts, "result")
    reviews = find_by_fingerprint(contracts, "review")
    requests_by_dir = {item.path.parent: item for item in contracts if item.kind == "request"}
    results_by_contract_id = {
        item.payload.get("contractId"): item
        for item in contracts
        if item.kind == "result" and isinstance(item.payload.get("contractId"), str)
    }

    for contract in contracts:
        payload = contract.payload
        if payload.get("persistedBy") != "main_agent":
            errors.append(f"{contract.path}:persistedBy 必须是 main_agent")
        validate_identity_branch(contract, errors)
        role = payload.get("role")
        if contract.kind == "review" and payload.get("reviewRole") != role:
            errors.append(f"{contract.path}:reviewRole 必须与 role 一致")

        if contract.kind == "result":
            request = requests_by_dir.get(contract.path.parent)
            expected = payload.get("requestFingerprint")
            if request is None or fingerprint(request.path) != expected:
                errors.append(f"{contract.path}:requestFingerprint 未关联同目录 request.json")
            if request is not None:
                for field in ("contractId", "change", "taskIds", "stage", "role"):
                    if payload.get(field) != request.payload.get(field):
                        errors.append(f"{contract.path}:{field} 必须与同目录 request.json 一致")
                allowed = request.payload.get("allowedWritePaths", [])
                forbidden = request.payload.get("forbiddenWritePaths", [])
                role_write_roots = ROLE_WRITE_ROOTS.get(role, ())
                for modified in payload.get("modifiedFiles", []):
                    if not any(path_matches_scope(modified, scope) for scope in allowed):
                        errors.append(
                            f"{contract.path}:modifiedFiles 包含 request allowlist 外文件 {modified!r}"
                        )
                    if any(path_matches_scope(modified, scope) for scope in forbidden):
                        errors.append(
                            f"{contract.path}:modifiedFiles 命中 request forbiddenWritePaths：{modified!r}"
                        )
                    if not has_control_identity(payload) and not any(
                        path_matches_scope(modified, scope) for scope in role_write_roots
                    ):
                        errors.append(
                            f"{contract.path}:modifiedFiles 超出 {role} 角色写入根：{modified!r}"
                        )
        elif contract.kind == "review":
            expected = payload.get("resultFingerprint")
            result = results.get(expected)
            if result is None:
                errors.append(f"{contract.path}:resultFingerprint 未关联 ResultContract")
            elif has_control_identity(result.payload):
                if payload.get("stage") == "EXPERIENCE_REVIEW":
                    errors.append(
                        f"{contract.path}:EXPERIENCE_REVIEW 不得使用控制面 resultFingerprint"
                    )
                if payload.get("stage") not in {"QA", "SPEC_REVIEW"}:
                    errors.append(
                        f"{contract.path}:控制面 resultFingerprint 只能由 QA 或 SPEC_REVIEW 复核"
                    )
        elif contract.kind == "correction":
            expected = payload.get("reviewFingerprint")
            review = reviews.get(expected)
            if review is None:
                errors.append(f"{contract.path}:reviewFingerprint 未关联 ReviewResult")
            if has_control_identity(payload):
                parent = results_by_contract_id.get(payload.get("parentContractId"))
                if parent is None or not has_control_identity(parent.payload):
                    errors.append(f"{contract.path}:parentContractId 未关联控制面 ResultContract")
                else:
                    for field in ("change", "taskIds", "stage", "role"):
                        if payload.get(field) != parent.payload.get(field):
                            errors.append(f"{contract.path}:{field} 必须与控制面 ResultContract 一致")
                    request = requests_by_dir.get(parent.path.parent)
                    if request is not None:
                        request_scope = set(request.payload.get("allowedWritePaths", []))
                        for allowed in payload.get("allowedWritePaths", []):
                            if allowed not in request_scope:
                                errors.append(
                                    f"{contract.path}:allowedWritePaths 扩大了原控制面精确范围：{allowed!r}"
                                )
                if review is not None:
                    parent_fingerprint = fingerprint(parent.path) if parent is not None else None
                    if review.payload.get("resultFingerprint") != parent_fingerprint:
                        errors.append(
                            f"{contract.path}:reviewFingerprint 未审查 parentContractId 对应结果"
                        )

    for result_fingerprint, result in results.items():
        if not has_control_identity(result.payload):
            continue
        related = [
            review
            for review in (item for item in contracts if item.kind == "review")
            if review.payload.get("resultFingerprint") == result_fingerprint
        ]
        acceptance_status = result.payload.get("acceptance", {}).get("status")
        if acceptance_status != "PENDING" or related:
            stages = {item.payload.get("stage") for item in related}
            for required_stage in ("QA", "SPEC_REVIEW"):
                if required_stage not in stages:
                    errors.append(
                        f"{result.path}:resultFingerprint 缺少 {required_stage} ReviewResult"
                    )


def validate_findings(contracts: list[Contract], errors: list[str]) -> None:
    reviews = [item for item in contracts if item.kind == "review"]
    results = find_by_fingerprint(contracts, "result")
    reviews_by_fingerprint = find_by_fingerprint(contracts, "review")
    for review in reviews:
        seen: set[str] = set()
        for finding in review.payload.get("findings", []):
            if not isinstance(finding, dict):
                continue
            finding_id = finding.get("findingId")
            if not isinstance(finding_id, str):
                continue
            if finding_id in seen:
                errors.append(f"{review.path}:findingId 重复：{finding_id}")
            seen.add(finding_id)
            if finding.get("ownerRole") == CONTROL_PLANE_ROLE:
                target = results.get(review.payload.get("resultFingerprint"))
                if target is None or not has_control_identity(target.payload):
                    errors.append(
                        f"{review.path}:ownerRole {CONTROL_PLANE_ROLE} 仅允许用于控制面 ResultContract"
                    )

    for correction in (item for item in contracts if item.kind == "correction"):
        source_review = reviews_by_fingerprint.get(
            correction.payload.get("reviewFingerprint")
        )
        finding_ids = correction.payload.get("findingIds", [])
        for finding_id in finding_ids:
            source_finding = None
            if source_review is not None:
                source_finding = next(
                    (
                        finding
                        for finding in source_review.payload.get("findings", [])
                        if isinstance(finding, dict)
                        and finding.get("findingId") == finding_id
                        and finding.get("status") == "OPEN"
                    ),
                    None,
                )
            if source_finding is None:
                errors.append(
                    f"{correction.path}:findingIds 中 {finding_id} 未被 reviewFingerprint "
                    "指向的 ReviewResult 记录为 OPEN"
                )
                continue

            required_role = str(source_review.payload.get("reviewRole"))
            target_result = source_review.payload.get("resultFingerprint")
            resolved = any(
                review.payload.get("reviewRole") == required_role
                and review.payload.get("resultFingerprint") == target_result
                and any(
                    isinstance(finding, dict)
                    and finding.get("findingId") == finding_id
                    and finding.get("status") == "RESOLVED"
                    for finding in review.payload.get("findings", [])
                )
                for review in reviews
            )
            if not resolved:
                errors.append(
                    f"{correction.path}:finding {finding_id} 尚无相同 reviewRole "
                    f"{required_role}、相同 resultFingerprint 的 RESOLVED 复核"
                )


def validate_bootstrap(
    root: Path, change: str, contracts: list[Contract], errors: list[str]
) -> None:
    product_contracts = [
        item for item in contracts if item.payload.get("stage") == "PRODUCT_SPEC"
    ]
    if change == PRE_CAPABILITY_CHANGE and any(
        item.payload.get("taskIds") == [BOOTSTRAP_TASK_ID] for item in product_contracts
    ):
        errors.append(
            "pre-capability PRODUCT_SPEC 合同持久化为 NOT_APPLICABLE，不得追溯伪造 request/result"
        )
        return
    tasks_exist = (root / "openspec/changes" / change / "tasks.md").is_file()
    for contract in product_contracts:
        if not tasks_exist and contract.payload.get("taskIds") != [BOOTSTRAP_TASK_ID]:
            errors.append(
                f"{contract.path}:taskIds bootstrap 必须是 [{BOOTSTRAP_TASK_ID!r}]"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=SKILL_ROOT.parent.parent.parent)
    parser.add_argument("--change", required=True)
    parser.add_argument("--all", action="store_true", help="校验 change 下全部合同")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    change_root = root / "openspec/changes" / args.change
    handoffs_root = change_root / "handoffs"
    errors: list[str] = []
    stale: list[str] = []

    common = load_json(SCHEMA_ROOT / "common.schema.json", errors) or {}
    schemas = {
        kind: load_json(SCHEMA_ROOT / filename, errors) or {}
        for kind, filename in SCHEMA_BY_KIND.items()
    }
    contracts: list[Contract] = []
    if handoffs_root.is_dir():
        for path in sorted(handoffs_root.rglob("*.json")):
            kind = contract_kind(path)
            if kind is None:
                errors.append(f"{path}: 无法识别合同类型")
                continue
            payload = load_json(path, errors)
            if payload is None:
                continue
            validate_object(payload, schemas[kind], path.as_posix(), common, errors)
            contract = Contract(kind=kind, path=path, payload=payload)
            contracts.append(contract)
            validate_contract_paths(contract, root, errors, stale)

    validate_cross_links(contracts, errors)
    validate_findings(contracts, errors)
    validate_bootstrap(root, args.change, contracts, errors)

    if errors:
        print("FAIL：阶段交接合同无效", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if stale:
        print("STALE：阶段交接合同输入已变化", file=sys.stderr)
        for item in stale:
            print(f"- {item}", file=sys.stderr)
        return 2
    print(f"PASS：{args.change} 的 {len(contracts)} 个阶段交接合同结构与引用有效")
    print("说明：机器门禁只验证结构、路径、fingerprint 与引用，不替代语义审查。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
