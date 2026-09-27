# Playbook: autonomous run

**Role:** you own the finish condition. The user asked for unattended iteration, such as "keep going until the tests pass", "fix all lint errors" or "loop until X", so the run has to know when to stop on its own.

## Steps (copy into todos; mark any you skip `skip: <reason>`)

1. **Write the exit predicate as a command** whose exit status or output decides done. For example, `<your lint>` exits 0, or `<your unit tests>` shows 0 failures.
   - A duration or an iteration count is not a finish condition. At most it is a budget.
2. **Isolate the work.** Use a worktree (`EnterWorktree` preferred), so a bad iteration can't damage the user's tree.
3. **Open a run folder** with `standing-orders.md` and `decisions.tsv` (`references/playbooks/multi-phase.md` § decisions.tsv).
4. **Iterate.** Each iteration makes one change, runs one check, and writes one trail row.
   - Pace the loop with `/loop` (self-paced `ScheduleWakeup`).
   - Use Monitor for long-running output.
   - Don't poll agents.
5. **Never relax the predicate.** Don't weaken a test, add a lint-disable or skip a check to get to green, unless the user explicitly allows it.
   - A plateau is not a stop. Change the approach (`references/principles.md`: attack-the-premise) and keep going.
6. **Stop only at the predicate or at a genuine dead end.** A dead end means the next move needs a decision, authority or information you don't have. Write up why.

## Done when

The exit predicate passes and its output is recorded, or a dead-end write-up explains precisely what is blocking.

## Reply shape

- **Predicate result**, with its output.
- **Iterations:** the count and a summary of the trail.
- **What changed.**
- **What was tried and abandoned.**
- **Anything that needs the user.**
