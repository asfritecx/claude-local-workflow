#!/usr/bin/env bash
# Pipe-test git-guard.sh. Usage: bash run-guard-tests.sh [cases.txt]
# cases.txt (default: the one next to this script): "<expected exit>\t<command>";
# \n is a newline, "" is removed (so a literal commit keyword never appears in
# this runner's own command line).
# Self-contained: the hook is found next to this script (kit hooks/ or an
# installed .claude/hooks/), and every case runs inside a throwaway fixture repo
# under mktemp -d, with the caller's git environment and global config ignored.
# The caller's repository is never read or modified.
here=$(cd "$(dirname "$0")" && pwd)
hook=$here/git-guard.sh
[ -f "$hook" ] || { echo "git-guard.sh not found next to this script ($here)" >&2; exit 2; }
casefile=${1:-$here/cases.txt}
[ -f "$casefile" ] || { echo "usage: bash run-guard-tests.sh [cases.txt] (file not found: $casefile)" >&2; exit 2; }
cases=$(cd "$(dirname "$casefile")" && pwd)/$(basename "$casefile")
for tool in git jq python3; do
  command -v "$tool" >/dev/null || { echo "run-guard-tests.sh needs $tool on PATH" >&2; exit 2; }
done
# Hermetic git: ignore an inherited repo (GIT_DIR and friends, as git exports
# them to hooks) and the caller's global/system config (autoStash, pull.rebase,
# core.hooksPath would otherwise change results). The hook inherits this env.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_CONFIG GIT_CONFIG_PARAMETERS GIT_CONFIG_COUNT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
# Fixture repo: branch main, one commit, and the tracked files the cases rely on.
# `git checkout <path>` blocks only for an existing (or deleted) tracked file, so:
#   package.json      -> `git checkout package.json`
#   docs/README.md    -> `git checkout docs` (a tracked directory)
#   src/lib/utils.ts  -> `cd src && git checkout lib/utils.ts`, the `cd src/lib && ...`
#                        cases and the cwd-from-json check below
#   src/db/schema.ts  -> `git checkout HEAD src/db/schema.ts` names a real tracked path
# No root-level utils.ts or a.ts: `echo $(git checkout utils.ts)` must stay allowed.
# Every temp path lives under one trapped root.
fixroot=$(mktemp -d) && [ -d "$fixroot" ] || { echo "mktemp -d failed" >&2; exit 2; }
trap 'rm -rf "$fixroot"' EXIT
fix=$fixroot/repo
git init -q -b main "$fix" || { echo "git init -b failed (git 2.28 or newer is required)" >&2; exit 2; }
mkdir -p "$fix/src/lib" "$fix/src/db" "$fix/docs"
echo '{}' > "$fix/package.json"
echo '# docs' > "$fix/docs/README.md"
echo 'export {};' > "$fix/src/lib/utils.ts"
echo 'export {};' > "$fix/src/db/schema.ts"
git -C "$fix" add -A
git -C "$fix" -c user.name=t -c user.email=t@t -c commit.gpgsign=false "com""mit" -qm init || exit 1
cd "$fix" || exit 1
err=$fixroot/err; : > "$err"
pass=0; fail=0
while IFS=$'\t' read -r want c; do
  c=$(printf '%b' "${c//\"\"/}")
  rc=0; jq -n --arg c "$c" '{tool_input:{command:$c}}' | bash "$hook" >/dev/null 2>"$err" || rc=$?
  if [ "$rc" = "$want" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL want=$want got=$rc: $(printf '%s' "$c" | tr '\n' '|')"; head -1 "$err"; fi
done < "$cases"
for payload in '{}' 'notjson' '"str"' '[1]' '{"tool_input":"x"}' '{"tool_input":{"command":123}}'; do
  rc=0; printf '%s' "$payload" | bash "$hook" 2>/dev/null || rc=$?
  if [ "$rc" = 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL malformed $payload rc=$rc"; fi
done
# cwd from the hook JSON: `git checkout utils.ts` is a path only inside src/lib.
rc=0; jq -n --arg d "$PWD/src/lib" '{cwd:$d,tool_input:{command:"git checkout utils.ts"}}' | bash "$hook" 2>/dev/null || rc=$?
if [ "$rc" = 2 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL cwd-from-json rc=$rc"; fi
# 1.2 MB command: must not hit the environment size limit, and must finish fast.
start=$(date +%s)
rc=0; python3 -c 'import json; print(json.dumps({"tool_input": {"command": "echo " + "a"*1200000 + "; git stash"}}))' | bash "$hook" 2>/dev/null || rc=$?
secs=$(( $(date +%s) - start ))
if [ "$rc" = 2 ] && [ "$secs" -lt 8 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL big command rc=$rc secs=$secs"; fi
# 400 nested unquoted heredocs inside $(: a RecursionError must block, not fail open.
rc=0; python3 -c 'import json; print(json.dumps({"tool_input": {"command": "git stash; x=$(" + "$(cat <<E\n"*400 + ")"}}))' | bash "$hook" 2>/dev/null || rc=$?
if [ "$rc" = 2 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL deep nesting rc=$rc"; fi
# Wrapper without its parser (CPython exits 2 on an unreadable script): must fail open.
lone=$fixroot/lone; mkdir "$lone"; cp "$hook" "$lone/"
rc=0; printf '%s' '{"tool_input":{"command":"git stash"}}' | bash "$lone/git-guard.sh" 2>/dev/null || rc=$?
if [ "$rc" = 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL missing parser rc=$rc"; fi
rm -rf "$lone"
# The hook's own git calls must not run a crafted repo's promisor lazy fetch:
# the command is blocked AND no payload runs.
evil=$fixroot/evilroot; mkdir "$evil"; r=$evil/evil
git init -q "$r"; touch "$r/x"
git -C "$r" config core.repositoryformatversion 1
git -C "$r" config extensions.partialClone origin
git -C "$r" config remote.origin.promisor true
git -C "$r" config protocol.ext.allow always
git -C "$r" config remote.origin.url "ext::sh -c touch% $evil/PWNED"
echo 1111111111111111111111111111111111111111 > "$r/.git/refs/heads/x"
rc=0; jq -n --arg c "cd '$r' && git checkout x" --arg d "$evil" '{cwd:$d,tool_input:{command:$c}}' | bash "$hook" 2>/dev/null || rc=$?
if [ "$rc" = 2 ] && [ ! -e "$evil/PWNED" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL lazy fetch rc=$rc payload=$([ -e "$evil/PWNED" ] && echo ran || echo none)"; fi
rm -rf "$evil"
# Throwaway repo: effective autoStash config and a deleted tracked file.
tmp=$fixroot/tmp; mkdir "$tmp"
git init -q -b main "$tmp"; echo hi > "$tmp/f.txt"; git -C "$tmp" add f.txt
git -C "$tmp" -c user.name=t -c user.email=t@t -c commit.gpgsign=false "com""mit" -qm init; rm "$tmp/f.txt"
git -C "$tmp" config rebase.autoStash true
while IFS='|' read -r want c; do
  rc=0; jq -n --arg c "$c" --arg d "$tmp" '{cwd:$d,tool_input:{command:$c}}' | bash "$hook" 2>/dev/null || rc=$?
  if [ "$rc" = "$want" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL tmp-repo want=$want got=$rc: $c"; fi
done <<'TMPCASES'
2|git checkout f.txt
0|git checkout main
2|git rebase main
2|git pull --rebase
0|git rebase --no-autostash main
0|git -c rebase.autoStash=false rebase main
0|git rebase --continue
0|git rebase --abort
0|git -c merge.autoStash=true merge --abort
2|git -c merge.autoStash=true pull
0|git -c merge.autoStash=true pull --dry-run
0|git pull
0|git pull --ff-only
2|git -c pull.rebase=true pull
2|git pull -r
0|git -c pull.rebase=true pull --no-rebase
TMPCASES
rm -rf "$tmp"
# Python warnings-as-errors in the environment must not make the parser fail open.
rc=0; printf '%s' '{"tool_input":{"command":"git checkout -f main"}}' | PYTHONWARNINGS=error bash "$hook" 2>/dev/null || rc=$?
if [ "$rc" = 2 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL PYTHONWARNINGS=error rc=$rc"; fi
rm -f "$err"
cd / || true
echo "pass=$pass fail=$fail"
[ "$fail" = 0 ]
