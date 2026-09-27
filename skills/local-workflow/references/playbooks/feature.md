# Playbook: feature

**Role:** you own the design and the integration. Writers build units; you decide the shape and prove the whole works.

## Steps (copy into todos; mark any you skip `skip: <reason>`)

1. **Scope.**
   - Check the branch (your project's branch notes in CLAUDE.md, if any).
   - Pick the skills from the Skill map in `SKILL.md`.
   - Digest the touched subsystems with readers.
2. **Name the data shape first:** the tables, columns, types and interfaces the feature adds or changes. Write it as an interface block.
3. **Run the throughput checkpoint.** Write these four todos, and mark any that don't apply `n/a: <reason>`:
   - blocking first steps;
   - independent workstreams;
   - shared mutable state;
   - the smallest safe decomposition.
4. **Settle factual questions by prototype, not by asking.**
   - If an open question has an observable answer, run a throwaway experiment in the scratchpad or a worktree and report the evidence.
   - Ask the user only about genuine preferences or material choices.
5. **Design it twice, but only when the design is contested.**
   - Sketch two approaches. The second comes from `code-digester` with a per-call `model: "fable"` (or another model family than your session's), or from `deep-analyst`, given the same brief.
   - Screen both sketches for shallow modules, information leakage and pass-through methods, then pick one and say why.
6. **Size check.** If it meets the multi-phase entry criteria, switch to `references/playbooks/multi-phase.md`.
7. **Build** through the brief contract.
   - Use `code-developer`, or the matching specialist writer if your project has one (for example schema, UI or infra).
   - Pre-warm research for any external library.
8. **Verify on the matching surface:**
   - UI: the browser, via a browser-automation tool or Playwright, including your project's accessibility checklist (`<ui-skill>`), if it has one.
   - Storage: read the value back.
   - Unit logic: tests.
9. **Run the review gate.** Add `adversarial-reviewer` and the model-diverse second opinion when the trigger applies.
10. **Keep guidance current:** staleness audit and rule capture.

## Done when

- The acceptance criteria pass on the right surface.
- The review dispositions are recorded and bound to the tree state.
- The docs are audited.

## Reply shape

- **What shipped**, framed by the user-facing outcome.
- **Design choice and why.**
- **Files.**
- **Verification level per surface.**
- **Review dispositions**, with who raised each.
- **Not verified.**
- **Follow-ups.**
