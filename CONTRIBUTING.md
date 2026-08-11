# Contributing

Thanks for helping improve `advise-project-approach`.

This repo is intentionally small. The best contributions make the skill more accurate, easier to install, or better tested against real project-review scenarios.

## Useful Contributions

- **New test cases:** a repo, prompt, what the skill got wrong, and what it should have said.
- **Evidence discipline fixes:** places where the skill could invent or overstate claims without verification.
- **Mode selection fixes:** prompts where it chooses pre-build, mid-build, or post-build incorrectly.
- **Documentation fixes:** install instructions, examples, or release notes that are unclear.
- **Trigger improvements:** frontmatter wording that catches real user requests without over-triggering.

## What To Avoid

- Broad rewrites that make the skill longer without improving behavior.
- Hard-coded star counts, release dates, or "latest" claims in examples.
- Adding dependencies or executable scripts inside the skill folder unless there is a clear repeated task that needs deterministic execution.
- Adding README files inside `skills/advise-project-approach/`; keep repo docs outside the skill folder.
- Adding agent-specific metadata files (`.claude-plugin/`, `agents/openai.yaml`, etc.) — the skill is designed to be portable.

## Local Workflow

1. Edit the skill source at `skills/advise-project-approach/SKILL.md`.
2. Validate the source:

```bash
python scripts/validate_skill.py
```

3. Commit with a clear message.

## Pull Request Checklist

- [ ] The skill still validates.
- [ ] Examples avoid stale time-sensitive claims.
- [ ] Changes preserve read-only behavior by default.
- [ ] New recommendations are tied to evidence, constraints, or real test cases.
- [ ] `CHANGELOG.md` is updated for user-visible changes.

## Release Checklist

1. Update version references in `CHANGELOG.md`.
2. Run validation.
3. Commit the changes.
4. Tag the release:

```bash
git tag vX.Y.Z
git push origin main --tags
```
