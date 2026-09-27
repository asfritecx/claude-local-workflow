---
name: local-workflow
description: Coordinate substantial research, debugging, implementation, review, or planning across multiple files or domains. Use when the task benefits from bounded subagents, specialist ownership, or independent review; skip for simple work the main thread can complete directly.
---

# Local Workflow

Keep the main thread responsible for scope, decisions, integration, and the final answer. Use subagents when independent work can run in parallel or when a specialist materially improves quality. The main thread may complete straightforward reads and edits itself.

## Route first

Classify the task, then pick one playbook from [playbooks](references/playbooks.md):
- investigation;
- bug fix;
- feature;
- refactor;
- review;
- multi-phase;
- autonomous run;
- session pickup and pause;
- docs, skills, rules and agents.

Copy its steps into the plan, and mark any step you skip `skip: <reason>`. A change to one or two files with no design decision takes the Direct route: do it, verify it on the right surface, and report. [Principles](references/principles.md) lists the triggers that change a decision.

## Start with scope

1. Read `AGENTS.md`, check the current branch (your project's branch notes, if any), and preserve unrelated work already in the tree.
2. Identify the smallest useful work streams. Give each stream one concrete question or one owned edit surface.
3. Read the project skills that apply from `.agents/skills/<skill>/SKILL.md`. Tell a subagent which skills to read; skill contents are not automatically injected into custom agents.
4. Read relevant entries from `docs/agent-rules/INDEX.md` and `docs/agent-knowledge/INDEX.md` explicitly. Treat knowledge notes as leads to verify against current code.

## Project routing

Populate this table during installation. Scan the available `.agents/skills/*/SKILL.md` metadata and applicable `AGENTS.md` files, and list only guidance that materially applies to a stream. `<prj>` is the project's short prefix; see [domain expert template](references/domain-expert-template.md).

| When the task touches | Read first / dispatch |
| --- | --- |
| `<your domain A>` | `<your AGENTS.md or .agents/skills/<skill>/SKILL.md paths>`; dispatch `<prj>-<domain-a>-expert` if installed |
| `<your domain B>` | `<your AGENTS.md or .agents/skills/<skill>/SKILL.md paths>`; otherwise use `code-digester` |
| Cross-cutting architecture or security | Root `AGENTS.md` plus the project's architecture and security sources; use `deep-analyst` when the reasoning is hard |
| External or current facts | `research-specialist` only; it checks `docs/agent-knowledge/research/` first |
| Local workflow, agent sync | This skill and its references; dispatch `localworkflow-sync` |

Keep this table a routing index. Do not copy whole skill descriptions or domain invariants into it.

## Delegate deliberately

Use `collaboration.spawn_agent` only for bounded work that can proceed independently. For a profile-pinned custom agent, pass `fork_turns: "none"` with a self-contained brief, or a deliberately bounded positive `fork_turns` value when limited recent context is required. A full-history fork can inherit the parent's model and reasoning effort instead of the custom profile. Pass the matching custom `agent_type`, a unique `task_name`, and a self-contained `message`.

The message carries the nine fields of the [brief contract](references/brief-contract.md): GOAL, SCOPE, CONTEXT, ACCEPTANCE, VERIFY, TIMEBOX, FORBIDDEN, STANDING and REPORT. STANDING is the run's standing-orders register, pasted verbatim. FORBIDDEN includes the reminder that other agents share the working tree and must preserve unrelated edits. Pilot one dispatch before fanning out three or more similar ones.

When the runtime exposes a spawned task's effective model, reasoning effort, or sandbox, inspect it before reporting that profile. Otherwise record the TOML configuration and any dispatch overrides separately, and state that the effective profile is unavailable. The TOML is the configured default and behavior contract; parent or live runtime overrides can change the effective profile.

Route domain-scoped reads to `<prj>-<domain>-expert` agents and `code-digester` (GPT-6 Luna / max); difficult multi-file traces to `deep-analyst` (GPT-6 Astra / high); and external or current facts to `research-specialist` (Luna / max). Use `code-developer` for general implementation (GPT-6 Sol / medium), scoped specialist writers and reviewers (Sol / high), and `bulk-editor` only for exact mechanical edits (Luna / max). Read [subagent best practices](references/subagent-best-practices.md) for the full roster policy.

Do not delegate merely to satisfy a workflow shape. Avoid overlapping write ownership. With limited concurrency, keep a slot available when review or follow-up work is likely.

After dispatch:

- use `collaboration.send_message` to add information without starting an idle agent;
- use `collaboration.followup_task` to give an existing idle agent more work and trigger a turn;
- use `collaboration.wait_agent` with a useful timeout to await mailbox updates;
- inspect every result and reconcile it with the current tree before acting.

See [dispatching a code developer](references/dispatching-code-developer.md) for implementation briefs and [adding a subagent](references/adding-a-subagent.md) when the roster itself must change.

## Implement and review

Writers own only the files named in their brief. Readers may propose edits or knowledge notes, but a writer or the main thread applies them. Continue through routine fixes already authorized by the user; do not insert automatic commit, push, run-start, or approval stops. If your project has a pre-commit gate, commits go through it.

After any code-changing wave:

1. Inspect the delta and run proportionate checks (`<your typecheck>`, `<your lint>`, `<your unit tests>`, targeted tests).
2. Dispatch `code-reviewer` for an independent defect review.
3. Also dispatch `adversarial-reviewer` when the change includes a material design or approach choice, a schema change, a security-sensitive path, or a concurrency or caching boundary, or when the user asks to challenge the approach.
4. Triage the findings into Act on, Consider, Noted or Dismissed, record who raised each one, and fix the confirmed issues that fall within the authorized scope.
5. Bind each verdict to the tree it saw: HEAD, the diff hash and the untracked files. A later edit voids the verdict, so rerun the affected checks and the review as needed.

Dispatch profile-pinned reviewers with `fork_turns: "none"` and a self-contained brief. If filesystem-enforced independence is required, start them from a read-only parent or runtime. Verify the effective child sandbox when the runtime exposes it; otherwise report that enforcement could not be independently observed. Reviewer TOMLs alone do not prove enforcement under a broader live override.

Read [review gate](references/review-gate.md) for the brief and disposition contract. For staged work, use the multi-phase playbook in [playbooks](references/playbooks.md); phases organize risk and evidence but do not imply automatic commits.

## Keep project guidance current

After implementation, audit the touched domain skills and explicitly loaded rules for stale claims. Use the owning `<prj>-<domain>-expert` for a single domain or `skill-auditor` for cross-domain changes. Apply confirmed docs updates in the same authorized task. Read [skill staleness audit](references/skill-staleness-audit.md).

Record reusable, project-specific knowledge in the curated indexes:

- `docs/agent-knowledge/INDEX.md` routes evidence-backed shared notes.
- `docs/agent-rules/INDEX.md` routes rules that agents must explicitly load.

Readers propose notes; the main thread or an assigned writer applies them. Do not create hidden memory injection or claim that these files load automatically. Read [rule capture](references/rule-capture.md) for the bar and [domain expert template](references/domain-expert-template.md) for domain ownership.

## Finish

Put the outcome first. Then report:
- the files changed;
- the checks run, each with an evidence label (`ran`, `read`, `inferred` or `unknown`) and each change's verification level;
- the review dispositions, with who raised each one, and the dismissed findings with the filter that dismissed them;
- what was not verified, and why;
- every dispatched agent and its outcome;
- residual risks and any intentionally deferred work.

Don't claim verification you didn't perform. Write in plain sentences.
