# Claude-to-Codex local-workflow port review

Reviewed 2026-07-18 against the source kit and current official Anthropic and OpenAI documentation.

## Executive conclusion

The orchestration behavior ports closely: Codex has project skills, project custom agents, parallel subagent threads, follow-up/steering, per-agent model and reasoning configuration, sandbox modes, web/MCP configuration, hooks, and hierarchical project guidance.

Five Claude features do not have exact documented Codex equivalents: a universal per-agent tool allow/deny list, full skill-body preloading into a custom agent, a scoped automatically injected agent-memory directory with a write exception, declarative per-agent worktree isolation, and a per-agent hard turn cap. The port preserves workflow behavior with explicit read-first instructions, sandbox/web/MCP configuration, mediated memory writes, orchestrator-created worktrees, and bounded dispatch/interruption rules. Residual limitations are documented rather than hidden.

## Skills

| Capability | Claude Code | Codex | Port decision |
| --- | --- | --- | --- |
| Project location | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | Keep separate native copies. |
| Discovery | Metadata available; body loads when used | Metadata available; body loads after activation | Preserve name/description trigger surface. |
| Frontmatter | Rich invocation, tool, model, path, fork, and hook controls | `name` and `description` are the core skill frontmatter; UI/dependency policy lives in `agents/openai.yaml` | Remove Claude-only fields and express workflow rules in the body/custom agents. |
| Invocation | `/skill-name` and automatic matching | `$skill-name`, skill picker, and automatic matching | Document `$local-workflow`; keep implicit invocation enabled. |
| Resources | Supporting docs, scripts, templates | `references/`, `scripts/`, and `assets/` | Direct mapping with progressive disclosure. |

Sources: [Anthropic skills](https://code.claude.com/docs/en/skills), [OpenAI skills](https://learn.chatgpt.com/docs/build-skills).

## Custom agents

| Capability | Claude Code | Codex | Port decision |
| --- | --- | --- | --- |
| Definition | `.claude/agents/*.md` with YAML + Markdown | `.codex/agents/*.toml` with required `name`, `description`, `developer_instructions` | Translate each house role into minimal TOML. |
| Model/effort | `model`, `effort` aliases | `model`, `model_reasoning_effort` | Pin user-selected Luna/Sol/Terra tiers and fail clearly if unavailable. |
| Read/write boundary | `tools`, `disallowedTools`, permission mode | `sandbox_mode`, parent permission mode, web/MCP config | Use read-only/workspace-write plus explicit web and MCP policy; qualify hosted-tool gaps. |
| Skill preload | `skills:` injects full skill content | `skills.config` enables/disables skills; it is not documented as preloading | Require explicit read-first skill paths. |
| Persistent agent memory | `memory:` injects and grants scoped memory access | No documented project custom-agent memory grant | Use tracked `.codex/agent-memory`; every agent returns exact specs for mediated `bulk-editor` writes. |
| Worktree isolation | `isolation: worktree` | No documented custom-agent isolation field | Orchestrator creates Git worktrees before conflicting writer dispatches. |
| Per-agent turn cap | `maxTurns` can bound a custom agent | No documented per-role turn-cap field; global thread/depth settings and interruption controls exist | Use bounded briefs, the two-to-three follow-up cap, phased writers, and orchestrator interrupt/redispatch on drift. |
| Lifecycle hooks | Per-agent and project hooks | Config-layer/project/plugin hooks; command handlers currently run | Keep the optional reminder out of the default install and document trust. |
| Proactive routing | Trigger-rich `description` and proactive wording | Agent `description` guides automatic role selection; the orchestrator can name the role explicitly | Preserve narrow trigger descriptions and explicitly name the selected house role in dispatches. |
| Presentation | `color` | Optional nickname candidates | Omit decorative mapping unless a project explicitly wants nicknames. |

Sources: [Anthropic subagents](https://code.claude.com/docs/en/sub-agents), [OpenAI subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [OpenAI hooks](https://learn.chatgpt.com/docs/hooks).

## Orchestration and context

Claude's Agent/SendMessage pattern maps to Codex subagent spawn, follow-up, steer, wait, interrupt, and thread inspection. Both approaches isolate worker context and return summaries to the orchestrator. The port keeps the main thread responsible for requirements, decisions, verification, and synthesis.

The source kit's two-to-three warm follow-up cap is retained as a conservative house heuristic, not represented as a documented Codex transcript-replay guarantee. The portable workflow queries live thread capacity rather than assuming Claude or Codex numeric defaults.

Codex defaults to shallow agent nesting; the house workflow needs only root-to-worker delegation. Recursive fan-out remains disabled unless a specific workflow justifies it.

## External research and cache

Claude's source research agent combines web tools with a project memory write exception. The Codex researcher instead runs read-only with live search, checks the tracked cache explicitly, and returns exact `CACHE_WRITE` content. `bulk-editor` persists the verified digest. All other agent-note changes use the same mediated pattern, including notes proposed by workspace writers. Writers remain web-disabled and stop with `NEEDS_CONTEXT` when the cache is missing, stale, or version-mismatched.

This preserves cache-first behavior and avoids granting a read-only researcher workspace-wide write access.

## Rules and durable guidance

Claude `.claude/rules/**/*.md` supports file-glob activation. Codex `.codex/rules` governs command execution policy, not behavioral guidance, so it is not a substitute.

The default behavioral replacement is the closest nested `AGENTS.md`. This is not exact glob parity: Codex builds its project guidance chain from project root to session working directory, and root-started workflows should not assume an arbitrary nested file activates dynamically merely because a file is read. Therefore:

- Put truly subtree-wide guidance in the nested `AGENTS.md`.
- Keep cross-tree or root-start requirements in root guidance or an explicitly invoked/read skill.
- Propose rather than auto-create a rule when safe scoping is impossible.

Sources: [Anthropic memory and rules](https://code.claude.com/docs/en/memory), [OpenAI AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [OpenAI command rules](https://learn.chatgpt.com/docs/agent-configuration/rules).

## Permissions and enforcement limits

Codex reapplies the parent turn's live sandbox and approval overrides to spawned agents. A permissive parent can supersede a custom agent's default, so agent files cannot promise a stronger boundary than the effective runtime.

For non-research agents the installer:

1. Sets `web_search = "disabled"`.
2. Uses read-only or workspace-write sandbox according to role.
3. Materializes explicit `enabled = false` entries for every effective MCP server while retaining each non-secret command/URL transport definition required for runtime deserialization.
4. Disables non-research MCP transports on `research-specialist`, leaving live web and the approved documentation/search MCP sources available.
5. Keeps an instruction-level prohibition on external apps/connectors because the documented custom-agent format has no universal hosted-tool allowlist.

The port describes these as the strongest available Codex equivalent, not literal feature parity.

## Hooks, worktrees, and plugins

Codex exposes SessionStart, SubagentStart/Stop, tool-use, compaction, prompt, and stop lifecycle events. Only command hook handlers currently execute, and project/plugin hooks require explicit trust. The source's optional session reminder remains optional.

Codex plugins can package skills, hooks, apps, MCP configuration, and assets. The current documented plugin manifest does not list project custom-agent TOMLs as a plugin component. A plugin-only distribution would therefore omit the core roster. The kit uses a copy-based deployment guide and may later add a skill-only plugin without representing it as the complete workflow.

Sources: [OpenAI hooks](https://learn.chatgpt.com/docs/hooks), [OpenAI plugin structure](https://learn.chatgpt.com/docs/build-plugins), [OpenAI worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees).

## Preserved workflow contracts

- Readers digest; writers write; the orchestrator verifies.
- External/current facts route only through `research-specialist`.
- Fully specified edits route to `bulk-editor`; judgment edits route to `code-developer`.
- Independent review uses a fresh read-only agent and never auto-fixes findings.
- Complex changes use testable phases, fresh writers, review gates, and explicit commit authorization.
- Every repository delta triggers guidance staleness review and durable-lesson consideration.
- The main thread performs no repository mutation while the skill is active, including deletion.

## Known non-1:1 residuals

1. Hosted tools and app connectors cannot be universally allowlisted per custom agent using the documented schema.
2. Agent memory/cache writes require a second mechanical-writer dispatch so every note change is observable and reviewed.
3. Nested `AGENTS.md` cannot reproduce arbitrary Claude path globs in every root-started session.
4. Worktree isolation is orchestrated rather than an agent manifest field.
5. Claude's per-agent `maxTurns` has no documented Codex role-file counterpart; bounded briefs, follow-up limits, interruption, and fresh redispatch replace the hard field.
6. Custom-agent authoring is documented as an evolving configuration-layer surface, so validation against the installed Codex release remains mandatory; plain TOML parsing is insufficient, and a fresh `--strict-config` session must also load every role.
