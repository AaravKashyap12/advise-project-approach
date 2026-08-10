# Changelog

## Unreleased

## 0.5.0 - 2026-08-11

- Added a turn-ending intake gate so vague project ideas cannot receive invented product or stack recommendations before constraints are known.
- Added required evidence status, constraint fit, comparable evidence, alternatives, failure conditions, and next actions to every completed recommendation.
- Added an explicit permission boundary before running repository tests, builds, linters, audits, benchmarks, or dependency installation.
- Added bounded first-pass repository inspection and external-research stopping rules.
- Added a reusable behavioral evaluation matrix, rubric, and the first recorded six-case forward-test report.
- Replaced the growing README test-case list with links to the dedicated `evals/` evidence area.
- Added a theme-aware project mark and compact README navigation.
- Reduced the README release summary to the current version and moved older history to this changelog.

## 0.4.0 - 2026-08-09

- Added a lightweight intake interview for vague pre-build requests while skipping unnecessary questions when constraints are already clear.
- Added user permission before researching current community signals from X, Reddit, and YouTube.
- Added capability routing, source fallback, and evidence-coverage disclosure for external research.
- Added optional Agent-Reach adapter guidance without bundling its dependencies or requiring installation.
- Added external-content prompt-injection and secret-handling guardrails.

## 0.3.0 - 2026-06-01

- Added pricing and operating-cost analysis for managed services, hosting, storage, auth, AI APIs, observability, and vendor lock-in.
- Added explicit "free to start is not cheap to operate" safeguards for stack and vendor recommendations.
- Made tradeoffs more aggressive: what you gain, what you give up, what becomes harder later, and when the recommendation becomes wrong.
- Added vendor-agnostic README guidance for copying `SKILL.md` into non-Claude/non-Codex agent harnesses.
- Added a pricing-focused example showing how generic "use Supabase" advice should be challenged.
- Updated trigger metadata and package metadata for cost/vendor-choice use cases.

## 0.2.0 - 2026-05-30

- Added an explicit decision methodology: constraints, comparables, transferable patterns, tradeoffs, recommendation, and failure conditions.
- Added comparable-project bias safeguards so popularity, stars, and mature-project infrastructure do not override user fit.
- Added repo-size and token-budget guidance for small, medium, large, and huge codebases.
- Added output requirements for inspection scope, skipped areas, transferable patterns, and limits.
- Added A/B comparison examples showing where the skill should change generic AI advice.

## 0.1.0 - 2026-05-29

- Initial public package layout.
- Added `advise-project-approach` skill source under `skills/`.
- Added packaged `.skill` archive under `dist/`.
- Added examples and validation notes for launch/readme proof.
- Added repository maintenance docs: `CONTRIBUTING.md`, `SECURITY.md`, and `CLAUDE.md`.
- Added `.claude-plugin/plugin.json` metadata for plugin-aware installers.
- Added validation and packaging scripts plus a GitHub Actions validation workflow.
- Removed obsolete draft archives for `project-analyzer` and `review-codebase`.
