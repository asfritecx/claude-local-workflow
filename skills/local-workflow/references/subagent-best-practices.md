# Subagent best practices — sourced

Anthropic's official guidance for building Claude Code subagents, distilled for the local-workflow house pattern, plus what has been verified empirically. Every external claim cites its source. Companion to `adding-a-subagent.md` (the procedure) — this file is the *why*.

Sources (crawled 2026-07-04):
- Official subagents docs: https://code.claude.com/docs/en/sub-agents
- Agent SDK subagents: https://code.claude.com/docs/en/agent-sdk/subagents
- Memory docs: https://code.claude.com/docs/en/memory
- Building effective agents: https://www.anthropic.com/engineering/building-effective-agents
- Context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Long-running harnesses: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

## Frontmatter / config semantics (official docs)

- Only `name` and `description` are required. `name` is lowercase+hyphens and need not match the filename (but keep them matching — `/doctor` flags same-scope duplicate names).
- **`tools` vs `disallowedTools`:** if both are set, `disallowedTools` is applied FIRST, then `tools` resolves from what remains; a tool listed in both is removed. Denylist patterns support `mcp__server`, `mcp__server__*`, `mcp__*`.
- **`skills` preloads FULL content.** Verbatim: "The full skill content is injected, not only the description. Subagents can still invoke unlisted project, user, and plugin skills through the Skill tool." Use this field — do not list `Skill` in `tools` to achieve preloading.
- **`memory`** — `user | project | local`; docs say "project is the recommended default scope" (`.claude/agent-memory/<name>/`, version-controlled). Injection limit, verbatim: "The subagent's system prompt also includes the first 200 lines or 25KB of MEMORY.md in the memory directory, whichever comes first, with instructions to curate MEMORY.md if it exceeds that limit." Enabling memory auto-adds Read/Write/Edit for the memory directory.
- **Preload budget heuristic:** keep an agent's combined `skills:` preloads at or under ~40KB. A roster audit measured several domain specialists preloading their full adjacent-skill set at ~45–80KB before trimming — preload only the primary domain skill(s) and move adjacents to conditional on-demand `Read .claude/skills/<skill>/SKILL.md` lines in the body.
- **Model resolution order:** `CLAUDE_CODE_SUBAGENT_MODEL` env var > per-invocation override > frontmatter `model` > main session model. `model` accepts `sonnet`/`opus`/`haiku`/`fable`, a full model ID, or `inherit` (the default).
- **`effort`** (`low` | `medium` | `high` | `xhigh` | `max`, or a number on the SDK surface) overrides the session level — the whole point of pinning a tier (code.claude.com/docs/en/agent-sdk/subagents).
- **`maxTurns`** is the official runaway safety net. `isolation: worktree` runs the agent in a temporary git worktree (auto-cleaned if unchanged). `background: true` forces background execution.
- **`maxTurns` house convention:** Bash-capable writers pin `maxTurns` (30–50); mechanical writers (`bulk-editor`) and read-only agents omit it.
- **Context isolation is total.** Verbatim: "Subagents receive only this system prompt plus basic environment details like the working directory, not the full Claude Code system prompt." A subagent never sees the parent conversation — every dispatch prompt must be self-contained.

## Behavior changes worth knowing (v2.1.7x–v2.1.19x)

- Subagents run **in the background by default** (v2.1.198); their permission prompts surface in the main session (v2.1.186).
- The **`/agents` interactive wizard was removed** (v2.1.198) — create/edit agents by editing `.claude/agents/*.md` directly.
- **Explore now inherits the session model** instead of always running Haiku (v2.1.198). The Opus cap on the inherited model applies only on the Anthropic API; on other providers (Bedrock etc.) Explore inherits the session model directly, uncapped (code.claude.com/docs/en/sub-agents).
- Subagents **inherit the session's extended-thinking config** (v2.1.198; previously disabled inside subagents).
- Nested subagents to 5 levels (v2.1.172); omit `Agent` from an agent's tools to prevent nesting.
- **Subagent continuation goes through `SendMessage`** — the Agent tool's old `resume` parameter was removed in v2.1.77; resume a subagent with `SendMessage({to: <raw agent ID>})`, which retains its full prior history (IDs resume completed agents reliably; names only reach running ones). On ~v2.1.77–v2.1.114 builds `SendMessage` was gated behind `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set in the shell, not settings.json (github.com/anthropics/claude-code issue #35240); current sub-agents docs drop the flag requirement for basic continuation. Self-test: if `ToolSearch("select:SendMessage")` finds nothing, set the flag. `Explore`/`Plan` built-ins return no agent ID and can't be resumed. Worktree caveat: an `isolation: worktree` agent that returns without file changes loses its worktree to auto-reap, and a later `SendMessage` resume can then fail its cwd preflight (reported: github.com/anthropics/claude-code issue #50889) — have a resumable worktree agent commit something before returning.

## System-prompt body shape

From the context-engineering post: aim for the "Goldilocks altitude" — specific enough to guide behavior, flexible enough for edge cases — and keep prompts "minimal but complete" (start minimal on the best model, add instructions only for observed failure modes). The house shape, used by every tier and domain-specialist agent:

1. One **role sentence** ("You are a … assisting an orchestrator").
2. **`When invoked:`** numbered startup workflow — stops the agent wasting turns deciding how to begin.
3. **Domain invariants** (domain agents only) — the load-bearing facts to check every conclusion against.
4. **Memory protocol** (memory-enabled agents only).
5. **Operating rules** stating WHY each constraint exists.
6. **`Output`** contract (DELIVERABLES shape, `file:line` refs, confirmed-vs-inferred).

## Description-driven delegation

The `description` field is the ONLY signal for automatic delegation. Official guidance, verbatim: "To encourage proactive delegation, include phrases like 'use proactively' in your subagent's description field." Lead with trigger conditions; official example description: "Expert code reviewer. Use proactively after code changes." Escalation levels when auto-delegation is not enough: natural language ("use the X agent") → `@agent-name` mention (guarantees invocation for one task) → `--agent` flag (entire session runs as that agent). Avoid an unquoted `: ` (colon-space) anywhere in the YAML value.

## Least-privilege tools

- Writers get a `tools:` allowlist (e.g. `Read, Edit, Write` for `bulk-editor`); readers get `disallowedTools: Write, Edit, NotebookEdit` and inherit everything else, EXCEPT every reader other than `research-specialist` carries an extended `disallowedTools` block that also locks away web-research tools — see the Web-research lock policy below.
- Tools NEVER available inside subagents regardless of config: `AskUserQuestion`, `EnterPlanMode`/`ExitPlanMode` (unless permissionMode is `plan`), `ScheduleWakeup`, `WaitForMcpServers`. A subagent cannot ask the user anything — the dispatch prompt must carry every decision.
- From building-effective-agents (agent-computer interface): invest as much in tool and prompt design as in behavior — "Put yourself in the model's shoes."
- **Web-research lock policy:** web-research tools (search/crawl/docs-lookup MCP tools and `WebSearch`) live SOLELY in `research-specialist` — every other reader carries an extended `disallowedTools` web-tool block, and every writer carries no web tools at all. `research-specialist` is cache-first: it checks its persistent memory (`.claude/agent-memory/research-specialist/`, MEMORY.md as topic index) before searching, and only searches on a cache miss, a version mismatch, an explicit re-check, or a stale entry when the request is implementation-bound — informational stale hits are served from cache and flagged stale. Readers cite the shared cache and report uncached needs as RESEARCH GAP deliverables; writers follow the Cache-verification protocol and STOP with `NEEDS_CONTEXT` on a gap. Residual gap: `Bash` (and any CLI or `curl` reachable through it) remains technically reachable by any agent that carries it — the lock is harness-enforced for MCP/Web tools only, instruction-level beyond that. Caveat: a user-global web-research skill is invisible to a fresh clone of this repo — the lock only holds for a session where that skill is installed.

## Model + effort routing

Official routing guidance: send easy/common work to smaller cost-efficient models (Haiku) and hard/unusual work to more capable models. House mapping: mechanical edits → haiku (`bulk-editor`); general reads/digests/reviews → sonnet at high effort (`code-digester`, `skill-auditor`); the sole external-research tier → sonnet at high effort (`research-specialist`, repo read-only + own memory doubling as the research cache); domain-pinned experts and the workflow-sync meta-agent → sonnet at medium effort; code authoring → sonnet at high effort (`code-developer`, docs-verified writes with a self-check before handoff); genuinely hard traces → opus at xhigh (`deep-analyst`). Pin BOTH model and effort in frontmatter so the tier holds regardless of the session level.

## Memory & note-taking

Official operational pattern: consult before work ("check your memory for patterns you've seen before") and update after ("save what you learned to your memory"). The house protocol layers on: one lesson per note with a one-line summary + `file:line` anchors; update-don't-duplicate; delete falsified notes; memory is hints, not ground truth (re-trace load-bearing claims); never save what the repo or preloaded skills already record; NEVER store secrets, PII, or sensitive domain data.

**Empirical (Claude Code v2.1.199+):** memory-directory writes SUCCEED even when `disallowedTools: Write, Edit, NotebookEdit` is set — repo files stay blocked, the memory directory stays writable. This is the recommended combination for read-only domain experts.

## Orchestration patterns (engineering posts)

- **Orchestrator–workers** (the local-workflow pattern): a central model decomposes, delegates, and synthesizes — right when subtasks cannot be predicted upfront.
- **Parallelization:** *sectioning* (independent subtasks in parallel — one message, multiple dispatches) and *voting* (the same task run N times for consensus on high-stakes correctness). Reach for voting when a single wrong answer is expensive and verification is cheap — 3 instances with independently-worded prompts, majority verdict; if the voters disagree, the question is under-specified, so tighten the brief rather than adding voters.
- Subagents should return **condensed summaries (~1–2K tokens)** even if they burned tens of thousands exploring — demand structured DELIVERABLES, never whole-file dumps.
- Multi-agent wins when the task exceeds one context window, independent verification matters, parallel exploration pays, or verbose output should stay out of the parent context. Otherwise a single agent is simpler — simplicity is Anthropic's first stated design principle.

## Context budgeting & overflow recovery

- **Hard overflow is a 400, not a compaction event.** When a request's input alone exceeds the model's window, the API rejects it before anything runs — auto-compaction protects a conversation growing toward the limit, not a `SendMessage` resume whose replayed transcript is already too long (platform.claude.com/docs/en/build-with-claude/context-windows). **Empirical (2026-07-05):** a warm writer resumed for a 4th resume round died mid-run with "Prompt is too long", leaving partial edits — and it had completed MORE than its last progress message claimed.
- **Soft failure — context anxiety — precedes the hard 400.** Models wrap up prematurely as they approach their perceived context limit, silently truncating scope with no error (Sonnet 4.5 exhibited this strongly per Anthropic's engineering post on effective context). Treat a suspiciously early "done" on a long thread as a truncation signal: verify coverage against the DELIVERABLES list, and shard the remainder rather than resuming the same agent.
- **Growth model:** every `SendMessage` resume replays the agent's full prior transcript; a substantive resume round adds ~50–80K tokens (reads + tool results + report), so rounds 3–4 cross a 200K window. **Cap warm reuse at 2 — exceptionally 3 — resume rounds, then dispatch fresh with a digested brief** (2–5K tokens of brief beats replaying a 150K transcript).
- **Shard at dispatch (house heuristic):** more than ~15–20 substantial files or >~100KB of source in one brief → split into parallel shards. A reader's transcript amplifies its reading 2–3× (search output, re-reads, report drafting), so one such scope ≈ 50–100K tokens — safe once in a window, not twice.
- **Overflow recovery:** a dead ID cannot be resumed (the resume replays the same over-long input and 400s again). Don't trust the last progress message; grep the working tree for one marker per scoped item, route the fully-specified remainder to `bulk-editor`, re-dispatch fresh for what still needs judgment.
- **`[1m]` escape hatch (secondary):** frontmatter `model:` accepts the same values as `--model`, including `sonnet[1m]` (code.claude.com/docs/en/model-config, code.claude.com/docs/en/sub-agents). 1M context bills at standard pricing with no premium beyond 200K, but plan/model availability varies — shard first; context rot doesn't care how big the window is.

## Smoke-testing (house method, empirically validated)

1. Registry pickup: the official docs say Claude Code picks up a new or edited agent file within seconds — the one documented exception being a brand-new `agents/` directory, whose first file needs a session restart because the watcher only covers directories that existed at session start (code.claude.com/docs/en/agent-sdk/subagents). **Empirically on builds around v2.1.199, neither claim held mid-session even with a pre-existing directory:** a newly created agent returned "Agent type not found" until a restart (2026-07-04, 2026-07-05), AND edits to an existing agent's frontmatter/body did NOT take effect mid-session — two consecutive dispatches after editing an existing agent's `## Output` contract both ran the OLD session-start version, with the edits confirmed on disk (2026-07-05). The definition is snapshotted at session start / first registry scan; the agent's memory dir still reads/writes live. Treat ANY agent-definition change (new file or edit) as needing a fresh session before validation — don't trust a mid-session re-dispatch to reflect it.
2. Meta-checks: confirm preloaded skills are actually in context (the agent cites skill facts with zero Read calls), memory is consulted first, and the `When invoked` workflow fires in order.
3. Real-task check: give it a genuine trace in its domain and verify the answer against the code yourself — an agent's report is a claim, not proof.
4. Memory check: verify the notes it writes are well-formed (frontmatter + a one-line index entry in its MEMORY.md), useful deltas (not documentation copies), and contain no PII or sensitive domain data.
