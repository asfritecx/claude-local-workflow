# Post-change Guidance Audit

Run after every repository-changing workflow, once verification and independent review are complete.

## Establish scope mechanically

Use changed paths and key symbols to search:

- `.agents/skills/**`
- Applicable root and nested `AGENTS.md`
- `.codex/agents/**`
- Relevant `.codex/agent-memory/<agent>/**`

Memory directories for a touched domain are included even without a text hit. A zero-scope result requires pasted evidence: no skill/agent hits, no applicable nested guidance beyond files already checked, and no relevant memory files.

## Choose the auditor

1. Use the owning project-domain expert when exactly one domain owns the change.
2. Otherwise use `skill-auditor`.
3. Use `code-digester` only as a fallback and include the output contract below.

Never ask the writer to grade the guidance impact of its own work.

## Brief

```text
CHANGE SUMMARY: <what landed, why, files, renamed/added/removed interfaces>

AUDIT SCOPE:
- <skill, AGENTS.md, agent TOML, and memory paths>
```

The auditor must ground truth the actual diff, read every scoped document, and return:

1. `AUDIT: <n> read, <m> STALE, <k> flags`.
2. One `FRESH`, `STALE`, or `read; no bearing` entry per scoped file.
3. For each stale project skill, nested `AGENTS.md`, or custom agent: the exact stale statement, contradicting code `path:line`, and a minimal exact old-to-new specification.
4. Trigger checks for skill descriptions, agent descriptions, routing entries, and nested-guidance location after moves.
5. Flag-only findings for root `AGENTS.md` and memory owned by a different agent.
6. Gaps and the evidence needed to close them.

An owning expert may return a `MEMORY_WRITE` spec for its own memory. It remains read-only; `bulk-editor` persists the verified spec.

## Apply results

- Send exact specifications to `bulk-editor` and re-read the changed regions.
- Propose root `AGENTS.md` changes to the user; never apply them silently.
- Dispatch the owning expert for memory flagged by a cross-domain auditor.
- Patch falsified claims; do not opportunistically rewrite the whole document.
