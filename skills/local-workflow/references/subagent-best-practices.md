# Subagent best practices — sourced

Anthropic's official guidance for building Claude Code subagents, distilled for the local-workflow house pattern, plus what has been observed in practice running it. Every external claim cites its source. Companion to `adding-a-subagent.md` (the procedure) — this file is the *why*. The condensed, versioned research note behind the harness and model facts is `docs/agent-knowledge/research/claude-code-subagents.md`; check its TTL before relying on a version-specific claim.

Sources (crawled 2026-09-25, CLI v2.1.282):
- Official subagents docs: https://code.claude.com/docs/en/sub-agents (sections: supported frontmatter fields, choose a model, what loads at startup, auto-compaction)
- Model configuration: https://code.claude.com/docs/en/model-config (model aliases, adjust effort level, extended context, work with Fable, Fable and usage credits, automatic model fallback)
- Models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Agent SDK subagents: https://code.claude.com/docs/en/agent-sdk/subagents (crawled 2026-07-04)
- Building effective agents: https://www.anthropic.com/engineering/building-effective-agents (crawled 2026-07-04)
- Context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (crawled 2026-07-04)
- Long-running harnesses: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents (crawled 2026-07-04)

## Frontmatter / config semantics (official docs)

- **Fields (v2.1.282):** `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `omitClaudeMd`, `effort`, `isolation`, `color`, `initialPrompt`, `experimental`. No field has been deprecated.
- Only `name` and `description` are required. `name` is lowercase+hyphens, cannot contain `:` (v2.1.218), and need not match the filename (but keep them matching — `/doctor` flags same-scope duplicate names).
- **`tools` vs `disallowedTools`:** if both are set, `disallowedTools` is applied FIRST, then `tools` resolves from what remains; a tool listed in both is removed. Denylist patterns support `mcp__server`, `mcp__server__*`, `mcp__*`.
- **`skills` preloads FULL content.** Verbatim: "The full skill content is injected, not only the description. Subagents can still invoke unlisted project, user, and plugin skills through the Skill tool." Use this field — do not list `Skill` in `tools` to achieve preloading.
- **Preload budget heuristic:** keep an agent's combined `skills:` preloads at or under ~40KB. Observed in practice: specialist writers that preloaded several adjacent domain skills measured ~45–80KB before trimming — preload only the primary domain skill(s) and move adjacents to conditional on-demand `Read .claude/skills/<skill>/SKILL.md` lines in the body.
- **`model`** accepts a model alias (`opus`, `fable`, `haiku` and the other family aliases), a full model ID, or `inherit`; full IDs "accept the same values as the `--model` flag". Omitting it no longer simply means inherit — Claude Code follows the resolution order below. The kit's agents pin aliases; see the family-alias rule below for when a full ID is worth pinning.
- **`effort`** — options `low`, `medium`, `high`, `xhigh`, `max`; "available levels depend on the model". The default is to inherit the session level. House agents always pin it.
- **`maxTurns`** is the official runaway safety net. Since v2.1.246, hitting the limit marks the output partial and resumable rather than just cutting it off. `isolation: worktree` runs the agent in a temporary git worktree (auto-cleaned if unchanged). `background: true` forces background execution.
- **`maxTurns` house convention:** Bash-capable writers pin `maxTurns` (30–50); mechanical writers (`bulk-editor`) and read-only agents omit it.
- **`omitClaudeMd`** (v2.1.271) launches the subagent without the user, project and local CLAUDE.md files. House agents do not set it: the CLAUDE.md invariants are part of what every tier checks against.
- **`experimental.cacheTtl`** (v2.1.248) takes `5m` or `1h`. Not used by house agents.
- **`permissionMode`** gained a `manual` alias for `default` (v2.1.200).
- **`memory`** still exists as a field, but **house agents carry no `memory:`** — the shared `docs/agent-knowledge/` base replaces per-agent memory (see § Knowledge base).
- **Context isolation is total.** Verbatim: "Subagents receive only this system prompt plus basic environment details like the working directory, not the full Claude Code system prompt." A subagent never sees the parent conversation — every dispatch prompt must be self-contained.

## Current harness behavior (verified 2026-09-25, CLI v2.1.282)

- **Model resolution order:** (1) the per-call `model` parameter, (2) frontmatter `model`, (3) `CLAUDE_CODE_SUBAGENT_MODEL`, (4) the main conversation's model. The env var dropped below frontmatter in v2.1.251; to force one model on every subagent set `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+). A per-call model sticks when the subagent is resumed (v2.1.211+).
- **Per-call `model` takes aliases only, and there is no per-call effort.** The Agent tool schema in v2.1.282 exposes `model` as an enum of family aliases — no full IDs, no `effort` (observed in the tool schema, not stated in the docs). So effort is set only per agent in frontmatter or for the whole session, and a per-call alias override is subject to the family-alias rule below. Don't count on a per-call override to reach a specific snapshot.
- **The family-alias rule.** Verbatim: when "the main conversation's model belongs to that family: the subagent runs on the main conversation's exact model, including any `[1m]` suffix". So an alias pin follows the session's snapshot within a family (convenient across model releases); pin a full ID when an agent must run one exact snapshot regardless of the session.
- **Allowlists:** if an org's `availableModels` blocks a family alias, the subagent runs on the newest version of that family the allowlist permits (v2.1.222+); if it blocks a full ID, the subagent falls back to the inherited model and interactive sessions show a warning.
- **Effort levels per model:** supported levels vary by model; some models don't support `xhigh`, and the docs say "Models not listed here do not support effort." An unsupported level "falls back to the highest supported level at or below the one you set" — never an error. Default effort also varies per model (the docs list the exceptions), and a top-level `effortLevel` in user settings does not apply to every model; levels are saved per model. Check the research note for the current per-model table.
- **Thinking:** subagents inherit the session's thinking setting; there is no per-subagent thinking setting.
- **Context window:** a subagent's window "is sized by its own model, not the parent's", and subagents auto-compact "using the same logic as the main conversation".
- **Effective profile:** `/tasks` shows each agent's effort next to its model (v2.1.242+). Frontmatter is the configured profile; `/tasks` is where the effective one is confirmed.
- **Reload:** verbatim, "Claude Code watches `~/.claude/agents/` and `.claude/agents/`… the next delegation uses the updated definition, with no restart needed." Restart is still needed for the first agent file in an `agents` directory that didn't exist at session start, for directories added with `--add-dir`, and for sessions started with `--disable-slash-commands`. Observed in practice: edited definitions have sometimes not been picked up until a restart — see § Smoke-testing.

Carried forward from the 2026-07-04 crawl and **not re-verified on 2026-09-25** — treat as leads:
- The interactive `/agents` wizard was removed (v2.1.198); create and edit agents as files.
- Subagents run in the background by default (v2.1.198); their permission prompts surface in the main session (v2.1.186).
- Explore inherits the session model instead of always running Haiku (v2.1.198).
- Nested subagents to 5 levels (v2.1.172); omit `Agent` from an agent's tools to prevent nesting.
- Subagent continuation goes through `SendMessage` — resume with `SendMessage({to: <raw agent ID>})`, which retains the agent's full prior history (IDs resume completed agents reliably; names only reach running ones). The Agent tool's old `resume` parameter was removed in v2.1.77. `Explore`/`Plan` built-ins return no agent ID and can't be resumed. Worktree caveat: an `isolation: worktree` agent that returns without file changes loses its worktree to auto-reap, and a later resume can then fail its cwd preflight (reported: github.com/anthropics/claude-code issue #50889) — have a resumable worktree agent commit something before returning.

## System-prompt body shape

From the context-engineering post: aim for the "Goldilocks altitude" — specific enough to guide behavior, flexible enough for edge cases — and keep prompts "minimal but complete" (start minimal on the best model, add instructions only for observed failure modes). The house shape, used by every tier and `<prj>-<domain>-expert` domain agent:

1. One **role sentence** ("You are a … assisting an orchestrator").
2. **`When invoked:`** numbered startup workflow — stops the agent wasting turns deciding how to begin.
3. **Domain invariants** (domain agents only) — the load-bearing facts to check every conclusion against, anchored by path and symbol name.
4. **Knowledge protocol** — which `docs/agent-knowledge/` notes to read as advisory leads, and how to return a PROPOSED KNOWLEDGE UPDATE.
5. **Operating rules** stating WHY each constraint exists.
6. **`Output`** contract (DELIVERABLES shape, `file:line` refs, evidence labels). Readers inherit the shared parts (evidence labels, timebox, citation self-scan, knowledge proposals) from the preloaded `house-agent-contract` skill; the body adds only role-specific rules.

## Description-driven delegation

The `description` field is the ONLY signal for automatic delegation. Official guidance, verbatim: "To encourage proactive delegation, include phrases like 'use proactively' in your subagent's description field." Lead with trigger conditions; official example description: "Expert code reviewer. Use proactively after code changes." Escalation levels when auto-delegation is not enough: natural language ("use the X agent") → `@agent-name` mention (guarantees invocation for one task) → `--agent` flag (entire session runs as that agent). Avoid an unquoted `: ` (colon-space) anywhere in the YAML value.

## Least-privilege tools

- **Allowlist, not denylist.** Every house agent pins `tools:`. Readers get `Read, Grep, Glob, Bash, Skill, ToolSearch`; writers get their own allowlist (e.g. `Read, Edit, Write` for `bulk-editor`). A denylist silently admits any tool added later, such as a new web-capable MCP server or `Agent`. An allowlist fails closed. `research-specialist` is the one exception: it keeps inherited web tools under `disallowedTools: Write, Edit, NotebookEdit, Agent`. The current boundary table is `.claude/rules/agents-roster.md` § Boundaries.
- Tools NEVER available inside subagents regardless of config: `AskUserQuestion`, `EnterPlanMode`/`ExitPlanMode` (unless permissionMode is `plan`), `ScheduleWakeup`, `WaitForMcpServers`. A subagent cannot ask the user anything — the dispatch prompt must carry every decision. (From the 2026-07-04 crawl; not re-verified 2026-09-25.)
- From building-effective-agents (agent-computer interface): invest as much in tool and prompt design as in behavior — "Put yourself in the model's shoes."
- **Web-research policy:** web tools (WebSearch, WebFetch, and your web-research skill/MCP, if any) belong SOLELY to `research-specialist`. It is cache-first: it checks `docs/agent-knowledge/research/` against the README's verify-before-use checklist (version match, fetch date and TTL, installed source, active-branch precedents) before searching. It searches only on a miss, a version mismatch, an explicit re-check, or a stale entry when the request is implementation-bound. It is **propose-only**: it returns a digest plus a PROPOSED NOTE, and the parent (or an assigned writer) applies it. Readers cite the shared notes and report uncached needs as RESEARCH GAP; writers STOP with `NEEDS_CONTEXT`. Residual gap: `Bash` can still reach documentation CLIs and `curl`, so the lock is instruction-level beyond the tool list. A user-global web-research skill (under `~/.claude/skills/`) is invisible to fresh clones.

## Model + effort routing

Official positioning (models overview) recommends starting with the default Opus model for most workloads and reaching for Fable for demanding reasoning and long-horizon agentic work, or when evals at higher Opus effort still fall short. **The tier table lives only in `.claude/rules/agents-roster.md`**; this section keeps the sourced rationale.

- **Effort, not model choice, is the cost lever within a family.** Per the docs the effort scale is calibrated per model, so compare relative cost by comparing effort levels on the same model, not by assuming labels transfer across models.
- **Fable caveats** (why a Fable pin should be reserved for the hardest tier, and why the review gate's per-call `model: "fable"` second opinion is trigger-gated):
  - The models overview rates Fable "Slower" than Opus.
  - Its per-token price is higher than Opus (see the models overview for current pricing).
  - Depending on plan and seat tier, it may bill to usage credits. Interactive sessions show a consent prompt, but under `-p` or the Agent SDK it bills "without asking". How that consent prompt behaves for a subagent is **unverified**, because the docs cover only the main session, background sessions and teammates.
  - Safety classifiers can re-run flagged requests on a different model.
  - Fable is unavailable under zero data retention unless Anthropic authorizes it.
  - Fable needs CLI v2.1.257+.
- **Haiku does not support effort** and has a smaller window, so pinning it gives up the effort lever; reserve it for mechanical tiers.

## Knowledge base (replaces per-agent memory)

House agents carry no `memory:` field. Durable, reusable knowledge lives in `docs/agent-knowledge/` — start at `INDEX.md`, which routes to `engineering/`, `domain/` and `research/`. The notes are **advisory leads**: re-verify every load-bearing claim in the current code before repeating it. Readers and specialists never write notes; they return a PROPOSED KNOWLEDGE UPDATE (target note path, exact text, evidence), and only the main thread or a writer with explicit ownership applies it. One lesson per change, update rather than duplicate, delete falsified notes, never copy what the repo or skills already record, and NEVER store secrets, PII, or sensitive data values.

## Two runtimes

Codex (`.codex/agents/*.toml`, `.agents/skills/`, `docs/agent-rules/`), if installed, is a parallel runtime over the same repo and the same `docs/agent-knowledge/` base. Shared facts stay in sync and tiers diverge on purpose; the rule is `.claude/rules/agents-roster.md` § Codex runtime.

## Orchestration patterns (engineering posts)

- **Orchestrator–workers** (the local-workflow pattern): a central model decomposes, delegates, and synthesizes — right when subtasks cannot be predicted upfront.
- **Parallelization:** *sectioning* (independent subtasks in parallel — one message, multiple dispatches) and *voting* (the same task run N times for consensus on high-stakes correctness).
- Subagents should return **condensed summaries (~1–2K tokens)** even if they burned tens of thousands exploring — demand structured DELIVERABLES, never whole-file dumps.
- Multi-agent wins when the task exceeds one context window, independent verification matters, parallel exploration pays, or verbose output should stay out of the parent context. Otherwise a single agent is simpler — simplicity is Anthropic's first stated design principle.

## Context budgeting & overflow recovery

- **Windows.** On the Anthropic API, the current Opus and Fable models run a native 1M window on every plan ("You don't select a `[1m]` variant"), and subagents auto-compact like the main conversation. There is **no fixed warm-reuse cap**: reuse a warm agent while its context is still relevant, and dispatch fresh with a digested brief when the thread changes (2–5K tokens of brief beats replaying a long transcript). A 200K limit still applies to smaller-window models such as Haiku, to any native-1M model under `CLAUDE_CODE_DISABLE_1M_CONTEXT=1`, and behind an LLM gateway where Claude Code cannot verify 1M support; there, keep resumes short.
- **Hard overflow is a 400, not a compaction event.** When a request's input alone exceeds the model's window, the API rejects it before anything runs (platform.claude.com/docs/en/build-with-claude/context-windows). Observed in practice: on a 200K window, a warm writer resumed several times died mid-run with "Prompt is too long", leaving partial edits — and it had completed MORE than its last progress message claimed.
- **Shard at dispatch (house heuristic, for quality and latency, not a window limit):** more than ~15–20 substantial files or >~100KB of source in one brief → split into parallel shards. Big windows do not cure context rot, and parallel shards finish sooner.
- **Overflow recovery:** a dead ID cannot be resumed (the resume replays the same over-long input and 400s again). Don't trust the last progress message; grep the working tree for one marker per scoped item, route the fully-specified remainder to `bulk-editor`, re-dispatch fresh for what still needs judgment.
- **`[1m]` suffix:** still accepted on aliases and full IDs, but it only matters for older models and LLM-gateway setups — not for native-1M models.

## Smoke-testing (house method, empirically validated)

1. Registry pickup: restart after an agent change (`.claude/rules/agents-roster.md` § Reload caveat). Until the restart, a dispatch can be told its loaded prompt is stale and to read its on-disk `.claude/agents/<name>.md` first.
2. Profile check: confirm in `/tasks` that the effective model and effort match the frontmatter before asserting either.
3. Meta-checks: confirm preloaded skills are actually in context (the agent cites skill facts with zero Read calls), the knowledge notes it should read are opened, and the `When invoked` workflow fires in order.
4. Real-task check: give it a genuine trace in its domain and verify the answer against the code yourself — an agent's report is a claim, not proof.
5. Knowledge check: any PROPOSED KNOWLEDGE UPDATE it returns names a real target note, carries evidence, is a useful delta (not a documentation copy), and contains no PII or sensitive data values — and the agent wrote nothing itself.
