#!/usr/bin/env python3
"""Rewrite the OPS block of README.md: a plain mission-brief table for recent repos.

This is the text equivalent of the flight-recorder chart (HIG: charts need an
accessible alternative), rebuilt on every showcase run from the live repo list.
Usage: explorer.py [user] [README.md]
"""
import re
import sys
from datetime import datetime, timezone

import common

USER = sys.argv[1] if len(sys.argv) > 1 else "Shlok-Parekh09"
README = sys.argv[2] if len(sys.argv) > 2 else "README.md"
START, END = "<!--OPS_START-->", "<!--OPS_END-->"
LIMIT = 8


def ago(days):
    if days == 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 60:
        return f"{days}d ago"
    return f"{days // 30}mo ago"


def brief(desc, n=96):
    d = re.sub(r"\s+", " ", (desc or "").strip()).replace("|", "/")
    if not d:
        return "_Still cooking._"
    if len(d) <= n:
        return d
    cut = d[:n].rsplit(" ", 1)[0].rstrip(",.;:-")
    return cut + "…"


def main():
    now = datetime.now(timezone.utc)
    rp = [r for r in common.repos(USER) if r["name"].lower() != USER.lower()]
    rp.sort(key=lambda r: r["pushed_at"], reverse=True)
    rows = ["| Repo | Stack | Last push | Brief |", "|:--|:--|:--|:--|"]
    for r in rp[:LIMIT]:
        days = max(0, (now - datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00"))).days)
        name = f"[**{r['name']}**]({r['html_url']})"
        if r.get("homepage"):
            name += f" · [live]({r['homepage']})"
        rows.append(f"| {name} | `{r['language'] or 'misc'}` | {ago(days)} | {brief(r['description'])} |")
    text = open(README, encoding="utf-8").read()
    a, b = text.index(START) + len(START), text.index(END)
    new = text[:a] + "\n" + "\n".join(rows) + "\n" + text[b:]
    if new != text:
        open(README, "w", encoding="utf-8").write(new)
    print(f"explorer: {min(LIMIT, len(rp))} rows, newest {rp[0]['name']}")


if __name__ == "__main__":
    main()
