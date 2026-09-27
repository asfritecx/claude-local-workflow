# Adding a house subagent

Read this when adding a new tier or specialist to `.claude/agents/` for the local-workflow orchestration pattern. The eight house orchestration tiers (`code-digester`, `deep-analyst`, `code-developer`, `bulk-editor`, `research-specialist`, `skill-auditor`, `code-reviewer`, `adversarial-reviewer`) are the worked examples for this pattern — copy the closest one; `code-developer` and `bulk-editor` are the two writer examples (judgment writer vs mechanical executor); `code-reviewer` and `adversarial-reviewer` are the two review-gate examples (defect pass vs design challenge), read-only (no Write or Edit; Bash writes are barred by instruction) and dispatched only after a code-changing wave; `skill-auditor` is the post-change docs auditor; `research-specialist` is the worked example of the **sole external-research tier**: repo read-only, checks the shared research notes in `docs/agent-knowledge/research/` first, returns a digest plus a PROPOSED NOTE for the parent to apply, and is the only agent carrying web-research tools. Any `<prj>-<domain>-expert` you install (template: `domain-expert-template.md`) is a **domain-pinned roster agent**: built like a tier (read-only reader, pinned model and effort) but scoped to one domain with invariants baked into the body. `localworkflow-sync` is the worked example of a **meta roster agent**: read-only, not domain-pinned, and responsible for local-workflow and agent sync audits. `.claude/agents/` may also hold your own domain-specialist writers, if any, that sit outside the roster system — they're dispatched directly by name for their own domain, not picked from the Agent roster in `SKILL.md`. Don't treat them as models when adding a new orchestration tier.

## Steps

1. **Create `.claude/agents/<name>.md`** with frontmatter:
   - `name` — matches the filename, lowercase + hyphens (no `:`).
   - `description` — lead with the trigger conditions and a "use proactively / use for …" cue so the orchestrator auto-delegates. This is the only field used to decide delegation, so make it specific. Avoid an unquoted `: ` (colon-space) anywhere in the value — strict YAML validators truncate or reject it.
   - `model` and `effort` — **pin a model and an explicit effort**, taken from the tier table in `.claude/rules/agents-roster.md`. The kit pins aliases (`opus`, `fable`, …); pin a full model ID instead when you need one exact snapshot (see `subagent-best-practices.md` § Current harness behavior for the family-alias rule).
   - `color` — a display color (`blue` / `purple` / `orange` / …).
   - **Tool boundary** — every agent pins a `tools:` allowlist.
     - A **reader** gets `tools: Read, Grep, Glob, Bash, Skill, ToolSearch`. That makes it harness-enforced read-only, with no web tools and no `Agent`. It also lists `house-agent-contract` in `skills:`, so its body carries only role-specific rules. Copy `.claude/agents/code-digester.md`'s frontmatter.
     - A **writer** gets its own allowlist (for example `Read, Edit, Write`) with no web tools. It checks `docs/agent-knowledge/research/`, using that README's verify-before-use checklist, and stops with `NEEDS_CONTEXT` on a gap rather than searching.
     - **Web tools belong only to `research-specialist`.** The boundary policy is in `.claude/rules/agents-roster.md` § Boundaries.
   - `skills` — list of project skills whose FULL content is preloaded into the agent's context at startup; prefer this over instructing the agent to Read SKILL.md itself (zero tool calls). See `subagent-best-practices.md` § Frontmatter / config semantics for the ~40KB preload budget heuristic and the `maxTurns` house convention (Bash-capable writers pin 30–50, mechanical writers and readers omit it).
   - **Never add `memory:`.** House agents carry no per-agent memory. Durable knowledge lives in the shared base `docs/agent-knowledge/` (start at `INDEX.md`): readers and specialists return PROPOSED knowledge updates, and only a writer with explicit ownership or the main thread applies them. Put a short knowledge-protocol section in the body instead: which `docs/agent-knowledge/` note to read, plus the pointer to the contract skill's proposal protocol.

2. **Write the body as the system prompt**, following Anthropic's efficient-subagent shape (code.claude.com/docs/en/sub-agents → "Example subagents"):
   - One **role sentence** ("You are a … assisting an orchestrator").
   - A **`When invoked:`** numbered workflow — the concrete startup procedure (read the pointed skill and knowledge note first → do the work → return the report). This is what stops the agent wasting turns deciding how to begin.
   - **Operating rules** that say *why* each constraint exists (the read/write boundary, "investigate before you answer," cite-URLs-for-external-facts).
   - An **`Output`** section describing the exact shape (numbered DELIVERABLES, `file:line` refs, verbatim quotes, evidence labels, PROPOSED KNOWLEDGE UPDATES). Keep it minimal but complete. For a reader, the preloaded `house-agent-contract` already supplies the evidence labels, NOT COVERED, the citation self-scan and the status vocabulary, so don't repeat them.

3. **Registry pickup.** Restart the session after any agent change. The reload caveat and its evidence live in `.claude/rules/agents-roster.md` § Reload caveat. (There is no interactive `/agents` wizard; agents are created and edited as files.)

4. **Smoke-test** by dispatching it once on a tiny task. Confirm the `When invoked:` workflow fires (it reads the pointed skill first and returns the structured report), and confirm the **effective** model and effort in `/tasks`, which shows them next to each agent — frontmatter is only the configured profile, so don't assert which model ran until `/tasks` shows it. Then update the keep-in-sync surfaces below.

## Keep in sync

Any new agent, or any change to an agent's role, boundary or tier, updates in the same pass:

- the **Agent roster** table (and the **Skill map**, for a domain expert) in `.claude/skills/local-workflow/SKILL.md`;
- `.claude/rules/agents-roster.md` — its tier table or Boundaries section;
- the Codex mirror `.codex/agents/<name>.toml`, if installed — **shared facts only**: description/role, read/write boundary, invariants, and paths. Codex is a parallel runtime with its own model/effort ladder; never copy Claude tiers into it or flag the tier difference as drift;
- for a `<prj>-<domain>-expert` that is added, renamed, or rescoped: the domain-note routing in `docs/agent-knowledge/domain/README.md`, and the Knowledge protocol note path in the agent body.

## Domain expert maintenance

When changing a domain expert (`.claude/agents/<prj>-<domain>-expert.md`), review every surface it touches:

- Dispatch `localworkflow-sync` for non-trivial changes or any change that touches the roster or the dispatch docs. It should return drift findings and exact edit specs; it should not edit files.
- Keep descriptions aligned by trigger and domain scope.
- Keep domain invariants aligned with the canonical domain skill and current code; anchor them by path and symbol name, not line number.
- Check the agent's domain note under `docs/agent-knowledge/domain/` still matches its area. Corrections go through the propose-then-apply flow; never store secrets, PII, or sensitive data values.
- If dispatch behavior changed, update `.claude/skills/local-workflow/SKILL.md`.
- Smoke-test the changed agent with a small domain question and verify it reads or preloads the right context, follows its startup workflow, and returns file:line evidence.

## Design principles (from the best-practice sources)

- **One focused job per agent** — each excels at one task; don't blur tiers.
- **Limit tool access** to only what the job needs (security + focus).
- **Detailed description** drives delegation — vague descriptions don't get picked.
- **Pin a model + explicit effort** in frontmatter so the tier holds regardless of the session's effort level (and pin a full model ID when the tier must not follow the session's model family).
- **Share boilerplate by preload, not by copy.** Rules common to every reader live in `house-agent-contract`; a body carries only what is specific to its role.

For the sourced rationale behind these rules (official docs + Anthropic engineering posts, with URLs and verbatim quotes), read `subagent-best-practices.md` in this directory.
