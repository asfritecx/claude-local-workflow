# Deploy the local-workflow kit into a project (Codex)

**This is a run-once bootstrap runbook.** It installs the Codex skill, the nine house custom agents and the Codex rule twins. It does not replace or modify the Claude install; run `DEPLOY.md` too if the project uses both runtimes. Whoever runs it deletes the kit folder at the end.

## What gets installed where

| Kit path | Installs to | Notes |
|---|---|---|
| `codex/skills/local-workflow/` | `.agents/skills/local-workflow/` | `SKILL.md` (router, Project routing table, delegation, review, finish), `agents/openai.yaml`, and `references/` with the brief contract, principles, review gate, a single `playbooks.md` and the authoring guides. |
| `codex/agents/*.toml` | `.codex/agents/` | The nine house agents. Tiers are in each TOML and in `references/subagent-best-practices.md` § Roster policy. |
| `codex/agent-rules/` | `docs/agent-rules/` | `INDEX.md` plus the Codex twins of the three Claude rules. Codex agents read these explicitly. |
| `knowledge/` | `docs/agent-knowledge/` | Shared with the Claude install. Skip it if `DEPLOY.md` already installed it. |

There is no `.codex/agent-memory/` and no run-ledger directory. Per-agent memory is retired: agents propose knowledge-note updates, and the parent applies them to `docs/agent-knowledge/`. Multi-phase runs keep their state in `docs/runs/<YYYY-MM-DD-slug>/` (see `references/playbooks.md`).

## Step 0: inspect and choose a path

Inspect `git status`, the source-file count, the current `AGENTS.md`, and any existing `.agents/skills`, `.codex/agents` and `docs/agent-rules`. Confirm whether the target is:

- **Greenfield:** install the nine house agents only.
- **Existing project:** install the house agents, then add domain experts for stable subsystems that have canonical guidance and code.

Never overwrite an existing skill, agent or rule silently. Back it up, merge deliberately, or stop.

## Step 1: verify models

The TOMLs carry these tiers:

| Agents | `model` / `model_reasoning_effort` |
|---|---|
| `code-digester`, `research-specialist`, `skill-auditor`, `localworkflow-sync`, `bulk-editor`, domain experts | `gpt-6-luna` / `max` |
| `code-developer` | `gpt-6-sol` / `medium` |
| `code-reviewer`, `adversarial-reviewer` | `gpt-6-sol` / `high` |
| `deep-analyst` | `gpt-6-astra` / `high` |

Confirm every slug is available in the installer's Codex model registry. If one is not, stop and ask the user for a replacement; do not silently inherit or substitute. When you change a tier, update the TOML, the Roster policy table in `references/subagent-best-practices.md` and the tier sentence in `SKILL.md` § Delegate deliberately. Codex tiers diverge from the Claude roster on purpose; don't mirror them.

## Step 2: copy the baseline

From the target project root:

```bash
mkdir -p .agents/skills .codex/agents docs/agent-rules docs/agent-knowledge
cp -R claude-local-workflow/codex/skills/local-workflow .agents/skills/
cp claude-local-workflow/codex/agents/*.toml .codex/agents/
cp claude-local-workflow/codex/agent-rules/*.md docs/agent-rules/
# only if DEPLOY.md did not already install it:
cp -R claude-local-workflow/knowledge/. docs/agent-knowledge/
```

## Step 3: external-tool boundaries (recommended)

The TOMLs restrict web and MCP use by instruction only: readers and writers are told not to use web or external tools, and `research-specialist` is the only research tier. Codex has no universal per-agent allowlist for every hosted tool or connector. To harden this:

1. List the effective user, project and plugin MCP servers.
2. In each non-research agent TOML, append one disabled table per effective server at the **end** of the file (keys after a table header belong to that table). Keep the non-secret transport fields, because Codex validates disabled entries too:

   ```toml
   [mcp_servers."stdio-server"]
   command = "server-command"
   args = ["arg-one"]
   enabled = false
   ```

   Never copy literal tokens, secret headers or secret environment values into the repository.
3. Leave `research-specialist` with the research sources it needs.
4. Repeat this step when the project's MCP configuration changes.

## Step 4: fill the placeholders

- `.agents/skills/local-workflow/SKILL.md` § Project routing: point each domain at its `AGENTS.md`, project skills and installed expert. Keep it an index, not a copy of the domain rules. A greenfield project lists only stable project-wide guidance.
- `<your typecheck>`, `<your lint>`, `<your unit tests>` in the skill: the project's real commands.
- `.codex/agents/code-reviewer.toml`, `adversarial-reviewer.toml` and `code-developer.toml`: replace `<your project's standing invariants>` with the handful a reviewer must check on every delta.
- `grep -rn '<your ' .agents .codex docs/agent-rules docs/agent-knowledge` lists what is left.
- **Domain experts** (existing projects): follow `references/domain-expert-template.md`, add the TOML under `.codex/agents/<prj>-<domain>-expert.toml`, and add its Project routing row, its Roster policy row and its note under `docs/agent-knowledge/domain/`.

## Step 5: validate and restart

1. Run the official skill validator on `.agents/skills/local-workflow`.
2. Parse every `.codex/agents/*.toml` and check the required fields (`name`, `description`, `developer_instructions`), names, models, effort and sandbox (`read-only` for readers and reviewers, `workspace-write` for `code-developer` and `bulk-editor`).
3. Run an ephemeral fresh session with `--strict-config`; plain TOML parsing cannot detect an incomplete MCP transport definition.
4. Run `git diff --check` and confirm only intended files changed.
5. Start a fresh Codex session so the project custom agents are discovered.
6. Smoke-test one reader, `research-specialist` against `docs/agent-knowledge/research/`, one writer in a disposable fixture, `code-reviewer` on a small delta, and any domain expert.
7. Negative-test a read-only mutation attempt and a non-research external-tool attempt.

## Optional SessionStart reminder

Codex supports project `SessionStart` hooks, but project hooks need a trust review and changed hooks are skipped until trusted. Add one only if the project wants a persistent reminder, for example:

```text
local-workflow: route to a playbook; the parent owns scope, decisions and the final answer; brief bounded agents; review every code-changing wave; shared knowledge in docs/agent-knowledge (propose, then apply)
```

Don't disable the project's whole hook feature just to avoid a trust prompt.

The git guard in `hooks/` is a Claude Code `PreToolUse` hook. In Codex the same ban (no stash, restore, reset or `checkout --` in a shared tree) stays instruction-only, through `docs/agent-rules/worktree-agent-dispatch.md`.

## Cleanup

```
rm -rf claude-local-workflow
```

Nothing installed depends on the kit folder.
