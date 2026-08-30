"""Deterministic lifecycle and comparison tests; never use real model credentials."""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid


TOOLS = Path(os.environ.get("EVAL_TOOLING_SOURCE", Path(__file__).parent)).resolve()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ToolingCase(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.gettempdir()).resolve() / ("apa-tooling-test-" + uuid.uuid4().hex)
        self.base.mkdir()
        self.addCleanup(self.cleanup)
        self.evals = self.base / "program/evals"
        (self.evals / "fixtures").mkdir(parents=True)
        for filename in ("run_behavior.py", "prepare_comparison.py"):
            shutil.copyfile(TOOLS / filename, self.evals / filename)
        shutil.copyfile(Path(__file__).parent / "fixtures/fixture_server.py", self.evals / "fixtures/fixture_server.py")
        self.case = {"id": "probe-case", "fixture": "app", "prompt": "Review app.py without execution.", "criteria": ["Inspect the file."]}
        self.suite = {"model": "fake-model", "reasoning_effort": "medium", "cases": [self.case]}
        self.write_suite()
        (self.evals / "comparison-rubric.md").write_text("Judge the supplied evidence.", encoding="utf-8")
        self.skill = self.base / "candidate.md"
        self.skill.write_text("Synthetic skill instructions.\n", encoding="utf-8")
        self.host = self.base / "host"
        (self.host / ".agents/skills/example").mkdir(parents=True)
        (self.host / ".agents/skills/example/SKILL.md").write_text("Synthetic installed skill")
        (self.host / ".codex").mkdir()
        (self.host / ".codex/auth.json").write_text('{"token":"FAKE_CI_TOKEN"}')
        self.runner = load_module("run_behavior", self.evals / "run_behavior.py")
        self.runner.SKILL = self.skill
        with patch.dict(sys.modules, {"run_behavior": self.runner}):
            self.comparison = load_module("prepare_comparison", self.evals / "prepare_comparison.py")
        self.output = self.base / "evidence"
        self.cli_version = "fake-codex 1"
        self.rg_available = True
        self.rg_fails = False
        self.case_timeout = False
        self.probe_fails = False
        self.version_fails = False
        self.interrupt_executor = False
        self.calls = []
        self.temps = []
        self.configs = []
        self.real_copy = shutil.copyfile

    def cleanup(self):
        target = self.base.resolve()
        if target.parent != Path(tempfile.gettempdir()).resolve() or not target.name.startswith("apa-tooling-test-"):
            raise RuntimeError("Unsafe test cleanup target")
        shutil.rmtree(target)

    def write_suite(self):
        (self.evals / "fixtures/scenarios.json").write_text(json.dumps(self.suite), encoding="utf-8")

    def temporary(self, **kwargs):
        path = self.base / ("temporary-" + str(len(self.temps)))
        path.mkdir()
        self.temps.append(path)
        return str(path)

    def which(self, name):
        return ("FAKE-RG" if self.rg_available else None) if name == "rg" else "FAKE-CODEX"

    def execute(self, command, **kwargs):
        if command[0] in ("rg", "FAKE-RG"):
            if not self.rg_available:
                raise FileNotFoundError("rg unavailable")
            root = Path(command[-1])
            paths = "\n".join(str(path) for path in root.rglob("SKILL.md"))
            return subprocess.CompletedProcess(command, 2 if self.rg_fails else 0, "" if self.rg_fails else paths, "")
        self.assertEqual(command[0], "FAKE-CODEX", "A real executor must never be launched")
        if "--version" in command:
            if self.version_fails:
                raise OSError("injected version failure")
            return subprocess.CompletedProcess(command, 0, self.cli_version, "")
        self.calls.append(command)
        self.configs.append((Path(kwargs["env"]["CODEX_HOME"]) / "config.toml").read_text())
        if self.interrupt_executor:
            raise KeyboardInterrupt("synthetic Python interrupt")
        answer = Path(command[command.index("-o") + 1])
        if answer.name == "isolation-probe-answer.txt":
            answer.write_text(json.dumps({"skills": ["unexpected"] if self.probe_fails else [], "probe": "APA_READ_PROBE_42"}))
            return subprocess.CompletedProcess(command, 0, "", "")
        if self.case_timeout:
            raise subprocess.TimeoutExpired(command, 1, output="", stderr="synthetic timeout")
        answer.write_text("Neutral synthetic answer", encoding="utf-8")
        work = command[command.index("-C") + 1]
        tool = {"tool": "read_file", "arguments": {"path": work + "/app.py"}, "result": {"path": work + "/app.py", "nested": [{"source": work + "/app.py"}]}}
        (answer.parent / "tool-calls.jsonl").write_text(json.dumps(tool) + "\n", encoding="utf-8")
        trace = [ {"type": "item.completed", "item": {"type": "agent_message", "text": "Neutral synthetic answer"}}, {"type": "turn.completed", "usage": {"input_tokens": 1}} ]
        return subprocess.CompletedProcess(command, 0, "\n".join(map(json.dumps, trace)), "")

    def invoke(self, *extra, output=None):
        argv = ["run_behavior.py", "--output", str(output or self.output), "--skill-file", str(self.skill), "--cases", "probe-case", "--repeats", "1", *extra]
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(sys, "argv", argv))
            stack.enter_context(patch.object(self.runner.shutil, "which", side_effect=self.which))
            stack.enter_context(patch.object(self.runner.tempfile, "mkdtemp", side_effect=self.temporary))
            stack.enter_context(patch.object(self.runner.subprocess, "run", side_effect=self.execute))
            stack.enter_context(patch.object(Path, "home", return_value=self.host))
            stack.enter_context(patch.dict(os.environ, {"CODEX_HOME": str(self.host / ".codex")}))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            return self.runner.main()

    def rejected(self, action):
        try:
            code = action()
        except (SystemExit, ValueError) as exc:
            self.assertNotEqual(getattr(exc, "code", 1), 0)
        else:
            self.assertIsInstance(code, int, "Invalid evidence was accepted without an error")
            self.assertNotEqual(code, 0, "Invalid evidence was accepted")

    def no_copied_auth(self):
        self.assertFalse(list(self.base.glob("temporary-*/codex-home/auth.json")))
        self.assertEqual((self.host / ".codex/auth.json").read_text(), '{"token":"FAKE_CI_TOKEN"}')

    def run_dir(self, output=None, condition="treatment"):
        return (output or self.output) / "runs" / f"probe-case--r1--{condition}"

    def compare(self, control, candidate, output=None):
        target = output or self.base / "packets"
        argv = ["prepare_comparison.py", "--control", str(control), "--candidate", str(candidate), "--output", str(target), "--cases", "probe-case", "--repeats", "1"]
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            self.comparison.main()
        return target

    def pair(self):
        control, candidate = self.base / "control", self.base / "candidate"
        self.assertEqual(self.invoke("--conditions", "baseline", output=control), 0)
        self.skill.write_text("Different treatment instructions.\n", encoding="utf-8")
        self.assertEqual(self.invoke(output=candidate), 0)
        return control, candidate


class RunnerTests(ToolingCase):
    def test_cleanup_covers_partial_credential_copy(self):
        def broken_copy(source, target, *args, **kwargs):
            if Path(source).name == "auth.json":
                Path(target).write_text("PARTIAL_FAKE_CREDENTIAL")
                raise OSError("injected partial credential copy")
            return self.real_copy(source, target, *args, **kwargs)
        with patch.object(self.runner.shutil, "copyfile", side_effect=broken_copy):
            with self.assertRaises(OSError):
                self.invoke()
        self.no_copied_auth()

    def test_cleanup_covers_configuration_write_failure(self):
        original = self.runner.put
        def broken_put(path, content):
            if Path(path).name == "config.toml":
                raise OSError("injected configuration failure")
            return original(path, content)
        with patch.object(self.runner, "put", side_effect=broken_put), self.assertRaises(OSError):
            self.invoke()
        self.no_copied_auth()

    def test_cleanup_covers_version_command_failure(self):
        self.version_fails = True
        with self.assertRaises(OSError):
            self.invoke()
        self.no_copied_auth()

    def test_cleanup_covers_failed_isolation_probe(self):
        self.probe_fails = True
        self.rejected(self.invoke)
        self.no_copied_auth()

    def test_cleanup_covers_keyboard_interrupt_after_auth_copy(self):
        self.interrupt_executor = True
        with self.assertRaises(KeyboardInterrupt):
            self.invoke()
        self.assertEqual(len(self.calls), 1)
        self.no_copied_auth()
        self.assertFalse((self.output / ".run.lock").exists())

    def test_cleanup_covers_post_copy_configuration_failure(self):
        original = self.runner.put
        config_writes = 0
        def broken_put(path, content):
            nonlocal config_writes
            if Path(path).name == "config.toml":
                config_writes += 1
                if config_writes == 2:
                    raise OSError("injected post-copy setup failure")
            return original(path, content)
        with patch.object(self.runner, "put", side_effect=broken_put), self.assertRaises(OSError):
            self.invoke()
        self.no_copied_auth()

    def test_rg_is_optional(self):
        self.rg_available = False
        self.assertEqual(self.invoke(), 0)
        self.assertIn("example", self.configs[0])
        self.no_copied_auth()

    def test_rg_error_falls_back_to_filesystem_discovery(self):
        self.rg_fails = True
        self.assertEqual(self.invoke(), 0)
        self.assertIn("example", self.configs[0])

    def test_new_output_must_be_empty(self):
        self.output.mkdir()
        (self.output / "kept.txt").write_text("KEEP")
        self.rejected(self.invoke)
        self.assertEqual(self.calls, [])
        self.assertEqual((self.output / "kept.txt").read_text(), "KEEP")

    def test_resume_requires_manifest(self):
        target = self.run_dir()
        target.mkdir(parents=True)
        (target / "result.json").write_text('{"status":"completed","skill_sha256":"foreign"}')
        self.rejected(lambda: self.invoke("--resume"))
        self.assertEqual(self.calls, [])
        self.assertFalse((self.output / "manifest.json").exists())

    def test_resume_rejects_foreign_result(self):
        self.assertEqual(self.invoke(), 0)
        result = self.run_dir() / "result.json"
        data = json.loads(result.read_text())
        data["skill_sha256"] = "foreign"
        result.write_text(json.dumps(data))
        self.calls.clear()
        self.rejected(lambda: self.invoke("--resume"))
        self.assertEqual(self.calls, [])

    def test_resume_rejects_changed_cli_without_relabeling(self):
        self.assertEqual(self.invoke(), 0)
        before = (self.output / "manifest.json").read_bytes()
        self.cli_version = "fake-codex 2"
        self.calls.clear()
        self.rejected(lambda: self.invoke("--resume"))
        self.assertEqual(self.calls, [])
        self.assertEqual((self.output / "manifest.json").read_bytes(), before)

    def test_resume_rejects_changed_runner(self):
        self.assertEqual(self.invoke(), 0)
        with (self.evals / "run_behavior.py").open("a") as handle:
            handle.write("\n# changed fixture generator or execution logic\n")
        self.rejected(lambda: self.invoke("--resume"))

    def test_resume_rejects_changed_timeout(self):
        self.assertEqual(self.invoke(), 0)
        self.rejected(lambda: self.invoke("--resume", "--timeout", "151"))

    def test_failed_case_remains_nonzero_on_resume(self):
        self.case_timeout = True
        self.assertEqual(self.invoke(), 2)
        before = (self.run_dir() / "result.json").read_bytes()
        self.case_timeout = False
        self.calls.clear()
        self.rejected(lambda: self.invoke("--resume"))
        self.assertEqual((self.run_dir() / "result.json").read_bytes(), before)
        self.assertEqual(self.calls, [])

    def test_completed_resume_preserves_manifest(self):
        self.assertEqual(self.invoke(), 0)
        before = (self.output / "manifest.json").read_bytes()
        self.assertEqual(self.invoke("--resume"), 0)
        self.assertEqual((self.output / "manifest.json").read_bytes(), before)
        self.no_copied_auth()

    def test_reasoning_configuration_drives_both_commands(self):
        self.suite["reasoning_effort"] = "high"
        self.write_suite()
        self.assertEqual(self.invoke(), 0)
        self.assertEqual(len(self.calls), 2)
        for command in self.calls:
            self.assertIn('model_reasoning_effort="high"', command)

    def test_resume_rejects_tampered_answer(self):
        self.assertEqual(self.invoke(), 0)
        (self.run_dir() / "answer.txt").write_text("Different answer")
        self.rejected(lambda: self.invoke("--resume"))

    def test_resume_rejects_missing_answer(self):
        self.assertEqual(self.invoke(), 0)
        (self.run_dir() / "answer.txt").unlink()
        self.rejected(lambda: self.invoke("--resume"))

    def test_resume_rejects_partial_run_directory(self):
        self.assertEqual(self.invoke(), 0)
        (self.run_dir() / "result.json").unlink()
        self.rejected(lambda: self.invoke("--resume"))

    def test_resume_rejects_changed_source(self):
        self.assertEqual(self.invoke(), 0)
        self.skill.write_text("Changed source")
        self.rejected(lambda: self.invoke("--resume"))

    def test_resume_rejects_changed_fixture_adapter(self):
        self.assertEqual(self.invoke(), 0)
        with (self.evals / "fixtures/fixture_server.py").open("a") as handle:
            handle.write("\n# changed adapter\n")
        self.rejected(lambda: self.invoke("--resume"))

    def test_snapshot_backed_fixture_adapter_is_executed(self):
        self.assertEqual(self.invoke(), 0)
        self.assertTrue(all("fixture-server-snapshot.py" in config for config in self.configs))

    def test_resume_rejects_tampered_source_snapshot(self):
        self.assertEqual(self.invoke(), 0)
        (self.output / "skill-snapshot.md").write_text("Different frozen instructions")
        self.rejected(lambda: self.invoke("--resume"))

    def test_resume_rejects_changed_executed_command(self):
        self.assertEqual(self.invoke(), 0)
        path = self.run_dir() / "result.json"
        result = json.loads(path.read_text())
        result["command"][result["command"].index("--model") + 1] = "another-model"
        path.write_text(json.dumps(result))
        self.rejected(lambda: self.invoke("--resume"))

    def test_resume_can_add_new_completed_runs_without_mutating_prior_evidence(self):
        self.assertEqual(self.invoke(), 0)
        before = {path.name: path.read_bytes() for path in self.run_dir().iterdir()}
        manifest = (self.output / "manifest.json").read_bytes()
        self.assertEqual(self.invoke("--resume", "--repeats", "2"), 0)
        self.assertEqual({path.name: path.read_bytes() for path in self.run_dir().iterdir()}, before)
        self.assertEqual((self.output / "manifest.json").read_bytes(), manifest)
        self.assertTrue((self.output / "runs/probe-case--r2--treatment/result.json").exists())


class ComparisonTests(ToolingCase):
    def test_matching_runs_generate_two_orders(self):
        control, candidate = self.pair()
        target = self.compare(control, candidate)
        first = json.loads((target / "packet-order-1.json").read_text())["pairs"][0]
        second = json.loads((target / "packet-order-2.json").read_text())["pairs"][0]
        self.assertEqual(first["A"], second["B"])
        self.assertEqual(first["B"], second["A"])

    def test_uses_saved_prompt_not_current_checkout(self):
        control, candidate = self.pair()
        original = self.case["prompt"]
        self.case["prompt"] = "Unrelated current checkout prompt"
        self.write_suite()
        target = self.compare(control, candidate)
        pair = json.loads((target / "packet-order-1.json").read_text())["pairs"][0]
        self.assertEqual(pair["user_request"], original)

    def test_rejects_different_served_prompts(self):
        control = self.base / "control"
        self.assertEqual(self.invoke("--conditions", "baseline", output=control), 0)
        self.case["prompt"] = "A different request"
        self.write_suite()
        candidate = self.base / "candidate"
        self.assertEqual(self.invoke(output=candidate), 0)
        self.rejected(lambda: self.compare(control, candidate))

    def test_rejects_different_fixture_inputs(self):
        control = self.base / "control"
        self.assertEqual(self.invoke("--conditions", "baseline", output=control), 0)
        original = self.runner.prepare_fixture
        def changed_fixture(path, kind):
            original(path, kind)
            (path / "app.py").write_text("DIFFERENT FIXTURE")
        candidate = self.base / "candidate"
        with patch.object(self.runner, "prepare_fixture", side_effect=changed_fixture):
            self.assertEqual(self.invoke(output=candidate), 0)
        self.rejected(lambda: self.compare(control, candidate))

    def test_rejects_tampered_served_prompt(self):
        control, candidate = self.pair()
        (self.run_dir(candidate) / "prompt.txt").write_text("Different served prompt")
        self.rejected(lambda: self.compare(control, candidate))

    def test_rejects_foreign_run_provenance(self):
        control, candidate = self.pair()
        path = self.run_dir(candidate) / "result.json"
        result = json.loads(path.read_text())
        result["skill_sha256"] = "foreign"
        path.write_text(json.dumps(result))
        self.rejected(lambda: self.compare(control, candidate))

    def test_rejects_legacy_evidence_without_rewriting(self):
        control, candidate = self.pair()
        for directory in (control, candidate):
            (directory / "manifest.json").write_text('{"model":"fake-model","reasoning_effort":"medium","cli":"fake-codex 1"}')
        before = (candidate / "manifest.json").read_bytes()
        self.rejected(lambda: self.compare(control, candidate))
        self.assertEqual((candidate / "manifest.json").read_bytes(), before)

    def test_anonymizes_all_nested_tool_evidence(self):
        control, candidate = self.pair()
        raw = (self.run_dir(candidate) / "tool-calls.jsonl").read_bytes()
        target = self.compare(control, candidate)
        for number in (1, 2):
            packet = (target / f"packet-order-{number}.json").read_text()
            self.assertNotIn("--baseline", packet)
            self.assertNotIn("--treatment", packet)
            self.assertNotIn(str(self.base).replace("\\", "\\\\"), packet)
        self.assertEqual((self.run_dir(candidate) / "tool-calls.jsonl").read_bytes(), raw)

    def test_rejects_changed_runtime(self):
        control = self.base / "control"
        self.assertEqual(self.invoke("--conditions", "baseline", output=control), 0)
        self.cli_version = "fake-codex 2"
        candidate = self.base / "candidate"
        self.assertEqual(self.invoke(output=candidate), 0)
        self.rejected(lambda: self.compare(control, candidate))

    def test_rejects_resealed_prompt_that_was_not_the_declared_request(self):
        control, candidate = self.pair()
        target = self.run_dir(candidate)
        (target / "prompt.txt").write_text("Unrelated served request")
        path = target / "result.json"
        result = json.loads(path.read_text())
        if "artifacts" in result:
            result["artifacts"]["prompt.txt"] = hashlib.sha256((target / "prompt.txt").read_bytes()).hexdigest()
        path.write_text(json.dumps(result))
        self.rejected(lambda: self.compare(control, candidate))

    def test_existing_partial_packet_output_is_preserved(self):
        control, candidate = self.pair()
        output = self.base / "packets"
        output.mkdir()
        (output / "mapping-parent-only.json").write_text("KEEP")
        self.rejected(lambda: self.compare(control, candidate, output))
        self.assertEqual((output / "mapping-parent-only.json").read_text(), "KEEP")

    def test_recursive_anonymization_handles_encoded_strings_and_keys(self):
        control, candidate = self.pair()
        path = self.run_dir(candidate)
        result = json.loads((path / "result.json").read_text())
        work = result["workdir"]
        tool = {"tool": "read_file", "arguments": {"path": work.lower().replace("\\", "/") + "/app.py"},
                "result": {work + "/key": [json.dumps({"path": work + "/app.py"})]}}
        (path / "tool-calls.jsonl").write_text(json.dumps(tool) + "\n")
        if "artifacts" in result:
            result["artifacts"]["tool-calls.jsonl"] = hashlib.sha256((path / "tool-calls.jsonl").read_bytes()).hexdigest()
        (path / "result.json").write_text(json.dumps(result))
        output = self.compare(control, candidate)
        packet = (output / "packet-order-1.json").read_text()
        self.assertNotIn("--treatment", packet)
        self.assertIn("fixture/key", packet)


if __name__ == "__main__":
    unittest.main(verbosity=2)
