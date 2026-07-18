# Capturing Durable Lessons

Use after the independent review and post-change guidance audit.

## Placement ladder

1. Update an existing applicable nested `AGENTS.md` rule when it already owns the topic.
2. Update the owning project skill when it describes the subsystem or workflow.
3. Add a small `AGENTS.md` in the narrowest common subtree when the lesson is stable for every file below it.
4. If only non-contiguous path globs could scope the lesson safely, propose a focused skill or root-guidance change instead of creating over-broad nested instructions.

Codex has no direct equivalent to Claude's `.claude/rules/` path-glob activation. Directory-scoped `AGENTS.md` is the default replacement.

## Worthiness bar

All conditions must hold:

- The lesson outlives the incident that revealed it.
- A future agent working in the scope could plausibly repeat the mistake.
- It is not already recorded in applicable `AGENTS.md`, skills, or enforced tooling.
- The placement does not broaden the instruction beyond files it should govern.
- It contains no personal preference, secret, credential, personal data, or transient task state.

## Consent

- Review-derived proposals travel with the review finding and require the user's disposition before being applied.
- Mid-run implementation quirks are proposed at the next natural stop. Do not silently change root or nested `AGENTS.md`.

## Shape

Keep the addition concise and imperative:

```markdown
## <Topic>

- <What must or must not happen.>
- <Why the failure is non-obvious, if needed.>
- <Correct pattern and a stable local example.>
```

Send approved exact content to `bulk-editor`, verify the diff, and include the affected `AGENTS.md` in future staleness audits.
