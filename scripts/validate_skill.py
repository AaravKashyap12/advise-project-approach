#!/usr/bin/env python3
"""Validate source and packaged skill structure."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path, PurePosixPath
import stat
from urllib.parse import urlsplit
from zipfile import BadZipFile, ZipFile
import zlib

try:
    import yaml
except ImportError:
    raise SystemExit("Validation requires development dependencies: python -m pip install -r requirements-dev.txt") from None


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
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
EXPECTED_PACKAGE_FILES = {
    f"{SKILL_NAME}/SKILL.md",
    f"{SKILL_NAME}/agents/openai.yaml",
}


def fail(message: str) -> None:
    raise SystemExit(f"Validation failed: {message}")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        fail(f"Cannot read {path.relative_to(ROOT)} as UTF-8: {exc}")


def unique_json_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def read_json_object(path: Path) -> dict:
    try:
        data = json.loads(read_text(path), object_pairs_hook=unique_json_object,
                          parse_constant=reject_json_constant)
    except ValueError as exc:
        fail(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return data


class UniqueSafeLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise yaml.constructor.ConstructorError(
                    "while reading a mapping", node.start_mark,
                    f"Non-string or duplicate YAML key: {key!r}", key_node.start_mark,
                )
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def parse_yaml_mapping(text: str, label: str) -> dict:
    try:
        data = yaml.load(text, Loader=UniqueSafeLoader)
    except yaml.YAMLError as exc:
        fail(f"Invalid YAML in {label}: {exc}")
    if not isinstance(data, dict):
        fail(f"{label} must contain a YAML mapping")
    return data


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("SKILL.md must start with YAML frontmatter")

    return parse_yaml_mapping(match.group(1), "SKILL.md frontmatter")


def validate_source() -> None:
    if not SOURCE_DIR.is_dir():
        fail(f"Missing source directory: {SOURCE_DIR.relative_to(ROOT)}")
    if not SKILL_FILE.is_file():
        fail("Missing skills/advise-project-approach/SKILL.md")
    if not AGENT_FILE.is_file():
        fail("Missing skills/advise-project-approach/agents/openai.yaml")

    if SOURCE_DIR.is_symlink() or any(path.is_symlink() for path in SOURCE_DIR.rglob("*")):
        fail("Skill source must not contain symbolic links")
    extra_skill_files = {
        path.relative_to(SOURCE_DIR).as_posix()
        for path in SOURCE_DIR.rglob("*")
        if path.is_file()
    } - {"SKILL.md", "agents/openai.yaml"}
    if extra_skill_files:
        fail(f"Unexpected files inside skill package: {sorted(extra_skill_files)}")

    text = read_text(SKILL_FILE)
    fields = parse_frontmatter(text)
    allowed_fields = {"name", "description"}
    extra_fields = set(fields) - allowed_fields
    missing_fields = allowed_fields - set(fields)
    if missing_fields:
        fail(f"Missing frontmatter fields: {sorted(missing_fields)}")
    if extra_fields:
        fail(f"Unexpected frontmatter fields: {sorted(extra_fields)}")
    for field in allowed_fields:
        if not isinstance(fields[field], str) or not fields[field].strip():
            fail(f"Frontmatter {field} must be a non-empty string")
    if fields["name"] != SKILL_NAME:
        fail("Frontmatter name must match skill folder name")
    if len(fields["description"]) > 1024:
        fail("Frontmatter description must be 1024 characters or fewer")

    agent = parse_yaml_mapping(read_text(AGENT_FILE), "agents/openai.yaml")
    if "interface" in agent:
        interface = agent["interface"]
        if not isinstance(interface, dict):
            fail("agents/openai.yaml interface must be a mapping")
        for field in ("display_name", "short_description", "default_prompt"):
            if field in interface and (not isinstance(interface[field], str) or not interface[field].strip()):
                fail(f"agents/openai.yaml interface.{field} must be a non-empty string")


def validate_package() -> None:
    if not PACKAGE_FILE.is_file():
        fail(f"Missing package: {PACKAGE_FILE.relative_to(ROOT)}")
    try:
        with ZipFile(PACKAGE_FILE) as archive:
            entries = archive.infolist()
            names = [info.filename for info in entries]
            if len(names) != len(EXPECTED_PACKAGE_FILES) or set(names) != EXPECTED_PACKAGE_FILES:
                fail(f"Package must contain exactly {sorted(EXPECTED_PACKAGE_FILES)}; got {names}")
            for info in entries:
                file_type = stat.S_IFMT(info.external_attr >> 16)
                if file_type not in (0, stat.S_IFREG):
                    fail(f"Package member must be a regular file: {info.filename}")
                source = ROOT / "skills" / info.filename
                expected = read_text(source).encode("utf-8")
                # Check size before decompression, then read to verify the member CRC.
                if info.file_size != len(expected):
                    fail(f"Package member size differs from source: {info.filename}; rebuild the package")
                if archive.read(info) != expected:
                    fail(f"Package member differs from source: {info.filename}; rebuild the package")
    except (BadZipFile, OSError, RuntimeError, NotImplementedError, EOFError, zlib.error) as exc:
        fail(f"Cannot read package {PACKAGE_FILE.relative_to(ROOT)}: {exc}")


def validate_eval_cases() -> None:
    if not EVAL_CASES_FILE.is_file():
        fail("Missing evals/cases.json")

    data = read_json_object(EVAL_CASES_FILE)
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        fail("evals/cases.json must use integer schema_version 1")

    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 6:
        fail("evals/cases.json must contain at least six cases")

    allowed_modes = {"pre-build", "mid-build", "post-build", "cross-mode"}
    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"Eval case at index {index} must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            fail("Every eval case must have a non-empty id")
        if case_id in seen_ids:
            fail(f"Duplicate eval case id: {case_id}")
        seen_ids.add(case_id)
        if not isinstance(case.get("mode"), str) or case["mode"] not in allowed_modes:
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
    if "@AGENTS.md" not in read_text(CLAUDE_FILE):
        fail("CLAUDE.md must import AGENTS.md")


def visible_markdown(text: str) -> str:
    """Select prose in the repository's ATX-heading/inline-link Markdown format."""
    text = re.sub(r"<!--.*?(?:-->|$)", lambda match: "\n" * match[0].count("\n"), text, flags=re.DOTALL)
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            lines.append("")
        elif marker:
            fence = marker[1]
            lines.append("")
        elif line.startswith(("    ", "\t")):
            lines.append("")
        else:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines), flags=re.DOTALL)


def markdown_sections(text: str) -> list[tuple[str, str]]:
    headings = list(re.finditer(r"(?m)^ {0,3}##[ \t]+(.+?)[ \t]*$", text))
    return [(re.sub(r"[ \t]+#+$", "", heading[1]),
             text[heading.end():headings[index + 1].start() if index + 1 < len(headings) else len(text)])
            for index, heading in enumerate(headings)]


def validate_release_documents(version: str, plugin: dict) -> None:
    readme = visible_markdown(read_text(README_FILE))
    current = [(title, body) for title, body in markdown_sections(readme) if title.startswith("What's New")]
    if len(current) != 1 or current[0][0] != f"What's New in v{version}" or not current[0][1].strip():
        fail("README must have one visible, non-empty current What's New section matching VERSION")

    targets = re.findall(r"(?<!!)\[[^\]\n]+\]\([ \t]*<?([^\s()<>]+)>?[ \t]*\)", readme)
    release_targets = [target for target in targets if f"/releases/download/" in target and target.endswith(f"/{SKILL_NAME}.skill")]
    repository = plugin.get("repository")
    if not isinstance(repository, str) or not repository.startswith("https://"):
        fail("plugin.json repository must be an HTTPS repository URL for the release asset")
    expected_url = f"{repository.rstrip('/')}/releases/download/v{version}/{SKILL_NAME}.skill"
    if release_targets != [expected_url] or not urlsplit(expected_url).netloc:
        fail("README must have one visible release asset link matching VERSION and the plugin repository")

    changelog = visible_markdown(read_text(CHANGELOG_FILE))
    current_entries = [(title, body) for title, body in markdown_sections(changelog)
                       if re.match(rf"^\[?{re.escape(version)}\]?(?:\s|$)", title)]
    if len(current_entries) != 1:
        fail("CHANGELOG.md must contain exactly one current dated version entry")
    title, body = current_entries[0]
    entry = re.fullmatch(rf"(?:{re.escape(version)}|\[{re.escape(version)}\]) - ([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})", title)
    if not entry or not body.strip():
        fail("CHANGELOG.md current entry must have an ISO date and non-empty release notes")
    try:
        date.fromisoformat(entry[1])
    except ValueError:
        fail("CHANGELOG.md current entry must have a valid calendar date")


def validate_release_version() -> None:
    if not VERSION_FILE.is_file():
        fail("Missing VERSION release source of truth")
    version = read_text(VERSION_FILE).strip()
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version):
        fail("VERSION must contain an ASCII MAJOR.MINOR.PATCH version without leading zeros")

    if not PLUGIN_FILE.is_file():
        fail("Missing .claude-plugin/plugin.json")
    plugin = read_json_object(PLUGIN_FILE)
    if plugin.get("version") != version:
        fail("Plugin version must match VERSION")
    if not isinstance(plugin.get("name"), str) or not plugin["name"].strip():
        fail("plugin.json name must be a non-empty string")
    skill_paths = plugin.get("skills")
    if not isinstance(skill_paths, list) or len(skill_paths) != 1:
        fail("plugin.json skills must contain exactly one local skill path")
    for value in skill_paths:
        if not isinstance(value, str) or not value.strip() or "\\" in value or ":" in value or "\x00" in value:
            fail("plugin.json skills entries must be relative POSIX paths")
        relative = PurePosixPath(value)
        if relative.is_absolute() or ".." in relative.parts:
            fail("plugin.json skills paths must stay inside the repository")
        target = ROOT.joinpath(*relative.parts).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.is_dir() or target != SOURCE_DIR.resolve():
            fail("plugin.json skills must reference the existing skills/advise-project-approach directory")

    validate_release_documents(version, plugin)


def main() -> None:
    validate_source()
    validate_package()
    validate_eval_cases()
    validate_repo_guidance()
    validate_release_version()
    print("Skill package is valid.")


if __name__ == "__main__":
    main()
