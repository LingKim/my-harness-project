#!/usr/bin/env python3
"""验证固定 profile 采集、脱敏、manifest 和时效检查。"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_SCRIPTS = PROJECT_ROOT / ".codex/skills/chinamate-fullstack-delivery/scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class VerificationCollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.collector = load_module("verification_collector", SKILL_SCRIPTS / "collect_verification.py")
        cls.freshness = load_module(
            "verification_freshness", SKILL_SCRIPTS / "check_verification_freshness.py"
        )

    def test_run_commands_preserves_each_exit_code_and_redacts_secrets(self) -> None:
        commands = [
            {
                "name": "success",
                "argv": [sys.executable, "-c", "print('ok token=secret-value')"],
            },
            {
                "name": "failure",
                "argv": [sys.executable, "-c", "import sys; print('bad'); sys.exit(7)"],
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            results = self.collector.run_commands(commands, Path(temp_dir))
        self.assertEqual([0, 7], [item["exitCode"] for item in results])
        self.assertEqual(["PASS", "FAIL"], [item["status"] for item in results])
        self.assertNotIn("secret-value", results[0]["summary"])
        self.assertIn("[REDACTED]", results[0]["summary"])

    def test_unknown_profile_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "未登记的验证 profile"):
            self.collector.resolve_profile("arbitrary-shell")

    def test_approved_profiles_do_not_use_shell_or_forbidden_commands(self) -> None:
        for profile_name in self.collector.PROFILES:
            commands = self.collector.resolve_profile(profile_name, "fixture-change")
            for command in commands:
                self.assertIsInstance(command["argv"], list)
                self.assertNotIn(command["argv"][0], {"rm", "curl", "wget"})
                if command["argv"][0] == "git":
                    self.assertEqual(["git", "diff", "--check"], command["argv"])
                joined = " ".join(command["argv"])
                self.assertNotIn(" build", joined)

    def test_manifest_round_trip_and_freshness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.txt"
            source.write_text("v1", encoding="utf-8")
            manifest_path = root / "manifest.json"
            manifest = self.collector.build_manifest(
                profile="fixture",
                repo_root=root,
                commands=[],
                input_paths=[source],
            )
            self.collector.write_manifest(manifest, manifest_path)
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual("chinamate-verification-manifest/v1", loaded["schema"])
            self.assertEqual("FRESH", self.freshness.check_manifest(manifest_path, root)["status"])
            source.write_text("v2", encoding="utf-8")
            result = self.freshness.check_manifest(manifest_path, root)
            self.assertEqual("STALE", result["status"])
            self.assertIn("source.txt", result["changedInputs"])

    def test_application_profiles_only_fingerprint_their_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "frontend").mkdir()
            (root / "backend").mkdir()
            frontend = self.collector.build_manifest("frontend-static", root, [], [])
            backend = self.collector.build_manifest("backend-test", root, [], [])
            self.assertEqual({"frontend"}, set(frontend["repositories"]))
            self.assertEqual({"backend"}, set(backend["repositories"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
