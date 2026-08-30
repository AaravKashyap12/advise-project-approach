"""Build blinded, order-reversed packets without exposing treatment labels."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
suite = json.loads((HERE / "suite.json").read_text(encoding="utf-8"))
rubric = """Judge answer utility against the original user request, not against an imagined skill or a preferred format.
For each dimension give pass, partial, fail, or not-applicable with a brief quote or specific evidence:
- Intent and scope: answers the request, respects constraints and explicit limits.
- Evidence calibration: inspected facts versus assumptions, no fake research or test success.
- Technical correctness: proposed behavior, calculations, and causal claims are sound.
- Actionability or intake: the response moves the user forward appropriately; a necessary question can be the right next step.
- Risk and validation: material risks are acknowledged, checks actually test the claim, and failure is not overdiagnosed.
- Clarity and proportionality: useful signal without unnecessary work or verbosity.
Do not reward length, section counts, or test terminology by themselves. Do not demand a build plan or tests from an appropriate intake-only answer. Do not penalize a useful testing/foundation step merely because it is not a product feature. A single racing request is not automatically a deterministic concurrency test. A failing local check alone does not prove the architecture is wrong.
Use only the supplied answers, request, environment and tool evidence. Pick A, B or Tie for overall user utility and give confidence plus material flaws. Scores are qualitative; do not manufacture a success percentage.
"""
packets = [[], []]
key = {}
index = 0
for case in suite["cases"]:
    if not case.get("paired"):
        continue
    for repeat in (1, 2):
        index += 1
        pair_id = f"P{index:02}"
        candidates = {}
        for condition in ("baseline", "treatment"):
            path = HERE / "runs" / f"{case['id']}--r{repeat}--{condition}"
            result = json.loads((path / "result.json").read_text(encoding="utf-8"))
            if result["status"] != "completed":
                raise SystemExit("Cannot grade incomplete pair " + pair_id)
            tool_file = path / "tool-calls.jsonl"
            answer = (path / "answer.txt").read_text(encoding="utf-8")
            if result.get("workdir"):
                answer = answer.replace(result["workdir"].replace("\\", "/"), "fixture").replace(result["workdir"], "fixture")
            if "--baseline" in answer or "--treatment" in answer:
                raise SystemExit("Candidate identity leaked in answer link: " + pair_id)
            candidates[condition] = {"answer": answer, "tools": [json.loads(line) for line in tool_file.read_text(encoding="utf-8").splitlines()] if tool_file.exists() else []}
        first_order = ["treatment", "baseline"] if index % 2 else ["baseline", "treatment"]
        key[pair_id] = {"case": case["id"], "repeat": repeat, "order1": dict(zip(("A", "B"), first_order)), "order2": dict(zip(("A", "B"), reversed(first_order)))}
        for order in (0, 1):
            conditions = first_order if order == 0 else list(reversed(first_order))
            packets[order].append({"id": pair_id, "user_request": case["prompt"], "environment": "External research unavailable; local files are synthetic fixtures. Both candidates had identical fixture tools and access.", "A": candidates[conditions[0]], "B": candidates[conditions[1]]})
target = HERE.parent / "grading"
target.mkdir(exist_ok=True)
for order, packet in enumerate(packets, 1):
    (target / f"packet-order-{order}.json").write_text(json.dumps({"rubric": rubric, "pairs": packet}, indent=2), encoding="utf-8")
(target / "mapping-parent-only.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
(target / "rubric.txt").write_text(rubric, encoding="utf-8")
print(f"Prepared {index} pairs in two blinded orders")
