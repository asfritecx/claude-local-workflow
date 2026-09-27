# Playbook: refactor

**Role:** you own behavior preservation. A refactor that changes behavior is a feature or a bug, so it can't be reported as a refactor.

## Steps (copy into todos; mark any you skip `skip: <reason>`)

1. **Name the goal.** Say what gets simpler, and measure it: fewer call sites, fewer lines, one owner instead of three.
2. **Pin the behavior first.**
   - Find the existing tests that cover the code.
   - Where coverage is thin, add characterization tests that record current behavior, including quirks.
3. **Subtract before adding** (`references/principles.md`). Look for code to delete or merge before introducing a new abstraction.
4. **Map the callers.** Grep every call site. A reader can digest them when there are many.
5. **Migrate in one wave.**
   - Move every caller.
   - Delete the old API in the same change. Don't leave shims unless the user asks for a staged migration.
6. **Verify.**
   - The characterization tests pass unchanged.
   - `<your typecheck>`, `<your lint>` and `<your unit tests>` pass.
7. **Review gate.** Ask `code-reviewer` specifically for behavior changes.
8. **Judge the result.** If the code isn't easier to read, revert your own edits and say so. Revert them by hand; never use broad git restore.

## Done when

- Behavior is pinned by tests that pass before and after.
- The old API is gone.
- The simplicity goal is measurably met.

## Reply shape

- **Before → after**, with the measurements.
- **Behavior evidence:** which tests pin it.
- **Callers migrated.**
- **Review dispositions.**
- **Anything deliberately left.**
