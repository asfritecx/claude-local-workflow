# local-workflow — a portable orchestration kit for Claude Code and Codex

A drop-in **orchestration workflow** for [Claude Code](https://claude.com/claude-code) and [Codex](https://developers.openai.com/codex): instead of letting the main agent bulk-read your codebase and blow its context, it acts as an **orchestrator** that fans out read-only subagents to read and research in parallel, then synthesizes the answer itself. This repo carries separate native skills and custom-agent definitions for both platforms, plus one-time installers.

> **The core idea:** the orchestrator holds the conclusion; the agents do the reading.

---

## Why

The orchestration pattern is genuinely reusable, but a real installation gets tangled up with one project's specifics — its subsystems, its domain experts, its review tooling. This kit is the pattern with all of that stripped out, so you can carry it between projects and re-fill only the project-specific parts (which skills map to which threads, and which domain experts to create).

**What it gives you:**
- A repeatable way to research, audit, debug-across-files, or plan in a large codebase without the main thread reading everything itself.
- A fixed set of model/effort **tiers** so work runs at the right cost/quality regardless of your session settings.
- A built-in discipline: **verify what agents did — never trust the self-report.**
- A fast path to onboard a brand-new codebase (fan out experts to digest it).

---

## What's in the box

```
claude-local-workflow/
├── README.md                              ← you are here (repo overview)
├── DEPLOY.md                              ← run-once installer; two paths (greenfield / existing)
├── DEPLOY-CODEX.md                        ← Codex-native installer and boundary checks
├── LICENSE                                ← MIT license (stays in the kit repo)
├── docs/
│   ├── anthropic-subagent-best-practices.md ← sourced Anthropic docs + engineering-post reference material
│   ├── anthropic-memory-rules.md          ← sourced memory/rules docs (grounds skill-auditor's audit scope)
│   └── codex-port-review.md               ← comprehensive Claude ↔ Codex capability mapping
├── skills/local-workflow/
│   ├── SKILL.md                           ← the orchestration skill (the workflow itself)
│   └── references/
│       ├── adding-a-subagent.md           ← how to author a new agent (frontmatter, body shape, smoke-test)
│       ├── subagent-best-practices.md     ← sourced rationale (Anthropic docs + engineering posts)
│       ├── domain-expert-template.md      ← copy-ready skeleton for a project domain expert
│       ├── dispatching-code-developer.md  ← fill-in brief template for dispatching code-developer
│       ├── phased-execution.md            ← multi-phase delivery protocol for complex code-authoring runs
│       ├── skill-staleness-audit.md       ← post-change audit brief (keeps skills in sync with code)
│       └── rule-capture.md                ← capture of review findings / quirks as path-scoped rules
├── agents/
│   ├── code-digester.md                   ← Tier: read-only researcher/digester (the default worker)
│   ├── research-specialist.md             ← Tier: sole external-research worker (cache-first, web-locked elsewhere)
│   ├── deep-analyst.md                    ← Tier: read-only hard reasoning (traces, architecture)
│   ├── code-developer.md                  ← Tier: judgment writer (authors code, verifies against the research cache, self-checks)
│   ├── bulk-editor.md                     ← Tier: mechanical edits only (verbatim old→new)
│   ├── skill-auditor.md                   ← Tier: read-only post-change docs audit (skills + rules)
│   └── localworkflow-sync.md              ← Meta agent: audits the kit + guides adding domain experts
└── codex/
    ├── skills/local-workflow/             ← Codex skill + UI metadata + references
    └── agents/*.toml                      ← seven project-scoped Codex custom agents
```

*(`claude-local-workflow/` is the folder `git clone` creates from this repo — you copy it into a target project's root, install from it, then delete it (see `DEPLOY.md`). If you cloned or copied it under a different folder name, substitute that name throughout.)*

---

## The agent roster

| Agent | Model / effort | Boundary | Role |
|---|---|---|---|
| `code-digester` | sonnet / high | read-only | **Default worker.** Digest a subsystem/file/skill, second-angle audits. |
| `research-specialist` | opus / high | repo read-only + own memory (research cache) | **Sole external-research tier.** ALL external/current-facts threads (library APIs, versions, upgrades, CVEs, vendor docs); cache-first, web search only on a miss, digests captured back to the cache for reuse. |
| `deep-analyst` | opus / high | read-only | Hard reasoning only — cross-file traces, architecture mapping, gnarly multi-file debugging. |
| `code-developer` | sonnet / high | Read/Edit/Write + Bash + own memory (no web tools) | Authoring code — features, fixes, refactors, library integrations. Verifies APIs against the shared research cache, self-checks typecheck/lint, returns a diff report for you to verify. |
| `bulk-editor` | haiku / high | Read/Edit/Write | Fully-specified mechanical edits — verbatim `old→new` strings. Makes no decisions; STOPs on ambiguity. |
| `skill-auditor` | sonnet / high | read-only | Post-change docs audit — FRESH/STALE verdicts + exact old→new specs for project skills and `.claude/rules/`; root CLAUDE.md and domain memory flag-only. |
| `localworkflow-sync` | sonnet / medium | read-only | Keeps the skill + roster + experts + memory aligned; **guides you to create new domain experts**. |
| `<prj>-<domain>-expert` | sonnet / medium | read-only + own memory | *Optional, per project.* One per major subsystem, carrying that domain's invariants. Branch from the template. |

The **two-stage change** pattern is central: readers digest the context, then the change routes by the writer test — does applying it still require a design, wording, or API decision? Yes → `code-developer` authors it (verifying APIs against the shared research cache, self-checking, returning a diff report); no → `bulk-editor` applies the verbatim old→new spec mechanically. Judgment stays upstream; you verify every diff.

---

## Requirements

- **Claude Code** with subagent + skill support. Treat ANY agent-definition change (new file or edit) as needing a session restart before validation — mid-session hot-reload is unreliable in practice (see `references/subagent-best-practices.md` §Smoke-testing).
- The agents use **model aliases** (`sonnet` / `opus` / `haiku`) rather than pinned model IDs, so they resolve to whatever your environment provides.
- **Codex** with project skills and custom-agent support. The Codex roster pins `gpt-5.6-luna`, `gpt-5.6-sol`, and `gpt-5.6-terra`; verify those environment-specific slugs before installation.
- No application dependencies. The kit is Markdown, YAML metadata, and TOML custom-agent definitions.

---

## Install Claude Code

Clone this repo (or copy the folder) into the root of the project you want to equip, then follow **[`DEPLOY.md`](DEPLOY.md)**. It branches on project type:

- **Greenfield** (new/empty repo) → installs the baseline only: the skill + the seven house agents. Add domain experts later, as subsystems appear.
- **Existing project** (a codebase to digest) → asks which domains you want experts for, installs the baseline + those experts, then has you restart the session so they register, and finally fans them out to **digest the codebase**.

At a glance:

```bash
# from your target project's root, with this folder copied in as claude-local-workflow/
mkdir -p .claude/skills .claude/agents
cp -R claude-local-workflow/skills/local-workflow .claude/skills/
cp    claude-local-workflow/agents/*.md          .claude/agents/
# ...then populate the Skill map in .claude/skills/local-workflow/SKILL.md,
#    optionally branch domain experts, restart, and delete claude-local-workflow/
```

`DEPLOY.md` and the staging folder are meant to be **deleted after installing** — they don't belong in the target project's `.claude/` tree. (This `README.md` stays in the published kit repo.)

## Install Codex

Follow **[`DEPLOY-CODEX.md`](DEPLOY-CODEX.md)**. It installs the Codex skill under `.agents/skills/local-workflow/` and the seven house custom agents under `.codex/agents/`, then requires model, TOML, sandbox, web, and effective MCP-boundary validation in a fresh session.

The Codex port preserves the eight-step loop and reader/writer split. Where Codex lacks a literal Claude feature, it uses the strongest documented native replacement: explicit skill reads instead of `skills:` preload, mediated tracked memory writes, nested `AGENTS.md` instead of `.claude/rules/` globs, and orchestrator-created worktrees instead of per-agent isolation. See **[`docs/codex-port-review.md`](docs/codex-port-review.md)** for the full source-cited comparison and residual gaps.

---

## Customizing per project

### Claude Code

Two things are project-specific and left as placeholders:

1. **The Skill map** (in `SKILL.md`) — a table pairing each domain with the project skills to hand a thread, and the domain expert to dispatch. Fill it with your project's skills.
2. **Domain experts** — one read-only specialist per major subsystem, named `<prj>-<domain>-expert` (`<prj>` is a short project prefix such as `shop`, `api`, or `app`). The fastest way to add one:
   - **Guided:** dispatch `localworkflow-sync` — it reads the domain's skill/code and the template, then returns the exact new-agent file **plus** the roster/Skill-map edits that wire it in.
   - **By hand:** copy `references/domain-expert-template.md`, fill the placeholders, and add its rows to the roster + Skill map.

Both are documented in `references/adding-a-subagent.md`.

### Codex

Edit `codex/skills/local-workflow/references/project-routing.md` to map project areas to applicable `AGENTS.md`, skills, specifications, and domain experts. Register any expert in `agent-roster.md`, create its `.toml` from `domain-expert-template.md`, and materialize the target environment's effective MCP boundaries during deployment. The detailed procedure lives in the Codex-native `references/adding-a-subagent.md` and `DEPLOY-CODEX.md`.

---

## How the workflow runs

1. **Decompose** the task into independent threads (one per subsystem / perspective / source).
2. **Dispatch in parallel** — fire every independent agent in one message, by tier.
3. **Review + gap-check** the reports; look for contradictions or a finding that reframes the task.
4. **Follow-up dispatch** to close gaps (often a verbatim extraction so you reason on ground truth).
5. **Synthesize** — make the decision yourself; separate confirmed facts from speculation; end with the next step.
6. **Gate code changes** — self-verify (diff/typecheck/lint), then run your project's independent review on the delta. Present findings, judge them, ask — never auto-fix.
7. **Audit docs staleness** — after any repo-change run, establish coverage mechanically and dispatch one read-only verdict pass. Claude audits `.claude/skills/**`, `.claude/rules/**`, and relevant `.claude/agent-memory/**`; Codex audits `.agents/skills/**`, nested `AGENTS.md`, `.codex/agents/**`, and `.codex/agent-memory/**`. Both return FRESH/STALE verdicts and exact old-to-new specifications.
8. **Capture durable lessons** — Claude uses a small path-scoped `.claude/rules/` file. Codex uses the closest safely scoped `AGENTS.md`, proposing root-wide guidance rather than silently editing it; agent-memory changes remain mediated.

Full detail — including the binding loop contract (steps are never self-skipped) — lives in `skills/local-workflow/SKILL.md` for Claude and `codex/skills/local-workflow/SKILL.md` for Codex.

---

## Notes on portability

This kit was extracted from a working installation and deliberately genericized: all project-domain references, project file paths, and any one review-tool's commands were removed and replaced with placeholders or tool-agnostic principles. If you adopt it and want an independent review gate, wire in whatever review tooling your project uses at step 6.

`research-specialist` is the sole web-research tier. Claude keeps its git-tracked cache under `.claude/agent-memory/research-specialist/` and may preload an Exa-style research skill. Codex uses `.codex/agent-memory/research-specialist/`, live web plus approved research MCP sources, and returns exact `CACHE_WRITE` content for mediated persistence through `bulk-editor`. Every other agent, including `code-developer`, is web-locked and reports an uncached need as a research gap.

---

## Credits & license

Built for [Claude Code](https://claude.com/claude-code) and [Codex](https://developers.openai.com/codex). Released under the [MIT License](LICENSE).
