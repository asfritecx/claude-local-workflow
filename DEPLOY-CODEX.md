# Deploy the Codex local-workflow kit

This run-once guide installs the Codex skill and custom-agent roster from this repository into a target project. It does not replace or modify the Claude kit.

## Installed layout

```text
.agents/skills/local-workflow/     # reusable orchestration skill
.codex/agents/*.toml               # seven project custom agents
.codex/agent-memory/               # created on first verified cache/memory write
.codex/run-ledgers/                # ignored scratch state for active runs
```

## Step 0: inspect and choose a path

Inspect `git status`, source-file count, current `AGENTS.md`, existing `.agents/skills`, `.codex/agents`, and effective Codex configuration. Confirm whether the target is:

- **Greenfield:** install the seven house agents only.
- **Existing project:** install the house agents, then add domain experts only for stable subsystems with canonical guidance and code.

Never overwrite an existing skill or agent silently. Back it up, merge deliberately, or stop.

## Step 1: verify models

The kit pins these locally selected tiers:

- `gpt-5.6-luna`: digester, mechanical, and workflow-synchronization tiers.
- `gpt-5.6-sol`: research, analysis, and audit tiers.
- `gpt-5.6-terra`: implementation tier.

`codex/skills/local-workflow/references/agent-roster.md` is the canonical role-by-role model and reasoning-effort matrix.

Confirm all three slugs are available in the installer's Codex model registry. If any is unavailable, stop and ask the user for a replacement; do not silently inherit or substitute.

## Step 2: copy the baseline

From the target project root, copy:

```bash
mkdir -p .agents/skills .codex/agents
cp -R <kit>/codex/skills/local-workflow .agents/skills/
cp <kit>/codex/agents/*.toml .codex/agents/
```

Add `/.codex/run-ledgers/` to `.gitignore`. Keep `.codex/agent-memory/` tracked.

## Step 3: enforce non-research MCP boundaries

Codex configuration is layered. Do not claim that the staging files' empty `mcp_servers = {}` value clears inherited servers in every release.

1. List effective user, project, and plugin MCP servers.
2. In every non-research agent TOML, remove the top-level `mcp_servers = {}` line and append one explicit disabled table per effective server at the end of the file. Retain the server's non-secret transport definition because Codex validates disabled entries too:

   ```toml
   [mcp_servers."stdio-server"]
   command = "server-command"
   args = ["arg-one"]
   enabled = false

   [mcp_servers."http-server"]
   url = "https://example.invalid/mcp"
   enabled = false
   ```

   Appending matters: in TOML, keys written after a table header belong to that table until another table begins.
   Preserve `command`, `args`, `cwd`, `url`, `startup_timeout_sec`, and bearer-token environment-variable names when applicable. Never copy literal tokens, secret headers, or secret environment values into the repository.

3. Include plugin-provided MCP configuration when it is exposed through the active environment.
4. Leave `research-specialist` with the approved research sources it needs.
5. Record the residual limitation: Codex has no universal custom-agent allowlist for every hosted app/connector tool. The developer instructions remain a required secondary boundary.

Repeat this step when the project's MCP configuration changes.

## Step 4: customize routing

Edit `.agents/skills/local-workflow/references/project-routing.md`:

- Point each domain to the applicable `AGENTS.md`, project skills, specifications, and installed expert.
- Keep it an index, not a duplicate of domain rules.
- For greenfield projects, list only stable project-wide guidance. Add domain experts later as code establishes real invariants.

If an existing project needs experts, follow `domain-expert-template.md`, add the TOML under `.codex/agents/`, and register it in `agent-roster.md` and `project-routing.md`.

## Step 5: validate and restart

1. Run the official skill validator on `.agents/skills/local-workflow`.
2. Parse every `.codex/agents/*.toml` and check required fields, names, models, effort, sandbox, web, and MCP policy.
3. Run an ephemeral fresh session with `--strict-config`; plain TOML parsing cannot detect an incomplete MCP transport definition.
4. Run `git diff --check` and confirm only intended files changed.
5. Start a fresh Codex session so project custom agents are discovered.
6. Smoke-test one reader, the research cache path, one writer in a disposable fixture, the independent review gate, and any domain expert.
7. Negative-test read-only mutation and non-research external-tool access.

## Optional SessionStart reminder

Codex supports project `SessionStart` hooks, but project hooks require trust review and changed hooks are skipped until trusted. Add a hook only when the project wants a persistent reminder such as:

```text
local-workflow: the eight-step loop is binding; delegate repository mutations and independently verify every delta.
```

Do not disable the project's entire hook feature merely to avoid a trust prompt.
