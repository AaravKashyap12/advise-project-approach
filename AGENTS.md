# Repository Guidance

This repository packages one public skill: `advise-project-approach`.

## Source of Truth

- Edit the skill source at `skills/advise-project-approach/SKILL.md`.
- Keep `CHANGELOG.md` and release notes in sync when changing the public version.

## Validation

Before committing changes, run:

```bash
python scripts/validate_skill.py
```

The validator checks:

- skill folder and required files exist
- frontmatter has only `name` and `description`
- skill name matches folder name
- description is within the trigger metadata budget

## Editing Rules

- Keep the skill folder minimal: only `SKILL.md`.
- Keep human documentation at the repository root or in `examples/`, not inside the skill folder.
- Do not add runtime scripts to the skill package unless the skill truly needs executable behavior.
- Preserve the read-only, evidence-first safety posture of the skill.
- Avoid stale claims in examples. Do not hard-code star counts, release dates, or "latest" claims unless the example states they must be verified at review time.

## Multi-Agent Compatibility

This skill is designed to be portable across agent harnesses:

- **pi** — install via `~/.agents/skills/advise-project-approach/SKILL.md`
- **Claude** — install via manual copy or plugin-aware installer
- **Codex** — install via manual copy or `.skill` archive
- **Other agents** — copy `SKILL.md` instructions and adapt trigger/loading mechanism

The workflow is intentionally self-contained in `SKILL.md`. No agent-specific metadata, adapters, or runtime dependencies are required.
