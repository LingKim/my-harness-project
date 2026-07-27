#!/usr/bin/env python3
"""使用隔离临时目录验证 custom agent 治理校验器的失败场景。"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_AGENTS = PROJECT_ROOT / ".codex/agents"
VALIDATOR = PROJECT_ROOT / "scripts/validate-custom-agents.py"


def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    if old not in content:
        raise AssertionError(f"测试夹具无法在 {path} 中找到：{old}")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def replace_all(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    if old not in content:
        raise AssertionError(f"测试夹具无法在 {path} 中找到：{old}")
    path.write_text(content.replace(old, new), encoding="utf-8")


def remove_if_present(path: Path, text: str) -> None:
    content = path.read_text(encoding="utf-8")
    path.write_text(content.replace(text, ""), encoding="utf-8")


def remove_assignment(path: Path, field: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if not line.startswith(f"{field} = ")]
    if len(kept) == len(lines):
        raise AssertionError(f"测试夹具无法在 {path} 中找到字段：{field}")
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def run_validator(agents_dir: Path, scan_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--agents-dir",
            str(agents_dir),
            "--skills-dir",
            str(PROJECT_ROOT / ".codex/skills"),
            "--rules-dir",
            str(PROJECT_ROOT / ".codex/rules"),
            "--scan-root",
            str(scan_root),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def assert_failure(
    name: str,
    mutate: Callable[[Path, Path], None],
    expected_message: str,
) -> None:
    with tempfile.TemporaryDirectory(prefix="chinamate-agent-fixture-") as temp_dir:
        scan_root = Path(temp_dir)
        agents_dir = scan_root / ".codex/agents"
        shutil.copytree(SOURCE_AGENTS, agents_dir)
        mutate(agents_dir, scan_root)
        result = run_validator(agents_dir, scan_root)
        if result.returncode == 0:
            raise AssertionError(f"失败夹具未被拒绝：{name}")
        if expected_message not in result.stderr:
            raise AssertionError(
                f"失败夹具 {name} 的错误不准确；期望包含 {expected_message!r}，"
                f"实际为 {result.stderr.strip()!r}"
            )
        print(f"通过：失败夹具 {name} 被准确拒绝")


def main() -> int:
    baseline = run_validator(SOURCE_AGENTS, PROJECT_ROOT)
    if baseline.returncode != 0:
        print(baseline.stderr, file=sys.stderr)
        raise AssertionError("正式 custom agents 基线必须先通过")

    cases: tuple[tuple[str, Callable[[Path, Path], None], str], ...] = (
        (
            "非法 TOML",
            lambda agents, _: (agents / "product_manager.toml").write_text(
                "name = [\n", encoding="utf-8"
            ),
            "不是有效 TOML",
        ),
        (
            "缺少必填字段",
            lambda agents, _: remove_assignment(
                agents / "product_manager.toml", "description"
            ),
            "缺少非空字段：description",
        ),
        (
            "角色重名",
            lambda agents, _: replace_once(
                agents / "interaction_designer.toml",
                'name = "interaction_designer"',
                'name = "product_manager"',
            ),
            "name 必须与文件名和预期角色一致",
        ),
        (
            "缺少角色章节",
            lambda agents, _: replace_once(
                agents / "qa_engineer.toml", "## Tools 授权", "## 工具说明"
            ),
            "缺少角色合同章节：Tools 授权",
        ),
        (
            "虚假 Skill",
            lambda agents, _: replace_once(
                agents / "frontend_engineer.toml",
                ".codex/skills/vercel-react-best-practices/SKILL.md",
                ".codex/skills/nonexistent-skill/SKILL.md",
            ),
            "引用了不存在的 Skill",
        ),
        (
            "虚假 Rule",
            lambda agents, _: replace_once(
                agents / "backend_engineer.toml",
                ".codex/rules/backend-conventions.md",
                ".codex/rules/nonexistent-rule.md",
            ),
            "引用了不存在的 Rule",
        ),
        (
            "未知顶层字段",
            lambda agents, _: (agents / "qa_engineer.toml").write_text(
                (agents / "qa_engineer.toml").read_text(encoding="utf-8")
                + '\ntools = ["Read", "Write"]\n',
                encoding="utf-8",
            ),
            "未批准的顶层字段：tools",
        ),
        (
            "缺少 Spec Reviewer",
            lambda agents, _: (agents / "spec_reviewer.toml").unlink(),
            "缺少 spec_reviewer.toml",
        ),
        (
            "Spec Reviewer 缺少合同章节",
            lambda agents, _: replace_once(
                agents / "spec_reviewer.toml", "## 输出格式", "## 报告结构"
            ),
            "缺少角色合同章节：输出格式",
        ),
        (
            "Spec Reviewer 缺少双向对账合同",
            lambda agents, _: replace_once(
                agents / "spec_reviewer.toml",
                "### 一、正向对账表（Spec → 代码）",
                "### 一、需求检查表",
            ),
            "缺少 Spec Reviewer 合同内容：### 一、正向对账表（Spec → 代码）",
        ),
        (
            "Spec Reviewer sandbox 越权",
            lambda agents, _: replace_once(
                agents / "spec_reviewer.toml",
                'sandbox_mode = "read-only"',
                'sandbox_mode = "workspace-write"',
            ),
            '必须使用 sandbox_mode = "read-only"',
        ),
        (
            "只读角色 sandbox 越权",
            lambda agents, _: replace_once(
                agents / "experience_reviewer.toml",
                'sandbox_mode = "read-only"',
                'sandbox_mode = "workspace-write"',
            ),
            '必须使用 sandbox_mode = "read-only"',
        ),
        (
            "QA 缺少证据交接合同",
            lambda agents, _: replace_all(
                agents / "qa_engineer.toml",
                "`evidence.md`",
                "交付摘要文档",
            ),
            "缺少交付证据合同内容：`evidence.md`",
        ),
        (
            "Spec Reviewer 缺少持久化路径",
            lambda agents, _: replace_all(
                agents / "spec_reviewer.toml",
                "`reviews/spec-review.md`",
                "完整审查报告",
            ),
            "缺少交付证据合同内容：`reviews/spec-review.md`",
        ),
        (
            "体验 Reviewer 缺少持久化路径",
            lambda agents, _: replace_all(
                agents / "experience_reviewer.toml",
                "`reviews/experience-review.md`",
                "完整体验报告",
            ),
            "缺少交付证据合同内容：`reviews/experience-review.md`",
        ),
        (
            "后端角色缺少工程实践合规清单",
            lambda agents, _: remove_if_present(
                agents / "backend_engineer.toml", "工程实践合规清单"
            ),
            "缺少后端工程实践合同：工程实践合规清单",
        ),
        (
            "QA 缺少后端工程实践验证",
            lambda agents, _: remove_if_present(
                agents / "qa_engineer.toml", "后端工程实践验证"
            ),
            "缺少QA 工程实践合同：后端工程实践验证",
        ),
        (
            "Spec Reviewer 缺少项目 Rule 对账",
            lambda agents, _: remove_if_present(
                agents / "spec_reviewer.toml", "代码 → 项目 Rules/技术基线"
            ),
            "缺少Spec Reviewer 工程实践合同：代码 → 项目 Rules/技术基线",
        ),
        (
            "子仓库重复 Agent",
            lambda agents, root: shutil.copytree(
                agents, root / "frontend/.codex/agents"
            ),
            "子仓库不得保存重复 Agent",
        ),
    )

    for name, mutate, expected_message in cases:
        assert_failure(name, mutate, expected_message)

    print(f"通过：{len(cases)} 个 custom agent 失败夹具全部生效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
