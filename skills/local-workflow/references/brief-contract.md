# Brief contract: every dispatch, reader or writer

A subagent sees only its brief, its own definition and any skills it preloads. It never sees this conversation, and it cannot ask you anything mid-run, so the brief is the product. Weak output usually means a weak brief. This file is the single template for readers and reviewers. For `code-developer`, `references/dispatching-code-developer.md` fills in the same fields with more writer detail.

## Required fields

Every brief carries all nine fields. If a field is missing, don't dispatch. A field can be one line, and "none" is a valid value when it's true. Size the brief to the unit of work, not to this template.

| Field | Readers and reviewers | Writers |
|---|---|---|
| **GOAL** | One line: the decision or artifact this read serves. | One line: what to build and why. The intent lets the agent make local calls the spec didn't anticipate. |
| **SCOPE** | Which paths and questions are in; what is out. | Target files as absolute paths (you own only these), plus explicit exclusions. |
| **CONTEXT** | 1–3 sentences plus the skills to read by path (`.claude/skills/<x>/SKILL.md`, the file, not the directory). | A digest of prior reads (`path:line` facts, the pattern to mirror); plan interface blocks quoted verbatim (`.claude/rules/writer-brief-crib-digests.md`); research pointers. |
| **ACCEPTANCE** | Numbered deliverables. The agent must return all of them. | Testable criteria that define done. |
| **VERIFY** | The evidence form: `path:line` plus a verbatim quote where you'll reason on exact text. | The commands to run: targeted tests, `<your typecheck>`, `<your lint>`, `<your unit tests>`. |
| **TIMEBOX** | A coverage budget, for example "at most ~15 files or ~100KB of source". Past it, return partial results with a NOT COVERED list. | The same. A partial diff plus an accurate list beats a dead writer. |
| **FORBIDDEN** | Read-only; no web research (report a RESEARCH GAP instead); nothing outside SCOPE. | The hygiene block below; nothing outside TARGET FILES. |
| **STANDING** | The run's standing orders, pasted verbatim (see below), or "none". | The same. |
| **REPORT** | The return shape plus a final status line. | The agent's own `STATUS:` contract, plus anything non-default for this task. |

**Hygiene block for writers**, pasted as is:

```
- Other agents and the user may have live edits in this tree. Preserve unrelated edits.
- Never use git restore, git reset, git checkout --, git stash (any form) or git clean -f.
- Write no per-agent memory files.
- Locate edits by verbatim text, never by line number, in files you edit.
```

In a worktree session, add absolute paths and the line "do not resolve paths relative to your working directory" (`.claude/rules/worktree-agent-dispatch.md`).

## Status vocabulary

- **Writers** end with their own report contract. `code-developer` (and any specialist writer you give the same contract) opens with `STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | STOPPED` (responses in `references/dispatching-code-developer.md`); `bulk-editor` returns applied edits or a STOP report; your other specialist writers, if any, return their numbered `## Output` report, with `NEEDS_CONTEXT` on a research gap.
- **Verifier tasks** (checks, smoke tests, audits) return `PASS | ISSUES | BLOCKED`, each with its evidence. A gap is never a pass: a check that couldn't run is `BLOCKED`, not `PASS`.
- **Readers** end with the deliverables plus `NOT COVERED: <list or none>`.

## Evidence labels

Every claim a reader returns, and every claim in your finish report, carries one of these labels:

| Label | Meaning | Carries |
|---|---|---|
| `ran` | A command was executed. | The command and its result. |
| `read` | Seen in the code or docs. | `path:line`, plus a verbatim quote where exact text matters. |
| `inferred` | Reasoned, not observed. | The chain of reasoning. |
| `unknown` | Searched and not found. | What was searched ("document the null"). |

A count claim (test totals, register counts, file counts) carries the command that regenerates it.

Each change's verification level is one of: `not-verified`, `type-check-only`, `unit-test-verified`, `integration-verified` (your real backing services), or `live-ui-verified`. Match the check to the surface: a UI change is checked in a browser (a browser-automation tool or Playwright), a storage change by reading the value back, and a CLI change by running the real command. An inconclusive check, or one run on the wrong surface, is not a pass. Never hand the user a check you could run yourself.

## Standing orders

Keep the user's instructions that are in force in a numbered register, each dated and quoted exactly:

- `docs/runs/<YYYY-MM-DD-slug>/standing-orders.md` for tracked runs and any run that spans a restart;
- `<scratchpad>/standing-orders.md` for an ad-hoc session. The scratchpad does not survive a new session.

When you catch yourself restating an instruction, append it to the register. Paste the register into every brief's STANDING field, and re-read it after a compaction.

## Fan-out and liveness

- **One message per wave.** Send every independent dispatch in a single message; sending them one at a time wastes wall-clock.
- **Pilot before fan-out.** Before three or more similar dispatches, run one end to end, fix the brief, then fan out.
- **Shard big reads.** A brief that names more than ~15–20 substantial files or ~100KB of source gets split into parallel shards (`references/subagent-best-practices.md`).
- **Don't poll.** Completion arrives as a notification. Never message a running agent just to check on it.
- **Fresh brief, not a chain.** When a writer's scope changes, send a new consolidated brief rather than chaining corrections through `SendMessage`. Follow-up questions to a warm reader are fine.
- **Retry according to how it failed:**

| Failure | Response |
|---|---|
| Ran out of context or turns | Retry with a smaller SCOPE, or run a digest first and send the writer the digest. |
| Transient tool or API error | Retry once, unchanged. |
| Wrong report shape | Send a fresh brief with a tighter REPORT field. |
| Died mid-run | Inventory the tree yourself, with one grep marker per scoped item: its last message may understate what landed. Route the fully specified remainder to `bulk-editor` and re-dispatch fresh for what still needs judgment. |
| The same failure twice | Stop retrying. Write down the premise both attempts shared, and attack it (`references/principles.md`). |

- **Account for every agent.** The finish report lists every dispatched agent and what came of it, including those that died or were superseded.

## Reader brief example

```
GOAL: Decide whether the order-summary report can reuse the invoice aggregation query.
SCOPE: src/api/orders.ts, src/lib/order-aggregation.ts, src/api/invoices.ts. Out: UI, schema.
CONTEXT: Read .claude/skills/<orders-skill>/SKILL.md first. Advisory leads:
  docs/agent-knowledge/INDEX.md; re-verify every claim in code.
ACCEPTANCE:
  1. Each query that aggregates order totals, with its path:line and the aggregation shape.
  2. Whether the predicates differ (status filter, period window, customer match), quoted verbatim.
  3. Reuse blockers, if any.
VERIFY: verbatim quotes for SQL.
TIMEBOX: those three files plus direct imports; return partial with NOT COVERED past that.
FORBIDDEN: read-only; no web research; report any external need as a RESEARCH GAP.
STANDING: <paste the register, or "none">
REPORT: the numbered deliverables; the preloaded contract supplies labels and closing sections.
```

Citation form for readers is owned by `.claude/skills/house-agent-contract/SKILL.md` (§ Before returning). Readers that preload it already carry the rule, so don't restate it in briefs.

## Keep in sync

- Re-check this file when a house agent's status line or output contract changes.
- Re-check it when `house-agent-contract` changes.
- Re-check it when `.claude/rules/worktree-agent-dispatch.md` changes the hygiene lines.
- The Codex twin (if installed) is `.agents/skills/local-workflow/references/brief-contract.md`.
