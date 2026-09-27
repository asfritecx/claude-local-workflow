# Playbook: review

**Role:** you own the verdict, not the fixes. The user asked for a judgment on existing work, such as a branch, a diff, a PR or a design.

## Steps (copy into todos; mark any you skip `skip: <reason>`)

1. **State the intent.**
   - What the change is supposed to do.
   - What scope to review: the dirty tree, including untracked files, or `<base>...HEAD`. Watch for the dirty-tree-vs-base-ref trap in `references/review-gate.md`.
2. **Bind the tree state:** HEAD, the diff hash, and the untracked-file list.
3. **Run the panel in one message:**
   - `code-reviewer` at its pinned tier;
   - `code-reviewer` with `model: "fable"` (or another model family than your session's) when the second-opinion trigger applies;
   - `adversarial-reviewer` when the change embodies a design choice.

   Brief each one independently, with no author rationale and no other reviewer's findings.
4. **Verify every finding in code yourself.**
5. **Triage** into Act on / Consider / Noted / Dismissed, apply the filters, and build the agreement map (`references/review-gate.md`).
6. **Deliver the verdict.** Fix things only if the user asks. If they do, switch to the bug-fix or feature playbook for the fixes.

## Done when

- Every finding has a bucket, a disposition, a reason and a Raised-by entry.
- Dismissed items are listed.
- The verdict names the tree state it covers.

## Reply shape

- **Verdict**, in one line.
- **Act on**, then **Consider**, then **Noted**, each with `path:line` and the failure scenario.
- **Dismissed**, with the filter for each.
- **Agreement map.**
- **Tree state reviewed.**
