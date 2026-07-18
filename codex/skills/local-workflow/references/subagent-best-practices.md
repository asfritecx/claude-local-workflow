# Codex Subagent Best Practices

This is the Codex-specific rationale for the house pattern. Review against current official documentation when custom-agent or skill behavior changes.

## Native surfaces

- Project skills live under `.agents/skills/<name>/SKILL.md`; Codex initially sees skill metadata and loads the body after activation. Skills use `name` and `description` frontmatter, with optional UI/dependency metadata in `agents/openai.yaml`. Source: https://learn.chatgpt.com/docs/build-skills
- Project custom agents live under `.codex/agents/*.toml`. Required fields are `name`, `description`, and `developer_instructions`; model, reasoning, sandbox, MCP, and other config keys may override the parent layer. Source: https://learn.chatgpt.com/docs/agent-configuration/subagents
- Codex can spawn, inspect, follow up, interrupt, and wait for subagent threads. Current local releases delegate after a direct request or applicable project/skill instruction. Source: https://learn.chatgpt.com/docs/agent-configuration/subagents
- `AGENTS.md` provides durable repository guidance. Put specialized rules in the closest subtree and keep the root concise. Source: https://learn.chatgpt.com/docs/agent-configuration/agents-md

## Differences from Claude Code

Claude custom agents expose YAML `tools`, `disallowedTools`, `skills`, `memory`, hooks, and worktree isolation. Claude skills also expose invocation/tool/model/path controls. Sources: https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/skills

Codex custom agents are configuration layers rather than dedicated manifests. The documented format does not provide a universal built-in tool allow/deny list, automatic skill-body preload, scoped persistent agent-memory grant, or declarative per-agent worktree isolation. Use:

- `sandbox_mode`, `web_search`, and MCP enable/disable config for the strongest native role boundary.
- Explicit read-first skill and memory paths.
- Mediated `bulk-editor` writes for read-only memory/cache updates.
- Orchestrator-created Git worktrees for conflicting writers.
- Narrow developer instructions for any hosted-tool boundary that native config cannot enforce.

Codex plugins can distribute skills, hooks, apps, and MCP configuration, but the documented plugin manifest does not bundle project custom-agent TOMLs. This kit therefore uses a copy-based deployment runbook rather than claiming a plugin-only 1:1 port. Source: https://learn.chatgpt.com/docs/build-plugins

## Context and topology

- Delegate independent, context-heavy reading; keep requirements and synthesis in the main thread.
- Bound each dispatch and request a distilled report. Multi-agent work costs more tokens and write-heavy concurrency increases conflicts.
- Group threads by the context they need, not merely by activity type.
- Prefer fresh agents after two substantial follow-ups, exceptionally three, to avoid replaying an oversized transcript.
- Respect live thread capacity. Codex defaults and product limits can change; never hard-code fan-out count in a prompt.
- Keep nesting at the default depth unless a concrete workflow requires recursive delegation.

## Verification

The generator's report is not proof. Independently inspect changes and run deterministic checks. Use a fresh read-only agent for the review gate, and require the user to disposition findings before fixes.

## Permissions

Subagents inherit the parent permission environment, and live parent overrides are reapplied. A permissive parent can supersede a read-only custom-agent default, just as Claude parent bypass modes can supersede agent permission settings. Always report the effective mode and avoid representing prompt-only restrictions as a hard sandbox.

## Installation checks

1. Verify model slugs locally.
2. Parse every TOML.
3. Confirm active web and MCP tools for each role in a fresh session.
4. Negative-test read-only mutation.
5. Forward-test realistic dispatch and report shapes.
