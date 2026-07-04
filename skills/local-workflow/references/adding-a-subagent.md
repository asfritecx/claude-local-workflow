# Adding a house subagent

Read this when adding a new tier or specialist to `.claude/agents/` for the local-workflow orchestration pattern. The six house orchestration tiers (`code-digester`, `deep-analyst`, `code-developer`, `bulk-editor`, `skill-auditor`, `research-specialist`) are the worked examples for this pattern — copy the closest one; `code-developer` and `bulk-editor` are the two writer examples (judgment writer vs mechanical executor); `research-specialist` is the worked example of the **sole external-research tier**: repo read-only + its own memory doubling as a persistent research cache (`.claude/agent-memory/research-specialist/`), the only agent carrying web-research tools. **Domain-pinned roster agents** are built like tiers (read-only Sonnet readers, pinned effort) but scoped to one domain with invariants baked into the body. A **meta roster agent** is read-only, not domain-pinned, and responsible for workflow and agent sync audits. `.claude/agents/` may also hold standalone domain specialists that sit outside the roster system — dispatched directly by name for their own domain, not picked from the Agent roster in `SKILL.md`. Don't treat them as models when adding a new orchestration tier.

## Steps

1. **Create `.claude/agents/<name>.md`** with frontmatter:
   - `name` — matches the filename, lowercase + hyphens.
   - `description` — lead with the trigger conditions and a "use proactively / use for …" cue so the orchestrator auto-delegates. This is the only field used to decide delegation, so make it specific. Avoid an unquoted `: ` (colon-space) anywhere in the value — strict YAML validators truncate or reject it.
   - `model` — `sonnet` / `opus` / `haiku` / `fable` / `inherit`.
   - `effort` — `low`–`max`; overrides the session level (the whole point of pinning a tier).
   - `color` — a display color (`blue` / `purple` / `orange` / …).
   - **Tool boundary** — pin `tools:` to an allowlist for a writer (e.g. `Read, Edit, Write`), or set `disallowedTools: Write, Edit, NotebookEdit` to make a reader harness-enforced read-only. **Web-research tools belong ONLY to `research-specialist`** (see `subagent-best-practices.md` § Least-privilege tools for the lock policy). A NEW reader agent must carry the extended `disallowedTools` web-tool block that locks web-research tools away — point at any domain-expert agent's frontmatter (e.g. `.claude/agents/<prj>-<domain>-expert.md`) as the reference shape. A NEW writer agent gets no web tools at all and follows the Cache-verification protocol (check `.claude/agent-memory/research-specialist/` for fresh, version-matched research; STOP with `NEEDS_CONTEXT` on a gap rather than searching).
   - `skills` — list of project skills whose FULL content is preloaded into the agent's context at startup; prefer this over instructing the agent to Read SKILL.md itself (zero tool calls, no EISDIR gotcha). See `subagent-best-practices.md` § Frontmatter / config semantics for the ~40KB preload-budget heuristic and the `maxTurns` house convention (Bash-capable writers pin 30–50, mechanical writers and readers omit it).
   - `memory` — `user | project | local` persistent agent-memory directory; house default is `project` (`.claude/agent-memory/<name>/`, checked into git). The memory system injects MEMORY.md into the agent's system prompt and enables memory-dir writes even when `disallowedTools` blocks Write/Edit (verified empirically on v2.1.199 with a domain-pinned agent — repo files stayed blocked, memory writes succeeded). Pair it with a memory-protocol section in the body: what to save (drift, gotchas, shortcuts), one lesson per note, update-don't-duplicate, treat notes as hints not ground truth, never store secrets/PII/sensitive domain data.
   - `mcpServers` — scope MCP access per agent (server-name reference or inline config); agents inherit the session's MCP tools by default, so use this (or `disallowedTools` patterns) to narrow a specialist to only the servers it needs.
   - `hooks` — per-agent lifecycle hooks; hooks also fire inside subagents carrying `agent_id`/`agent_type` context, and `SubagentStart`/`SubagentStop` events exist at the session level. Use for per-agent enforcement a prompt alone can't guarantee.

2. **Write the body as the system prompt**, following Anthropic's efficient-subagent shape (code.claude.com/docs/en/sub-agents → "Example subagents"):
   - One **role sentence** ("You are a … assisting an orchestrator").
   - A **`When invoked:`** numbered workflow — the concrete startup procedure (read the pointed skill first → do the work → return the report). This is what stops the agent wasting turns deciding how to begin.
   - **Operating rules** that say *why* each constraint exists (the read/write boundary, "investigate before you answer," cite-URLs-for-external-facts).
   - An **`Output`** section describing the exact shape (numbered DELIVERABLES, `file:line` refs, verbatim quotes, confirmed-vs-inferred). Keep it minimal but complete.

3. **Registry pickup.** Treat ANY agent-definition change — a new file or an edit to an existing one — as needing a session restart before validation. Mid-session pickup is unreliable in practice: edits to an existing agent's body did NOT take effect mid-session (two consecutive dispatches ran the old session-start snapshot with the edits confirmed on disk, 2026-07-05), and new-file pickup is version- and situation-dependent. See `subagent-best-practices.md` § Smoke-testing for the empirical record. (The interactive `/agents` wizard was removed in v2.1.198 — agents are created/edited by editing the files directly.)

4. **Smoke-test** by dispatching it once on a tiny task, confirm the `When invoked:` workflow fires (it reads the pointed skill first and returns the structured report), then update the **Agent roster** table and **Keep in sync** list in `SKILL.md` to match.

## Domain expert maintenance

When changing a domain expert agent, apply these principles:

- Keep descriptions aligned by trigger and domain scope.
- Keep model/effort intent current — reflect any change in reasoning depth or tool boundary in the frontmatter.
- Keep boundaries aligned: use `tools` or `disallowedTools` to pin what the agent can touch.
- Keep read-first references aligned. Agents may preload active project skills via the `skills` frontmatter field, or be instructed to read the relevant skill's `SKILL.md` at startup.
- Keep domain invariants aligned with the canonical domain skill and current code.
- Review `.claude/agent-memory/<agent>/MEMORY.md` and note files. Update or delete stale notes only for durable drift, gotchas, or investigation shortcuts. Never store secrets, PII, or sensitive domain data.
- Smoke-test the changed agent with a small domain question and verify it reads or preloads the right context, follows its startup workflow, and returns file:line evidence.

## Design principles (from the best-practice sources)

- **One focused job per agent** — each excels at one task; don't blur tiers.
- **Limit tool access** to only what the job needs (security + focus).
- **Detailed description** drives delegation — vague descriptions don't get picked.
- **Pin model + effort** in frontmatter so the tier holds regardless of the session level.

For the sourced rationale behind these rules (official docs + Anthropic engineering posts, with URLs and verbatim quotes), read `subagent-best-practices.md` in this directory.
