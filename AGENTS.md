# Repository Guidance

This repository packages one public skill: `advise-project-approach`.

## Source of Truth

- Edit the runtime skill at `skills/advise-project-approach/SKILL.md`.
- Do not edit `dist/advise-project-approach.skill` by hand. Rebuild it with `python scripts/package_skill.py`.
- Keep `.claude-plugin/plugin.json`, `skills/advise-project-approach/agents/openai.yaml`, `CHANGELOG.md`, and release notes in sync when changing their public metadata.

## Validation

Before committing changes, run:

```bash
python scripts/validate_skill.py
python scripts/package_skill.py
python scripts/validate_skill.py
```

The validator checks:

- skill folder and required files exist
- frontmatter has only `name` and `description`
- skill name matches folder name
- description is within the trigger metadata budget
- packaged `.skill` archive contains the expected root folder and files
- evaluation cases retain their required schema
- repository guidance remains available to generic agents and Claude Code

## Editing Rules

- Keep the packaged skill folder minimal: `SKILL.md` plus optional host metadata under `agents/`.
- Keep human documentation at the repository root or in `examples/` and `evals/`, not inside the skill folder.
- Do not add runtime scripts to the skill package unless the skill truly needs executable behavior.
- Preserve the read-only, evidence-first safety posture of the skill.
- Avoid stale claims in examples. Do not hard-code star counts, release dates, or "latest" claims unless the example states they must be verified at review time.

## Cross-Harness Compatibility

- `SKILL.md` is the portable runtime contract and must remain usable without optional metadata or adapters.
- Host-specific files are additive compatibility layers. Do not remove one harness's metadata merely to support another harness.
- Pi can discover the skill from `~/.agents/skills/` or `~/.pi/agent/skills/`.
- Claude Code can discover it from `~/.claude/skills/` and can use the optional plugin manifest.
- Codex can discover it from `~/.codex/skills/`; `agents/openai.yaml` supplies recommended UI metadata.
- Other Agent Skills-compatible harnesses can load the skill folder or point directly to `SKILL.md`.
