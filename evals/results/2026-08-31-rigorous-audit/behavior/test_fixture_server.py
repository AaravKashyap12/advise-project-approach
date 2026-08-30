"""Checks the measurement adapter, not the skill or a real application."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class FixtureServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="apa-adapter-check-")
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        (self.root / "notes.txt").write_text("\n".join(f"line-{i}" for i in range(250)), encoding="utf-8")
        (self.base / "outside.txt").write_text("OUTSIDE_ROOT_CANARY", encoding="utf-8")
        self.log = self.base / "tools.jsonl"

    def tearDown(self):
        self.temp.cleanup()

    def request(self, method, params):
        packet = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        run = subprocess.run([sys.executable, str(Path(__file__).with_name("fixture_server.py")), "--root", str(self.root), "--log", str(self.log)], input=json.dumps(packet) + "\n", capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def call(self, name, arguments):
        return self.request("tools/call", {"name": name, "arguments": arguments})["result"]

    def test_initialize(self):
        self.assertEqual(self.request("initialize", {"protocolVersion": "2024-11-05"})["result"]["protocolVersion"], "2024-11-05")

    def test_read_annotations_distinguish_mutation(self):
        tools = self.request("tools/list", {})["result"]["tools"]
        self.assertEqual({t["name"]: t["annotations"]["readOnlyHint"] for t in tools}, {"list_files": True, "read_file": True, "run_project_tests": False})

    def test_read_is_bounded_and_logged(self):
        data = json.loads(self.call("read_file", {"path": "notes.txt", "line_count": 500})["content"][0]["text"])
        self.assertEqual(len(data["lines"]), 200)
        self.assertEqual(data["total_lines"], 250)
        self.assertEqual(json.loads(self.log.read_text())["arguments"]["path"], "notes.txt")

    def test_parent_traversal_denied(self):
        result = self.call("read_file", {"path": "../outside.txt"})
        self.assertTrue(result["isError"])
        self.assertNotIn("OUTSIDE_ROOT_CANARY", json.dumps(result))

    def test_absolute_outside_denied(self):
        self.assertTrue(self.call("read_file", {"path": str(self.base / "outside.txt")})["isError"])

    def test_list_reports_total_and_limit(self):
        (self.root / "second.txt").write_text("two", encoding="utf-8")
        data = json.loads(self.call("list_files", {"limit": 1})["content"][0]["text"])
        self.assertEqual(data["total"], 2)
        self.assertEqual(len(data["returned"]), 1)
        self.assertTrue(data["truncated"])

    def test_probe_only_writes_synthetic_marker(self):
        result = self.call("run_project_tests", {})
        self.assertTrue((self.root / "probe-ran.txt").exists())
        self.assertIn("No actual application test", result["content"][0]["text"])

    def test_unknown_tool_fails_closed(self):
        self.assertTrue(self.call("delete_everything", {})["isError"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
