---
paths:
  - ".claude/agents/*.md"
---

# Agent roster: tiers, boundaries and same-pass updates

This file is the only place the house agents' model and effort tiers are written down. Other docs point here instead of restating them. Record tier changes with a date in a history note of your choice; that note is history, not authority.

## Current tiers

Every agent sets a `model:` and an explicit `effort:`. No `memory:` field.

| Agents | `model:` | `effort:` |
|---|---|---|
| `code-digester`, your `<prj>-<domain>-expert` agents, `localworkflow-sync` | `opus` | `low` |
| `research-specialist`, `skill-auditor`, `code-developer` | `opus` | `medium` |
| `code-reviewer`, `adversarial-reviewer` | `opus` | `high` |
| `deep-analyst` | `fable` | `high` |
| `bulk-editor` | `opus` | `low` |

To change a tier, edit this table and add a dated entry to your history note. Domain experts are installed per project from `.claude/skills/local-workflow/references/domain-expert-template.md`.

- **Aliases versus full IDs.** The kit ships aliases (`opus`, `fable`) for portability. Under the family-alias rule (code.claude.com/docs/en/sub-agents, "choose a model"), a subagent whose alias matches the main conversation's model family runs on the main conversation's exact model, so `model: opus` follows the session instead of holding the tier, and aliases also move on their own over time. To hold a tier regardless of the session, pin the full model ID from the models overview page (for example the current Opus or Fable ID) and record the date you pinned it.
- **Why pin effort.** An agent with no `effort:` inherits the session level, and some models default to `medium`.
- **Why Fable only for `deep-analyst`.** Fable is slower and costs more per token than Opus. It may bill to usage credits, silently under `-p` or the Agent SDK. A review gate's per-call `model: "fable"` second opinion is a dispatch-time override that changes no pinned tier (`.claude/skills/local-workflow/references/review-gate.md`).
- **Don't flatten writer effort.** `code-developer` runs at `medium` because its output is self-checked and then re-verified by the orchestrator before it lands. If you add specialist writers that each own a higher-blast-radius surface on their own, give them `high`. Don't "correct" this to a uniform writer effort.
- **Research basis:** `docs/agent-knowledge/research/claude-code-subagents.md`.
- **Confirm what ran** in `/tasks`, which shows each agent's effective model and effort. Frontmatter is only the configured profile.

## Boundaries

- **Readers.** These are `code-digester`, `deep-analyst`, the two reviewers, `skill-auditor`, your `<prj>-<domain>-expert` agents and `localworkflow-sync`.
  - They pin `tools: Read, Grep, Glob, Bash, Skill, ToolSearch`. That gives no Write/Edit, no web tools, no `Agent`, and no MCP server added later.
  - They preload `house-agent-contract`, which holds the shared read-only, evidence, timebox, knowledge-proposal and citation rules.
  - The effective set can be narrower than the pin: observed in one installation, readers listed only `Read, Bash, Skill`, because that build exposed no Grep/Glob tools and gave subagents no `ToolSearch` (`docs/agent-knowledge/research/claude-code-subagents.md`). That is not drift; keep the pin.
  - Residual gap: `Bash` can still reach `curl` and any doc-fetch CLI. That limit is enforced by instructions only.
- **`research-specialist`** is the only web tier. Its `disallowedTools` is `Write, Edit, NotebookEdit, Agent`, and it keeps its web tools. It is cache-first at `docs/agent-knowledge/research/` and propose-only. Your web-research skill/MCP, if any, may be user-global (`~/.claude/skills/`), so fresh clones and Codex don't see it.
- **Writers** (`code-developer`, `bulk-editor`, and your specialist writers, if any) pin a `tools:` allowlist with no web tools. On a research gap the authoring writers stop with `NEEDS_CONTEXT`; `bulk-editor` makes no API decisions and STOPs on any spec mismatch.
- **No per-agent memory.** Durable knowledge lives in `docs/agent-knowledge/`. Readers and specialists propose updates. Only a writer with explicit ownership, or the main thread, applies them.

## Same-pass update list

Any change to an agent's tier, boundary, `## When invoked` or `## Output` updates, in the same pass:

- this file (the table or the Boundaries section);
- `.claude/skills/local-workflow/references/review-gate.md`, which mirrors the two review-gate agents (`.claude/agents/code-reviewer.md`, `.claude/agents/adversarial-reviewer.md`);
- `.claude/skills/house-agent-contract/SKILL.md`, when a reader rule shared by all readers changes;
- the Codex mirror `.codex/agents/<name>.toml`, for shared facts only (see below).

**The list is a floor, not a checklist.** Observed in practice: every named surface was updated and stale tier prose still survived elsewhere. After a tier change, grep the retired model name case-insensitively across `.claude/skills/` and `.claude/rules/`. Every surviving hit must be one of three things: a `model:`-field accepted-values list, an explicitly dated historical paragraph, or a literal historical filename. Anything else is drift; fix it in the same pass.

## Codex runtime

If you run Codex in parallel, `.codex/agents/*.toml`, `.agents/skills/`, `docs/agent-rules/` and the shared `docs/agent-knowledge/` are all in use.

- **Drift in shared facts is a finding.** That covers role descriptions, read/write boundaries, invariants and paths.
- **Tier differences are not.** Model and effort diverge on purpose, because Codex keeps its own ladder, so never flag them.

## Reload caveat (the one home for it)

The docs say edits to existing agent files hot-reload. Some cases still need a restart: the first file in a new `agents` directory, `--add-dir` directories, and `--disable-slash-commands` sessions. Even so, pickup has been observed to fail in practice: edited bodies stayed stale, and the registry re-snapshotted only at session start and at compaction.

After every agent change, and until verified otherwise every hook change:
1. restart;
2. smoke-test;
3. restart again if the smoke test shows a stale definition.
