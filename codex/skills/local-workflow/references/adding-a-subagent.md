# Adding a project custom agent

Use this procedure when a recurring responsibility needs a distinct prompt, model tier, or read/write boundary. Prefer an existing agent plus a precise dispatch brief when the need is one-off.

Source of truth: [OpenAI Codex subagents documentation](https://learn.chatgpt.com/docs/codex/subagents).

1. Choose a narrow role with clear inputs, outputs, ownership, and exclusions.
2. Create `.codex/agents/<name>.toml`. The `name` field is authoritative; matching the filename is the project convention.
3. Define the required fields: `name`, `description`, and `developer_instructions`.
4. Set `model` and `model_reasoning_effort` according to the roster policy in `subagent-best-practices.md`.
5. Configure `sandbox_mode = "read-only"` for readers and reviewers and include a behavioral instruction not to edit. This is the custom agent's default, not proof of the effective sandbox: a parent or live runtime override may broaden it. For enforced read-only execution, use a read-only parent or runtime. Verify the effective child sandbox when runtime metadata exposes it; otherwise state that enforcement could not be independently observed.
6. Instruct the agent to read applicable `.agents/skills/<skill>/SKILL.md`, `docs/agent-rules/INDEX.md`, and `docs/agent-knowledge/INDEX.md` entries explicitly. Codex custom agents do not support Claude-style `skills:` preloading or memory injection.
7. Update the roster documentation and any dispatch references that name the new role.
8. Start a new Codex session if the current client has not discovered the new definition, then forward-test with a realistic self-contained prompt using `fork_turns: "none"` or a deliberately bounded positive value. Verify the effective model, reasoning effort, and sandbox when runtime metadata exposes them. Otherwise report the configured profile and dispatch overrides, and mark the effective profile unavailable rather than inferring it from TOML.

Minimal shape:

```toml
name = "example-reviewer"
description = "Read-only reviewer for a specific recurring risk."
model = "gpt-6-sol"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Read AGENTS.md and every project skill or rule named in the dispatch.
Review only the assigned delta. Return severity-ranked findings with file references and concrete failure scenarios. Do not edit files.
"""
```

Test that the role is discoverable, reads the named guidance, respects its behavioral boundary, and returns the requested contract. Record configured and effective profiles separately when the runtime exposes both; otherwise mark the effective profile unavailable. Do not claim automatic skill loading or persistent injected memory.
