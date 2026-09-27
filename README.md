# local-workflow: a portable orchestration kit for Claude Code and Codex

A drop-in **orchestration workflow** for [Claude Code](https://claude.com/claude-code) and [Codex](https://developers.openai.com/codex). The main thread owns scope, decisions, integration and the final answer. It routes each task to a playbook, and it delegates bounded, independent work to read-only house agents and briefed writers. It verifies what those agents did before it reports. The kit ships native skills, custom agents, rules and a knowledge scaffold for both platforms, plus one-time installers.

> **The core idea:** the main thread holds the conclusion; bounded agents do the reading, and an independent reviewer checks the writing.

Synced to myfinance f0d50696 (2026-09-27).

---

## Why

The orchestration pattern is reusable, but a real installation gets tangled up with one project's specifics: its subsystems, its domain experts, its invariants and its checks. This kit is the pattern with all of that stripped out and replaced by placeholders, so you can carry it between projects and fill in only the project-specific parts.

**What it gives you:**
- A **router with nine playbooks** (investigation, bug-fix, feature, refactor, review, multi-phase, autonomous-run, session-pickup, docs-and-skills). Simple work skips them and is done directly.
- A **brief contract**. Every dispatch carries GOAL, SCOPE, CONTEXT, ACCEPTANCE, VERIFY, TIMEBOX, FORBIDDEN, STANDING and REPORT, and every claim carries an evidence label (`ran`, `read`, `inferred`, `unknown`).
- A **review gate**. `code-reviewer` runs after every code-changing wave. `adversarial-reviewer` and a model-diverse second opinion join it for design, schema, security and concurrency changes. Findings are triaged into Act on, Consider, Noted and Dismissed.
- **Shared knowledge instead of per-agent memory.** Agents propose notes for `docs/agent-knowledge/`, and the main thread applies them.
- **One tier table** (`.claude/rules/agents-roster.md`) that sets each agent's model and effort.
- An **optional git guard hook** that blocks stash, restore, reset, `checkout --` and similar commands in a tree that several agents share.
- A built-in discipline: **verify what agents did; never trust the self-report.**

---

## What's in the box

```
claude-local-workflow/
├── README.md                     ← you are here
├── DEPLOY.md                     ← run-once Claude Code installer (greenfield / existing project)
├── DEPLOY-CODEX.md               ← run-once Codex installer
├── LICENSE
├── docs/                         ← background research (not installed)
│   ├── anthropic-subagent-best-practices.md
│   ├── anthropic-memory-rules.md
│   └── codex-port-review.md      ← historical July Claude↔Codex mapping
├── skills/
│   ├── local-workflow/           → .claude/skills/local-workflow/
│   │   ├── SKILL.md              ← router, contracts, Skill map (placeholder), roster, reply contract
│   │   └── references/
│   │       ├── brief-contract.md, principles.md, review-gate.md
│   │       ├── dispatching-code-developer.md, adding-a-subagent.md, domain-expert-template.md
│   │       ├── skill-staleness-audit.md, rule-capture.md, subagent-best-practices.md
│   │       └── playbooks/        ← the nine playbooks
│   └── house-agent-contract/     → .claude/skills/house-agent-contract/ (preloaded into readers)
├── agents/                       → .claude/agents/ (nine house agents)
├── rules/                        → .claude/rules/
│   ├── agents-roster.md          ← the only model/effort tier table
│   ├── worktree-agent-dispatch.md
│   └── writer-brief-crib-digests.md
├── knowledge/                    → docs/agent-knowledge/ (INDEX + research/engineering/domain)
├── hooks/                        → .claude/hooks/ (optional git guard, its tests and settings snippet)
└── codex/
    ├── skills/local-workflow/    → .agents/skills/local-workflow/ (SKILL.md, openai.yaml, references incl. playbooks.md)
    ├── agents/*.toml             → .codex/agents/ (the same nine house agents)
    └── agent-rules/              → docs/agent-rules/ (Codex twins of the three rules)
```

`claude-local-workflow/` is the folder `git clone` creates. You copy it into a target project's root, install from it, then delete it (see `DEPLOY.md`). If it has a different folder name, substitute that name throughout.

---

## The agent roster

Model and effort tiers are set only in `rules/agents-roster.md`; the columns below mirror it.

| Agent | Model / effort | Boundary | Role |
|---|---|---|---|
| `code-digester` | opus / low | read-only | **Default reader.** Digest a subsystem, file or skill; audits; second-angle reads. |
| `research-specialist` | opus / medium | repo read-only; web | **Sole external-research tier.** Cache-first at `docs/agent-knowledge/research/`; returns a digest plus a PROPOSED NOTE. |
| `deep-analyst` | fable / high | read-only | Genuinely hard threads only: cross-file traces, architecture mapping, gnarly debugging. |
| `code-developer` | opus / medium | writer (no web) | Authoring that needs any design, wording, placement or API decision. Self-checks and returns a diff report. |
| `bulk-editor` | opus / low | writer | Fully specified mechanical edits only; STOPs on any mismatch. |
| `skill-auditor` | opus / medium | read-only | Post-change docs audit: FRESH/STALE verdicts plus edit specs. |
| `code-reviewer` | opus / high | read-only | The defect pass after every code-changing wave. Derives the delta from git. |
| `adversarial-reviewer` | opus / high | read-only | Challenges the design when a change embodies a material design choice. |
| `localworkflow-sync` | opus / low | read-only | Drift audits across the workflow layer and the Codex mirror; guides adding a domain expert. |
| `<prj>-<domain>-expert` *(yours)* | opus / low | read-only | One per major subsystem, from `domain-expert-template.md`. |

Readers pin a `tools:` allowlist (`Read, Grep, Glob, Bash, Skill, ToolSearch`) and preload `house-agent-contract`. `research-specialist` uses `disallowedTools` instead, so it keeps its web tools. The kit ships model **aliases**. `rules/agents-roster.md` explains when to pin full model IDs instead.

---

## How the workflow runs

1. **Route.** Classify the task and pick one playbook, or do it directly if it is one or two files with no design decision. Copy the playbook's steps into the todo list, and mark a skipped step `skip: <reason>`.
2. **Brief.** Every dispatch carries the nine brief fields. Independent agents go out in one message. A pilot runs before a large fan-out.
3. **Verify.** Inspect the delta yourself, run the project's checks, and treat each agent's report as a self-report, not proof.
4. **Review.** Run the review gate after every code-changing wave, triage the findings, and bind the verdict to the tree state.
5. **Keep guidance current.** Audit the touched skills and rules, apply knowledge-note proposals, and prefer a mechanism over a new rule when a defect exposes a durable invariant.
6. **Report** by the reply contract: outcome first, then files, checks with evidence labels, review dispositions, what was not verified, residual risks, deferred work, and an account of every dispatched agent.

Full detail lives in `skills/local-workflow/SKILL.md` and its `references/` (Claude), and in `codex/skills/local-workflow/SKILL.md` (Codex).

---

## Install

- **Claude Code:** follow **[`DEPLOY.md`](DEPLOY.md)**. Copy the kit folder into the target project's root and ask your agent to run it, or run it by hand. It installs the skills, agents, rules and knowledge scaffold, optionally the git guard, then asks you to fill the placeholders, restart, and smoke-test.
- **Codex:** follow **[`DEPLOY-CODEX.md`](DEPLOY-CODEX.md)**. It installs `.agents/skills/local-workflow/`, the nine `.codex/agents/*.toml` and the `docs/agent-rules/` twins, and shares `docs/agent-knowledge/` with the Claude install.

Restart the session after installing. New agents, skills and hooks are picked up at session start.

---

## Customizing per project

Everything project-specific is a `<placeholder>`. `grep -rn '<your ' .claude docs/agent-knowledge` lists what is left after install.

1. **The Skill map** in `SKILL.md`: pair each domain with the project skills a stream should receive, and with its domain expert.
2. **Domain experts:** one read-only `<prj>-<domain>-expert` per major subsystem (`<prj>` is a short project prefix such as `shop`, `api` or `app`). Dispatch `localworkflow-sync` to draft one, or fill `references/domain-expert-template.md` by hand.
3. **`code-reviewer` invariants:** the handful of project invariants a reviewer must check on every delta.
4. **Checks:** `<your typecheck>`, `<your lint>`, `<your unit tests>`.
5. **Pre-commit gate** (optional): if your project has one, commits go through it. The workflow never commits or pushes unless the user asks.

---

## Credits & license

Built for [Claude Code](https://claude.com/claude-code) and [Codex](https://developers.openai.com/codex). Released under the [MIT License](LICENSE).
