#!/usr/bin/env python3
"""assets/vitals.svg: three live gauges in one card.

  1. Activity rings   streak / 90-day consistency / this week's momentum
  2. Circadian clock  when you push, by hour (from the public events feed)
  3. Weekly momentum  26 weeks of contribution totals

Everything is computed from the GitHub API on each run. Pure SMIL.
"""
import math
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Shlok-Parekh09"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/vitals.svg"
TZ_MIN, TZ_NAME = 330, "IST"
W, H = 830, 350
DUR = 14.0


def kt(*pts):  # keyTimes string
    return ";".join(f"{p:.3f}" for p in pts)


def grow(delay, rise=0.18):
    """keyTimes for: hidden -> grown -> hold -> reset. delay in 0..1 of the loop."""
    a = 0.03 + delay
    return kt(0, a, a + rise, 0.86, 0.95, 1)


def main():
    u = common.user_graph(USER)
    ds = common.days(u)
    cur, longest = common.streaks(ds)
    last90 = ds[-90:]
    active90 = sum(1 for _, c in last90 if c)
    week = sum(c for _, c in ds[-7:])
    prior = sum(c for _, c in ds[-91:-7]) / 12.0
    mom = week / prior if prior else 0.0
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    wk = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks][-26:]
    hist, npush = common.push_hours(USER, TZ_MIN)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Activity rings, a circadian push-time clock and a 26 week momentum chart">',
         f"<title>VITALS // {escape(USER)}</title>", t.defs(), t.card_open(W, H, "LIVE VITALS", f"{datetime.now(timezone.utc):%Y-%m-%d} UTC")]
    for x in (290, 560):
        o.append(f'<line x1="{x}" y1="64" x2="{x}" y2="{H - 24}" stroke="{t.HAIRLINE}"/>')

    # ---------- 1. activity rings ----------
    cx, cy = 150, 176
    rings = [
        ("STREAK", min(1, cur / 30), t.RINGS[0], 80, f"{cur} days", "goal 30"),
        ("CONSISTENCY", active90 / 90, t.RINGS[1], 60, f"{active90}/90 days", "active"),
        ("MOMENTUM", min(1, mom / 1.5), t.RINGS[2], 40, f"{week} commits", f"{mom:.1f}x avg week"),
    ]
    o.append(f'<text x="28" y="74" class="label">ACTIVITY RINGS</text>')
    for i, (name, frac, col, r, val, sub) in enumerate(rings):
        c = 2 * math.pi * r
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t.RAISED}" stroke-width="14"/>')
        d0 = i * 0.03
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="14" stroke-linecap="round" '
                 f'transform="rotate(-90 {cx} {cy})" stroke-dasharray="0 {c:.1f}" filter="url(#glow)">'
                 f'<animate attributeName="stroke-dasharray" values="0 {c:.1f};0 {c:.1f};{max(frac, .001) * c:.1f} {c:.1f};{max(frac, .001) * c:.1f} {c:.1f};0 {c:.1f};0 {c:.1f}" '
                 f'keyTimes="{grow(d0, .22)}" dur="{DUR}s" repeatCount="indefinite" calcMode="spline" '
                 f'keySplines="0 0 1 1;.2 .8 .2 1;0 0 1 1;.4 0 .6 1;0 0 1 1"/></circle>')
        y = 292 + i * 17
        o.append(f'<circle cx="34" cy="{y - 4}" r="4" fill="{col}"/>')
        o.append(f'<text x="46" y="{y}" font-size="{t.T_CAP}" fill="{t.TEXT2}">{name.title()}</text>')
        o.append(f'<text x="272" y="{y}" font-size="{t.T_CAP}" font-weight="600" fill="{t.TEXT}" text-anchor="end">{escape(val)} '
                 f'<tspan fill="{t.TEXT3}" font-weight="400">&#183; {escape(sub)}</tspan></text>')
    o.append(f'<text x="{cx}" y="{cy + 5}" font-size="26" font-weight="700" fill="{t.TEXT}" text-anchor="middle">{cur}</text>')
    o.append(f'<text x="{cx}" y="{cy + 19}" class="label" text-anchor="middle" style="font-size:9px;letter-spacing:.08em">DAY STREAK</text>')

    # ---------- 2. circadian clock ----------
    cx2, cy2, r_in, r_max = 425, 190, 46, 84
    top = max(hist) or 1
    night = sum(hist[h] for h in list(range(18, 24)) + list(range(0, 5)))
    morn = sum(hist[h] for h in range(5, 12))
    tot = sum(hist) or 1
    if night / tot > 0.45:
        chrono = "NIGHT OWL"
    elif morn / tot > 0.45:
        chrono = "EARLY BIRD"
    else:
        chrono = "ALL-DAYER"
    peak = max(range(24), key=lambda h: hist[h])
    o.append(f'<text x="318" y="74" class="label">CIRCADIAN RHYTHM</text>')
    o.append(f'<text x="544" y="74" class="label" text-anchor="end">{npush} pushes &#183; {TZ_NAME}</text>')
    o.append(f'<circle cx="{cx2}" cy="{cy2}" r="{r_in - 5}" fill="none" stroke="{t.HAIRLINE}"/>')
    o.append(f'<circle cx="{cx2}" cy="{cy2}" r="{r_max + 8}" fill="none" stroke="{t.HAIRLINE}" stroke-dasharray="2 5"/>')

    def hcol(h):
        if h >= 22 or h < 5:
            return t.CLOCK[0]
        if h < 12:
            return t.CLOCK[1]
        if h < 18:
            return t.CLOCK[2]
        return t.CLOCK[3]

    for h in range(24):
        a = math.radians(h * 15 - 90)
        ux, uy = math.cos(a), math.sin(a)
        ln = 3 if hist[h] == 0 else 8 + (r_max - r_in - 8) * (hist[h] / top) ** 0.8
        x1, y1 = cx2 + r_in * ux, cy2 + r_in * uy
        x2, y2 = cx2 + (r_in + ln) * ux, cy2 + (r_in + ln) * uy
        col = hcol(h)
        op = ".28" if hist[h] == 0 else "1"
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{col}" stroke-width="7" stroke-linecap="round" opacity="{op}"'
                 f'{" filter=\"url(#glow)\"" if h == peak else ""}>'
                 f'<animate attributeName="x2" values="{x1:.1f};{x1:.1f};{x2:.1f};{x2:.1f};{x1:.1f};{x1:.1f}" keyTimes="{grow(h * .006, .16)}" dur="{DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1;0 0 1 1;.4 0 .6 1;0 0 1 1"/>'
                 f'<animate attributeName="y2" values="{y1:.1f};{y1:.1f};{y2:.1f};{y2:.1f};{y1:.1f};{y1:.1f}" keyTimes="{grow(h * .006, .16)}" dur="{DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1;0 0 1 1;.4 0 .6 1;0 0 1 1"/></line>')
    for h, lab in ((0, "00"), (6, "06"), (12, "12"), (18, "18")):
        a = math.radians(h * 15 - 90)
        o.append(f'<text x="{cx2 + (r_max + 20) * math.cos(a):.1f}" y="{cy2 + (r_max + 20) * math.sin(a) + 4:.1f}" class="mono" font-size="10" fill="{t.TEXT3}" text-anchor="middle">{lab}</text>')
    o.append(f'<text x="{cx2}" y="{cy2 - 1}" font-size="10" font-weight="700" fill="{t.TEXT}" text-anchor="middle" letter-spacing=".6">{chrono}</text>')
    o.append(f'<text x="{cx2}" y="{cy2 + 13}" font-size="9" fill="{t.TEXT3}" text-anchor="middle">peak {peak:02d}:00</text>')
    for i, (lab, col) in enumerate((("night", t.CLOCK[0]), ("morning", t.CLOCK[1]), ("day", t.CLOCK[2]), ("evening", t.CLOCK[3]))):
        x = 318 + i * 62
        o.append(f'<circle cx="{x}" cy="{H - 36}" r="4" fill="{col}"/><text x="{x + 9}" y="{H - 32}" font-size="{t.T_CAP}" fill="{t.TEXT2}">{lab}</text>')

    # ---------- 3. weekly momentum ----------
    bx0, base, hmax = 590, 248, 130
    mxw = max(wk) or 1
    o.append(f'<text x="590" y="74" class="label">WEEKLY MOMENTUM</text>')
    o.append(f'<text x="802" y="74" class="label" text-anchor="end">26 weeks</text>')
    pk = max(range(len(wk)), key=lambda i: wk[i])
    for i, v in enumerate(wk):
        h = max(3, hmax * (v / mxw) ** 0.75)
        x = bx0 + i * 8.2
        o.append(f'<rect x="{x:.1f}" y="{base}" width="5.6" height="0" rx="2.8" fill="{"url(#auroraV)" if v else t.RAISED}">'
                 f'<animate attributeName="height" values="0;0;{h:.1f};{h:.1f};0;0" keyTimes="{grow(i * .004, .2)}" dur="{DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1;0 0 1 1;.4 0 .6 1;0 0 1 1"/>'
                 f'<animate attributeName="y" values="{base};{base};{base - h:.1f};{base - h:.1f};{base};{base}" keyTimes="{grow(i * .004, .2)}" dur="{DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1;0 0 1 1;.4 0 .6 1;0 0 1 1"/></rect>')
    px = bx0 + pk * 8.2 + 2.8
    o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt(0, .26, .3, .86, .95, 1)}" dur="{DUR}s" repeatCount="indefinite"/>'
             f'<text x="{min(px, 770):.1f}" y="{base - max(3, hmax) - 10:.0f}" font-size="{t.T_CAP}" font-weight="600" fill="{t.A3}" text-anchor="middle">peak {wk[pk]}</text></g>')
    half = sum(wk[13:])
    prev = sum(wk[:13])
    delta = (half / prev) if prev else 0
    o.append(f'<text x="590" y="{base + 40}" font-size="30" font-weight="700" fill="{t.TEXT}">{delta:.1f}x</text>')
    o.append(f'<text x="590" y="{base + 58}" font-size="{t.T_CAP}" fill="{t.TEXT2}">last 13 weeks vs the 13 before</text>')
    o.append(t.card_border(W, H))
    o.append("</svg>")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print(f"wrote {OUT}: streak {cur}, consistency {active90}/90, momentum {mom:.2f}x, {npush} pushes, {chrono} (peak {peak}h), 13wk delta {delta:.2f}x")


if __name__ == "__main__":
    main()
