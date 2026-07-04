# Dispatching the post-change docs-staleness audit

Code changes rot documentation silently. After a run changes behavior, adds a feature, or alters a pattern the docs layer records, the skills and rules describing that subsystem — and any domain-expert agent memory built on them — still describe the OLD world. The next orchestration run briefs its agents on those docs as ground truth, so stale guidance compounds into wrong work. This audit closes the loop (SKILL.md loop step 7): one read-only agent compares what landed against what the docs claim and returns minimal edit specs.

## When to run

- Any run that changed behavior, added a feature, or altered a documented pattern — including renamed or removed exports, changed defaults, new invariants, and retired flows.
- Skip only with evidence that the changed paths and key symbols match nothing in `.claude/skills/**` or `.claude/rules/**`, and that relevant `.claude/agent-memory/<prj>-*/` dirs for touched domain(s) do not exist or contain no memory files. Memory dirs are not grep-gated: if relevant memory files exist, include them in the audit scope even when their text has no grep hit.
- Run it in the SAME run that landed the change, after verification and the review gate, while the diff is still in hand.
- In phased runs (`references/phased-execution.md`), the audit runs ONCE at the end of the run over the accumulated diff, not per phase.

## Who runs it

Start with one read-only documentation auditor, in this order of preference:

1. The touched subsystem's `<prj>-<domain>-expert` if exactly one domain owns the change and a matching expert exists — it knows the domain's invariants and refreshes its own memory notes in the same pass.
2. `skill-auditor` — the dedicated post-change auditor for cross-domain changes, undomained changes, or single-domain changes without a matching `<prj>-*` expert; its definition carries the full deliverables contract, so the brief stays short. It is read-only and emits flag-only findings for affected domain memories.
3. `code-digester` — fallback where `skill-auditor` isn't installed; you must paste the deliverables contract into the brief yourself (copy `agents/skill-auditor.md` §Output).

Never the agent that wrote the change: a writer grading its own documentation impact repeats the generator-grades-itself failure.

If a cross-domain audit finds stale `.claude/agent-memory/<prj>-*/` notes, dispatch the owning `<prj>-*` experts as follow-up read-only repo audits so each expert refreshes only its own memory. The one-auditor rule covers the docs verdict pass, not multi-domain memory refresh.

## Audit scope — skills AND rules

- **Project skills** (`.claude/skills/<skill>/SKILL.md`) — the Skill-map rows overlapping the touched files.
- **Project rules** (`.claude/rules/**/*.md`) — discovered recursively by the harness. A rule with `paths:` frontmatter loads only when files matching its globs are read; an unscoped rule loads at launch with the same priority as `.claude/CLAUDE.md`. Include every rule whose `paths:` globs match the changed files, plus any unscoped rule whose topic overlaps. The official memory docs mandate this hygiene — review rules "periodically to remove outdated or conflicting instructions" (sourced snapshot: `docs/anthropic-memory-rules.md` in the kit repo).
- **Domain memory** (`.claude/agent-memory/<prj>-*/`) — always expand memory dirs for touched domain experts when they exist, even when skill/rule grep has no hits and even when memory text does not match changed symbols. Memory is a hint, but stale hints still bias future expert reads.
- **Flag-only** — root CLAUDE.md, auto-memory, and user-level `~/.claude/rules/` are the user's curated layer: the audit quotes stale claims and states what changed, but never specs direct edits to them. Domain memory under `.claude/agent-memory/<prj>-*/` is also flag-only for `skill-auditor`; owning `<prj>-*` experts update their own notes in follow-up passes.

## Brief skeleton

```
You are auditing documentation staleness after a code change. Read-only against code and docs — do NOT modify repo files. If this brief is sent to the owning `<prj>-*` expert, the only permitted write is that expert's own `.claude/agent-memory/<name>/` notes.

CHANGE SUMMARY: <3–6 lines from the orchestrator's own synthesis: what landed, why, the files
touched, and any renamed/removed/added exports, defaults, or invariants>

AUDIT SCOPE — check each of these against the changed code:
- .claude/skills/<skill-a>/SKILL.md        <- the Skill-map rows overlapping the touched files
- .claude/skills/<skill-b>/SKILL.md
- .claude/rules/<rule>.md                  <- rules whose paths: globs match the touched files
- <domain-expert agent-memory paths, if the project uses them>
```

When a memory directory appears in the scope, the auditor expands it before
reading: `MEMORY.md` plus note files under that directory. If no memory files
exist, the auditor records that fact instead of trying to read the directory
itself.

`skill-auditor` carries the DELIVERABLES contract in its own definition (per-doc FRESH/STALE verdicts with both-sides evidence, exact old→new specs, trigger checks on skill `description`s and rule `paths:` globs, flags, gaps) — do not restate it. When falling back to `code-digester`, copy that contract from `agents/skill-auditor.md` §Output into the brief so the report shape stays identical.

When dispatching an owning `<prj>-<domain>-expert`, use the same per-doc FRESH/STALE contract for project skills and rules, but do not copy `skill-auditor`'s domain-memory flag-only clause. The owning expert may update only its own `.claude/agent-memory/<name>/` notes and must report either the refreshed memory files or `no memory changes needed`.

## Handling the report

- **Apply specs via `bulk-editor`,** like any fully-specified mechanical spec, then re-read the changed regions yourself — the audit report is a claim, not proof.
- **Relay flag-only findings** (root CLAUDE.md, auto-memory, user-level rules) to the user; never auto-edit the curated layer. For domain memory findings, dispatch the owning `<prj>-*` expert to refresh its own notes.
- **Patch, don't rewrite.** The audit emits minimal old→new specs for claims the change falsified. If it flags that a doc needs a wholesale rewrite, treat that as a separate, deliberate task.
- **A domain expert may refresh its OWN memory notes** during the audit (its sanctioned write surface) and must report refreshed files or `no memory changes needed`; every other file stays read-only — specs come back to the orchestrator.

## Keep in sync

This reference pairs with the audit step in `SKILL.md`'s loop (step 7) and with `agents/skill-auditor.md` (which owns the deliverables contract). Re-check it when the Skill-map shape, the domain-expert pattern, that step's wording, or the auditor's Output contract changes. Sourced memory/rules rationale: `docs/anthropic-memory-rules.md`.
