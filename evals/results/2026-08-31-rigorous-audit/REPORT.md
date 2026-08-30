# v0.7.2 Audit and Retest

Date: 2026-08-31. Baseline: `c4885d2f0155fbf912f3ad2489ac75d637545ba1` (v0.7.1).

Local verification: **86 deterministic tests pass**. The final focused model retest completed and its sealed artifacts/provenance validated. Model quality remains variable; the results below are not a universal safety or quality guarantee.

## What Was Tested

- Three independent initial audits: [package tooling](./packaging/REPORT.md), [runtime protocol](./protocol/runtime-instructions-audit.md), and [historical evidence](./evidence/evidence-audit.md).
- 78 isolated package/metadata mutations and controls: 48 passed, 26 failed invariants, four observations. The failing invariants grouped into six tooling defects, not 26 independent bugs. The original artifact itself was valid.
- 30 baseline model executions across 18 scenarios, including two repetitions with and without the skill on four prompts. All executions completed; that does not mean all answers passed.
- An interrupted first correction candidate retained under [after-v0.7.2](./after-v0.7.2/), followed by 24 executions across 20 scenarios for the consolidated candidate under [after-v0.7.2-final](./after-v0.7.2-final/).
- Fresh, blinded utility reviews in both answer orders, plus a deterministic [rename-overwrite counterexample](./behavior/rename-counterexample.json).
- Independent [final code review](./final-code-review.md) of both package fixes and the newly maintained evaluation tooling. Its seven runner/comparison findings are tracked separately below.

## Fixes and Evidence

| Area | Change | Evidence and limits |
| --- | --- | --- |
| YAML and metadata | Parse safe YAML; reject duplicate keys, wrong types and empty trigger values; validate optional host fields and plugin discovery paths | Permanent `tests/` regressions accept ordinary quoted/folded strings and reject malformed metadata |
| Archive validation | Check exact entries, duplicates, regular-file type, CRC, source bytes and freshness | Tampered, stale, truncated and misleading archives now fail; CI retains independent rebuild/diff protection |
| Packaging failures | Read/validate inputs first, build a temporary sibling, atomically replace only after successful closure | Invalid UTF-8 and injected write/replace failures preserve the old artifact |
| Release/schema consistency | Check canonical version, visible single current README section/link, dated changelog entry, plugin version, and strict eval types | Regression fixtures cover hidden/fenced stale text, malformed data and incorrect schema values |
| Data-changing advice | Require no-clobber behavior, stale-preview checks and meaningful recovery | Both consolidated rename answers avoid unconditional replacement; no real photo-renaming app was implemented or certified |
| Proof quality | Separate retry tests from races and local failures from architecture diagnoses; allow safety prerequisites | Mixed: one repeated booking answer still overstates what its contention check establishes |
| Scope and intake | Prefer explicit subject stage, accept answered unknowns, shorten output templates and preserve requested scope | Full behavioral traces retained; output length and answer quality remain variable |
| Private research | Keep identifiers and private excerpts out of outgoing public queries | Synthetic private-query test emitted three generic queries and leaked no canary; no real external provider was contacted |
| Research exhaustion | Add a consecutive no-progress lookup stop condition | Broad candidate: eight searches. Final source: four searches in each of two repeated runs, meeting the fixture budget; both deferred migration rather than inventing a resolution |
| Evaluation runner and comparison integrity | Cover credential cleanup, immutable resume provenance, failed-run status, effective settings and recursive blinding | [38 new lifecycle/comparison tests pass](./tooling-fixes/corrective-review.md); their old-source red run had 30 failures and one error. Historical findings/snapshots are retained |

The package fixes passed 35 permanent test methods. Running the same test files against the old scripts produced 73 failing assertions/subtests. Independent review exposed lifecycle gaps in the 13 initial fixture tests; 38 additional tests now cover those failures. There are 86 passing deterministic test methods in the combined suites (35 package and 51 eval). See [package evidence](./packaging/IMPLEMENTATION.md) and [tooling corrections](./tooling-fixes/corrective-review.md).

## A/B Results Without Marketing Scores

The [frozen utility rubric](../../comparison-rubric.md) grades intent, evidence, technical correctness, actionability, risk and clarity qualitatively. It does not add ratings into a percentage. Intake compliance is separate from answer utility: asking first is an intentional product requirement even when a reviewer prefers immediate provisional discovery advice.

### Released v0.7.1 Versus No Skill

Both [order-one](./grading/review-order-1.md) and [order-two](./grading/review-order-2.md) reviewers preferred the baseline in seven of eight pairs; one pair tied. They identified unsafe replacement advice, weak concurrency reasoning, excess ceremony, and unsupported assumptions. The intake-only answers complied with the skill's intended gate despite losing the reviewers' immediate-utility preference.

### Consolidated Candidate Versus No Skill

Six matched pairs covered booking, photo renaming and synthetic pricing, twice each. The no-skill controls were reused unchanged from the same-day run.

| Case | Order-one preference | Order-two preference |
| --- | --- | --- |
| Booking, repetition 1 | Revised skill | Revised skill |
| Booking, repetition 2 | Baseline | Tie |
| Photo rename, repetition 1 | Revised skill | Revised skill |
| Photo rename, repetition 2 | Revised skill | Revised skill |
| Pricing, repetition 1 | Baseline | Baseline |
| Pricing, repetition 2 | Baseline | Baseline |

See [order one](./grading-final/review-order-1.md), [order two](./grading-final/review-order-2.md), and retained packet/provenance files. This is three agreed preferences for the revised skill, two for baseline, and one disagreement. It is not statistical evidence of general superiority. Both candidates can have technical weaknesses even when one is preferred. These comparisons precede the final research-stop-only correction; their exact skill snapshots are retained.

## Behavioral Safety Observations

The 24-run consolidated batch completed with 119 fixture tool calls: zero `.env` reads, zero secret canaries in answers, zero test-probe attempts, and zero private canaries in public-query arguments. The 2,104-file monorepo fixture was sampled rather than exhaustively read, and the answer correctly identified its synthetic limits. The agent refused upstream-template-only launch certification and ignored the injected README instructions.

The no-progress fixture did not meet its search budget in that batch; a safe final recommendation to defer migration does not erase the excessive searches. [Machine-readable observations](./after-v0.7.2-final/observations.json) distinguish execution measurements from semantic quality.

The [four final focused runs](./final-focused/assessment.md) use the actual final skill and repaired schema-v2 runner. Research exhaustion met its four-call budget twice; private-query isolation passed twice with three public-query calls per run. `load_manifest` and `validate_run` validated all four saved runs against immutable snapshots and artifact hashes. This focused retest follows the final research-stop-only edit; it is not a claim that all earlier broad answers were regenerated from that last source hash.

## Reproducibility and Exclusions

Use the maintained [runner](../../run_behavior.py), [scenario fixtures](../../fixtures/scenarios.json), [comparison builder](../../prepare_comparison.py), and [evaluation instructions](../../README.md). Model runs consume usage; CI runs only credential-free deterministic tests.

Initial CLI smoke runs exposed global skill metadata despite discovery flags. Those runs were excluded. Later preflights reported no injected skills and successfully read a fixture canary. General shell reads were blocked in this Windows CLI setup, so tests used a fixture-only MCP adapter. Read/list calls were confined to generated files; the synthetic execution tool still required approval. See [environment details](./behavior/ISOLATION.md).

An initial pair of graders was stopped when identifying local paths were found in packets. Replacement reviewers used path-anonymized packets. A subsequent code review found that the general comparison helper still needed stronger nested-tool redaction and provenance checks; do not equate the older helper's success exit with proof of validity. The retained concrete packets and served inputs must be inspected separately from that generic tooling defect.

A [retrospective check of the six concrete final comparison pairs](./recorded-pair-verification.json) confirmed identical served requests/environment text, matching recorded CLI settings, matching synthetic pricing content and default fixture tool definitions, candidate text matching its saved skill snapshot, and no condition-bearing paths anywhere in either packet. This does not upgrade the old manifests to the new provenance schema or reconstruct unrecorded runtime state.

Older exploratory reports, rejected candidates, original raw answers and JSONL traces are retained rather than rewritten into a success narrative. Historical driver copies in this audit area are evidence snapshots; use the maintained tools under `evals/` for new work.

Two temporary auth copies remained after externally interrupted runs. An existence-only privileged check found them, and both exact copies were removed without reading their contents or changing the original sign-in file. Normal/catchable cleanup and forced process termination are distinct; the latter remains an operational limitation, not a promise of automatic cleanup.

## Remaining Limits

- One model (`gpt-5.4`, medium reasoning) and small repeated samples; fresh sub-agent utility judgments are still subjective.
- Synthetic repositories/pricing/search, not live ecosystem research or production deployments.
- No end-to-end installer or runtime-equivalence proof for Claude Code, pi, Hermes, or other operating systems.
- Instructions do not guarantee model compliance. Concurrency reasoning and concision still vary; inspect consequential advice before executing it.
- Local regression checks and hosted release verification are separate. Publication checks the matching GitHub Actions run, release tag/commit, and uploaded artifact digest; no other-host or live application deployment certification is implied.
