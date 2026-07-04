# Dispatching `code-developer` — the brief template

`code-developer` has **total context isolation**: it never sees this conversation, the reports your readers returned, or the decisions you already made — only the prompt you hand it (plus its own memory and preloaded skills). It also cannot ask you anything mid-run (subagents have no `AskUserQuestion`). So the brief IS the spec: every decision the work needs must be written down, or the agent guesses. This is the orchestrator's fill-in template for that brief.

Load this when you're about to dispatch `code-developer`. For the routing decision (is this even a `code-developer` job?) stay in `SKILL.md`; this file assumes you've already decided to author code.

## The writer test (confirm before you fill anything in)

Does *applying* the change require any decision — design, wording, API choice, where the logic goes? **Yes → `code-developer`.** **No → `bulk-editor`** with a verbatim old→new spec. If you find yourself writing exact replacement strings into the brief below, stop: you've specified it fully, so it's a `bulk-editor` job at haiku price. Don't pay Sonnet to retype your spec.

## The skeleton

```
You are implementing a change for an orchestrator that will verify your diff.

CONTEXT: <1–3 sentences — what to build and WHY. The agent has none of the
backstory; this is all it knows about intent.>

DIGESTED FINDINGS (from prior reads — treat as ground truth, do NOT re-digest):
- <fact + src/path.ts:line>
- <the pattern to follow + where it already lives, src/path.ts:line>
- <any constraint a reader surfaced>

RESEARCH CACHE POINTERS: <the research-specialist topic file(s) relevant to this
change — .claude/agent-memory/research-specialist/<segment>/<topic>.md — that
you PRE-WARMED by dispatching research-specialist before this dispatch for any
external library the change touches, or the line "no external APIs touched".>

TARGET FILES: <exact paths to create/modify — the ones you want touched>

SKILLS (read these SKILL.md files for house conventions):
- .claude/skills/<skill>/SKILL.md
- .claude/skills/<skill>/SKILL.md

SCOPE: <what to change — and explicitly what NOT to touch. "Only X; leave Y alone.">

DONE WHEN (the contract your report is verified against):
- <observable behavior, or the command that must pass>
- typecheck + lint clean on changed files (introduced diagnostics = not done)

CONSTRAINTS / KNOWN APIS (optional): <versions already pinned, house cross-cuts
that apply, an API a reader already verified so it needn't look it up again.>
```

**Brief longer than ~a screen?** Write the brief to a scratch file and shrink the dispatch to two lines: "Read <path> first — it is your requirements; exact values are verbatim" plus the report contract. Everything you paste into a dispatch stays resident in YOUR context for the rest of the session; a file path doesn't. Symmetrically, for a large change have the agent write its full report to a sibling `<brief>-report.md` and return only the STATUS line, files changed, and a one-line self-check summary — then Read the report file when you verify.

## Fill-in guidance

| Block | Get right | Why |
|---|---|---|
| **CONTEXT** | The *intent*, not the mechanics. "Users can't see X" beats "add a field to Y." | Intent lets the agent make the local calls the spec didn't anticipate. |
| **DIGESTED FINDINGS** | Paste the reader's `path:line` facts + the existing pattern to mirror. | Stops the agent re-reading the subsystem your digester already covered — the whole point of two-stage. |
| **RESEARCH CACHE POINTERS** | Pre-warm the cache (dispatch `research-specialist`) BEFORE dispatching the writer, for any external library the change touches; name the topic file(s) or state "no external APIs touched". | The writer cannot web-search — an uncached API forces a `NEEDS_CONTEXT` round-trip instead of a clean first pass. |
| **TARGET FILES** | Name exact paths. | Bounds the diff so your verification plan is finite. |
| **SKILLS** | Only the SKILL.md paths whose conventions this change actually touches — nothing "just in case". | The agent must read every skill you name (item 8 makes it account for each). Naming one that doesn't bear on the change wastes its turns AND trains it to skim the block, so it starts skipping the skills that DO matter. A pure-logic change (helper, math, a param) often needs zero skills — leave the block out rather than pad it. |
| **SCOPE** | State the boundary AND the exclusions. | Agents over-reach; "while I'm here" edits break your verification. |
| **CONSTRAINTS** | Feed forward any API a reader already verified. | Saves a redundant docs lookup; the agent still verifies anything you didn't pin. |

## Don't restate its workflow

The agent already scouts empty memory, verifies external APIs against the shared research cache before using them, self-checks with the project's typecheck/lint commands, and logs the run to its memory — all from its definition. **Do not re-describe those steps in the brief.** It bloats the prompt and risks contradicting the agent file. (Verified in a 2026-07-05 smoke test on the reference deployment: a brief that named only the task + one skill still fired scout, cache verification, self-check, and the memory log correctly.) Only override when *this* task needs something non-default — e.g. "skip lint, the file is generated" or "the research cache doesn't cover this API, use the vendored types" (pre-warm the cache first — see RESEARCH CACHE POINTERS above — rather than telling the writer to guess).

## What comes back — verify against this

`code-developer` returns a `STATUS:` first line (`DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | STOPPED`) plus an 8-item report: (1) files + purpose, (2) changed regions with `file:line`, (3) the COMPLETE verbatim typecheck + lint output — every error and warning, tagged introduced-vs-pre-existing, never summarized or dropped as "unrelated" — labeled "self-checked" (when a phase brief carried TDD STEPS, this item also carries both the red (failing) and green (passing) test run output verbatim; when the scope touched rendered UI and the project defines an accessibility checklist, it also reports each applicable check `pass` / `fail` / `not-tested (reason)`), (4) cache provenance — each research-specialist topic file consulted, with its `fetched_at`, or the explicit line "no external APIs touched", (5) UNVERIFIED-API flags, (6) memory notes written, (7) STOPs, (8) skills accounting — per named skill, the path + the one convention it applied, or "read; no bearing". If item 8 comes back "no bearing" for a skill, you mis-picked it — tighten the SKILLS block next dispatch; if it echoes the path with no real detail, the agent likely didn't open it (spot-check). "Self-checked" is the agent's claim, not your verification — you still own `SKILL.md` step 6 (independent `git diff` + build/lint, then the independent review gate). Any UNVERIFIED-API flag or STOP is a signal to re-dispatch or resolve, not to wave through.

Handle the STATUS line before anything else — and never re-dispatch unchanged after a non-DONE:

| STATUS | Your move |
|---|---|
| `DONE` | Verify the diff yourself (step 6) — the status is a claim, not the check. |
| `DONE_WITH_CONCERNS` | Read the concerns BEFORE verifying; correctness/scope concerns get resolved first, observations get noted. |
| `NEEDS_CONTEXT` | Supply the missing context and re-dispatch — the brief was incomplete, not the agent. **Research-gap case:** if the missing context is an uncached external API, dispatch `research-specialist` to fill the named gaps (library, version, functions), marking that dispatch **implementation-bound** so any stale entry it finds is refreshed rather than re-served — the writer rejects any entry aged >= ttl_days, so an unrefreshed stale hit just reproduces the same `NEEDS_CONTEXT` on the next round. Then resume the writer with the new cache pointers — that resume counts toward the warm-reuse round cap below. |
| `STOPPED` | Change something before re-dispatching: tighten the spec, add the missing decision, split the task, or route the ambiguity back to the user. |

## Reuse the warm reader

If the change direction came out of a digest you already ran, don't fill this template from scratch and spawn a fresh agent — it would re-read everything. Continue the digester that still holds the files in context via `SendMessage`, addressed by the raw agent ID from its dispatch result, and give it the same blocks as a follow-up brief. (The reader tiers are read-only, so this produces a *spec or brief*; the actual authoring still routes to `code-developer`.)

**Cap the reuse at 2 — exceptionally 3 — resume rounds in the same files.** Every `SendMessage` resume replays the agent's full prior transcript as input; at ~50–80K tokens per substantive round, a 4th round crosses a 200K window and dies mid-run with a hard "Prompt is too long" 400 (observed 2026-07-05, with partial edits left in the tree). Past the cap, fill this template for a FRESH `code-developer` instead — the DIGESTED FINDINGS block exists precisely so a fresh dispatch is cheap: 2–5K tokens of brief vs 150K of replayed transcript.

### If the warm agent dies mid-run

A dead ID cannot be resumed — the resume replays the same over-long input and 400s again. And do NOT trust its last progress message: the 2026-07-05 crash had completed MORE items than it reported. Recover orchestrator-side:

1. Inventory the working tree with one grep marker per scoped item (the identifier or string each item introduces) — the tree, not the report, is ground truth for what landed.
2. Route the fully-specified remainder (verbatim old→new hunks you already hold) to `bulk-editor`.
3. Re-dispatch a fresh `code-developer` with this template for what still needs judgment, noting in DIGESTED FINDINGS what already landed.

## Phase briefs (phased execution)

For phased dispatches (`references/phased-execution.md`), fill the same skeleton above plus two extra fields, drawn from the phase spec:

```
ACCEPTANCE CRITERIA: <the testable statement(s) that define this phase done —
copied verbatim from the phase spec.>

TDD STEPS: Follow red-green strictly:
1. Write the failing test.
2. Run it — confirm it fails.
3. Implement the minimal code to pass.
4. Run it — confirm it passes.
5. Return your diff report (the orchestrator commits — you do not).
```

Place both fields after CONSTRAINTS in the skeleton. A phase with genuinely no testable surface (e.g. pure CSS) states that in ACCEPTANCE CRITERIA and asks for a typecheck/lint/manual-verification fallback instead of steps 1–4 — see `references/phased-execution.md` §Testing bar.

The existing STATUS table and crash-recovery rules above apply unchanged to phase handoffs — a phase dispatch is dispatched, verified, and recovered exactly like any other `code-developer` dispatch. The only new pieces are the two fields above and that the orchestrator, not the agent, owns the commit (`references/phased-execution.md` §Per-phase cycle step 5).

## Worked example (illustrative)

```
You are implementing a change for an orchestrator that will verify your diff.

CONTEXT: Items can have an end date but the list gives no visual cue once one
lapses. Add an "Ended" state so users can see at a glance which items are no
longer active.

DIGESTED FINDINGS (ground truth, do NOT re-digest):
- endDate is a nullable column; already read in the list query at
  src/actions/items.ts:<line>
- the row component renders status via a Badge at
  src/components/item-row.tsx:<line>
- "ended" = endDate present AND before today; the project's date helper is
  todayInUserTimezone(tz) in src/lib/dates.ts

RESEARCH CACHE POINTERS: no external APIs touched.

TARGET FILES:
- src/components/item-row.tsx

SKILLS:
- .claude/skills/<domain-skill>/SKILL.md
- .claude/skills/<ui-skill>/SKILL.md

SCOPE: Only the "Ended" badge + its derived condition in the row component.
Do NOT touch the query, the schema, or any lifecycle logic.

CONSTRAINTS: Use the existing Badge component and the project's styling
conventions; compare dates with the project's timezone helper, never new Date().
```

## Project cross-cuts worth naming in CONSTRAINTS (when the change touches them)

The agent follows CLAUDE.md and the named skills, but naming the cross-cuts in play sharpens the diff: the project's validation layer, the helper/handler classes that own mutations, encryption or serialization helpers, date/timezone helpers — any layer the change must route through rather than reimplement.

## Keep in sync

If `code-developer`'s `## Output` contract or `## When invoked` workflow changes in `.claude/agents/code-developer.md`, update the "What comes back" and "Don't restate its workflow" sections here to match.
