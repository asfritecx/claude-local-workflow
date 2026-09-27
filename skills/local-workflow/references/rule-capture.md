# Capturing durable lessons as project rules

Review findings and mid-run gotchas are one-off events unless the docs layer records them. `.claude/rules/` is Claude's capture surface: small path-scoped markdown files the harness loads automatically when matching files are read, so the lesson resurfaces exactly where the mistake would repeat (shape below). If you run the Codex mirror, Codex reads the same rules from `docs/agent-rules/`, routed by `docs/agent-rules/INDEX.md`. Official rationale for "when to add" — https://code.claude.com/docs/en/memory.

Capture is discretionary: do it when the bar below is met, and report it in the finish.

## The bar — ALL must hold

- A confirmed defect or repeated gotcha reveals a non-obvious invariant. A finding judged rejected never becomes a rule.
- The lesson is stable and tied to identifiable paths or symbols — you can name real `paths:` globs. If it applies everywhere, it is a CLAUDE.md candidate, which stays the user's curated layer — flag it instead.
- Existing CLAUDE.md, skills, rules, and code comments do not already cover it — grep `.claude/rules/`, the relevant skills, and CLAUDE.md (its Gotchas section) first.
- Forgetting it would cause a concrete correctness, security, privacy, or operational failure.
- It changes a decision: a future agent reading it would act differently. Prose that restates what careful work already does is not a rule.
- It has recurred at least twice, or a single occurrence cost real damage (lost work, a security or data defect). One-off surprises go in the run's trail, not the rules.

Avoid rules for generic advice, personal style, one-off history, or facts easily derived from current code. How the user wants you to work belongs in auto-memory, never in committed rules. When in doubt, don't create it — a rule that fails the bar is context every future session pays for.

## Where the lesson belongs — dedupe ladder

Work down; stop at the first match:

0. **Structure beats prose.** Could the lesson be enforced by a test, a lint rule, a type, a hook or a script? If so, encode it there and don't write prose for it (or delete prose that it replaces). Example: the broad git restore/reset/checkout/stash ban is enforced in Claude Code by `.claude/hooks/git-guard.sh`, not only by the dispatch rule.
1. **An existing rule covers the topic** → update that rule (in both runtimes, if you run both), never create a near-duplicate.
2. **A project skill owns the subsystem** → put it in that skill via the staleness path (`references/skill-staleness-audit.md`). In a project with a dense skill layer, expect this rung to catch most lessons.
3. **The invariant belongs beside one implementation** → a code comment.
4. **Nothing owns it** → a new rule.

## House rule shape

One topic per file, descriptive kebab-case filename, YAML `paths:` frontmatter, `# Title`, tight bullets (aim well under ~30 lines), shaped like this:

```
---
paths:
  - "src/api/<domain>.ts"
  - "src/lib/<module>.ts"
---

# <Topic title>

- <The quirk: what breaks / what must hold.>
- <Why: the failure it causes when violated.>
- <How to comply: the correct pattern, with file refs.>

Captured: <YYYY-MM-DD> — from <review finding | mid-run quirk: one-line origin>.
```

- Derive the `paths:` globs from the files the finding or quirk actually touched.
- Rules without `paths:` load at launch for every session; reserve them for genuinely global constraints, and prefer flagging those for the user.
- The provenance footer lets a future staleness audit judge whether the origin still exists.

## Write both runtimes

If you run the Codex mirror, a newly captured rule is written to BOTH:

- `.claude/rules/<x>.md` — with `paths:` frontmatter and `.claude/` paths;
- `docs/agent-rules/<x>.md` — the same rule with Codex-side paths (`.agents/skills/…`, `AGENTS.md`), plus a row in `docs/agent-rules/INDEX.md` giving its path or situation routing.

Updates to an existing rule land in both copies too.

## Reflect pass at multi-phase closeout

At the close of a multi-phase run (`references/playbooks/multi-phase.md`), run one reflect pass before the finish report:

- **Who:** two read-only reviewers in one message, briefed with the run folder's `decisions.tsv`, the ledger (if any), and the disposition tables.
  - One is `code-digester` with a judgment lens: which decisions held, which were reversed, and what cost the most rework.
  - The other is `deep-analyst` (ideally on a different model family from the session; tier in `.claude/rules/agents-roster.md`) with a divergent lens: what the run's shape assumed that it didn't need to, and which lesson would change the next run's first decision.
  - The model difference is deliberate (see `references/review-gate.md`).
- **What they don't read:** transcript `.output` files. The trail and the tree are the evidence.
- **Output:** proposals sorted into **Accepted / Rejected / Backlog**. Each proposal is a rule edit, a skill edit, a mechanism (rung 0 above), or a `tune description` for a skill that should have triggered and didn't.
- **Approval:** the user approves before anything is edited.

## Mechanics & boundaries

- Readers and reviewers propose rule text with evidence. The main thread or an assigned writer checks for duplicates and applies it within scope.
- Root CLAUDE.md, auto-memory, and user-level `~/.claude/rules/` stay the user's curated layer: propose, never write.
- Captured rules are ordinary staleness-audit targets — including their `paths:` globs after renames.
- **Retirement:** revisit a rule when its anchored implementation changes, and remove it (from both runtimes and the index, if mirrored) when the invariant no longer exists.

## Keep in sync

Re-check this reference when the rule shape, the `docs/agent-rules/` mirror convention, or `references/skill-staleness-audit.md`'s scope changes.
