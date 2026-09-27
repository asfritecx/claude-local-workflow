# Dispatching the post-change docs-staleness audit

Code changes rot documentation silently. After a run changes behavior, adds a feature, or alters a pattern the docs layer records, the skills, rules, and knowledge notes describing that subsystem still describe the OLD world. The next run briefs its agents on those docs, so stale guidance compounds into wrong work. This audit closes the loop: one read-only agent compares what landed against what the docs claim and returns minimal edit specs.

## When to run

- Any run that changed behavior, added a feature, or altered a documented pattern — including renamed or removed exports, changed defaults, new invariants, and retired flows.
- Skip when the changed paths and key symbols match nothing in `.claude/skills/**`, `.claude/rules/**`, or the relevant `docs/agent-knowledge/domain/*.md` note(s); say so in the finish.
- Run it in the same run that landed the change, after verification and the review gate, while the diff is in hand. In phased runs, run it once at the end over the accumulated change.

## Who runs it

One read-only auditor, in this order of preference:

1. The touched subsystem's `<prj>-<domain>-expert` if exactly one domain owns the change and a matching expert exists (e.g. `shop-billing-expert` for a billing change).
2. `skill-auditor` — for cross-domain changes, undomained changes, or a single domain without a matching expert. Its definition carries the full deliverables contract, so the brief stays short.
3. `code-digester` — fallback only; paste the deliverables contract from `.claude/agents/skill-auditor.md` §Output into the brief.

Never the agent that wrote the change: a writer grading its own documentation impact repeats the generator-grades-itself failure.

**Boundary with `localworkflow-sync`:** roster and agent-definition drift across the `.claude/` workflow layer is its job; this audit owns CONTENT staleness — claims falsified by code changes.

## Audit scope

- **Project skills** (`.claude/skills/<skill>/SKILL.md` and references) — the Skill-map rows overlapping the touched files. Check each skill's frontmatter `description` as well as its body: a technically correct skill is still stale if its trigger text no longer routes the right work.
- **Project rules** (`.claude/rules/**/*.md`) — a rule carrying `paths:` frontmatter auto-loads when matching files are read; an unscoped one loads at launch alongside the root `CLAUDE.md`. Derive the current list when needed (`grep -l '^paths:' .claude/rules/*.md`) and include every rule whose globs match the changed files, plus any unscoped rule whose topic overlaps. Stale rule findings apply to the `docs/agent-rules/` copy too, if you run the Codex mirror.
- **Domain knowledge** — the relevant `docs/agent-knowledge/domain/*.md` note(s) for the touched domain, routed by `docs/agent-knowledge/INDEX.md`. The auditor flags stale claims; the main thread or a writer applies the fixes.
- **Flag-only** — root CLAUDE.md, auto-memory, and user-level `~/.claude/rules/` are the user's curated layer: quote the stale claim and what changed, never spec a direct edit.
- **Archival records** — keep clearly labeled archival records (e.g. a retired benchmark skill) intact; audit only active instructions.

## Brief skeleton

```
You are auditing documentation staleness after a code change. Read-only — do NOT modify files.

CHANGE SUMMARY: <3–6 lines from the main thread's own synthesis: what landed, why, the files
touched, and any renamed/removed/added exports, defaults, or invariants>

AUDIT SCOPE — check each of these against the changed code:
- .claude/skills/<skill-a>/SKILL.md             <- Skill-map rows overlapping the touched files
- .claude/skills/<skill-b>/SKILL.md
- .claude/rules/<rule>.md                       <- rules whose paths: globs match the touched files
- docs/agent-knowledge/domain/<domain>.md       <- domain note(s) for the touched domain
<replace the examples above with the actual overlapping skills, matching rules, and domain notes>
```

`skill-auditor` carries the DELIVERABLES contract in its own definition (per-doc FRESH/STALE verdicts with both-sides evidence, exact old→new specs, trigger checks on skill `description`s and rule `paths:` globs, flags, gaps) — do not restate it. When dispatching an owning `<prj>-<domain>-expert` or the `code-digester` fallback, use the same per-doc FRESH/STALE contract.

## Handling the report

- **Apply specs** via `bulk-editor` or directly from the main thread, then re-read the changed regions — the audit report is a claim, not proof.
- **Relay flag-only findings** (root CLAUDE.md, auto-memory, user-level rules) to the user; never auto-edit the curated layer.
- **Patch, don't rewrite.** The audit emits minimal old→new specs. A doc that needs a wholesale rewrite is a separate, deliberate task.

## Keep in sync

This reference pairs with `SKILL.md` §Implement, review, keep guidance current and `.claude/agents/skill-auditor.md` (which owns the deliverables contract). Re-check it when the Skill-map shape, the domain-expert pattern, the `docs/agent-knowledge/` domain routing, or the auditor's Output contract changes.
