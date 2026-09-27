# Skill and guidance staleness audit

After implementation changes, check whether maintained project guidance still describes the code accurately.

## Scope

Search changed paths and key symbols across:

- `.agents/skills/**` for domain instructions and references;
- the explicit rule paths routed by `docs/agent-rules/INDEX.md`;
- relevant shared notes routed by `docs/agent-knowledge/INDEX.md`;
- `AGENTS.md` for root-level architecture claims.

Use the owning `<prj>-<domain>-expert` when one domain clearly owns the change. Use `skill-auditor` for cross-domain or unowned changes. Auditors are read-only: they return evidence and exact edit specifications. A writer or the main thread applies confirmed updates.

## Audit brief

```text
Audit project guidance after this code delta. Do not edit files.
Changed files/symbols: <list>
Read: <relevant skills, explicit rules, and knowledge notes>
For each document, return FRESH or STALE with code and documentation evidence.
For STALE items, provide an exact replacement or concise edit specification.
Flag root AGENTS.md separately.
Report coverage gaps and broken links.
```

Check descriptions as well as bodies: a technically correct skill can still be stale if its trigger text no longer routes the right work. Leave records that are clearly labeled archival intact; convert only active instructions to the current Codex runtime.

Apply confirmed documentation fixes within the already authorized implementation task. Do not claim that rule or knowledge files load automatically; agents reach them through their indexes and explicit dispatch instructions.
