# Dispatching `code-developer`

Use `code-developer` for implementation or documentation work that requires judgment. Use one of your specialist writers, if any, when the task falls squarely inside its remit (for example schema and migrations, UI styling, or deployment infrastructure). Use `bulk-editor` only when every edit is already specified exactly.

## Brief template

This is the writer form of the nine-field contract in `references/brief-contract.md`: Objective is GOAL, Ownership is SCOPE, Read first and Requirements are CONTEXT, Validation is VERIFY, the hygiene lines are FORBIDDEN, and Return is REPORT. ACCEPTANCE, TIMEBOX and STANDING are required here too.

```text
Objective: <observable outcome>

Ownership:
- You own: <exact files or modules>
- Do not edit: <adjacent or independently owned surfaces>
- Other agents share this tree. Preserve unrelated edits and adapt to concurrent changes.
- Never use git restore, git reset, git checkout --, git stash (any form) or git clean -f.
- Write no per-agent memory files. Locate edits by verbatim text, not line numbers.

Read first:
- AGENTS.md
- .agents/skills/<relevant-skill>/SKILL.md
- <specific entries routed by docs/agent-rules/INDEX.md>
- <specific code or tests>

Requirements:
- <behavior and invariants>
- <accepted design decisions>
- <error and edge-case expectations>

External APIs:
- <research-specialist note or official source already verified>

Acceptance:
- <testable criteria that define done>

Validation:
- <targeted tests>
- <your typecheck>
- <your lint>
- <your unit tests>

Timebox: <coverage budget>. If it runs out before Acceptance is met, stop at a safe boundary and return STOPPED with what landed and the remaining work.

Standing orders: <the run's standing orders, verbatim, or "none">

Return:
- status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | STOPPED
- changed files and regions
- checks with complete diagnostics
- open questions or residual risks
```

If strict red-green work is required, give the failing-test command and expected reason for failure. The writer should record both the red and green results.

## Dispatch and follow-up

Call `collaboration.spawn_agent` with `agent_type: "code-developer"`, `fork_turns: "none"`, a unique task name, and the complete self-contained brief. Use a deliberately bounded positive `fork_turns` value only when recent context is required. A full-history fork can inherit the parent model and reasoning effort instead of the custom profile. Avoid sending conclusions that the writer should independently derive, but include decisions already made by the user or orchestrator. Inspect the spawned task's effective model, reasoning effort, and sandbox when runtime metadata exposes them. Otherwise record the configured profile and dispatch overrides separately and mark the effective profile unavailable.

Use `collaboration.send_message` for newly discovered context while the task is running. Use `collaboration.followup_task` for a bounded next step after the agent is idle. Prefer a fresh task when ownership or the core objective changes.

Inspect the actual diff after completion. The writer's checks are self-checks; the main thread remains responsible for integration, independent review, and the final claim.
