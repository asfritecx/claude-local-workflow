# Playbooks

Classify the task, pick one playbook, and copy its steps into the plan. Mark any step you skip as `skip: <reason>`, so skips stay visible. Route again when the user starts a new task.

**Direct route.** A change to one or two files with no design decision needs no playbook. Do it, verify it on the right surface, and report.

The Claude twin keeps one file per playbook, under `.claude/skills/local-workflow/references/playbooks/`.

## Investigation

**You own the explanation. Nothing is edited.**

1. Restate the question as sub-questions that evidence can answer.
2. Use one reader for a simple question. For a complex one, spawn 2–4 parallel explorers: `code-digester`, the matching `<prj>-<domain>-expert`, or `deep-analyst`.
3. All explorers return the same sections: Components, Flow, Files read, Boundaries, Non-obvious, Open questions, NOT COVERED.
4. Send external facts to `research-specialist`.
5. Settle any disagreement between explorers in the code yourself, and check every load-bearing claim yourself before you reply.

**Reply:** Overview, Key concepts, How it works, Where things live, Gotchas, all with evidence labels.

## Bug fix

**You own the diagnosis and the proof.**

1. Reproduce the bug and record the failing command verbatim.
2. Narrow the hypotheses by bisection.
3. Confirm the mechanism with runtime evidence.
4. Land a failing test first (for behavior that depends on real backing services, use your integration-test harness, `<your integration tests>`).
5. Fix the root cause.
6. Grep for the same pattern elsewhere.
7. Paste the output before and after the fix.
8. Run the review gate, then keep guidance current.

**Stop:** after two failed fixes that share one premise, attack that premise before trying again.

## Feature

**You own the design and the integration.**

1. Scope the work: check the branch, the skills and the digests.
2. Name the data shape first, as an interface block.
3. Run the throughput checkpoint: blocking first steps, independent workstreams, shared mutable state, and the smallest safe decomposition. Mark any that don't apply `n/a: <reason>`.
4. Settle factual questions with a throwaway prototype instead of asking the user.
5. Sketch two designs only when the design is contested. Screen both for shallow modules, information leakage and pass-through methods.
6. Switch to Multi-phase if the work meets its entry criteria.
7. Build through the brief contract.
8. Verify on the matching surface, then run the review gate.

## Refactor

**You own behavior preservation.**

1. Name what gets simpler, and measure it.
2. Pin the current behavior with characterization tests.
3. Subtract before adding.
4. Map every caller.
5. Migrate every caller and delete the old API in the same wave.
6. Characterization tests must pass unchanged.
7. If the code isn't easier to read, revert your own edits by hand.

## Review

**You own the verdict, not the fixes.**

1. State the intent and the review scope.
2. Bind the tree state.
3. Run the reviewers independently, in one wave.
4. Verify every finding yourself.
5. Triage the findings with an agreement map (`review-gate.md`).
6. Deliver the verdict. Fix things only if asked.

## Multi-phase

**You own the plan and the verdicts, never the code.**

**Entry criteria.** Use this playbook when any of these holds:
- the work spans two or more subsystems;
- about four or more files each carry a design decision;
- schema, code and UI are stacked in one change;
- landing it needs more than one writer dispatch.

**Steps:**
1. Open `docs/runs/<YYYY-MM-DD-slug>/` with:
   - `README.md`, whose state table is the one home for status;
   - `standing-orders.md`;
   - `decisions.tsv`.
2. Write each phase with these parts:
   - an outcome;
   - files owned and files excluded;
   - interfaces as a fenced block, which is the contract;
   - acceptance criteria;
   - validation, with an evidence level and a **Pass when** predicate;
   - review requirements;
   - blocking conditions.

   No placeholders.
3. Pilot the first phase end to end.
4. For each phase:
   1. dispatch a fresh writer with a phase brief;
   2. the writer works red-green;
   3. inspect the delta and run the checks yourself;
   4. run the review gate, binding the verdict to the tree state;
   5. fix, recheck, then advance.

   Parallelize only across disjoint write sets.
5. Close out with:
   - one staleness audit and rule capture over the whole change;
   - the reflect pass (`rule-capture.md`);
   - the finish report.

**Commits and pauses.** A phase is an integration checkpoint, not an automatic commit or approval stop. Don't commit or push between phases unless asked. Pause only for a material choice, a destructive action, an external mutation or expanded authority. Don't assume a fixed context window. Spawn a fresh task when a concise brief is safer than a long thread.

**`decisions.tsv`.** The header is `ts	phase	decision	why	evidence	result`, tab-separated.
- Rows are append-only and record decision points only.
- To supersede a row, append a new one. Never edit an old row.
- Keep each row to one line, with no tabs inside cells.
- `evidence` carries a label and a command, path or tree hash.
- `result` is `done`, `reverted`, `superseded` or `open`.
- On resume, read the README state table and the TSV tail first, then `git status` and `git diff`.

## Autonomous run

**You own the finish condition.**

1. Write the exit predicate as a command. A duration is only a budget.
2. Work in an isolated worktree.
3. Open a run folder with `standing-orders.md` and `decisions.tsv`, and keep the trail there.
4. Each iteration makes one change, runs one check and adds one trail row.
5. Never relax the predicate by weakening tests, disabling lint rules or skipping checks.
6. A plateau is not a stop: change the approach.
7. Stop at the predicate, or at a genuine dead end, with a write-up.

## Session pickup and pause

**You own continuity.**

**To pick up:**
1. Find the run folder.
2. Read the README state table, `standing-orders.md` and the `decisions.tsv` tail.
3. Compare them with `git status` and `git diff`.
4. Re-verify inherited claims before building on them.
5. State the next move.

**To pause:**
1. Stop at a safe boundary.
2. Add a trail row.
3. Write a recall capsule into the README:
   - at most five bullets;
   - threads tagged `[verified, uncommitted]`, `[in flight <branch>]`, `[planned]` or `[merged #N]`;
   - problems;
   - the next move.

## Docs, skills, rules and agents

**You own reader load.**

1. Change each fact in the file that owns it, and point to it from elsewhere.
2. Subtract first, and prefer a mechanism to prose.
3. Anchor edits by verbatim text.
4. Check frontmatter and links.
5. Write the twin for any shared fact (`.claude/` ⇄ `.agents/skills/`, `docs/agent-rules/`, `.codex/agents/`). Never mirror model or effort tiers.
6. Audit with `skill-auditor`, the matching `<prj>-<domain>-expert` for a single-domain skill, or `localworkflow-sync` for the workflow layer.
7. If a skill misbehaves mid-task, fix it later as its own change.
