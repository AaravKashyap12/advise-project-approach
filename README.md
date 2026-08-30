<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/brand/lockup-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./assets/brand/lockup-light.svg">
    <img alt="advise-project-approach" src="./assets/brand/lockup-light.svg" width="680">
  </picture>
</p>

<p align="center"><strong>AI agents should not give project advice from vibes.</strong></p>

<p align="center">
  <strong>
    <a href="#one-line-install">Install</a> |
    <a href="./skills/advise-project-approach/SKILL.md">Skill source</a> |
    <a href="#whats-new-in-v072">What's new in v0.7.2</a> |
    <a href="#demo">Examples</a> |
    <a href="#evaluation">Tests &amp; evidence</a> |
    <a href="./CHANGELOG.md">Changelog</a> |
    <a href="./CONTRIBUTING.md">Contributing</a>
  </strong>
</p>

`advise-project-approach` is an agent skill for project planning, course correction, and review. Its portable `SKILL.md` can be loaded by Codex, Claude Code, pi, Hermes, and other Agent Skills-compatible harnesses.

Portability is a design contract, not proof of identical behavior in every host. See the [host evidence matrix](./evals/portability.md).

Before recommending a stack, architecture, vendor, refactor, or shipping plan, it checks:

- your actual constraints
- comparable real-world projects
- tradeoffs and failure conditions
- cost and lock-in realities
- when the recommendation becomes wrong

## Use It When

- you have a rough project idea and need a build plan
- your repo is getting messy and you need course correction
- you are choosing between stacks or vendors
- you want a review before shipping
- you want the agent to explain what not to build yet

## One-Line Install

```bash
npx skills@latest add AaravKashyap12/advise-project-approach --skill advise-project-approach
```

This uses the open `skills` installer to fetch the repo from GitHub and install only this skill. It requires Node.js/npm. Review installed skills before use; skills run with your agent's normal permissions.

## Source of Truth

The runtime skill spec lives in [skills/advise-project-approach/SKILL.md](./skills/advise-project-approach/SKILL.md). That file is the source of truth for the workflow agents actually run.

Everything else in this repo exists to package, explain, test, or distribute that skill.

## What's New in v0.7.2

v0.7.2 addresses concrete failures found by independent audits, adversarial package tests, and repeated model evaluations.

- Adds no-clobber and recovery checks for advice that changes user data, plus stronger concurrency-test guidance.
- Keeps private project details out of public research queries and stops research after an inconclusive follow-up.
- Clarifies project-stage routing, accepted intake unknowns, safety prerequisites, and requested answer limits.
- Hardens YAML/metadata, archive integrity, release consistency, and failed-build handling, with permanent regression tests.
- Preserves failures, mixed baseline comparisons, and post-fix evidence in a [dedicated audit report](./evals/results/2026-08-31-rigorous-audit/REPORT.md).

See the [full changelog](./CHANGELOG.md) for earlier versions.

## Where This Fits

Use recent-signal tools to discover what changed.

Use `advise-project-approach` to decide what to build, change, defer, or avoid.

The skill is not trying to be a general search engine. It is a project-judgment workflow for turning evidence into engineering decisions.

## Try These Prompts

```text
"What's the best way to build a self-hosted bookmark manager?"
"Research comparable projects before I start this."
"I'm halfway through building a Node/Express API. Is my approach right?"
"Review my finished project at github.com/owner/repo."
"Should I use Postgres or SQLite for this?"
"What stack should I use given I know Python and want to self-host?"
"Should I use Supabase/Firebase/Neon/Vercel, or will pricing hurt later?"
```

## What It Does

Drop it into your agent and it will:

- **Pre-build:** Research your stack, find comparable real projects, compare architecture options, and hand you a build plan before you commit to anything you will regret in month three.
- **Mid-build:** Inspect your repo, identify what is actually wrong, not just what is fashionable to fix, and give you a prioritized list of changes ordered by impact.
- **Post-build:** Review your finished project against mature comparables, call out the gaps, and tell you what to harden before you ship.

It does the research loop a good engineer would do manually: understand the goal, inspect the evidence, study credible comparables, evaluate the tradeoffs, and recommend the highest-leverage path.

No vibes. Evidence first.

## Works Across Agent Harnesses

The workflow is self-contained in its runtime skill file:

```text
skills/advise-project-approach/SKILL.md
```

From a local clone, install the same skill folder into the location your harness scans:

| Harness | Local skill location |
| --- | --- |
| pi | `~/.agents/skills/` or `~/.pi/agent/skills/` |
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Other compatible agents | Point the loader at the skill folder or `SKILL.md` |

```bash
cp -r skills/advise-project-approach <your-agent-skill-directory>/
```

Pi documents recursive discovery of directories containing `SKILL.md` and permits freeform additional files. See [pi's skill documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md).

The packaged `.skill` archive, `.claude-plugin/plugin.json`, and `agents/openai.yaml` are additive compatibility layers for installers and host UIs. They do not change the portable `SKILL.md` workflow, and harnesses that do not use them can ignore them.

## Other Install Methods

To inspect the available skill before installing:

```bash
npx skills@latest add AaravKashyap12/advise-project-approach --list
```

### Manual Download

Download the packaged skill:

[dist/advise-project-approach.skill](./dist/advise-project-approach.skill)

Or install from the GitHub release:

[Download the v0.7.2 release asset](https://github.com/AaravKashyap12/advise-project-approach/releases/download/v0.7.2/advise-project-approach.skill)

#### Skill UI

1. Download `dist/advise-project-approach.skill`.
2. Open your agent's skill settings.
3. Upload the `.skill` file.
4. Start a new conversation.

### Plugin Metadata

This repo also includes `.claude-plugin/plugin.json` for plugin-aware installers that can read skill collections from GitHub repositories.

## Demo

```text
You: I want to build a self-hosted bookmark manager. Solo dev, Python background, want tags and full-text search.

Agent, with skill: researches linkding, Linkwarden, LinkAce, official framework docs, and relevant search/storage options.

## Project Approach: Self-Hosted Bookmark Manager

### TL;DR
Go with Django + SQLite FTS5 or Postgres full-text search, depending on your hosting target and expected scale. Keep the main UI server-rendered with HTMX, Turbo, or light JavaScript unless the UI needs true SPA complexity. This matches your Python skills, keeps deployment simple, and is backed by nearby real projects like linkding.

### Comparable Projects
1. linkding - github.com/sissbruecker/linkding; Django, DRF, Huey, Turbo/Lit, Docker, optional Postgres; nearest domain match; limits: current details must be verified at review time.
2. Linkwarden - github.com/linkwarden/linkwarden; heavier collaborative bookmark manager; useful contrast for when archiving/collaboration matter more than simplicity.
3. LinkAce - linkace.org; mature self-hosted bookmark manager in a different stack; useful for feature comparison, less useful for implementation fit.
```

The demo avoids hard-coded star counts and "latest" dates because those decay. The skill requires the agent to verify those values at review time.

See more examples:

- [Illustrative contrasts with generic advice, not measured A/B tests](./examples/ab-comparisons.md)
- [Pricing and operating-cost example](./examples/pricing-operating-cost.md)
- [Pre-build bookmark manager](./examples/prebuild-bookmark-manager.md)
- [Mid-build Express API](./examples/midbuild-express-api.md)
- [Post-build FastAPI template](./examples/postbuild-fastapi-template.md)

## Why This Is Different From Just Asking

Without the skill, an agent will usually give you an answer. This skill makes it give you an accountable answer:

- Every "active" or "maintained" claim needs an exact date or adoption signal.
- Comparable projects are verified against real repos, docs, or other primary sources.
- Comparables must be separated into what transfers and what should not be copied.
- Pricing claims must distinguish "free to start" from "cheap to operate."
- Vendor choices must consider storage, bandwidth, usage limits, add-ons, migration cost, and lock-in.
- If no repo was provided, it says "advisory from description" instead of pretending it inspected files.
- Large repos are mapped first, then sampled by relevance instead of read blindly.
- The recommendation includes what you gain, what you give up, what becomes harder later, and when it becomes wrong.
- A self-check runs before output: is this grounded in actual project constraints, or is it generic?

## What It Produces

### Pre-Build

The recommendation and constraint fit, relevant evidence, a credible alternative and tradeoffs, the first useful action and its checks, and what could reverse the decision. Vague ideas start with intake; bounded questions stay bounded.

### Mid-Build or Post-Build

Prioritized, file-grounded findings; what to keep, change, and defer; inspection limits; and a focused validation plan. Report length follows the requested scope, not a mandatory list of headings.

## Guardrails

The skill instructs the agent to avoid the following. These are not guarantees of model behavior; verify material advice and sources.

- Invent star counts, last-commit dates, benchmark numbers, or production adoption claims.
- Treat "free to start" as proof that a vendor is cheap to operate.
- Invent prices, quotas, usage limits, or cost estimates without sources.
- Pretend it reviewed files when you only gave it a description.
- Tell you to add auth, tests, or Docker if you already have them.
- Recommend something because it is trending instead of because it fits your constraints.
- Give a production-grade review to a weekend prototype without calibrating the advice.

## Repo Structure

```text
.
|-- README.md
|-- LICENSE
|-- CHANGELOG.md
|-- ROADMAP.md
|-- CONTRIBUTING.md
|-- SECURITY.md
|-- AGENTS.md
|-- CLAUDE.md
|-- assets/
|   `-- brand/
|       |-- lockup-dark.svg
|       `-- lockup-light.svg
|-- .claude-plugin/
|   `-- plugin.json
|-- .github/
|   `-- workflows/
|       `-- validate.yml
|-- dist/
|   `-- advise-project-approach.skill
|-- skills/
|   `-- advise-project-approach/
|       |-- SKILL.md
|       `-- agents/
|           `-- openai.yaml
|-- examples/
|   |-- ab-comparisons.md
|   |-- pricing-operating-cost.md
|   |-- prebuild-bookmark-manager.md
|   |-- midbuild-express-api.md
|   `-- postbuild-fastapi-template.md
|-- evals/
|   |-- README.md
|   |-- cases.json
|   |-- portability.md
|   |-- run_behavior.py
|   |-- prepare_comparison.py
|   |-- fixtures/
|   `-- results/
|-- tests/
|-- requirements-dev.txt
|-- scripts/
|   |-- package_skill.py
|   `-- validate_skill.py
```

The packaged `.skill` file is a zip archive containing the `advise-project-approach/` skill folder.

## Development

Install developer-only dependencies, then rebuild and validate after edits:

```bash
python -m pip install -r requirements-dev.txt
python scripts/package_skill.py
python scripts/validate_skill.py
```

See [Contributing](./CONTRIBUTING.md) for regression-test and release commands. CI runs both deterministic suites, validates/rebuilds the archive, and rejects uncommitted artifact drift. People installing the skill do not need Python or these developer dependencies.

## Evaluation

Tests cover package integrity and model behavior separately. Model cases include intake, narrow planning, pricing arithmetic, repository review, prompt injection, secret handling, large-repository sampling, and unavailable research.

The August 31 audit found real failures and did not show a general advantage over the no-skill baseline. Those results and post-fix runs are retained with prompts, source hashes, tool traces, and qualitative blind reviews. Earlier exploratory scores are historical observations, not calibrated quality guarantees.

[Methodology and commands](./evals/README.md) | [Behavioral cases](./evals/cases.json) | [Regression tests](./tests/) | [Latest audit and retest](./evals/results/2026-08-31-rigorous-audit/REPORT.md) | [Portability audit](./evals/portability.md)

Controlled model tests use synthetic fixtures and one model; live research quality and other hosts still need separate verification. No broad improvement percentage is claimed.

## Contributing

Issues and PRs are welcome. The most useful contributions are:

- New repo test cases: a repo, what the skill got wrong, and what it should have said.
- Evidence discipline failures: cases where a claim was made without a verifiable source.
- Mode selection bugs: cases where the skill picked the wrong operating mode.

## License

MIT

---

### Portfolio

See more of my work at [https://www.aaravkashyap.live/](https://www.aaravkashyap.live/).
