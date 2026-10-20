#!/usr/bin/env python3
"""assets/ops.svg: a flight recorder for your active repos.

One lane per repo (most recently pushed first). Each lane is an equaliser of
push activity over the last two weeks, in 6-hour bins, coloured by the repo's
language. A scanner sweeps the timeline, bars rise as it passes, and the newest
push in every lane pulses. Built from the public events feed. Pure SMIL.
"""
import sys
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Shlok-Parekh09"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/ops.svg"
DAYS, BIN_H, LANES = 14, 6, 8
W = 830
LX, RX = 218, 784  # lane area
PITCH, TOPY = 44, 96
DUR = 16.0
HMAX = 26


def ago(td):
    h = td.total_seconds() / 3600
    if h < 1:
        return "just now"
    if h < 24:
        return f"{int(h)}h ago"
    return f"{int(h // 24)}d ago"


def main():
    now = datetime.now(timezone.utc)
    evs = common.push_events(USER)
    repos = {r["name"]: r for r in common.repos(USER)}
    start = now - timedelta(days=DAYS)
    evs = [(n, d) for n, d in evs if d >= start and n in repos]
    nb = DAYS * 24 // BIN_H
    span = (now - start).total_seconds()

    per = {}
    for n, d in evs:
        b = min(nb - 1, int((d - start).total_seconds() / (BIN_H * 3600)))
        per.setdefault(n, [0] * nb)[b] += 1
    last = {}
    for n, d in evs:
        last[n] = max(last.get(n, d), d)
    names = sorted(per, key=lambda n: last[n], reverse=True)[:LANES]
    H = TOPY + max(1, len(names)) * PITCH + 56
    bw = (RX - LX) / nb
    mx = max((max(per[n]) for n in names), default=1)
    total = sum(sum(per[n]) for n in names)

    alt = (f"Push activity for the {len(names)} most recently active repositories over the last {DAYS} days. "
           + "; ".join(f"{n}: {sum(per[n])} pushes, last {ago(now - last[n])}" for n in names) + ".")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(alt)}">',
         "<title>ACTIVE OPS // flight recorder</title>",
         t.defs(f'<clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>'),
         '<g clip-path="url(#card)">',
         t.card_open(W, H, "FLIGHT RECORDER", f"last {DAYS} days &#183; {total} pushes &#183; 6h bins")]

    if not names:  # empty state with guidance (HIG: never a blank chart)
        o.append(f'<text x="{W / 2}" y="{H / 2}" font-size="{t.T_HEAD}" fill="{t.TEXT2}" text-anchor="middle">No pushes in the last {DAYS} days. The recorder fills as soon as I ship.</text>')
        o += ["</g>", t.card_border(W, H), "</svg>"]
        open(OUT, "w", encoding="utf-8").write("\n".join(o))
        print("wrote empty-state", OUT)
        return

    # day grid + weekend shading + labels
    for d in range(DAYS + 1):
        x = LX + d * 24 / BIN_H * bw
        day = start + timedelta(days=d)
        if d < DAYS and (day.weekday() >= 5):
            o.append(f'<rect x="{x:.1f}" y="{TOPY - 18}" width="{24 / BIN_H * bw:.1f}" height="{len(names) * PITCH + 10}" fill="#ffffff" fill-opacity=".03"/>')
        o.append(f'<line x1="{x:.1f}" y1="{TOPY - 18}" x2="{x:.1f}" y2="{TOPY + len(names) * PITCH - 8}" stroke="{t.HAIRLINE}" stroke-width=".7"/>')
        if d < DAYS and d % 2 == 0:
            o.append(f'<text x="{x + 3:.1f}" y="{TOPY - 26}" class="mono" font-size="9" fill="{t.TEXT3}">{day:%d %b}</text>')

    # lanes
    for li, n in enumerate(names):
        y = TOPY + li * PITCH + 28  # baseline
        col = t.lang_color(repos[n]["language"] if repos[n]["language"] in t.LANG else "Other")
        o.append(f'<line x1="{LX}" y1="{y}" x2="{RX}" y2="{y}" stroke="{t.HAIRLINE}"/>')
        o.append(f'<circle cx="34" cy="{y - 11}" r="4" fill="{col}"/>')
        o.append(f'<text x="46" y="{y - 8}" font-size="{t.T_HEAD}" font-weight="600" fill="{t.TEXT}">{escape(n[:22])}</text>')
        o.append(f'<text x="46" y="{y + 7}" font-size="{t.T_CAP}" fill="{t.TEXT3}">{escape(repos[n]["language"] or "misc")} &#183; {ago(now - last[n])}</text>')
        o.append(f'<text x="{RX + 36}" y="{y - 4}" class="mono" font-size="12" fill="{t.TEXT2}" text-anchor="end">{sum(per[n])}</text>')
        newest = max(i for i, c in enumerate(per[n]) if c)
        for b, c in enumerate(per[n]):
            x = LX + b * bw
            if not c:
                o.append(f'<rect x="{x + 1:.1f}" y="{y - 1.5}" width="{bw - 2:.1f}" height="2" rx="1" fill="{t.HAIRLINE}"/>')
                continue
            h = 5 + (HMAX - 5) * (c / mx) ** 0.6
            frac = b / nb
            t0 = 0.8 + frac * 7.2  # when the scanner reaches this bin
            a, e = t0 / DUR, (t0 + .45) / DUR
            kt = ";".join(f"{v:.4f}" for v in (0, a, e, 0.86, 0.95, 1))
            sp = "0 0 1 1;.2 .8 .2 1;0 0 1 1;.4 0 .6 1;0 0 1 1"
            o.append(f'<rect x="{x + 1:.1f}" y="{y}" width="{bw - 2:.1f}" height="0" rx="2" fill="{col}" fill-opacity="{0.55 + 0.45 * min(1, c / mx):.2f}"'
                     f'{" filter=\"url(#glow)\"" if b == newest else ""}>'
                     f'<animate attributeName="height" values="0;0;{h:.1f};{h:.1f};0;0" keyTimes="{kt}" dur="{DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="{sp}"/>'
                     f'<animate attributeName="y" values="{y};{y};{y - h:.1f};{y - h:.1f};{y};{y}" keyTimes="{kt}" dur="{DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="{sp}"/></rect>')
        # newest push pulses
        nx = LX + newest * bw + bw / 2
        o.append(f'<circle cx="{nx:.1f}" cy="{y - 5 - (HMAX - 5) * (per[n][newest] / mx) ** 0.6:.1f}" r="3" fill="none" stroke="{col}" stroke-width="1.2" opacity="0">'
                 f'<animate attributeName="r" values="3;12" dur="2.4s" begin="{8.6 + li * .15:.2f}s;{8.6 + li * .15 + DUR:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".9;0" dur="2.4s" begin="{8.6 + li * .15:.2f}s;{8.6 + li * .15 + DUR:.2f}s" repeatCount="indefinite"/></circle>')

    # scanner + now line
    y0, y1 = TOPY - 20, TOPY + len(names) * PITCH - 6
    k = ";".join(f"{v:.4f}" for v in (0, .8 / DUR, 8.0 / DUR, 1))
    o.append(f'<rect x="{LX}" y="{y0}" width="2" height="{y1 - y0}" fill="{t.A3}" filter="url(#glow)" opacity="0">'
             f'<animate attributeName="x" values="{LX};{LX};{RX};{RX}" keyTimes="{k}" dur="{DUR}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="{k}" dur="{DUR}s" repeatCount="indefinite"/></rect>')
    o.append(f'<line x1="{RX}" y1="{y0}" x2="{RX}" y2="{y1}" stroke="{t.A3}" stroke-width="1.2" stroke-dasharray="3 3"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></line>')
    o.append(f'<text x="{RX}" y="{y1 + 14}" class="label" text-anchor="middle" style="fill:{t.A3}">NOW</text>')
    o.append(f'<text x="{RX + 36}" y="{TOPY - 26}" class="label" text-anchor="end">PUSHES</text>')
    o.append(f'<text x="28" y="{H - 14}" font-size="{t.T_CAP}" fill="{t.TEXT3}">each bar = pushes in a 6-hour window &#183; taller = busier &#183; glowing bar = latest push &#183; shaded columns = weekends</text>')
    o.append("</g>")
    o.append(t.card_border(W, H))
    o.append("</svg>")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print(f"wrote {OUT}: {len(names)} lanes, {total} pushes in {DAYS}d, lanes={names}")


if __name__ == "__main__":
    main()
