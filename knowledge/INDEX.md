# Agent knowledge index

These notes preserve reusable evidence and investigation shortcuts for both Codex and Claude workflows. They are not native context injection: an agent must open the relevant index and note explicitly.

Knowledge is advisory. Treat historical project notes as leads, verify them against the current branch and source, and follow current project instructions (CLAUDE.md or AGENTS.md), project skills, and rules when they differ. External research is version-bound; recheck its package/runtime match and freshness before implementation (see the verify-before-use checklist in [research/README.md](research/README.md)).

Readers and specialist agents may propose corrections or new notes. Only the main thread or a writer with explicit ownership applies them. Keep source provenance, remove secrets and sensitive data values, and avoid copying implementation logs or current-state inventories into this layer.

## Topics

- [Engineering](engineering/README.md) — reusable implementation lessons: `<your typing/test-narrowing notes>`, `<your integration-harness notes>`, `<your implementation shortcuts>`.
- [Domain](domain/README.md) — investigation leads per area of the project: `<your domain areas>`.
- [External research](research/README.md) — versioned, dated findings about external libraries and runtimes: `<your libraries>`, plus Claude Code subagent/model configuration.

When you add a note, add its row to the matching README in the same pass, and give it a date and (for research) a TTL.
