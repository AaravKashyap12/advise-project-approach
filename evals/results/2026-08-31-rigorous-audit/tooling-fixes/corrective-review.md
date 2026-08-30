# Evaluation Tooling Corrections

Date: 2026-08-31. Scope: the seven findings in the independent final code review. The implementation changes only `evals/run_behavior.py`, `evals/prepare_comparison.py`, and the new `evals/test_runner.py`. This directory contains new corrective evidence; historical evidence was not edited.

## Outcome

All seven reproduced findings are addressed and covered by deterministic tests. The original 28-test regression set was run against byte-exact reviewed script snapshots before production edits: **23 failures, 1 error, 4 passes**. The same 28 tests then passed against the corrections. An expanded 38-test set, including interruption and additional provenance boundaries, produced **30 failures, 1 error, 7 passes** against those same original snapshots and **38 passes** against the corrected code.

Broader verification passed: **35 package/metadata tests** and **51 eval tests** (the existing 13 fixture tests plus the new 38 tooling tests). No model/API calls, real credentials, nested agents, Git mutations, publication actions, dependency installation, or root package rebuild were performed.

## Corrections

| Finding | Implementation | Evidence |
| --- | --- | --- |
| Setup failures leave copied authentication | Credential copying and all setup execute inside cleanup protection. Discovery/version/config preparation precede the copy where possible. Partial-copy failures are covered. | Fake partial-copy, configuration, version-command, post-copy setup, probe-failure, and KeyboardInterrupt tests. |
| Unmanifested or foreign evidence can be resumed | New runs require empty directories; resume requires a valid schema-v2 manifest and matching saved snapshots. Every existing run must have matching identity, case/condition/repeat metadata, command settings, and complete hashed artifacts. A lock prevents cooperating writers sharing an output directory. | Unmanifested output, nonempty new output, foreign result, tampered/missing answer, partial directory, and additive-resume tests. |
| Resume relabels old runs with a new runtime | The manifest is written once and never rewritten on resume. Identity includes raw/served skill hashes, suite, runner, fixture adapter, CLI version/executable, Python version/executable/platform, command prefix, timeout, and discovered disabled-skill paths. | Changed CLI, runner, timeout, source, fixture adapter, and executed-command tests; manifest and prior-run byte preservation. |
| Failed resumed cases incorrectly return success | Only validated completed runs are reused. A failed or incomplete existing run stops with nonzero status; the tool does not overwrite or silently retry failed evidence. | Timeout followed by resume stays nonzero and preserves the failed result. |
| Comparison accepts different tested tasks or tools | Comparison reads validated saved suite/source/adapter/runner snapshots, checks runtime identity, reconstructs and verifies the served prompt, checks recorded command settings and artifact hashes, and requires identical initial fixture contents. Only the intended skill treatment hashes may differ. | Changed served prompt, fixture contents, runtime, result provenance, resealed incorrect prompt, and changed-current-checkout tests. |
| Blind packets expose condition-bearing tool paths | Path normalization recursively processes answers, nested lists/maps, map keys, and JSON-encoded strings. It handles Windows path case/separator variants and rejects key collisions or residual condition labels. Raw input evidence remains unchanged. | Nested tool-path and encoded-string/key tests; raw-log byte preservation and reversed-order checks. |
| Declared reasoning differs from actual command | Probe and case commands share one command builder driven by the suite's reasoning setting, which is also part of the immutable identity. | A nondefault `high` setting is asserted in both captured fake commands. |

The optional `rg` optimization now has a standard-library discovery fallback when unavailable, failing, or timing out. Both missing-`rg` and failing-`rg` paths retain explicit skill disables. The copied fixture adapter, not the live checkout adapter, is used for new executions.

## Code Locations

- [run_behavior.py](../../../run_behavior.py#L110): schema-v2 evidence contract and validation helpers.
- [run_behavior.py](../../../run_behavior.py#L192): optional `rg` discovery and fallback.
- [run_behavior.py](../../../run_behavior.py#L351): output checks, immutable identity, protected lifecycle, and resume.
- [prepare_comparison.py](../../../prepare_comparison.py#L14): recursive anonymization and snapshot-backed comparison.
- [test_runner.py](../../../test_runner.py#L157): fake-executor runner regressions.
- [test_runner.py](../../../test_runner.py#L345): comparison regressions.

## Red/Green Evidence

| Run | Result | Record |
| --- | --- | --- |
| Original tests, exact reviewed scripts, before edits | 28 tests: 23 failures, 1 error, 4 passes; exit 1 | [red-reviewed-snapshots.txt](red-reviewed-snapshots.txt) |
| Runner-only implementation increment | 28 tests: 8 comparison failures, 20 passes; exit 1 | [runner-increment.txt](runner-increment.txt) |
| Both implementations, original tests | 28 passes; exit 0 | [green-initial.txt](green-initial.txt) |
| Expanded tests, exact original scripts | 38 tests: 30 failures, 1 error, 7 passes; exit 1 | [red-expanded.txt](red-expanded.txt) |
| Expanded tests, corrected scripts | 38 passes; exit 0 | [green-expanded.txt](green-expanded.txt) |
| Package/metadata suite | 35 passes in 18.872 seconds; exit 0 | [package-regressions.txt](package-regressions.txt) |
| Entire deterministic eval suite | 51 passes in 10.774 seconds; exit 0 | [eval-regressions.txt](eval-regressions.txt) |

The one baseline error is the deliberately missing `rg` executable escaping the old runner, not a broken test setup. Additional tests were run red against the same frozen original scripts even though they were added after the first implementation increment. The initial `red.txt` is also retained: it exposed a defect in the first draft of the test helper, which treated a returned Path as nonzero failure. The helper was corrected before production edits and the authoritative pre-edit run is `red-reviewed-snapshots.txt`. No failing evidence was discarded.

Commands used:

```powershell
$env:EVAL_TOOLING_SOURCE = (Resolve-Path 'evals/results/2026-08-31-rigorous-audit/tooling-fixes/before').Path
python -B -m unittest discover -s evals -p 'test_runner.py' -v
# Green runs used a fresh shell with EVAL_TOOLING_SOURCE unset.
python -B -m unittest discover -s evals -p 'test_runner.py' -v
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s evals -p 'test_*.py' -v
```

The full eval suite was run outside the Windows sandbox because the existing `test_fixtures.py` uses owner-only temporary directories that previously failed inside that sandbox. The new tests use inherited-ACL disposable directories and passed within the sandbox. `test_fixtures.py` was not changed. Python was 3.12.13 and PyYAML 6.0.3. Both script `--help` entry points and `git diff --check` passed.

## Authentication Limits

Normal Python exceptions and `KeyboardInterrupt` execute the cleanup `finally`; the fake interrupted-executor test verifies removal of the copied fake credential and lock while leaving the fake main auth intact. Setup failures and forced termination are different cases.

**No protection against forced process kill is claimed.** Host termination, an uncatchable kill, power loss, or interpreter failure can bypass `finally`, leave copied auth in the owner-only temporary home, and leave a stale output lock. Owner-only temporary-directory permissions mitigate exposure but do not remove the copy. Filesystem permission failures during cleanup likewise surface as errors, not successful cleanup. No watchdog or signal-survival mechanism was added.

The parent reported existence-only confirmation of surviving auth copies in `apa-rigorous-m_owrwij` and `apa-rigorous-oc3cfwgi` after tool Ctrl+C stops and is handling those exact copies without reading contents or altering main auth. This implementation task did not inspect or delete either real copy and does not independently establish whether those stops delivered catchable Python interrupts or forcibly terminated the interpreter. The corrected setup cleanup must not be presented as fixing uncatchable termination.

## Legacy and Remaining Limits

- Existing runs and comparison artifacts were produced with the older helpers. They lack the complete schema-v2 saved input and runtime contract and are intentionally rejected for automatic resume/comparison. Nothing was silently relabeled or migrated. The parent will manually verify actual served prompts, recorded command settings, and selected fixture responses before relying on those comparisons.
- New comparisons conservatively require identical whole-suite, runner, adapter, and runtime identity except for the intended skill treatment. Even an unrelated suite edit or interpreter/path change requires new evidence or an explicitly separate manual assessment.
- Failed/partial cases are retained and require classification or a new output directory. There is no automatic retry that overwrites them. A stale lock from a terminated process also requires explicit operator handling; this tool never guesses that another writer is dead.
- Artifact hashes detect mismatches and accidental mixing, not malicious rewriting by someone who can replace the artifacts and recompute all hashes. They are not signed attestations.
- The new real-Codex execution path and schema-v2 model-produced evidence have not been exercised against a model/API in this task. All executors and credentials in the tests were fake. Existing adapter tests exercise the real local synthetic MCP server without a network provider.
- Source/package metadata, SKILL runtime, VERSION, documentation outside this corrective directory, the fixture server, and historical evidence were left to the parent. Publication and hosted CI were not attempted. No independent nested review agent was used; this is implementation self-review plus retained deterministic evidence.

## Snapshot Digests

| Snapshot | SHA-256 |
| --- | --- |
| Reviewed runner (`before/run_behavior.py`) | `3442cd132052f712b6976dbe376ffdc8e46b60b78011e89b67ce3ab59ecb312c` |
| Reviewed comparison (`before/prepare_comparison.py`) | `fbdd40b417cbcebd693f06c772e2c2a74950568e0d5a09865e3ca3aed629513d` |
| Corrected runner (`after/run_behavior.py`) | `af44458fa9b7a55582acbdaf497f691ae84d8a62efb65906d03e9095d2785f2f` |
| Corrected comparison (`after/prepare_comparison.py`) | `41c985ee44876d8d73043aa27202620931e173a2ca71ab2775a875e9a4c13470` |
| Expanded regression tests (`after/test_runner.py`) | `81dad2a83985cc704a0f580a4a7d9e158d080f0ee0ef99884b0659bbaa1b64e8` |

`before/test_runner.py` retains the original 28-test regression set used before production edits. `after/test_runner.py` retains the expanded 38-test set. Both script snapshots in `before/` still match the exact hashes from the independent final review.
