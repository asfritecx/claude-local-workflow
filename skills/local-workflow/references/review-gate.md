# Review gate — the independent check after code changes

Independent verification for code-changing waves, driven by two house agents dispatched through the Agent tool:

- **`code-reviewer`** (`subagent_type: code-reviewer`) — the defect pass. Correctness bugs, security holes, partial-failure and concurrency errors, regressions, meaningful missing tests, and breaches of the project's standing invariants. Runs on EVERY code-changing wave. Each finding carries a trigger and a consequence (the concrete failure scenario), and the report lists the checks considered and found clean.
- **`adversarial-reviewer`** (`subagent_type: adversarial-reviewer`) — the design/approach challenge, added when the change embodies a material design choice. Give it 1–2 task-specific questions; it walks the design axes (including state ownership and time boundaries — timezone, DST, clock skew, expiry) and returns `verdict: approve | needs-attention`, severity-ranked findings, and the alternatives it considered.

Both are read-only readers with restricted direct tools: neither has Write or Edit, and their contracts forbid changes. They still have Bash, so a file write is prevented by instruction, not by construction. Each report ends with PROPOSED KNOWLEDGE UPDATES (usually `none`); apply any you accept to `docs/agent-knowledge/` yourself or through an assigned writer.

## How to dispatch

Run the gate after you have inspected the delta and completed proportionate checks. When both reviewers run for the same delta they are INDEPENDENT of each other and go in ONE message so they run concurrently. Never brief `adversarial-reviewer` with `code-reviewer`'s conclusions.

Dispatch-brief skeleton — keep it this short:

```
GOAL: review gate for <run name>.
SCOPE: <one or two sentences — the files/areas touched and the shape of the change>.
  Derive the delta yourself from git — do not review anything pasted here.
CONTEXT: <the user-facing requirement or defect that motivated it>.
  Focus (adversarial pass only): <1–2 task-derived questions — e.g. "challenge the choice to
  compute the window in Node rather than in SQL, and what it forecloses for DST">.
ACCEPTANCE: findings per your Output contract, bound to the tree state you reviewed.
VERIFY: `path:line` plus a verbatim quote for each finding; label claims ran/read/inferred/unknown.
TIMEBOX: <coverage budget, e.g. ~30 probes>; past it, return what you have plus NOT COVERED.
FORBIDDEN: read-only; no fixes; nothing outside SCOPE.
STANDING: <the run's standing orders, verbatim, or "none">
REPORT: your agent's Output contract.
```

**What must NOT go in the brief:** the writer's rationale, the writer's self-assessment, a pasted diff, or another reviewer's findings. A brief carrying the author's story reproduces the generator-grades-itself failure, and a pasted diff is the author's selection of what gets seen. Both agents are told to discount such content; do not lean on that.

**Independence has two layers.** The procedural layer is fresh context, each reviewer's own derivation of the delta, no author rationale, and adversarial framing. Two reviewers on the same model still share blind spots, so the second layer is a model-diverse second opinion.

## Model-diverse second opinion

- **When:** the same trigger that adds `adversarial-reviewer`. That means a material design choice, a schema change, a security-sensitive path, a concurrency or caching boundary, or a user request to challenge the approach.
- **What:** re-send the identical `code-reviewer` brief with a per-call `model` alias from a different model family than your session (for example `model: "fable"` from an Opus session), in the same message as the other reviewers.
  - A different-family alias gives a real cross-family run. A same-family alias would collapse back to the session model.
  - The agent's own contract and tools still apply.
- **Reading the two reports:**
  - A finding both models raise is high confidence.
  - A finding only one model raises gets checked against the code before it gets a disposition.
  - Record which model raised what in the **Raised by** column.
- **Cost:** a larger model family (such as Fable) can be slower and costlier and may bill to usage credits (`.claude/rules/agents-roster.md`), which is why it runs only on this trigger. The consent-prompt behavior for a subagent is unverified (`docs/agent-knowledge/research/claude-code-subagents.md`).
- **Further passes:** when a change warrants yet another independent pass, the user can run the built-in `/code-review` skill.

## Review scope, from git state

- **Dirty tree** → the working-tree diff, INCLUDING untracked files. Untracked files never appear in any diff and must be read directly.
- **Clean tree** → `<base>...HEAD`.
- **The trap:** reviewing a dirty tree against a base ref silently EXCLUDES the uncommitted changes — you get a clean review of already-committed work while the actual delta goes unreviewed (observed in practice).
- A new file is invisible in branch scope and can draw a spurious "add the file to the patch" finding — recognise it as a scope artifact, not a defect.

**Execution mode:** subagents run in the background by default (`docs/agent-knowledge/research/claude-code-subagents.md`); wait for the completion notification and don't poll.

## Triage, then disposition

Sort every finding into a bucket before deciding anything. Then map the bucket to a disposition:

| Bucket | Meaning | Disposition |
|---|---|---|
| **Act on** | Real, in scope, worth fixing now. | `confirmed` |
| **Consider** | Real but debatable in value or scope. | `confirmed` or `deferred`, with a reason |
| **Noted** | True, but no action is warranted now. | `deferred` |
| **Dismissed** | Fails a filter below. | `rejected`, with the filter named |

**Filters.** A finding is dismissed when it is:
- nitpick gravity: style or taste with no correctness effect;
- hypothetical rather than actual: no reachable trigger in this code;
- a premature abstraction;
- "I would have done it differently" without a defect;
- missing context the reviewer didn't have, such as a documented invariant or a deliberate plan decision (cite it).

**Never dismissed by default:** findings about security, auth, encryption or other data-protection boundaries, migrations, money arithmetic, concurrency, or `<your project's invariants>`. Verify these in code, and escalate them if you can't settle them.

**Agreement map.** When two or more reviewers ran, note which findings each raised. Overlap raises confidence; a solo finding needs your own check.

1. Verify every finding against the code yourself. Keep file paths and line numbers exactly as the reviewer reports them.
2. Record each finding in a disposition table: **Finding | Bucket | Disposition | Reason | Raised by** (for example `code-reviewer@opus`, `code-reviewer@fable`, `adversarial-reviewer@opus`).
3. Fix confirmed findings that fall within the user's authorized scope, via the appropriate writer (or directly, when straightforward), and rerun the affected checks.
4. Seek another independent pass when a fix materially changes behavior.
5. With no findings, say so explicitly and keep the residual-risk note brief.
6. List the dismissed findings in the finish report with their filters. Showing what you rejected is how the user can trust the rest.

## Verdict binding

A review verdict or check result holds only for the tree it saw. Next to each disposition table and each check result, record the tree state:

```sh
git rev-parse --short HEAD; git diff HEAD | shasum -a 256
git ls-files -z --others --exclude-standard | xargs -0 -r shasum -a 256
```

The last line hashes the CONTENTS of every untracked file, because `git diff HEAD` never covers them. Take the snapshot before dispatching the reviewers and again when their reports arrive; if anything differs, the review saw a moving tree. Any later edit to the reviewed files voids the verdict. Re-run the affected checks, and re-review when a fix changes behavior. A report that pairs a verdict with a different tree state is claiming verification it didn't do.

Review is not an automatic approval stop. Escalate to the user only when a finding exposes a material product or design choice, needs a destructive or external action, or needs authority not already granted. A deferred finding is reported in the finish, with its reason.

A confirmed finding that teaches a durable, file-tied lesson may also become a rule proposal — see `references/rule-capture.md`.

## When to run which

- **Always after a code-changing wave:** `code-reviewer`, after your own inspection and checks.
- **Add `adversarial-reviewer` and the model-diverse second opinion** (§ Model-diverse second opinion) when the change embodied a material design choice (new pattern, schema change, security-sensitive path, concurrency or caching boundary) or the user asks to challenge the approach.
- **Docs-only changes** (skills, rules, docs markdown) may get a lighter editorial check instead of the full gate; code changes always get the defect pass.
- **Zero repo changes** → no gate.

In multi-phase runs (`references/playbooks/multi-phase.md`) the gate runs per phase on that phase's delta, and each phase's verdict is bound to its own tree state.

## Keep in sync

Contract mirrored from `.claude/agents/code-reviewer.md` and `.claude/agents/adversarial-reviewer.md`. Re-check this reference when either agent's `## When invoked` or `## Output` section changes. The Codex twin (if installed) is `.agents/skills/local-workflow/references/review-gate.md`.
