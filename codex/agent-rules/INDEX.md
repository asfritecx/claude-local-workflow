# Agent rule index

These Markdown rules do not load automatically. Before changing a file, match its repository-relative path against the routes below and read every matching rule. Also load the relevant project skills from `.agents/skills/` and treat `AGENTS.md` as the repository-wide baseline.

The rules below are the Codex twins of the workflow rules in `.claude/rules/`. They mirror shared facts only; model and effort tiers stay runtime-specific.

| Rule | Load for these paths or situations | Disposition |
|---|---|---|
| [agents-roster.md](agents-roster.md) | `.codex/agents/*.toml`; `.agents/skills/local-workflow/**` | Adapted from `.claude/rules/agents-roster.md` for the Codex roster and collaboration API. |
| [worktree-agent-dispatch.md](worktree-agent-dispatch.md) | Any worktree or multi-checkout subagent dispatch | Adapted for Codex shared-filesystem collaboration. |
| [writer-brief-crib-digests.md](writer-brief-crib-digests.md) | Writer briefs involving large reference documents, mutable line anchors, or frozen public interfaces | Runtime-neutral writer-brief guidance, identical in substance to the Claude rule. |

When a new reusable invariant is added, give it explicit path or situation routing here. Keep source history in the rule when it explains a real failure mode, but keep runtime-specific model and orchestration policy in the local-workflow skill and agent definitions.
