---
name: local-workflow
description: Orchestrate substantial multi-step repository work by delegating focused reading, external research, implementation, mechanical edits, review, and documentation audits to specialized Codex subagents. Use for cross-file research, architecture analysis, security audits, difficult debugging, planning, feature implementation, code review, or requests to delegate, fan out, investigate, digest, build, or review a non-trivial change. Do not use for a trivial lookup or one-line edit that is faster and clearer to complete directly.
---

# Local Workflow

Act as the orchestrator: retain requirements, decisions, verification, and the final synthesis in the main thread; delegate bounded reading and execution to the narrowest suitable custom agent.

Read `references/agent-roster.md` before the first dispatch. Read `references/project-routing.md` to select project guidance and domain experts for each thread.

## Binding loop

1. **Inspect and decompose.** Check the working tree and applicable `AGENTS.md`. Split the task by independent context, subsystem, or evidence source. Shard a reading brief that names more than roughly 15-20 substantial files or 100 KB of source. For implementation work, evaluate the entry criteria in `references/phased-execution.md`; if any match, read it and obtain its run-start phase, branch/worktree, and commit-authorization decisions before phase 1.
2. **Dispatch readers first.** Start all independent agents before waiting. Use `code-digester` by default, `deep-analyst` for hard traces, `research-specialist` for current external facts, and a project expert for a clearly owned domain.
3. **Review and close gaps.** Check every report for evidence, omissions, contradictions, and research gaps. Send focused follow-ups to warm agents when useful; prefer a fresh agent after two substantial follow-ups, exceptionally three.
4. **Route mutations.** Send authored changes to `code-developer`; send exact old-to-new replacements or exact file contents to `bulk-editor`. The main thread never mutates repository files while this skill is active, including deletions.
5. **Verify and synthesize.** Independently inspect the diff and run the narrowest relevant checks. Reconcile reports into decisions; never concatenate agent summaries as the answer.
6. **Run an independent gate.** For any repository delta, use a fresh read-only reviewer, normally `deep-analyst`, for a defect pass. Add an adversarial pass when the change embodies a design or security decision. Present findings with your own judgment and obtain the user's decision before fixes.
7. **Audit guidance staleness.** Compare the landed delta with affected `.agents/skills/**`, nested `AGENTS.md`, `.codex/agents/**`, and `.codex/agent-memory/**`. Follow `references/skill-staleness-audit.md`; apply exact documentation specs through `bulk-editor`.
8. **Capture durable lessons.** Follow `references/rule-capture.md`. Put stable, subtree-specific guidance in the closest nested `AGENTS.md`; propose root-wide changes instead of silently editing the root guidance.

Record each step as `done`, `n/a - zero repository changes`, or `user-waived: <quoted decision>` in `.codex/run-ledgers/`. A step is never skipped merely because it appears unnecessary.

## Mutation and permission rules

- Preserve unrelated working-tree changes. Writers receive exact target files, scope exclusions, acceptance criteria, and relevant skill or `AGENTS.md` paths.
- Never stage, commit, push, install dependencies, apply migrations, or contact external systems unless the user has authorized that action.
- For phased delivery, ask separately whether clean phases may be staged and committed automatically. Only an explicit yes is standing authorization; plan approval alone is not.
- Treat an agent's report as a claim. Re-read changed regions or run a deterministic check before reporting success.
- Respect the parent session's sandbox and live permission mode; custom-agent defaults cannot weaken a stricter parent policy and a permissive parent can override agent defaults.

## Detailed procedures

- `references/agent-roster.md`: routing, model tiers, boundaries, and dispatch format.
- `references/dispatching-code-developer.md`: writer brief, status handling, and warm-agent recovery.
- `references/phased-execution.md`: multi-phase entry criteria, worktrees, TDD, reviews, and commits.
- `references/cache-and-memory.md`: cache freshness and mediated memory writes.
- `references/skill-staleness-audit.md`: post-change guidance audit.
- `references/rule-capture.md`: durable lesson placement.
- `references/adding-a-subagent.md` and `references/domain-expert-template.md`: extend the roster.
- `references/subagent-best-practices.md`: Codex capability boundaries and sourced rationale.

## Gotchas

- Codex custom agents do not provide Claude-style `skills:` preloading or scoped agent-memory grants. Agent instructions must read skill and memory files explicitly; read-only memory updates are persisted through `bulk-editor`.
- `web_search = "disabled"` and explicitly disabled effective MCP transports are the strongest native per-agent web restrictions, but hosted tools do not have a universal custom-agent allowlist. Keep the instruction boundary and validate role discovery after installation.
- Keep writer file sets disjoint if they run concurrently. Otherwise serialize writers or isolate them in orchestrator-created worktrees.
- A review finding never chains directly into an automatic fix.

## Keep in sync

- `.codex/agents/*.toml` and `references/agent-roster.md`
- `references/project-routing.md` and installed project/domain skills
- Writer output contracts and `references/dispatching-code-developer.md`
- Steps 6-8 and their three procedure references
