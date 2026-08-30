"""Retrospectively check concrete saved pairs; not a substitute for new runner provenance."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
control = HERE / "behavior"
candidate = HERE / "after-v0.7.2-final"
checks = []


def data(path):
    return json.loads(path.read_text(encoding="utf-8"))


def request_text(path):
    text = path.read_text(encoding="utf-8")
    assert "\nUser request:\n" in text
    return text.rsplit("\nUser request:\n", 1)[1].strip(), text.splitlines()[0]


def cli_settings(command):
    configs = [command[i + 1] for i, value in enumerate(command[:-1]) if value == "-c"]
    disabled = [command[i + 1] for i, value in enumerate(command[:-1]) if value == "--disable"]
    return {"model": command[command.index("--model") + 1], "sandbox": command[command.index("--sandbox") + 1], "config": configs, "disabled": disabled}


for key in ("model", "reasoning_effort", "cli"):
    assert data(control / "manifest.json")[key] == data(candidate / "manifest.json")[key]

for case in ("booking-known-case", "cli-holdout", "pricing-fixture"):
    for repeat in (1, 2):
        dirs = [control / "runs" / f"{case}--r{repeat}--baseline", candidate / "runs" / f"{case}--r{repeat}--treatment"]
        results = [data(path / "result.json") for path in dirs]
        assert all(result["status"] == "completed" and result["exit_code"] == 0 for result in results)
        assert all(result["case"] == case and result["repeat"] == repeat for result in results)
        assert request_text(dirs[0] / "prompt.txt") == request_text(dirs[1] / "prompt.txt")
        settings = [cli_settings(result["command"]) for result in results]
        assert settings[0] == settings[1]
        assert settings[0]["model"] == "gpt-5.4"
        assert 'model_reasoning_effort="medium"' in settings[0]["config"]
        assert "Use these active skill instructions:" not in (dirs[0] / "prompt.txt").read_text(encoding="utf-8")
        text = (dirs[1] / "prompt.txt").read_text(encoding="utf-8")
        snapshot = (candidate / "skill-snapshot.md").read_text(encoding="utf-8")
        assert ("Use these active skill instructions:\n\n" + snapshot) in text
        if case == "pricing-fixture":
            payloads = []
            for path in dirs:
                calls = [json.loads(line) for line in (path / "tool-calls.jsonl").read_text(encoding="utf-8").splitlines()]
                reads = [call["result"] for call in calls if call["tool"] == "read_file" and call["arguments"].get("path") == "pricing.md"]
                assert reads
                payloads.append(reads[0])
            assert payloads[0] == payloads[1]
        checks.append({"case": case, "repeat": repeat, "matched_served_request_and_environment": True, "matched_recorded_command_settings": True, "candidate_matches_saved_skill_text": True, "pricing_payloads_match": case == "pricing-fixture"})

for order in (1, 2):
    packet = (HERE / "grading-final" / f"packet-order-{order}.json").read_text(encoding="utf-8")
    assert "--baseline" not in packet and "--treatment" not in packet

with tempfile.TemporaryDirectory(prefix="apa-tool-schema-check-") as scratch:
    responses = []
    for server in (control / "fixture_server.py", ROOT / "evals/fixtures/fixture_server.py"):
        packet = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\n"
        run = subprocess.run([sys.executable, str(server), "--root", scratch, "--log", str(Path(scratch) / "log.jsonl")], input=packet, text=True, capture_output=True, check=True, timeout=10)
        responses.append(data_from_output := json.loads(run.stdout)["result"]["tools"])
    assert responses[0] == responses[1]

result = {"pairs": checks, "matching_default_fixture_tool_definitions": True, "condition_paths_absent_from_complete_packets": True, "limitations": ["This validates concrete saved records, not every historical execution property.", "Historical manifests lack the new runner's full provenance schema and cannot be silently upgraded.", "No model was called; declared CLI identities were compared, not reconstructed from a network capture."]}
(HERE / "recorded-pair-verification.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"Verified {len(checks)} saved pairs, identical default tool definitions, and complete packet path blinding")
