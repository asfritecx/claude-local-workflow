---
name: local-workflow
description: Coordinate substantial research, debugging, implementation, review, or planning across multiple files or domains. Use when the task benefits from bounded house subagents, specialist ownership, or independent review — "look into / analyze / investigate / build / review X", "delegate this", "be an orchestrator", "use house agents". Skip simple work the main thread can finish directly, such as single-fact lookups or one-line edits.
user-invocable: true
---

# Local workflow: main thread plus bounded house agents

The main thread owns scope, decisions, integration and the final answer. It may do straightforward reads and edits itself. Delegate bounded, independent work when parallel reading or a specialist materially improves the result, never just to satisfy a workflow shape.

## Route first

Classify the task, pick one playbook, and copy its steps into the todo list verbatim. Mark any step you skip `skip: <reason>`, so the skip stays visible. When the user says "new task" or the work changes kind, route again.

| The task is… | Playbook |
|---|---|
| One or two files, no design decision | **Direct:** do it, verify it on the right surface, report. No playbook needed. |
| "How does X work / where is / why does" | `references/playbooks/investigation.md` |
| Something is broken | `references/playbooks/bug-fix.md` |
| New behavior | `references/playbooks/feature.md` |
| Same behavior, simpler code | `references/playbooks/refactor.md` |
| Judge existing work (a branch, diff, PR or design) | `references/playbooks/review.md` |
| Two or more subsystems, or dependent milestones | `references/playbooks/multi-phase.md` |
| Unattended "until X passes" | `references/playbooks/autonomous-run.md` |
| Resuming or pausing a run | `references/playbooks/session-pickup.md` |
| Skills, rules, agents, docs | `references/playbooks/docs-and-skills.md` |

Principles fire on triggers, such as the second failed fix or adding structure. They are listed in `references/principles.md`.

Always:
- Check the branch (your project's branch notes in CLAUDE.md, if any).
- Preserve unrelated work already in the tree.
- Ask the user only about a material choice, a destructive action, an external mutation or expanded authority.
- Settle an observable fact with a quick experiment instead of asking.

## Contracts

- **Brief contract** (`references/brief-contract.md`):
  - Every dispatch carries GOAL, SCOPE, CONTEXT, ACCEPTANCE, VERIFY, TIMEBOX, FORBIDDEN, STANDING and REPORT. A missing field means no dispatch.
  - That file also holds the evidence labels (`ran` / `read` / `inferred` / `unknown`), the verification levels, the standing-orders register, and the fan-out and liveness rules: one message per wave, pilot before fan-out, don't poll, retry according to how it failed, account for every agent.
- **Writers** (`references/dispatching-code-developer.md`):
  - A writer owns only the files named in its brief. Parallel writers need disjoint file sets.
  - The writer test: does applying the change need any decision? If yes, use `code-developer` or a specialist writer. If no, use `bulk-editor` with a verbatim old→new spec.
- **Review gate** (`references/review-gate.md`):
  - Run `code-reviewer` after every code-changing wave.
  - Add `adversarial-reviewer`, plus the same `code-reviewer` brief with a per-call `model: "fable"` (or another model family than your session's), for a design choice, schema change, security-sensitive path, concurrency or caching boundary, or a user request to challenge the approach.
  - Triage findings into Act on / Consider / Noted / Dismissed. Record confirmed / rejected / deferred with a reason and who raised it, and bind the verdict to the tree state.
- **Knowledge:**
  - `docs/agent-knowledge/INDEX.md` routes to advisory notes; re-verify them in code.
  - Readers propose note updates, and the main thread or an assigned writer applies them.
  - External or current facts go only to `research-specialist`, which checks `docs/agent-knowledge/research/` first. Pre-warm research before a writer touches an external library, because writers can't web-search.

## Skill map: pick the relevant skills per stream

Scan every available skill by **name and description** (or `ls .claude/skills/`) and pick what matches. This map covers the high-signal pairings and indexes relevance only. Name skills by file path, `.claude/skills/<skill>/SKILL.md`: a skill is a directory, and reading the directory throws EISDIR.

<!-- Populate per project. Replace the placeholder rows with real domain → skill pairings.
     `<prj>` is this project's short prefix (for example `shop`, `api` or `app`); see references/domain-expert-template.md. -->

| When the task touches… | Hand the agent these skills |
|---|---|
| `<your domain A>` (for example billing) | `<your skill-1>`, `<your skill-2>`. Dispatch **`<prj>-<domain-a>-expert`** if one exists. |
| `<your domain B>` (for example auth) | `<your skill-3>`, `<your skill-4>`. Dispatch **`<prj>-<domain-b>-expert`** if one exists. |
| Web or external research, current facts | Dispatch **`research-specialist`**, the sole web tier. It returns a digest plus a PROPOSED NOTE for you to apply. |
| Local workflow, agent sync | `local-workflow` and its references. Dispatch **`localworkflow-sync`**. |

**Cross-cutting skills:** list the skills every stream touching a given surface should also receive (for example a security or data-handling skill whenever user data is read or written, or a UI skill whenever rendered UI changes).

## Agent roster

Model and effort tiers live only in `.claude/rules/agents-roster.md`.

| `subagent_type` | Boundary | Dispatch it for |
|---|---|---|
| **`code-digester`** | read-only | **Default reader:** digest a subsystem, file or skill; audits; second-angle reads. |
| **`<prj>-<domain>-expert`** *(optional, per project)* | read-only | A stream squarely in that domain. Each expert preloads its domain skills and reads its note under `docs/agent-knowledge/domain/`. |
| **`localworkflow-sync`** | read-only | Drift audits across the workflow and agent layer, the knowledge wiring and the Codex mirror; guides adding a new domain expert. |
| **`deep-analyst`** | read-only | Genuinely hard threads only: cross-file traces, architecture mapping, gnarly debugging. Its pinned tier is slower and costlier (`.claude/rules/agents-roster.md`). |
| **`research-specialist`** | repo read-only; web | The sole external-research tier. |
| **`code-developer`** | writer | Authoring that needs any design, wording, placement or API decision. It checks its own work and returns a diff report. |
| **`bulk-editor`** | writer | Fully specified mechanical edits only. |
| *your specialist writers, if any* | writer | Specialist execution in their surfaces (for example schema, infra or UI). |
| **`skill-auditor`** | read-only | Post-change docs audit: FRESH/STALE verdicts plus edit specs. |
| **`code-reviewer`** | read-only | The defect pass after every code-changing wave. It derives the delta from git. |
| **`adversarial-reviewer`** | read-only | A design challenge when a change embodies a material design choice. |

**Routing and dispatch:**
- **Pick the agent.** Default to `code-digester`. Use the matching `<prj>-<domain>-expert` for a single-domain stream, `skill-auditor` for cross-domain docs audits, and `deep-analyst` only when it's genuinely hard. Prefer house agents over `Explore` or `general-purpose`, including in plan mode. Use `general-purpose` only for a read-and-act thread no house agent covers, and say which capability was missing.
- **Warm or fresh.** Continue a warm reader with `SendMessage` while its context is relevant, for example to draft a writer's spec. Send writers fresh consolidated briefs instead.
- **Model override.** A per-call `model` accepts aliases only, and there is no per-call effort. An alias from a different model family than the session gives a real cross-family run; a same-family alias collapses to the session model.
- **Shared contract.** Read-only house agents preload `house-agent-contract`, which covers the read-only rule, citation form, evidence labels, the timebox and knowledge proposals. Don't restate those in briefs.

## Implement, review, keep guidance current

- **After every code-changing wave:**
  1. Inspect the delta yourself (`git diff`, untracked files).
  2. Run proportionate checks (`<your typecheck>`, `<your lint>`, `<your unit tests>`, targeted tests).
  3. Run the review gate.
  4. Fix confirmed in-scope findings, and re-review when a fix changes behavior.
- **Scope of the gate.** Docs-only changes get a lighter editorial check. Phases are integration checkpoints, not commit points: no commits or pushes unless the user asked. If your project has a pre-commit gate, commits go through it.
- **Verify agent work yourself.** An agent's final message is a self-report, not proof.
  - Check the diff against the ask: all of the requested change, and only that.
  - Prefer a runnable check over prose.
  - Read-only reports must use plain relative `path:line` citations. Treat anything else as malformed evidence to correct or verify independently.
- **Keep guidance current after a change lands.**
  - Audit the touched skills and rules: the owning `<prj>-<domain>-expert` for a single domain, or `skill-auditor` for a cross-domain change (`references/skill-staleness-audit.md`).
  - When a confirmed defect exposes a durable invariant, prefer a mechanism over prose, then consider a rule (`references/rule-capture.md`).

## Finish: the reply contract

- **Lead with the outcome.**
- **Then:**
  - files changed;
  - checks run, each with its evidence label and verification level;
  - review dispositions, with who raised each;
  - dismissed findings;
  - what was not verified, and why;
  - residual risks;
  - deferred work;
  - an account of every dispatched agent.
- **Style.** Write plain sentences, not symbol-speak. "No" and "not verified" are acceptable answers. Never claim verification you didn't perform.

## When NOT to use

Skip the fan-out for single-fact lookups, a one-line edit, or anything answerable from context already in the conversation. If you'd finish faster yourself, do that.

## Adding a house subagent

- **Procedure:** `references/adding-a-subagent.md` covers frontmatter, body shape, registry pickup, the smoke test and the sync list.
- **Per-subsystem expert:** use `references/domain-expert-template.md`, or dispatch `localworkflow-sync` to draft one.
- **Sourced rationale:** `references/subagent-best-practices.md`.

## Keep in sync

- **`.claude/agents/*.md`:**
  - On a model or effort change, update `.claude/rules/agents-roster.md`, which is the only tier table.
  - On a boundary or roster change, update the Agent roster table above and `references/adding-a-subagent.md`.
  - Agent changes may need a session restart before they take effect (`.claude/rules/agents-roster.md` § Reload caveat).
- **`.claude/skills/house-agent-contract/SKILL.md`:** re-check `references/brief-contract.md` and `references/domain-expert-template.md` when it changes.
- **`references/review-gate.md`** and **`references/dispatching-code-developer.md`:** re-check when the matching agent's `## When invoked` or `## Output` changes.
- **The playbooks, `references/brief-contract.md` and `references/principles.md`:** re-check when the router table, a brief field or a principle name changes. The playbooks cite principles by name.
- **`references/skill-staleness-audit.md`:** re-check when the Skill map, the domain-expert pattern or `skill-auditor`'s Output changes.
- **`references/rule-capture.md`:** re-check when the rule shape or the `docs/agent-rules/` mirror convention changes.
- **Skill map:** keep it curated as skills are added, renamed or removed. Never copy skill descriptions into it.
- **Codex mirror** (if installed): `.agents/skills/local-workflow/`, `.codex/agents/*.toml` and `docs/agent-rules/`.
  - Mirror shared facts only: roles, boundaries, invariants and paths.
  - Never mirror model or effort tiers; they diverge on purpose.
- **`docs/agent-knowledge/INDEX.md`:** re-check the domain-note routing when a `<prj>-<domain>-expert` is added, renamed or rescoped.
