# Independent review gate

Run review after each code-changing wave once the implementing thread has inspected the diff and completed proportionate checks.

## Reviewers

- `code-reviewer` finds correctness defects, security problems, regressions, missing tests, and breaches of the project's standing invariants (`<your project's standing invariants>`).
- `adversarial-reviewer` challenges a material design or implementation approach. Dispatch it for a design choice, a schema change, a security-sensitive path, or a concurrency or caching boundary, or when the user asks to challenge the approach. Give it one or two task-specific questions; do not bias it with the first reviewer's conclusions.

When both apply, spawn them as independent bounded tasks with non-overlapping objectives. Use `fork_turns: "none"` and a self-contained brief for each profile-pinned reviewer, or a deliberately bounded positive value when limited context is necessary. Each reviewer has a configured read-only default and a behavioral contract not to edit; it should derive the delta from git, read the relevant project skills and explicit rules, and return severity-ranked findings with file references and concrete failure scenarios.

Verify the effective child model, reasoning effort, and sandbox before recording the reviewer profile when runtime metadata exposes them. Otherwise record the configured profile and dispatch overrides, and mark the effective profile unavailable. A parent or live runtime override may broaden the sandbox despite the TOML default. When filesystem-enforced read-only review is required, dispatch from a read-only parent or runtime; report whether the effective child sandbox was independently observable.

Brief shape:

```text
Review the current uncommitted delta for <objective>.
Scope: <files or comparison base>.
Read: AGENTS.md, .agents/skills/<skill>/SKILL.md, and <explicit rule paths>.
Focus: <task-specific risks>.
Return findings only, ordered by severity. For each finding include evidence, a failure scenario, and the smallest defensible fix. State no findings when clean. Do not edit files.
```

## Triage and disposition

The main thread verifies every finding against the code, then sorts it into a bucket and records who raised it (reviewer@model):

| Bucket | Disposition |
|---|---|
| Act on | `confirmed` |
| Consider | `confirmed` or `deferred`, with a reason |
| Noted | `deferred` |
| Dismissed | `rejected`, naming the filter that dismissed it |

**Filters for dismissal:**
- nitpick gravity;
- hypothetical rather than actual;
- premature abstraction;
- "I would have done it differently";
- missing context the reviewer didn't have.

**Never dismissed by default:** findings about security, auth, encryption or other data-protection boundaries, migrations, money arithmetic, concurrency, or `<your project's invariants>`.

**Agreement map.** When two or more reviewers ran, note the overlap. A finding only one reviewer raised needs your own check.

List the dismissed findings in the finish report.

**Verdict binding.** Record `git rev-parse --short HEAD`, `git diff HEAD | shasum -a 256` and the content hashes of the untracked files (`git ls-files -z --others --exclude-standard | xargs -0 -r shasum -a 256`) beside each disposition table and each check. Take the snapshot before the review and again after it; a difference means the review saw a moving tree. A later edit to the reviewed files voids the verdict.

In the Claude runtime the same trigger that adds `adversarial-reviewer` also adds a second-model rerun of the `code-reviewer` brief. Codex has no equivalent lane configured. Fix confirmed issues that fall within the user's authorized scope, rerun affected checks, and seek another independent pass when the fix materially changes behavior.

Do not use review as an automatic approval stop. Ask the user only when a finding exposes a product decision, destructive action, or authority not already granted. Documentation-only changes may use a lighter editorial check, but code changes always receive the independent defect pass.
