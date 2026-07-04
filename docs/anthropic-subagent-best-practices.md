# Anthropic subagent best practices — research findings

Compiled 2026-07-06 from official Claude Code / Claude API documentation, Anthropic engineering posts, and (clearly labeled) community reports. This document holds the *research layer* behind the kit: deeper operational facts that `skills/local-workflow/references/subagent-best-practices.md` — the curated house reference — deliberately keeps out to stay short. Read the reference first; come here when you need the economics, the platform mechanics, or the source trail.

Labels: **[OFFICIAL]** = docs.claude.com / code.claude.com / anthropic.com / claude.com blog. **[COMMUNITY]** = everything else — treat as *reported*, not fact.

---

## 1. Token economics — what multi-agent actually costs

**[OFFICIAL]** Anthropic's production numbers from their Research system: "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats." Token volume alone explained 80% of performance variance in their BrowseComp eval — the architecture buys performance by purchasing tokens. The stated gate: "For economic viability, multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance."
— https://www.anthropic.com/engineering/multi-agent-research-system

**[OFFICIAL]** A later framing gives 3–10× for typical multi-agent implementations, attributing the overhead to "duplicating context across agents, coordination messages between agents, and summarizing results for handoffs."
— https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them

**Kit takeaway:** the orchestrator pattern is a 3–15× token bet. It pays on breadth-first, high-value tasks; it loses on tasks a well-prompted single agent finishes in one pass.

## 2. Effort scaling belongs in the orchestrator prompt, not in code

**[OFFICIAL]** Anthropic's fix for overprovisioning ("Early agents made errors like spawning 50 subagents for simple queries") was scaling rules embedded in the prompt: "Simple fact-finding requires just 1 agent with 3-10 tool calls, direct comparisons might need 2-4 subagents with 10-15 calls each, and complex research might use more than 10 subagents with clearly divided responsibilities."
— https://www.anthropic.com/engineering/multi-agent-research-system

The kit encodes this as the SKILL.md rule "Scale the fan-out to the task"; this is its sourced rationale.

## 3. The 4-element delegation spec

**[OFFICIAL]** The load-bearing sentence for every dispatch prompt: "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries. Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information."
— https://www.anthropic.com/engineering/multi-agent-research-system

Documented production failure modes when this is skipped: duplicated work (two agents investigating the same supply-chain question), gaps ("without an effective division of labor"), and infinite search (agents "scouring the web endlessly for nonexistent sources"). The kit's dispatch template (CONTEXT / FIRST / DELIVERABLES / evidence format) maps 1:1 onto these four elements.

**[OFFICIAL]** Tool descriptions are part of the same interface problem: "Bad tool descriptions can send agents down completely wrong paths." Anthropic measured a 40% decrease in task completion time after an agent rewrote flawed MCP tool descriptions from observed failure modes — and notes "the Claude 4 models can be excellent prompt engineers" for diagnosing agent failures.
— https://www.anthropic.com/engineering/multi-agent-research-system

## 4. Context management: rot, anxiety, compaction vs reset

**[OFFICIAL]** "Context rot": "as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases" (n² attention spread). Prescription: "the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."
— https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

**[OFFICIAL]** Hand workers a compact brief, take back a condensed summary — e.g. a subagent that consumed a full order history returns "only the 50-100 tokens it actually needs."
— https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them

**[OFFICIAL]** Compaction vs reset for long-horizon work: "compaction preserves continuity, it doesn't give the agent a clean slate, which means context anxiety can still persist. A reset provides a clean slate, at the cost of the handoff artifact having enough state for the next agent to pick up the work cleanly." "Context anxiety" = agents "wrapping up work prematurely as they approach what they believe is their context limit"; Sonnet 4.5 exhibited it strongly enough that "compaction alone wasn't sufficient... so context resets became essential." Resets require a structured handoff artifact (progress file + git log + feature checklist an agent may mark `passes` on but never delete).
— https://www.anthropic.com/engineering/harness-design-long-running-apps and https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

**[OFFICIAL]** Subagents auto-compact with the same logic as the main conversation (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` applies; compact events logged in the subagent transcript as `compact_boundary`). Main-conversation compaction does not touch subagent transcripts. "Project-root CLAUDE.md and auto memory survive compaction and reload from disk; instructions given only in conversation may be lost." See §4b for the hard-overflow case compaction cannot save.
— https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/glossary

**[COMMUNITY]** Reported: a long-running subagent can compact itself mid-task and the parent only ever sees the final return value — one more reason to bound each dispatch to a single well-defined subtask.
— https://neural-llm.com/blog/guides/claude-code-auto-compact-context-loss

## 4b. Operational context budgeting — the house layer on §4

Incident-derived (reference deployment, 2026-07-05): a warm writer agent continued via `SendMessage` for a 4th sequential work phase died mid-run with "Prompt is too long" (API 400), leaving partial edits in the working tree — and it had completed MORE items than its last progress message claimed.

**[OFFICIAL]** Hard overflow is a request rejection, not a compaction trigger: when a request's input alone exceeds the model's context window, the API returns a validation error before anything runs — so §4's auto-compaction (which protects a conversation *growing* toward the limit) cannot rescue a resume whose replayed transcript is already too long at dispatch time.
— https://platform.claude.com/docs/en/build-with-claude/context-windows

**Growth model (empirical):** every `SendMessage` resume replays the agent's full prior transcript as input. A substantive work phase (file reads + tool results + an 8-item report) adds roughly 50–80K tokens, so phases 3–4 cross a 200K window.

House rules:

1. **Cap warm reuse at 2 — exceptionally 3 — work phases** in the same files. Past the cap, dispatch a FRESH agent with a digested brief: 2–5K tokens of brief beats replaying a 150K-token transcript, and the fresh agent starts with full headroom.
2. **Shard at dispatch:** a brief pointing one reader at more than ~15–20 substantial files or >~100KB of source gets split into parallel shards. 100KB ≈ 25–35K raw tokens, and a reader's transcript amplifies its reading 2–3× (search output, re-reads, report drafting) — one such scope ≈ 50–100K transcript tokens, safe once in a 200K window, not twice. (House heuristics, not API limits.)
3. **One well-defined subtask per dispatch** (§4's community report is one more reason) — open-ended "continue with the next phase" resumes are where transcripts quietly compound.
4. **Overflow recovery:** a dead agent ID cannot be resumed — the resume replays the same over-long input and 400s again. Don't trust the last progress message (see the incident). Inventory the working tree directly: grep one marker per scoped item (the identifier each item introduces), route the fully-specified remainder to the mechanical-edit tier, re-dispatch a fresh writer for what still needs judgment.
5. **`[1m]` escape hatch (secondary):** agent frontmatter `model:` accepts the same values as `--model`, including 1M-context aliases like `sonnet[1m]`. 1M context bills at standard pricing ("no premium for tokens beyond 200K") with no beta header, but availability varies by plan and model — and §4's context rot argues for sharding first regardless of window size.
— https://code.claude.com/docs/en/model-config and https://code.claude.com/docs/en/sub-agents

## 5. Prompt-caching economics for subagent dispatch

**[OFFICIAL]** API pricing mechanics: default cache TTL 5 minutes (1-hour tier costs more); cache-write (5m) = 1.25× base input, cache-write (1h) = 2×, cache-read = 0.1×; caching is an exact prefix match — "Any change anywhere in the prefix invalidates everything after it."
— https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching and https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything

**[OFFICIAL]** How this lands on subagents: a subagent starts its own isolated conversation, so it "builds its own cache from scratch" — no hits on its first call. Subagents use the 5-minute TTL even on subscriptions where the main conversation gets the automatic 1-hour TTL. A *fork* (unlike a subagent) inherits the parent's prefix exactly and cache-hits it. Parallel subagents each independently bill cache reads: N agents × K context tokens = N×K cache-read tokens, no deduplication.
— https://code.claude.com/docs/en/prompt-caching

**[COMMUNITY]** Reported quirks: every fresh subagent spawn incurs ~4.7K tokens of cache_creation because the trailing environment block (gitStatus, cwd, date) sits after the last cache marker (https://github.com/anthropics/claude-code/issues/50213); parallel fan-outs accumulate large cache-read volumes with no per-session cap — still 0.1× rate, but material at scale (https://github.com/anthropics/claude-code/issues/46421).

**Kit takeaway:** repeated dispatches of the same agent type within ~5 minutes warm its cache; a big simultaneous fan-out all cold-starts. Cheap per-token, but budget for the multiplier in §1 rather than expecting cache to erase it.

## 6. Verification: never let the generator grade itself

**[OFFICIAL]** "When asked to evaluate work they've produced, agents tend to respond by confidently praising the work—even when, to a human observer, the quality is obviously mediocre." The structural fix: "Separating the agent doing the work from the agent judging it proves to be a strong lever... tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work." Related pattern: generator and evaluator agree a "sprint contract" — what done looks like — before work starts.
— https://www.anthropic.com/engineering/harness-design-long-running-apps

**[OFFICIAL]** The verification subagent is "one multi-agent pattern that consistently works well across domains." Caveat: "more capable orchestrator models... are increasingly able to evaluate subagent work directly without a separate verification step," but dedicated verifiers stay valuable with weaker orchestrators, specialized verification tooling, or when you want enforced checkpoints.
— https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them

This is the sourced rationale for the kit's "Quality-control what agents do — you own it" section and its independent review gate.

## 7. Topology: when multi-agent loses

**[OFFICIAL]** "Decomposition follows context, not problem type. Group work by what context it requires, not by what kind of work it is." Direct cautions: teams "invest months building elaborate multi-agent architectures only to discover that improved prompting on a single agent achieved equivalent results," and pipelines with per-stage agents "suffered from lost context at each handoff and spent more tokens coordinating than executing."
— https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them

**[OFFICIAL]** Fit boundary: "some domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems today. For instance, most coding tasks involve fewer truly parallelizable tasks than research." Multi-agent "excel[s] especially for breadth-first queries that involve pursuing multiple independent directions simultaneously." The often-quoted 90.2% improvement figure comes from an internal breadth-first research eval — it does not generalize to coding.
— https://www.anthropic.com/engineering/multi-agent-research-system

## 8. Permission and trust model (parent ↔ subagent)

**[OFFICIAL]** "Subagents inherit the internal tools and MCP tools available in the main conversation by default." Spawning a subagent doesn't itself prompt; each of the subagent's own tool calls is checked against your permission rules. Precedence: "If the parent uses `bypassPermissions` or `acceptEdits`, this takes precedence and can't be overridden. If the parent uses auto mode, the subagent inherits auto mode and any `permissionMode` in its frontmatter is ignored." Plan-mode carveout: plan routes file-edit and shell-write tools to the permission callback "regardless of allow rules, so write operations cannot be auto-approved while planning."
— https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/agent-sdk/permissions.md

**[OFFICIAL]** Hooks DO fire inside subagents, with `agent_id` and `agent_type` added to the hook input; dedicated `SubagentStart` / `SubagentStop` events exist, and project hooks can target one agent by matching `agent_type`. Per-subagent `hooks:` frontmatter is also supported (auto-converting `Stop` → `SubagentStop`).
— https://code.claude.com/docs/en/hooks and https://code.claude.com/docs/en/sub-agents

## 9. MCP tools inside subagents

**[OFFICIAL]** Inherited by default; scopable per agent via the `mcpServers` frontmatter field (server name reference or inline config), and removable via `disallowedTools` patterns (`mcp__server__*`, `mcp__*`). On the SDK surface, "MCP tools require explicit permission before Claude can use them"; prefer `allowedTools` over permission modes — `acceptEdits` does NOT auto-approve MCP tools.
— https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/agent-sdk/mcp.md

**NOT DOCUMENTED:** whether MCP server connections are shared or re-established per subagent, and per-subagent MCP auth behavior.

## 10. Structured output from subagents

**[OFFICIAL, SDK-only]** `outputFormat` / `output_format` on `query()` validates the agent's output against a JSON Schema, re-prompting on mismatch (Zod/Pydantic supported). It applies to the top-level query, NOT per `AgentDefinition` — from the parent's perspective a subagent's return value is always free-form final-message text. Failure modes: schema too complex, ambiguous task, retry limit, or "a model fallback can retract an already-completed output mid-stream."
— https://code.claude.com/docs/en/agent-sdk/structured-outputs

**Kit takeaway:** in CLI orchestration, the DELIVERABLES contract in the dispatch prompt is the only output-shaping lever for file-based subagents — which is why the kit's template makes it numbered and explicit. (Workflow scripts' `agent(..., {schema})` is the exception on the workflow surface.)

## 11. Observability and debugging

**[OFFICIAL]** OpenTelemetry: metrics (`OTEL_METRICS_EXPORTER`), log events (`OTEL_LOGS_EXPORTER`), and beta traces (`OTEL_TRACES_EXPORTER` + `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`) with per-tool-call and hook spans; all off until `CLAUDE_CODE_ENABLE_TELEMETRY=1`.
— https://code.claude.com/docs/en/agent-sdk/observability.md

**[OFFICIAL]** `/usage` attributes token usage to skills, subagents, plugins, and MCP servers (v2.1.174+); the dollar figure is a local estimate. `/usage-credits` sets monthly spend limits. Sessions (incl. subagent transcripts) persist under `~/.claude/projects/` with `continue`/`resume`/`fork` semantics; transcripts are cleaned up per `cleanupPeriodDays` (default 30).
— https://code.claude.com/docs/en/costs and https://code.claude.com/docs/en/agent-sdk/sessions.md

## 12. `isolation: worktree` in depth

**[OFFICIAL]** Creates a separate checkout under `.claude/worktrees/<name>/` on branch `worktree-<name>`, sharing the main `.git`. Branches from `origin/HEAD` by default (`worktree.baseRef: "head"` uses local HEAD). `.worktreeinclude` (gitignore syntax) copies matching gitignored files (e.g. `.env`) into new worktrees. Cleanup: unchanged worktrees are removed automatically; with changes, Claude prompts keep/remove and returns the branch + path to the parent; non-interactive runs don't auto-clean; a background sweep removes clean worktrees older than `cleanupPeriodDays`. Locked (`git worktree lock`) while the agent runs. Use when parallel agents would touch the same files; skip for read-only or single-file tasks.
— https://code.claude.com/docs/en/worktrees and https://code.claude.com/docs/en/sub-agents

**[COMMUNITY]** Reported: the no-change auto-reap breaks `SendMessage` resume — a worktree-isolated agent that returns without file changes loses its worktree, and resuming it then violates its cwd preflight (https://github.com/anthropics/claude-code/issues/50889). If a worktree agent must be resumable, have it commit something (even `--allow-empty`) before returning.

## 13. Concurrency, rate limits, nesting

**[OFFICIAL]** No numeric cap is documented for ad-hoc parallel subagent dispatch — the effective constraint is the account's rate limit ("Running several sessions or subagents at once multiplies token usage"). Dynamic workflows are capped at 16 concurrent agents ("fewer on machines with limited CPU cores") and 1,000 agents per run. Nesting: subagents can spawn subagents to 5 levels (v2.1.172+); "the limit is fixed and not configurable."
— https://code.claude.com/docs/en/workflows , https://code.claude.com/docs/en/agents.md , https://code.claude.com/docs/en/sub-agents

**[OFFICIAL]** v2.1.199 hardened fan-out failure handling: transient 429s auto-retry with backoff; subagents cut off by rate limits return partial work instead of silently failing; API errors no longer report as successful results; `SendMessage` no longer misroutes when a respawned agent reuses a prior agent's name. Scope note: this partial-work guarantee covers rate-limit cutoffs — a hard context-window overflow on a resume (400) returns nothing at all; see §4b.
— https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md

**[COMMUNITY]** Reported: several concurrent workflow runs from one account triggered 429/500/529 storms — concurrency is bounded by the plan's TPM, not by the tool (https://github.com/anthropics/claude-code/issues/64177); the workflow cap resolves as `min(16, cpu_cores - 2)` locally (https://github.com/anthropics/claude-code/issues/63938).

## 14. Registry pickup and hot-reload — docs vs observation

**[OFFICIAL]** Current docs: Claude Code watches `~/.claude/agents/` and `.claude/agents/` and "picks up a new or edited agent file within a few seconds, with no restart needed" — BUT "the watcher covers only directories that existed when the session started, so the first file in a new directory needs a session restart" (the most common cause of agents not loading). Other documented causes: invalid YAML frontmatter, duplicate `name`, `--disable-slash-commands` sessions, and a programmatic agent silently overriding a filesystem agent of the same name.
— https://code.claude.com/docs/en/agent-sdk/subagents

**Empirical (this kit's reference deployment, 2026-07-04/05):** neither new-file pickup nor edits to an existing agent definition took effect mid-session, with the `agents/` directory pre-existing — dispatches ran the session-start snapshot. The safe rule stands regardless of what the watcher promises: **treat any agent-definition change as needing a fresh session before validation.** See the curated reference's Smoke-testing section.

## 15. Corrections this research produced

Applied to `references/subagent-best-practices.md` (and its source-repo counterpart) on 2026-07-06:

1. **Registry pickup** — added the officially documented new-directory restart caveat alongside the empirical fresh-session rule (§14 above).
2. **`effort` enumeration** — official AgentDefinition accepts `'low' | 'medium' | 'high' | 'xhigh' | 'max' | number`; the reference previously omitted `medium` and the numeric form (https://code.claude.com/docs/en/agent-sdk/subagents).
3. **Explore model cap** — the Opus cap on Explore's inherited model applies only on the Anthropic API; on other providers (Bedrock, etc.) Explore inherits the session model directly, uncapped (https://code.claude.com/docs/en/sub-agents).
4. **Worktree + resume caveat** — noted next to the SendMessage continuation guidance (§12 above).

## Sources

Official docs: https://code.claude.com/docs/en/sub-agents · https://code.claude.com/docs/en/agent-sdk/subagents · https://code.claude.com/docs/en/agent-sdk/permissions.md · https://code.claude.com/docs/en/agent-sdk/mcp.md · https://code.claude.com/docs/en/agent-sdk/structured-outputs · https://code.claude.com/docs/en/agent-sdk/observability.md · https://code.claude.com/docs/en/agent-sdk/sessions.md · https://code.claude.com/docs/en/hooks · https://code.claude.com/docs/en/worktrees · https://code.claude.com/docs/en/workflows · https://code.claude.com/docs/en/costs · https://code.claude.com/docs/en/prompt-caching · https://code.claude.com/docs/en/glossary · https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching · https://code.claude.com/docs/en/model-config · https://platform.claude.com/docs/en/build-with-claude/context-windows

Engineering posts: https://www.anthropic.com/engineering/building-effective-agents · https://www.anthropic.com/engineering/multi-agent-research-system · https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents · https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents · https://www.anthropic.com/engineering/harness-design-long-running-apps · https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them · https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything

Community (reported, not verified): GitHub issues #50213, #46421, #50889, #63938, #64177 on https://github.com/anthropics/claude-code · https://neural-llm.com/blog/guides/claude-code-auto-compact-context-loss
