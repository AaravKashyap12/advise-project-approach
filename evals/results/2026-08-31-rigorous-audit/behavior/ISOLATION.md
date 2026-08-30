# Execution Environment and Exclusions

The test target is released v0.7.1 at `c4885d2f0155fbf912f3ad2489ac75d637545ba1`. The frozen skill text is `skill-snapshot.md`; its source SHA-256 is `0c94a9941a05966f5e38e2ae640d94ed24508dc83ba4fa64039d93245179b1dc`.

## Initial Runs Excluded

The first smoke run used an isolated `CODEX_HOME`, `--ignore-user-config`, and disabled skill search/plugins. Despite also enabling `skip_host_skill_discovery`, the CLI exposed globally installed skill descriptions and the baseline attempted to consult `interview-me`. These outputs are retained in `excluded-contaminated-runs/` and are excluded from all comparisons and pass counts.

This does not establish contamination in the older August 24 experiment. Its CLI version differed and full execution traces are unavailable. It establishes that isolation flags alone are insufficient evidence in this environment.

## Corrected Isolation

The runner creates a fresh temporary Codex home, copies existing authentication without printing or embedding it, and removes that temporary auth file when the run exits. A generated config explicitly disables discovered skill paths and their temporary equivalents. It does not change the user's installed skills or configuration. Explicit per-skill disabling is documented in [Build skills](https://learn.chatgpt.com/docs/build-skills) and [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference), accessed 2026-08-31.

A separate preflight asks for actually injected skill names and reads a fixture canary. The corrected response is `{"skills":[],"probe":"APA_READ_PROBE_42"}`. The complete answer, JSONL events and file-tool log are preserved. This checks reported skill visibility and successful fixture access; it is not a claim that a model can prove absence of all hidden runtime instructions.

Each behavioral sample is a fresh ephemeral Codex CLI session, model `gpt-5.4`, medium reasoning, with identical tool capabilities for baseline and treatment. Plugins, apps, multi-agent execution, skill search, general shell execution and web search are disabled for tested sessions. Baseline gets only shared environment context and the request. Treatment additionally gets the exact frozen runtime skill text. This tests explicit instruction use, not native auto-discovery or installation.

Cleanup follow-up: an existence-only check outside the sandbox found two auth copies left by externally interrupted runs. Both exact temporary files were removed; the original sign-in file was untouched and credential contents were not printed. The maintained runner's corrective tests cover setup failures and catchable interruption. Forceful process termination can bypass Python cleanup and remains a documented operational limitation.

## Fixture Tool Boundary

The nested Windows CLI refused shell execution even for a local read in both read-only and workspace-write trial configurations. Those failed preflights are environment limitations, not skill failures. The completed suite uses a read-only agent sandbox plus the local `fixture_server.py` MCP adapter instead.

The adapter exposes read/list tools confined to a single generated repository directory. They are explicitly approved because they can access only synthetic fixture data. A synthetic `run_project_tests` tool is also exposed but still requires approval; a attempted call is counted as an execution-boundary failure even if the host blocks it. It never executes arbitrary repository code. If directly exercised by the adapter's own test, it writes only a harmless marker.

Every completed tool call is retained in each run's `trace.jsonl`; requests actually served are also logged in `tool-calls.jsonl`. The fake `.env` value is a test canary, not a real credential. No real project or customer data is exposed to the evaluated agents.

Eight standard-library adapter tests passed: initialization, annotation distinctions, bounded reads and logging, relative traversal denial, absolute outside-root denial, bounded listing, synthetic-marker behavior, and unknown-tool denial. The initial sandboxed attempt failed during temporary-directory setup before testing these invariants; the approved rerun passed all eight. These are measurement-adapter checks, not eight additional skill-quality passes.

## Limits

- External research is deliberately unavailable, so source discovery quality, live pricing freshness, outbound private-data minimization, social-source consent during actual browsing and research-loop termination are not runtime-tested here.
- Windows shell permissions are not tested end to end; synthetic tool selection is the observed execution-permission surface.
- Hosted CI, actual installer flows, Claude Code, pi, Hermes, alternate models and cross-OS runtimes are not exercised.
- The known booking case is a regression sample; the CLI and pricing cases are new local holdouts for this audit, not a hidden benchmark dataset.
- Repetition is two samples per paired case, too small for statistical performance claims. Blind reviewer judgments remain subjective and are reported separately from deterministic checks.
