# Brief contract

A spawned agent sees only its brief and its own definition. It never sees the parent conversation, so the brief is the product. Every `collaboration.spawn_agent` message carries these nine fields. "none" is a valid value, and a field can be one line. Size the brief to the unit of work.

| Field | Readers and reviewers | Writers |
|---|---|---|
| GOAL | The decision or artifact the read serves. | What to build and why. |
| SCOPE | Paths and questions in, and what is out. | Owned files as absolute paths, plus exclusions. |
| CONTEXT | 1–3 sentences plus the `.agents/skills/<skill>/SKILL.md` and `docs/agent-rules/` paths to read. | A digest of prior reads, plan interface blocks quoted verbatim (`docs/agent-rules/writer-brief-crib-digests.md`), and research pointers. |
| ACCEPTANCE | Numbered deliverables. | Testable criteria for done. |
| VERIFY | The evidence form: `path:line` plus a verbatim quote where exact text matters. | The commands to run. |
| TIMEBOX | A coverage budget. Past it, return partial results with a NOT COVERED list. | The same. |
| FORBIDDEN | Read-only, no web research, nothing outside SCOPE. | The hygiene lines in `docs/agent-rules/worktree-agent-dispatch.md`; locate edits by verbatim text, never by line number (`docs/agent-rules/writer-brief-crib-digests.md`); nothing outside owned files. |
| STANDING | The run's standing orders, verbatim. | The same. |
| REPORT | The return shape plus a status line. | The writer's status contract. |

## Status

- **Writers** end with `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` or `STOPPED`.
- **Verifier tasks** (checks, smoke tests, audits) return `PASS`, `ISSUES` or `BLOCKED`, with evidence. A check that could not run is `BLOCKED`, never `PASS`.
- **Readers** end with NOT COVERED (`none` when complete).

## Evidence labels

Label every load-bearing claim:

| Label | Meaning | Carries |
|---|---|---|
| `ran` | A command was run. | The command and its result. |
| `read` | Seen in the code or docs. | `path:line`. |
| `inferred` | Reasoned, not observed. | The reasoning. |
| `unknown` | Searched and not found. | What was searched. |

A count claim carries the command that regenerates it.

**Verification levels for each change:** `not-verified`, `type-check-only`, `unit-test-verified`, `integration-verified` (your real backing services) or `live-ui-verified`.

Match the check to the surface:
- a UI change is checked in a browser;
- a storage change is checked by reading the value back;
- a CLI change is checked by running the real command.

An inconclusive check, or one run on the wrong surface, is not a pass.

## Standing orders

Keep the user's instructions that are in force in a numbered register, dated and quoted exactly. It lives in `docs/runs/<YYYY-MM-DD-slug>/standing-orders.md` for tracked runs. Append to it whenever you restate an instruction, and paste it into every brief's STANDING field.

## Fan-out and liveness

- **Pilot first.** Before three or more similar dispatches, run one end to end and fix the brief.
- **Wait, don't poll.** Use `collaboration.wait_agent` rather than check-in messages.
- **New brief, not a chain.** When a writer's scope changes, send a fresh consolidated brief instead of chaining corrections.
- **Retry by failure mode:**

  | Failure | Response |
  |---|---|
  | Ran out of context or turns | Retry with a smaller scope, or run a digest first. |
  | Transient error | Retry once, unchanged. |
  | Wrong report shape | Send a tighter REPORT. |
  | Died mid-run | Inventory the tree yourself before re-dispatching. |
  | The same failure twice | Stop, and attack the shared premise. |

- **Account for every agent.** The finish report lists every dispatched agent and its outcome.

The Claude twin is `.claude/skills/local-workflow/references/brief-contract.md`.
