# Dispatching `code-developer` — the brief template

`code-developer` has **total context isolation**: it never sees this conversation, the reports your readers returned, or the decisions you already made — only the prompt you hand it (plus its preloaded skills). It also cannot ask you anything mid-run (subagents have no `AskUserQuestion`). So the brief IS the spec: every decision the work needs must be written down, or the agent guesses.

Load this when you're about to dispatch `code-developer`. The routing decision (is this even a `code-developer` job?) stays in `SKILL.md`. The skeleton below is the writer form of `references/brief-contract.md`: CONTEXT and DIGESTED FINDINGS fill GOAL and CONTEXT, TARGET FILES and SCOPE fill SCOPE, VALIDATION fills VERIFY, HYGIENE fills FORBIDDEN, and RETURN fills REPORT. ACCEPTANCE, TIMEBOX and STANDING are required fields here too.

## The writer test (confirm before you fill anything in)

Does *applying* the change require any decision — design, wording, API choice, where the logic goes? **Yes → `code-developer`.** **No → `bulk-editor`** with a verbatim old→new spec. If you find yourself writing exact replacement strings into the brief below, you've specified it fully: send it to `bulk-editor`, which has no decisions to make. Use one of your specialist writers instead, if any, when the work is primarily in its surface (for example schema/migrations, AI features, UI styling, or deployment infrastructure).

## The skeleton

```
You are implementing a change for an orchestrator that will verify your diff.

CONTEXT: <1–3 sentences — what to build and WHY. The agent has none of the
backstory; this is all it knows about intent.>

DIGESTED FINDINGS (from prior reads — treat as ground truth, do NOT re-digest):
- <fact + src/path.ts:line>
- <the pattern to follow + where it already lives, src/path.ts:line>
- <any constraint a reader surfaced>

RESEARCH POINTERS: <the docs/agent-knowledge/research/<topic>.md note(s) or
research-specialist digest covering each external library the change touches,
checked against the pinned version — or the line "no external APIs touched".>

ADVISORY NOTES (optional): <docs/agent-knowledge/engineering/<note>.md entries
that bear on this change — leads to re-verify in code, not ground truth.>

TARGET FILES (you own only these; absolute paths):
- <absolute path to create/modify>

SKILLS (read these SKILL.md files for house conventions):
- .claude/skills/<skill>/SKILL.md

SCOPE: <what to change — and explicitly what NOT to touch. "Only X; leave Y alone.">

CONSTRAINTS / KNOWN APIS (optional): <versions already pinned, house cross-cuts
that apply, an API a reader already verified so it needn't look it up again.>

ACCEPTANCE: <the testable statement(s) that define done.>

HYGIENE:
- Other agents and the user may have live edits in this tree. Preserve unrelated
  edits; never use git restore / reset / checkout -- / stash (any form) / clean -f.
- Write no per-agent memory files.
- Locate edits by verbatim text, not line numbers, in files you edit.

VALIDATION (proportionate): <targeted tests>, <your typecheck>,
<your lint>, <your unit tests>

TIMEBOX: <coverage budget>. If you hit it before ACCEPTANCE is met, stop at a safe
boundary and return STOPPED with what landed and a REMAINING list of what did not.

STANDING: <the run's standing orders, verbatim, or "none">

RETURN: changed files and regions; checks with complete diagnostics, each with
its evidence label and the resulting verification level; open questions /
residual risks.
```

## Fill-in guidance

| Block | Get right | Why |
|---|---|---|
| **CONTEXT** | The *intent*, not the mechanics. "Users can't see X" beats "add a field to Y." | Intent lets the agent make the local calls the spec didn't anticipate. |
| **DIGESTED FINDINGS** | Paste the reader's `path:line` facts + the existing pattern to mirror. Hand over a digest, never a pointer into a long crib file (`.claude/rules/writer-brief-crib-digests.md`). | Stops the agent re-reading the subsystem your digester already covered — the whole point of two-stage. |
| **RESEARCH POINTERS** | Pre-warm BEFORE dispatching: check `docs/agent-knowledge/research/` (version + freshness per its README), else dispatch `research-specialist` first. | The writer cannot web-search — an uncovered API forces a `NEEDS_CONTEXT` round-trip. |
| **ADVISORY NOTES** | Only the `docs/agent-knowledge/engineering/*` notes that match the change. | They are leads; the writer re-verifies in code. |
| **TARGET FILES** | Exact absolute paths. | Bounds the diff so your verification is finite; absolute paths avoid wrong-tree writes (`.claude/rules/worktree-agent-dispatch.md`). |
| **SKILLS** | Only SKILL.md paths whose conventions this change actually touches. | Naming irrelevant skills wastes turns and trains the agent to skim the block. A pure-logic change often needs none. |
| **SCOPE** | State the boundary AND the exclusions. | Agents over-reach; "while I'm here" edits break your verification. |
| **CONSTRAINTS** | Feed forward any API a reader already verified. If the change alters a public signature, paste the plan's interface block verbatim. | Saves a redundant lookup; a paraphrased interface drifts (`.claude/rules/writer-brief-crib-digests.md`). |

## Don't restate its workflow

The agent's definition already carries its API-verification, self-check, and report steps. Don't re-describe them — it bloats the prompt and risks contradicting the agent file. Override only when *this* task needs something non-default (e.g. "skip lint, the file is generated", or this run's hygiene rules).

## What comes back — verify against this

`code-developer` returns a `STATUS:` first line (`DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | STOPPED`) plus a numbered report: files and purpose, changed regions, complete verbatim check output tagged introduced-vs-pre-existing (plus red/green output when a phase spec applies), an accessibility report when rendered UI was touched and the project defines a checklist, research provenance, any unverified-API flags, residual risks / STOPs / open questions, skills accounting per named skill, and PROPOSED KNOWLEDGE UPDATES (apply accepted ones yourself or through an assigned writer). If skills accounting says "no bearing" for a skill, you mis-picked it; if it echoes the path with no real detail, spot-check whether it was opened. "Self-checked" is the agent's claim — you still inspect the diff, run checks, and run the review gate.

Handle the STATUS line before anything else — and never re-dispatch unchanged after a non-DONE:

| STATUS | Your move |
|---|---|
| `DONE` | Verify the diff yourself — the status is a claim, not the check. |
| `DONE_WITH_CONCERNS` | Read the concerns BEFORE verifying; correctness/scope concerns get resolved first, observations get noted. |
| `NEEDS_CONTEXT` | Supply the missing context and resume or re-dispatch — the brief was incomplete, not the agent. **Research-gap case:** dispatch `research-specialist` for the named gaps (library, version, functions), marked **implementation-bound** so a stale note is refreshed rather than re-served, apply or pass on its digest, then resume the writer with the new pointers. |
| `STOPPED` | Change something first: tighten the spec, add the missing decision, split the task, or route the ambiguity to the user. A TIMEBOX stop lists REMAINING work: verify what landed, then dispatch the remainder as a fresh, smaller brief. |

## Reuse the warm reader

If the change direction came out of a digest you already ran, continue that reader via `SendMessage` (addressed by the agent ID from its dispatch result) to draft the brief or spec while it still holds the files. Readers are read-only, so this produces a *brief or spec*; authoring still routes to a writer.

There is no fixed follow-up cap: reuse a warm agent while its context is relevant, and start fresh when the objective or ownership changes or when a concise current brief is safer than a long transcript. The DIGESTED FINDINGS block exists so a fresh dispatch is cheap.

### If a dispatch dies mid-run

Don't trust its last progress message: a crashed writer can leave more in the tree than it reported (observed in practice). Recover from the main thread:

1. Inventory the working tree with one grep marker per scoped item. The tree, not the report, is ground truth for what landed.
2. Route the fully specified remainder (verbatim old→new hunks you already hold) to `bulk-editor`.
3. Dispatch a fresh `code-developer` for what still needs judgment, noting in DIGESTED FINDINGS what already landed.

For other failure modes (context exhausted, wrong report shape, the same failure twice), use the retry table in `references/brief-contract.md` § Fan-out and liveness.

## Phase briefs (phased execution)

For phased dispatches (`references/playbooks/multi-phase.md`), fill the same skeleton. Copy ACCEPTANCE verbatim from the phase spec, including its "Pass when" predicate and evidence level, and add one field after CONSTRAINTS:

```
TDD STEPS: Follow red-green strictly:
1. Write the failing test.
2. Run it — confirm it fails for the expected reason.
3. Implement the minimal code to pass.
4. Run it — confirm it passes.
5. Return your diff report with both runs' output.
```

A phase with genuinely no testable surface (e.g. pure CSS) states that in ACCEPTANCE and asks for a typecheck/lint/manual-verification fallback instead. The STATUS table and recovery rules above apply unchanged to phase dispatches.

## Worked example (illustrative)

```
You are implementing a change for an orchestrator that will verify your diff.

CONTEXT: Orders can have an expiry date but the list gives no visual cue
once one lapses. Add an "Expired" state so users can see at a glance which
orders can no longer be fulfilled.

DIGESTED FINDINGS (ground truth, do NOT re-digest):
- expiresAt is a nullable date column; already read in the list query
  at src/api/orders.ts:<line>
- the table renders status via a StatusBadge helper at
  src/components/orders/orders-table.tsx:<line>
- "expired" = expiresAt present AND before today in the user's timezone; the
  timezone-aware helper is <todayInTimezone(tz)> in src/lib/<dates>.ts

RESEARCH POINTERS: no external APIs touched.

TARGET FILES (you own only these; absolute paths):
- <repo-root>/src/components/orders/orders-table.tsx

SKILLS:
- .claude/skills/<orders-skill>/SKILL.md
- .claude/skills/<ui-skill>/SKILL.md

SCOPE: Only the "Expired" badge + its derived condition in the table component.
Do NOT touch the query, the schema, or any auto-cancellation logic.

CONSTRAINTS: Use the existing Badge component and color conventions from
<ui-skill>; compare dates with the timezone-aware helper, never the raw clock.

VALIDATION: <your typecheck>, <your lint>, <your unit tests>
```

## Project cross-cuts worth naming in CONSTRAINTS (when the change touches them)

List your project's invariants here once, so every writer brief can copy the ones that apply: `<your project's invariants>` — for example the helper every write to a protected column must go through, the single owner of a derived value (balances, totals, counters), the input-validation layer at each trust boundary, the shared mutation or loading hook callers must use, tenancy or ownership scoping rules, and the timezone-aware "today" helper.

## Keep in sync

If `code-developer`'s `## Output` contract or `## When invoked` workflow changes in `.claude/agents/code-developer.md`, update "What comes back" and "Don't restate its workflow" here to match. If `references/brief-contract.md` changes its field list, update the skeleton here.
