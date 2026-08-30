# Independent Packaging Audit

Date: 2026-08-31. Target: `C:\Users\aarav\Desktop\skills`, version `0.7.1`, Git HEAD `c4885d2f0155fbf912f3ad2489ac75d637545ba1`.

Scope: deterministic packaging, structural validation, local execution of CI commands, and adversarial mutations. Runtime prompt quality, live installations, hosted CI runs, and releases are excluded. AGENTS.md was read first. This audit was performed independently without subagents or prior audit conclusions.

## Verdict

**Current artifact: PASS in the tested environment. Adversarial validation: FAIL.** The checked-in artifact matches normalized source bytes, and the normal checks pass. Six grouped findings below expose validation gaps and a non-atomic packaging failure. These are reproduced mutations, not claims that the current release already contains those defects.

Final run: **78 scenarios: 48 PASS, 26 FAIL, 4 OBSERVED**, 329 captured subprocess commands, no harness errors. The 26 failing invariants group into six findings; they are not 26 independent product bugs.

Of 43 local CI-sequence scenarios, 21 passed and 22 failed. The 21 passing sequences comprise two valid controls, four observations without an asserted contract, and **15 invalid-source/metadata scenarios that CI accepted**. CI correctly rejected all eight archive-integrity/staleness cases that standalone validation missed, via its final diff. Two valid YAML forms were incorrectly rejected before the build.

## Findings

### 1. [P2 / Medium] Frontmatter parsing accepts invalid YAML and rejects valid YAML

Confidence: high. Location: [validate_skill.py:34](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L34), [line 45](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L45), [line 75](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L75). Contract: YAML frontmatter and required trigger fields, [AGENTS.md:40](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/AGENTS.md#L40).

The parser splits lines at the first colon and strips double quotes rather than parsing YAML. Mutation F07 uses an unterminated quoted description. Installed PyYAML independently raises `ScannerError`, while both validator invocations print `Skill package is valid.` and CI exits `[0, 0, 0, 0]` after packaging those exact bytes. F08's duplicate `name` key is silently overwritten; a duplicate-rejecting SafeLoader oracle rejects it. F09-F11 and F14 accept list, null, empty/null, and boolean descriptions as if they were strings.

Conversely, F12's single-quoted matching name and F13's folded string description parse correctly in PyYAML but fail validation, respectively with `Frontmatter name must match skill folder name` and `Invalid frontmatter line:   Audit fixture`. These valid values remain within the field allowlist and length budget.

Impact: a rebuilt, fully CI-green package can carry unparseable or incorrectly typed portable metadata; conventional valid YAML is needlessly blocked. No loader installation was performed. Direction: parse a YAML mapping, explicitly validate unique keys and string types, then apply the existing name and length constraints. Preserve a portable documented syntax contract.

### 2. [P2 / Medium] Host metadata syntax and plugin skill paths are not validated

Confidence: high for structural failures; downstream installer behavior not tested. Locations: [validate_skill.py:55](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L55), [line 144](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L144). Relevant fields: [openai.yaml:1](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/skills/advise-project-approach/agents/openai.yaml#L1), [plugin.json:22](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/.claude-plugin/plugin.json#L22).

M10 replaces `openai.yaml` with `interface: [unterminated`. PyYAML raises `ParserError`; standalone validation and the complete CI sequence still succeed, including the unchanged regenerated malformed metadata. The validator checks only that this YAML file exists.

M12 changes the plugin's `skills` list to `./skills/missing-skill`, which the independent filesystem oracle confirms does not exist. Validation and CI still exit zero: only the plugin version is inspected. This leaves declared discovery metadata pointing at absent source.

Impact: CI certifies structurally broken optional compatibility layers despite healthy portable source. Direction: parse supplied host metadata and check declared repository-local skill paths against existing allowed source directories. Empty optional metadata (M11) and missing plugin name (M13) are recorded only as observations because their external loader requirements were not tested.

### 3. [P2 / Medium] Standalone archive validation ignores payload integrity, duplicates, and source freshness

Confidence: high. Location: [validate_skill.py:81](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L81), especially [line 85](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L85). Mitigation: [validate.yml:31](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/.github/workflows/validate.yml#L31).

The validator reduces member names to a set and never reads member bytes. A03 changes a payload, A04 empties both expected members, A05 adds a conflicting duplicate member, A06 adds an unexpected root-directory entry, and A07 adds a traversal-shaped directory entry with data. All print `Skill package is valid.`. No mutation archive was extracted; A07 demonstrates allowlist blindness, not a proven traversal exploit.

A08 flips a byte in a stored member while retaining its original CRC. `ZipFile.read()` independently raises `BadZipFile: Bad CRC-32 for file 'advise-project-approach/agents/openai.yaml'`, yet validation exits zero. S01 and S02 change source/metadata without rebuilding; the independently computed member comparison is false, while validation exits zero.

**CI containment was directly verified:** every one of these eight cases exits `[0, 0, 0, 1]`. Rebuilding restores canonical bytes, then `git diff --exit-code dist/advise-project-approach.skill` detects the candidate artifact mismatch. This is not a demonstrated bypass of the full existing CI pipeline.

Impact: a standalone validator success is not evidence that an artifact can be read or matches the source being reviewed. Direction: enumerate all entries without deduplicating, reject unexpected entries/duplicates, read members to check CRC, and compare expected payloads with normalized source. Retain CI's independent rebuild/diff safeguard.

### 4. [P2 / Medium] Failed packaging destroys the last good artifact

Confidence: high. Locations: [package_skill.py:22](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/package_skill.py#L22), [line 30](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/package_skill.py#L30), [line 38](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/package_skill.py#L38).

P01 writes invalid UTF-8 bytes (`ff 69 6e ...`) to the temporary `agents/openai.yaml`. Initial validation exits zero. Packaging deletes the existing output and opens its final path before attempting to decode inputs; it raises `UnicodeDecodeError` and exits one. The former **13,657-byte valid archive becomes a 22-byte empty ZIP**, with no members. Subsequent validation correctly fails.

Before SHA-256: `b0b1453f662ddd6411965227f521945a0e65fa3143a5d557b90da6680630cdbd`.

After SHA-256: `8739c76e681f900923b900c9df0ef75cf421d39cabb54650c4b9ad19b6a76d85`.

P02 is a control: an absent source directory fails before replacement and preserves the artifact. Impact is bounded local artifact loss, recoverable from source or version control, not loss of production source or a silent CI success. Direction: complete input reads/validation and build to a temporary sibling file; replace the final artifact only after successful ZIP closure.

### 5. [P2 / Medium] Release consistency checks do not enforce documented release constraints

Confidence: high. Locations: [validate_skill.py:139](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L139), [line 151](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L151), [line 154](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L154). Contract: [AGENTS.md:14](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/AGENTS.md#L14), [line 17](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/AGENTS.md#L17).

V07 deletes CHANGELOG.md and V08 removes the current dated release entry. V09 adds an old `What's New` section alongside the current one. V10 changes the visible heading and asset URL to an old release while placing the expected current strings only inside an HTML comment. All four complete CI sequences pass. Raw substring presence does not establish a single visible current section/link; CHANGELOG.md is never checked.

The lower-impact V05/V06 cases also pass the full sequence after synchronizing metadata to `00.7.1` and a version beginning with Arabic-Indic digit U+0660. Python's `\d+` admits leading zeros and Unicode digits rather than the ASCII, no-leading-zero SemVer core promised by the repository.

Impact: green CI does not enforce these documented release-file relationships. Current checked-in metadata is aligned; no published release was audited or changed. Direction: validate canonical version syntax, a dated current changelog entry, and actual current README structures rather than arbitrary substring occurrences. Historical version-bump policy and live release assets remain separate human/remote checks.

### 6. [P3 / Low] Eval schema version accepts a JSON boolean

Confidence: high. Location: [validate_skill.py:97](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/validate_skill.py#L97). Contract: required eval schema, [AGENTS.md:44](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/AGENTS.md#L44), [evals/README.md:7](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/evals/README.md#L7).

E02 changes only `schema_version` from `1` to JSON `true`. Validation and all CI commands succeed because Python compares `True == 1`. A boolean is not a numeric schema identifier. Direction: validate the JSON value type as well as its supported value, excluding booleans.

E03 (`1.0`) is not counted as a defect because a numeric schema contract can treat it as equivalent to one. E07 (whitespace-only ID) is not counted because the local requirement says non-empty without an explicit trimming policy. Malformed JSON, array roots, null case objects, and list-valued modes fail closed, although several produce raw tracebacks rather than friendly validation errors.

## Baseline And Reproducibility

Normal commands executed in an isolated source copy, in CI order:

```powershell
python scripts/validate_skill.py
python scripts/package_skill.py
python scripts/validate_skill.py
git diff --exit-code dist/advise-project-approach.skill
```

B01: exit codes `[0, 0, 0, 0]`; outputs `Skill package is valid.`, `Built dist\advise-project-approach.skill`, `Skill package is valid.`, then an empty diff. Archive member reads succeed and both payloads match normalized source bytes.

R01: seven successful builds, each followed by validation: baseline, repeat, changed mtimes, CRLF source, LF source, reversed file creation order, and changed `PYTHONHASHSEED`/`TZ`/`SOURCE_DATE_EPOCH`. All produce exactly one SHA-256:

```text
b0b1453f662ddd6411965227f521945a0e65fa3143a5d557b90da6680630cdbd
```

All outputs match the checked-in archive. Two members, total archive size 13,657 bytes, timestamp 2026-01-01 00:00:00, Unix creator field 3, permission field 0644, DEFLATE compression. Relevant implementation: [package_skill.py:25](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/package_skill.py#L25), [line 34](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/package_skill.py#L34), [line 38](https://github.com/AaravKashyap12/advise-project-approach/blob/c4885d2f0155fbf912f3ad2489ac75d637545ba1/scripts/package_skill.py#L38).

## Coverage

| Area | Scenarios | PASS | FAIL | OBSERVED | Evidence IDs |
| --- | ---: | ---: | ---: | ---: | --- |
| Normal pipeline | 1 | 1 | 0 | 0 | B01 |
| Frontmatter | 16 | 8 | 8 | 0 | F01-F16 |
| Required files and metadata | 15 | 11 | 2 | 2 | M01-M15 |
| ZIP structure/content | 10 | 4 | 6 | 0 | A01-A10 |
| Stale dist/source | 2 | 0 | 2 | 0 | S01-S02 |
| Release consistency | 12 | 6 | 6 | 0 | V01-V12 |
| Eval schema | 19 | 16 | 1 | 2 | E01-E19 |
| Reproducibility, seven variants | 1 | 1 | 0 | 0 | R01 |
| Failed-build preservation | 2 | 1 | 1 | 0 | P01-P02 |
| **Total** | **78** | **48** | **26** | **4** | |

PASS means a stated invariant held, including deliberate rejection of bad input. FAIL means a reproducible invariant violation. OBSERVED does not assert an undocumented requirement. Seven malformed-input rejection cases terminate with tracebacks; these are counted as successful rejection, not false acceptance or additional findings. This is targeted fixture mutation coverage, not line coverage or exhaustive automated mutation-score analysis.

## Reproduce And Inspect

Run from any directory with Python and Git already available:

```powershell
python C:\Users\aarav\Desktop\skills\evals\results\2026-08-31-rigorous-audit\packaging\audit_packaging.py --repo C:\Users\aarav\Desktop\skills
```

Expected current exit code: **1**, intentionally signaling reproduced audit defects. Exit 0 means all asserted audit invariants hold; exit 2 means a harness error detected during suite execution or changed production bytes. No production fix was made to turn failing tests green.

The harness uses fresh OS-temp copies for each scenario, invokes the original scripts unmodified, and captures exact argv, working directory, stdout, stderr, exit code, timing, fixture differences, payload hashes, and independent YAML/ZIP evidence. Before each local CI simulation it runs `git init -q --template=<empty-temp-template>` and `git -c core.autocrlf=false add -- dist/advise-project-approach.skill` in that temp copy. The staged candidate artifact provides the index baseline for the **exact** CI diff command. There is no commit, clone, push, remote contact, production index update, or copied Git history. CI stages stop at their first failure just as the workflow does.

- [Runnable harness](audit_packaging.py)
- [Per-scenario matrix and counts](matrix.md)
- [Final raw structured results and all 329 commands](results.json)
- [Unabridged subprocess transcript](commands.txt)
- [Exact numbered source excerpts](source-lines.txt)
- [Before/after production SHA-256 manifest](source-manifest.json)
- [Preliminary full-run evidence](preliminary-results.json)
- [Initial temp-permission setup failure](initial-attempt.txt)

The preliminary completed run had 48 PASS / 30 FAIL. Four expectations (M11, M13, E03, E07) were conservatively reclassified as observations, then the entire suite was executed again. Nothing in production changed between runs. This was oracle review, not retrying intermittent test failures until green. The initial setup attempt failed before running any tests because Windows sandbox access was denied to an owner-only `TemporaryDirectory`; the harness now creates its uniquely named scratch directory with inherited permissions. That failed attempt's inaccessible empty directory was not forcibly removed. Completed-run temp trees were cleaned up.

## Environment, Integrity, And Limitations

- Windows 11 build 26200; Python 3.12.13; zlib 1.3.2; Git 2.49.0.windows.1. Parent and subprocess Python paths/versions are captured. Preinstalled PyYAML 6.0.3 supplied an independent syntax/type oracle; a custom SafeLoader constructor additionally rejects duplicate keys. No dependencies were installed. If PyYAML is absent on rerun, oracle availability is explicitly recorded as false.
- All 29 non-result production files have identical before/after SHA-256 values, and the temp snapshot matches that manifest. An independent final PowerShell rehash also found no production drift; `git diff --exit-code` returned zero. The manifest deliberately excludes `.git` and all `evals/results/` so independently owned sibling audit results are neither hashed as production nor copied. Initial Git status was clean; final status contains only the new audit results tree. Sibling audit artifacts appeared during execution and were not inspected or changed. All persistent writes for this audit are inside the requested `packaging/` area.
- Hosted Ubuntu Actions was not launched. The checkout and setup-python actions were inspected, not executed; only their four repository shell commands were reproduced locally. Local index-vs-worktree behavior for the single binary path is equivalent to the final diff under a clean checkout, but does not test GitHub permissions, branch protection, action availability, or remote release automation.
- Byte reproducibility is established only for this runtime and the tested variants. Cross-OS, alternate Python/zlib builds, filesystem case behavior, permission variations, symlinks, concurrent builds, disk-full failures, and interrupted writes were not tested. The changed TZ environment variable is a process-environment perturbation, not a claim that Windows changed the system timezone.
- Source-dependent tests intentionally target this version's current layout and release strings. No loader was installed or invoked, no runtime prompt quality was graded, no mutation archive was extracted, and no network/external system or release was changed. Downstream rejection of malformed metadata is a risk inference; the direct evidence is parser failure or nonexistent paths together with local validation/CI acceptance.
- The validator is not a release-history checker. This audit does not establish whether every prior public push bumped VERSION or whether remote release assets match local dist. AGENTS.md explicitly treats green checks as necessary but insufficient for merging.

No production scripts, source skill, metadata, CI, checked-in dist, or releases were changed. No commits, pushes, installs, or nested subagents were used.
