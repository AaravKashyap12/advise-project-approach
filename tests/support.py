"""Small real repositories for exercising the two public script entry points."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
import warnings
from zipfile import ZIP_STORED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
NAME = "advise-project-approach"
SKILL = f"skills/{NAME}/SKILL.md"
AGENT = f"skills/{NAME}/agents/openai.yaml"
DIST = f"dist/{NAME}.skill"
PLUGIN = ".claude-plugin/plugin.json"
CASES = "evals/cases.json"


class RepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_parent = Path(tempfile.gettempdir()).resolve()
        # Inherit Windows sandbox ACLs rather than mkdtemp's owner-only ACL.
        self.repo = self.temp_parent / f"skill-test-{uuid.uuid4().hex}"
        self.repo.mkdir()
        self.addCleanup(self.remove_fixture)
        self.version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for script in ("package_skill.py", "validate_skill.py"):
            destination = self.repo / "scripts" / script
            destination.parent.mkdir(exist_ok=True)
            shutil.copyfile(ROOT / "scripts" / script, destination)
        self.frontmatter(f"name: {NAME}\ndescription: Test fixture")
        self.write(AGENT, 'interface:\n  display_name: "Test fixture"\n')
        self.write("AGENTS.md", "# Repository guidance\n")
        self.write("CLAUDE.md", "@AGENTS.md\n")
        self.write_json(PLUGIN, {"name": NAME, "version": self.version,
                                "skills": [f"./skills/{NAME}"],
                                "repository": f"https://github.com/example/{NAME}"})
        self.set_version(self.version)
        self.write_json(CASES, {"schema_version": 1, "cases": [
            {"id": f"case-{i}", "mode": "pre-build", "prompt": "Fixture prompt",
             "assertions": ["Fixture assertion"], "failure_conditions": ["Fixture failure"]}
            for i in range(6)
        ]})
        self.sync_archive()

    def remove_fixture(self):
        target = self.repo.resolve()
        if target.parent != self.temp_parent or not target.name.startswith("skill-test-"):
            raise RuntimeError(f"Refusing cleanup outside test fixture: {target}")
        shutil.rmtree(target)

    def write(self, relative, text):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def write_json(self, relative, data):
        self.write(relative, json.dumps(data, ensure_ascii=True) + "\n")

    def read_json(self, relative):
        return json.loads((self.repo / relative).read_text(encoding="utf-8"))

    def frontmatter(self, fields):
        self.write(SKILL, f"---\n{fields}\n---\n\n# Test fixture\n")

    def set_version(self, version):
        self.version = version
        self.write("VERSION", version + "\n")
        plugin = self.read_json(PLUGIN)
        plugin["version"] = version
        self.write_json(PLUGIN, plugin)
        self.write("README.md", f"# Test fixture\n\n## What's New in v{version}\n\n"
                   f"Fixture changes.\n\n[Download]({plugin['repository']}/releases/download/v{version}/{NAME}.skill)\n")
        self.write("CHANGELOG.md", f"# Changelog\n\n## Unreleased\n\n## {version} - 2026-01-01\n\n- Fixture change.\n")

    def sync_archive(self):
        entries = [(f"{NAME}/SKILL.md", (self.repo / SKILL).read_text(encoding="utf-8").encode()),
                   (f"{NAME}/agents/openai.yaml", (self.repo / AGENT).read_text(encoding="utf-8").encode())]
        self.write_archive(entries)

    def write_archive(self, entries):
        (self.repo / "dist").mkdir(exist_ok=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(self.repo / DIST, "w", compression=ZIP_STORED) as archive:
                for name, payload in entries:
                    archive.writestr(name, payload)

    def archive_entries(self):
        with ZipFile(self.repo / DIST) as archive:
            return [(info.filename, archive.read(info)) for info in archive.infolist()]

    def run_python(self, *args):
        return subprocess.run([sys.executable, "-B", *args], cwd=self.repo,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                              capture_output=True, text=True, encoding="utf-8", timeout=20)

    def validate(self):
        return self.run_python("scripts/validate_skill.py")

    def package(self):
        return self.run_python("scripts/package_skill.py")

    def assert_valid(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_invalid(self, message):
        result = self.validate()
        self.assertNotEqual(result.returncode, 0, "Validator accepted invalid fixture")
        self.assertIn("Validation failed:", result.stderr)
        self.assertIn(message.lower(), result.stderr.lower())
        self.assertNotIn("Traceback", result.stderr)
