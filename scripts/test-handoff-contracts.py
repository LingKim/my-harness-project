#!/usr/bin/env python3
"""验证阶段隔离交接合同 schema、freshness、权限边界与复核闭环。"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = PROJECT_ROOT / ".codex/skills/chinamate-fullstack-delivery"
VALIDATOR = SKILL_ROOT / "scripts/validate_handoff_contract.py"
SCHEMA_FILES = (
    SKILL_ROOT / "schemas/common.schema.json",
    SKILL_ROOT / "schemas/task-contract.schema.json",
    SKILL_ROOT / "schemas/result-contract.schema.json",
    SKILL_ROOT / "schemas/review-result.schema.json",
    SKILL_ROOT / "schemas/correction-contract.schema.json",
)
BOOTSTRAP_TASK_ID = "BOOTSTRAP-PRODUCT-SPEC"
PRE_CAPABILITY_CHANGE = "enable-stage-isolated-subagent-orchestration"
CONTROL_PLANE_STAGE = "CONTROL_PLANE_IMPLEMENTATION"
CONTROL_PLANE_ROLE = "main_agent"
CONTROL_PLANE_MODE = "CONTROL_PLANE"
CONTROL_PLANE_ALLOWED_FILES = (
    ".codex/skills/chinamate-fullstack-delivery/schemas/task-contract.schema.json",
    ".codex/skills/chinamate-fullstack-delivery/scripts/validate_handoff_contract.py",
    "scripts/test-handoff-contracts.py",
)


def sha256_bytes(content: bytes) -> str:
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def file_fingerprint(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def mutate_json(path: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    write_json(path, payload)


def gate(name: str, status: str, *evidence_refs: str) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "evidenceRefs": list(evidence_refs),
    }


def acceptance(status: str = "PENDING", *evidence_refs: str) -> dict[str, Any]:
    return {"status": status, "evidenceRefs": list(evidence_refs)}


def create_project_root(temp_dir: str, change: str = "fixture-change") -> Path:
    root = Path(temp_dir)
    (root / "backend").mkdir(parents=True)
    change_root = root / "openspec/changes" / change
    change_root.mkdir(parents=True)
    (change_root / "proposal.md").write_text("# fixture\n", encoding="utf-8")
    return root


def create_implementation_handoff(root: Path, change: str = "fixture-change") -> dict[str, Path]:
    change_root = root / "openspec/changes" / change
    input_path = change_root / "proposal.md"
    contract_root = change_root / "handoffs/backend-impl-001"
    request_path = contract_root / "request.json"
    result_path = contract_root / "result.json"
    open_review_path = contract_root / "reviews/qa-open.json"
    correction_path = contract_root / "corrections/fix-finding-001.json"
    resolved_review_path = contract_root / "reviews/qa-resolved.json"

    request = {
        "schemaVersion": "1.0",
        "contractId": "backend-impl-001",
        "change": change,
        "stage": "BACKEND_IMPLEMENTATION",
        "role": "backend_engineer",
        "taskIds": ["2.1"],
        "executionMode": "SUBAGENT",
        "authoritativeInputs": [
            {
                "path": input_path.relative_to(root).as_posix(),
                "fingerprint": file_fingerprint(input_path),
            }
        ],
        "dependencies": ["product-spec-001"],
        "allowedWritePaths": ["backend/"],
        "forbiddenWritePaths": [
            ".codex/",
            "openspec/",
            f"openspec/changes/{change}/handoffs/",
        ],
        "expectedOutputs": ["backend implementation result"],
        "acceptanceCriteria": ["目标验证通过且没有越界修改"],
        "verificationPlan": ["python3 scripts/test-handoff-contracts.py"],
        "userGates": [gate("SPEC_CONFIRMATION", "SATISFIED", "user-message:confirmed")],
        "gitGates": [gate("GIT_WRITE", "NOT_APPLICABLE")],
        "status": "ISSUED",
        "persistedBy": "main_agent",
    }
    write_json(request_path, request)

    result = {
        "schemaVersion": "1.0",
        "contractId": "backend-impl-001",
        "change": change,
        "stage": "BACKEND_IMPLEMENTATION",
        "role": "backend_engineer",
        "taskIds": ["2.1"],
        "requestFingerprint": file_fingerprint(request_path),
        "status": "PASS_WITH_ISSUES",
        "modifiedFiles": ["backend/src/test/java/example/ContractTest.java"],
        "outputReferences": ["backend/src/test/java/example/ContractTest.java"],
        "verificationSummary": [
            {
                "command": "./mvnw -Dtest=ContractTest test",
                "status": "PASS",
                "summary": "1 test passed",
            }
        ],
        "deviations": [],
        "blockers": [],
        "notRun": [],
        "residualRisks": ["需要 QA 复核边界"],
        "recommendations": ["建议 QA 复核；该建议不是自行派工"],
        "acceptance": acceptance(),
        "persistedBy": "main_agent",
    }
    write_json(result_path, result)

    open_review = {
        "schemaVersion": "1.0",
        "contractId": "qa-review-001",
        "change": change,
        "stage": "QA",
        "role": "qa_engineer",
        "taskIds": ["1.1"],
        "resultFingerprint": file_fingerprint(result_path),
        "reviewRole": "qa_engineer",
        "status": "FAIL",
        "findings": [
            {
                "findingId": "FINDING-001",
                "severity": "P1",
                "status": "OPEN",
                "evidenceRefs": ["backend/src/test/java/example/ContractTest.java"],
                "ownerRole": "backend_engineer",
                "requiredVerification": ["重新运行 ContractTest"],
            }
        ],
        "verificationSummary": [],
        "blockers": ["FINDING-001 未关闭"],
        "notRun": [],
        "residualRisks": [],
        "acceptance": acceptance(),
        "persistedBy": "main_agent",
    }
    write_json(open_review_path, open_review)

    correction = {
        "schemaVersion": "1.0",
        "contractId": "fix-finding-001",
        "change": change,
        "stage": "BACKEND_IMPLEMENTATION",
        "role": "backend_engineer",
        "taskIds": ["2.1"],
        "parentContractId": "backend-impl-001",
        "reviewFingerprint": file_fingerprint(open_review_path),
        "findingIds": ["FINDING-001"],
        "authoritativeInputs": copy.deepcopy(request["authoritativeInputs"]),
        "allowedWritePaths": ["backend/"],
        "forbiddenWritePaths": request["forbiddenWritePaths"],
        "expectedFixes": ["修复 FINDING-001"],
        "acceptanceCriteria": ["原 QA 复核将 FINDING-001 标记为 RESOLVED"],
        "retestPlan": ["重新运行 ContractTest"],
        "userGates": request["userGates"],
        "gitGates": request["gitGates"],
        "status": "ISSUED",
        "persistedBy": "main_agent",
    }
    write_json(correction_path, correction)

    resolved_review = copy.deepcopy(open_review)
    resolved_review["contractId"] = "qa-review-002"
    resolved_review["status"] = "PASS"
    resolved_review["findings"][0]["status"] = "RESOLVED"
    resolved_review["blockers"] = []
    resolved_review["verificationSummary"] = [
        {
            "command": "./mvnw -Dtest=ContractTest test",
            "status": "PASS",
            "summary": "复核通过",
        }
    ]
    write_json(resolved_review_path, resolved_review)

    return {
        "request": request_path,
        "result": result_path,
        "open_review": open_review_path,
        "correction": correction_path,
        "resolved_review": resolved_review_path,
        "input": input_path,
    }


def create_bootstrap_handoff(root: Path, change: str) -> dict[str, Path]:
    change_root = root / "openspec/changes" / change
    bootstrap_input = root / "README.md"
    bootstrap_input.write_text("# bootstrap input\n", encoding="utf-8")
    contract_root = change_root / "handoffs/bootstrap-product-spec-001"
    request_path = contract_root / "request.json"
    result_path = contract_root / "result.json"
    request = {
        "schemaVersion": "1.0",
        "contractId": "bootstrap-product-spec-001",
        "change": change,
        "stage": "PRODUCT_SPEC",
        "role": "product_manager",
        "taskIds": [BOOTSTRAP_TASK_ID],
        "executionMode": "SUBAGENT",
        "authoritativeInputs": [
            {"path": "README.md", "fingerprint": file_fingerprint(bootstrap_input)}
        ],
        "dependencies": [],
        "allowedWritePaths": [f"openspec/changes/{change}/"],
        "forbiddenWritePaths": ["frontend/", "backend/"],
        "expectedOutputs": ["proposal.md", "design.md", "tasks.md", "specs/**/*.md"],
        "acceptanceCriteria": ["规划 artifacts 完整并等待真实用户确认"],
        "verificationPlan": [f"openspec validate {change} --strict"],
        "userGates": [gate("SPEC_CONFIRMATION", "PENDING")],
        "gitGates": [gate("GIT_WRITE", "NOT_APPLICABLE")],
        "status": "ISSUED",
        "persistedBy": "main_agent",
    }
    write_json(request_path, request)
    result = {
        "schemaVersion": "1.0",
        "contractId": "bootstrap-product-spec-001",
        "change": change,
        "stage": "PRODUCT_SPEC",
        "role": "product_manager",
        "taskIds": [BOOTSTRAP_TASK_ID],
        "requestFingerprint": file_fingerprint(request_path),
        "status": "PASS",
        "modifiedFiles": [
            f"openspec/changes/{change}/proposal.md",
            f"openspec/changes/{change}/design.md",
            f"openspec/changes/{change}/tasks.md",
        ],
        "outputReferences": [f"openspec/changes/{change}/proposal.md"],
        "verificationSummary": [],
        "deviations": [],
        "blockers": ["等待真实用户确认"],
        "notRun": [],
        "residualRisks": [],
        "recommendations": ["请主 Agent 请求用户确认；本结果不生成确认"],
        "acceptance": acceptance(),
        "persistedBy": "main_agent",
    }
    write_json(result_path, result)
    return {"request": request_path, "result": result_path}


def create_control_plane_handoff(
    root: Path, change: str = "fixture-change"
) -> dict[str, Path]:
    """建立控制面实现、QA/Spec Review 与 correction 复核的完整有效链。"""
    change_root = root / "openspec/changes" / change
    design_path = change_root / "design.md"
    tasks_path = change_root / "tasks.md"
    design_path.write_text("# control plane governance design\n", encoding="utf-8")
    tasks_path.write_text(
        "- [ ] 2.1 实现控制面 schema 与 validator\n",
        encoding="utf-8",
    )

    contract_root = change_root / "handoffs/control-plane-impl-001"
    request_path = contract_root / "request.json"
    result_path = contract_root / "result.json"
    qa_open_path = contract_root / "reviews/qa-open.json"
    spec_review_path = contract_root / "reviews/spec-review.json"
    correction_path = contract_root / "corrections/fix-control-finding-001.json"
    qa_resolved_path = contract_root / "reviews/qa-resolved.json"

    request = {
        "schemaVersion": "1.0",
        "contractId": "control-plane-impl-001",
        "change": change,
        "stage": CONTROL_PLANE_STAGE,
        "role": CONTROL_PLANE_ROLE,
        "taskIds": ["2.1"],
        "executionMode": CONTROL_PLANE_MODE,
        "authoritativeInputs": [
            {
                "path": design_path.relative_to(root).as_posix(),
                "fingerprint": file_fingerprint(design_path),
            },
            {
                "path": tasks_path.relative_to(root).as_posix(),
                "fingerprint": file_fingerprint(tasks_path),
            },
        ],
        "dependencies": ["spec-update-control-plane-001"],
        "allowedWritePaths": list(CONTROL_PLANE_ALLOWED_FILES),
        "forbiddenWritePaths": [
            "openspec/",
            "frontend/",
            "backend/",
            f"openspec/changes/{change}/handoffs/",
        ],
        "expectedOutputs": ["受限控制面 schema、validator 与 RED 测试"],
        "acceptanceCriteria": ["控制面联合身份、精确 allowlist 与复核链可机器校验"],
        "verificationPlan": ["python3 scripts/test-handoff-contracts.py"],
        "userGates": [
            gate(
                "UPDATED_SPEC_CONFIRMATION",
                "SATISFIED",
                "conversation:user-confirmation:2026-07-28",
            )
        ],
        "gitGates": [gate("GIT_WRITE", "NOT_APPLICABLE")],
        "status": "ISSUED",
        "persistedBy": "main_agent",
    }
    write_json(request_path, request)

    result = {
        "schemaVersion": "1.0",
        "contractId": "control-plane-impl-001",
        "change": change,
        "stage": CONTROL_PLANE_STAGE,
        "role": CONTROL_PLANE_ROLE,
        "taskIds": ["2.1"],
        "requestFingerprint": file_fingerprint(request_path),
        "status": "PASS_WITH_ISSUES",
        "modifiedFiles": [
            ".codex/skills/chinamate-fullstack-delivery/schemas/task-contract.schema.json",
            "scripts/test-handoff-contracts.py",
        ],
        "outputReferences": ["scripts/test-handoff-contracts.py"],
        "verificationSummary": [
            {
                "command": "python3 scripts/test-handoff-contracts.py",
                "status": "PASS_WITH_ISSUES",
                "summary": "控制面实现等待独立 QA 与 Spec Review",
            }
        ],
        "deviations": [],
        "blockers": [],
        "notRun": [],
        "residualRisks": ["需要关闭 QA finding"],
        "recommendations": ["由既有 QA 与 Spec Reviewer 独立复核"],
        "acceptance": acceptance(),
        "persistedBy": "main_agent",
    }
    write_json(result_path, result)

    qa_open = {
        "schemaVersion": "1.0",
        "contractId": "control-plane-qa-001",
        "change": change,
        "stage": "QA",
        "role": "qa_engineer",
        "taskIds": ["2.1"],
        "resultFingerprint": file_fingerprint(result_path),
        "reviewRole": "qa_engineer",
        "status": "FAIL",
        "findings": [
            {
                "findingId": "CONTROL-FINDING-001",
                "severity": "P1",
                "status": "OPEN",
                "evidenceRefs": ["scripts/test-handoff-contracts.py"],
                "ownerRole": CONTROL_PLANE_ROLE,
                "requiredVerification": ["重跑控制面合同测试"],
            }
        ],
        "verificationSummary": [],
        "blockers": ["CONTROL-FINDING-001 未关闭"],
        "notRun": [],
        "residualRisks": [],
        "acceptance": acceptance(),
        "persistedBy": "main_agent",
    }
    write_json(qa_open_path, qa_open)

    spec_review = {
        "schemaVersion": "1.0",
        "contractId": "control-plane-spec-review-001",
        "change": change,
        "stage": "SPEC_REVIEW",
        "role": "spec_reviewer",
        "taskIds": ["2.1"],
        "resultFingerprint": file_fingerprint(result_path),
        "reviewRole": "spec_reviewer",
        "status": "PASS",
        "findings": [],
        "verificationSummary": [],
        "blockers": [],
        "notRun": [],
        "residualRisks": [],
        "acceptance": acceptance(),
        "persistedBy": "main_agent",
    }
    write_json(spec_review_path, spec_review)

    correction = {
        "schemaVersion": "1.0",
        "contractId": "fix-control-finding-001",
        "change": change,
        "stage": CONTROL_PLANE_STAGE,
        "role": CONTROL_PLANE_ROLE,
        "taskIds": ["2.1"],
        "parentContractId": "control-plane-impl-001",
        "reviewFingerprint": file_fingerprint(qa_open_path),
        "findingIds": ["CONTROL-FINDING-001"],
        "authoritativeInputs": copy.deepcopy(request["authoritativeInputs"]),
        "allowedWritePaths": list(CONTROL_PLANE_ALLOWED_FILES),
        "forbiddenWritePaths": request["forbiddenWritePaths"],
        "expectedFixes": ["修复 CONTROL-FINDING-001"],
        "acceptanceCriteria": ["原 qa_engineer 将 finding 复核为 RESOLVED"],
        "retestPlan": ["python3 scripts/test-handoff-contracts.py"],
        "userGates": request["userGates"],
        "gitGates": request["gitGates"],
        "status": "ISSUED",
        "persistedBy": "main_agent",
    }
    write_json(correction_path, correction)

    qa_resolved = copy.deepcopy(qa_open)
    qa_resolved["contractId"] = "control-plane-qa-002"
    qa_resolved["status"] = "PASS"
    qa_resolved["findings"][0]["status"] = "RESOLVED"
    qa_resolved["blockers"] = []
    qa_resolved["verificationSummary"] = [
        {
            "command": "python3 scripts/test-handoff-contracts.py",
            "status": "PASS",
            "summary": "原 qa_engineer 复核控制面 finding 已关闭",
        }
    ]
    write_json(qa_resolved_path, qa_resolved)

    return {
        "request": request_path,
        "result": result_path,
        "qa_open": qa_open_path,
        "spec_review": spec_review_path,
        "correction": correction_path,
        "qa_resolved": qa_resolved_path,
        "design": design_path,
        "tasks": tasks_path,
    }


class HandoffContractTests(unittest.TestCase):
    def require_capability(self) -> None:
        missing = [str(path.relative_to(PROJECT_ROOT)) for path in (*SCHEMA_FILES, VALIDATOR) if not path.is_file()]
        if missing:
            self.skipTest(f"合同能力尚未实现：{', '.join(missing)}")

    def run_validator(self, root: Path, change: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--project-root",
                str(root),
                "--change",
                change,
                "--all",
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_status(
        self,
        result: subprocess.CompletedProcess[str],
        expected_status: str,
        *expected_fragments: str,
    ) -> None:
        output = f"{result.stdout}\n{result.stderr}"
        if expected_status == "PASS":
            self.assertEqual(0, result.returncode, output)
        else:
            self.assertNotEqual(0, result.returncode, output)
        self.assertIn(expected_status, output)
        for fragment in expected_fragments:
            self.assertIn(fragment, output)

    def test_required_contract_resources_exist(self) -> None:
        missing = [
            str(path.relative_to(PROJECT_ROOT))
            for path in (*SCHEMA_FILES, VALIDATOR)
            if not path.is_file()
        ]
        self.assertEqual([], missing, f"缺少合同 schema/validator：{missing}")

    def test_four_contract_types_accept_a_valid_closed_fixture(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(prefix="chinamate-handoff-valid-") as temp_dir:
            root = create_project_root(temp_dir)
            create_implementation_handoff(root)
            self.assert_status(self.run_validator(root, "fixture-change"), "PASS")

    def test_required_fields_and_unknown_fields_are_rejected_for_all_contracts(self) -> None:
        self.require_capability()
        cases = (
            ("request", "authoritativeInputs"),
            ("result", "requestFingerprint"),
            ("open_review", "findings"),
            ("correction", "findingIds"),
        )
        for contract_name, required_field in cases:
            with self.subTest(contract=contract_name, field=required_field):
                with tempfile.TemporaryDirectory(prefix="chinamate-handoff-required-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_implementation_handoff(root)
                    mutate_json(paths[contract_name], lambda payload: payload.pop(required_field))
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        required_field,
                    )

        for contract_name in ("request", "result", "open_review", "correction"):
            with self.subTest(contract=contract_name, field="unexpectedField"):
                with tempfile.TemporaryDirectory(prefix="chinamate-handoff-unknown-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_implementation_handoff(root)
                    mutate_json(
                        paths[contract_name],
                        lambda payload: payload.__setitem__("unexpectedField", True),
                    )
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        "unexpectedField",
                    )

    def test_unknown_enums_and_main_agent_control_stage_are_rejected(self) -> None:
        self.require_capability()
        cases: tuple[str, str, str] = (
            ("request", "stage", "EVIDENCE_AND_ARCHIVE"),
            ("result", "role", "main_agent"),
            ("open_review", "status", "SUCCESS"),
            ("correction", "status", "APPROVED"),
        )
        for contract_name, field, invalid_value in cases:
            with self.subTest(contract=contract_name, field=field, value=invalid_value):
                with tempfile.TemporaryDirectory(prefix="chinamate-handoff-enum-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_implementation_handoff(root)
                    mutate_json(
                        paths[contract_name],
                        lambda payload: payload.__setitem__(field, invalid_value),
                    )
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        field,
                    )

    def test_paths_must_be_project_relative_normalized_and_inside_role_roots(self) -> None:
        self.require_capability()
        cases = ("../backend/", "/tmp/backend/", "frontend/")
        for invalid_path in cases:
            with self.subTest(path=invalid_path):
                with tempfile.TemporaryDirectory(prefix="chinamate-handoff-path-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_implementation_handoff(root)
                    mutate_json(
                        paths["request"],
                        lambda payload: payload.__setitem__("allowedWritePaths", [invalid_path]),
                    )
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        "allowedWritePaths",
                    )

    def test_symlink_escape_is_rejected_after_realpath_resolution(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(
            prefix="chinamate-handoff-symlink-"
        ) as temp_dir, tempfile.TemporaryDirectory(
            prefix="chinamate-handoff-outside-"
        ) as outside_dir:
            root = create_project_root(temp_dir)
            paths = create_implementation_handoff(root)
            outside = Path(outside_dir) / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            symlink = root / "linked-input.md"
            symlink.symlink_to(outside)
            mutate_json(
                paths["request"],
                lambda payload: payload.__setitem__(
                    "authoritativeInputs",
                    [{"path": "linked-input.md", "fingerprint": file_fingerprint(outside)}],
                ),
            )
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "authoritativeInputs",
                "linked-input.md",
            )

    def test_authoritative_input_change_returns_stale(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(prefix="chinamate-handoff-stale-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_implementation_handoff(root)
            paths["input"].write_text("# changed after issue\n", encoding="utf-8")
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "STALE",
                "authoritativeInputs",
            )

    def test_request_result_review_and_correction_fingerprints_must_link(self) -> None:
        self.require_capability()
        cases = (
            ("result", "requestFingerprint"),
            ("open_review", "resultFingerprint"),
            ("correction", "reviewFingerprint"),
        )
        for contract_name, field in cases:
            with self.subTest(contract=contract_name, field=field):
                with tempfile.TemporaryDirectory(prefix="chinamate-handoff-link-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_implementation_handoff(root)
                    mutate_json(
                        paths[contract_name],
                        lambda payload: payload.__setitem__(field, "sha256:" + "0" * 64),
                    )
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        field,
                    )

    def test_final_spec_role_boundary_rejects_specialist_result_scope_violations(self) -> None:
        """FINAL-SPEC-ROLE-BOUNDARY-001：specialist result 不能越过三重写入边界。"""
        cases = (
            (
                "request allowlist",
                lambda paths: mutate_json(
                    paths["request"],
                    lambda payload: payload.__setitem__(
                        "allowedWritePaths", ["backend/src/main/"]
                    ),
                ),
                "backend/src/test/java/example/OutsideAllowlistTest.java",
                ("modifiedFiles", "allowlist"),
            ),
            (
                "forbiddenWritePaths",
                lambda paths: mutate_json(
                    paths["request"],
                    lambda payload: payload["forbiddenWritePaths"].append(
                        "backend/src/test/"
                    ),
                ),
                "backend/src/test/java/example/ContractTest.java",
                ("modifiedFiles", "forbiddenWritePaths"),
            ),
            (
                "role write root",
                lambda paths: None,
                "frontend/src/app/page.tsx",
                ("modifiedFiles", "backend_engineer"),
            ),
        )
        for label, mutate_request, modified_file, expected_fragments in cases:
            with self.subTest(boundary=label):
                with tempfile.TemporaryDirectory(
                    prefix="chinamate-specialist-result-scope-"
                ) as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_implementation_handoff(root)
                    paths["open_review"].unlink()
                    paths["correction"].unlink()
                    paths["resolved_review"].unlink()
                    mutate_request(paths)
                    mutate_json(
                        paths["result"],
                        lambda payload: payload.update(
                            {
                                "requestFingerprint": file_fingerprint(paths["request"]),
                                "modifiedFiles": [modified_file],
                            }
                        ),
                    )
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        *expected_fragments,
                    )

    def test_final_spec_finding_link_binds_correction_and_resolution_to_source_review(self) -> None:
        """FINAL-SPEC-FINDING-LINK-002：finding 不能跨 ReviewResult 借用。"""
        cases = ("wrong review", "finding absent", "borrowed resolution")
        for case in cases:
            with self.subTest(link=case):
                with tempfile.TemporaryDirectory(
                    prefix="chinamate-finding-review-link-"
                ) as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_implementation_handoff(root)

                    if case == "wrong review":
                        mutate_json(
                            paths["correction"],
                            lambda payload: payload.__setitem__(
                                "reviewFingerprint",
                                file_fingerprint(paths["resolved_review"]),
                            ),
                        )
                        expected_fragments = ("reviewFingerprint", "FINDING-001")
                    elif case == "finding absent":
                        unrelated_review_path = (
                            paths["open_review"].parent / "qa-unrelated-open.json"
                        )
                        unrelated_review = json.loads(
                            paths["open_review"].read_text(encoding="utf-8")
                        )
                        unrelated_review["contractId"] = "qa-unrelated-open-001"
                        unrelated_review["findings"][0]["findingId"] = "FINDING-OTHER"
                        write_json(unrelated_review_path, unrelated_review)
                        mutate_json(
                            paths["correction"],
                            lambda payload: payload.__setitem__(
                                "reviewFingerprint",
                                file_fingerprint(unrelated_review_path),
                            ),
                        )
                        expected_fragments = ("reviewFingerprint", "FINDING-001")
                    else:
                        other_contract_root = (
                            root
                            / "openspec/changes/fixture-change/handoffs/backend-impl-002"
                        )
                        other_request_path = other_contract_root / "request.json"
                        other_result_path = other_contract_root / "result.json"
                        other_request = json.loads(
                            paths["request"].read_text(encoding="utf-8")
                        )
                        other_request["contractId"] = "backend-impl-002"
                        write_json(other_request_path, other_request)
                        other_result = json.loads(
                            paths["result"].read_text(encoding="utf-8")
                        )
                        other_result["contractId"] = "backend-impl-002"
                        other_result["requestFingerprint"] = file_fingerprint(
                            other_request_path
                        )
                        write_json(other_result_path, other_result)
                        mutate_json(
                            paths["resolved_review"],
                            lambda payload: payload.__setitem__(
                                "resultFingerprint", file_fingerprint(other_result_path)
                            ),
                        )
                        expected_fragments = (
                            "FINDING-001",
                            "resultFingerprint",
                        )

                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        *expected_fragments,
                    )

    def test_finding_ids_are_unique_and_correction_requires_reviewer_closure(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(prefix="chinamate-handoff-finding-duplicate-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_implementation_handoff(root)
            mutate_json(
                paths["open_review"],
                lambda payload: payload["findings"].append(copy.deepcopy(payload["findings"][0])),
            )
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "findingId",
                "FINDING-001",
            )

        with tempfile.TemporaryDirectory(prefix="chinamate-handoff-finding-missing-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_implementation_handoff(root)
            mutate_json(
                paths["correction"],
                lambda payload: payload.__setitem__("findingIds", ["FINDING-404"]),
            )
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "findingIds",
                "FINDING-404",
            )

        with tempfile.TemporaryDirectory(prefix="chinamate-handoff-finding-open-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_implementation_handoff(root)
            paths["resolved_review"].unlink()
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "FINDING-001",
                "RESOLVED",
            )

    def test_only_main_agent_may_be_recorded_as_persistence_actor(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(prefix="chinamate-handoff-writer-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_implementation_handoff(root)
            mutate_json(
                paths["request"],
                lambda payload: payload.__setitem__("persistedBy", "backend_engineer"),
            )
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "persistedBy",
                "main_agent",
            )

    def test_bootstrap_uses_reserved_non_empty_task_id_and_is_immediately_persisted(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(prefix="chinamate-handoff-bootstrap-") as temp_dir:
            root = create_project_root(temp_dir, "future-change")
            paths = create_bootstrap_handoff(root, "future-change")
            self.assertTrue(paths["request"].is_file())
            self.assertTrue(paths["result"].is_file())
            self.assert_status(self.run_validator(root, "future-change"), "PASS")

            mutate_json(paths["request"], lambda payload: payload.__setitem__("taskIds", []))
            mutate_json(paths["result"], lambda payload: payload.__setitem__("taskIds", []))
            self.assert_status(
                self.run_validator(root, "future-change"),
                "FAIL",
                "taskIds",
                BOOTSTRAP_TASK_ID,
            )

    def test_pre_capability_rollout_must_not_retroactively_forge_bootstrap_contracts(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(prefix="chinamate-handoff-pre-capability-") as temp_dir:
            root = create_project_root(temp_dir, PRE_CAPABILITY_CHANGE)
            self.assert_status(self.run_validator(root, PRE_CAPABILITY_CHANGE), "PASS")
            create_bootstrap_handoff(root, PRE_CAPABILITY_CHANGE)
            self.assert_status(
                self.run_validator(root, PRE_CAPABILITY_CHANGE),
                "FAIL",
                "pre-capability",
                "NOT_APPLICABLE",
            )

    def test_control_plane_result_has_qa_and_spec_review_with_correction_closure(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-valid-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_control_plane_handoff(root)
            self.assertTrue(paths["request"].is_file())
            self.assertTrue(paths["result"].is_file())
            self.assertTrue(paths["qa_open"].is_file())
            self.assertTrue(paths["spec_review"].is_file())
            self.assertTrue(paths["correction"].is_file())
            self.assertTrue(paths["qa_resolved"].is_file())
            self.assert_status(self.run_validator(root, "fixture-change"), "PASS")

    def test_control_plane_identity_markers_are_an_indivisible_branch(self) -> None:
        self.require_capability()
        cases = (
            ("stage", "BACKEND_IMPLEMENTATION"),
            ("role", "backend_engineer"),
            ("executionMode", "SUBAGENT"),
        )
        for field, invalid_value in cases:
            with self.subTest(field=field, value=invalid_value):
                with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-identity-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_control_plane_handoff(root)
                    mutate_json(
                        paths["request"],
                        lambda payload, key=field, value=invalid_value: payload.__setitem__(
                            key, value
                        ),
                    )
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        field,
                    )

    def test_control_plane_requires_satisfied_spec_confirmation_with_evidence(self) -> None:
        self.require_capability()
        mutations = (
            lambda payload: payload["userGates"][0].__setitem__("status", "PENDING"),
            lambda payload: payload["userGates"][0].__setitem__("evidenceRefs", []),
        )
        for index, mutation in enumerate(mutations):
            with self.subTest(case=index):
                with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-gate-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_control_plane_handoff(root)
                    mutate_json(paths["request"], mutation)
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        "userGates",
                        "UPDATED_SPEC_CONFIRMATION",
                    )

    def test_control_plane_requires_exact_allowlisted_files(self) -> None:
        self.require_capability()
        invalid_paths = (
            ".codex/",
            "scripts/",
            "docs/",
            "compose.yaml",
            "frontend/src/app/page.tsx",
            "backend/src/main/java/example/Application.java",
        )
        for invalid_path in invalid_paths:
            with self.subTest(path=invalid_path):
                with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-allowlist-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_control_plane_handoff(root)
                    mutate_json(
                        paths["request"],
                        lambda payload, value=invalid_path: payload.__setitem__(
                            "allowedWritePaths", [value]
                        ),
                    )
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        "allowedWritePaths",
                        invalid_path,
                    )

    def test_control_plane_result_identity_and_modified_files_match_request(self) -> None:
        self.require_capability()
        identity_cases = (
            ("contractId", "different-control-contract"),
            ("change", "different-governance-change"),
            ("taskIds", ["9.9"]),
            ("stage", "BACKEND_IMPLEMENTATION"),
            ("role", "backend_engineer"),
        )
        for field, invalid_value in identity_cases:
            with self.subTest(field=field, value=invalid_value):
                with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-result-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_control_plane_handoff(root)
                    mutate_json(
                        paths["result"],
                        lambda payload, key=field, value=invalid_value: payload.__setitem__(
                            key, value
                        ),
                    )
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        field,
                    )

        with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-modified-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_control_plane_handoff(root)
            mutate_json(
                paths["result"],
                lambda payload: payload["modifiedFiles"].append("README.md"),
            )
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "modifiedFiles",
                "README.md",
            )

    def test_control_plane_reviews_keep_specialist_identity_and_exclude_experience_review(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-review-identity-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_control_plane_handoff(root)
            mutate_json(
                paths["qa_open"],
                lambda payload: payload.update(
                    {
                        "stage": CONTROL_PLANE_STAGE,
                        "role": CONTROL_PLANE_ROLE,
                        "reviewRole": CONTROL_PLANE_ROLE,
                    }
                ),
            )
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "stage",
                CONTROL_PLANE_STAGE,
            )

        with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-experience-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_control_plane_handoff(root)
            mutate_json(
                paths["spec_review"],
                lambda payload: payload.update(
                    {
                        "stage": "EXPERIENCE_REVIEW",
                        "role": "experience_reviewer",
                        "reviewRole": "experience_reviewer",
                    }
                ),
            )
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "EXPERIENCE_REVIEW",
                "resultFingerprint",
            )

    def test_main_agent_finding_owner_requires_a_valid_control_plane_result(self) -> None:
        self.require_capability()
        with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-owner-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_implementation_handoff(root)
            mutate_json(
                paths["open_review"],
                lambda payload: payload["findings"][0].__setitem__(
                    "ownerRole", CONTROL_PLANE_ROLE
                ),
            )
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "ownerRole",
                CONTROL_PLANE_ROLE,
            )

    def test_control_plane_correction_preserves_identity_scope_and_original_reviewer_closure(self) -> None:
        self.require_capability()
        mutations = (
            (
                "stage",
                lambda payload: payload.__setitem__("stage", "BACKEND_IMPLEMENTATION"),
            ),
            (
                "role",
                lambda payload: payload.__setitem__("role", "backend_engineer"),
            ),
            (
                "allowedWritePaths",
                lambda payload: payload["allowedWritePaths"].append("README.md"),
            ),
            (
                "findingIds",
                lambda payload: payload.__setitem__("findingIds", ["CONTROL-FINDING-404"]),
            ),
        )
        for field, mutation in mutations:
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-correction-") as temp_dir:
                    root = create_project_root(temp_dir)
                    paths = create_control_plane_handoff(root)
                    mutate_json(paths["correction"], mutation)
                    self.assert_status(
                        self.run_validator(root, "fixture-change"),
                        "FAIL",
                        field,
                    )

        with tempfile.TemporaryDirectory(prefix="chinamate-control-plane-reviewer-") as temp_dir:
            root = create_project_root(temp_dir)
            paths = create_control_plane_handoff(root)
            mutate_json(
                paths["qa_resolved"],
                lambda payload: payload.update(
                    {
                        "stage": "SPEC_REVIEW",
                        "role": "spec_reviewer",
                        "reviewRole": "spec_reviewer",
                    }
                ),
            )
            self.assert_status(
                self.run_validator(root, "fixture-change"),
                "FAIL",
                "CONTROL-FINDING-001",
                "qa_engineer",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
