# Capturing durable lessons as project rules

Review findings and mid-run gotchas are one-off events unless the docs layer records them. `.claude/rules/` is the capture surface: small path-scoped markdown files the harness loads automatically when matching files are read, so the lesson resurfaces exactly where the mistake would repeat. This guide covers loop step 8 (SKILL.md): deciding what deserves a rule, where the lesson actually belongs, and the shape a new rule takes. Sourced rationale — including the official mandate's "when to add" heuristics ("a code review catches something Claude should have known", "Claude makes the same mistake a second time") — lives in `docs/anthropic-memory-rules.md` in the kit repo.

## Triggers — two classes, two consent paths

- **Gate-derived** (from the step-6 review gate): a confirmed true-positive review or security finding whose lesson would have prevented the defect. Present the rule proposal AT the gate's existing STOP, alongside the findings — the user approves fixes and rules in one round-trip. A finding the user judges a false positive never becomes a rule.
- **Mid-run quirks**: durable gotchas hit during the run — build failures with non-obvious causes, API or library drift discovered the hard way, environment surprises. No natural stop exists, so these are created directly (via `bulk-editor`) once they pass the bar below, and reported in the synthesis so the user can prune.

## Where the lesson belongs — dedupe ladder

Work down; stop at the first match:

1. **An existing rule covers the topic** → update that rule (minimal old→new spec), never create a near-duplicate — two overlapping rules that drift apart is exactly the inconsistency the official docs warn about.
2. **A project skill owns the subsystem** → the lesson belongs in that skill; route it through the step-7 staleness path (`references/skill-staleness-audit.md`) as an edit spec instead of minting a rule.
3. **Nothing owns it** → new path-scoped rule.

## The rule-worthiness bar — ALL must hold

- **Durable** — outlives the change that surfaced it; not incident cleanup notes.
- **File-tied** — you can name real `paths:` globs it should trigger on. If it applies everywhere, it's a candidate for the user's CLAUDE.md, not a scoped rule — flag it instead.
- **Repeat-preventing** — a future session touching those files without this rule would plausibly make the same mistake.
- **Not already recorded** — grep `.claude/rules/`, the relevant skills, and CLAUDE.md first.
- **Not personal feedback** — how the user wants YOU to work goes to your personal memory layer, never into the project's committed rules.

When in doubt, don't create it — a rule that fails the bar is context bloat every future session pays for.

## House rule shape

One topic per file, descriptive kebab-case filename, small (aim well under ~30 lines):

```
---
paths:
  - "src/<dir>/**"
  - "src/<specific-file>.ts"
---

# <Topic title>

- <The quirk: what breaks / what must hold.>
- <Why: the failure it causes when violated.>
- <How to comply: the correct pattern, with file refs.>

Captured: <YYYY-MM-DD> — from <review finding | mid-run quirk: one-line origin>.
```

- Derive the `paths:` globs from the files the finding or quirk actually touched — the rule loads when those files are read.
- Rules without `paths:` load at launch for every session; reserve unscoped rules for genuinely global constraints, and prefer flagging those for the user's own curation.
- The provenance footer is one line; it lets a future step-7 audit judge whether the origin still exists.

## Mechanics & boundaries

- The orchestrator drafts the rule markdown in the main thread and `bulk-editor` applies it (new-file content LAST in the op spec) — same as any other authored doc.
- Root CLAUDE.md, auto-memory, and user-level `~/.claude/rules/` stay the user's curated layer: propose, never write.
- Rules created here are ordinary step-7 audit targets in future runs — the staleness audit keeps them honest, including their `paths:` globs after renames.

## Keep in sync

This reference pairs with loop step 8 in `SKILL.md` and with the review gate's STOP (step 6), where gate-derived proposals ride along. Re-check it when the loop's step numbering, the gate's result handling, or `references/skill-staleness-audit.md`'s scope changes. Sourced memory/rules rationale: `docs/anthropic-memory-rules.md` in the kit repo.
