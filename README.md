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
    <a href="#install">Install</a> |
    <a href="./skills/advise-project-approach/SKILL.md">Skill source</a> |
    <a href="#whats-new-in-v060">What's new in v0.6</a> |
    <a href="#demo">Examples</a> |
    <a href="#evaluation">Tests &amp; evidence</a> |
    <a href="./CHANGELOG.md">Changelog</a> |
    <a href="./CONTRIBUTING.md">Contributing</a>
  </strong>
</p>

`advise-project-approach` is an agent skill for project planning, course correction, and review. It works with pi, Claude, Codex, and any agent harness that loads Markdown-based skill instructions.

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

## Install

### pi

```bash
# Copy skill to your pi skills directory
cp -r skills/advise-project-approach ~/.agents/skills/
# Or symlink it
ln -s $(pwd)/skills/advise-project-approach ~/.pi/agent/skills/advise-project-approach
```

### Claude / Codex

```bash
# Manual copy to Claude skills directory
cp -r skills/advise-project-approach ~/.claude/skills/
```

### Any Agent

Copy the contents of [skills/advise-project-approach/SKILL.md](./skills/advise-project-approach/SKILL.md) into your agent's skill loading mechanism. The workflow is self-contained in that single file.

## Source of Truth

The runtime skill spec lives in [skills/advise-project-approach/SKILL.md](./skills/advise-project-approach/SKILL.md). That file is the source of truth for the workflow agents actually run.

Everything else in this repo exists to explain, test, or document that skill.

## What's New in v0.6.0

v0.6 removes agent-specific lock-in and makes the skill portable across all major agent harnesses.

- Removed Claude-specific files: `.claude-plugin/plugin.json`, `agents/openai.yaml`, and `dist/*.skill` archive.
- Renamed `CLAUDE.md` to `AGENTS.md` with multi-agent guidance.
- Removed Agent-Reach adapter references (non-portable external dependency).
- Removed "Community Research Permission" section that added unnecessary friction.
- Consolidated redundant Decision Methodology and Workflow sections.
- Streamlined External Research Rules into a single focused section.
- Updated README with agent-agnostic install instructions.

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
Risks and Unknowns / References
```

### Mid-Build or Post-Build

```text
## Project Approach Review: <name>
TL;DR / Project Summary / Evidence Reviewed, including evidence status /
What Is Working / Comparable Projects / Gap Analysis /
Recommended Changes, grouped High / Medium / Low /
Stack and Architecture Verdict / Cost and Vendor Reality / Risks and References
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
|-- assets/
|   `-- brand/
|       |-- lockup-dark.svg
|       `-- lockup-light.svg
|-- .github/
|   `-- workflows/
|       `-- validate.yml
|-- skills/
|   `-- advise-project-approach/
|       `-- SKILL.md
|-- examples/
|   |-- ab-comparisons.md
|   |-- pricing-operating-cost.md
|   |-- prebuild-bookmark-manager.md
|   |-- midbuild-express-api.md
|   `-- postbuild-fastapi-template.md
|-- evals/
|   |-- README.md
|   |-- cases.json
|   `-- results/
|-- scripts/
|   `-- validate_skill.py
```

## Development

Validate the skill:

```bash
python scripts/validate_skill.py
```

The GitHub Actions workflow runs the same checks on push and PR.

## Evaluation

The skill is forward-tested across vague and detailed pre-build requests, vendor-cost decisions, mid-build repository reviews, large-repository sampling, and post-build launch reviews.

The first exploratory six-case run surfaced risks in intake enforcement, research completeness, repository permission boundaries, and stopping behavior. A stricter rerun explicitly invoked the skill by name and path. Both records are preserved rather than hiding the rough first pass.

[Methodology and rubric](./evals/README.md) | [Reusable cases](./evals/cases.json) | [Initial failure run](./evals/results/2026-08-11-v0.4.0-forward-test.md) | [v0.5.0 focused rerun](./evals/results/2026-08-11-v0.5.0-rerun.md)

These are exploratory forward tests, not yet a controlled same-model baseline benchmark. No improvement percentage is claimed.

## Contributing

Issues and PRs are welcome. The most useful contributions are:

- New repo test cases: a repo, what the skill got wrong, and what it should have said.
- Evidence discipline failures: cases where a claim was made without a verifiable source.
- Mode selection bugs: cases where the skill picked the wrong operating mode.

## License

MIT

---

### Portfolio

See more of the original author's work at [https://www.aaravkashyap.live/](https://www.aaravkashyap.live/).
