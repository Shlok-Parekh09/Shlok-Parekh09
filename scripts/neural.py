#!/usr/bin/env python3
"""assets/neural.svg: your repositories as a living neural map.

Each repo is a neuron. Neurons cluster by language and are wired to the repos
they share the most with (topics, name family, language). Signals travel along
the wires; repos pushed in the last week fire rings. The layout is a small
force-directed simulation (stdlib only), seeded so it is stable between runs.
Pure SMIL, so it animates inside <img>.

The CTF stage-2 hex lives in this file's <desc> (written from ctf/desc.hex).
"""
import math
import os
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Shlok-Parekh09"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/neural.svg"
DESC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ctf", "desc.hex")
W, H = 830, 520
CX, CY = 415, 270
LEFT, RIGHT, TOP, BOT = 40, W - 40, 78, H - 62


def family(name):
    """Leading token of a repo name: FSD_Lab_7 -> fsd, learn-os -> learn."""
    tok = ""
    for ch in name.lower():
        if ch in "-_ .":
            break
        tok += ch
    return tok if len(tok) >= 3 else ""


def main():
    now = datetime.now(timezone.utc)
    rp = [r for r in common.repos(USER) if r["name"].lower() != USER.lower()]
    nodes = []
    for r in rp:
        pushed = datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00"))
        lang = r["language"] if r["language"] in t.LANG else "Other"
        nodes.append(dict(name=r["name"], lang=lang, days=max(0, (now - pushed).days), stars=r["stargazers_count"],
                          size=r["size"], topics=set(r.get("topics") or []), fam=family(r["name"])))
    n = len(nodes)
    if n == 0:
        raise SystemExit("no repositories to draw")

    # ---- similarity -> sparse wiring ----
    def sim(a, b):
        s = 2.0 * len(a["topics"] & b["topics"])
        if a["fam"] and a["fam"] == b["fam"]:
            s += 3.0
        if a["lang"] == b["lang"] and a["lang"] != "Other":
            s += 1.0
        return s

    edges = set()
    for i, a in enumerate(nodes):
        ranked = sorted((j for j in range(n) if j != i), key=lambda j: (-sim(a, nodes[j]), abs(nodes[j]["days"] - a["days"]), j))
        for j in ranked[:2]:
            if sim(a, nodes[j]) >= 1.0:
                edges.add((min(i, j), max(i, j)))
    for i in range(n):  # cross-language bridges from shared topics
        for j in range(i + 1, n):
            if nodes[i]["lang"] != nodes[j]["lang"] and len(nodes[i]["topics"] & nodes[j]["topics"]) >= 2:
                edges.add((i, j))
    edges = sorted(edges)
    deg = Counter()
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1

    # ---- cluster centres on an ellipse ----
    langs = [l for l, _ in Counter(x["lang"] for x in nodes).most_common()]
    g = len(langs)
    centres = {}
    for k, l in enumerate(langs):
        ang = math.radians(-90 + k * 360 / g + (12 if g > 1 else 0))
        centres[l] = (CX + 255 * math.cos(ang), CY + 128 * math.sin(ang))

    # ---- force-directed layout (seeded) ----
    rnd = random.Random(2210)
    for x in nodes:
        c = centres[x["lang"]]
        x["x"], x["y"] = c[0] + rnd.uniform(-28, 28), c[1] + rnd.uniform(-28, 28)
        x["vx"] = x["vy"] = 0.0
        x["r"] = 3.6 + min(3.4, math.log10(x["size"] + 10) - 1.0) * 1.3 + min(3.5, math.sqrt(x["stars"]) * 1.6) + (1.2 if x["days"] <= 7 else 0)
    for it in range(420):
        cool = 1 - it / 420 * 0.85
        for i, a in enumerate(nodes):
            fx = fy = 0.0
            c = centres[a["lang"]]
            fx += (c[0] - a["x"]) * 0.030
            fy += (c[1] - a["y"]) * 0.030
            for j, b in enumerate(nodes):
                if i == j:
                    continue
                dx, dy = a["x"] - b["x"], a["y"] - b["y"]
                d2 = dx * dx + dy * dy + 0.01
                d = math.sqrt(d2)
                min_d = a["r"] + b["r"] + 15
                if d < 150:
                    f = 520.0 / d2
                    if d < min_d:
                        f += (min_d - d) * 0.25
                    fx += dx / d * f
                    fy += dy / d * f
            a["vx"] = (a["vx"] + fx) * 0.62
            a["vy"] = (a["vy"] + fy) * 0.62
        for (i, j) in edges:
            a, b = nodes[i], nodes[j]
            dx, dy = b["x"] - a["x"], b["y"] - a["y"]
            d = math.sqrt(dx * dx + dy * dy) + 0.01
            rest = 46 if a["lang"] == b["lang"] else 130
            f = (d - rest) * 0.012
            a["vx"] += dx / d * f
            a["vy"] += dy / d * f
            b["vx"] -= dx / d * f
            b["vy"] -= dy / d * f
        for a in nodes:
            step = min(5.0, math.hypot(a["vx"], a["vy"]))
            m = math.hypot(a["vx"], a["vy"]) or 1
            a["x"] = min(RIGHT, max(LEFT, a["x"] + a["vx"] / m * step * cool))
            a["y"] = min(BOT, max(TOP, a["y"] + a["vy"] / m * step * cool))

    # ---- labels: most interesting first, no overlaps ----
    def score(i):
        a = nodes[i]
        return 3.0 * math.exp(-a["days"] / 14) + 0.5 * deg[i] + 2 * a["stars"]
    labelled, taken = [], []
    for i in sorted(range(n), key=score, reverse=True):
        a = nodes[i]
        w = 6.2 * len(a["name"][:20]) + 14
        side = 1 if a["x"] < CX + 120 else -1
        box = (a["x"] + (a["r"] + 5 if side > 0 else -(a["r"] + 5 + w)), a["y"] - 8, w, 14)
        if box[0] < 8 or box[0] + w > W - 8:
            continue
        if any(not (box[0] + box[2] < q[0] or q[0] + q[2] < box[0] or box[1] + box[3] < q[1] or q[1] + q[3] < box[1]) for q in taken):
            continue
        taken.append(box)
        labelled.append((i, side))
        if len(labelled) >= 14:
            break
    hubs = sorted(range(n), key=lambda i: -deg[i])[:3]
    active = sum(1 for x in nodes if x["days"] <= 7)

    # ---- draw ----
    desc = ""
    try:
        desc = open(DESC_FILE, encoding="utf-8").read().strip()
    except OSError:
        pass
    alt = (f"Neural map of {n} repositories in {g} language clusters with {len(edges)} connections; "
           f"{active} were pushed in the last 7 days.")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(alt)}">',
         "<title>REPO NEURAL MAP</title>", f"<desc>{desc}</desc>",
         t.defs('<clipPath id="card"><rect width="830" height="520" rx="16"/></clipPath>' + "".join(
             f'<radialGradient id="h{k}"><stop offset="0" stop-color="{t.lang_color(l)}" stop-opacity=".20"/><stop offset="1" stop-color="{t.lang_color(l)}" stop-opacity="0"/></radialGradient>'
             for k, l in enumerate(langs))),
         '<g clip-path="url(#card)">', t.card_open(W, H, "REPO NEURAL MAP", f"{n} repos &#183; {len(edges)} links &#183; {active} firing")]
    for gx in range(LEFT, RIGHT + 1, 32):
        for gy in range(TOP, BOT + 1, 32):
            o.append(f'<circle cx="{gx}" cy="{gy}" r=".9" fill="#ffffff" fill-opacity=".07"/>')
    for k, l in enumerate(langs):
        c = centres[l]
        o.append(f'<circle cx="{c[0]:.0f}" cy="{c[1]:.0f}" r="92" fill="url(#h{k})"/>')
    # wires
    for e, (i, j) in enumerate(edges):
        a, b = nodes[i], nodes[j]
        col = t.lang_color(a["lang"]) if a["lang"] == b["lang"] else t.TEXT3
        o.append(f'<line x1="{a["x"]:.1f}" y1="{a["y"]:.1f}" x2="{b["x"]:.1f}" y2="{b["y"]:.1f}" stroke="{col}" stroke-opacity="{0.34 if a["lang"] == b["lang"] else 0.22}" stroke-width="1"/>')
    # travelling signals
    for e, (i, j) in enumerate(edges):
        if e % 5 in (1, 3):
            continue
        a, b = nodes[i], nodes[j]
        if rnd.random() < .5:
            a, b = b, a
        dur = rnd.uniform(2.4, 6.0)
        col = t.lang_color(a["lang"])
        o.append(f'<circle r="1.9" fill="{col}" opacity="0"><animateMotion path="M{a["x"]:.1f},{a["y"]:.1f} L{b["x"]:.1f},{b["y"]:.1f}" dur="{dur:.1f}s" '
                 f'begin="-{rnd.uniform(0, dur):.1f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;.95;.95;0" keyTimes="0;.15;.85;1" dur="{dur:.1f}s" '
                 f'begin="-{rnd.uniform(0, dur):.1f}s" repeatCount="indefinite"/></circle>')
    # neurons
    for i, a in enumerate(nodes):
        rec = math.exp(-a["days"] / 45)
        col = t.lang_color(a["lang"])
        op = 0.42 + 0.58 * rec
        glow = ' filter="url(#glow)"' if a["days"] <= 14 else ""
        o.append(f'<circle cx="{a["x"]:.1f}" cy="{a["y"]:.1f}" r="{a["r"]:.1f}" fill="{col}" opacity="0"{glow}>'
                 f'<animate attributeName="opacity" from="0" to="{op:.2f}" begin="{0.2 + i * 0.025:.2f}s" dur=".7s" fill="freeze"/></circle>')
        if a["days"] <= 7:
            o.append(f'<circle cx="{a["x"]:.1f}" cy="{a["y"]:.1f}" r="{a["r"]:.1f}" fill="none" stroke="{col}" stroke-width="1.3" opacity="0">'
                     f'<animate attributeName="r" values="{a["r"]:.1f};{a["r"] + 13:.1f}" dur="2.8s" begin="{1.5 + (i % 9) * .31:.2f}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values=".85;0" dur="2.8s" begin="{1.5 + (i % 9) * .31:.2f}s" repeatCount="indefinite"/></circle>')
    for i in hubs:
        a = nodes[i]
        o.append(f'<circle cx="{a["x"]:.1f}" cy="{a["y"]:.1f}" r="{a["r"] + 6:.1f}" fill="none" stroke="{t.TEXT2}" stroke-width=".8" stroke-dasharray="2 3" opacity=".7"/>')
    for i, side in labelled:
        a = nodes[i]
        tx = a["x"] + (a["r"] + 5 if side > 0 else -(a["r"] + 5))
        o.append(f'<text x="{tx:.1f}" y="{a["y"] + 4:.1f}" font-size="{t.T_CAP}" font-weight="{600 if a["days"] <= 7 else 400}" fill="{t.TEXT if a["days"] <= 14 else t.TEXT2}" '
                 f'text-anchor="{"start" if side > 0 else "end"}" stroke="{t.SURFACE}" stroke-width="3" paint-order="stroke">{escape(a["name"][:20])}</text>')
    # cluster captions
    for l in langs:
        c = centres[l]
        cnt = sum(1 for x in nodes if x["lang"] == l)
        o.append(f'<text x="{c[0]:.0f}" y="{(max(TOP - 2, c[1] - 84) if c[1] < CY else min(c[1] + 84, H - 52)):.0f}" class="label" text-anchor="middle" style="fill:{t.lang_color(l)};stroke:{t.SURFACE};stroke-width:3px;paint-order:stroke">{escape(l)} &#183; {cnt}</text>')
    # legend / explainer
    o.append(f'<text x="28" y="{H - 24}" font-size="{t.T_CAP}" fill="{t.TEXT3}">size = repo size &#183; brightness = recency &#183; ringing = pushed this week &#183; dashed = most connected &#183; wires = shared topics, name or language</text>')
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print(f"wrote {OUT}: {n} neurons, {len(edges)} wires, {g} clusters, {active} firing, {len(labelled)} labels, hubs {[nodes[i]['name'] for i in hubs]}")


if __name__ == "__main__":
    main()
