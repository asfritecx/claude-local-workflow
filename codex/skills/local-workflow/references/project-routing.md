# Project Routing

Customize this file during installation. Scan available `.agents/skills/*/SKILL.md` metadata and applicable `AGENTS.md` files; list only guidance that materially applies to a thread.

| When the task touches | Read first / dispatch |
| --- | --- |
| `<domain-a>` | `<AGENTS.md or skill paths>`; dispatch `<project>-<domain-a>-expert` if installed |
| `<domain-b>` | `<AGENTS.md or skill paths>`; otherwise use `code-digester` |
| Cross-cutting architecture or security | Root `AGENTS.md` plus the project's architecture/security sources; use `deep-analyst` when reasoning is hard |
| External/current facts | `research-specialist` only; check `.codex/agent-memory/research-specialist/MEMORY.md` first |

Keep this table as a routing index. Do not duplicate whole skill descriptions or domain invariants here.
