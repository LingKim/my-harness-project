#!/usr/bin/env python3
"""运行固定验证 profile，并生成精简、可复核的机器清单。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "chinamate-verification-manifest/v1"
SUMMARY_LIMIT = 1600
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*)([^\s,;]+)"),
    re.compile(r"(?i)((?:api[_-]?key|token|cookie|password|secret)\s*[:=]\s*)([^\s,;]+)"),
)

PROFILES: dict[str, list[dict[str, Any]]] = {
    "root-governance": [
        {"name": "agent-governance", "argv": ["./scripts/check-agent-governance.sh"]},
        {"name": "harness", "argv": ["./scripts/check-harness.sh"]},
        {
            "name": "openspec-strict",
            "argv": ["openspec", "validate", "{change}", "--strict"],
        },
        {"name": "diff-check", "argv": ["git", "diff", "--check"]},
    ],
    "frontend-static": [
        {"name": "frontend-lint", "cwd": "frontend", "argv": ["pnpm", "lint"]},
        {"name": "frontend-typecheck", "cwd": "frontend", "argv": ["pnpm", "typecheck"]},
        {"name": "frontend-test", "cwd": "frontend", "argv": ["pnpm", "test"]},
    ],
    "frontend-e2e": [
        {"name": "frontend-e2e", "cwd": "frontend", "argv": ["pnpm", "test:e2e"]},
    ],
    "backend-architecture": [
        {
            "name": "backend-architecture",
            "cwd": "backend",
            "argv": ["./mvnw", "-Dtest=ArchitectureRulesTests", "test"],
        }
    ],
    "backend-test": [
        {"name": "backend-test", "cwd": "backend", "argv": ["./mvnw", "test"]},
    ],
    "fullstack-governance": [
        {"name": "agent-governance", "argv": ["./scripts/check-agent-governance.sh"]},
        {"name": "harness", "argv": ["./scripts/check-harness.sh"]},
        {
            "name": "frontend-governance",
            "cwd": "frontend",
            "argv": ["./scripts/check-agent-governance.sh"],
        },
        {
            "name": "backend-governance",
            "cwd": "backend",
            "argv": ["./scripts/check-agent-governance.sh"],
        },
    ],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def redact(text: str) -> str:
    result = text
    for pattern in SENSITIVE_PATTERNS:
        result = pattern.sub(r"\1[REDACTED]", result)
    if len(result) > SUMMARY_LIMIT:
        result = result[-SUMMARY_LIMIT:]
    return result.strip()


def resolve_profile(name: str, change: str | None = None) -> list[dict[str, Any]]:
    if name not in PROFILES:
        raise ValueError(f"未登记的验证 profile：{name}")
    resolved: list[dict[str, Any]] = []
    for command in PROFILES[name]:
        item = {**command, "argv": list(command["argv"])}
        if any("{change}" in value for value in item["argv"]):
            if not change:
                raise ValueError(f"验证 profile {name} 需要 --change")
            item["argv"] = [value.replace("{change}", change) for value in item["argv"]]
        resolved.append(item)
    return resolved


def run_commands(commands: list[dict[str, Any]], repo_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for command in commands:
        argv = command.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(v, str) for v in argv):
            raise ValueError("验证命令必须是非空参数数组")
        cwd = repo_root / command.get("cwd", ".")
        started_at = now_iso()
        try:
            completed = subprocess.run(
                argv,
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
                shell=False,
            )
            output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
            exit_code: int | None = completed.returncode
            status = "PASS" if completed.returncode == 0 else "FAIL"
            summary = redact(output)
        except (FileNotFoundError, PermissionError, OSError) as error:
            exit_code = None
            status = "BLOCKED"
            summary = redact(str(error))
        results.append(
            {
                "name": command["name"],
                "cwd": command.get("cwd", "."),
                "argv": argv,
                "command": " ".join(argv),
                "startedAt": started_at,
                "finishedAt": now_iso(),
                "exitCode": exit_code,
                "status": status,
                "summary": summary,
            }
        )
    return results


def hash_path(path: Path) -> str:
    digest = hashlib.sha256()
    if not path.exists():
        return "MISSING"
    if path.is_file():
        digest.update(path.read_bytes())
        return digest.hexdigest()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(child.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def relative_name(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def fingerprint_inputs(paths: list[Path], repo_root: Path) -> list[dict[str, str]]:
    unique = {path.resolve(): path for path in paths}
    return [
        {"path": relative_name(path, repo_root), "sha256": hash_path(path)}
        for path in sorted(unique.values(), key=lambda item: str(item))
    ]


def git_head(path: Path) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, check=False, capture_output=True, text=True
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def git_diff_hash(path: Path) -> str | None:
    completed = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--binary", "HEAD"],
        cwd=path,
        check=False,
        capture_output=True,
    )
    return hashlib.sha256(completed.stdout).hexdigest() if completed.returncode == 0 else None


def repository_states(profile: str, repo_root: Path) -> dict[str, dict[str, str | None]]:
    states: dict[str, dict[str, str | None]] = {}
    if profile in {"root-governance", "fullstack-governance"}:
        repositories = (("root", repo_root), ("frontend", repo_root / "frontend"), ("backend", repo_root / "backend"))
    elif profile.startswith("frontend"):
        repositories = (("frontend", repo_root / "frontend"),)
    elif profile.startswith("backend"):
        repositories = (("backend", repo_root / "backend"),)
    else:
        repositories = (("root", repo_root),)
    for name, path in repositories:
        if path.exists():
            states[name] = {"head": git_head(path), "diffSha256": git_diff_hash(path)}
    return states


def build_manifest(
    profile: str,
    repo_root: Path,
    commands: list[dict[str, Any]],
    input_paths: list[Path],
) -> dict[str, Any]:
    statuses = [item.get("status") for item in commands]
    overall = "BLOCKED" if "BLOCKED" in statuses else "FAIL" if "FAIL" in statuses else "PASS"
    return {
        "schema": SCHEMA,
        "profile": profile,
        "createdAt": now_iso(),
        "status": overall,
        "commands": commands,
        "inputs": fingerprint_inputs(input_paths, repo_root),
        "repositories": repository_states(profile, repo_root),
    }


def write_manifest(manifest: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def profile_inputs(profile: str, repo_root: Path, change: str | None) -> list[Path]:
    paths: list[Path] = []
    if change:
        change_root = repo_root / "openspec/changes" / change
        paths.extend(
            [change_root / "proposal.md", change_root / "design.md", change_root / "tasks.md", change_root / "specs"]
        )
    if profile in {"root-governance", "fullstack-governance"}:
        paths.extend(
            [
                repo_root / "AGENTS.md",
                repo_root / "README.md",
                repo_root / ".codex/agents",
                repo_root / ".codex/rules",
                repo_root / ".codex/manifest.json",
                repo_root / ".codex/skills-lock.json",
                repo_root / ".codex/skills/chinamate-fullstack-delivery",
                repo_root / "scripts",
                repo_root / "docs/architecture",
                repo_root / "docs/standards",
                repo_root / "docs/templates/openspec-change-evidence.md",
            ]
        )
    if profile.startswith("frontend"):
        paths.extend([repo_root / "frontend/src", repo_root / "frontend/e2e", repo_root / "frontend/package.json"])
    if profile.startswith("backend"):
        paths.extend([repo_root / "backend/src", repo_root / "backend/pom.xml"])
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=sorted(PROFILES))
    parser.add_argument("--change")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    commands = resolve_profile(args.profile, args.change)
    results = run_commands(commands, repo_root)
    manifest = build_manifest(
        args.profile,
        repo_root,
        results,
        profile_inputs(args.profile, repo_root, args.change),
    )
    output = args.output if args.output.is_absolute() else repo_root / args.output
    write_manifest(manifest, output)
    print(json.dumps({"status": manifest["status"], "output": str(output)}, ensure_ascii=False))
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
