#!/usr/bin/env bash
# .claude/hooks/git-guard.sh
# PreToolUse hook (Bash): blocks git commands that discard uncommitted work
# in a tree other sessions and agents may be editing -- git stash (except
# list/show), git restore, git reset, git clean -f, git checkout -- <path> / . /
# -f / -p / <tree-ish> <path>, git switch --discard-changes / -f,
# pull/rebase/merge that would autostash (--autostash, or a true
# rebase/merge.autoStash from -c or config; --continue/--abort and other
# in-progress actions are allowed), and git worktree remove --force.
# It also follows $(...), shells and python/node/perl/ruby fed a script, and
# the literal arguments of those interpreters' exec calls.
# Rule: .claude/rules/worktree-agent-dispatch.md (Codex twin: docs/agent-rules/).
# The user can still run any of these directly with `! git ...`.
# The parser lives in git-guard.py and reads the hook JSON from stdin. It runs
# with -I (PYTHON* environment ignored) so warnings-as-errors cannot fail it open.
# Exit 2 = block (stderr goes to Claude). Any other failure fails open: the
# rule then stays instruction-level, as it was before this hook.

command -v python3 >/dev/null 2>&1 || exit 0

# git-guard.py signals a block with exit 10; every other status (including
# CPython's own 2 for an unreadable script) allows the command.
python3 -I -W ignore "$(dirname "$0")/git-guard.py"
rc=$?
[ "$rc" -eq 10 ] && exit 2
exit 0
