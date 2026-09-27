# Playbook: multi-phase delivery

**Role:** you own the plan and the verdicts, never the code. Writers land each phase. You sequence the phases, verify each one, and carry facts forward. A phase is an integration checkpoint, not an automatic commit or approval boundary. This file is the single source for the phased protocol.

## Entry criteria

Use phases when a code-authoring change meets ANY of these:

- it spans two or more subsystems;
- it touches about four or more files that each carry a design decision;
- it stacks schema, code and UI in one change;
- it would need more than one `code-developer` dispatch to land.

Below that bar, use `references/playbooks/feature.md` or `references/playbooks/bug-fix.md`.

## Steps (copy into todos; mark any you skip `skip: <reason>`)

1. **Open the run folder** at `docs/runs/<YYYY-MM-DD-slug>/`. It holds:
   - `README.md` with a state table, which is the one home for status;
   - `standing-orders.md` (`references/brief-contract.md` § Standing orders);
   - `decisions.tsv` (see below);
   - the plan, when one is written.
2. **Present the phase list**, with a name and a one-line scope for each, and proceed.
   - Pause for the user only for a material choice, a destructive action, an external mutation or expanded authority.
   - Don't commit or push between phases unless the user asked.
   - When the tree is dirty at the start, or the user asks for isolation, use a worktree (`EnterWorktree` preferred) and follow `.claude/rules/worktree-agent-dispatch.md`.
3. **Write the phase specs** (see below). Check that the sequence is verifiable: each phase can be checked before the next starts.
4. **Pilot the first phase end to end.** Fix the brief template from what the pilot teaches before running later phases, especially before any parallel fan-out.
5. **Run the per-phase cycle** (see below) for each phase. Add a row to `decisions.tsv` at each decision point, and update the README state table.
6. **Close out:**
   - Run the docs staleness audit and rule capture once, over the whole accumulated change.
   - Run the reflect pass (`references/rule-capture.md` § Reflect pass).
   - Write the finish report.

## Phase spec

A phase is the smallest unit that carries its own test cycle and is worth an independent review.
- Fold setup into the phase that needs it.
- Split only where a reviewer could reject one phase while approving its neighbor.

Each phase spec contains:

| Part | Contents |
|---|---|
| **Outcome** | The observable result. |
| **Files** | Files to create, modify and test, as exact paths, plus the surfaces explicitly excluded. |
| **Interfaces** | What it consumes from earlier phases and produces for later ones, as exact signatures in a fenced block. That block is the contract (`.claude/rules/writer-brief-crib-digests.md`). |
| **Acceptance criteria** | The testable statements that define done. |
| **Validation** | The targeted tests plus the standard checks, the target evidence level (`references/brief-contract.md`), and a **Pass when:** predicate. |
| **Review requirements** | `code-reviewer` always. Add `adversarial-reviewer` and the model-diverse second opinion when the phase carries a material design choice. |
| **Blocking conditions** | What must hold before the next phase starts. |

No placeholders. That means no "TBD", no "add appropriate error handling" without showing it, and no stub or TODO deliverables. Every spec carries what a fresh agent needs.

## Per-phase cycle

1. Fill the phase brief (`references/dispatching-code-developer.md` § Phase briefs) and dispatch a writer.
   - A fresh writer per phase is the usual default, since a concise current brief beats a long transcript.
   - Pre-warm research for any external library the phase touches: `docs/agent-knowledge/research/`, or else `research-specialist` first.
2. The writer runs red-green per the spec, checks its own work, and returns a diff report.
3. Inspect the phase delta and run the targeted checks yourself.
4. Run the review gate on the phase delta (`references/review-gate.md`).
   - Triage and record the dispositions with Raised-by.
   - Bind the verdict to the phase's tree state.
5. Fix confirmed in-scope findings, recheck, and re-review when a fix changes behavior. Then advance.

Parallelize inside a phase only when tasks are independent and write ownership doesn't overlap (`references/principles.md`: separate-before-serializing-shared-state). You integrate the results and carry facts learned in earlier phases into later briefs.

## `decisions.tsv`: the run's resume index

Columns, tab-separated, with this header row:

```
ts	phase	decision	why	evidence	result
```

- Rows are append-only. Log decision points only, not every action.
- Supersede a row by appending a new one that names the old one. Never edit a row.
- Keep each row to one line, with no tabs inside cells.
- `evidence` carries an evidence label and its command, path or tree hash. `result` is `done`, `reverted`, `superseded` or `open`.
- After a compaction or restart, read the README state table and the tail of `decisions.tsv` before anything else, then `git status` and `git diff`. Trust the trail and the tree over recollection.
- A long observational ledger is optional. If you keep one, it holds evidence only; status lives in the README state table, and decisions live in the TSV. Don't copy status by hand into several files.


## Testing bar

Red-green in every phase:
1. Write the failing test.
2. Run it and confirm it fails for the expected reason.
3. Implement the minimal code.
4. Run it and confirm it passes.

A phase with genuinely no testable surface, such as pure CSS, says so in its spec and falls back to typecheck, lint and manual or browser verification. Record the fallback; never skip the test step silently.

## Done when

- Every phase is verified and reviewed, with bound verdicts.
- The README state table is current.
- The reflect proposals have gone to the user.

## Reply shape

- **Outcome.**
- **Phase table:** phase, files, checks with verification level, and review dispositions.
- **Deferred findings.**
- **Reflect proposals** (Accepted / Rejected / Backlog), awaiting approval.
- **Not verified.**
- **Agent accounting.**
