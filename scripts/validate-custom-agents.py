#!/usr/bin/env python3
"""校验项目级 Codex custom agents 的结构、引用和权限边界。"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


EXPECTED_AGENTS = (
    "product_manager",
    "interaction_designer",
    "frontend_engineer",
    "backend_engineer",
    "qa_engineer",
    "spec_reviewer",
    "experience_reviewer",
)
READ_ONLY_AGENTS = {"spec_reviewer", "experience_reviewer"}
REQUIRED_SECTIONS = (
    "角色职责",
    "输出格式",
    "角色限制",
    "Skills",
    "Rules",
    "Tools 授权",
    "输出语言",
)
ALLOWED_FIELDS = {
    "name",
    "description",
    "developer_instructions",
    "sandbox_mode",
}
ALLOWED_SANDBOX_MODES = {"read-only", "workspace-write"}
SKILL_REFERENCE = re.compile(r"\.codex/skills/([a-z0-9][a-z0-9-]*)/SKILL\.md")
RULE_REFERENCE = re.compile(r"\.codex/rules/([a-z0-9][a-z0-9-]*\.md)")
SPEC_REVIEWER_REQUIRED_CONTENT = (
    "### 一、正向对账表（Spec → 代码）",
    "### 二、反向对账表（代码 → Spec）",
    "### 四、覆盖率统计",
    "### 五、修复 Action Items",
    "文件路径和行号",
)


class ValidationError(Exception):
    """表示 custom agent 配置违反项目治理合同。"""


def require_non_empty_string(config: dict[str, Any], field: str, source: Path) -> str:
    value = config.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{source} 缺少非空字段：{field}")
    return value


def validate_agent(
    source: Path,
    expected_name: str,
    skills_dir: Path,
    rules_dir: Path,
) -> str:
    try:
        with source.open("rb") as stream:
            config = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ValidationError(f"{source} 不是有效 TOML：{error}") from error

    unknown_fields = sorted(set(config) - ALLOWED_FIELDS)
    if unknown_fields:
        raise ValidationError(
            f"{source} 包含未批准的顶层字段：{', '.join(unknown_fields)}"
        )

    name = require_non_empty_string(config, "name", source)
    require_non_empty_string(config, "description", source)
    instructions = require_non_empty_string(config, "developer_instructions", source)

    if name != expected_name or source.stem != name:
        raise ValidationError(
            f"{source} 的 name 必须与文件名和预期角色一致：{expected_name}"
        )

    missing_sections = [
        section
        for section in REQUIRED_SECTIONS
        if not re.search(rf"^##[ \t]+{re.escape(section)}[ \t]*$", instructions, re.MULTILINE)
    ]
    if missing_sections:
        raise ValidationError(
            f"{source} 缺少角色合同章节：{', '.join(missing_sections)}"
        )

    for required_phrase in ("必需输入", "允许写入范围", "完成报告"):
        if required_phrase not in instructions:
            raise ValidationError(f"{source} 缺少角色合同内容：{required_phrase}")

    if name == "spec_reviewer":
        for required_content in SPEC_REVIEWER_REQUIRED_CONTENT:
            if required_content not in instructions:
                raise ValidationError(
                    f"{source} 缺少 Spec Reviewer 合同内容：{required_content}"
                )

    skill_names = set(SKILL_REFERENCE.findall(instructions))
    if not skill_names:
        raise ValidationError(f"{source} 的 Skills 章节未引用项目 Skill 入口")
    for skill_name in sorted(skill_names):
        skill_path = skills_dir / skill_name / "SKILL.md"
        if not skill_path.is_file():
            raise ValidationError(f"{source} 引用了不存在的 Skill：{skill_path}")

    rule_names = set(RULE_REFERENCE.findall(instructions))
    if not rule_names:
        raise ValidationError(f"{source} 的 Rules 章节未引用项目 Rule")
    for rule_name in sorted(rule_names):
        rule_path = rules_dir / rule_name
        if not rule_path.is_file():
            raise ValidationError(f"{source} 引用了不存在的 Rule：{rule_path}")

    sandbox_mode = config.get("sandbox_mode")
    if sandbox_mode not in ALLOWED_SANDBOX_MODES:
        raise ValidationError(
            f"{source} 的 sandbox_mode 必须是 read-only 或 workspace-write"
        )
    if name in READ_ONLY_AGENTS and sandbox_mode != "read-only":
        raise ValidationError(f"{source} 必须使用 sandbox_mode = \"read-only\"")
    if name not in READ_ONLY_AGENTS and sandbox_mode != "workspace-write":
        raise ValidationError(f"{source} 写入型角色必须使用 workspace-write sandbox")

    return name


def validate_forbidden_roots(scan_root: Path) -> None:
    forbidden = (
        scan_root / "frontend/.codex/agents",
        scan_root / "backend/.codex/agents",
    )
    for path in forbidden:
        if path.exists():
            raise ValidationError(f"子仓库不得保存重复 Agent：{path}")


def validate_all(
    agents_dir: Path,
    skills_dir: Path,
    rules_dir: Path,
    scan_root: Path,
) -> None:
    readme = agents_dir / "README.md"
    if not readme.is_file():
        raise ValidationError(f"缺少 Agent 索引：{readme}")

    expected_files = {f"{name}.toml" for name in EXPECTED_AGENTS}
    actual_files = {path.name for path in agents_dir.glob("*.toml")}
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        unexpected = sorted(actual_files - expected_files)
        details = []
        if missing:
            details.append(f"缺少 {', '.join(missing)}")
        if unexpected:
            details.append(f"存在未登记文件 {', '.join(unexpected)}")
        raise ValidationError(f"Agent 文件清单不正确：{'; '.join(details)}")

    names = [
        validate_agent(agents_dir / f"{name}.toml", name, skills_dir, rules_dir)
        for name in EXPECTED_AGENTS
    ]
    if len(names) != len(set(names)):
        raise ValidationError("Agent name 必须全局唯一")

    validate_forbidden_roots(scan_root)


def parse_args() -> argparse.Namespace:
    script_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-dir", type=Path, default=script_root / ".codex/agents")
    parser.add_argument("--skills-dir", type=Path, default=script_root / ".codex/skills")
    parser.add_argument("--rules-dir", type=Path, default=script_root / ".codex/rules")
    parser.add_argument("--scan-root", type=Path, default=script_root)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        validate_all(args.agents_dir, args.skills_dir, args.rules_dir, args.scan_root)
    except ValidationError as error:
        print(f"失败：{error}", file=sys.stderr)
        return 1
    print("通过：七个 Codex custom agents 的结构、引用与权限边界有效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
