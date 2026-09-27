# Domain knowledge

Open only the note that matches the task. These are curated trace shortcuts from past investigations, not claims that an old implementation or bug still exists.

- `<domain-area>.md` — `<one-line scope>` (add a row per note; for example database and schema, authentication, core read/write paths, background jobs, UI and deployment)

Start with the matching project skill (`.claude/skills/` for Claude, `.agents/skills/` for Codex). Use these notes only when the skill does not answer the question or when the rationale behind an invariant matters. Verify every named function, migration, test, and status against the active branch before editing.
