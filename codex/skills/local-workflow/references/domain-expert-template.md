# Domain expert pattern

Use a domain expert for a stable project subsystem with enough non-obvious invariants to justify a dedicated reader. Domain experts investigate and digest; they do not implement application changes. Create one only after stable code and canonical guidance exist, and keep the `<prj>` prefix consistent across the roster.

## Definition shape

Create `.codex/agents/<prj>-<domain>-expert.toml` with:

- a description containing concrete domain triggers;
- `model = "gpt-6-luna"` and `model_reasoning_effort = "max"`;
- `sandbox_mode = "read-only"` as the configured default, plus an instruction not to edit; use a separate writer for an explicitly assigned docs-only note update, and verify the effective child sandbox when enforcement matters;
- instructions to read `AGENTS.md`, the named `.agents/skills/<domain>/SKILL.md`, and routed rule or knowledge notes before analysis;
- a structured output contract requiring file:line evidence, verbatim snippets where useful, invariants, risks, and gaps.

Skeleton:

```toml
name = "<prj>-<domain>-expert"
description = "Read-only <domain> specialist. Use for <5-8 concrete topics>. Prefer over code-digester when the thread is about how <domain> works in this project. Not a writer or external-research agent."
model = "gpt-6-luna"
model_reasoning_effort = "max"
sandbox_mode = "read-only"
developer_instructions = """
Act as the <domain> specialist for this repository.

Match each in-scope repository path against `docs/agent-rules/INDEX.md` and read every matching rule explicitly.

Read AGENTS.md, `.agents/skills/<domain-skill>/SKILL.md`, and every skill named in the dispatch. Read only the code paths needed for the question. Consult `docs/agent-knowledge/INDEX.md` and linked domain notes only as leads; reverify load-bearing claims in code.

Check each conclusion against the domain invariants:
- <6-12 verified rules covering abstractions, data integrity, security, validation, ownership, and domain semantics>

Return the requested deliverables with relative file:line evidence, separating confirmed facts, inference, invariant impact, and gaps. For a repository change, return a writer-ready brief or an exact mechanical spec. Do not modify files, write notes, or routinely delegate. Propose durable knowledge updates to the parent.

Label each load-bearing claim `ran`, `read`, `inferred`, or `unknown`, and give a count claim the command that regenerates it. Respect the brief's TIMEBOX: past it, return partial results and list what remains under NOT COVERED. For a verifier task (check, smoke test, audit), state PASS, ISSUES, or BLOCKED with evidence; a check that could not run is BLOCKED, never PASS.
"""
```

Wire the new agent into the Project routing table in `SKILL.md` and the roster table in `subagent-best-practices.md`, then smoke-test it in a fresh session.

## Dispatch boundary

Give the expert one subsystem question. Include the exact code paths and project skill. Ask it to distinguish facts from inference and to report stale documentation separately. The agent may propose an edit specification or curated knowledge note; a writer or main thread applies it.

Use `localworkflow-sync` after changes to `.codex/agents/*.toml`, `.agents/skills/local-workflow/**`, `docs/agent-knowledge/**`, or `docs/agent-rules/**`. It checks that roster names, model policy, paths, and workflow claims remain aligned.

Do not duplicate application facts in the agent definition when the domain skill already owns them. The definition should specify behavior and output; the skill should carry maintained domain knowledge.
