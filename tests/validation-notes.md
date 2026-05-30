# Validation Notes

These notes record the manual forward tests used before the first public package layout.

## Structural Validation

- Validated `skills/advise-project-approach` with the local `skill-creator` validator.
- Rebuilt `dist/advise-project-approach.skill` from the skill source folder.
- Verified the `.skill` archive contains the expected root folder layout:

```text
advise-project-approach/SKILL.md
advise-project-approach/agents/openai.yaml
```

## Behavioral Test Cases

### Pre-Build: Self-Hosted Bookmark Manager

Prompt: a solo Python developer wants tagging, full-text search, and a browser extension.

What it exposed:

- The skill should recommend from constraints, not trends.
- Comparable project details must be verified at review time.
- The answer should include when the recommended stack becomes wrong.

### Mid-Build: Node/Express API

Prompt: halfway through an Express API with routes and MongoDB connection, but no auth/tests.

What it exposed:

- With no repo, the answer must be marked as advisory from description.
- The skill should not claim file-level findings without files.
- Folder advice should be tied to testability and maintainability, not taste.

### Repo Review: linkding

Repo: https://github.com/sissbruecker/linkding

What it exposed:

- Mature project stacks evolve.
- Do not flatten a current project into an older, simpler stack summary.
- Freshness rules are necessary for last commit, release, star, and maintenance claims.

### Repo Review: Node Express RealWorld Example

Repo: https://github.com/gothinkster/node-express-realworld-example-app

What it exposed:

- The skill must inspect actual files before recommending "add auth" or "add tests."
- Recommendations should adapt when auth, tests, error handling, and structure already exist.

### Repo Review: Full Stack FastAPI Template

Repo: https://github.com/fastapi/full-stack-fastapi-template

What it exposed:

- A good template is not automatically the right fit.
- The review should compare template completeness against user scale, operational appetite, and product needs.

## Remaining Risks

- Automatic invocation still depends heavily on the `description` field.
- Star counts, release dates, package downloads, and "active" claims must always be rechecked live.
- The skill is intentionally advisory and read-only; users may still expect it to implement changes unless the agent explains the boundary.

## v0.2 Feedback Cases

Launch feedback added these validation expectations:

- Comparable projects must not become a popularity vote. The output should name what transfers and what should not be copied.
- The recommendation should expose its decision framework, not only a confident answer.
- Large repo reviews should map first, inspect targeted slices, and disclose skipped areas.
- A/B examples should show where comparable research changes, narrows, or confirms the recommendation compared with generic prompting.
