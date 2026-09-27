---
paths:
  - ".codex/agents/*.toml"
  - ".agents/skills/local-workflow/**"
---

# Agent roster changes must update routing guidance

Project-scoped Codex agents live in `.codex/agents/*.toml`. Each file owns its role description, model, reasoning effort, sandbox boundary, and developer instructions.

## Roster and boundaries

- **Read-only** (`sandbox_mode = "read-only"`): `code-digester`, `deep-analyst`, `code-reviewer`, `adversarial-reviewer`, `skill-auditor`, `localworkflow-sync`, and your `<prj>-<domain>-expert` agents (install your own from `.agents/skills/local-workflow/references/domain-expert-template.md`).
- **Web tier**: `research-specialist` is the only role that does web research. It is cache-first at `docs/agent-knowledge/research/` and propose-only; it writes no repository files.
- **Writers** (`workspace-write`): `code-developer` and `bulk-editor`, plus your specialist writers, if any. `bulk-editor` makes no API decisions and stops on any spec mismatch; authoring writers stop with `NEEDS_CONTEXT` on a research gap.
- **Knowledge**: no per-agent memory. Durable knowledge lives in `docs/agent-knowledge/`. Readers and specialists propose updates; only the main thread or a writer with explicit ownership applies them.

## Same-pass updates

When an agent's remit, name, model, effort, or read/write boundary changes, inspect these surfaces in the same pass:

- `.agents/skills/local-workflow/SKILL.md` and its relevant references;
- other agent definitions that route work to or away from the changed role;
- `docs/agent-rules/INDEX.md` and `docs/agent-knowledge/INDEX.md` for stale routing or ownership;
- `.agents/skills/local-workflow/references/review-gate.md` when `code-reviewer` or `adversarial-reviewer` changes.

Read-only roles share one behavior contract with their Claude counterparts. The contract covers:
- evidence labels (`ran`, `read`, `inferred`, `unknown`);
- the brief's TIMEBOX, with partial returns listing NOT COVERED;
- `PASS`, `ISSUES` or `BLOCKED` for verifier tasks;
- no routine delegation, and no web research outside `research-specialist`.

Keep that contract in step when either side changes. The Claude side carries it in `.claude/skills/house-agent-contract/SKILL.md`.

Validate every TOML, require the filename to match `name`, and check that referenced skills and indexed knowledge paths exist. Readers and reviewers use `sandbox_mode = "read-only"`; implementation roles use `workspace-write` only when their remit requires edits. Skill instructions are not preloaded into a custom agent: prompts and agent definitions must tell the agent which `.agents/skills/<skill>/SKILL.md` files to read.

Use `collaboration.spawn_agent` with a registered `agent_type`. Use `send_message`, `followup_task`, and `wait_agent` only when needed. Avoid overlapping write ownership and routine delegation.

The Claude-side roster tiers and tool declarations (`.claude/rules/agents-roster.md`) are not Codex configuration and must not be copied into this layer. Model and effort differences between the runtimes are intentional, never drift.
