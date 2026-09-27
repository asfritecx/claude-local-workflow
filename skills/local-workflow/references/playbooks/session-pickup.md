# Playbook: session pickup and pause

**Role:** you own continuity. Resuming means picking up from what is verifiably true, not from what someone remembers. Pausing means leaving a state the next session can trust.

## Pickup steps (copy into todos; mark any you skip `skip: <reason>`)

1. **Find the run.** Look for the run folder under `docs/runs/`, the user's pointer, or any SessionStart branch context your project injects.
2. **Read the trail, which is authoritative:**
   - the run README's state table and recall capsule;
   - `standing-orders.md`;
   - the tail of `decisions.tsv`.
3. **Read the tree:** `git status --porcelain`, `git diff --stat`, and `git log --oneline -10`. Match what's there against the trail.
4. **Verify inherited claims on the real artifact** before building on them: re-run the one check that matters, or read the file. Don't redo work that is already verified.
5. **State the next move** in one line and continue with the playbook the run was using.

## Pause steps

1. Stop at a safe boundary: no half-applied edit and no writer mid-run. Account for every dispatched agent.
2. Add a `decisions.tsv` row for the pause.
3. Write a **recall capsule** into the run README, or into the scratchpad for an ad-hoc session and then hand it to the user, since the scratchpad won't survive:
   - at most five bullets;
   - each thread tagged `[verified, uncommitted]`, `[in flight <branch>]`, `[planned]` or `[merged #N]`;
   - **Problems:** open issues, with evidence labels;
   - **Next move:** one line.
4. Update the README state table.

## Done when

- Pickup: the trail and the tree agree, and the next move is stated.
- Pause: the capsule, the trail row and the state table are all current.

## Reply shape

- **Where things stand:** the capsule.
- **Discrepancies** between the trail and the tree, if any.
- **Next move.**
