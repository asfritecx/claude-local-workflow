# Phased execution — multi-phase delivery protocol

Canonical spec for splitting a complex code-authoring task into testable delivery phases. `SKILL.md` only points here (loop step 1's complexity check, step 6's per-phase gate variant, the loop contract's commit carve-out) — this file is the single source of truth; never duplicate its detail back into `SKILL.md`. Maps house tiers onto the `superpowers` shape this protocol ports (these are skill names from the public `superpowers` Claude Code plugin — if it isn't installed in your environment, the references below are descriptive of the pattern, not a hard dependency): `code-developer` = implementer, your project's independent review gate = reviewer, the run ledger = progress file.

## Terminology

- **Phase** — a delivery unit: a testable slice of a multi-file change, gated by your project's independent review gate and committed on its own.
- **Resume round** — the warm-agent context-reuse unit (renamed from the old "work"-prefixed phase term — see `references/dispatching-code-developer.md` §Reuse the warm reader). Distinct from a phase; a single delivery phase's dispatch (plus its own follow-ups) is one resume round.

## Entry criteria (evaluated at loop step 1, Decompose)

Phased mode when the change meets ANY of:
- spans ≥2 subsystems
- touches ~4+ files that each carry a design decision
- stacks schema + code + UI in one change
- would need more than one `code-developer` dispatch to land

Below that bar: the existing two-stage path (`SKILL.md` §Agent roster "Two-stage changes") applies unchanged — no phase list, no per-phase gate/commit.

## Run-start STOP

Before dispatching phase 1, propose to the user in one STOP:
- the phase list (names + one-line scope each)
- the branch/worktree plan (see below)
- the sentence: "Clean phases will be committed automatically as they pass gate."

User approval of this plan starts phase 1 AND is the standing explicit authorization to commit each clean phase for the rest of the run — no further per-phase commit confirmation is needed.

## Phase breakdown rules (ported from `superpowers:writing-plans`)

A phase is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate — fold setup/scaffolding into the phase that needs it; split only where a reviewer could reject one phase while approving its neighbor.

Each phase spec contains:
- **Files** — create / modify / test, exact paths
- **Interfaces** — consumes (from earlier phases, exact signatures) / produces (for later phases, exact signatures)
- **Acceptance criteria** — the testable statement(s) that define done
- **TDD steps** — the 5-step cadence below

No-placeholders bar: no "TBD", no "add appropriate error handling" without showing the handling, no stub/TODO deliverables — every phase spec contains the actual content a fresh agent needs.

## Per-phase cycle

1. Orchestrator fills the phase brief — the extended dispatch template in `references/dispatching-code-developer.md` §Phase briefs — and dispatches a **fresh** `code-developer`. Fresh is the cheap default; the resume-round cap is unchanged and applies only within a phase's own follow-ups, never across phases. Before dispatching, pre-warm the research cache for any external library the phase touches (dispatch `research-specialist` first if the cache doesn't already cover it) and include the resulting cache pointers in the phase brief's RESEARCH CACHE POINTERS block.
2. `code-developer` executes TDD red-green per its spec, self-checks the project's typecheck / lint / unit-test commands, logs the run to its own memory, and returns a diff report.
3. Orchestrator verifies the diff against the phase spec — the same quality-control rules as any writer dispatch (`SKILL.md` §Quality-control).
4. Run your project's independent review gate on the phase delta: a defect pass always; add an adversarial pass with 1–2 lines of task-derived focus when the phase embodies a design decision.
5. Zero findings → orchestrator runs `git add <phase files> && git commit -m "(phase N/<total>) <summary>"`, appends the ledger row, and advances to the next phase. Any finding → STOP, present with your true/false-positive judgment, user decides; fixes land via a fix dispatch, re-gate, then commit. This clean/finding split is the binding result contract for every per-phase gate run — never auto-apply a fix, and never skip the commit+auto-advance on a clean pass.
6. After the final phase: synthesis + endgame STOP (merge / PR / keep / discard, per `superpowers:finishing-a-development-branch`). Loop steps 7–8 (docs staleness, rule capture) run ONCE over the accumulated run, not per phase — except a review-gate-derived rule proposal, which rides whichever finding-STOP the gate produces (mid-phase or final).

## Branch / worktree policy

Phased mode NEVER commits to the trunk/main branch — always a feature branch. Use a worktree (`.worktrees/<name>`, your tooling's native worktree helper if it has one, `git worktree` fallback per `superpowers:using-git-worktrees`) when the tree is dirty at run start or the user asks for one. Endgame follows `superpowers:finishing-a-development-branch`: merge / PR / keep / discard.

## Ledger row shape

`Phase N: done — <files>, self-check clean, review clean, commit <sha>`

Record deviations inline, e.g. `Phase N: done — no testable surface (pure CSS), fell back to typecheck/lint/manual verification, commit <sha>`.

## Testing bar

FULL TDD per phase:
1. Write failing test
2. Run it — confirm it fails
3. Implement minimal code
4. Run it — confirm it passes
5. Orchestrator commits (per-phase cycle step 5 above)

A phase with genuinely no testable surface (e.g. pure CSS) must say so in its phase spec and fall back to the project's typecheck/lint/manual verification — record the fallback in the ledger row; never silently skip TDD.

## Ported from

- `superpowers:subagent-driven-development` — fresh-subagent-per-task + task review + final broad review shape.
- `superpowers:writing-plans` — task right-sizing, Files/Interfaces/Acceptance criteria structure, no-placeholders bar.
- `superpowers:using-git-worktrees` — worktree detection/creation order.
- `superpowers:finishing-a-development-branch` — endgame options (merge / PR / keep / discard).
