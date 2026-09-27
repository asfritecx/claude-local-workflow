# Codex subagent best practices

Source of truth: [OpenAI Codex subagents documentation](https://learn.chatgpt.com/docs/codex/subagents) and the repository's `.codex/agents/*.toml` files.

## When delegation helps

Delegate bounded, independent work whose separate context or specialist instructions improve speed or quality. Read-heavy exploration, external research, focused implementation, and independent review are strong candidates. Keep tightly coupled decisions and small edits in the main thread.

All agents share the same working directory. Assign non-overlapping write ownership, tell every writer to preserve others' changes, and inspect the combined tree before validation. A custom agent's `sandbox_mode` is a configured default plus a behavior contract. Parent or live runtime overrides may broaden the effective sandbox. When filesystem enforcement matters, start from a parent or runtime with the required sandbox and verify the effective child profile.

## Real collaboration controls

- `collaboration.spawn_agent({ agent_type, task_name, message, ... })` creates a bounded task. `agent_type` selects a built-in or `.codex/agents/*.toml` custom agent.
- `collaboration.send_message({ target, message })` delivers context to an existing agent without starting an idle turn.
- `collaboration.followup_task({ target, message })` delivers work and triggers an idle agent.
- `collaboration.wait_agent({ timeout_ms })` waits for mailbox activity. Use a long useful timeout rather than frequent polling.
- `collaboration.interrupt_agent({ target })` stops the current turn when it is no longer useful.

For profile-pinned agents, use `fork_turns: "none"` with a self-contained brief, or a deliberately bounded positive value when limited recent history is needed. A full-history fork can inherit the parent model and reasoning effort instead of the custom profile. Omit explicit model overrides in normal use so the selected custom agent file supplies its configured tier. If runtime metadata exposes the effective model, reasoning effort, and sandbox, inspect it before claiming which profile ran. If it does not, report the configured profile and dispatch overrides separately and mark the effective profile unavailable. Custom agents do not receive project skills or curated knowledge automatically; prompts must name the files they need to read.

## Roster policy

Project custom agents live in `.codex/agents/*.toml`. Each declares `name`, `description`, and `developer_instructions`; model pins use `model` and `model_reasoning_effort`.

| Roles | Model / effort | Boundary |
| --- | --- | --- |
| `code-digester`, `research-specialist`, `skill-auditor`, `localworkflow-sync`, any `<prj>-<domain>-expert` agents | `gpt-6-luna` / max | Read and distill; readers may propose curated-note updates. The main thread or an explicitly assigned writer applies them. |
| `code-developer` | `gpt-6-sol` / medium | General implementation and documentation authoring. |
| `deep-analyst` | `gpt-6-astra` / high | Difficult multi-file reasoning, read-only. |
| `code-reviewer`, `adversarial-reviewer`, your specialist writers, if any | `gpt-6-sol` / high | Reviewers are read-only; writers stay within specialist boundaries. |
| `bulk-editor` | `gpt-6-luna` / max | Fully specified mechanical edits only. |

This routing follows [OpenAI's model selection guidance](https://developers.openai.com/api/docs/guides/model-selection): Sol for coding and judgment, Luna for scoped work, and Astra for difficult analysis. Keep the configured reasoning efforts stable when comparing model changes. `bulk-editor` uses Luna / max because the runtime model catalog did not offer its originally intended effort tier for Luna. The installer may adjust these tiers to the models your runtime offers.

Use the role description as the routing authority. `research-specialist` owns web and current-fact research. Readers return evidence and edit specifications; writers apply changes. `code-reviewer` independently checks every code-changing wave, and `adversarial-reviewer` challenges material design choices.

## Prompt shape

Include the objective, ownership, raw evidence or known context, required project skills and rules, constraints, expected deliverable, and validation. State whether the agent may edit. Do not assume it can ask the user for missing product decisions; route such decisions back to the main thread.

Keep reuse practical. A follow-up is useful when the agent still has relevant context. Spawn a fresh task when the objective or ownership changes materially, or when a concise brief is clearer than replaying a long thread.
