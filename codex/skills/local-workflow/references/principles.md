# Principles and their triggers

Each principle applies on its trigger, not on every task. Name one in a reply only where it changed a decision.

| Principle | Trigger | Check |
|---|---|---|
| prove-it-works | Before saying "done". | Run the check on the real surface; record the verification level. |
| encode-lessons-in-structure | Writing an instruction a second time; capturing a rule. | Could a test, lint rule, type, hook or script enforce it? Encode it and delete the prose. |
| sequence-verifiable-units | Multi-step work. | Each unit is checkable before the next starts. |
| separate-before-serializing-shared-state | Parallel writers; two streams on one file or register. | Disjoint file sets. Otherwise split the state or serialize. |
| guard-the-context-window | Bulk reading; long runs. | Digest first. Give writers digests. Shard briefs over ~15–20 files or ~100KB. |
| attack-the-premise | The second failed fix or retry. | Write down the shared assumption and test it. |
| subtract-before-you-add | Adding structure, prose, a helper or a rule. | Delete or merge first. New prose must change a decision. |
| fix-root-causes | Debugging. | Confirm the mechanism with runtime evidence. Grep for the same pattern elsewhere. |
| make-operations-idempotent | Retries, resumes, restores, migrations. | Is running it twice safe? If not, add a check or say why. |
| boundary-discipline | Inputs crossing a trust boundary. | Validate once at the boundary (with `<your project's validation layer>`), then trust the types inside. |

The Claude twin is `.claude/skills/local-workflow/references/principles.md`.
