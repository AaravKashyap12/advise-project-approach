# Changelog

## 0.6.0 - 2026-08-11

### Multi-Agent Portability Release

This release removes agent-specific lock-in and makes the skill portable across pi, Claude, Codex, and any agent harness that loads Markdown-based skill instructions.

#### Removed (Claude-Specific Files)

- **Removed `.claude-plugin/plugin.json`** — Claude-only plugin metadata that prevented other agents from treating this as a standard skill. The skill works without agent-specific manifest files.
- **Removed `skills/advise-project-approach/agents/openai.yaml`** — OpenAI/Codex-specific agent interface file with Claude-style `$advise-project-approach` invocation syntax. This syntax is not portable and confused non-Claude agents.
- **Removed `dist/advise-project-approach.skill`** — Pre-packaged zip archive in a Claude-specific format. The source `SKILL.md` is the single source of truth; pre-built archives add maintenance burden and drift risk.
- **Removed `scripts/package_skill.py`** — Packaging script for the now-removed `.skill` archive format.

#### Renamed

- **Renamed `CLAUDE.md` to `AGENTS.md`** — The repository guidance file now serves all agents, not just Claude. Includes multi-agent install instructions for pi, Claude, Codex, and generic harnesses.

#### Removed (SKILL.md Bloat)

- **Removed "Community Research Permission" section** — This section required the agent to ask permission before using X/Reddit/YouTube sources, adding a round-trip for every research-heavy request. The hard gates and evidence-first protocol already prevent uncited claims; an extra permission prompt adds friction without improving output quality.
- **Removed Agent-Reach adapter section** — Referenced `https://github.com/Panniantong/agent-reach`, an external adapter with uncertain availability, browser session dependencies, and platform-specific backends. Bundling optional adapter guidance into the core skill creates portability problems and maintenance debt. The skill already documents how to use available browsing/search tools.
- **Consolidated Decision Methodology** — Merged the verbose "Decision Methodology" section with the existing "Workflow" checklist to eliminate repetition. The 7-step framework remains but is now concise.
- **Consolidated External Research Rules** — Merged the "Research capability routing" sub-section into the main research section. Removed adapter-specific routing logic that assumed specific tool availability.
- **Streamlined output contracts** — Removed redundant explanatory text around the pre-build and mid-build templates while preserving all required headings and deliverables.

#### Updated

- **README.md** — Replaced Claude/Codex-specific install instructions with agent-agnostic instructions for pi, Claude, Codex, and generic agents. Removed references to deleted files. Updated repo structure diagram.
- **README.md** — Updated "Works Beyond Claude/Codex" section to reflect that the skill is now fully portable by default, not just "copyable."
- **README.md** — Added v0.6.0 release notes.

#### Why These Changes

The original skill was designed for Claude/Codex but its core value — evidence-based project advice — is agent-agnostic. The Claude-specific files (`.claude-plugin/`, `agents/openai.yaml`, `dist/*.skill`) created three problems:

1. **Discovery barrier** — Agents that scan for standard skill formats see agent-specific metadata and may skip or misparse the skill.
2. **Maintenance burden** — Multiple metadata files must be kept in sync with the actual `SKILL.md` content. The packaging script, validation script, and CI workflow all existed to maintain files that add no runtime value.
3. **False dependency** — Users and agents see optional adapters (Agent-Reach) and plugin metadata and assume they are required, when the skill works from `SKILL.md` alone.

The "Community Research Permission" section was removed because it optimized for the wrong failure mode. The skill already has hard gates requiring evidence citations and date-stamped claims. Adding a permission prompt before research sources treats the agent as incapable of following its own evidence rules, and adds a user interaction that most research-heavy requests don't need.

The Agent-Reach adapter was removed because it externalizes a capability (web browsing) that most agent harnesses already provide natively. Documenting an optional adapter that may not exist in the user's environment creates more confusion than value.

#### Migration

- If you used `dist/advise-project-approach.skill` to install, switch to copying `skills/advise-project-approach/SKILL.md` directly.
- If your installer relied on `.claude-plugin/plugin.json`, copy the skill folder manually.
- If you referenced `CLAUDE.md`, use `AGENTS.md` instead.

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
