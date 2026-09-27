# Capturing durable rules

Use `docs/agent-rules/` for small, project-specific instructions that should be explicitly loaded whenever matching code is touched. `docs/agent-rules/INDEX.md` is the routing surface.

Capture a rule when all are true:

- a confirmed defect or repeated gotcha reveals a non-obvious invariant;
- the lesson is stable and tied to identifiable paths or symbols;
- existing `AGENTS.md`, skills, rules, and code comments do not already cover it;
- forgetting it would cause a concrete correctness, security, privacy, or operational failure;
- it changes a decision: a future agent reading it would act differently;
- it has recurred at least twice, or a single occurrence did real damage. One-off surprises belong in the run's trail.

Structure beats prose. If a test, lint rule, type, hook or script could enforce the lesson, encode it there and write no prose, or delete the prose it replaces.

Prefer updating the owning domain skill when the guidance is broad domain knowledge. Prefer a code comment when the invariant belongs beside one implementation. Avoid rules for generic advice, personal style, one-off history, or facts easily derived from the current code.

A rule should contain a short title, explicit load conditions, the required behavior, the failure it prevents, and current file anchors. Add it to the index with a concise route such as paths, subsystem, or trigger terms. Agents must read the index and selected rule explicitly; there is no automatic path-scoped injection.

A newly captured or updated rule is written to both runtimes: `docs/agent-rules/<x>.md` (plus its `docs/agent-rules/INDEX.md` row) and the Claude twin `.claude/rules/<x>.md` with `paths:` frontmatter.

## Reflect pass at multi-phase closeout

At the close of a multi-phase run, spawn two read-only reviewers in one wave.
- **Brief:** the run's `decisions.tsv`, its ledger if there is one, and the disposition tables.
- **Lenses:** one takes a judgment lens (which decisions held, which were reversed, what cost the most rework). The other takes a divergent lens (what the run's shape assumed without needing to, and which lesson would change the next run's first decision). Where the runtime allows it, give the second reviewer a different model.
- **Evidence:** neither reads transcripts; the trail and the tree are the evidence.
- **Output:** proposals sorted into Accepted, Rejected and Backlog. Each is a rule edit, a skill edit, a mechanism, or a description tune for a skill that failed to trigger.
- **Approval:** the user approves before anything is edited.

Readers and reviewers propose rule text with evidence. The main thread or an assigned writer checks for duplicates and applies it within scope. Revisit a rule when its anchored implementation changes, and remove it when the invariant no longer exists.
