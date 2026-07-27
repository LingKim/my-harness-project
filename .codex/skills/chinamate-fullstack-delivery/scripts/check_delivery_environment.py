#!/usr/bin/env python3
"""只读检查临时全栈交付环境中的已知兼容性风险。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


MOCKITO_MARKERS = ("org.mockito", "MockitoBean", "MockitoExtension")
STATUS_PRIORITY = {"PASS": 0, "NOT_APPLICABLE": 0, "REVIEW_REQUIRED": 1, "BLOCKED": 2}


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def check_frontend_dependencies(frontend: Path) -> dict[str, Any]:
    node_modules = frontend / "node_modules"
    if not frontend.exists():
        return {"name": "frontendDependencies", "status": "NOT_APPLICABLE", "code": "FRONTEND_MISSING"}
    if not node_modules.exists() and not node_modules.is_symlink():
        return {
            "name": "frontendDependencies",
            "status": "REVIEW_REQUIRED",
            "code": "NODE_MODULES_MISSING",
            "recovery": "在当前 worktree 使用 pnpm store 执行 pnpm install --offline；需要联网时另行申请授权。",
        }
    if node_modules.is_symlink():
        target = node_modules.resolve(strict=False)
        if not is_within(target, frontend):
            return {
                "name": "frontendDependencies",
                "status": "BLOCKED",
                "code": "EXTERNAL_NODE_MODULES_SYMLINK",
                "target": str(target),
                "recovery": "删除该临时软链接后，在当前 worktree 使用 pnpm install --offline；仅在已验证时使用 webpack fallback。",
            }
    return {"name": "frontendDependencies", "status": "PASS", "code": "DEPENDENCIES_LOCAL"}


def java_major(version_output: str) -> int | None:
    match = re.search(r'version\s+"(?P<major>\d+)(?:\.|\")', version_output)
    if not match:
        match = re.search(r"\b(?P<major>\d+)(?:\.\d+)+", version_output)
    return int(match.group("major")) if match else None


def backend_uses_mockito(backend: Path) -> bool:
    test_root = backend / "src/test"
    if not test_root.exists():
        return False
    for path in test_root.rglob("*"):
        if path.is_file() and path.suffix in {".java", ".kt", ".groovy"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if any(marker in text for marker in MOCKITO_MARKERS):
                return True
    return False


def has_explicit_test_agent(backend: Path) -> bool:
    pom = backend / "pom.xml"
    if not pom.is_file():
        return False
    return "-javaagent" in pom.read_text(encoding="utf-8", errors="ignore")


def check_backend_test_runtime(backend: Path, java_version_output: str) -> dict[str, Any]:
    if not backend.exists():
        return {"name": "backendTestRuntime", "status": "NOT_APPLICABLE", "code": "BACKEND_MISSING"}
    major = java_major(java_version_output)
    if major is None:
        return {
            "name": "backendTestRuntime",
            "status": "REVIEW_REQUIRED",
            "code": "JAVA_VERSION_UNKNOWN",
            "recovery": "先运行 java -version 并记录真实 JDK，再执行后端测试。",
        }
    if major >= 21 and backend_uses_mockito(backend) and not has_explicit_test_agent(backend):
        return {
            "name": "backendTestRuntime",
            "status": "REVIEW_REQUIRED",
            "code": "MOCKITO_AGENT_REVIEW",
            "javaMajor": major,
            "recovery": "先运行最小 Mockito 测试；若动态 attach 失败，记录为环境阻塞或采用项目级 surefire -javaagent 配置。",
        }
    return {
        "name": "backendTestRuntime",
        "status": "PASS",
        "code": "TEST_RUNTIME_READY",
        "javaMajor": major,
    }


def read_java_version() -> str:
    try:
        completed = subprocess.run(
            ["java", "-version"], check=False, capture_output=True, text=True, shell=False
        )
    except (FileNotFoundError, PermissionError, OSError) as error:
        return str(error)
    return "\n".join(part for part in (completed.stdout, completed.stderr) if part)


def check_environment(repo_root: Path, version_output: str | None = None) -> dict[str, Any]:
    checks = [
        check_frontend_dependencies(repo_root / "frontend"),
        check_backend_test_runtime(repo_root / "backend", version_output or read_java_version()),
    ]
    status = max((item["status"] for item in checks), key=lambda item: STATUS_PRIORITY[item])
    return {"schema": "chinamate-delivery-environment/v1", "status": status, "checks": checks}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> int:
    result = check_environment(parse_args().repo_root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"PASS": 0, "NOT_APPLICABLE": 0, "REVIEW_REQUIRED": 3, "BLOCKED": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
