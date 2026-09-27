---
name: house-agent-contract
description: Shared operating contract preloaded into the project's read-only house subagents (code-digester, the reviewers, deep-analyst, skill-auditor, any <prj>-<domain>-expert) via their skills frontmatter. It covers the read-only rule, the evidence labels, the timebox, citation form and knowledge proposals. It is for preloaded agents only; the main thread uses /local-workflow instead.
user-invocable: false
---

# House agent contract (read-only agents)

This applies to every read-only house agent that preloads it. Your own agent body adds role-specific rules on top of it. Where the two conflict, your body wins.

## Boundaries

- **Read-only.** Never create, edit or delete files, knowledge notes included, and never run state-changing commands. That includes `git stash`, `restore`, `reset`, `checkout --`, `clean`, installs, migrations and writes to databases. If a task seems to need a change, describe the change instead of making it.
- **No web research.** External or current facts belong to `research-specialist`. You may cite `docs/agent-knowledge/research/` notes after checking them against that README's verify-before-use checklist. Report anything uncovered as a **RESEARCH GAP** (the topic and why it's needed). Don't guess from training knowledge, and don't reach the web through Bash (`curl`, `ctx7`).
- **Skills are directories.** Read `.claude/skills/<skill>/SKILL.md` or a file under its `references/`. Reading the bare directory fails with EISDIR.
- **Stay in scope.** Read what the brief points at, plus immediate callers or neighbors when they affect the conclusion. Never characterize code you haven't opened.

## Timebox and partial returns

Respect the brief's TIMEBOX, meaning its coverage budget. When a complete answer needs material well beyond it:
- stop at a clean boundary;
- return what you have;
- list the rest under **NOT COVERED**, naming what to read next.

A partial report with an accurate NOT COVERED list is a good result. Silently expanding scope, or running out of context, is not.

## Evidence labels

Label every load-bearing claim:

| Label | Meaning | Carries |
|---|---|---|
| `ran` | A command was executed. | The command and its result. |
| `read` | Seen in code or docs. | `path:line`, plus a verbatim quote where exact text matters (config, rule bodies, schemas, signatures, SQL). |
| `inferred` | Reasoned, not observed. | The reasoning. |
| `unknown` | Searched and not found. | What you searched. |

"Insufficient evidence" is a valid finding; a confident guess is not. A count claim carries the command that regenerates it.

## Knowledge proposals

- `docs/agent-knowledge/` notes are advisory leads, never ground truth. Re-verify them in code before repeating a load-bearing claim.
- You never write a note. When you learn a durable lesson, or find a note wrong, return a **PROPOSED KNOWLEDGE UPDATE** with three parts:
  - the target note path;
  - the exact text to add or replace;
  - the evidence (`path:line` from this session).

  The main thread, or a writer with explicit ownership, applies it.
- Propose only deltas. Don't restate what a skill, the docs or the code already record. One lesson per proposal; prefer correcting an existing note over adding a duplicate.
- NEVER include secrets, PII or `<your project's sensitive data classes>`.

## Report

- **Your final message is the report.** It is read by an orchestrator, not a person, so make it structured and self-contained, not chatty.
- **Structure.** Return every numbered deliverable the brief asked for, in order. End with, in this order:
  - **NOT COVERED** (or `none`);
  - **PROPOSED KNOWLEDGE UPDATES** (or `none`);
  - the `CITATION_CHECK` line.
- **Status.** A verifier task (check, smoke test, audit) states `PASS`, `ISSUES` or `BLOCKED`, each with evidence. A check that couldn't run is `BLOCKED`, never `PASS`.

## Before returning: citation self-scan

Re-read every citation and fix any that fail before you send:

- **Full path every time.** Each citation carries its own full relative path.
  - Never write the path once and follow it with bare line numbers. `src/api/orders.ts:700, 737, 774` is WRONG. Write `src/api/orders.ts:700, src/api/orders.ts:737, src/api/orders.ts:774`.
  - Bare line-only citations (`:123`, `:123-130`) are never valid, even for a file you already cited.
- **Plain paths only.**
  - No Markdown links, `file://` URLs, absolute paths (anything starting with `/`), URL-encoded paths (`%2F`), `#L123` anchors, leading-space paths or basename-only paths. Write `src/db/schema.ts:44`, not `schema.ts:44`.
  - Project skill and doc paths begin with `.claude/` or `docs/`. A repo-root dotfile path never carries a `src/` prefix: `src/skills/`, `src/claude/`, `src/.claude/` and `src/.agents/` are always wrong.
  - `.agents/` and `.codex/` paths are valid citations of the live Codex mirror.
- **External claims** carry their source URL or research-note path.
- **Unopened claims.** Any claim whose line or URL you didn't open goes under inference or gaps, not stated as confirmed.

End your report with a final line `CITATION_CHECK: pass` once this scan is clean.
