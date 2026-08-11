#!/usr/bin/env python3
"""Validate source and packaged skill structure."""

from __future__ import annotations

import json
import re
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "advise-project-approach"
SOURCE_DIR = ROOT / "skills" / SKILL_NAME
SKILL_FILE = SOURCE_DIR / "SKILL.md"
AGENT_FILE = SOURCE_DIR / "agents" / "openai.yaml"
PACKAGE_FILE = ROOT / "dist" / f"{SKILL_NAME}.skill"
EVAL_CASES_FILE = ROOT / "evals" / "cases.json"
AGENTS_FILE = ROOT / "AGENTS.md"
CLAUDE_FILE = ROOT / "CLAUDE.md"
VERSION_FILE = ROOT / "VERSION"
PLUGIN_FILE = ROOT / ".claude-plugin" / "plugin.json"
README_FILE = ROOT / "README.md"
EXPECTED_PACKAGE_FILES = {
    f"{SKILL_NAME}/SKILL.md",
    f"{SKILL_NAME}/agents/openai.yaml",
}


def fail(message: str) -> None:
    raise SystemExit(f"Validation failed: {message}")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("SKILL.md must start with YAML frontmatter")

    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            fail(f"Invalid frontmatter line: {raw_line}")
        key, value = raw_line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def validate_source() -> None:
    if not SOURCE_DIR.is_dir():
        fail(f"Missing source directory: {SOURCE_DIR.relative_to(ROOT)}")
    if not SKILL_FILE.is_file():
        fail("Missing skills/advise-project-approach/SKILL.md")
    if not AGENT_FILE.is_file():
        fail("Missing skills/advise-project-approach/agents/openai.yaml")

    extra_skill_files = {
        path.relative_to(SOURCE_DIR).as_posix()
        for path in SOURCE_DIR.rglob("*")
        if path.is_file()
    } - {"SKILL.md", "agents/openai.yaml"}
    if extra_skill_files:
        fail(f"Unexpected files inside skill package: {sorted(extra_skill_files)}")

    text = SKILL_FILE.read_text(encoding="utf-8")
    fields = parse_frontmatter(text)
    allowed_fields = {"name", "description"}
    extra_fields = set(fields) - allowed_fields
    missing_fields = allowed_fields - set(fields)
    if missing_fields:
        fail(f"Missing frontmatter fields: {sorted(missing_fields)}")
    if extra_fields:
        fail(f"Unexpected frontmatter fields: {sorted(extra_fields)}")
    if fields["name"] != SKILL_NAME:
        fail("Frontmatter name must match skill folder name")
    if len(fields["description"]) > 1024:
        fail("Frontmatter description must be 1024 characters or fewer")


def validate_package() -> None:
    if not PACKAGE_FILE.is_file():
        fail(f"Missing package: {PACKAGE_FILE.relative_to(ROOT)}")
    with ZipFile(PACKAGE_FILE) as archive:
        names = {name for name in archive.namelist() if not name.endswith("/")}
    if names != EXPECTED_PACKAGE_FILES:
        fail(
            "Package contents differ from expected files: "
            f"expected {sorted(EXPECTED_PACKAGE_FILES)}, got {sorted(names)}"
        )


def validate_eval_cases() -> None:
    if not EVAL_CASES_FILE.is_file():
        fail("Missing evals/cases.json")

    data = json.loads(EVAL_CASES_FILE.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        fail("evals/cases.json must use schema_version 1")

    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 6:
        fail("evals/cases.json must contain at least six cases")

    allowed_modes = {"pre-build", "mid-build", "post-build", "cross-mode"}
    seen_ids: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            fail("Every eval case must have a non-empty id")
        if case_id in seen_ids:
            fail(f"Duplicate eval case id: {case_id}")
        seen_ids.add(case_id)
        if case.get("mode") not in allowed_modes:
            fail(f"Invalid mode for eval case {case_id}")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            fail(f"Eval case {case_id} must have a prompt")
        for field in ("assertions", "failure_conditions"):
            values = case.get(field)
            if not isinstance(values, list) or not values:
                fail(f"Eval case {case_id} must have non-empty {field}")
            if not all(isinstance(value, str) and value.strip() for value in values):
                fail(f"Eval case {case_id} has an invalid {field} entry")


def validate_repo_guidance() -> None:
    if not AGENTS_FILE.is_file():
        fail("Missing AGENTS.md cross-harness repository guidance")
    if not CLAUDE_FILE.is_file():
        fail("Missing CLAUDE.md compatibility bridge")
    if "@AGENTS.md" not in CLAUDE_FILE.read_text(encoding="utf-8"):
        fail("CLAUDE.md must import AGENTS.md")


def validate_release_version() -> None:
    if not VERSION_FILE.is_file():
        fail("Missing VERSION release source of truth")
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail("VERSION must contain a semantic version such as 0.6.0")

    if not PLUGIN_FILE.is_file():
        fail("Missing .claude-plugin/plugin.json")
    plugin = json.loads(PLUGIN_FILE.read_text(encoding="utf-8"))
    if plugin.get("version") != version:
        fail("Plugin version must match VERSION")

    if not README_FILE.is_file():
        fail("Missing README.md")
    readme = README_FILE.read_text(encoding="utf-8")
    if f"## What's New in v{version}" not in readme:
        fail("README current What's New section must match VERSION")
    release_url = f"/releases/download/v{version}/advise-project-approach.skill"
    if release_url not in readme:
        fail("README release asset link must match VERSION")


def main() -> None:
    validate_source()
    validate_package()
    validate_eval_cases()
    validate_repo_guidance()
    validate_release_version()
    print("Skill package is valid.")


if __name__ == "__main__":
    main()
