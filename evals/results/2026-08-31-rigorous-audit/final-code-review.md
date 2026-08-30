# Independent Final Code Review: v0.7.2

Historical pre-correction review. All seven findings below have been addressed with [red/green lifecycle and comparison regressions](./tooling-fixes/corrective-review.md). Reviewed runner/comparison source links point to the retained pre-fix snapshots.

Date: 2026-08-31. Baseline: `c4885d2f0155fbf912f3ad2489ac75d637545ba1` (`HEAD`). Target: the current uncommitted source and newly maintained evaluation tooling. This review did not rely on other workers' pass claims.

## Findings

### 1. [P2] Credential cleanup does not cover setup failures

Location: [evals/run_behavior.py:149](tooling-fixes/before/run_behavior.py#L149), with the protected block starting at line 185 and cleanup at line 248. Confidence: confirmed.

The real `auth.json` is copied before skill discovery, configuration writes, CLI-version discovery, and evidence-directory writes. Any exception in those operations exits before the cleanup `finally`. A missing `rg` is a concrete trigger: discovery invokes it without checking availability, and it is not a declared developer dependency. A fake-auth reproduction injected `FileNotFoundError` at discovery and confirmed that the copied credential remained in `codex-home/auth.json`, with zero model calls. Owner-only temporary-directory permissions reduce exposure, but do not satisfy the documented removal-on-exit guarantee.

Start cleanup protection before attempting the credential copy, covering partial copies and every subsequent setup operation. Preflight ordinary dependencies before copying credentials. Add regressions for discovery/configuration/version-command failures and assert that no copied auth survives. The synthetic credential used by this review was removed.

### 2. [P2] Resume accepts evidence without a matching manifest

Location: [evals/run_behavior.py:135](tooling-fixes/before/run_behavior.py#L135) and [evals/run_behavior.py:211](tooling-fixes/before/run_behavior.py#L211). Confidence: confirmed.

The candidate/configuration guard runs only when `manifest.json` exists. With `--resume`, a directory containing an old `runs/<id>/result.json` but no manifest is admitted; the runner writes a fresh current-candidate manifest and blindly imports that old result. Reproduction: precreate a completed result with `skill_sha256: ANOTHER-CANDIDATE`, omit the manifest, and resume. The runner returns 0 and produces a summary whose run hash disagrees with its new manifest. Without `--resume`, a nonempty unmanifested directory can also have existing evidence overwritten or logs combined.

Require a valid matching manifest for resume and require a new/empty output directory for a new run. Validate each reused result's identity and candidate/configuration provenance before skipping it. Test missing manifests, foreign per-run hashes, and preexisting partial output, not just the existing test's mismatched manifest hash.

### 3. [P2] Resume can relabel old runs with a different runtime

Location: [evals/run_behavior.py:128](tooling-fixes/before/run_behavior.py#L128), [evals/run_behavior.py:172](tooling-fixes/before/run_behavior.py#L172), and [evals/run_behavior.py:183](tooling-fixes/before/run_behavior.py#L183). Confidence: confirmed.

Resume compares source/suite/server hashes and model settings, but not the actual CLI version, runner implementation, or timeout. It then overwrites the manifest with the new runtime description while retaining completed old runs. Reproduction: finish a fake run under `codex-mocked-old`, resume under `codex-mocked-new`, and observe that only the isolation probe executes while the retained old answer is now described by a manifest naming the new CLI. Changes to `prepare_fixture`, prompt construction, or execution flags inside this runner are likewise outside its fingerprint.

Construct and validate the effective runtime identity before accepting existing evidence. Include the CLI version, runner/fixture-generation identity, and relevant execution settings, and preserve the original manifest for resumed runs. Reject a changed identity or retain explicit per-attempt provenance instead of silently relabeling evidence.

### 4. [P2] A failed resumed case is skipped and the command reports success

Location: [evals/run_behavior.py:211](tooling-fixes/before/run_behavior.py#L211), bypassing the failure handling at lines 244-246. Confidence: confirmed.

Every existing `result.json` is treated as reusable, including `timeout` and `execution_error`. Reproduction: make the only selected case time out; the first invocation correctly returns 2. Resume it with a healthy fake executor: only the isolation probe runs, the timeout result is retained, and the command returns 0. Automation or a maintainer checking the command status can therefore interpret an unresolved failed evaluation as a successful run.

Skip only completed, validated results. For failed attempts, either stop with a nonzero result until explicitly classified, or create a separate retry attempt while preserving the original evidence. Add a two-invocation timeout/resume regression that checks both exit status and whether the case actually executes.

### 5. [P2] Comparison packets do not require the same tested inputs

Location: [evals/prepare_comparison.py:40](tooling-fixes/before/prepare_comparison.py#L40) and [evals/prepare_comparison.py:43](tooling-fixes/before/prepare_comparison.py#L43). Confidence: confirmed.

The comparison gate checks only model, reasoning label, and CLI label. It ignores the recorded suite and fixture-server hashes, does not validate each result against its manifest, and labels answers using the current checkout's scenario prompt rather than the prompt actually served. Reproduction: give control and candidate identical runtime labels but different suite/server hashes and unrelated per-run hashes. Both packets are generated successfully. This permits two different tasks or tool environments to be presented as a controlled comparison, including after the suite changes between measurement and grading.

Verify that the selected runs used identical user requests, fixture inputs, and tool/runtime configuration, allowing only the intended skill treatment to differ. Check manifest/run provenance, and use a saved scenario snapshot or verify its hash before using the checkout's prompts. Add tests rejecting mismatched suite/tool hashes and a changed current scenario prompt. This counterexample establishes a tooling defect, not that any particular historical comparison was contaminated.

### 6. [P2] Raw tool evidence leaks baseline/treatment labels into blind packets

Location: [evals/prepare_comparison.py:22](tooling-fixes/before/prepare_comparison.py#L22) and [evals/prepare_comparison.py:26](tooling-fixes/before/prepare_comparison.py#L26). Confidence: confirmed.

Only answer text is anonymized and checked. Tool-call arguments and returned values are copied verbatim. `read_file` accepts absolute paths within the fixture root and echoes the requested path, so valid calls can contain `...--baseline/app.py` or `...--treatment/app.py`. A reproduction with neutral answers and absolute tool paths produced both ostensibly blind packets with those condition labels intact. Reversing A/B order does not repair this disclosure.

Normalize identifying fixture paths in all nested tool-evidence strings as well as answers, and scan the complete serialized packet for condition-bearing paths before writing it. Keep the raw logs in parent-only evidence. Add a packet test containing absolute paths in both tool arguments and results.

### 7. [P2] Recorded reasoning settings can differ from the executed settings

Location: [evals/run_behavior.py:190](tooling-fixes/before/run_behavior.py#L190) and [evals/run_behavior.py:220](tooling-fixes/before/run_behavior.py#L220), versus the suite-derived manifest at line 133. Confidence: confirmed.

Both CLI commands hard-code `model_reasoning_effort="medium"`, while the manifest and comparison gate use `suite["reasoning_effort"]`. Changing that maintained configuration to `high` produces evidence labeled high while still executing medium. This was reproduced with an isolated scenario copy and captured fake CLI arguments; the current default of medium masks the defect.

Build execution arguments and fingerprints from the same validated effective setting. A deterministic command-capture test should set a nondefault reasoning effort and assert that both the probe and case commands agree with the manifest.

## Verification Evidence

- Environment: Windows, Python 3.12.13, installed PyYAML 6.0.3. No dependencies installed by this review.
- `python -B -m unittest discover -s tests -v`: 35 tests passed in 19.375 seconds.
- `python -B -m unittest discover -s evals -p "test_*.py" -v`: the sandboxed run failed all 13 tests during `setUp`, before adapter behavior, because `TemporaryDirectory` children were inaccessible. The same unmodified suite run outside the sandbox passed all 13 in 1.853 seconds. This is recorded as an environment limitation, not an adapter logic failure. `tests/support.py` already uses an inherited-ACL temporary-directory pattern; the eval tests do not.
- In an isolated copy with the current tests and the two scripts restored to `HEAD`, 35 test methods produced 73 failing assertions/subtests and zero test-runner errors. Detected regressions included malformed/typed YAML, duplicate metadata, CRC/payload integrity, stale archives, write/replace failure handling, plugin paths, and release consistency. These tests detect real differences from the old implementation, rather than merely asserting that the new code runs.
- Copied the current package source, scripts, metadata, and release documents to a temporary repository; `python -B scripts/package_skill.py` followed by `python -B scripts/validate_skill.py` both passed. Temporary archive SHA-256: `ae50e152c1268461ecb30a0ba39e8ce8e3d6292778e62b3b4615dddc48ec5deb`.
- Direct fixture-server checks rejected `../` traversal, an absolute outside path, and a Windows directory junction leading outside the root. A valid inside-root read succeeded; no outside canary was returned.
- Deterministic fake-executor probes reproduced all seven findings. Real CLI execution and all model API calls were replaced; only synthetic credentials and synthetic answers were used. Reproduction harness: temporary `checks.py` (permanent regressions and old-source snapshots are retained in [tooling fixes](./tooling-fixes/corrective-review.md)), executed with `python -B`.
- `git diff --check`: passed. Source/tests/dependency hashes matched the verification copy at the final check.

## Assessment

Request changes to the maintained evaluation tooling before treating this release as ready. The package builder/validator passed the reviewed YAML, ZIP, source-payload, deterministic-output, atomic-replacement, metadata, and release-document checks; no additional actionable defect was found there. CI installs the pinned developer dependency before both deterministic suites and validation, and keeps model runs out of CI.

The existing 13 eval tests exercise the fixture adapter and two early runner rejection paths, but none exercise successful runner lifecycle/resumption or comparison-packet generation. Consequently they remain green despite the reproduced evidence-integrity and cleanup defects. Add deterministic coverage at those boundaries with fake executors and credentials, without making CI call a model.

The intentionally pending root `dist` rebuild was not treated as a bug. A root archive update observed during review was left untouched. SKILL prose, human-document/report integration, real model behavior, hosted CI, other-host installation, and publication remain the parent's responsibility. No source, tests, configuration, root archive, Git state, or external system was modified by this review; the only repository write was this report. No agents were spawned.

Reviewed source SHA-256 identifiers:

| File | SHA-256 |
| --- | --- |
| `scripts/validate_skill.py` | `d27c1b443420fdc5dd89f74148c52020f2a4a3e049218226ee54018414917e5d` |
| `scripts/package_skill.py` | `4cf8519bbd97be1e94f39e789ff0ed08bd162c67eb51a8af01e1e772689a5bbe` |
| `evals/run_behavior.py` | `3442cd132052f712b6976dbe376ffdc8e46b60b78011e89b67ce3ab59ecb312c` |
| `evals/prepare_comparison.py` | `fbdd40b417cbcebd693f06c772e2c2a74950568e0d5a09865e3ca3aed629513d` |
| `evals/fixtures/fixture_server.py` | `3b88fccd87a88429da1812bc97be28a62d5e53524301343463b717489db3ba89` |
| `evals/test_fixtures.py` | `93758782b89294136c3fdb67ba4f594997a5b729fa568116490af53d24e9eb2f` |
