---
name: local-workflow
description: Use when tackling any substantial multi-step task in a project where answering well means reading or researching across many files, project skills, or external sources — research, analysis, security audits, cross-file debugging, planning, implementing or reviewing a feature, or "look into / analyze / investigate / build / review X". The house orchestration workflow; delegate reading to parallel subagents and synthesize yourself. Triggers on "be an orchestrator", "use sonnet agents", "don't read the code yourself", "delegate this", "digest/summarize the codebase", or any task big enough to need fan-out. Do NOT use for trivial single-fact lookups or one-line edits you can finish in one step. You MUST follow this workflow strictly.
user-invocable: true
---

# Local orchestration workflow — delegate, don't bulk-read

The house pattern for substantial tasks: **you are an orchestrator.** You do not bulk-read code or docs in the main thread — you decompose the task, fan out Sonnet subagents to read and research in parallel, review what comes back, fill gaps, then synthesize the answer yourself. The orchestrator holds the conclusion; the agents do the reading. DO NOT use generic Explore agents.

```
Task ──▶ [Orchestrator = you]
            │  1. decompose into independent threads
            ├──▶ code-digester  (digest a subsystem / read a skill+code)  ─┐
            ├──▶ code-digester  (audit / second angle)                    ├─▶ reports
            └──▶ research-specialist (external research — cache-first)    ─┘
            │  3. review reports → find gaps & contradictions
            └──▶ deep-analyst   (hard trace / verbatim extraction)        ─▶ report
            │  changes to make? delegate the writing (you never write repo files)
            ├──▶ code-developer (authors code, verifies against the research cache, self-checks) ─▶ diff report
            └──▶ bulk-editor    (applies fully-specified mechanical specs)     ─▶ edit report
            │
            ▼  5. synthesize: decisions + recommendations + next step (you, main thread)
            ▼  6. changed code? → run your review gate on the diff (independent check — never auto-fix)
            ▼  7. changed behavior? → skill-auditor re-checks the docs layer (skills + rules)
            ▼  8. durable lesson? → capture it as a path-scoped rule (.claude/rules/)
```

## The loop

1. **Decompose** the task into independent threads — one per subsystem, perspective, or knowledge source (e.g. "digest the architecture", "audit it", "research the external standard"). Threads must not depend on each other's output. **Scale the fan-out to the task:** a single-subsystem digest is 1 agent; a typical cross-file task 2–4 threads; a comprehensive audit or "be thorough" request 5+ plus a second wave. Agents are bad at judging effort on their own — you set it at dispatch. Scale by **reading volume** too, not just thread count: a brief pointing one agent at more than ~15–20 substantial files or >~100KB of source will burn most of its context window before it reports — split it into parallel shards, each returning its own digest. **For code-authoring tasks, also evaluate complexity against the phased-mode entry criteria** — spans ≥2 subsystems, ~4+ files each carrying a design decision, schema+code+UI stacked in one change, or needing more than one `code-developer` dispatch — and propose a phase list at a run-start STOP when it qualifies; see `references/phased-execution.md`.
2. **Pick each thread's skills, then dispatch in parallel.** Choose which project skills each thread needs via the **Skill map** below and name the exact `.claude/skills/<skill>/SKILL.md` paths in that agent's prompt. Then fire every independent agent in ONE message, dispatching by `subagent_type` from the **Agent roster** below.
3. **Review + gap-check.** Read the reports. Look for missing pieces, contradictions, or a finding that reframes the task (e.g. an existing fix that *should* have already solved the problem).
4. **Follow-up dispatch.** Send focused agents to close gaps — often a VERBATIM extraction ("quote rules 11001–11008 exactly") so you can reason on ground truth, not paraphrase. Don't stop at the first wave; the sharpest insight usually comes from the second.
5. **Synthesize.** Reconcile the reports into the answer: make the decision, separate confirmed facts from speculation, and end with the concrete next step. This is your job, not an agent's — never just concatenate agent outputs.
6. **Gate the delta through review.** At synthesis, classify `git status`: any changed repo file outside the project's user-granted docs-only waiver (if it has one — note it in the ledger when applied) → self-verify first (git diff, typecheck/lint), then run your project's independent review gate on the diff — see Quality-control below. Zero changed files is the only other skip, recorded in the ledger — never a judgment. **In phased runs, this step's timing changes:** the gate runs per phase, on the phase delta, as each phase completes rather than once at synthesis — clean → orchestrator commits + auto-advances to the next phase, any finding → STOP. The final synthesis still closes step 6's dispositions for the whole run. See `references/phased-execution.md`.
7. **Audit docs staleness after the change lands.** After any run that changed repo files, establish coverage mechanically: grep the changed paths and key symbols across `.claude/skills/**` and `.claude/rules/**`, and always expand relevant `.claude/agent-memory/<prj>-*/` directories derived from the touched domain(s). Any skill/rule hit or any relevant memory file → dispatch one read-only docs verdict pass — the touched domain's `<prj>-<domain>-expert` if exactly one domain owns the change and a matching expert exists (it may refresh its own memory in the same pass), else `skill-auditor` when available, else `code-digester` as fallback only with the `skill-auditor` Output contract pasted into the brief; it returns FRESH/STALE verdicts with exact old→new edit specs (root CLAUDE.md and auto-memory flag-only; domain memory flag-only when reported by `skill-auditor`). Dispatch owning `<prj>-*` experts for any domain-memory refreshes the auditor flags, then apply doc specs via `bulk-editor` in the same run. Zero-hit n/a requires no skills/rules grep hits and no relevant memory files; paste that evidence into the ledger. "Not warranted" from memory is never a disposition. Read `references/skill-staleness-audit.md` for the brief skeleton.
8. **Capture durable lessons as project rules.** A confirmed review finding or a mid-run gotcha that would bite again becomes a small path-scoped `.claude/rules/` file. Gate-derived proposals ride the step-6 STOP (fixes and rules approved together); qualifying quirks are created via `bulk-editor` and reported in the synthesis. Read `references/rule-capture.md` for the rule-worthiness bar, the dedupe ladder, and the rule shape.

**The loop is binding.** A step is never self-skipped: if you believe one doesn't apply, surface that as a proposal at a STOP — the user decides, this run; standing memories or cost never waive anything (the sole standing waiver is step 6's docs-only one). The only self-serve disposition is mechanical: `git status` shows zero repo changes at synthesis → steps 6–8 close `n/a — zero repo changes`. **Never Write/Edit a repo file from the main thread** — every repo change (code, docs, rules, configs, new files, one-line fixes) lands via `code-developer` or `bulk-editor`; deletions: run `git rm` yourself and record it in the ledger. In phased mode (`references/phased-execution.md`), after a phase passes its gate the orchestrator runs `git add`/`git commit` itself and records the SHA in the ledger — the run-start phase-plan approval is the standing authorization to do so. Change runs open the ledger with a step-disposition table (steps 1–8: `done | n/a — zero repo changes | user-waived: "<quote>"`; step 8 closes `considered: <outcome>` — the rule-worthiness bar judges content, never whether the step runs) and the synthesis ends with the step 6–8 dispositions.

## Dispatch prompt template

Every agent prompt follows this skeleton. Vague prompts return vague reports — be explicit about scope and shape.

```
You are a research agent assisting an orchestrator. Read-only — do NOT modify files.

CONTEXT: <1–3 sentences: the task + why it matters for the decision being made>

FIRST: read <.claude/skills/X/SKILL.md> to orient (skills are directories — read the SKILL.md file inside, not the dir, which throws EISDIR), then <specific code paths / docs>.
<External/current facts: route that thread to research-specialist instead; readers may cite the shared research cache (.claude/agent-memory/research-specialist/) and must report uncached needs as RESEARCH GAPs.>

DELIVERABLES — return ALL of:
1. <specific structured item>
2. <specific structured item>
...

Return distilled facts + plain relative `path:line` refs + targeted snippets.
Repeat the full relative path on every citation, even for the same file. Do
not use Markdown links, `file://` URLs, absolute paths, URL-encoded paths,
`#L123` anchors, or bare line-only citations like `:123` for repo evidence.
When citing several lines in one file, repeat the full path on each — WRONG
`some-file.ts:700, 737, 774`, RIGHT `src/module/some-file.ts:700, src/module/some-file.ts:737, src/module/some-file.ts:774`.
Do NOT dump whole files. Quote VERBATIM where fidelity matters (config, rule
bodies, schemas).
```

## Skill map — pick the relevant skills per thread

Every agent's first step is to read the project skills you point it at, so choosing the right ones is the orchestrator's job, not the agent's. Scan every available skill by **name + description** (already in your context, or run `ls .claude/skills/`) and pick what matches the thread. Populate the table below per project — one row per domain, listing the skill names to hand a thread and any domain-pinned expert to dispatch (see the Agent roster).

<!-- Populate per project. Replace these placeholder rows with real domain → skill pairings.
     `<prj>` is this project's short prefix (for example `shop`, `api`, or `app`); see references/domain-expert-template.md. -->

| When the task touches… | Hand the agent these skills |
|---|---|
| `<domain A>` (e.g. billing) | `<skill-1>`, `<skill-2>` — dispatch **`<prj>-<domain>-expert`** if one exists |
| `<domain B>` (e.g. auth) | `<skill-3>`, `<skill-4>` — dispatch **`<prj>-auth-expert`** if one exists |
| `<cross-cutting concern>` | `<skill-5>` |
| Web/external research, current facts | dispatch **research-specialist** — sole web tier, cache-first (`.claude/agent-memory/research-specialist/`); your web-research skill (e.g. `exa-web-research`) is preloaded by that agent only — the orchestrator no longer hands it out |

The map indexes *relevance* only — full descriptions live in each skill's frontmatter. Keep it curated as skills are added, renamed, or removed. If the project has multiple product lines/branches, note branch-variant skills here.

## Agent roster — dispatch by `subagent_type`

The house subagents bake model + effort + read/write boundary into `.claude/agents/`, so dispatching by `subagent_type` locks the tier regardless of the session level. This is the orchestrator's main lever — pick the agent, not a raw model.

| `subagent_type` | Tier | Boundary | Dispatch it for |
|-----------------|------|----------|-----------------|
| **`code-digester`** | sonnet / high | read-only | **Default for most threads** — digest a subsystem/file/skill, audits, second-angle reads. |
| **`research-specialist`** | sonnet / high | repo read-only + own memory (research cache) | **Sole external-research tier** — ALL external/current-facts threads (library APIs, versions, upgrades, CVEs, vendor docs); cache-first (checks `.claude/agent-memory/research-specialist/` before searching), web search only on a miss, digests captured back to that cache for reuse. |
| **`deep-analyst`** | opus / high | read-only | Hard reasoning only — cross-file traces, architecture mapping, gnarly multi-file debugging. |
| **`code-developer`** | sonnet / high | Read/Edit/Write + Bash + own memory (no web tools) | Authoring code — features, fixes, refactors, library integrations. Verifies APIs against the shared research cache (`.claude/agent-memory/research-specialist/`), self-checks typecheck/lint, returns a diff report for orchestrator verification. |
| **`bulk-editor`** | haiku / high | Read/Edit/Write | Fully-specified mechanical edits only — verbatim old→new strings, precise insertions. No judgment. |
| **`skill-auditor`** | sonnet / high | read-only | Post-change docs audit (loop step 7) — FRESH/STALE verdicts + exact old→new specs for project skills and `.claude/rules/`; root CLAUDE.md and domain memory flag-only. |
| **`localworkflow-sync`** | sonnet / medium | read-only | Meta agent — audits this skill + the agent roster + domain experts + memory for drift, and guides creating/wiring a new `<prj>-<domain>-expert`. |
| **`<prj>-<domain>-expert`** | sonnet / medium | repo read-only + own memory | *(optional, per project)* One per major subsystem — carries that domain's invariants, preloads its skill. Branch from `references/domain-expert-template.md`. |

Full trigger scopes live in each agent's frontmatter `description` (don't duplicate them here). A `<prj>-<domain>-expert` is a project-specific extension: `<prj>` is a short project prefix, `<domain>` matches a skill. Each preloads its domain skill(s), carries the domain invariants, keeps persistent notes in `.claude/agent-memory/<name>/`, and produces edit specs for `bulk-editor` or context briefs for `code-developer`. To add one, dispatch `localworkflow-sync` (it reads the domain skill and returns the exact new-agent file + roster/Skill-map edit specs) or follow `references/domain-expert-template.md` + `references/adding-a-subagent.md` by hand.

- **Routing:** default to `code-digester`; use a matching `<prj>-<domain>-expert` when a thread is squarely in its domain; use `skill-auditor` for loop-step-7 cross-domain, undomained, or no-matching-expert docs-staleness work, with `code-digester` only as fallback; `deep-analyst` only when a thread is genuinely hard (deep code comprehension); **`code-developer` whenever code must be AUTHORED** — any change that still requires a design, wording, or API decision; `bulk-editor` only when the edit is purely mechanical and fully specified. The writer test: does applying the change require any decision? Yes → `code-developer`; no → `bulk-editor`. When unsure among readers outside the docs-staleness path, use `code-digester`. **External/current-facts threads always go to `research-specialist`** — `code-digester` and `deep-analyst` may only read the shared research cache (`.claude/agent-memory/research-specialist/`) and must report uncached needs as RESEARCH GAPs, never search the web themselves.
- **Orchestrator PRE-WARM rule.** Before dispatching a writer (`code-developer`) whose brief touches an external library, verify the research cache covers it — dispatch `research-specialist` first if it doesn't, marking that pre-warm dispatch **implementation-bound** so any stale entry it finds is refreshed rather than served as-is — then pass the cache pointers/digest into the writer's brief (`references/dispatching-code-developer.md` §RESEARCH CACHE POINTERS). Writers cannot web-search; an uncached API forces a `NEEDS_CONTEXT` round-trip.
- **Two-stage changes: readers digest, writers write, you verify.** Have readers digest the context, then dispatch `code-developer` with the digested findings, the exact target files, and the relevant `.claude/skills/<skill>/SKILL.md` paths — you still own step 6 and never write repo files in the main thread. Fully-specified edits (verbatim old→new strings, precise insertion points) skip the writer and go straight to `bulk-editor`. **Reuse the warm reader** for the spec or brief via `SendMessage` (it still holds the files — zero re-reading), but **cap warm reuse at 2 — exceptionally 3 — resume rounds**: a 4th crosses a 200K window and dies mid-run ("Prompt is too long", observed 2026-07-05). **Writers run one at a time** unless their file sets are provably disjoint. Read `references/dispatching-code-developer.md` for the fill-in brief template, the warm-reuse rules, and crash recovery. **Multi-phase delivery runs** (complex code-authoring changes, per the step-1 entry criteria) follow `references/phased-execution.md` instead of this single-shot path.
- **No generic readers — even in plan mode.** `code-digester` is the universal reading fallback; reading threads never go to `Explore`/`general-purpose`. Plan mode changes nothing: the house read-only agents ARE the explorers (they satisfy its read-only constraint), and a harness phase default never overrides this skill once invoked. `general-purpose` is allowed only for a read+act thread no house tier covers — name the missing capability in the ledger (it follows the session model, no pinned effort).
- **Effort policy.** General readers/reviewers, hard-analysis readers, and all writers pin `high`; `localworkflow-sync` and every `<prj>-<domain>-expert` pin `medium`. In a Workflow script, effort is the `effort` option on `agent()`. In chat (Agent tool) there is **no per-call effort** — it follows the session, *unless* the named subagent pins its own via `effort:` in its `.claude/agents/<name>.md` frontmatter (all house agents do).

## Quality-control what agents do — you own it

Dispatching the work does not dispatch the responsibility. An agent's final message is a **self-report** — a claim about what it did, not proof. When an agent *does* something (edits a file, writes code, runs a command, applies a config change), the orchestrator owns its correctness: verify before you report it done.

- **Verify write/edit work yourself — don't relay the agent's diff.** The agent's summary is the claim, not the check. Confirm independently: re-read the changed region (the sanctioned use of a single targeted Read) or run `git diff` / the build / the linter.
- **Check it against the ask.** All of the requested change, only that, and nothing it shouldn't touch. Agents over-reach, miss a case, or quietly drop a constraint.
- **Check evidence formatting.** Read-only reports should use plain relative `path:line` refs. Treat Markdown file links, `file://` URLs, absolute paths, URL-encoded paths, `#L123` anchors, and bare line-only citations like `:123` as malformed evidence that needs correction or independent verification.
- **Prefer a runnable check over prose.** If a build, test, or command can confirm the work, run it (or dispatch one that does). "Done" in an agent report is not evidence.
- **On a gap, re-dispatch and re-verify** — then tell the user what you verified and how it stands, not what the agent claimed.
- **Independent review gate — the check after code changes.** Self-verification above is necessary but not independent. Once edits are applied and self-verified, run your project's independent review on the git delta (a static analyzer, a review subagent, or a separate model), always on a defect pass and — when the change embodied a design decision — on an adversarial pass with 1–2 lines of task-derived focus. Present findings by severity with your own true/false-positive judgment, then STOP and ask which findings to fix — never auto-apply review fixes. The same STOP carries any rule proposals a confirmed finding earned (loop step 8 — see `references/rule-capture.md`).

## Gotchas

- **Stay out of the files.** Don't Read/Grep code to *understand* a subsystem — that's the agent's job. A single targeted Read to confirm one known line before an edit is fine; reading to learn an area is not.
- **Parallel means one message.** Independent agents go in a single response block, not serialized. Serializing wastes wall-clock for nothing.
- **Demand structure.** Give every agent a numbered DELIVERABLES list and ask for `file:line` refs + snippets, not whole-file dumps. Ask for verbatim quotes when you'll reason on the exact text (config, schemas, rule bodies).
- **Budget each dispatch's context.** One well-defined subtask per dispatch; shard any brief naming more than ~15–20 substantial files or >~100KB of source. A reader's transcript amplifies its reading 2–3× (search output, re-reads, report drafting) — a scope that fits once does not fit twice. See `references/subagent-best-practices.md` § Context budgeting & overflow recovery.
- **A warm agent that dies mid-run ("Prompt is too long") is gone.** Its ID cannot be resumed — the resume replays the same over-long input — and its last progress message understates what actually landed. Inventory the working tree yourself (one grep marker per scoped item), route the fully-specified remainder to `bulk-editor`, and re-dispatch a fresh writer for the rest.
- **Keep a durable ledger on multi-phase change runs.** Your own context can be compacted mid-run, and the most expensive failure mode is re-dispatching work that already landed. Append one line per completed phase to a scratch ledger file (`Phase N: done — files touched, self-check clean`); after any compaction, trust the ledger + `git diff` over your recollection. Open it with the loop contract's step-disposition table. In `references/phased-execution.md` runs, each row also carries the review outcome and commit SHA: `Phase N: done — <files>, self-check clean, review clean, commit <sha>`.
- **Surface → judge → decide.** Route external/current facts (library APIs, CVEs, versions) to `research-specialist`, which cites source URLs and caches the digest for reuse — never training knowledge. If a second-wave finding reframes the task, pivot the synthesis around it. Separate confirmed from speculative and say plainly what to do next.
- **Review gates need a git delta.** A review gate diffs local git state — a dirty working tree or a `--base` branch delta. Research-only means `git status` shows zero repo changes at synthesis — a ledger-recorded fact, not a judgment. And findings never chain into an auto-fix: present, judge, ask.

## When NOT to use

Skip the fan-out for trivial single-fact lookups, a one-line edit, or anything answerable from context already in the conversation. Delegation has overhead — if you'd finish it faster yourself, do that.

## Adding a house subagent

To add a new tier or specialist to `.claude/agents/`, read `references/adding-a-subagent.md` for the full procedure (frontmatter fields, the "When invoked" body shape, registry re-scan, smoke-test, and what to keep in sync). Read `references/domain-expert-template.md` when creating a per-subsystem domain expert. Read `references/subagent-best-practices.md` for the sourced rationale (official docs + Anthropic engineering posts) whenever you design or review an agent definition.

## Keep in sync

- **`.claude/agents/*.md`** — the agent definitions (the seven house agents — `code-digester`, `research-specialist`, `deep-analyst`, `code-developer`, `bulk-editor`, `skill-auditor`, `localworkflow-sync` — plus any `<prj>-<domain>-expert`). On any model/effort/boundary/roster change, update the **Agent roster** table here and `references/adding-a-subagent.md`. Keep each `<prj>-<domain>-expert` aligned with its domain skill's invariants; smoke-test after a change; dispatch `localworkflow-sync` for a drift check and to be guided through creating a new one.
- **`references/dispatching-code-developer.md`** — the orchestrator's fill-in brief template for `code-developer`. It restates that agent's `## Output` contract and non-default-workflow rule; re-check both sections when `.claude/agents/code-developer.md`'s `## When invoked` or `## Output` changes.
- **`references/phased-execution.md`** — the canonical multi-phase delivery protocol (entry criteria, run-start STOP, per-phase cycle, branch/worktree policy, ledger row shape, testing bar). Re-check when the per-phase cycle, commit convention, or branch/worktree policy changes; keep in lockstep with the phase-brief fields in `references/dispatching-code-developer.md`.
- **`references/skill-staleness-audit.md`** — dispatch guide for loop step 7. Re-check when the Skill map's shape, the domain-expert pattern, the step's wording, or the `skill-auditor` Output contract changes.
- **`references/rule-capture.md`** — the guide for capturing review findings and mid-run quirks as path-scoped `.claude/rules/` files (loop step 8). Re-check it when the loop's step numbering, the review gate's result handling, or the staleness audit's scope changes.
- **Skill map** — keep curated as skills are added, renamed, or removed. It indexes *relevance* only; never copy skill descriptions into it (they live in each skill's frontmatter and would drift).
- Otherwise this is a meta-skill not tied to repo code: update it only if the available agent types, model names, or dispatch conventions change.
