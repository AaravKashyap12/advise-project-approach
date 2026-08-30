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
- Adding dependencies or executable scripts inside the packaged skill unless there is a clear repeated task that needs deterministic execution.
- Adding README files inside `skills/advise-project-approach/`; keep repo docs outside the skill folder.

## Local Workflow

1. Install developer dependencies (not needed to use the skill):

```bash
python -m pip install -r requirements-dev.txt
```

2. Edit the source and add a regression test for a demonstrated failure.
3. Run the deterministic suites:

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s evals -p "test_*.py" -v
```

4. Rebuild and validate the package. Validation rejects stale archives after source edits:

```bash
python scripts/package_skill.py
python scripts/validate_skill.py
```

5. For runtime-instruction changes, follow the [behavioral evaluation workflow](./evals/README.md). Preserve failures, source hashes, prompts, and tool traces; a model preference score is not a correctness test.
6. Commit source, tests, documentation, and the rebuilt archive with a clear message.

## Pull Request Checklist

- [ ] The skill still validates.
- [ ] Both deterministic test suites pass and new tests detect the original defect.
- [ ] `dist/advise-project-approach.skill` was rebuilt if `SKILL.md` or `agents/openai.yaml` changed.
- [ ] Examples avoid stale time-sensitive claims.
- [ ] Changes preserve read-only behavior by default.
- [ ] New recommendations are tied to evidence, constraints, or real test cases.
- [ ] `CHANGELOG.md` is updated for user-visible changes.

## Release Checklist

1. Bump canonical `VERSION` for every public push, then synchronize:
   - `.claude-plugin/plugin.json`
   - the README's single current `What's New` section and release-asset link
   - `CHANGELOG.md`
2. Run regression tests, rebuild, and run the validation/package/validation sequence from `AGENTS.md`.
3. Commit the changes.
4. Tag the release:

```bash
git tag vX.Y.Z
git push origin main --tags
```

5. Attach `dist/advise-project-approach.skill` to the GitHub release.
6. Check hosted CI, the release tag's commit, and the uploaded artifact digest.
