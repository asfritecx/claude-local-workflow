# Claude Code subagents, skills, hooks and workflows

Fetched 2026-09-27 from the live Claude Code docs (`code.claude.com/docs/en/<page>.md`), with Claude Code CLI v2.1.283 installed. Model and effort sections confirmed unchanged from a fetch two days earlier (v2.1.282). TTL 30 days.

Re-check `claude --version` and refresh through the research specialist before relying on a version-gated claim. Search-engine caches of these pages lag by dozens of versions; fetch the raw `.md` pages instead. Lines marked "observed in one installation" are local observations, not docs facts.

## Model values and aliases

Subagent frontmatter `model` accepts `sonnet`, `opus`, `haiku`, `fable`, a full model ID, or `inherit`. On the Anthropic API, Bedrock, Claude Platform on AWS and Google Cloud, `opus` resolves to Opus 5.5 (v2.1.280+). On Foundry it resolves to Opus 4.6. `fable` resolves to Fable 5.1 (v2.1.257+). `best` means `fable` where Fable is available, otherwise `opus`. Aliases move over time; full IDs pin a version.

**Family-alias rule.** If the main session's model is in the alias's family, a per-call or frontmatter alias resolves to the session's exact model, including `[1m]`. An alias in `CLAUDE_CODE_SUBAGENT_MODEL` always resolves to the alias target. Pin a full ID in frontmatter to hold a tier.

**Resolution order.** 1) per-call `model`; 2) frontmatter `model`; 3) `CLAUDE_CODE_SUBAGENT_MODEL`; 4) the session model. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+) forces it on every subagent, teammate and workflow agent. A per-call model sticks on resume (v2.1.211+). Subagents inherit the session's thinking setting.

**Agent tool schema (v2.1.283).** `model` is the enum `sonnet|opus|haiku|fable` only: no full IDs and no per-call effort. `mode` is deprecated and ignored (v2.1.212+). `isolation` accepts `worktree` or `remote`. There is no `run_in_background` parameter; subagents run in the background by default (observed in one installation from the v2.1.283 tool schema). `Task` is still accepted as an alias of `Agent`. For a cross-family second opinion, pass another family's alias per call. For a same-family different version, use a separate agent file with a full ID.

## Effort

Frontmatter `effort` accepts `low`, `medium`, `high`, `xhigh` and `max`; the default inherits the session. Fable 5.1/5, Opus 5.5/5, Sonnet 5 and Opus 4.8/4.7 support all five. Opus 4.6 and Sonnet 4.6 support all except `xhigh`. Unlisted models, including Haiku 4.5, don't support effort. An unsupported level falls back to the highest supported one at or below it. The default is `high`, except Opus 5.5 (`medium`) and Opus 4.7 (`xhigh`). `/tasks` shows effective model and effort (v2.1.242+).

## Context windows and Fable caveats

The native 1M window applies to Fable 5.1/5, Sonnet 5 and Opus 4.7+ on the Anthropic API. The `[1m]` suffix matters only for Opus/Sonnet 4.6 and gateways. A subagent's window is sized by its own model. Fable 5.1 costs $10/$50 per MTok against Opus 5.5's $4/$20, is slower, and may bill to usage credits (no consent prompt under `-p` or the SDK). How the consent prompt behaves for subagents is unverified. Classifier fallbacks re-run biology-flagged requests on Opus 5 and cyber-flagged requests on Opus 4.8.

## Subagent frontmatter

`name` (no `:`), `description`, `tools` (comma string or YAML list), `disallowedTools` (a specifier entry removes the whole tool), `model`, `permissionMode`, `maxTurns` (output marked partial and resumable, v2.1.246+), `skills` (full content preloaded; skills with `disable-model-invocation` can't be preloaded), `mcpServers`, `hooks`, `memory` (`user`/`project`/`local`), `background`, `omitClaudeMd`, `effort`, `isolation: worktree` (branches from the default branch, not HEAD), `color`, `initialPrompt` (only with `--agent`), `experimental.cacheTtl` (`5m`/`1h`). `hooks`, `mcpServers`, `permissionMode` and `initialPrompt` are ignored for plugin agents. A project agent named `Explore` overrides the built-in.

## Permission modes and plan mode

An unset `permissionMode` inherits the main session's mode. If the main session is in `bypassPermissions`, `acceptEdits` or auto, the subagent runs in that mode and its own `permissionMode` is ignored. If the main session is in `default`, `dontAsk` or `plan`, the subagent runs in the mode it declares, except `bypassPermissions` (v2.1.267+). **So a custom agent declaring `acceptEdits` can edit during plan mode.** Enforce read-only with `tools`/`disallowedTools`. The docs give no specific guidance for custom agents in plan mode; the built-in Plan agent is read-only with Write/Edit denied.

## Tools removed from subagents and background behavior

Every subagent loses `AskUserQuestion`, `EnterPlanMode`, `ScheduleWakeup`, `TaskOutput`, `Workflow`, `WaitForMcpServers` and `EndConversation`. It loses `ExitPlanMode` unless its own mode is `plan`, and `Agent` at the depth limit. Subagents have run in the background by default since v2.1.198. Background subagents keep all MCP tools but only a fixed built-in subset (Read, Grep, Glob, Bash, Edit, Write, WebFetch, WebSearch, TodoWrite, Skill, ToolSearch, worktree tools, Monitor, TaskStop, SendMessage, Artifact and a few others). Removal is silent unless it leaves `tools` empty. Permission prompts from background agents surface in the main session. Results arrive as a completion notification in a later turn, and Claude waits for it (reliable since v2.1.211). Forks inherit the full context and tool pool.

Observed in one installation (v2.1.283, after a restart): readers pinned to `tools: Read, Grep, Glob, Bash, Skill, ToolSearch` listed only `Read, Bash, Skill` (plus `SubagentHandback`). That build exposed no Grep/Glob tools, not even on the main thread, so search ran through Bash; subagents also got no `ToolSearch`. The pin is still correct: it is what excludes web, MCP, `Agent`, `Write` and `Edit`.

## Skills

Frontmatter: `name`, `description`, `when_to_use` (1,536 characters combined with `description`), `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools` (pre-approves for the invoking turn only; restricts nothing), `disallowed-tools`, `model` and `effort` (current turn only), `context: fork`, `agent`, `background` (v2.1.218+), `hooks` (stay registered for the rest of the session; `once: true` removes one after its first successful run), `paths` (globs for auto-activation), `shell`, `metadata`, `license`, `compatibility`. `context: fork` runs the body as a new subagent's prompt, without conversation history. It runs in the background by default, with the background tool set, and outside checkpoints. It is not a conversation fork. Rendered skill content stays in context but is not re-read; re-invoke after compaction.

## Hooks

Events include SessionStart, Setup, UserPromptSubmit, UserPromptExpansion, Pre/PostToolUse, PostToolUseFailure, PostToolBatch, PermissionRequest/Denied, Notification, MessageDisplay, SubagentStart/Stop, TaskCreated/Completed, Stop, StopFailure, TeammateIdle, InstructionsLoaded, ConfigChange, CwdChanged, DirectoryAdded, FileChanged, WorktreeCreate/Remove, Pre/PostCompact, Pre/PostModelSwitch, Elicitation/Result and SessionEnd.

- Stop and SubagentStop: `decision: "block"` with `reason` (or exit 2) continues the turn. `hookSpecificOutput.additionalContext` continues it without an error label. Guard with `stop_hook_active`; there is an 8-continuation cap (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`). A SubagentStop block sends `reason` to the subagent as its next instruction.
- To inform the parent after a subagent returns, use PostToolUse with matcher `Agent`. Whether a `Task` matcher fires is undocumented.
- SessionStart matchers: `startup`, `resume`, `clear`, `compact`, `fork`. Context only.
- PreCompact can block; PostCompact receives `compact_summary` and has no control.
- TaskCompleted and TeammateIdle: exit 2 blocks with feedback.
- PreToolUse: exit 2 blocks the tool call and sends stderr to Claude, for the main thread and subagents alike (observed in one installation: a PreToolUse Bash guard such as `.claude/hooks/git-guard.sh` blocked subagent Bash calls; not a docs fetch). A hook added before a compaction was live after it; whether a mid-session hook edit takes effect without a restart or compaction is still unverified.
- Exit-code collision: `python3 <script>` itself exits 2 when the script is missing or unreadable (`[Errno 2]`, `[Errno 13]`); syntax errors and uncaught exceptions exit 1. A wrapper that maps a Python exit 2 to a PreToolUse block therefore blocks every matched call when its parser file is absent. Signal a block with a code the interpreter never uses and map that to 2 (`.claude/hooks/git-guard.sh` uses 10). Observed in one installation, raised independently by two reviewers.
- `additionalContext` over 10,000 characters is written to a file. Phrase it as facts, not commands, because imperative text can trip prompt-injection defenses.
- `type: "prompt"` and `type: "agent"` hooks (agent hooks are experimental) work on Stop, SubagentStop, TaskCompleted, Pre/PostToolUse and a few others.
- Subagent-frontmatter hooks run only while the agent runs, and `Stop` becomes `SubagentStop`.

## Dynamic workflows

Requires v2.1.154+. Saved scripts live in `.claude/workflows/` or `~/.claude/workflows/` and run as `/<meta.name>`. `/reload-skills` re-reads them. The `Workflow` tool takes `name`, `scriptPath` or `script`, plus `args` (real JSON, read as the global `args`) and `resumeFromRunId` (same session only; completed calls with unchanged inputs return cached results). It returns asynchronously; completion arrives later. The script is plain JS whose first statement is `export const meta = { name, description, phases? }`, a pure literal. `Date.now()`, `Math.random()` and argless `new Date()` throw. `agent()` supports `schema` (validated, 5 retries) and a model override (per-call precedence). The bundled `/workflow-authoring` skill (v2.1.248+) also documents `agentType` (same registry as the Agent tool), `effort`, `isolation` and `label`/`phase`. Limits: up to 16 concurrent agents, 1,000 per run, no mid-run user input. Workflow agents run in `acceptEdits`. Only the main conversation can call `Workflow`. Allow rule: `Workflow(<name>)`. Unverified: whether `agent()`'s `model` accepts full IDs.

## Output styles, /loop and Monitor

Output styles live in `.claude/output-styles/` or `~/.claude/output-styles/`. Select with `/output-style <name>` (v2.1.269+), `/config`, or `outputStyle` in settings. Instructions go with every request; mid-session switches apply from the next message (v2.1.251+). Set `keep-coding-instructions: true` to keep engineering guidance. Styles don't reach named subagents, only forks. New or edited style files need a restart.

`/loop` without an interval self-paces through `ScheduleWakeup`: 1 minute to 1 hour, `stop: true` ends it, and a fallback wakeup fires about 20 minutes after an iteration that doesn't reschedule. Loops are session-scoped with 7-day expiry; `.claude/loop.md` sets the default prompt. On Bedrock, Vertex and Foundry the interval is a fixed 10 minutes.

Monitor streams script stdout lines or WebSocket frames as events. Default deadline 5 minutes, maximum 30, and 10 under `-p`. It follows Bash permission rules and is unavailable on Bedrock, Vertex and Foundry, or with telemetry or nonessential traffic disabled.

## Reload behavior

The docs say agent files are watched and the next delegation uses the edited definition. Observed in one installation, on more than one occasion: edited agent bodies stayed stale mid-session. Restart and smoke-test after any agent change. Skill `SKILL.md` text is live-reloaded; output-style files are not. Not re-checked: the claim that the interactive `/agents` wizard no longer exists.

Primary sources:

- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/model-config
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/workflows
- https://code.claude.com/docs/en/agent-sdk/typescript (Agent, Workflow, Monitor tool schemas)
- https://code.claude.com/docs/en/output-styles
- https://code.claude.com/docs/en/scheduled-tasks
- https://code.claude.com/docs/en/tools-reference
- https://code.claude.com/docs/en/permission-modes
- https://platform.claude.com/docs/en/about-claude/models/overview

Verification targets: installed CLI version; the Agent tool `model` enum; the effective model and effort per agent in `/tasks`; subagent `permissionMode` behavior under plan mode; `agent()` `agentType` and full-ID `model` in a saved workflow; a `Task` vs `Agent` hook matcher; Stop-hook continuation behavior on the current build; agent reload after restart.
