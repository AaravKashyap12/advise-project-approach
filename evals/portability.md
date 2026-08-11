# Portability Audit

Date: 2026-08-11

This is a structural compatibility audit, not a claim that the skill has been executed end to end in every harness.

| Harness | Discovery or packaging contract | Repository support | Evidence status |
| --- | --- | --- | --- |
| pi | Recursively discovers directories containing `SKILL.md` from `~/.agents/skills/`, `~/.pi/agent/skills/`, project paths, packages, settings, or `--skill` | Portable `SKILL.md`; no pi-only files required | Verified against pi documentation; runtime smoke test not yet recorded |
| Claude Code | Loads skills from its skill directory; `CLAUDE.md` can import `AGENTS.md` with `@AGENTS.md` | Skill folder, optional plugin manifest, packaged archive, and documented `CLAUDE.md` bridge | Import pattern verified against Claude Code documentation; runtime smoke test not yet recorded |
| Codex | Loads skills from its skill directory and supports recommended `agents/openai.yaml` UI metadata | Skill folder, `agents/openai.yaml`, and packaged archive | Validated by repository and official skill validators; fresh-install smoke test not yet recorded |
| Other Agent Skills-compatible harnesses | Load a directory containing a valid `SKILL.md` | Self-contained `SKILL.md` with only required frontmatter fields | Structurally portable; each harness still needs its own loader verification |

## Primary References

- [Pi skill locations and structure](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)
- [Agent Skills specification](https://agentskills.io/specification)
- [OpenAI Codex skill-creator guidance](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md)
- [Claude Code memory and AGENTS.md bridge](https://code.claude.com/docs/en/memory#agents-md)

## What This Audit Does Not Prove

- installation succeeds on every operating system
- every harness auto-triggers the skill on the same prompts
- optional host metadata is interpreted identically across versions
- a packaged archive is accepted by every UI

Record those claims only after a clean installation and invocation trace from the named harness.
