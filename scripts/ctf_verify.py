#!/usr/bin/env python3
"""Verify a README-CTF submission and update the Hall of Fame.

Runs from .github/workflows/ctf.yml on `issues: opened`.
Proof format: first 12 hex chars of sha256("<FLAG>:<github-login-lowercase>").
Because the proof is bound to the submitter's login, a leaked proof is useless
to anyone else. The flag itself lives only in the CTF_FLAG repo secret.

Untrusted input (issue body) is read from the event JSON and is only ever
regex-matched; it is never passed to a shell.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

README = "README.md"
DB = "ctf/solvers.json"
START, END = "<!--HOF_START-->", "<!--HOF_END-->"
LOGIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
PROOF_RE = re.compile(r"\b[0-9a-f]{12}\b")


def gh(*args):
    if os.environ.get("DRY_RUN"):
        print("gh", *args)
        return
    subprocess.run(["gh", *args], check=False)


def render(solvers):
    if not solvers:
        return "_no one has cracked it yet. first blood is up for grabs._"
    medals = ["🥇", "🥈", "🥉"]
    rows = ["| # | operator | cracked on |", "|:-:|:--|:--|"]
    for i, s in enumerate(solvers):
        rank = medals[i] if i < 3 else str(i + 1)
        rows.append(f"| {rank} | [@{s['login']}](https://github.com/{s['login']}) | {s['date']} |")
    return "\n".join(rows)


def main():
    flag = os.environ.get("CTF_FLAG", "")
    event = json.load(open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8"))
    issue = event["issue"]
    num, login = str(issue["number"]), issue["user"]["login"]
    if not LOGIN_RE.match(login):
        sys.exit("unexpected login format")
    if not flag:
        gh("issue", "comment", num, "--body", "CTF is not armed yet (maintainer: set the `CTF_FLAG` secret).")
        return

    m = PROOF_RE.search((issue.get("body") or "").lower())
    want = hashlib.sha256(f"{flag}:{login.lower()}".encode()).hexdigest()[:12]
    solvers = json.load(open(DB)) if os.path.exists(DB) else []

    if not m or m.group(0) != want:
        gh("issue", "comment", num, "--body",
           "🔒 **ACCESS DENIED.** That proof doesn't match.\n\n"
           f"Remember the proof is bound to *your* login (`{login.lower()}`, lowercase). "
           "Re-check each stage and try again with a new issue.")
        gh("issue", "close", num, "--reason", "not planned")
        return

    if any(s["login"].lower() == login.lower() for s in solvers):
        gh("issue", "comment", num, "--body", "✅ Already in the Hall of Fame. Nice try, though. 😉")
        gh("issue", "close", num, "--reason", "completed")
        return

    solvers.append({"login": login, "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")})
    json.dump(solvers, open(DB, "w"), indent=2)
    text = open(README, encoding="utf-8").read()
    a, b = text.index(START) + len(START), text.index(END)
    open(README, "w", encoding="utf-8").write(text[:a] + "\n" + render(solvers) + "\n" + text[b:])
    gh("issue", "comment", num, "--body",
       f"🔓 **ACCESS GRANTED.** Welcome to the Hall of Fame, @{login}. "
       f"You are operator #{len(solvers)}. Your name is now on the profile README.")
    gh("issue", "close", num, "--reason", "completed")
    print("solver added:", login)


if __name__ == "__main__":
    main()
