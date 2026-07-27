#!/usr/bin/env python3
"""验证全栈演练的环境预检、边界证据与零残留检查合同。"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = PROJECT_ROOT / ".codex/skills/chinamate-fullstack-delivery"
SKILL_SCRIPTS = SKILL_ROOT / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class DeliverySafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.environment = load_module(
            "delivery_environment", SKILL_SCRIPTS / "check_delivery_environment.py"
        )
        cls.cleanup = load_module(
            "delivery_cleanup", SKILL_SCRIPTS / "check_delivery_cleanup.py"
        )

    def test_external_node_modules_symlink_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            frontend = root / "worktree/frontend"
            external_modules = root / "original/frontend/node_modules"
            frontend.mkdir(parents=True)
            external_modules.mkdir(parents=True)
            (frontend / "node_modules").symlink_to(external_modules, target_is_directory=True)

            result = self.environment.check_frontend_dependencies(frontend)

        self.assertEqual("BLOCKED", result["status"])
        self.assertEqual("EXTERNAL_NODE_MODULES_SYMLINK", result["code"])
        self.assertIn("pnpm install --offline", result["recovery"])

    def test_java21_mockito_without_agent_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = Path(temp_dir)
            test_source = backend / "src/test/java/example/SampleTests.java"
            test_source.parent.mkdir(parents=True)
            test_source.write_text("import org.mockito.Mockito;", encoding="utf-8")
            (backend / "pom.xml").write_text("<project/>", encoding="utf-8")

            result = self.environment.check_backend_test_runtime(
                backend, 'openjdk version "21.0.8"'
            )

        self.assertEqual("REVIEW_REQUIRED", result["status"])
        self.assertEqual("MOCKITO_AGENT_REVIEW", result["code"])
        self.assertIn("最小 Mockito 测试", result["recovery"])

    def test_pagination_guidance_requires_boundary_fixture(self) -> None:
        text = (SKILL_ROOT / "references/verification-profiles.md").read_text(encoding="utf-8")
        self.assertIn("pageSize + 1", text)
        self.assertIn("单条 CRUD smoke test", text)
        self.assertIn("stable tie-breaker", text)

    def test_cleanup_manifest_rejects_commands_and_unsafe_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            unsafe_manifests = [
                {
                    "schema": "chinamate-cleanup-manifest/v1",
                    "resources": [{"type": "path", "path": "/", "expected": "ABSENT"}],
                },
                {
                    "schema": "chinamate-cleanup-manifest/v1",
                    "resources": [{"type": "tcpPort", "host": "0.0.0.0", "port": 8080, "expected": "CLOSED"}],
                },
                {
                    "schema": "chinamate-cleanup-manifest/v1",
                    "resources": [{"type": "path", "path": "/private/tmp/x", "expected": "ABSENT", "command": "rm -rf /"}],
                },
                {
                    "schema": "chinamate-cleanup-manifest/v1",
                    "resources": [{"type": "mysqlDatabase", "host": "127.0.0.1", "port": 3306, "user": "root", "passwordEnv": "MYSQL_PWD", "name": "heness", "expected": "ABSENT"}],
                },
            ]
            for manifest in unsafe_manifests:
                with self.subTest(manifest=manifest):
                    with self.assertRaises(ValueError):
                        self.cleanup.validate_manifest(manifest, root)

    def test_cleanup_checker_reports_absent_path_closed_port_and_database(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            missing = Path("/private/tmp/chinamate-cleanup-fixture-missing")
            manifest = {
                "schema": "chinamate-cleanup-manifest/v1",
                "resources": [
                    {"type": "path", "path": str(missing), "expected": "ABSENT"},
                    {"type": "tcpPort", "host": "127.0.0.1", "port": 9, "expected": "CLOSED"},
                    {"type": "mysqlDatabase", "host": "127.0.0.1", "port": 3306, "user": "root", "passwordEnv": "MYSQL_PWD", "name": "heness_fixture_test", "expected": "ABSENT"},
                ],
            }
            completed = type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            with patch.dict("os.environ", {"MYSQL_PWD": "fixture-secret"}, clear=False), patch.object(
                self.cleanup.subprocess, "run", return_value=completed
            ) as run:
                result = self.cleanup.check_manifest(manifest, root)

        self.assertEqual("PASS", result["status"])
        self.assertEqual(["ABSENT", "CLOSED", "ABSENT"], [item["actual"] for item in result["resources"]])
        command = run.call_args.args[0]
        self.assertNotIn("fixture-secret", " ".join(command))
        self.assertNotIn("password", json.dumps(result).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
