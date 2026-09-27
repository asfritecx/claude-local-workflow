# Playbook: docs, skills, rules and agents

**Role:** you own reader load. Every line in a skill, rule or agent body is context some future session pays for, so keep only prose that changes a decision.

## Steps (copy into todos; mark any you skip `skip: <reason>`)

1. **Find the owner.** Work out which file owns the fact and change it there. Point to paths rather than restating them elsewhere.
   - Model tiers live only in `.claude/rules/agents-roster.md`.
   - Shared agent boilerplate lives only in `.claude/skills/house-agent-contract/SKILL.md`.
2. **Subtract first** (`references/principles.md`). Delete stale or duplicated prose before adding new prose. Ask whether the lesson could be a mechanism instead: a hook, script, test or lint rule (`references/rule-capture.md` rung 0).
3. **Edit.**
   - Anchor edits by verbatim text.
   - For many mechanical edits, send `bulk-editor` an exact old→new spec.
   - Hand wording that needs design to `code-developer`.
4. **Check structure:**
   - frontmatter keys are valid (skills: `name`, `description`, `user-invocable`, and so on; agents: see `references/adding-a-subagent.md`);
   - every relative link resolves;
   - no line-number back-references into files that are being edited.
5. **Write the Codex twin** (if you run the Codex mirror) for any shared fact: roles, boundaries, invariants or paths. The targets are `.agents/skills/`, `docs/agent-rules/` and `.codex/agents/*.toml`. Never mirror model or effort tiers.
6. **Review.**
   - `skill-auditor` for skills and rules.
   - `localworkflow-sync` for the workflow and agent layer, including the Codex mirror (if installed).
   - The matching `<prj>-<domain>-expert` for a single-domain skill, if one exists.
7. **Agent or hook changes need a restart.** Agent definitions have been observed not to hot-reload, and hook reload is unverified (`.claude/rules/agents-roster.md` § Reload caveat). Restart, then smoke-test.

If a skill misbehaves mid-task, note it and fix it as its own change after the current task, not in the middle of it.

## Done when

- Links and frontmatter check out.
- The twin is written.
- The audit is clean or its findings are dispositioned.
- A smoke test has run after the restart, for agent changes.

## Reply shape

- **What changed**, per file.
- **What was deleted.**
- **Twin status.**
- **Audit result.**
- **Restart and smoke-test status.**
