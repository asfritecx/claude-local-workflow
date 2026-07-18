# Phased Execution

Use this protocol for complex code-authoring runs. It replaces the single-writer path, not the eight-step workflow.

## Entry criteria

Use phases when any condition holds:

- The change spans at least two subsystems.
- Roughly four or more files each carry a design decision.
- Schema, backend, and UI changes stack into one delivery.
- More than one `code-developer` dispatch is expected.

## Run-start authorization

Before phase 1, present:

1. Phase names and one-line scope.
2. Exact files, consumed/produced interfaces, acceptance criteria, and TDD steps per phase.
3. Branch/worktree plan.
4. A separate question: `May clean phases be staged and committed automatically after their review gate passes?`

Only an explicit yes to item 4 authorizes staging and committing. Approval of the technical plan alone does not.

## Phase design

A phase is the smallest testable slice worth an independent review. Fold scaffolding into the first phase that consumes it. Do not leave placeholders, unspecified error handling, stubs, or TODO deliverables.

Each phase defines:

- Files to create, modify, delete, and test.
- Interfaces consumed from earlier phases and produced for later phases.
- Testable acceptance criteria.
- Red-green steps, or a stated non-testable fallback.

## Per-phase cycle

1. Pre-warm external API research and persist the cache spec if needed.
2. Dispatch a fresh `code-developer` with the phase brief.
3. Require red-green: failing test, observed failure, minimal implementation, observed pass.
4. Independently verify the diff and affected checks.
5. Run a fresh `deep-analyst` defect review; add an adversarial focus for design/security decisions.
6. Any finding triggers a stop: present it with your judgment and wait for the user's disposition. Fixes go through a fresh or warm writer, then the gate repeats.
7. A clean phase is staged and committed only when run-start commit authorization exists. Use `(phase N/total) <summary>` and record the SHA.
8. Advance automatically only after the gate and any authorized commit complete.

After the final phase, synthesize the run and execute documentation audit/rule capture once over the accumulated change.

## Branch and worktree policy

- Never run phased delivery directly on trunk/main.
- Use a feature branch.
- Use an orchestrator-created worktree when the starting tree is dirty, the user requests isolation, or concurrent writers could overlap.
- Do not rely on a custom-agent field for worktree isolation; Codex custom agents do not expose Claude's `isolation: worktree` equivalent.

## Ledger

Use `.codex/run-ledgers/<run-id>.md`:

```text
Phase N: done - <files>, self-check <result>, review <result>, commit <sha|not-authorized>
```

Record non-testable fallbacks and user waivers inline. Trust the ledger plus Git state after context compaction.
