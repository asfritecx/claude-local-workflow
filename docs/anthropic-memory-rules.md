# Claude Code memory & rules — research findings

Compiled 2026-07-07 from the official Claude Code memory documentation. This snapshot grounds the kit's post-change docs audit (loop step 7 / `agents/skill-auditor.md`): what the docs layer is made of, how `.claude/rules/` loads, and the official mandate to keep it current. Quotes are verbatim from the source.

## 1. The docs layer

Project instructions live in CLAUDE.md files (project root and `.claude/CLAUDE.md`) plus modular rule files under `.claude/rules/`. Rules exist to keep instructions topical and bounded — "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence. If your instructions are growing large, use path-scoped rules so instructions load only when Claude works with matching files."

## 2. `.claude/rules/` mechanics

- One topic per file, descriptive filenames (`testing.md`, `api-design.md`). "All `.md` files are discovered recursively, so you can organize rules into subdirectories like `frontend/` or `backend/`."
- **Unscoped rules** (no frontmatter) — "Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`."
- **Path-scoped rules** — YAML frontmatter with a `paths` list of globs. "Path-scoped rules trigger when Claude reads files matching the pattern, not on every tool use." Multiple patterns and brace expansion are supported:

  ```
  ---
  paths:
    - "src/**/*.{ts,tsx}"
    - "tests/**/*.test.ts"
  ---
  ```

- Symlinked-path matching requires Claude Code ≥ 2.1.198.

## 3. User-level vs project rules

"Personal rules in `~/.claude/rules/` apply to every project on your machine." They load BEFORE project rules — "giving project rules higher priority." Project rules are checked into version control; user-level rules are personal preferences.

## 4. The maintenance mandate

- "Consistency: if two rules contradict each other, Claude may pick one arbitrarily. Review your CLAUDE.md files, nested CLAUDE.md files in subdirectories, and `.claude/rules/` periodically to remove outdated or conflicting instructions."
- When to add an instruction — Claude makes the same mistake a second time; a code review catches something Claude should have known; you re-type the same correction across sessions; a new teammate would need the same context.
- The `/memory` command "lists all CLAUDE.md, CLAUDE.local.md, and rules files loaded in your current session."

## 5. What this means for the kit's audit

- **Rules are audit targets with edit specs.** They are topic-scoped docs whose technical claims are as falsifiable as a skill's, and the official guidance mandates removing outdated instructions. `skill-auditor` treats `.claude/rules/**/*.md` like skills — FRESH/STALE verdicts plus exact old→new specs.
- **Root CLAUDE.md, auto-memory, and `~/.claude/rules/` stay flag-only.** They are the user's curated/personal layer — the audit quotes stale claims, never specs direct edits.
- **`paths:` globs are part of the audit.** A renamed or moved directory silently orphans a path-scoped rule (it stops loading for the files it was written for) — the auditor checks globs still match after renames, mirroring its skill-description trigger check.
- **Rules are also the capture surface for new lessons.** Loop step 8 turns confirmed review findings and durable mid-run quirks into new path-scoped rules — §4's "when to add" heuristics are the bar; the working guide is `skills/local-workflow/references/rule-capture.md`.

## Sources

- https://code.claude.com/docs/en/memory (fetched 2026-07-07)
