#!/usr/bin/env python3
"""验证单人全栈 AI 交付治理结构与轻量知识地图。"""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = PROJECT_ROOT / ".codex/skills/chinamate-fullstack-delivery"
CONTROL_TYPES = {"SCRIPT", "TEST", "REVIEW", "MAIN_AGENT", "USER_CONFIRMATION"}
REQUIRED_SKILL_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/stage-routing.md",
    "references/control-matrix.md",
    "references/knowledge-routing.md",
    "references/verification-profiles.md",
    "references/handoff-contracts.md",
    "references/role-routing.md",
    "schemas/common.schema.json",
    "schemas/task-contract.schema.json",
    "schemas/result-contract.schema.json",
    "schemas/review-result.schema.json",
    "schemas/correction-contract.schema.json",
    "scripts/collect_verification.py",
    "scripts/check_verification_freshness.py",
    "scripts/check_delivery_environment.py",
    "scripts/check_delivery_cleanup.py",
    "scripts/validate_handoff_contract.py",
)
BLOCKER_ESCALATION_RULE_ID = "RULE-WF-006"
DELEGATED_STAGE_ROLES = {
    "PRODUCT_SPEC": "product_manager",
    "INTERACTION_DESIGN": "interaction_designer",
    "FRONTEND_IMPLEMENTATION": "frontend_engineer",
    "BACKEND_IMPLEMENTATION": "backend_engineer",
    "QA": "qa_engineer",
    "SPEC_REVIEW": "spec_reviewer",
    "EXPERIENCE_REVIEW": "experience_reviewer",
}
EXPECTED_CUSTOM_AGENTS = frozenset(DELEGATED_STAGE_ROLES.values())
HANDOFF_RESOURCE_PATHS = tuple(
    f".codex/skills/chinamate-fullstack-delivery/{path}"
    for path in REQUIRED_SKILL_FILES
    if path.startswith(("references/handoff", "references/role-routing", "schemas/", "scripts/validate_handoff"))
)


def project_skill_hash(skill_root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in skill_root.rglob("*") if item.is_file()):
        relative = path.relative_to(skill_root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def parse_markdown_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or re.fullmatch(r"[| :\-]+", line):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def parse_markdown_table(path: Path, expected_header: list[str]) -> list[list[str]]:
    """只返回指定表头所属表，避免独立控制面表污染 specialist 路由集合。"""
    table: list[list[str]] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            if in_table:
                break
            continue
        if re.fullmatch(r"[| :\-]+", line):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not in_table:
            if cells != expected_header:
                continue
            in_table = True
        table.append(cells)
    return table


def validate_blocker_escalation_contract(project_root: Path) -> list[str]:
    """使用稳定 Rule ID 校验阻塞即时升级合同的三个治理入口。"""
    errors: list[str] = []
    agents_text = (project_root / "AGENTS.md").read_text(encoding="utf-8")
    workflow_text = (project_root / ".codex/rules/workflow.md").read_text(encoding="utf-8")
    matrix_text = (
        project_root
        / ".codex/skills/chinamate-fullstack-delivery/references/control-matrix.md"
    ).read_text(encoding="utf-8")

    if BLOCKER_ESCALATION_RULE_ID not in agents_text:
        errors.append(f"根 AGENTS.md 缺少 {BLOCKER_ESCALATION_RULE_ID} 入口")
    if not re.search(
        rf"^##\s+{re.escape(BLOCKER_ESCALATION_RULE_ID)}(?:：|:)",
        workflow_text,
        re.MULTILINE,
    ):
        errors.append(f"workflow.md 缺少 {BLOCKER_ESCALATION_RULE_ID} 定义")
    if not re.search(
        rf"^\|\s*{re.escape(BLOCKER_ESCALATION_RULE_ID)}\s*\|",
        matrix_text,
        re.MULTILINE,
    ):
        errors.append(f"控制矩阵缺少 {BLOCKER_ESCALATION_RULE_ID} 登记")
    return errors


class AiDeliveryGovernanceTests(unittest.TestCase):
    def test_blocker_escalation_contract_is_registered(self) -> None:
        self.assertEqual([], validate_blocker_escalation_contract(PROJECT_ROOT))

    def test_blocker_escalation_contract_failure_fixtures(self) -> None:
        with tempfile.TemporaryDirectory(prefix="chinamate-blocker-governance-") as temp_dir:
            fixture_root = Path(temp_dir)
            agents_path = fixture_root / "AGENTS.md"
            workflow_path = fixture_root / ".codex/rules/workflow.md"
            matrix_path = (
                fixture_root
                / ".codex/skills/chinamate-fullstack-delivery/references/control-matrix.md"
            )
            workflow_path.parent.mkdir(parents=True)
            matrix_path.parent.mkdir(parents=True)

            valid_contents = {
                agents_path: f"- 遵循 `{BLOCKER_ESCALATION_RULE_ID}`。\n",
                workflow_path: f"## {BLOCKER_ESCALATION_RULE_ID}：阻塞即时升级\n",
                matrix_path: f"| {BLOCKER_ESCALATION_RULE_ID} | 三仓库 |\n",
            }
            expected_errors = {
                agents_path: f"根 AGENTS.md 缺少 {BLOCKER_ESCALATION_RULE_ID} 入口",
                workflow_path: f"workflow.md 缺少 {BLOCKER_ESCALATION_RULE_ID} 定义",
                matrix_path: f"控制矩阵缺少 {BLOCKER_ESCALATION_RULE_ID} 登记",
            }

            for path, content in valid_contents.items():
                path.write_text(content, encoding="utf-8")
            self.assertEqual([], validate_blocker_escalation_contract(fixture_root))

            for missing_path, expected_error in expected_errors.items():
                for path, content in valid_contents.items():
                    path.write_text(content, encoding="utf-8")
                missing_path.write_text("", encoding="utf-8")
                self.assertIn(
                    expected_error,
                    validate_blocker_escalation_contract(fixture_root),
                )

    def test_skill_contains_required_resources(self) -> None:
        missing = [name for name in REQUIRED_SKILL_FILES if not (SKILL_ROOT / name).is_file()]
        self.assertEqual([], missing, f"编排 Skill 缺少资源：{missing}")

    def test_role_routing_has_exactly_seven_specialists_and_main_agent_control_state(self) -> None:
        path = SKILL_ROOT / "references/role-routing.md"
        self.assertTrue(path.is_file(), "缺少角色路由矩阵：references/role-routing.md")
        expected_header = [
            "任务类型",
            "stage",
            "role",
            "进入条件",
            "退出条件",
            "默认 executionMode",
            "允许并行对象",
            "写入根",
        ]
        rows = parse_markdown_table(path, expected_header)
        self.assertTrue(rows, "角色路由矩阵不得为空")
        header, *entries = rows
        self.assertEqual(expected_header, header)
        self.assertTrue(all(len(row) == 8 for row in entries), entries)
        by_stage = {row[1].strip("`"): row for row in entries}
        self.assertEqual(set(DELEGATED_STAGE_ROLES) | {"EVIDENCE_AND_ARCHIVE"}, set(by_stage))
        for stage, role in DELEGATED_STAGE_ROLES.items():
            row = by_stage[stage]
            self.assertEqual(role, row[2].strip("`"), row)
            self.assertTrue(row[3] and row[4] and row[7], row)
            self.assertIn(row[5].strip("`"), {"SUBAGENT", "SINGLE_AGENT_FAST_PATH", "DEGRADED"})

        control_row = by_stage["EVIDENCE_AND_ARCHIVE"]
        self.assertEqual("MAIN_AGENT", control_row[2].strip("`"))
        self.assertIn("不签发", " ".join(control_row))
        self.assertNotIn("EVIDENCE_AND_ARCHIVE", DELEGATED_STAGE_ROLES)
        self.assertNotIn("main_agent", DELEGATED_STAGE_ROLES.values())

        self.assertIn("BACKEND_IMPLEMENTATION", by_stage["FRONTEND_IMPLEMENTATION"][6])
        self.assertIn("FRONTEND_IMPLEMENTATION", by_stage["BACKEND_IMPLEMENTATION"][6])
        self.assertNotIn("IMPLEMENTATION", by_stage["QA"][6])
        self.assertIn("稳定", by_stage["QA"][3])
        self.assertIn("EXPERIENCE_REVIEW", by_stage["SPEC_REVIEW"][6])
        self.assertIn("SPEC_REVIEW", by_stage["EXPERIENCE_REVIEW"][6])

    def test_control_plane_self_hosting_is_not_an_eighth_custom_agent(self) -> None:
        agent_files = {
            path.stem for path in (PROJECT_ROOT / ".codex/agents").glob("*.toml")
        }
        self.assertEqual(EXPECTED_CUSTOM_AGENTS, agent_files)

        manifest = json.loads((PROJECT_ROOT / ".codex/manifest.json").read_text(encoding="utf-8"))
        manifest_agents = {item["name"] for item in manifest.get("customAgents", [])}
        self.assertEqual(EXPECTED_CUSTOM_AGENTS, manifest_agents)
        self.assertNotIn("main_agent", manifest_agents)

        routing_path = SKILL_ROOT / "references/role-routing.md"
        routing_text = routing_path.read_text(encoding="utf-8")
        control_rows = [
            row
            for row in parse_markdown_rows(routing_path)
            if "CONTROL_PLANE_IMPLEMENTATION" in row
        ]
        self.assertEqual(1, len(control_rows), "控制面必须在独立表中恰好登记一次")
        control_row = " ".join(control_rows[0])
        for marker in (
            "CONTROL_PLANE_IMPLEMENTATION",
            "main_agent",
            "CONTROL_PLANE",
            "SATISFIED",
            "精确",
        ):
            self.assertIn(marker, control_row)

        specialist_rows = parse_markdown_table(
            routing_path,
            [
                "任务类型",
                "stage",
                "role",
                "进入条件",
                "退出条件",
                "默认 executionMode",
                "允许并行对象",
                "写入根",
            ],
        )
        self.assertNotIn("CONTROL_PLANE_IMPLEMENTATION", " ".join(map(" ".join, specialist_rows)))

    def test_control_plane_governance_requires_real_result_qa_and_spec_review_chain(self) -> None:
        texts = {
            "Skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "role routing": (SKILL_ROOT / "references/role-routing.md").read_text(
                encoding="utf-8"
            ),
            "stage routing": (SKILL_ROOT / "references/stage-routing.md").read_text(
                encoding="utf-8"
            ),
            "根 README": (PROJECT_ROOT / "README.md").read_text(encoding="utf-8"),
        }
        for source, content in texts.items():
            with self.subTest(source=source):
                for marker in (
                    "CONTROL_PLANE_IMPLEMENTATION",
                    "main_agent",
                    "CONTROL_PLANE",
                    "QA",
                    "SPEC_REVIEW",
                ):
                    self.assertIn(marker, content)

        combined = "\n".join(texts.values())
        self.assertIn("resultFingerprint", combined)
        self.assertIn("EXPERIENCE_REVIEW", combined)
        self.assertRegex(combined, r"精确(?:文件|路径|allowlist)")

    def test_handoff_resources_are_referenced_by_all_governance_entrypoints(self) -> None:
        texts = {
            "Skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "workflow Rule": (PROJECT_ROOT / ".codex/rules/workflow.md").read_text(encoding="utf-8"),
            "根 README": (PROJECT_ROOT / "README.md").read_text(encoding="utf-8"),
            "Agents README": (PROJECT_ROOT / ".codex/agents/README.md").read_text(encoding="utf-8"),
        }
        for source, content in texts.items():
            with self.subTest(source=source):
                self.assertIn("TaskContract", content)
                self.assertRegex(content, r"fresh\s+subagent")

        skill_text = texts["Skill"]
        for marker in (
            "references/handoff-contracts.md",
            "references/role-routing.md",
            "scripts/validate_handoff_contract.py",
            "BOOTSTRAP-PRODUCT-SPEC",
            "EVIDENCE_AND_ARCHIVE",
        ):
            self.assertIn(marker, skill_text)

        manifest_text = (PROJECT_ROOT / ".codex/manifest.json").read_text(encoding="utf-8")
        lock_text = (PROJECT_ROOT / ".codex/skills-lock.json").read_text(encoding="utf-8")
        required_files_text = (PROJECT_ROOT / "scripts/check-agent-governance.sh").read_text(
            encoding="utf-8"
        )
        for resource in HANDOFF_RESOURCE_PATHS:
            with self.subTest(resource=resource):
                self.assertIn(resource, manifest_text)
                self.assertIn(resource, lock_text)
                self.assertIn(resource, required_files_text)

    def test_stage_and_control_references_define_parallel_and_control_boundaries(self) -> None:
        stage_text = (SKILL_ROOT / "references/stage-routing.md").read_text(encoding="utf-8")
        control_text = (SKILL_ROOT / "references/control-matrix.md").read_text(encoding="utf-8")
        for marker in (
            "TaskContract",
            "FRONTEND_IMPLEMENTATION",
            "BACKEND_IMPLEMENTATION",
            "QA",
            "SPEC_REVIEW",
            "EXPERIENCE_REVIEW",
            "EVIDENCE_AND_ARCHIVE",
        ):
            self.assertIn(marker, stage_text)
        self.assertIn("主 Agent", control_text)
        self.assertIn("唯一签发", control_text)
        self.assertIn("唯一验收", control_text)

    def test_manifest_and_lock_register_first_party_skill(self) -> None:
        manifest = json.loads((PROJECT_ROOT / ".codex/manifest.json").read_text(encoding="utf-8"))
        project_skills = {item["name"]: item for item in manifest.get("projectSkills", [])}
        self.assertIn("chinamate-fullstack-delivery", project_skills)
        self.assertEqual(
            ".codex/skills/chinamate-fullstack-delivery/SKILL.md",
            project_skills["chinamate-fullstack-delivery"]["path"],
        )

        lock = json.loads((PROJECT_ROOT / ".codex/skills-lock.json").read_text(encoding="utf-8"))
        entry = lock["projectSkills"]["chinamate-fullstack-delivery"]
        self.assertEqual("project", entry["sourceType"])
        self.assertEqual(project_skill_hash(SKILL_ROOT), entry["computedHash"])
        self.assertEqual(project_skill_hash(SKILL_ROOT), entry["contentHash"])

    def test_java_skill_is_first_party_and_hash_locked(self) -> None:
        java_skill_root = PROJECT_ROOT / ".codex/skills/java-springboot"
        manifest = json.loads((PROJECT_ROOT / ".codex/manifest.json").read_text(encoding="utf-8"))
        project_skills = {item["name"]: item for item in manifest.get("projectSkills", [])}
        self.assertIn("java-springboot", project_skills)
        self.assertEqual(
            ".codex/skills/java-springboot/SKILL.md",
            project_skills["java-springboot"]["path"],
        )
        self.assertEqual("project-maintained", project_skills["java-springboot"]["source"])

        lock = json.loads((PROJECT_ROOT / ".codex/skills-lock.json").read_text(encoding="utf-8"))
        self.assertNotIn("java-springboot", lock.get("skills", {}))
        entry = lock["projectSkills"]["java-springboot"]
        self.assertEqual("project", entry["sourceType"])
        self.assertEqual("ChinaMate project", entry["source"])
        self.assertEqual(project_skill_hash(java_skill_root), entry["computedHash"])
        self.assertEqual(project_skill_hash(java_skill_root), entry["contentHash"])

    def test_custom_mybatis_sql_requires_mapper_xml(self) -> None:
        database_rules = (PROJECT_ROOT / ".codex/rules/database-conventions.md").read_text(
            encoding="utf-8"
        )
        java_skill = (PROJECT_ROOT / ".codex/skills/java-springboot/SKILL.md").read_text(
            encoding="utf-8"
        )
        combined = "\n".join((database_rules, java_skill))

        self.assertIn("新增或实质修改的自定义 SQL 必须使用 Mapper XML", database_rules)
        self.assertIn("SQL 注解和 Provider 注解", database_rules)
        self.assertIn("`BaseMapper<T>` 自动 CRUD", database_rules)
        self.assertIn("自定义 SQL 必须写入 Mapper XML", java_skill)
        self.assertIn("`BaseMapper<T>` 自动 CRUD", java_skill)
        self.assertNotIn("XML 或注解 SQL", combined)

    def test_control_matrix_references_real_unique_rules(self) -> None:
        rule_ids = set(
            re.findall(
                r"RULE-[A-Z]+-\d{3}",
                "\n".join(
                    path.read_text(encoding="utf-8")
                    for path in (PROJECT_ROOT / ".codex/rules").glob("*.md")
                ),
            )
        )
        rows = parse_markdown_rows(SKILL_ROOT / "references/control-matrix.md")
        header, *entries = rows
        self.assertEqual(
            ["Rule ID", "作用域", "风险", "主要责任", "控制类型", "执行入口", "阻断条件", "证据位置"],
            header,
        )
        seen: set[str] = set()
        for row in entries:
            self.assertEqual(8, len(row), row)
            rule_id, _, risk, owner, control_type, entrypoint, blocking, evidence = row
            self.assertIn(rule_id, rule_ids)
            self.assertNotIn(rule_id, seen)
            seen.add(rule_id)
            if risk == "CRITICAL":
                self.assertTrue(owner and control_type and entrypoint and blocking and evidence)
                self.assertIn(control_type, CONTROL_TYPES)
        self.assertTrue(seen, "控制矩阵不得为空")

    def test_current_system_map_paths_exist_and_planned_paths_may_not(self) -> None:
        rows = [
            row
            for row in parse_markdown_rows(PROJECT_ROOT / "docs/architecture/system-map.md")
            if len(row) == 4 and row[0] in {"状态", "CURRENT", "PLANNED"}
        ]
        header, *entries = rows
        self.assertEqual(["状态", "能力", "路径", "说明"], header)
        for status, _, raw_path, _ in entries:
            self.assertIn(status, {"CURRENT", "PLANNED"})
            if status == "CURRENT":
                path = raw_path.strip("`")
                self.assertTrue((PROJECT_ROOT / path).exists(), f"CURRENT 路径不存在：{path}")

    def test_central_governance_ownership_is_not_contradicted(self) -> None:
        text = (PROJECT_ROOT / ".codex/rules/repository-boundaries.md").read_text(encoding="utf-8")
        self.assertIn("根 `.codex/` 集中拥有", text)
        self.assertNotIn("技术 Rules 与 Skills 跟随对应 submodule", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
