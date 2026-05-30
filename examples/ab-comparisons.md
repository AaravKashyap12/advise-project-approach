# A/B Comparisons

These examples show the difference between generic prompting and the behavior `advise-project-approach` is designed to enforce.

## Example 1: Pre-Build Stack Choice

Prompt:

```text
I want to build a self-hosted bookmark manager with tagging, full-text search, and a browser extension. Solo developer, comfortable with Python and basic React. What's the best way to approach this?
```

### Generic AI Answer

Likely recommendation:

- Next.js frontend
- Node or FastAPI API
- Postgres
- Docker Compose
- optional search service later

This may be reasonable, but it can overfit to modern full-stack defaults instead of the user's constraints.

### Skill-Guided Answer

The skill should first compare nearby real projects and ask what transfers:

- A lightweight self-hosted bookmark manager may not need a separate SPA and API.
- A Python-comfortable solo developer benefits from Django's built-in auth, admin, ORM, migrations, and deployment familiarity.
- SQLite FTS5 or Postgres full-text search may be enough before adding a dedicated search service.
- Heavier comparables are useful for feature contrast, not necessarily for stack copying.

Expected recommendation:

- Django
- server-rendered UI with HTMX, Turbo, or light JavaScript unless the UI requires SPA complexity
- SQLite FTS5 for personal/small scale, with Postgres as the upgrade path
- WebExtensions API for the browser extension
- single-container deployment first

The key difference: comparable research should reject the obvious trendy stack when the user's scale and skills point somewhere simpler.

## Example 2: Mid-Build Course Correction

Prompt:

```text
I'm halfway through building a task manager API in Node.js/Express. I've got routes and a MongoDB connection working but no auth, no tests, and I'm not sure if my folder structure will scale.
```

### Generic AI Answer

Likely recommendation:

- add auth
- add tests
- add Docker
- split routes/controllers/services
- add validation

This is useful but risks becoming a checklist that does not adapt to the repo.

### Skill-Guided Answer

If no repo is provided, the skill should clearly mark the advice as description-only. If a repo is provided, it should inspect actual evidence before recommending changes.

Expected behavior:

- If auth already exists, do not recommend "add auth."
- If tests already exist but miss integration coverage, recommend specific coverage gaps instead.
- If the app is small, avoid over-engineering the folder structure.
- If routes mix validation, persistence, and response shaping, recommend a small split tied to testability rather than taste.

The key difference: the skill should use comparable practice and local evidence to change or narrow the advice, not repeat generic Express API checklists.

## Example 3: Large Repo Review

Prompt:

```text
Review this monorepo and tell me if the architecture is healthy.
```

### Generic AI Answer

Risky behavior:

- tries to read too much
- summarizes shallow directory names
- gives broad advice without saying what was inspected

### Skill-Guided Answer

Expected behavior:

- map the repo first
- identify apps/packages/services
- ask for a target area if the request is too broad
- inspect manifests, docs, entry points, tests, and relevant slices
- state what was mapped, inspected, sampled, and skipped
- mark conclusions as high-confidence or provisional

The key difference: large-repo analysis should be bounded and transparent instead of pretending a full review happened.
