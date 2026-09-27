#!/usr/bin/env python3
"""Git guard for the Bash PreToolUse hook. Called by git-guard.sh with the hook
JSON on stdin. Exit 10 blocks the command (the wrapper turns it into 2, and
stderr goes to Claude); exit 0 allows.

Blocks git commands that discard uncommitted work in a tree other sessions and
agents may be editing. Rule: .claude/rules/worktree-agent-dispatch.md.

The tokenizer follows bash closely enough for this job: quotes, backslash
escapes, line continuations, comments only at a word start, redirections (and
their targets) dropped, heredoc bodies skipped unless a shell or interpreter
reads them as its program, and $(...) / backtick bodies scanned as commands of
their own with the cwd reached at their command. python/node/perl/ruby code
(-c/-e or stdin) is scanned for exec calls with string-literal arguments;
Python comments and strings are masked, other languages' are not (so there a
call named in a comment can block).
Known residual bypasses (aliases, computed arguments, script files, xargs-style
indirection it cannot see, GIT_CONFIG_* environment config, plumbing such as
checkout-index, an exec call's cwd= option, launchers such as uv run or npx,
text piped to a shell by echo/printf or process substitution, and a cd inside
a subshell leaking to later commands) are accepted: the guard stops accidents,
not a determined bypass.
"""
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tokenize as pytokenize

WRAPPERS = {"command", "builtin", "exec", "env", "sudo", "doas", "time", "nohup", "nice",
            "timeout", "xargs", "caffeinate", "stdbuf", "ionice", "watch"}
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}"}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
GIT_OPTS_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix",
                     "--config-env", "--attr-source", "--exec-path"}
ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\+?=.*", re.S)
NUMERIC = re.compile(r"[0-9.]+[smhd]?")
SHORT_CLUSTER = re.compile(r"-[A-Za-z]+")
XARGS_INPUT = "<xargs input>"
HEREDOC_DELIM_STOP = set(" \t\n;&|()<>")


def read_heredoc_op(text, i):
    """text[i:i+2] is '<<' (not '<<<'). Return ((delimiter, strip_tabs, quoted),
    index after the delimiter word)."""
    n = len(text)
    i += 2
    strip_tabs = i < n and text[i] == "-"
    if strip_tabs:
        i += 1
    while i < n and text[i] in " \t":
        i += 1
    delim, quoted = [], False
    while i < n and text[i] not in HEREDOC_DELIM_STOP:
        if text[i] in "'\"\\":
            quoted = True
        else:
            delim.append(text[i])
        i += 1
    return ("".join(delim), strip_tabs, quoted), i


def find_substitutions(body):
    """$(...) and backtick bodies inside unquoted-heredoc text, which bash expands."""
    subs, j, n = [], 0, len(body)
    while j < n:
        if body[j] == "\\":
            j += 2
        elif body.startswith("$(", j):
            sub, j = capture_subst(body, j + 2, ")")
            subs.append(sub)
        elif body[j] == "`":
            sub, j = capture_subst(body, j + 1, "`")
            subs.append(sub)
        else:
            j += 1
    return subs


def skip_heredoc_bodies(text, i, heredocs, subs, bodies=None):
    """i is just past the newline that ends a heredoc's command line. Skip each
    pending body; substitutions in an unquoted body go to subs and, with bodies
    given, the body goes to bodies, both as (owning command index, text). Return
    the index after the last delimiter line."""
    n = len(text)
    for op in heredocs:
        delim, strip_tabs, quoted = op[:3]
        start, body_end = i, n
        while i < n:
            k = text.find("\n", i)
            line = text[i:] if k < 0 else text[i:k]
            line_start, i = i, (n if k < 0 else k + 1)
            if (line.lstrip("\t") if strip_tabs else line) == delim:
                body_end = line_start
                break
        owner = op[3] if len(op) > 3 else None
        if not quoted:
            subs.extend((owner, sub) for sub in find_substitutions(text[start:body_end]))
        if bodies is not None and owner is not None:
            bodies.append((owner, text[start:body_end]))
    return i


def match_close(text, i, opener, closer):
    """text[i] is opener. Return the index just past its matching closer."""
    depth, j, n = 0, i, len(text)
    while j < n:
        if text[j] == opener:
            depth += 1
        elif text[j] == closer:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return n


def capture_subst(text, i, closer):
    """text[i] is the first char inside $( or `. Return (body, index after closer)."""
    n = len(text)
    if closer == "`":
        j = i
        while j < n and text[j] != "`":
            j += 2 if text[j] == "\\" else 1
        return text[i:j], j + 1
    depth, j, pending = 1, i, []
    arith = i < n and text[i] == "("  # $(( ... )): << is a shift, not a heredoc
    while j < n:
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == '"':
            j += 1
            while j < n and text[j] != '"':
                if text[j] == "\\":
                    j += 2
                elif text.startswith("$(", j):
                    j = capture_subst(text, j + 2, ")")[1]
                elif text[j] == "`":
                    j = capture_subst(text, j + 1, "`")[1]
                else:
                    j += 1
            j += 1
            continue
        if c == "\n" and pending:
            # Heredoc bodies are not shell syntax: an apostrophe or paren in
            # them must not unbalance the capture.
            j = skip_heredoc_bodies(text, j + 1, pending, [])
            pending = []
            continue
        if text.startswith("<<<", j):
            j += 3
            continue
        if text.startswith("<<", j) and not arith:
            op, j = read_heredoc_op(text, j)
            pending.append(op)
            continue
        if c == "'":
            k = text.find("'", j + 1)
            j = n if k < 0 else k + 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[i:j], j + 1
        j += 1
    return text[i:], n


def tokenize(text):
    """Return (commands, substitutions, bodies, pipe_to): commands is a list of
    simple commands (lists of words, redirections removed); substitutions are
    (command index, $(...) or backtick body) pairs to scan separately; bodies
    are (command index, heredoc or here-string body) pairs; pipe_to maps a
    command's index to the index of the command its stdout is piped into (every
    command of a ( ... ) or { ...; } group piped as a whole maps past the group)."""
    commands, subs, words, bodies, pipe_to = [], [], [], [], {}
    cur, in_word, quoted, drop_next, herestring = [], False, False, False, False
    heredocs = []  # (delimiter, strip_leading_tabs, quoted, owner)
    groups, closed = [], None  # open group start indices; last closed (start, end)
    i, n = 0, len(text)

    def end_word():
        nonlocal cur, in_word, quoted, drop_next, herestring
        if in_word:
            if drop_next:
                if herestring:  # bash <<< 'cmd': a script if the owner is a shell
                    bodies.append((len(commands), "".join(cur)))
                drop_next = herestring = False
            else:
                words.append("".join(cur))
        cur, in_word, quoted = [], False, False

    def end_command():
        nonlocal words, drop_next, herestring, closed
        end_word()
        drop_next = herestring = False
        if words:
            if words[0] == "{":
                groups.append(len(commands))
            commands.append(words)
            if words == ["}"] and groups:
                closed = (groups.pop(), len(commands))
        words = []

    while i < n:
        c = text[i]
        if c == "\\":
            if i + 1 < n and text[i + 1] == "\n":
                i += 2  # line continuation
                continue
            if i + 1 < n:
                cur.append(text[i + 1])
            in_word, quoted = True, True
            i += 2
            continue
        if c == "'":
            k = text.find("'", i + 1)
            k = n if k < 0 else k
            cur.append(text[i + 1:k])
            in_word, quoted = True, True
            i = k + 1
            continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    # In double quotes a backslash escapes only $ ` " \ and newline.
                    if text[j + 1] not in '$`"\\\n':
                        cur.append("\\")
                    cur.append(text[j + 1])
                    j += 2
                    continue
                if text[j] == "$" and j + 1 < n and text[j + 1] == "(":
                    body, j = capture_subst(text, j + 2, ")")
                    subs.append((len(commands), body))
                    cur.append("$(...)")
                    continue
                if text[j] == "`":
                    body, j = capture_subst(text, j + 1, "`")
                    subs.append((len(commands), body))
                    cur.append("`...`")
                    continue
                cur.append(text[j])
                j += 1
            in_word, quoted = True, True
            i = j + 1
            continue
        if c == "$" and i + 1 < n and text[i + 1] == "(":
            body, i = capture_subst(text, i + 2, ")")
            subs.append((len(commands), body))
            cur.append("$(...)")
            in_word = True
            continue
        if c == "`":
            body, i = capture_subst(text, i + 1, "`")
            subs.append((len(commands), body))
            cur.append("`...`")
            in_word = True
            continue
        if c == "#" and not in_word:
            k = text.find("\n", i)
            i = n if k < 0 else k
            continue
        if c in " \t":
            end_word()
            i += 1
            continue
        if c == "\n":
            end_command()
            i += 1
            i = skip_heredoc_bodies(text, i, heredocs, subs, bodies)
            heredocs = []
            continue
        if (text.startswith("((", i) and not in_word
                and (not words or words == ["for"] or words[-1] in KEYWORDS)):
            # Arithmetic command, where << is a shift, only when it closes on a
            # literal )) as bash requires; ((cmd) || x) is nested subshells.
            k = match_close(text, i, "(", ")")
            if text[k - 2:k] == "))" and match_close(text, i + 1, "(", ")") == k - 1:
                subs.extend((len(commands), sub) for sub in find_substitutions(text[i + 2:k]))
                i = k
                continue
        if text.startswith("$[", i):
            k = match_close(text, i + 1, "[", "]")
            subs.extend((len(commands), sub) for sub in find_substitutions(text[i + 2:k]))
            cur.append("$[...]")
            in_word = True
            i = k
            continue
        if c in ";()":
            end_command()
            if c == "(":
                groups.append(len(commands))
            elif c == ")" and groups:
                closed = (groups.pop(), len(commands))
            i += 1
            continue
        if c == "|":
            end_command()
            if text[i:i + 2] != "||" and commands:
                end = len(commands)
                if closed and closed[1] == end:  # (a; b) | sh: the whole group feeds sh
                    for k in range(closed[0], end):
                        pipe_to.setdefault(k, end)
                else:
                    pipe_to[end - 1] = end
            i += 2 if text[i:i + 2] in ("||", "|&") else 1
            continue
        if c == "&":
            if text[i:i + 2] == "&&":
                end_command()
                i += 2
                continue
            if text[i:i + 2] == "&>":
                end_word()
                i += 3 if text[i:i + 3] == "&>>" else 2
                drop_next = True
                continue
            end_command()
            i += 1
            continue
        if c in "<>":
            # A pure-digit word right before the operator is its fd number.
            if in_word and not quoted and "".join(cur).isdigit():
                cur, in_word = [], False
            else:
                end_word()
            if text.startswith("<<<", i):
                i += 3
                drop_next = herestring = True
                continue
            if text.startswith("<<", i):
                op, i = read_heredoc_op(text, i)
                heredocs.append(op + (len(commands),))  # owner: the command being built
                continue
            i += 1
            if i < n and text[i] in ">&|":
                i += 1
            drop_next = True
            continue
        cur.append(c)
        in_word = True
        i += 1
    end_command()
    return commands, subs, bodies, pipe_to


# Block exit code. Not 2: CPython itself exits 2 when it cannot open this
# script, and that must fail open, not block every Bash call.
BLOCK = 10
TOO_DEEP = "the command is nested too deeply to check; split it up"


def base(word):
    return os.path.basename(word).lower()


def unwrap(words, j):
    """Skip wrapper programs (sudo -u me, nice -n 5, timeout 30, xargs -I{} ...)
    and return the index of the real program, or None."""
    while j < len(words) and base(words[j]) in WRAPPERS:
        k = j + 1
        while k < len(words):
            w = words[k]
            if w.startswith("-") or ASSIGN.fullmatch(w) or NUMERIC.fullmatch(w):
                k += 1
                continue
            if base(w) == "git" or base(w) in WRAPPERS:
                break
            prev = words[k - 1]
            if k - 1 > j and prev.startswith("-") and "=" not in prev:
                k += 1  # most likely the previous option's argument
                continue
            break
        j = k
    return j if j < len(words) else None


# The hook runs before the permission prompt and outside any sandbox, in a
# directory the command names, so its own git calls must not execute that repo's
# config: no promisor lazy fetch (ext::, core.sshCommand, uploadpack), no
# transport at all, no fsmonitor, no prompts.
GIT_ENV = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_ALLOW_PROTOCOL="none",
               GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")


def git_query(workdir, *args):
    """Run a read-only git query in workdir. Return (exit code, stdout) or None."""
    try:
        r = subprocess.run(["git", "-C", workdir, "-c", "core.fsmonitor=false", *args],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, env=GIT_ENV, timeout=3, text=True)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def is_revision(workdir, name):
    r = git_query(workdir, "rev-parse", "--verify", "--quiet", "--end-of-options", name + "^{commit}")
    return r is not None and r[0] == 0


def is_tracked(workdir, name):
    r = git_query(workdir, "ls-files", "--error-unmatch", "--", name)
    return r is not None and r[0] == 0


def long_opt(arg, *names):
    """True if arg is one of names or an abbreviation git would accept for it."""
    a = arg.split("=", 1)[0]
    return len(a) > 2 and a.startswith("--") and any(n.startswith(a) for n in names)


def short_flags(arg):
    return arg[1:] if SHORT_CLUSTER.fullmatch(arg) else ""


def check_checkout(rest, workdir):
    positional, after_dd, seen_dd, skip = [], [], False, False
    for a in rest:
        if seen_dd:
            after_dd.append(a)
            continue
        if skip:
            skip = False
            continue
        if a == "--":
            seen_dd = True
            continue
        if long_opt(a, "--force", "--patch", "--pathspec-from-file"):
            return "git checkout --force/--patch/--pathspec-from-file discards uncommitted changes"
        flags = short_flags(a)
        if flags:
            own = re.split("[bB]", flags, maxsplit=1)  # -bfeature: "feature" is the branch name
            if "f" in own[0] or "p" in own[0]:
                return "git checkout -f/-p discards uncommitted changes"
            skip = len(own) == 2 and not own[1]
            continue
        if long_opt(a, "--orphan"):
            skip = True
            continue
        if a.startswith("-"):
            continue
        positional.append(a)
    if after_dd:
        return "git checkout ... -- <path> overwrites the whole file from the index or a commit"
    # ${var} and rev^{/regex} are expansions and revision syntax, not globs.
    if any(ch in re.sub(r"\$\{[^}]*\}|\^\{[^}]*\}", "", a) for a in positional for ch in "*?["):
        return "git checkout <glob> overwrites every matching file (refnames cannot contain * ? [)"
    if XARGS_INPUT in positional:
        return "xargs git checkout <paths> overwrites files"
    if "." in positional or any(a.startswith(":") for a in positional):
        return "git checkout . / pathspec overwrites uncommitted changes"
    if len(positional) >= 2:
        return "git checkout <tree-ish> <path> overwrites the file"
    if len(positional) == 1:
        name = positional[0]
        if name == "-" or name.startswith("@{"):
            return None
        if os.path.exists(os.path.join(workdir, name)):
            if not is_revision(workdir, name):
                return "git checkout <path> overwrites the file (it names an existing path, not a revision)"
        elif is_tracked(workdir, name) and not is_revision(workdir, name):
            return "git checkout <path> restores a deleted tracked file, discarding the uncommitted deletion"
    return None


def clean_flags(rest):
    """(force, dry_run) as git clean's option parser would read rest."""
    force = dry = False
    k = 0
    while k < len(rest):
        a = rest[k]
        if a == "--":
            break
        if a in ("-e", "--exclude"):
            k += 1  # the next word is the pattern
        elif long_opt(a, "--force"):
            force = True
        elif long_opt(a, "--dry-run"):
            dry = True
        elif a.startswith("-") and not a.startswith("--"):
            for idx, ch in enumerate(a[1:]):
                if ch == "e":
                    k += idx == len(a) - 2  # bare -e: the pattern is the next word
                    break  # otherwise the rest of the cluster is the pattern
                force |= ch == "f"
                dry |= ch == "n"
        k += 1
    return force, dry


AUTOSTASH_KEYS = {"pull": ("rebase.autostash", "merge.autostash"),
                  "rebase": ("rebase.autostash",), "merge": ("merge.autostash",)}
TRUE_VALUES = {"true", "yes", "on"}


def is_true(value):
    """git's bool parsing: true/yes/on or a nonzero integer."""
    value = value.strip().lower()
    return value in TRUE_VALUES or (re.fullmatch(r"[+-]?\d+", value) is not None and int(value) != 0)


SEQUENCER_ACTIONS = {"--continue", "--abort", "--skip", "--quit", "--edit-todo",
                     "--show-current-patch"}


def pull_rebases(rest, overrides, workdir):
    """True if git pull would rebase: -r/--rebase[=mode], else pull.rebase."""
    mode = None
    for a in rest:
        if a == "-r" or long_opt(a, "--rebase"):
            mode = a.split("=", 1)[1].lower() if "=" in a else "true"
        elif long_opt(a, "--no-rebase"):
            mode = "false"
    if mode is None:
        mode = overrides.get("pull.rebase")
        if mode is None:
            r = git_query(workdir, "config", "--get", "pull.rebase")
            mode = r[1].lower() if r is not None else ""
    return mode not in ("", "false", "no", "off", "0")


def autostash_on(sub, rest, overrides, workdir):
    """True if git pull/rebase/merge would autostash: --autostash, or a true
    rebase/merge.autoStash from -c / --config-env (last one wins) or the
    effective config, unless --no-autostash is given."""
    if any(a in SEQUENCER_ACTIONS for a in rest):
        return False  # --continue/--abort/... take no --autostash and start no new stash
    if sub == "pull" and any(long_opt(a, "--dry-run") for a in rest):
        return False
    on = False
    for a in rest:
        if long_opt(a, "--autostash"):
            on = True
        elif long_opt(a, "--no-autostash"):
            on = False
    if any(long_opt(a, "--autostash", "--no-autostash") for a in rest):
        return on
    keys = AUTOSTASH_KEYS[sub]
    if sub == "pull":
        keys = ("rebase.autostash",) if pull_rebases(rest, overrides, workdir) else ("merge.autostash",)
    for key in keys:
        if key in overrides:
            on = on or overrides[key]
            continue
        r = git_query(workdir, "config", "--type=bool", "--get", key)
        on = on or (r is not None and r[1] == "true")
    return on


def verdict_for_git(args, cwd):
    """args: words after the git binary. Returns a reason string or None."""
    i, workdir, overrides = 0, cwd, {}
    while i < len(args) and args[i].startswith("-"):
        opt = args[i]
        if opt.startswith("--config-env="):
            # The value comes from an environment variable: assume it is true.
            overrides[opt[len("--config-env="):].split("=", 1)[0].lower()] = True
        if opt in GIT_OPTS_WITH_ARG and i + 1 < len(args):
            if opt == "-C":
                workdir = os.path.normpath(os.path.join(workdir, os.path.expanduser(args[i + 1])))
            elif opt == "-c":
                key, eq, value = args[i + 1].partition("=")
                key = key.lower()
                if key == "pull.rebase":
                    overrides[key] = value.lower() if eq else "true"
                else:
                    overrides[key] = not eq or is_true(value)
            elif opt == "--config-env":
                overrides[args[i + 1].split("=", 1)[0].lower()] = True
            i += 2
            continue
        i += 1
    if i >= len(args):
        return None
    sub, rest = args[i], args[i + 1:]
    # Help is honoured only where no option can take it as a value: first, or
    # right after a sub-subcommand (git stash push --help).
    if rest[:1] in (["--help"], ["-h"]) or (
            rest[:1] and not rest[0].startswith("-") and rest[1:2] in (["--help"], ["-h"])):
        return None
    if sub == "stash":
        if rest and rest[0] in ("list", "show"):
            return None
        return "git stash (anything but list/show) reverts every uncommitted change in the file, not just your own"
    if sub == "restore":
        return "git restore overwrites uncommitted changes"
    if sub == "reset":
        return "git reset rewrites the index or working tree"
    if sub == "clean":
        force, dry = clean_flags(rest)
        if force and not dry:
            return "git clean -f deletes untracked files other sessions may own"
        return None
    if sub == "switch":
        if any(long_opt(a, "--force", "--discard-changes")
               or "f" in re.split("[cC]", short_flags(a), maxsplit=1)[0] for a in rest):  # -cfeat: a name
            return "git switch --discard-changes/-f throws away uncommitted changes"
        return None
    if sub == "checkout":
        return check_checkout(rest, workdir)
    if sub in AUTOSTASH_KEYS and autostash_on(sub, rest, overrides, workdir):
        return (f"git {sub} would autostash (--autostash or rebase/merge.autoStash config), which "
                "stashes uncommitted work and can strand it on conflict; pass --no-autostash "
                f"(or git -c {'merge' if sub == 'merge' else 'rebase'}.autoStash=false)")
    if sub == "worktree" and rest[:1] == ["remove"] and any(
            long_opt(a, "--force") or "f" in short_flags(a) for a in rest[1:]):
        return "git worktree remove --force deletes a worktree with its uncommitted changes"
    return None


def interp_lang(prog):
    for lang, pattern in (("python", r"python[0-9.]*"), ("node", r"node(js)?"),
                          ("perl", r"perl[0-9.]*"), ("ruby", r"ruby[0-9.]*")):
        if re.fullmatch(pattern, prog):
            return lang
    return None


CODE_LETTERS = {"python": "c", "node": "ep", "perl": "eE", "ruby": "e"}
VALUE_LETTERS = {"python": "WX", "node": "rC", "perl": "MmIxdD", "ruby": "rIxECK0"}
VALUE_OPTS = {"python": {"-W", "-X", "--check-hash-based-pycs"},
              "node": {"-r", "--require", "--import", "--input-type", "--loader",
                       "--experimental-loader", "-C", "--conditions"},
              "perl": set(), "ruby": {"-r", "-I", "-C", "-E", "-K"}}


def interp_args(lang, args):
    """Return (inline code strings, reads its program from stdin)."""
    codes, operand, k = [], None, 0
    while k < len(args):
        a = args[k]
        if a == "--":
            operand = args[k + 1] if k + 1 < len(args) else None
            break
        if lang == "node" and a in ("-p", "-e", "-pe", "-ep", "--print", "--eval"):
            k += 1
            while k < len(args) and args[k] in ("-p", "-e", "--print", "--eval"):
                k += 1  # node -p -e 'code': both flags, one program
            if k < len(args):
                codes.append(args[k])
            k += 1
            continue
        if lang == "node" and a.split("=", 1)[0] in ("--eval", "--print"):
            if "=" in a:
                codes.append(a.split("=", 1)[1])
            elif k + 1 < len(args):
                codes.append(args[k + 1])
                k += 1
            k += 1
            continue
        if a in VALUE_OPTS[lang]:
            k += 2
            continue
        if lang == "python" and a.startswith("-m"):
            return codes, False  # runs a module
        if a.startswith("-") and not a.startswith("--") and a != "-":
            letters = a[1:]
            for idx, ch in enumerate(letters):
                if ch in CODE_LETTERS[lang]:
                    attached = letters[idx + 1:]
                    if attached:
                        codes.append(attached)
                    elif k + 1 < len(args):
                        codes.append(args[k + 1])
                        k += 1
                    break
                if ch in VALUE_LETTERS[lang] or not ch.isalpha():
                    break  # the rest of the cluster is this option's value
            if lang == "python" and codes:
                return codes, False  # python -c ends option parsing
            k += 1
            continue
        if a.startswith("-") and a != "-":
            k += 1
            continue
        operand = a
        break
    return codes, not codes and operand in (None, "-")


# Exec calls whose literal arguments are a command: Python subprocess/os,
# Node child_process, Ruby and Perl system/exec. Arguments are read only while
# they are string literals or lists of them; anything computed is not followed.
EXEC_CALL = {
    "python": re.compile(
        r"\b(?:subprocess\s*\.\s*(?:run|call|check_call|check_output|Popen|getoutput|getstatusoutput)"
        r"|os\s*\.\s*(?:system|popen|exec\w*|spawn\w*|posix_spawnp?)"
        r"|(?:\w+\s*\.\s*)?(?:run|call|check_call|check_output|Popen|getoutput|getstatusoutput"
        r"|system|popen))\s*\(\s*(?:args\s*=\s*)?"),
    # /re/.exec(...) is RegExp.exec, not child_process.
    "node": re.compile(r"(?<!/\.)\b(?:execSync|execFileSync|execFile|spawnSync|spawn|exec)\s*\(\s*"),
    "perl": re.compile(r"\b(?:system|exec)\b\s*\(?\s*"),
    "ruby": re.compile(r"\b(?:system|exec|spawn)\b\s*\(?\s*"),
}
STRING_START = {"python": re.compile(r"[rRbBuUfF]{0,2}(\"\"\"|'''|\"|')"),
                "node": re.compile(r"(\"|'|`)"), "perl": re.compile(r"(\"|')"),
                "ruby": re.compile(r"(\"|')")}
# Perl/Ruby text where a backtick is not a command: strings and regex operators.
NOT_BACKTICK_CODE = re.compile(
    r"\b(?:s|tr|y)([/|#!,])(?:\\.|(?!\1).)*\1(?:\\.|(?!\1).)*\1"
    r"|\b(?:m|qr)([/|#!,])(?:\\.|(?!\2).)*\2"
    r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", re.S)
ESCAPES = {"n": "\n", "t": "\t"}


def parse_string(code, j, q):
    out, n = [], len(code)
    while j < n:
        if code.startswith(q, j):
            return "".join(out), j + len(q)
        if code[j] == "\\" and j + 1 < n:
            out.append(ESCAPES.get(code[j + 1], code[j + 1]))
            j += 2
            continue
        out.append(code[j])
        j += 1
    return None, n


def literal_args(code, j, lang):
    """Read the string literals (and lists of them) that start at code[j].
    Return (strings, whether it was a single plain string)."""
    items, groups = [], []  # groups: (was a list, strings read)
    while True:
        while j < len(code) and code[j] in " \t\n":
            j += 1
        close = {"[": "]", "(": ")"}.get(code[j]) if j < len(code) else None
        in_list = close is not None
        if in_list:
            j += 1
        got = []
        while True:
            while j < len(code) and code[j] in " \t\n":
                j += 1
            m = STRING_START[lang].match(code, j)
            if not m:
                break
            value, j = parse_string(code, m.end(), m.group(1))
            if value is None:
                break
            got.append(value)
            while j < len(code) and code[j] in " \t\n":
                j += 1
            if not (in_list and j < len(code) and code[j] == ","):
                break
            j += 1
        if in_list and j < len(code) and code[j] == close:
            j += 1
        if not got:
            break
        items.extend(got)
        groups.append((in_list, len(got)))
        while j < len(code) and code[j] in " \t\n":
            j += 1
        if j >= len(code) or code[j] != ",":
            break
        j += 1
    return items, groups == [(False, 1)]


def python_masked(code):
    """(start, end) spans of Python comments and string literals, so a call
    named inside one is not read as a call. [] when the code does not tokenize:
    nothing is masked, so the scan stays on the blocking side."""
    offsets = [0]
    for line in io.StringIO(code).readlines():
        offsets.append(offsets[-1] + len(line))
    spans, fstrings = [], []
    try:
        for t in pytokenize.generate_tokens(io.StringIO(code).readline):
            name = pytokenize.tok_name[t.type]
            if name in ("COMMENT", "STRING", "FSTRING_START", "FSTRING_END"):
                start = offsets[t.start[0] - 1] + t.start[1]
                end = offsets[t.end[0] - 1] + t.end[1]
                if name == "FSTRING_START":
                    fstrings.append(start)
                elif name == "FSTRING_END":
                    if fstrings:
                        spans.append((fstrings.pop(), end))
                else:
                    spans.append((start, end))
    except Exception:
        return []
    return spans


def exec_strings(code, lang):
    """Shell command strings that code passes to an exec call."""
    found = []
    masked = python_masked(code) if lang == "python" else []
    for m in EXEC_CALL[lang].finditer(code):
        if any(a <= m.start() < b for a, b in masked):
            continue
        items, single = literal_args(code, m.end(), lang)
        if not items:
            continue
        if single:
            found.append(items[0])  # one string: a shell command line
            continue
        if len(items) > 1 and items[0] == items[1]:
            items = items[1:]  # os.execvp("git", ["git", ...])
        found.append(" ".join(shlex.quote(w) for w in items))
    if lang in ("ruby", "perl"):
        found += re.findall(r"`([^`]*)`", NOT_BACKTICK_CODE.sub(" ", code))
        found += [a or b for a, b in re.findall(r"(?:%x|qx)\s*(?:\(([^)]*)\)|\{([^}]*)\})", code)]
    return found


def analyze_code(code, lang, cwd, depth):
    commands = exec_strings(code, lang)
    if commands and depth > 3:
        return TOO_DEEP
    for command in commands:
        reason = analyze(command, cwd, depth)
        if reason:
            return reason
    return None


def check_command(words, cwd, depth):
    """Return (reason or None, cwd after this command)."""
    if depth > 3:
        return TOO_DEEP, cwd
    j = 0
    while j < len(words) and (words[j] in KEYWORDS or ASSIGN.fullmatch(words[j])):
        j += 1
    if j >= len(words):
        return None, cwd
    j = unwrap(words, j)
    if j is None:
        return None, cwd
    prog, args = base(words[j]), words[j + 1:]
    if prog == "cd":
        target = next((a for a in args if not a.startswith("-")), None)
        if target:
            cwd = os.path.normpath(os.path.join(cwd, os.path.expanduser(target)))
        return None, cwd
    if prog == "git":
        if any(base(w) == "xargs" for w in words[:j]):
            args = args + [XARGS_INPUT]  # xargs appends its input as arguments
        return verdict_for_git(args, cwd), cwd
    if prog in SHELLS:
        for k, a in enumerate(args[:-1]):
            if "c" in short_flags(a):
                return analyze(args[k + 1], cwd, depth + 1), cwd
        return None, cwd
    if prog == "eval":
        return analyze(" ".join(args), cwd, depth + 1), cwd
    lang = interp_lang(prog)
    if lang:
        for code in interp_args(lang, args)[0]:
            reason = analyze_code(code, lang, cwd, depth + 1)
            if reason:
                return reason, cwd
        return None, cwd
    if prog == "find":
        segment = None
        for a in args + [";"]:
            if a in ("-exec", "-execdir", "-ok", "-okdir"):
                segment = []
            elif segment is not None and a in (";", "+"):
                segment = [XARGS_INPUT if w == "{}" else w for w in segment]  # found paths
                reason = check_command(segment, cwd, depth + 1)[0]
                if reason:
                    return reason, cwd
                segment = None
            elif segment is not None:
                segment.append(a)
    return None, cwd


def stdin_consumer(words):
    """"shell" if words run a shell that reads its script from stdin, the
    language if they run an interpreter that does, else None."""
    j = 0
    while j < len(words) and (words[j] in KEYWORDS or ASSIGN.fullmatch(words[j])):
        j += 1
    j = unwrap(words, j) if j < len(words) else None
    if j is None:
        return None
    lang = interp_lang(base(words[j]))
    if lang:
        return lang if interp_args(lang, words[j + 1:])[1] else None
    if base(words[j]) not in SHELLS:
        return None
    args, operands, k = words[j + 1:], [], 0
    while k < len(args):
        a = args[k]
        if a in ("-o", "+o", "-O", "+O", "--rcfile", "--init-file"):
            k += 1
        elif not a.startswith(("-", "+")):
            operands.append(a)
        k += 1
    flags = "".join(short_flags(a) for a in args)
    # -n parses without running; -c is analysed in check_command.
    runs = "c" not in flags and "n" not in flags and ("s" in flags or not operands)
    return "shell" if runs else None


def analyze(text, cwd, depth=0):
    if depth > 3:
        return TOO_DEEP
    commands, subs, bodies, pipe_to = tokenize(text)
    last = len(commands)
    for idx in range(last + 1):
        # Substitutions run before their command, with the cwd reached there;
        # any owned past the last command (a trailing assignment) run at the end.
        for owner, body in subs:
            if owner == idx or (idx == last and (owner is None or owner > last)):
                reason = analyze(body, cwd, depth + 1)
                if reason:
                    return reason
        if idx == last:
            break
        for owner, body in bodies:
            if owner != idx:
                continue
            # A heredoc or here-string is a program when its command, or a later
            # stage of the same pipeline, reads one from stdin (bash <<EOF,
            # cat <<EOF | sh, (cat <<EOF) | bash, python3 - <<EOF).
            t, targets = owner, [owner]
            while t in pipe_to:
                t = pipe_to[t]
                targets.append(t)
            for t in targets:
                kind = stdin_consumer(commands[t]) if t < last else None
                if kind == "shell":
                    reason = analyze(body, cwd, depth + 1)
                elif kind:
                    reason = analyze_code(body, kind, cwd, depth + 1)
                else:
                    continue
                if reason:
                    return reason
        reason, cwd = check_command(commands[idx], cwd, depth)
        if reason:
            return reason
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(data, dict):
        return 0
    tool_input = data.get("tool_input")
    cmd = tool_input.get("command") if isinstance(tool_input, dict) else data.get("command")
    if not isinstance(cmd, str) or "git" not in cmd.lower():
        return 0
    cwd = data.get("cwd") if isinstance(data.get("cwd"), str) else os.getcwd()
    try:
        reason = analyze(cmd, cwd)
    except RecursionError:
        reason = TOO_DEEP
    if not reason:
        return 0
    sys.stderr.write(
        "GIT GUARD BLOCKED: " + reason + ".\n\n"
        "Rule (.claude/rules/worktree-agent-dispatch.md): other agents and the user may have live "
        "changes in this tree; never use broad restore, reset, checkout --, stash or clean -f.\n"
        "Instead: Edit the specific hunk back, `git apply -R <patch>` for exactly your own hunks, "
        "or `git switch <branch>` to change branches.\n"
        "If the user really wants this command, they can run it themselves: ! " + cmd.strip()[:200] + "\n"
    )
    return BLOCK


if __name__ == "__main__":
    sys.exit(main())
