# Deploy the local-workflow kit into a project (Claude Code)

**This is a run-once bootstrap runbook. Whoever runs it (a human or an AI agent) deletes the whole `claude-local-workflow/` folder at the end (Cleanup).** For Codex, follow `DEPLOY-CODEX.md` instead or as well.

The kit installs the `local-workflow` skill, the shared `house-agent-contract` skill, nine house agents, three workflow rules and a `docs/agent-knowledge/` scaffold into a project. The git guard hook is optional. There are **two paths**: a greenfield repo needs only the baseline; an existing codebase also gets domain experts. If you are an AI agent running this, do Step 0, then that path's steps in order.

## What gets installed where

| Kit path | Installs to | Notes |
|---|---|---|
| `skills/local-workflow/` | `.claude/skills/local-workflow/` | Router, contracts, roster; `references/` holds the brief contract, review gate, principles and nine playbooks. |
| `skills/house-agent-contract/` | `.claude/skills/house-agent-contract/` | Preloaded into every read-only agent via `skills:`. Not user-invocable. |
| `agents/*.md` | `.claude/agents/` | Nine house agents (see README roster). |
| `rules/*.md` | `.claude/rules/` | `agents-roster.md` is the only model/effort tier table. |
| `knowledge/` | `docs/agent-knowledge/` | Shared advisory notes that agents propose and the main thread applies. Replaces per-agent memory. |
| `hooks/` *(optional)* | `.claude/hooks/` | Git guard: blocks stash / restore / reset / `checkout --` and similar in a tree other agents share. |

README.md, LICENSE, `docs/` and `codex/` are not installed by this runbook.

---

## Step 0: pick the path

- Quick signals: `git log --oneline | head` (shallow or empty history suggests greenfield) and a count of source files.
- Confirm with the user: **"Is this a greenfield project (little or no code yet), or an existing codebase you want domain experts for?"**
- Ask once, too: **"Install the optional git guard hook?"** It needs `python3` (its test runner also needs `jq` and git 2.28 or newer) and blocks the listed git commands for you and every agent; you can still run them yourself with `! git …`.

---

## Path A: greenfield (baseline only)

1. **Pre-flight.** `mkdir -p .claude/skills .claude/agents .claude/rules docs/agent-knowledge`. If any target file already exists (`.claude/skills/local-workflow/`, a same-named agent or rule, `docs/agent-knowledge/INDEX.md`), back it up or ask; the copies below overwrite.
2. **Install skills.** `cp -R claude-local-workflow/skills/local-workflow claude-local-workflow/skills/house-agent-contract .claude/skills/`
3. **Install agents.** `cp claude-local-workflow/agents/*.md .claude/agents/`
4. **Install rules.** `cp claude-local-workflow/rules/*.md .claude/rules/`
5. **Install the knowledge scaffold.** `cp -R claude-local-workflow/knowledge/. docs/agent-knowledge/`
6. **Optional git guard.**
   - `mkdir -p .claude/hooks && cp claude-local-workflow/hooks/* .claude/hooks/`
   - Merge the entry from `.claude/hooks/settings-snippet.json` into `.claude/settings.json` under `hooks.PreToolUse` (keep any existing entries), then delete the snippet file.
   - Test it: `bash .claude/hooks/run-guard-tests.sh .claude/hooks/cases.txt` must end with `fail=0`.
7. **Fill the placeholders.**
   - `.claude/skills/local-workflow/SKILL.md` Skill map: replace the `<your domain A>` / `<your domain B>` rows with the project's real skills (often just the research row at first).
   - `.claude/agents/code-reviewer.md`: replace `<your project's standing invariants>` with the handful of invariants a reviewer must check on every delta, or delete the block.
   - `<your typecheck>`, `<your lint>`, `<your unit tests>` in the skill: the project's real commands.
   - `grep -rn '<your ' .claude docs/agent-knowledge` lists what is left.
8. **Models.** Agents ship with aliases (`model: opus`; `model: fable` for `deep-analyst`) and explicit `effort:`. To hold a tier regardless of the session's model, pin full model IDs and update `.claude/rules/agents-roster.md`, which explains the tradeoff.
9. **Restart** the session so the new agents, skills and hook register, then smoke-test: dispatch `code-digester` on one small file and check its report ends with `CITATION_CHECK: pass`.
10. **Later, as subsystems emerge:** add a `<prj>-<domain>-expert` per major subsystem (see Path B step 3), then restart.
11. **Clean up.**

---

## Path B: existing project (baseline plus domain experts)

1. **Ask which domains to cover first** ("Which subsystems do you want dedicated expert agents for?", for example `billing`, `auth`). Map each to its code and, if one exists, its skill under `.claude/skills/<domain>/`.
2. **Do Path A steps 1–9.**
3. **Branch a domain expert per chosen domain.** Pick a short project prefix `<prj>` (for example `shop`, `api` or `app`) and reuse it. For each domain, either:
   - **Guided (recommended):** dispatch `localworkflow-sync`. It reads `.claude/skills/local-workflow/references/domain-expert-template.md` plus the domain's skill and code, and returns the new agent file, its `docs/agent-knowledge/domain/<domain>.md` note, and the Skill map, roster and `docs/agent-knowledge/INDEX.md` edits. Apply them (a `bulk-editor` pass works well).
   - **By hand:** copy the template to `.claude/agents/<prj>-<domain>-expert.md`, fill every `<…>` placeholder, and add its Skill map row, its row in `.claude/rules/agents-roster.md` and its domain note.
4. **Restart** so the experts register.
5. **Digest the codebase.** Invoke `/local-workflow` with an investigation task; it fans out `code-digester` and the new experts. Apply the knowledge-note proposals they return to `docs/agent-knowledge/` yourself (agents propose; the main thread applies).
6. **Verify.** `ls .claude/skills/local-workflow/references/playbooks .claude/agents .claude/rules docs/agent-knowledge` shows the nine playbooks, nine house agents plus each expert, three rules and the knowledge scaffold. Then clean up.

---

## Optional: SessionStart reminder

A SessionStart hook can echo one line so every session opens with the contract in view, for example:

```
local-workflow: main thread owns scope, decisions and the final answer; delegate bounded work to house agents (.claude/agents); code-reviewer after code changes; shared knowledge in docs/agent-knowledge (propose, then apply)
```

---

## Cleanup (both paths)

```
rm -rf claude-local-workflow
```

Nothing installed depends on the kit folder.
