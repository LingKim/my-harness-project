#!/usr/bin/env python3
"""复核 ChinaMate verification manifest 的输入与仓库状态是否仍然新鲜。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


SCHEMA = "chinamate-verification-manifest/v1"


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


def git_value(repo: Path, argv: list[str], binary: bool = False) -> str | None:
    completed = subprocess.run(argv, cwd=repo, check=False, capture_output=True)
    if completed.returncode != 0:
        return None
    if binary:
        return hashlib.sha256(completed.stdout).hexdigest()
    return completed.stdout.decode("utf-8").strip()


def current_repository_state(repo: Path) -> dict[str, str | None]:
    return {
        "head": git_value(repo, ["git", "rev-parse", "HEAD"]),
        "diffSha256": git_value(
            repo, ["git", "diff", "--no-ext-diff", "--binary", "HEAD"], binary=True
        ),
    }


def check_manifest(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError(f"不支持的 verification manifest schema：{manifest.get('schema')}")

    changed: list[str] = []
    for entry in manifest.get("inputs", []):
        raw_path = Path(entry["path"])
        path = raw_path if raw_path.is_absolute() else repo_root / raw_path
        if hash_path(path) != entry.get("sha256"):
            changed.append(entry["path"])

    changed_repositories: list[str] = []
    for name, expected in manifest.get("repositories", {}).items():
        repo = repo_root if name == "root" else repo_root / name
        if repo.exists() and current_repository_state(repo) != expected:
            changed_repositories.append(name)

    status = "STALE" if changed or changed_repositories else "FRESH"
    return {
        "status": status,
        "profile": manifest.get("profile"),
        "changedInputs": changed,
        "changedRepositories": changed_repositories,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest if args.manifest.is_absolute() else repo_root / args.manifest
    result = check_manifest(manifest_path, repo_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "FRESH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
