# Playbook: investigation

**Role:** you own the explanation. The user wants to understand how something works, where it lives or why it behaves as it does. Nothing gets edited.

## Steps (copy into todos; mark any you skip `skip: <reason>`)

1. Restate the question as one or more concrete sub-questions, each answerable with evidence.
2. Size the fan-out:
   - A simple question gets one reader, or you read it yourself.
   - A complex one gets 2–4 parallel explorers in one message: `code-digester`, the matching `<prj>-<domain>-expert` (if one exists), or `deep-analyst` for a genuinely hard trace.
3. Brief each explorer with `references/brief-contract.md`. They all share one return schema:
   - **Components**
   - **Flow**
   - **Files read**
   - **Boundaries**
   - **Non-obvious**
   - **Open questions**
   - **NOT COVERED**
4. External or current facts go to `research-specialist`. It checks `docs/agent-knowledge/research/` first.
5. Reconcile the reports:
   - Where two explorers disagree, check the code yourself.
   - An `unknown` stays `unknown`. Say what was searched.
6. Before writing the reply, check any load-bearing claim yourself.

## Done when

Every sub-question has an answer with evidence labels, or an explicit `unknown` with what was searched.

## Reply shape

- **Overview**
- **Key concepts**
- **How it works:** the flow, with `path:line` evidence.
- **Where things live**
- **Gotchas**
- **Open questions**

Put evidence labels on the claims. Offer a knowledge-note update if the answer is reusable (propose it; don't write it).
