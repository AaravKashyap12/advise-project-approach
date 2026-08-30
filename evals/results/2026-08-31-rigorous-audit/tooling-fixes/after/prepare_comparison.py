"""Prepare blind packets only from validated, snapshot-backed evaluation evidence."""

import argparse
import hashlib
import json
from pathlib import Path
import re

from run_behavior import context_for, load_manifest, read_json, suite_cases, validate_run

EVALS = Path(__file__).resolve().parent


def anonymize(value, replacements):
    """Remove identifying paths recursively, including keys and JSON-encoded strings."""
    if isinstance(value, str):
        for source, target in replacements:
            variants = {source, source.replace("\\", "/"), source.replace("\\", "\\\\")}
            for variant in sorted(variants, key=len, reverse=True):
                flags = re.IGNORECASE if re.match(r"^[a-zA-Z]:", variant) else 0
                value = re.sub(re.escape(variant), lambda match: target, value, flags=flags)
        return value
    if isinstance(value, list):
        return [anonymize(item, replacements) for item in value]
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            key = anonymize(key, replacements)
            if key in cleaned:
                raise ValueError("Anonymization would merge tool-evidence keys")
            cleaned[key] = anonymize(item, replacements)
        return cleaned
    return value


def candidate(directory, manifest, case, repeat, condition):
    result = validate_run(directory, manifest, case, repeat, condition)
    path = directory / "runs" / result["id"]
    log = path / "tool-calls.jsonl"
    evidence = {"answer": (path / "answer.txt").read_text(encoding="utf-8"),
                "tools": [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]}
    replacements = [(result["workdir"], "fixture"), (str(path), "run-evidence"),
                    (str(directory), "evidence"), (result["id"], "run")]
    evidence = anonymize(evidence, sorted(replacements, key=lambda item: len(item[0]), reverse=True))
    return evidence, read_json(path / "fixture-snapshot.json")


def prepare(args):
    control = args.control.resolve()
    treatment = args.candidate.resolve()
    control_manifest = load_manifest(control)
    candidate_manifest = load_manifest(treatment)
    # Only the skill treatment may differ. Runtime, suite and fixture code must match.
    excluded = {"skill_sha256", "skill_prompt_sha256"}
    control_identity = {k: v for k, v in control_manifest["identity"].items() if k not in excluded}
    candidate_identity = {k: v for k, v in candidate_manifest["identity"].items() if k not in excluded}
    if control_identity != candidate_identity:
        raise ValueError("Comparison runtime/suite/fixture identity mismatch")
    cases = suite_cases(read_json(control / "suite-snapshot.json"))
    candidate_cases = suite_cases(read_json(treatment / "suite-snapshot.json"))
    if args.repeats < 1 or len(args.cases) != len(set(args.cases)) or set(args.cases) - set(cases):
        raise ValueError("Use unique known cases and a positive repeat count")
    rubric = (EVALS / "comparison-rubric.md").read_text(encoding="utf-8")
    packets, mapping = [[], []], {}
    for name in args.cases:
        for repeat in range(1, args.repeats + 1):
            pair = f"P{len(mapping) + 1:02}"
            left, left_fixture = candidate(control, control_manifest, cases[name], repeat, args.control_condition)
            right, right_fixture = candidate(treatment, candidate_manifest, candidate_cases[name], repeat, "treatment")
            if cases[name] != candidate_cases[name] or left_fixture != right_fixture:
                raise ValueError(f"Comparison served prompt/fixture inputs differ: {name}")
            answers = {"control": left, "candidate": right}
            order = ["control", "candidate"] if len(mapping) % 2 else ["candidate", "control"]
            mapping[pair] = {"case": name, "repeat": repeat, "order1": dict(zip(("A", "B"), order)),
                             "order2": dict(zip(("A", "B"), reversed(order)))}
            for number, sequence in enumerate((order, list(reversed(order)))):
                packets[number].append({"id": pair, "user_request": cases[name]["prompt"],
                                        "environment": context_for(cases[name]).strip(),
                                        "A": answers[sequence[0]], "B": answers[sequence[1]]})
    files = {}
    for number, pairs in enumerate(packets, 1):
        payload = json.dumps({"rubric": rubric, "pairs": pairs}, indent=2)
        if re.search(r"--(?:baseline|treatment)", payload, flags=re.IGNORECASE):
            raise ValueError("Identifying condition paths remain in blind packet")
        files[f"packet-order-{number}.json"] = payload
    files["mapping-parent-only.json"] = json.dumps(mapping, indent=2)
    files["provenance.json"] = json.dumps({
        "schema_version": 2, "control": str(control), "candidate": str(treatment),
        "control_condition": args.control_condition, "rubric_sha256": hashlib.sha256(rubric.encode()).hexdigest(),
        "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "control_manifest": control_manifest, "candidate_manifest": candidate_manifest,
    }, indent=2)
    # A partial previous attempt must not be silently completed or relabeled.
    args.output.mkdir(parents=True, exist_ok=False)
    for name, payload in files.items():
        with (args.output / name).open("x", encoding="utf-8") as handle:
            handle.write(payload)
    print(f"Prepared {len(mapping)} pairs in two blind orders")


def main():
    parser = argparse.ArgumentParser(description="Compare schema-v2 evidence. Legacy runs require manual provenance verification; no automatic migration is performed.")
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--control-condition", choices=("baseline", "treatment"), default="baseline")
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()
    try:
        prepare(args)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
