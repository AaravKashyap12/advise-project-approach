#!/usr/bin/env python3
"""Read-only repository audit. All mutations and Git indexes live in temp copies.

Exit 0: all audit invariants held; 1: reproduced defects; 2: harness error.
PyYAML is optional and is never installed. Without it YAML oracle checks skip.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import traceback
import warnings
import uuid
from zipfile import ZIP_STORED, ZipFile, ZipInfo
import zlib

try:
    import yaml
except ImportError:
    yaml = None


NAME = "advise-project-approach"
SKILL = f"skills/{NAME}/SKILL.md"
AGENT = f"skills/{NAME}/agents/openai.yaml"
DIST = f"dist/{NAME}.skill"
PLUGIN = ".claude-plugin/plugin.json"
CASES = "evals/cases.json"
OUTPUT = Path("evals/results/2026-08-31-rigorous-audit/packaging")
EXPECTED_NAMES = [f"{NAME}/SKILL.md", f"{NAME}/agents/openai.yaml"]
SOURCES = ["AGENTS.md", "scripts/package_skill.py", "scripts/validate_skill.py",
           ".github/workflows/validate.yml", PLUGIN, AGENT, "VERSION", ".gitattributes",
           "README.md", "CHANGELOG.md", "evals/README.md", "CONTRIBUTING.md"]


@contextmanager
def temporary_workspace():
    # Default mkdir permissions inherit the sandbox ACL on Windows. Python's
    # mkdtemp(mode=0700) can produce an owner-only directory inaccessible to it.
    parent = Path(tempfile.gettempdir()).resolve()
    root = parent / ("advise-packaging-audit-" + uuid.uuid4().hex)
    root.mkdir()
    try:
        yield root
    finally:
        target = root.resolve()
        if target.parent != parent or not target.name.startswith("advise-packaging-audit-"):
            raise RuntimeError(f"Refusing cleanup outside audit temp parent: {target}")
        def remove_readonly(function, path, exc_info):
            import stat
            Path(path).chmod(stat.S_IWRITE | stat.S_IREAD)
            function(path)
        shutil.rmtree(target, onerror=remove_readonly)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path, value):
    write_text(path, json.dumps(value, indent=2, ensure_ascii=True) + "\n")


def manifest(root):
    result = {}
    for directory, subdirs, files in os.walk(root):
        subdirs[:] = [d for d in subdirs if d != ".git"]
        for filename in files:
            path = Path(directory) / filename
            relative = path.relative_to(root).as_posix()
            # Other independent auditors may own sibling results directories.
            if not relative.startswith("evals/results/"):
                result[relative] = digest(path.read_bytes())
    return result


def archive_evidence(root):
    path = root / DIST
    if not path.is_file():
        return {"exists": False}
    result = {"exists": True, "sha256": digest(path.read_bytes()), "size": path.stat().st_size,
              "entries": [], "errors": []}
    try:
        with ZipFile(path) as archive:
            for info in archive.infolist():
                entry = {"name": info.filename, "size": info.file_size,
                         "date_time": info.date_time, "external_attr": info.external_attr,
                         "create_system": info.create_system, "compression": info.compress_type}
                try:
                    data = archive.read(info)
                    entry["sha256"] = digest(data)
                    source = root / "skills" / info.filename
                    if source.is_file():
                        normalized = source.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                        entry["matches_normalized_source"] = data == normalized
                except Exception as exc:
                    entry["read_error"] = f"{type(exc).__name__}: {exc}"
                    result["errors"].append(entry["read_error"])
                result["entries"].append(entry)
    except Exception as exc:
        result["errors"].append(f"{type(exc).__name__}: {exc}")
    return result


def yaml_evidence(root, metadata=False):
    if yaml is None:
        return {"available": False}
    text = (root / (AGENT if metadata else SKILL)).read_text(encoding="utf-8")
    payload = text if metadata else text.split("---\n", 2)[1]

    class UniqueKeyLoader(yaml.SafeLoader):
        pass

    def unique_mapping(loader, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f"Duplicate YAML mapping key: {key}")
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping

    UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
    try:
        value = yaml.load(payload, Loader=UniqueKeyLoader)
        return {"available": True, "valid_yaml": True, "parsed": value,
                "types": {k: type(v).__name__ for k, v in value.items()} if isinstance(value, dict) else {}}
    except Exception as exc:
        return {"available": True, "valid_yaml": False, "error": f"{type(exc).__name__}: {exc}"}


def frontmatter(root, lines):
    text = (root / SKILL).read_text(encoding="utf-8")
    body = text.split("---\n", 2)[2]
    write_text(root / SKILL, "---\n" + lines + "\n---\n" + body)


def edit_json(root, relative, mutate):
    data = json.loads((root / relative).read_text(encoding="utf-8"))
    mutate(data)
    write_json(root / relative, data)


def rewrite_zip(root, transform):
    with ZipFile(root / DIST) as archive:
        entries = [(info.filename, archive.read(info)) for info in archive.infolist()]
    entries = transform(entries)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with ZipFile(root / DIST, "w", compression=ZIP_STORED) as archive:
            for name, payload in entries:
                archive.writestr(ZipInfo(name), payload)


def corrupt_crc(root):
    rewrite_zip(root, lambda entries: entries)
    with ZipFile(root / DIST) as archive:
        offset = archive.infolist()[0].header_offset
    data = bytearray((root / DIST).read_bytes())
    name_size, extra_size = struct.unpack_from("<HH", data, offset + 26)
    data[offset + 30 + name_size + extra_size] ^= 1
    (root / DIST).write_bytes(data)


class Audit:
    def __init__(self, repo, output, temp):
        self.repo, self.output, self.temp = repo, output, temp
        self.commands, self.results = [], []
        self.snapshot = temp / "snapshot"
        shutil.copytree(repo, self.snapshot, ignore=self.ignore_copy)
        self.env = os.environ.copy()
        for key in list(self.env):
            if key.startswith("GIT_") or key.startswith("PYTHON"):
                del self.env[key]
        self.env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
                         "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                         "GIT_TERMINAL_PROMPT": "0"})
        self.env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + self.env.get("PATH", "")
        self.template = temp / "empty-git-template"
        self.template.mkdir()

    @staticmethod
    def ignore_copy(directory, names):
        ignored = {name for name in names if name in {".git", "__pycache__"}}
        if Path(directory).name == "evals":
            ignored.add("results")
        return ignored

    def fresh(self, test_id):
        root = self.temp / test_id
        shutil.copytree(self.snapshot, root)
        return root

    def run(self, test_id, root, argv, extra_env=None):
        started = time.monotonic()
        env = dict(self.env, **(extra_env or {}))
        try:
            p = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=45)
            code, stdout, stderr = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Command timeout: {argv}") from exc
        record = {"index": len(self.commands) + 1, "test_id": test_id, "cwd": str(root),
                  "argv": argv, "command": subprocess.list2cmdline(argv), "exit_code": code,
                  "stdout": stdout, "stderr": stderr,
                  "elapsed_seconds": round(time.monotonic() - started, 4),
                  "extra_env": extra_env or {}}
        self.commands.append(record)
        return record

    def validate(self, test_id, root):
        return self.run(test_id, root, ["python", "scripts/validate_skill.py"])

    def package(self, test_id, root):
        return self.run(test_id, root, ["python", "scripts/package_skill.py"])

    def ci(self, test_id, root):
        # git diff compares worktree vs index. Stage only the candidate artifact,
        # matching a checkout for that path, without copying Git history or committing.
        for argv in (["git", "init", "-q", f"--template={self.template}"],
                     ["git", "-c", "core.autocrlf=false", "add", "--", DIST]):
            record = self.run(test_id, root, argv)
            if record["exit_code"]:
                raise RuntimeError(f"CI fixture setup failed: {record}")
        records = []
        for argv in (["python", "scripts/validate_skill.py"],
                     ["python", "scripts/package_skill.py"],
                     ["python", "scripts/validate_skill.py"],
                     ["git", "diff", "--exit-code", DIST]):
            record = self.run(test_id, root, argv)
            records.append(record)
            if record["exit_code"]:
                break
        return {"exit_codes": [r["exit_code"] for r in records],
                "commands": [r["index"] for r in records],
                "accepted": len(records) == 4 and all(r["exit_code"] == 0 for r in records)}

    def record(self, test_id, category, invariant, passed, evidence, root=None, status=None):
        record = {"id": test_id, "category": category, "invariant": invariant,
                  "status": status or ("PASS" if passed else "FAIL"), "evidence": evidence,
                  "commands": [r["index"] for r in self.commands if r["test_id"] == test_id]}
        if root is not None:
            # Save changed fixture bytes as base64 for binaries, or exact text otherwise.
            import base64
            differences = []
            baseline = manifest(self.snapshot)
            current = manifest(root)
            for path in sorted(baseline.keys() | current.keys()):
                if baseline.get(path) == current.get(path):
                    continue
                entry = {"path": path, "before_sha256": baseline.get(path), "after_sha256": current.get(path)}
                if path in current:
                    data = (root / path).read_bytes()
                    try:
                        entry["text"] = data.decode("utf-8")
                    except UnicodeDecodeError:
                        entry["base64"] = base64.b64encode(data).decode("ascii")
                differences.append(entry)
            record["final_fixture_differences"] = differences
        self.results.append(record)
        print(f"{record['status']:5} {test_id}: {invariant}", flush=True)

    def mutation(self, test_id, category, invariant, mutate, expected_accept=False,
                 rebuild=False, run_ci=False, oracle=None):
        root = self.fresh(test_id)
        mutate(root)
        evidence = {}
        if oracle:
            evidence["oracle"] = oracle(root)
        if category in {"archive", "staleness"}:
            evidence["archive_before"] = archive_evidence(root)
        if rebuild:
            package = self.package(test_id, root)
            if package["exit_code"]:
                raise RuntimeError(f"Unexpected mutation setup build failure: {test_id}")
        validation = self.validate(test_id, root)
        evidence.update({"validator_exit": validation["exit_code"],
                         "validator_accepted": validation["exit_code"] == 0,
                         "rejected_with_traceback": "Traceback (most recent call last)" in validation["stderr"]})
        if run_ci:
            evidence["ci"] = self.ci(test_id, root)
        status = "OBSERVED" if expected_accept is None else None
        self.record(test_id, category, invariant,
                    (validation["exit_code"] == 0) == expected_accept, evidence, root, status)


def run_suite(a):
    root = a.fresh("B01")
    initial = archive_evidence(root)
    baseline = a.ci("B01", root)
    rebuilt = archive_evidence(root)
    expected = sorted(EXPECTED_NAMES)
    integrity = (sorted(e["name"] for e in initial["entries"]) == expected
                 and not initial["errors"]
                 and all(e.get("matches_normalized_source") for e in initial["entries"]))
    a.record("B01", "baseline", "Normal validation/build/validation/CI diff pass; checked-in bytes match source",
             baseline["accepted"] and integrity and initial["sha256"] == rebuilt["sha256"],
             {"ci": baseline, "checked_in": initial, "rebuilt": rebuilt})

    fm_cases = [
        ("F01", "Missing name rejected", "description: Audit fixture", False),
        ("F02", "Missing description rejected", f"name: {NAME}", False),
        ("F03", "Extra field rejected", f"name: {NAME}\ndescription: Audit fixture\nextra: no", False),
        ("F04", "Wrong name rejected", "name: wrong-name\ndescription: Audit fixture", False),
        ("F05", "1025-character description rejected", f"name: {NAME}\ndescription: " + "a" * 1025, False),
        ("F06", "1024-character description accepted", f"name: {NAME}\ndescription: " + "a" * 1024, True),
        ("F07", "Unterminated YAML quote rejected", f'name: {NAME}\ndescription: "unterminated', False),
        ("F08", "Duplicate YAML key rejected", f"name: wrong-name\nname: {NAME}\ndescription: Audit fixture", False),
        ("F09", "List-valued description rejected", f"name: {NAME}\ndescription: [not, a, string]", False),
        ("F10", "Null description rejected", f"name: {NAME}\ndescription: null", False),
        ("F11", "Empty description rejected", f"name: {NAME}\ndescription:", False),
        ("F12", "Valid single-quoted YAML name accepted", f"name: '{NAME}'\ndescription: Audit fixture", True),
        ("F13", "Valid folded YAML description accepted", f"name: {NAME}\ndescription: >\n  Audit fixture\n  description", True),
        ("F14", "Boolean description rejected", f"name: {NAME}\ndescription: true", False),
    ]
    for test_id, invariant, lines, accept in fm_cases:
        a.mutation(test_id, "frontmatter", invariant, lambda r, s=lines: frontmatter(r, s),
                   expected_accept=accept, rebuild=True, run_ci=True, oracle=yaml_evidence)
    a.mutation("F15", "frontmatter", "Missing opening delimiter rejected",
               lambda r: write_text(r / SKILL, (r / SKILL).read_text(encoding="utf-8")[4:]))
    a.mutation("F16", "frontmatter", "Missing closing delimiter rejected",
               lambda r: write_text(r / SKILL, f"---\nname: {NAME}\ndescription: Audit fixture\n"))

    for test_id, path in [("M01", AGENT), ("M02", PLUGIN), ("M03", "VERSION"),
                          ("M04", "AGENTS.md"), ("M05", "CLAUDE.md"), ("M06", "README.md"),
                          ("M07", SKILL), ("M08", DIST), ("M09", CASES)]:
        a.mutation(test_id, "metadata", f"Missing {path} rejected", lambda r, p=path: (r / p).unlink())
    a.mutation("M10", "metadata", "Malformed openai.yaml rejected",
               lambda r: write_text(r / AGENT, 'interface: [unterminated\n'),
               rebuild=True, run_ci=True, oracle=lambda r: yaml_evidence(r, True))
    a.mutation("M11", "metadata", "Characterize empty optional host metadata (required content not specified locally)",
               lambda r: write_text(r / AGENT, ""), expected_accept=None, rebuild=True, run_ci=True,
               oracle=lambda r: yaml_evidence(r, True))
    a.mutation("M12", "metadata", "Plugin skill path resolving to no source rejected",
               lambda r: edit_json(r, PLUGIN, lambda d: d.update(skills=["./skills/missing-skill"])),
               run_ci=True, oracle=lambda r: {"declared_path_exists": (r / "skills/missing-skill").exists()})
    a.mutation("M13", "metadata", "Characterize missing plugin name (external loader schema not exercised)",
               lambda r: edit_json(r, PLUGIN, lambda d: d.pop("name")), expected_accept=None, run_ci=True)
    a.mutation("M14", "metadata", "CLAUDE.md without import rejected",
               lambda r: write_text(r / "CLAUDE.md", "No import here.\n"))
    a.mutation("M15", "metadata", "Unexpected source file rejected",
               lambda r: write_text(r / f"skills/{NAME}/extra.txt", "Audit fixture\n"))

    a.mutation("A01", "archive", "Additional archive file rejected",
               lambda r: rewrite_zip(r, lambda e: e + [(f"{NAME}/extra.txt", b"fixture")]), run_ci=True)
    a.mutation("A02", "archive", "Missing archive member rejected",
               lambda r: rewrite_zip(r, lambda e: e[:1]), run_ci=True)
    a.mutation("A03", "archive", "Changed archive payload rejected",
               lambda r: rewrite_zip(r, lambda e: [(e[0][0], b"WRONG PAYLOAD\n"), e[1]]), run_ci=True)
    a.mutation("A04", "archive", "Zero-byte expected members rejected",
               lambda r: rewrite_zip(r, lambda e: [(n, b"") for n, _ in e]), run_ci=True)
    a.mutation("A05", "archive", "Duplicate archive member rejected",
               lambda r: rewrite_zip(r, lambda e: e + [(e[0][0], b"DUPLICATE PAYLOAD\n")]), run_ci=True)
    a.mutation("A06", "archive", "Unexpected directory archive entry rejected",
               lambda r: rewrite_zip(r, lambda e: e + [("unexpected-root/", b"")]), run_ci=True)
    a.mutation("A07", "archive", "Traversal-shaped directory entry with payload rejected",
               lambda r: rewrite_zip(r, lambda e: e + [("../outside/", b"audit marker, never extracted")]), run_ci=True)
    a.mutation("A08", "archive", "Corrupt member CRC rejected", corrupt_crc, run_ci=True)
    a.mutation("A09", "archive", "Non-ZIP artifact rejected",
               lambda r: (r / DIST).write_bytes(b"not a zip archive"), run_ci=True)
    a.mutation("A10", "archive", "Wrong archive root rejected",
               lambda r: rewrite_zip(r, lambda e: [(n.replace(NAME, "wrong-root"), b) for n, b in e]), run_ci=True)

    a.mutation("S01", "staleness", "Source change with stale dist rejected by validator",
               lambda r: write_text(r / SKILL, (r / SKILL).read_text(encoding="utf-8") + "\n<!-- audit staleness marker -->\n"),
               run_ci=True)
    a.mutation("S02", "staleness", "Metadata change with stale dist rejected by validator",
               lambda r: write_text(r / AGENT, (r / AGENT).read_text(encoding="utf-8") + "\n# audit marker\n"),
               run_ci=True)

    a.mutation("V01", "release", "Plugin version mismatch rejected",
               lambda r: edit_json(r, PLUGIN, lambda d: d.update(version="0.0.0")), run_ci=True)
    a.mutation("V02", "release", "README current version mismatch rejected",
               lambda r: write_text(r / "README.md", (r / "README.md").read_text(encoding="utf-8").replace(
                   "## What's New in v0.7.1", "## What's New in v0.0.0")), run_ci=True)
    a.mutation("V03", "release", "README release asset mismatch rejected",
               lambda r: write_text(r / "README.md", (r / "README.md").read_text(encoding="utf-8").replace(
                   "/releases/download/v0.7.1/", "/releases/download/v0.0.0/")), run_ci=True)
    a.mutation("V04", "release", "Malformed VERSION rejected", lambda r: write_text(r / "VERSION", "garbage\n"))

    def version_sync(r, value):
        old = (r / "VERSION").read_text(encoding="utf-8").strip()
        write_text(r / "VERSION", value + "\n")
        edit_json(r, PLUGIN, lambda d: d.update(version=value))
        for path in ("README.md", "CHANGELOG.md"):
            write_text(r / path, (r / path).read_text(encoding="utf-8").replace(old, value))

    a.mutation("V05", "release", "SemVer core leading zero rejected",
               lambda r: version_sync(r, "00.7.1"), run_ci=True)
    a.mutation("V06", "release", "Non-ASCII VERSION digits rejected",
               lambda r: version_sync(r, "\u0660.7.1"), run_ci=True)
    a.mutation("V07", "release", "Missing changelog rejected",
               lambda r: (r / "CHANGELOG.md").unlink(), run_ci=True)
    a.mutation("V08", "release", "Missing current dated changelog entry rejected",
               lambda r: write_text(r / "CHANGELOG.md", "# Changelog\n\n## Unreleased\n"), run_ci=True)
    a.mutation("V09", "release", "Accumulated old What's New section rejected",
               lambda r: write_text(r / "README.md", (r / "README.md").read_text(encoding="utf-8") +
                                    "\n## What's New in v0.0.0\n\nOld release summary.\n"), run_ci=True)

    def hidden_readme(r):
        text = (r / "README.md").read_text(encoding="utf-8")
        text = text.replace("## What's New in v0.7.1", "## What's New in v0.0.0")
        text = text.replace("/releases/download/v0.7.1/", "/releases/download/v0.0.0/")
        text += f"\n<!-- ## What's New in v0.7.1 /releases/download/v0.7.1/{NAME}.skill -->\n"
        write_text(r / "README.md", text)

    a.mutation("V10", "release", "Stale visible release references hidden by HTML comment rejected",
               hidden_readme, run_ci=True)
    a.mutation("V11", "release", "Malformed plugin JSON rejected",
               lambda r: write_text(r / PLUGIN, "{not json"))
    a.mutation("V12", "release", "Plugin root array rejected",
               lambda r: write_json(r / PLUGIN, []))

    def eval_change(test_id, invariant, change, ci=False, expected_accept=False):
        a.mutation(test_id, "eval-schema", invariant,
                   lambda r: edit_json(r, CASES, change), run_ci=ci, expected_accept=expected_accept)

    eval_change("E01", "Unsupported schema version rejected", lambda d: d.update(schema_version=2))
    eval_change("E02", "Boolean schema version rejected", lambda d: d.update(schema_version=True), True)
    eval_change("E03", "Characterize numerically equivalent schema version 1.0 (integer lexical form not required)",
                lambda d: d.update(schema_version=1.0), True, None)
    eval_change("E04", "Fewer than six cases rejected", lambda d: d.update(cases=d["cases"][:5]))
    eval_change("E05", "Duplicate case ID rejected", lambda d: d["cases"][1].update(id=d["cases"][0]["id"]))
    eval_change("E06", "Empty case ID rejected", lambda d: d["cases"][0].update(id=""))
    eval_change("E07", "Characterize whitespace ID (non-empty, but trimming policy not specified)",
                lambda d: d["cases"][0].update(id="   "), True, None)
    eval_change("E08", "Invalid mode rejected", lambda d: d["cases"][0].update(mode="invalid"))
    eval_change("E09", "Blank prompt rejected", lambda d: d["cases"][0].update(prompt=" \n\t"))
    eval_change("E10", "Numeric prompt rejected", lambda d: d["cases"][0].update(prompt=9))
    eval_change("E11", "Empty assertions rejected", lambda d: d["cases"][0].update(assertions=[]))
    eval_change("E12", "Non-string assertion rejected", lambda d: d["cases"][0].update(assertions=[5]))
    eval_change("E13", "Blank failure condition rejected", lambda d: d["cases"][0].update(failure_conditions=[" "]))
    eval_change("E14", "Missing failure_conditions rejected", lambda d: d["cases"][0].pop("failure_conditions"))
    eval_change("E15", "Cases object instead of array rejected", lambda d: d.update(cases={}))
    eval_change("E16", "Null case element rejected", lambda d: d["cases"].__setitem__(0, None))
    eval_change("E17", "List-valued mode rejected", lambda d: d["cases"][0].update(mode=[]))
    a.mutation("E18", "eval-schema", "Malformed eval JSON rejected", lambda r: write_text(r / CASES, "{bad"))
    a.mutation("E19", "eval-schema", "Array eval root rejected", lambda r: write_json(r / CASES, []))

    root = a.fresh("R01")
    hashes, variants = [], []
    for variant in ("baseline", "repeat", "changed-mtime", "crlf", "lf", "reversed-file-creation", "changed-process-env"):
        if variant == "changed-mtime":
            for path in (root / f"skills/{NAME}").rglob("*"):
                if path.is_file():
                    os.utime(path, (1234567890, 1234567890))
        if variant in {"crlf", "lf"}:
            for rel in (SKILL, AGENT):
                data = (root / rel).read_bytes().replace(b"\r\n", b"\n")
                (root / rel).write_bytes(data.replace(b"\n", b"\r\n") if variant == "crlf" else data)
        if variant == "reversed-file-creation":
            values = {rel: (root / rel).read_bytes() for rel in (SKILL, AGENT)}
            for rel in values:
                (root / rel).unlink()
            for rel in reversed(values):
                (root / rel).write_bytes(values[rel])
        env = {"PYTHONHASHSEED": "47", "TZ": "Pacific/Honolulu", "SOURCE_DATE_EPOCH": "1"} if variant == "changed-process-env" else None
        build = a.run("R01", root, ["python", "scripts/package_skill.py"], env)
        check = a.validate("R01", root)
        hashes.append(digest((root / DIST).read_bytes()))
        variants.append({"variant": variant, "sha256": hashes[-1], "build_exit": build["exit_code"],
                         "validation_exit": check["exit_code"]})
    a.record("R01", "reproducibility", "Seven same-runtime builds remain byte-identical across metadata/order/newline/env changes",
             len(set(hashes)) == 1 and all(v["build_exit"] == v["validation_exit"] == 0 for v in variants),
             {"variants": variants, "unique_hashes": len(set(hashes)), "archive": archive_evidence(root)})

    root = a.fresh("P01")
    before = archive_evidence(root)
    (root / AGENT).write_bytes(b"\xffinvalid UTF-8\n")
    pre = a.validate("P01", root)
    package = a.package("P01", root)
    after = archive_evidence(root)
    post = a.validate("P01", root)
    a.record("P01", "failure-atomicity", "Failed UTF-8 build preserves last good dist archive",
             package["exit_code"] != 0 and before["sha256"] == after.get("sha256"),
             {"validation_before_exit": pre["exit_code"], "package_exit": package["exit_code"],
              "validation_after_exit": post["exit_code"], "before": before, "after": after}, root)

    root = a.fresh("P02")
    before = archive_evidence(root)
    # A simple rename remains strictly inside this fresh temp fixture.
    (root / f"skills/{NAME}").rename(root / "skills/temporarily-absent")
    package = a.package("P02", root)
    after = archive_evidence(root)
    a.record("P02", "failure-atomicity", "Missing source build fails without replacing dist",
             package["exit_code"] != 0 and before["sha256"] == after["sha256"],
             {"package_exit": package["exit_code"], "before": before, "after": after})


def save_results(a, environment, source_before, source_after, elapsed, error):
    counts = dict(Counter(r["status"] for r in a.results))
    categories = {}
    for r in a.results:
        categories.setdefault(r["category"], Counter())[r["status"]] += 1
    ci = [r for r in a.results if "ci" in r["evidence"]]
    summary = {"tests": len(a.results), "counts": counts, "categories": categories,
               "subprocess_commands": len(a.commands), "ci_scenarios": len(ci),
               "ci_accepted": sum(r["evidence"]["ci"]["accepted"] for r in ci),
               "ci_rejected": sum(not r["evidence"]["ci"]["accepted"] for r in ci),
               "elapsed_seconds": round(elapsed, 3), "harness_error": error,
               "production_files_unchanged": source_before == source_after}
    write_json(a.output / "results.json", {"environment": environment, "summary": summary,
                                          "tests": a.results, "commands": a.commands})
    write_json(a.output / "source-manifest.json", {"before": source_before, "after": source_after,
                                                 "unchanged": source_before == source_after})
    transcript = []
    for record in a.commands:
        transcript.extend([f"[{record['index']:03d}] {record['test_id']} cwd={record['cwd']}",
                           "$ " + record["command"], "exit=" + str(record["exit_code"]),
                           "stdout:\n" + record["stdout"], "stderr:\n" + record["stderr"], ""])
    write_text(a.output / "commands.txt", "\n".join(transcript))
    matrix = ["# Executed Audit Matrix", "", "PASS means the stated invariant held; FAIL is a reproduced audit defect, not a harness crash. OBSERVED records behavior without asserting an undocumented requirement.", "",
              "| ID | Category | Result | Validator exit | CI exits | Invariant |",
              "| --- | --- | --- | --- | --- | --- |"]
    for record in a.results:
        evidence = record["evidence"]
        matrix.append(f"| {record['id']} | {record['category']} | {record['status']} | "
                      f"{evidence.get('validator_exit', '-')} | {evidence.get('ci', {}).get('exit_codes', '-')} | "
                      f"{record['invariant']} |")
    matrix.extend(["", "```json", json.dumps(summary, indent=2), "```", ""])
    write_text(a.output / "matrix.md", "\n".join(matrix))
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output", type=Path, default=None,
                        help="Must be inside the authorized packaging results directory or OS temp directory")
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (args.output or repo / OUTPUT).resolve()
    allowed = (repo / OUTPUT).resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if not (output == allowed or allowed in output.parents or temp_root in output.parents):
        parser.error(f"Output outside authorized area: {output}")
    output.mkdir(parents=True, exist_ok=True)
    source_before = manifest(repo)
    started = time.monotonic()
    with temporary_workspace() as temp_path:
        temp_name = str(temp_path)
        a = Audit(repo, output, temp_path)
        environment = {"utc_started": datetime.now(timezone.utc).isoformat(),
                       "repo": str(repo), "python": sys.version, "executable": sys.executable,
                       "platform": platform.platform(), "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
                       "pyyaml": getattr(yaml, "__version__", None), "temp_root": temp_name,
                       "invocation": subprocess.list2cmdline([sys.executable] + sys.argv),
                       "git_env_isolated": True, "dependencies_installed": False}
        for key, command in [("git_head", ["git", "rev-parse", "HEAD"]),
                             ("git_version", ["git", "--version"]),
                             ("subprocess_python", ["python", "-c", "import sys; print(sys.executable); print(sys.version)"]),
                             ("git_status_before", ["git", "status", "--short"])]:
            record = a.run("ENV", repo, command)
            environment[key] = record["stdout"].strip()
        environment["snapshot_manifest_matches_source"] = manifest(a.snapshot) == source_before
        error = None
        try:
            if not environment["snapshot_manifest_matches_source"]:
                raise RuntimeError("Repository changed while taking the temp snapshot")
            run_suite(a)
        except Exception:
            error = traceback.format_exc()
        source_after = manifest(repo)
        record = a.run("ENV", repo, ["git", "status", "--short"])
        environment["git_status_after"] = record["stdout"].strip()
        excerpts = []
        for relative in SOURCES:
            excerpts.extend([f"===== {relative} =====", *[
                f"{index:4}: {line}" for index, line in enumerate((repo / relative).read_text(encoding="utf-8").splitlines(), 1)], ""])
        write_text(output / "source-lines.txt", "\n".join(excerpts))
        summary = save_results(a, environment, source_before, source_after, time.monotonic() - started, error)
    if error or not summary["production_files_unchanged"]:
        return 2
    return 1 if summary["counts"].get("FAIL", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
