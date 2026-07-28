#!/usr/bin/env python3
"""验证单人全栈 AI 交付治理结构与轻量知识地图。"""

from __future__ import annotations

import hashlib
import json
import re
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
    "scripts/collect_verification.py",
    "scripts/check_verification_freshness.py",
    "scripts/check_delivery_environment.py",
    "scripts/check_delivery_cleanup.py",
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


class AiDeliveryGovernanceTests(unittest.TestCase):
    def test_skill_contains_required_resources(self) -> None:
        missing = [name for name in REQUIRED_SKILL_FILES if not (SKILL_ROOT / name).is_file()]
        self.assertEqual([], missing, f"编排 Skill 缺少资源：{missing}")

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
