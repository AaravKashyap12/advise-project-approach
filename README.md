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
    <a href="#whats-new-in-v071">What's new in v0.7.1</a> |
    <a href="#demo">Examples</a> |
    <a href="#evaluation">Tests &amp; evidence</a> |
    <a href="./CHANGELOG.md">Changelog</a> |
    <a href="./CONTRIBUTING.md">Contributing</a>
  </strong>
</p>

`advise-project-approach` is an agent skill for project planning, course correction, and review. Its portable `SKILL.md` can be loaded by Codex, Claude Code, pi, Hermes, and other Agent Skills-compatible harnesses.

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

## What's New in v0.7.1

v0.7.1 keeps implementation-proof advice proportionate after the first controlled A/B exposed unnecessary report expansion.

- Makes the first numbered step itself an end-to-end slice instead of horizontal schema or setup work.
- Adds a narrow-advice route that preserves the user's requested shape and count without unnecessary browsing or full-report expansion.
- Requires testable escalation thresholds rather than vague complexity language.
- Requires every numbered greenfield step to deliver observable product behavior instead of proactive service-layer or folder-structure extraction.
- Records the initial v0.7.0 A/B result, including the graders' position-biased disagreement.

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

[Download the v0.7.1 release asset](https://github.com/AaravKashyap12/advise-project-approach/releases/download/v0.7.1/advise-project-approach.skill)

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

- [A/B comparisons against generic prompting](./examples/ab-comparisons.md)
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

```text
## Project Approach: <name>
TL;DR / Project Frame / Comparable Projects / Recommended Stack /
Cost and Vendor Reality / Architecture Direction / Alternatives Considered / Build Plan /
Validation Plan / Risks and Unknowns / References
```

### Mid-Build or Post-Build

```text
## Project Approach Review: <name>
TL;DR / Project Summary / Evidence Reviewed, including evidence status /
What Is Working / Comparable Projects / Gap Analysis /
Recommended Changes, grouped High / Medium / Low /
Validation Plan / Stack and Architecture Verdict / Cost and Vendor Reality / Risks and References
```

## What It Will Not Do

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
|   `-- results/
|-- scripts/
|   |-- package_skill.py
|   `-- validate_skill.py
```

The packaged `.skill` file is a zip archive containing the `advise-project-approach/` skill folder.

## Development

Validate and rebuild the package:

```bash
python scripts/validate_skill.py
python scripts/package_skill.py
python scripts/validate_skill.py
```

The GitHub Actions workflow runs the same checks and fails if the generated package differs from what is committed.

## Evaluation

The skill is forward-tested across vague and detailed pre-build requests, vendor-cost decisions, mid-build repository reviews, large-repository sampling, and post-build launch reviews.

The first exploratory six-case run surfaced risks in intake enforcement, research completeness, repository permission boundaries, and stopping behavior. Later controlled A/B runs use the same prompt, model, isolation settings, and order-reversed blind graders. Rough and improved outputs are preserved rather than hidden.

[Methodology and rubric](./evals/README.md) | [Reusable cases](./evals/cases.json) | [Latest controlled A/B](./evals/results/2026-08-24-v0.7.1-ab-report.md) | [v0.7.0 inconclusive A/B](./evals/results/2026-08-24-v0.7.0-ab-report.md) | [Portability audit](./evals/portability.md) | [Initial failure run](./evals/results/2026-08-11-v0.4.0-forward-test.md)

The latest narrow-advice A/B is controlled and order-robust, but it covers one prompt and one model. No broad improvement percentage is claimed.

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
