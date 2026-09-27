# Playbook: bug fix

**Role:** you own the diagnosis and the proof. A fix without a reproduced failure and a passing re-run is a guess.

## Steps (copy into todos; mark any you skip `skip: <reason>`)

1. **Reproduce.**
   - Get a failing command, test or UI path. Record it verbatim.
   - If it won't reproduce, say so and gather runtime evidence before theorizing.
2. **Narrow.**
   - List hypotheses and eliminate them by binary search: bisect the input, the code path, or `git bisect` across commits.
   - Use the matching `<prj>-<domain>-expert` (if one exists) or `deep-analyst` for the trace when it's cross-file.
3. **Confirm the mechanism** with runtime evidence: instrument, log or query rather than infer. Label it `ran`.
4. **Write the failing test or repro first.**
   - Use red-green. Skip only when there is genuinely no testable surface, and say which fallback check replaces it.
   - For behavior that depends on real backing services (database, queue, external API), use your integration-test harness (`<your integration tests>`).
5. **Fix the root cause** (`references/principles.md`: fix-root-causes).
   - Hand it to a writer via `references/dispatching-code-developer.md` when the fix needs design.
   - Hand it to `bulk-editor` when it's fully specified.
   - Or edit it yourself when it's small.
6. **Grep for the same pattern elsewhere.** Fix it or list the other sites.
7. **Verify.** Paste the failing-then-passing output verbatim, then run `<your typecheck>`, `<your lint>` and `<your unit tests>` as needed.
8. **Review gate** (`references/review-gate.md`), with the verdict bound to the tree state.
9. **Keep guidance current.** If the bug exposed a durable invariant, consider a rule (`references/rule-capture.md`).

**Stop rule:** after two failed fixes that share one premise, stop and attack the premise before trying again.

## Done when

- The original repro passes.
- A regression test exists, or its absence is justified.
- Sibling sites are handled.
- The review dispositions are recorded.

## Reply shape

- **Root cause**, with evidence.
- **Fix:** files and regions.
- **Proof:** the failing-then-passing output.
- **Sibling sites.**
- **Verification level.**
- **Review dispositions.**
- **Residual risk.**
