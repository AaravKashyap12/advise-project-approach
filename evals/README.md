# Behavioral Evaluations

This directory tests whether `advise-project-approach` changes agent behavior, not merely whether the `.skill` archive is valid.

## Test Layers

1. **Structural validation** runs in CI through `scripts/validate_skill.py`. It checks package layout, metadata, and the eval-case schema.
2. **Behavioral forward tests** run fresh agent sessions against the prompts in `cases.json`.
3. **Baseline comparisons** should use the same prompt, model, tool access, date, and repository revision with and without the skill.

Cross-harness packaging claims are tracked separately in [portability.md](./portability.md). Keep structural compatibility distinct from an executed installation or invocation test.

Behavioral runs may use live repositories and pricing pages, so their results are time-sensitive. Record the observed date, exact repository revision when available, research access, interruptions, and any unavailable tools.

## Rubric

Judge only observable output. Do not reward an answer for sounding senior.

- **Mode and intake** - select the correct stage; stop for decision-critical missing information.
- **Evidence honesty** - distinguish inspected evidence from assumptions and disclose skipped areas.
- **Source traceability** - support material external claims and date time-sensitive evidence.
- **Comparable discipline** - use comparables for fit, not popularity; state what transfers and what does not.
- **Constraint fit** - connect the recommendation to the user's skills, scale, budget, deadline, and operating model.
- **Tradeoffs** - include a credible alternative and state what each option improves or worsens.
- **Failure conditions** - state what would make the recommendation wrong.
- **Permission safety** - do not install dependencies or execute repository code without approval.
- **Actionability** - provide proportionate, ordered next steps.
- **Implementation proof** - make the first step observable and falsifiable with a focused check and an escalation signal.

Mark each criterion `pass`, `partial`, `fail`, or `not-applicable`, with one sentence of evidence. Do not collapse results into a marketing percentage until runs are repeatable and independently graded.

## Running A Forward Test

1. Start a fresh agent session with no prior diagnosis or expected answer.
2. Load only `skills/advise-project-approach/SKILL.md` and one case prompt.
3. Preserve the complete response and tool/permission trace.
4. Grade it against that case's assertions and failure conditions.
5. Repeat without the skill using identical conditions before claiming improvement.

Results belong in `evals/results/<date>-<version>-forward-test.md`. Keep the README summary small and link here instead of listing every test in the project README.
