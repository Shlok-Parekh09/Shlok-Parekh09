#!/usr/bin/env python3
"""Add a visitor star to the Contribution Galaxy from a "[STAR]" issue.

Runs from .github/workflows/stars.yml on `issues: opened`. The issue body is
UNTRUSTED text from a stranger that ends up on a public profile, so:
  * it is only read from the event JSON and regex-parsed, never given to a shell
  * the message passes a strict whitelist (letters, digits, space and ! ? ' , -)
    so no URLs, markup or HTML can survive, and is capped at 32 chars
  * a profanity/slur blocklist rejects abuse (leet-speak normalised)
  * colour must be one of five known values
  * one star per login (re-submitting just updates your message)
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

DB = os.environ.get("STARS_DB") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stars", "visitors.json")
LOGIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
COLORS = {"cyan", "pink", "gold", "green", "violet"}
MAX_LEN, MAX_STARS = 32, 300
BLOCK = ["fuck", "shit", "bitch", "cunt", "nigg", "fagg", "retard", "rape", "nazi", "hitler", "slut", "whore",
         "dick", "cock", "pussy", "porn", "sex", "kys", "killyourself", "suicide", "asshole", "bastard", "twat"]
LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "!": "i"})
BODY_RE = re.compile(r"###\s*Message\s*\n+(.*?)\n+###\s*Color\s*\n+(\S+)", re.S | re.I)


def gh(*args):
    if os.environ.get("DRY_RUN"):
        print("gh", *args)
        return
    subprocess.run(["gh", *args], check=False)


def clean(msg):
    msg = re.sub(r"[^A-Za-z0-9 !?',\-]", "", msg)
    return re.sub(r"\s+", " ", msg).strip()[:MAX_LEN]


def blocked(msg):
    flat = re.sub(r"[^a-z]", "", msg.lower().translate(LEET))
    return any(w in flat for w in BLOCK)


def main():
    event = json.load(open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8"))
    issue = event["issue"]
    num, login = str(issue["number"]), issue["user"]["login"]
    if not LOGIN_RE.match(login):
        sys.exit("unexpected login format")

    m = BODY_RE.search(issue.get("body") or "")
    if not m:
        gh("issue", "comment", num, "--body", "Couldn't read that form. Please use the **Add my star** template.")
        gh("issue", "close", num, "--reason", "not planned")
        return
    msg = clean(m.group(1)) or "hello from the void"
    color = m.group(2).strip().lower()
    color = color if color in COLORS else "cyan"
    if blocked(msg):
        gh("issue", "comment", num, "--body", "🚫 That message didn't pass the filter. Try something friendlier and open a new issue.")
        gh("issue", "close", num, "--reason", "not planned")
        return

    db = json.load(open(DB, encoding="utf-8")) if os.path.exists(DB) else []
    db = [v for v in db if v["login"].lower() != login.lower()]  # one star per login
    db.append({"login": login, "msg": msg, "color": color, "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")})
    db = db[-MAX_STARS:]
    json.dump(db, open(DB, "w", encoding="utf-8"), indent=2)
    gh("issue", "comment", num, "--body",
       f"⭐ **Your star is in the galaxy, @{login}.** It appears on the profile within a minute and keeps orbiting. "
       f"Open another issue any time to change your message.")
    gh("issue", "close", num, "--reason", "completed")
    print("star added:", login, color, repr(msg))


if __name__ == "__main__":
    main()
