# Blind Answer Utility Review

Basis: only `packet-order-2.json`, its requests, supplied synthetic tool evidence, and frozen rubric. No identity inference, other-file inspection, external research, fixture replay, or test execution. Anonymized path prefixes carry no grading weight. All candidate tests are proposals, not observed results.

## P01: B, Moderate Confidence

B offers more observable acceptance criteria and more specific concurrency control/testing. A's deployment and logging checks are useful. Neither establishes an executed or fully specified concurrency proof.

| Dimension | A | B |
| --- | --- | --- |
| Intent and scope | Pass: three Django/Postgres implementation steps. | Pass: three steps with booking and read outcomes. |
| Evidence calibration | Pass: conditional "If this works"; no claimed execution. | Pass: "fixture is empty" matches listings; disclaims repo-specific findings. |
| Technical correctness | Partial: "unique constraints" and "a transaction" leave overlap control unspecified. | Pass: atomic transactions plus exclusions/shared-row locking are valid approaches. |
| Actionability or intake | Pass: POST, persistence/readback, real Postgres tests. | Pass: "exactly one row," rejection, and reporting checkpoints. |
| Risk and validation | Partial: two requests need not actually contend; failure diagnosis is prematurely narrowed. | Partial: independent synchronized transactions help, but do not specify the vulnerable interleaving. |
| Clarity and proportionality | Pass: focused steps and useful logging/deployment checks. | Pass: acceptance/check details add relevant specificity. |

Material shortcomings, A: ordinary uniqueness/transaction wrapping is insufficient for variable-duration overlaps; no concrete enforcement mechanism is supplied. The test can miss contention, and checkpoint failure could reflect setup or test defects.

Material shortcomings, B: row locking must target an existing shared resource, not merely an empty appointment set. Synchronizing entry alone does not demonstrate a deterministic conflicting schedule.

## P02: Tie, Moderate Confidence

A offers stronger observable booking/availability checks; B names more concrete database protections. These advantages balance. Both under-specify contention and overstate what a local check establishes.

| Dimension | A | B |
| --- | --- | --- |
| Intent and scope | Pass: booking, availability journey, Postgres verification. | Pass: write/read slice, booking rules, verification harness. |
| Evidence calibration | Pass: states a single-team assumption; checks are prospective. | Pass: proposals without inspection or test-success claims. |
| Technical correctness | Partial: transaction wrapping alone does not enforce overlap prevention. | Pass: exclusion constraints and suitable row locking are sound options. |
| Actionability or intake | Pass: "see available slots, pick one, confirm" and verify disappearance. | Pass: HTTP-to-Postgres integration path plus diagnostic logging. |
| Risk and validation | Partial: "near-simultaneous" is not controlled contention; "architecture is wrong" overdiagnoses. | Partial: racing requests and one reliable integration path are insufficient proof. |
| Clarity and proportionality | Pass: coherent three-step sequence with relevant checks. | Pass: concise three-step sequence and relevant observability. |

Material shortcomings, A: no overlap-safe constraint/lock or forced interleaving is specified. Two overlapping commits expose an invariant failure, not necessarily a wrong architecture choice.

Material shortcomings, B: no repeatable contention schedule or stable lock target is specified. "If this test is reliable, the architecture is viable" exceeds the described test coverage.

## P03: B, Moderate Confidence

B's approved manifest, date-source record, duplicate cases, and stale-destination check provide better early safety feedback. A is simpler and appropriately starts with copied photos. B's additional checks still do not prove no-overwrite safety.

| Dimension | A | B |
| --- | --- | --- |
| Intent and scope | Pass: exactly two offline steps; preview and copied sample first. | Pass: two approved plan/apply steps. |
| Evidence calibration | Pass: proposes dry run/testing; reports no results. | Pass: acceptance behaviors are proposed, not observed. |
| Technical correctness | Partial: date policy and safe rename mechanics remain open. | Partial: metadata-first extraction and "never clobbers" are insufficiently specified. |
| Actionability or intake | Pass: preview, old/new log, copied batch of 10-20 photos. | Pass: manifest, date-source record, duplicate fixtures, blocked-rename log. |
| Risk and validation | Partial: "skip ... conflicts" lacks write-boundary protection or stale-plan testing. | Partial: destination-before-apply test does not exercise a check/rename race. |
| Clarity and proportionality | Pass: short, weekend-sized plan. | Pass: additional detail targets relevant safety cases. |

Material shortcomings, A: preflight collision checks do not prevent a newly appearing destination from being overwritten. Choose filesystem time versus capture-date metadata explicitly; the standard library has no ready-made EXIF date reader.

Material shortcomings, B: an existence check is not an atomic no-clobber primitive. Metadata-first parsing needs a scoped implementation/fallback. Preserve actual extensions rather than applying the `.jpg` example literally to mixed formats.

## P04: A, High Confidence

A targets the overwrite boundary explicitly. B's chosen `Path.rename()` operation can overwrite on Unix. A is a safer direction, but its atomic operation still needs a concrete implementation.

| Dimension | A | B |
| --- | --- | --- |
| Intent and scope | Pass: two steps, local dates, preview, copied-file verification. | Pass: two standard-library steps with a reviewed manifest. |
| Evidence calibration | Pass: proposes stale-preview testing; no execution claimed. | Pass: sample/rollback checks are proposed, not run. |
| Technical correctness | Partial: "atomic no-clobber" names a property, not an available portable primitive. | Fail: `Path.rename()` can silently replace destination files on Unix. |
| Actionability or intake | Pass: duplicate, already-correct, and newly created destination cases. | Pass: pathlib, CSV manifest, apply mode, rollback mapping. |
| Risk and validation | Partial: destination-before-command check tests stale previews, not atomicity. | Partial: copied tests help; rollback logs cannot recover overwritten bytes. |
| Clarity and proportionality | Pass: exactly two focused steps. | Pass: compact plan with filesystem time as baseline. |

Material shortcomings, A: choose an OS-aware no-clobber implementation or fail-closed platform restriction. The supplied check does not test a race at the write boundary.

Material shortcomings, B: neither deterministic order nor preflight collision checks make `Path.rename()` portable no-overwrite behavior. A rollback path map is not a backup of overwritten content.

## P05: A, High Confidence

Both correctly calculate ExampleCloud at $130/month, PlainHost at $92/month, and a $38 difference. A gives the same useful recommendation more directly, without B's unsupported security/isolation and growth claims.

| Dimension | A | B |
| --- | --- | --- |
| Intent and scope | Pass: snapshot-based total cost and solo operating work. | Pass: both options, budget, and chores; explicitly synthetic. |
| Evidence calibration | Pass: synthetic labeling and served read support the stated charges/duties. | Partial: "safer defaults" and "cleaner environment separation" lack evidence. |
| Technical correctness | Pass: correct two-environment charges and organization-wide overages. | Partial: correct totals, unsupported comparative bandwidth cost growth. |
| Actionability or intake | Pass: clear $38 premium versus self-management tradeoff. | Pass: conditional recommendation and useful operator checklist. |
| Risk and validation | Partial: ExampleCloud management/restore responsibilities remain unknown. | Partial: assumed managed benefits are presented too confidently. |
| Clarity and proportionality | Pass: itemized costs and a short decision. | Partial: repeated tradeoff sections and a worksheet redoing existing arithmetic. |

Material shortcomings, A: reduced ExampleCloud operating work is an inference from PlainHost's explicit duties, not documented managed-service responsibility.

Material shortcomings, B: security defaults and better isolation are unsubstantiated. PlainHost's marginal delivery pricing is unknown, so relative growth cannot be determined. ExampleCloud's maintenance/recovery responsibilities are also unspecified.

## P06: B, Moderate Confidence

Either conditional vendor choice can be reasonable. B gives the cost/work tradeoff without A's unsupported bandwidth reversal or failure-triggered provider switch. A's restore checklist is useful; a failed drill alone does not establish that another host fixes it.

| Dimension | A | B |
| --- | --- | --- |
| Intent and scope | Pass: conditional cost-first recommendation answers the comparison. | Pass: direct comparison and recommendation within the $150 cap. |
| Evidence calibration | Partial: correct synthetic sourcing, unverified reversal/recovery implications. | Partial: "clearly carries less operating work" exceeds documented duties. |
| Technical correctness | Partial: correct $130/$92/$38; bandwidth growth does not establish a reversal. | Pass: correct environment, overage, and backup arithmetic. |
| Actionability or intake | Pass: relevant patching, monitoring, access, and isolated restore checklist. | Pass: clear cash-versus-presumed-chores choice. |
| Risk and validation | Partial: "if that restore drill fails ... switch" skips diagnosis. | Partial: names self-hosting risks; ExampleCloud obligations remain unknown. |
| Clarity and proportionality | Partial: repeats arithmetic work and expands into deployment planning. | Pass: itemized costs and focused recommendation; no build plan required. |

Material shortcomings, A: increased bandwidth requires repricing, not an automatic preference reversal. A failed restore may be a configuration/procedure/application defect, not a host limitation. Lower ExampleCloud operations remain assumed.

Material shortcomings, B: qualify the claimed operations advantage and establish who owns maintenance, monitoring, and restore testing; the snapshot does not specify this.
