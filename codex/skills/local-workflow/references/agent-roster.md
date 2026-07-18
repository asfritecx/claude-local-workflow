# Agent Roster and Dispatch

Load before the first delegation in a `local-workflow` run.

## House agents

| Agent | Model / effort | Boundary | Use for |
| --- | --- | --- | --- |
| `code-digester` | `gpt-5.6-luna` / `max` | read-only, no web/MCP | Default code, documentation, or skill digest. |
| `research-specialist` | `gpt-5.6-sol` / `medium` | read-only repo; live web + approved research MCP only | Current vendor docs, library APIs, versions, migrations, CVEs, and standards. |
| `deep-analyst` | `gpt-5.6-sol` / `high` | read-only, no web/MCP | Cross-file traces, architecture, difficult debugging, and independent review. |
| `code-developer` | `gpt-5.6-terra` / `high` | workspace writer, no web/MCP | Authored features, fixes, refactors, integrations, and tests. |
| `bulk-editor` | `gpt-5.6-luna` / `high` | mechanical workspace writer | Exact old-to-new edits, insertions, deletions, and exact new-file content. |
| `skill-auditor` | `gpt-5.6-sol` / `medium` | read-only, no web/MCP | Cross-domain post-change skill, agent, memory, and `AGENTS.md` staleness. |
| `localworkflow-sync` | `gpt-5.6-luna` / `max` | read-only, no web/MCP | Workflow/roster drift and creating domain-expert specifications. |

Installed projects may add `<project>-<domain>-expert` agents. Prefer one when the thread is squarely in its domain; otherwise use `code-digester`.

## Routing rules

- External or current facts always go to `research-specialist`. Other agents may use a fresh, version-matched cache entry and must report an uncached need as `RESEARCH_GAP`.
- A change that still requires a design, wording, or API decision goes to `code-developer`. A fully decided change goes to `bulk-editor`.
- Writers run one at a time unless target file sets are provably disjoint. For overlapping or risky parallel writes, create separate Git worktrees before dispatch.
- Use a fresh `deep-analyst` for independent review; never ask the writer to be the final evaluator.
- Ask the live agent system for available capacity. Start every independent agent before waiting, but never assume a fixed thread count.

## Dispatch contract

Give each agent one bounded task:

```text
CONTEXT: <goal, decision being supported, and why it matters>

READ FIRST:
- <applicable AGENTS.md and .agents/skills/.../SKILL.md paths>
- <specific code/docs/cache paths>

SCOPE: <what is included and explicitly excluded>

DELIVERABLES:
1. <structured item>
2. <structured item>

Return distilled facts with a complete relative path and line number for every
repository claim. Quote exact text where fidelity matters. Separate confirmed
facts, inference, gaps, and external claims. Cite a direct source URL for every
external claim.
```

For a writer, replace the read-only framing with the brief in `dispatching-code-developer.md`.

## Report verification

- Check that all deliverables are present and scoped.
- Reject malformed evidence, unverified external claims, and unexplained expansion.
- Independently inspect mutations with `git diff`, targeted reads, tests, or builds.
- On a gap, follow up with the warm agent or dispatch a fresh specialist; do not fill the gap from assumption.
