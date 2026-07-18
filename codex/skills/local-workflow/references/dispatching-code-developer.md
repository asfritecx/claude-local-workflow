# Dispatching Code Developer

Use this brief after readers have already identified the relevant behavior and patterns. Do not ask the writer to rediscover the subsystem.

## Brief template

```text
CONTEXT: <user-visible intent and why it matters>

DIGESTED FINDINGS:
- <confirmed fact with path:line>
- <existing pattern to mirror with path:line>

RESEARCH CACHE POINTERS:
- <fresh .codex/agent-memory/research-specialist/... topic files>
- or: no external APIs touched

READ FIRST:
- <applicable AGENTS.md files>
- <applicable .agents/skills/.../SKILL.md files>

TARGET FILES: <exact create/modify/delete paths>

SCOPE: <what to change and what must remain untouched>

ACCEPTANCE CRITERIA:
- <observable behavior or exact command>

CONSTRAINTS: <versions, interfaces, security boundaries, and known APIs>
```

For a phase, append the exact phase interfaces and TDD steps from `phased-execution.md`.

## Writer status contract

The first line must be one of:

- `STATUS: DONE`
- `STATUS: DONE_WITH_CONCERNS`
- `STATUS: NEEDS_CONTEXT`
- `STATUS: STOPPED`

The report then includes:

1. Files created, modified, or deleted and one-line purpose.
2. Changed regions with complete relative `path:line` evidence.
3. Every verification command and its complete relevant output; label failures or warnings introduced versus pre-existing.
4. Research-cache provenance, or `no external APIs touched`.
5. Any unverified API use; normally none because the writer stops on a gap.
6. Any `MEMORY_WRITE` specification proposed, or none; the writer never edits agent memory directly.
7. Concerns, stops, or open questions.
8. Per-guidance accounting: each named `AGENTS.md`/skill path and the convention applied.

## Status handling

- `DONE`: independently verify the diff and proceed to the review gate.
- `DONE_WITH_CONCERNS`: resolve correctness or scope concerns before the gate.
- `NEEDS_CONTEXT`: fill the named gap. For external APIs, dispatch `research-specialist` as implementation-bound, persist its cache spec through `bulk-editor`, then follow up with the writer.
- `STOPPED`: change the brief, obtain the missing decision, or split the task before continuing.

Never resend an unchanged brief after a non-DONE status.

## Warm-agent reuse and recovery

Use follow-up messaging when a writer or reader still holds valuable context. Cap substantive follow-ups at two, exceptionally three. Then dispatch a fresh agent with the distilled findings.

If a warm agent fails or overflows:

1. Inspect the working tree; do not trust the last progress message.
2. Inventory each scoped item by an exact marker.
3. Send already-decided remainder to `bulk-editor`.
4. Send remaining judgment work to a fresh `code-developer`.

The main thread always verifies the resulting tree.
