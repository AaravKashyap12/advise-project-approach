# Executed Audit Matrix

PASS means the stated invariant held; FAIL is a reproduced audit defect, not a harness crash. OBSERVED records behavior without asserting an undocumented requirement.

| ID | Category | Result | Validator exit | CI exits | Invariant |
| --- | --- | --- | --- | --- | --- |
| B01 | baseline | PASS | - | [0, 0, 0, 0] | Normal validation/build/validation/CI diff pass; checked-in bytes match source |
| F01 | frontmatter | PASS | 1 | [1] | Missing name rejected |
| F02 | frontmatter | PASS | 1 | [1] | Missing description rejected |
| F03 | frontmatter | PASS | 1 | [1] | Extra field rejected |
| F04 | frontmatter | PASS | 1 | [1] | Wrong name rejected |
| F05 | frontmatter | PASS | 1 | [1] | 1025-character description rejected |
| F06 | frontmatter | PASS | 0 | [0, 0, 0, 0] | 1024-character description accepted |
| F07 | frontmatter | FAIL | 0 | [0, 0, 0, 0] | Unterminated YAML quote rejected |
| F08 | frontmatter | FAIL | 0 | [0, 0, 0, 0] | Duplicate YAML key rejected |
| F09 | frontmatter | FAIL | 0 | [0, 0, 0, 0] | List-valued description rejected |
| F10 | frontmatter | FAIL | 0 | [0, 0, 0, 0] | Null description rejected |
| F11 | frontmatter | FAIL | 0 | [0, 0, 0, 0] | Empty description rejected |
| F12 | frontmatter | FAIL | 1 | [1] | Valid single-quoted YAML name accepted |
| F13 | frontmatter | FAIL | 1 | [1] | Valid folded YAML description accepted |
| F14 | frontmatter | FAIL | 0 | [0, 0, 0, 0] | Boolean description rejected |
| F15 | frontmatter | PASS | 1 | - | Missing opening delimiter rejected |
| F16 | frontmatter | PASS | 1 | - | Missing closing delimiter rejected |
| M01 | metadata | PASS | 1 | - | Missing skills/advise-project-approach/agents/openai.yaml rejected |
| M02 | metadata | PASS | 1 | - | Missing .claude-plugin/plugin.json rejected |
| M03 | metadata | PASS | 1 | - | Missing VERSION rejected |
| M04 | metadata | PASS | 1 | - | Missing AGENTS.md rejected |
| M05 | metadata | PASS | 1 | - | Missing CLAUDE.md rejected |
| M06 | metadata | PASS | 1 | - | Missing README.md rejected |
| M07 | metadata | PASS | 1 | - | Missing skills/advise-project-approach/SKILL.md rejected |
| M08 | metadata | PASS | 1 | - | Missing dist/advise-project-approach.skill rejected |
| M09 | metadata | PASS | 1 | - | Missing evals/cases.json rejected |
| M10 | metadata | FAIL | 0 | [0, 0, 0, 0] | Malformed openai.yaml rejected |
| M11 | metadata | OBSERVED | 0 | [0, 0, 0, 0] | Characterize empty optional host metadata (required content not specified locally) |
| M12 | metadata | FAIL | 0 | [0, 0, 0, 0] | Plugin skill path resolving to no source rejected |
| M13 | metadata | OBSERVED | 0 | [0, 0, 0, 0] | Characterize missing plugin name (external loader schema not exercised) |
| M14 | metadata | PASS | 1 | - | CLAUDE.md without import rejected |
| M15 | metadata | PASS | 1 | - | Unexpected source file rejected |
| A01 | archive | PASS | 1 | [1] | Additional archive file rejected |
| A02 | archive | PASS | 1 | [1] | Missing archive member rejected |
| A03 | archive | FAIL | 0 | [0, 0, 0, 1] | Changed archive payload rejected |
| A04 | archive | FAIL | 0 | [0, 0, 0, 1] | Zero-byte expected members rejected |
| A05 | archive | FAIL | 0 | [0, 0, 0, 1] | Duplicate archive member rejected |
| A06 | archive | FAIL | 0 | [0, 0, 0, 1] | Unexpected directory archive entry rejected |
| A07 | archive | FAIL | 0 | [0, 0, 0, 1] | Traversal-shaped directory entry with payload rejected |
| A08 | archive | FAIL | 0 | [0, 0, 0, 1] | Corrupt member CRC rejected |
| A09 | archive | PASS | 1 | [1] | Non-ZIP artifact rejected |
| A10 | archive | PASS | 1 | [1] | Wrong archive root rejected |
| S01 | staleness | FAIL | 0 | [0, 0, 0, 1] | Source change with stale dist rejected by validator |
| S02 | staleness | FAIL | 0 | [0, 0, 0, 1] | Metadata change with stale dist rejected by validator |
| V01 | release | PASS | 1 | [1] | Plugin version mismatch rejected |
| V02 | release | PASS | 1 | [1] | README current version mismatch rejected |
| V03 | release | PASS | 1 | [1] | README release asset mismatch rejected |
| V04 | release | PASS | 1 | - | Malformed VERSION rejected |
| V05 | release | FAIL | 0 | [0, 0, 0, 0] | SemVer core leading zero rejected |
| V06 | release | FAIL | 0 | [0, 0, 0, 0] | Non-ASCII VERSION digits rejected |
| V07 | release | FAIL | 0 | [0, 0, 0, 0] | Missing changelog rejected |
| V08 | release | FAIL | 0 | [0, 0, 0, 0] | Missing current dated changelog entry rejected |
| V09 | release | FAIL | 0 | [0, 0, 0, 0] | Accumulated old What's New section rejected |
| V10 | release | FAIL | 0 | [0, 0, 0, 0] | Stale visible release references hidden by HTML comment rejected |
| V11 | release | PASS | 1 | - | Malformed plugin JSON rejected |
| V12 | release | PASS | 1 | - | Plugin root array rejected |
| E01 | eval-schema | PASS | 1 | - | Unsupported schema version rejected |
| E02 | eval-schema | FAIL | 0 | [0, 0, 0, 0] | Boolean schema version rejected |
| E03 | eval-schema | OBSERVED | 0 | [0, 0, 0, 0] | Characterize numerically equivalent schema version 1.0 (integer lexical form not required) |
| E04 | eval-schema | PASS | 1 | - | Fewer than six cases rejected |
| E05 | eval-schema | PASS | 1 | - | Duplicate case ID rejected |
| E06 | eval-schema | PASS | 1 | - | Empty case ID rejected |
| E07 | eval-schema | OBSERVED | 0 | [0, 0, 0, 0] | Characterize whitespace ID (non-empty, but trimming policy not specified) |
| E08 | eval-schema | PASS | 1 | - | Invalid mode rejected |
| E09 | eval-schema | PASS | 1 | - | Blank prompt rejected |
| E10 | eval-schema | PASS | 1 | - | Numeric prompt rejected |
| E11 | eval-schema | PASS | 1 | - | Empty assertions rejected |
| E12 | eval-schema | PASS | 1 | - | Non-string assertion rejected |
| E13 | eval-schema | PASS | 1 | - | Blank failure condition rejected |
| E14 | eval-schema | PASS | 1 | - | Missing failure_conditions rejected |
| E15 | eval-schema | PASS | 1 | - | Cases object instead of array rejected |
| E16 | eval-schema | PASS | 1 | - | Null case element rejected |
| E17 | eval-schema | PASS | 1 | - | List-valued mode rejected |
| E18 | eval-schema | PASS | 1 | - | Malformed eval JSON rejected |
| E19 | eval-schema | PASS | 1 | - | Array eval root rejected |
| R01 | reproducibility | PASS | - | - | Seven same-runtime builds remain byte-identical across metadata/order/newline/env changes |
| P01 | failure-atomicity | FAIL | - | - | Failed UTF-8 build preserves last good dist archive |
| P02 | failure-atomicity | PASS | - | - | Missing source build fails without replacing dist |

```json
{
  "tests": 78,
  "counts": {
    "PASS": 48,
    "FAIL": 26,
    "OBSERVED": 4
  },
  "categories": {
    "baseline": {
      "PASS": 1
    },
    "frontmatter": {
      "PASS": 8,
      "FAIL": 8
    },
    "metadata": {
      "PASS": 11,
      "FAIL": 2,
      "OBSERVED": 2
    },
    "archive": {
      "PASS": 4,
      "FAIL": 6
    },
    "staleness": {
      "FAIL": 2
    },
    "release": {
      "PASS": 6,
      "FAIL": 6
    },
    "eval-schema": {
      "PASS": 16,
      "FAIL": 1,
      "OBSERVED": 2
    },
    "reproducibility": {
      "PASS": 1
    },
    "failure-atomicity": {
      "FAIL": 1,
      "PASS": 1
    }
  },
  "subprocess_commands": 329,
  "ci_scenarios": 43,
  "ci_accepted": 21,
  "ci_rejected": 22,
  "elapsed_seconds": 39.156,
  "harness_error": null,
  "production_files_unchanged": true
}
```
