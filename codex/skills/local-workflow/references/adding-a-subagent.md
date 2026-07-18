# Adding a Custom Agent

Use when adding a house tier or project-domain expert to `.codex/agents/`.

## Authoring procedure

1. Create `.codex/agents/<name>.toml`. Match the filename to `name` and use lowercase kebab-case.
2. Define the required fields:

   ```toml
   name = "<name>"
   description = "Specific trigger and boundary."
   developer_instructions = """
   <role, workflow, boundaries, and output contract>
   """
   ```

3. Pin the intended tier with `model` and `model_reasoning_effort`. Verify the slug in the local Codex model registry; do not silently fall back.
4. Set `sandbox_mode = "read-only"` for readers and `web_search = "disabled"` for every non-research agent. Use `mcp_servers = {}` in the portable template. During deployment, replace it with every effective inherited MCP server's non-secret transport fields plus `enabled = false`; disabled entries without a command or URL fail runtime role deserialization.
5. In `developer_instructions`, require applicable `AGENTS.md`, project skill, and memory paths to be read explicitly. Codex has no Claude-style custom-agent `skills:` preload or scoped injected memory grant.
6. Give the agent one focused role, a numbered startup procedure, operating boundaries with stop conditions, and a self-contained output contract.
7. Register it in `agent-roster.md` and `project-routing.md`. Update `localworkflow-sync` when the roster semantics change.
8. Parse the TOML, run an ephemeral fresh session with `--strict-config`, smoke-test a small task, and negatively test the intended sandbox/web boundary.

## Tier selection

- `gpt-5.6-luna` / `max`: high-volume code digestion and workflow synchronization.
- `gpt-5.6-sol` / `high`: difficult analysis and security review.
- `gpt-5.6-sol` / `medium`: research synthesis and guidance audits.
- `gpt-5.6-terra` / `high`: implementation work.
- `gpt-5.6-luna` / `high`: exact mechanical edits.

These are this kit's pinned roles, not universal Codex recommendations. An installation lacking a slug must stop and ask the user for a replacement.

## Read-only memory

Read-only agents never receive workspace-write merely to maintain notes. They read `.codex/agent-memory/<name>/` explicitly and return an exact `MEMORY_WRITE` or `CACHE_WRITE` specification. The orchestrator verifies it and dispatches `bulk-editor` to persist it.

## Smoke-test checklist

- Description routes the intended prompt to the new agent.
- Agent reads the named guidance before repository files.
- Report matches the requested deliverables and uses complete `path:line` evidence.
- Read-only mutation attempts fail.
- Non-research web and configured MCP attempts are unavailable or refused.
- Memory updates are returned as specs, not written by a read-only agent.
- A changed agent definition is tested in a new session; do not rely on hot reload.
