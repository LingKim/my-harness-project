#!/usr/bin/env python3
"""只读复核 cleanup manifest 中声明的临时资源是否达到期望终态。"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
from pathlib import Path
from typing import Any


SCHEMA = "chinamate-cleanup-manifest/v1"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
TEMP_ROOTS = tuple(Path(item).resolve() for item in ("/tmp", "/private/tmp", "/private/var/folders"))
BRANCH_PATTERN = re.compile(r"codex/[a-z0-9][a-z0-9._/-]*\Z")
DATABASE_PATTERN = re.compile(r"[a-z][a-z0-9_]*_test\Z")
ALLOWED_FIELDS = {
    "path": {"type", "path", "expected"},
    "gitBranch": {"type", "repo", "name", "expected"},
    "gitWorktree": {"type", "repo", "path", "expected"},
    "tcpPort": {"type", "host", "port", "expected"},
    "mysqlDatabase": {"type", "host", "port", "user", "passwordEnv", "name", "expected"},
}
EXPECTED_BY_TYPE = {
    "path": "ABSENT",
    "gitBranch": "ABSENT",
    "gitWorktree": "ABSENT",
    "tcpPort": "CLOSED",
    "mysqlDatabase": "ABSENT",
}


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def validate_temp_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute() or path.resolve() == Path("/"):
        raise ValueError(f"临时路径不安全：{raw_path}")
    if not any(is_within(path, root) for root in TEMP_ROOTS):
        raise ValueError(f"临时路径必须位于系统临时目录：{raw_path}")
    return path


def validate_repo(raw_repo: str, project_root: Path) -> Path:
    repo = Path(raw_repo)
    if not repo.is_absolute():
        repo = project_root / repo
    repo = repo.resolve()
    if not is_within(repo, project_root):
        raise ValueError(f"Git 仓库越出项目根：{raw_repo}")
    return repo


def validate_manifest(manifest: dict[str, Any], project_root: Path) -> list[dict[str, Any]]:
    if set(manifest) != {"schema", "resources"} or manifest.get("schema") != SCHEMA:
        raise ValueError("cleanup manifest schema 或顶层字段不合法")
    resources = manifest.get("resources")
    if not isinstance(resources, list) or not resources:
        raise ValueError("cleanup manifest resources 必须是非空数组")
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(resources):
        if not isinstance(raw, dict):
            raise ValueError(f"resources[{index}] 必须是对象")
        resource_type = raw.get("type")
        if resource_type not in ALLOWED_FIELDS:
            raise ValueError(f"resources[{index}] 类型未登记：{resource_type}")
        if set(raw) != ALLOWED_FIELDS[resource_type]:
            raise ValueError(f"resources[{index}] 字段不合法")
        if raw.get("expected") != EXPECTED_BY_TYPE[resource_type]:
            raise ValueError(f"resources[{index}] expected 不合法")
        item = dict(raw)
        if resource_type == "path":
            item["path"] = str(validate_temp_path(str(raw["path"])))
        elif resource_type == "gitBranch":
            item["repo"] = str(validate_repo(str(raw["repo"]), project_root))
            if not BRANCH_PATTERN.fullmatch(str(raw["name"])):
                raise ValueError(f"resources[{index}] 只允许 codex/ 临时分支")
        elif resource_type == "gitWorktree":
            item["repo"] = str(validate_repo(str(raw["repo"]), project_root))
            item["path"] = str(validate_temp_path(str(raw["path"])))
        elif resource_type == "tcpPort":
            if raw["host"] not in LOOPBACK_HOSTS or not isinstance(raw["port"], int) or not 1 <= raw["port"] <= 65535:
                raise ValueError(f"resources[{index}] 只允许有效回环端口")
        elif resource_type == "mysqlDatabase":
            if raw["host"] not in LOOPBACK_HOSTS or not isinstance(raw["port"], int) or not 1 <= raw["port"] <= 65535:
                raise ValueError(f"resources[{index}] 只允许有效回环 MySQL")
            if raw["passwordEnv"] != "MYSQL_PWD" or not DATABASE_PATTERN.fullmatch(str(raw["name"])):
                raise ValueError(f"resources[{index}] 数据库必须是 *_test 且凭据来自 MYSQL_PWD")
            if not re.fullmatch(r"[a-zA-Z0-9_.-]+", str(raw["user"])):
                raise ValueError(f"resources[{index}] MySQL 用户名不合法")
        normalized.append(item)
    return normalized


def check_path(item: dict[str, Any]) -> tuple[str, str | None]:
    return ("PRESENT" if Path(item["path"]).exists() else "ABSENT", None)


def check_git_branch(item: dict[str, Any]) -> tuple[str, str | None]:
    completed = subprocess.run(
        ["git", "branch", "--list", item["name"]],
        cwd=item["repo"], check=False, capture_output=True, text=True, shell=False,
    )
    if completed.returncode != 0:
        return "UNKNOWN", completed.stderr.strip() or "git branch 检查失败"
    return ("PRESENT" if completed.stdout.strip() else "ABSENT", None)


def check_git_worktree(item: dict[str, Any]) -> tuple[str, str | None]:
    completed = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=item["repo"], check=False, capture_output=True, text=True, shell=False,
    )
    if completed.returncode != 0:
        return "UNKNOWN", completed.stderr.strip() or "git worktree 检查失败"
    registered = {
        line.removeprefix("worktree ").strip()
        for line in completed.stdout.splitlines()
        if line.startswith("worktree ")
    }
    return ("PRESENT" if str(Path(item["path"]).resolve()) in registered else "ABSENT", None)


def check_tcp_port(item: dict[str, Any]) -> tuple[str, str | None]:
    try:
        with socket.create_connection((item["host"], item["port"]), timeout=0.3):
            return "OPEN", None
    except (ConnectionRefusedError, TimeoutError, OSError):
        return "CLOSED", None


def check_mysql_database(item: dict[str, Any]) -> tuple[str, str | None]:
    if not os.environ.get("MYSQL_PWD"):
        return "UNKNOWN", "缺少 MYSQL_PWD 环境变量"
    query = (
        "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
        f"WHERE SCHEMA_NAME='{item['name']}';"
    )
    try:
        completed = subprocess.run(
            [
                "mysql", f"-h{item['host']}", f"-P{item['port']}", f"-u{item['user']}",
                "--batch", "--skip-column-names", "-e", query,
            ],
            check=False, capture_output=True, text=True, shell=False, env=os.environ.copy(),
        )
    except (FileNotFoundError, PermissionError, OSError) as error:
        return "UNKNOWN", type(error).__name__
    if completed.returncode != 0:
        return "UNKNOWN", "MySQL 只读检查失败"
    return ("PRESENT" if completed.stdout.strip() else "ABSENT", None)


CHECKERS = {
    "path": check_path,
    "gitBranch": check_git_branch,
    "gitWorktree": check_git_worktree,
    "tcpPort": check_tcp_port,
    "mysqlDatabase": check_mysql_database,
}


def check_manifest(manifest: dict[str, Any], project_root: Path) -> dict[str, Any]:
    resources = validate_manifest(manifest, project_root.resolve())
    results: list[dict[str, Any]] = []
    for item in resources:
        actual, error = CHECKERS[item["type"]](item)
        result = {
            "type": item["type"],
            "expected": item["expected"],
            "actual": actual,
            "status": "BLOCKED" if actual == "UNKNOWN" else "PASS" if actual == item["expected"] else "FAIL",
        }
        if error:
            result["error"] = error
        results.append(result)
    statuses = [item["status"] for item in results]
    status = "BLOCKED" if "BLOCKED" in statuses else "FAIL" if "FAIL" in statuses else "PASS"
    return {"schema": "chinamate-cleanup-result/v1", "status": status, "resources": results}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = check_manifest(manifest, args.project_root.resolve())
    except (OSError, json.JSONDecodeError, ValueError) as error:
        result = {"schema": "chinamate-cleanup-result/v1", "status": "BLOCKED", "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
