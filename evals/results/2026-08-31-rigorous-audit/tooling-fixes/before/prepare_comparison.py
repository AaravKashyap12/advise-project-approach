"""Prepare path-anonymized, order-reversed answer packets for independent reviewers."""

import argparse
import hashlib
import json
from pathlib import Path

EVALS = Path(__file__).resolve().parent


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def candidate(directory, case, repeat, condition):
    path = directory / "runs" / f"{case}--r{repeat}--{condition}"
    result = read_json(path / "result.json")
    if result["status"] != "completed":
        raise ValueError("Incomplete comparison run: " + str(path))
    answer = (path / "answer.txt").read_text(encoding="utf-8")
    if result.get("workdir"):
        answer = answer.replace(result["workdir"].replace("\\", "/"), "fixture").replace(result["workdir"], "fixture")
    if "--baseline" in answer or "--treatment" in answer:
        raise ValueError("Identifying source paths remain in candidate: " + str(path))
    log = path / "tool-calls.jsonl"
    return {"answer": answer, "tools": [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--control-condition", choices=("baseline", "treatment"), default="baseline")
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()
    control_manifest = read_json(args.control / "manifest.json")
    candidate_manifest = read_json(args.candidate / "manifest.json")
    for field in ("model", "reasoning_effort", "cli"):
        if control_manifest.get(field) != candidate_manifest.get(field):
            parser.error("Comparison runtime mismatch: " + field)
    cases = {case["id"]: case for case in read_json(EVALS / "fixtures/scenarios.json")["cases"]}
    if args.repeats < 1 or set(args.cases) - set(cases):
        parser.error("Use known cases and a positive repeat count")
    rubric = (EVALS / "comparison-rubric.md").read_text(encoding="utf-8")
    packets, mapping = [[], []], {}
    for name in args.cases:
        for repeat in range(1, args.repeats + 1):
            pair = f"P{len(mapping) + 1:02}"
            answers = {"control": candidate(args.control, name, repeat, args.control_condition), "candidate": candidate(args.candidate, name, repeat, "treatment")}
            order = ["control", "candidate"] if len(mapping) % 2 else ["candidate", "control"]
            mapping[pair] = {"case": name, "repeat": repeat, "order1": dict(zip(("A", "B"), order)), "order2": dict(zip(("A", "B"), reversed(order)))}
            for number, sequence in enumerate((order, list(reversed(order)))):
                packets[number].append({"id": pair, "user_request": cases[name]["prompt"], "environment": "External research unavailable; supplied fixture file contents are synthetic and identical. Tool evidence below records actual served calls.", "A": answers[sequence[0]], "B": answers[sequence[1]]})
    args.output.mkdir(parents=True, exist_ok=True)
    for number, pairs in enumerate(packets, 1):
        target = args.output / f"packet-order-{number}.json"
        if target.exists():
            parser.error("Use a new output directory; existing packets must not be replaced")
        target.write_text(json.dumps({"rubric": rubric, "pairs": pairs}, indent=2), encoding="utf-8")
    (args.output / "mapping-parent-only.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    (args.output / "provenance.json").write_text(json.dumps({"control": str(args.control), "candidate": str(args.candidate), "control_condition": args.control_condition, "rubric_sha256": hashlib.sha256(rubric.encode()).hexdigest(), "control_manifest": control_manifest, "candidate_manifest": candidate_manifest}, indent=2), encoding="utf-8")
    print(f"Prepared {len(mapping)} pairs in two blind orders")


if __name__ == "__main__":
    main()
