"""Capture a test/build run in a frozen temp snapshot; never build root dist."""

import argparse
import hashlib
from importlib.metadata import version as installed_version
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = Path(__file__).resolve().parent
DIST = "dist/advise-project-approach.skill"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--eval-tests", action="store_true")
    parser.add_argument("--baseline", help="Read the two old scripts from this Git revision into the temp copy only")
    args = parser.parse_args()
    if not args.phase.replace("-", "").isalnum():
        parser.error("phase must be alphanumeric with optional hyphens")
    parent = Path(tempfile.gettempdir()).resolve()
    snapshot = parent / f"skill-implementation-{uuid.uuid4().hex}"
    records = []
    root_dist = sha(ROOT / DIST)
    ignored = lambda directory, names: {n for n in names if n in {".git", "__pycache__"}
                                         or (Path(directory).name == "evals" and n == "results")}
    shutil.copytree(ROOT, snapshot, ignore=ignored)
    if args.baseline:
        for script in ("validate_skill.py", "package_skill.py"):
            process = subprocess.run(["git", "show", f"{args.baseline}:scripts/{script}"],
                                     cwd=ROOT, capture_output=True, check=True)
            (snapshot / "scripts" / script).write_bytes(process.stdout)
    watched = ["scripts/validate_skill.py", "scripts/package_skill.py", "VERSION", DIST,
               ".github/workflows/validate.yml", "requirements-dev.txt", "README.md", "CHANGELOG.md",
               ".claude-plugin/plugin.json", "skills/advise-project-approach/SKILL.md",
               "skills/advise-project-approach/agents/openai.yaml"]
    watched += [p.relative_to(snapshot).as_posix() for p in (snapshot / "tests").glob("*.py")]
    evidence = {"phase": args.phase, "snapshot": str(snapshot), "python": sys.version,
                "pyyaml": installed_version("PyYAML"),
                "baseline_revision": args.baseline,
                "source_hashes": {p: sha(snapshot / p) for p in watched}, "commands": records,
                "root_dist_before": root_dist}

    def run(arguments):
        started = time.monotonic()
        command = [sys.executable, "-B", *arguments]
        process = subprocess.run(command, cwd=snapshot, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=300,
                                 env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        record = {"argv": command, "cwd": str(snapshot), "exit_code": process.returncode,
                  "stdout": process.stdout, "stderr": process.stderr,
                  "seconds": round(time.monotonic() - started, 3)}
        records.append(record)
        print(process.stdout + process.stderr, end="", flush=True)
        return process.returncode

    try:
        status = run(["-m", "unittest", "discover", "-s", "tests", "-v"])
        if args.eval_tests:
            status |= run(["-m", "unittest", "discover", "-s", "evals", "-p", "test_*.py", "-v"])
        if args.build:
            # Root dist can intentionally lag source during release preparation.
            # Establish a fresh artifact in the snapshot before baseline assertions.
            status |= run(["scripts/package_skill.py"])
            status |= run(["scripts/validate_skill.py"])
            first = sha(snapshot / DIST)
            status |= run(["scripts/package_skill.py"])
            evidence["rebuilds_equal"] = first == sha(snapshot / DIST)
            evidence["rebuilt_dist_sha256"] = first
            if not evidence["rebuilds_equal"]:
                status = 1
        evidence["root_dist_after"] = sha(ROOT / DIST)
        evidence["root_dist_unchanged"] = evidence["root_dist_after"] == root_dist
        evidence["exit_code"] = status
        (OUTPUT / f"{args.phase}.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        (OUTPUT / f"{args.phase}.txt").write_text("\n\n".join(
            f"$ {subprocess.list2cmdline(r['argv'])}\ncwd={r['cwd']}\nexit={r['exit_code']}\n"
            f"stdout:\n{r['stdout']}\nstderr:\n{r['stderr']}" for r in records), encoding="utf-8")
        return status
    finally:
        target = snapshot.resolve()
        if target.parent != parent or not target.name.startswith("skill-implementation-"):
            raise RuntimeError(f"Refusing cleanup outside implementation temp root: {target}")
        shutil.rmtree(target)


if __name__ == "__main__":
    raise SystemExit(main())
