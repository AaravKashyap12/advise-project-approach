#!/usr/bin/env python3
"""Validate source skill structure."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "advise-project-approach"
SOURCE_DIR = ROOT / "skills" / SKILL_NAME
SKILL_FILE = SOURCE_DIR / "SKILL.md"


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

    # Only SKILL.md should exist in the skill folder
    extra_skill_files = {
        path.relative_to(SOURCE_DIR).as_posix()
        for path in SOURCE_DIR.rglob("*")
        if path.is_file()
    } - {"SKILL.md"}
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


def main() -> None:
    validate_source()
    print("Skill is valid.")


if __name__ == "__main__":
    main()
