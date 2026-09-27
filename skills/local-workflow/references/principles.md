# Principles, each with the trigger that applies it

Ten working principles, adapted from pstack's principle skills. Each one fires on a trigger, not on every task. Name a principle in a reply only where it changed a decision.

| Principle | Trigger | Working check |
|---|---|---|
| **prove-it-works** | Before saying "done". | Run the check on the real surface and record the verification level (`references/brief-contract.md`). A type check doesn't prove UI behavior; a unit test doesn't prove a migration. |
| **encode-lessons-in-structure** | Writing the same instruction a second time, or capturing a rule. | Could a test, lint rule, type, hook or script enforce it? Then encode it and delete the prose (`references/rule-capture.md` rung 0). |
| **sequence-verifiable-units** | Multi-step work. | Order the work so each unit can be checked before the next starts. A unit you can't verify on its own is too big or badly cut. |
| **separate-before-serializing-shared-state** | Dispatching parallel writers, or two streams touching one file, table or register. | Give each writer a disjoint file set. If two streams need the same state, split the state first or run them in order. Disjoint files make the tree safe, not cross-file claims (`.claude/rules/worktree-agent-dispatch.md`). |
| **guard-the-context-window** | Bulk reading, big cribs, long runs. | Delegate reads to a digester and hand writers digests, not pointers into long files (`.claude/rules/writer-brief-crib-digests.md`). Shard briefs over ~15–20 files or ~100KB. |
| **attack-the-premise** | The second failed fix, or the second retry with the same failure. | Stop. Write down the assumption both attempts shared, and test that assumption instead of trying a third variant. |
| **subtract-before-you-add** | Adding structure, prose, a helper or a rule. | Look for something to delete or merge first. New prose must change a decision; new code must not duplicate an existing helper. |
| **fix-root-causes** | Debugging. | Confirm the mechanism with runtime evidence before fixing. Grep for the same pattern elsewhere. A guard that hides a symptom is not a fix. |
| **make-operations-idempotent** | Retries, resumes, restore paths, re-dispatches, migrations. | Would running it twice be safe? If not, add a check-before-write or a marker, or say explicitly why it can't be retried. |
| **boundary-discipline** | Inputs crossing a trust boundary: API handlers, request bodies, webhooks, file uploads, model output. | Validate at the boundary (with `<your project's validation layer>`), then trust the types inside. Don't re-validate deep in the call chain, and don't skip the boundary. |

## Keep in sync

- The Codex twin (if installed) is `.agents/skills/local-workflow/references/principles.md`.
- Playbooks cite these principles by name, so rename a principle in both places.
