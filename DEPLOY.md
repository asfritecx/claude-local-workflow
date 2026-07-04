# Deploy the local-workflow kit into a project

**This is a run-once bootstrap runbook. Whoever runs it (a human or an AI agent) should delete the whole `claude-local-workflow/` folder at the end (Cleanup).**

This kit installs the `local-workflow` orchestration skill plus its house agents into a project's `.claude/` tree. There are **two paths** — a greenfield repo needs only the baseline; an existing codebase also gets domain experts so it can be digested. If you are an AI agent running this, follow Step 0 to pick the path, then that path's steps in order.

## What's in the box

```
claude-local-workflow/
├── README.md                              ← repo overview (stays in the published kit; not installed)
├── DEPLOY.md                              ← you are here; delete after deploying
├── LICENSE                                ← MIT license (stays in the kit repo; not installed)
├── docs/
│   ├── anthropic-subagent-best-practices.md ← sourced Anthropic docs + engineering-post reference material (stays in the kit repo; not installed)
│   └── anthropic-memory-rules.md          ← sourced memory/rules docs (stays in the kit repo; not installed)
├── skills/local-workflow/
│   ├── SKILL.md
│   └── references/
│       ├── adding-a-subagent.md
│       ├── subagent-best-practices.md
│       ├── domain-expert-template.md
│       ├── dispatching-code-developer.md
│       ├── phased-execution.md
│       ├── skill-staleness-audit.md
│       └── rule-capture.md
└── agents/
    ├── code-digester.md                   ← tier: read-only researcher (default worker)
    ├── research-specialist.md             ← tier: sole external-research worker (cache-first)
    ├── deep-analyst.md                    ← tier: read-only hard reasoning
    ├── code-developer.md                  ← tier: judgment writer (authors code, verifies against the research cache, self-checks)
    ├── bulk-editor.md                     ← tier: mechanical edits only
    ├── skill-auditor.md                   ← tier: read-only post-change docs audit (skills + rules)
    └── localworkflow-sync.md              ← house meta agent: audits the kit + guides adding domain experts
```

The seven `agents/*.md` files are the **baseline** — they install in both paths. Domain experts (`<prj>-<domain>-expert`) are project-specific and are created only in Path B (or later, once a greenfield project grows code). `research-specialist` maintains its own research cache under `.claude/agent-memory/research-specialist/`, created on first use — git-track that directory once it appears so cached lookups survive across sessions and are reusable by future writer dispatches.
---

## Step 0 — Pick the path

Determine the project type, then **confirm with the user before proceeding**:

- Quick signals: `git log --oneline | head` (shallow / empty history → likely greenfield), and count source files (few or none → greenfield).
- Ask the user to confirm: **"Is this a greenfield project (little/no code yet) or an existing codebase you want digested with domain experts?"**

Then follow **Path A** (greenfield) or **Path B** (existing project).

---

## Path A — Greenfield (baseline only)

Install just the skill + the seven baseline agents. Do **not** create domain experts yet — there is no code to pin their invariants to.

1. **Pre-flight.** `mkdir -p .claude/skills .claude/agents`. If `.claude/skills/local-workflow/` already exists, back it up or skip — this kit overwrites it.
2. **Install the skill.** `cp -R claude-local-workflow/skills/local-workflow .claude/skills/`
3. **Install the baseline agents.** `cp claude-local-workflow/agents/*.md .claude/agents/` — installs `code-digester`, `research-specialist`, `deep-analyst`, `code-developer`, `bulk-editor`, `skill-auditor`, and `localworkflow-sync`.
4. **Populate the Skill map (lightly).** Open `.claude/skills/local-workflow/SKILL.md` and replace the placeholder Skill-map rows with whatever skills already exist (often just a web-research row at first). Expand it as the project grows.
5. **Verify.** `ls .claude/skills/local-workflow/ .claude/agents/` — confirm the skill, its references, and the seven agents are present.
6. **Later, as subsystems emerge:** add a `<prj>-<domain>-expert` per major subsystem — dispatch `localworkflow-sync` (it returns the exact agent file + roster/Skill-map edits) or copy `references/domain-expert-template.md` by hand. Restart the session so each new agent registers.
7. **Clean up** (see Cleanup).

---

## Path B — Existing project (baseline + domain experts)

Install the baseline, then create domain experts for the subsystems the user names, restart to register them, and use them to digest the codebase.

1. **Ask the user which domains to cover first.** "Which subsystems/domains do you want dedicated expert agents for?" (e.g. `billing`, `auth`, `inventory`). Map each to a subsystem and, if one exists, its skill under `.claude/skills/<domain>/`.
2. **Pre-flight.** `mkdir -p .claude/skills .claude/agents` (back up any existing `local-workflow` skill).
3. **Install the skill.** `cp -R claude-local-workflow/skills/local-workflow .claude/skills/`
4. **Install the baseline agents.** `cp claude-local-workflow/agents/*.md .claude/agents/` (seven house agents, including `research-specialist` and `localworkflow-sync`).
5. **Branch a domain expert per chosen domain.** Pick a short project prefix `<prj>` (for example `shop`, `api`, or `app`) and reuse it. For each domain, either:
   - **Guided (recommended):** dispatch `localworkflow-sync` — it reads `references/domain-expert-template.md` + the domain's skill/code and returns the exact new-agent file plus the **Agent roster** + **Skill map** edit specs. Apply them (a mechanical `bulk-editor` pass works well). **or**
   - **By hand:** `cp .claude/skills/local-workflow/references/domain-expert-template.md .claude/agents/<prj>-<domain>-expert.md`, fill every `<...>` placeholder from the domain's code/skill, and add its row to the SKILL.md **Agent roster** + a **Skill map** entry.
6. **Populate the Skill map** with the project's real skills so the orchestrator routes threads correctly.
7. **Restart to register the agents.** Have the user **close and reopen (restart) the project/session** — new `.claude/agents/*.md` files are not dispatchable until the harness re-scans on restart.
8. **Digest the codebase.** After the restart, invoke `local-workflow` and let the orchestrator fan out `code-digester` and the new `<prj>-<domain>-expert` agents to read and summarize each subsystem. The experts will build up their `.claude/agent-memory/` notes as they go.
9. **Verify.** `ls .claude/skills/local-workflow/ .claude/agents/` — confirm the skill, references, seven baseline agents, and each `<prj>-<domain>-expert` are present, then **clean up**.

---

## Optional — SessionStart loop reminder

Projects that want a per-session nudge can have a SessionStart hook echo one line so every session opens with the loop contract in view:

```
local-workflow: loop steps 1-8 are binding — no self-skipped steps; repo files change only via subagents (bulk-editor / code-developer)
```

Wire it into an existing SessionStart hook (or add a minimal one via `.claude/settings.json` hooks). Skip this if the project doesn't use hooks.

---

## Cleanup (both paths)

Delete the bootstrap kit — it has no place in the deployed project:

```
rm -rf claude-local-workflow
```

Nothing under `.claude/` depends on it after deployment. This `DEPLOY.md` and the staging folder exist only to install the kit.
