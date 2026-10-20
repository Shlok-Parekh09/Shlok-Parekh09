#!/usr/bin/env python3
"""assets/skyline.svg: your contribution year as an animated isometric night city.

Research note: the best-known contribution visuals (github-profile-3d-contrib,
lowlighter/metrics isocalendar, Isometric Contributions) are static isometric
skylines. This one animates it: every day is a building (height = commits),
towers rise in a diagonal wave, windows light up and twinkle, searchlights
sweep the sky, a beacon blinks on the peak day and the whole scene loops.
Pure SMIL, so it runs inside <img> on a GitHub README.
"""
import math
import random
import sys
from datetime import date, datetime, timezone
from xml.sax.saxutils import escape

import common
import theme as th

USER = sys.argv[1] if len(sys.argv) > 1 else "Shlok-Parekh09"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/skyline.svg"
W, H = 830, 460
U = (14.2, 1.7)  # one week step across the screen
V = (-6.5, 6.6)  # one weekday step
F = 0.80  # footprint fraction of a cell
MAXH = 128.0
DUR, HOLD = 22.0, 18.6
GREEN = th.A2
BASE = th.RAMP  # level 0..4 top colours
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"


def shade(hexcol, k):
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))


def P(c, r, z=0.0):
    return (c * U[0] + r * V[0], c * U[1] + r * V[1] - z)


def poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def faces(c, r, h):
    A, B, C, D = P(c, r), P(c + F, r), P(c, r + F), P(c + F, r + F)
    A2, B2, C2, D2 = P(c, r, h), P(c + F, r, h), P(c, r + F, h), P(c + F, r + F, h)
    return (poly([A2, B2, D2, C2]),  # top
            poly([C, D, D2, C2]),  # left (front) face
            poly([B, D, D2, B2]))  # right face


def main():
    u = common.user_graph(USER)
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    nw = len(weeks)
    cells = []
    for ci, w in enumerate(weeks):
        for ri, d in enumerate(w["contributionDays"]):
            cells.append((ci, ri, d["contributionCount"], d["date"]))
    counts = sorted(c for _, _, c, _ in cells if c)
    mx = max(counts) if counts else 1
    q = [counts[int(len(counts) * p)] for p in (0.3, 0.6, 0.85)] if counts else [1, 2, 3]
    total = sum(counts)

    def level(c):
        return 0 if c == 0 else 1 + sum(c > t for t in q)

    def height(c):
        return 1.4 if c == 0 else 5 + (MAXH - 5) * (math.log1p(c) / math.log1p(mx)) ** 1.15

    peak = max(cells, key=lambda x: x[2])

    # fit the scene into the card
    xs = [P(c, r)[0] for c in (0, nw) for r in (0, 7)]
    ys_lo = [P(c, r)[1] for c in (0, nw) for r in (0, 7)]
    minx, maxx = min(xs), max(xs)
    top_y = min(ys_lo) - MAXH * 1.15
    bot_y = max(ys_lo)
    sc = min(1.0, (W - 64) / (maxx - minx), (H - 118) / (bot_y - top_y))
    tx = (W - (maxx - minx) * sc) / 2 - minx * sc
    ty = (H - 52) - bot_y * sc

    rnd = random.Random(2210)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="My last year of contributions as an animated isometric night city: each day is a building">',
         f"<title>CONTRIBUTION SKYLINE // {escape(USER)}</title>",
         f"""<defs>
{th.BDR}
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{th.SKY_GRAD[0]}"/><stop offset=".55" stop-color="{th.SKY_GRAD[1]}"/><stop offset="1" stop-color="{th.SKY_GRAD[2]}"/></linearGradient>
<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{th.BEAM}" stop-opacity=".30"/><stop offset="1" stop-color="{th.BEAM}" stop-opacity="0"/></linearGradient>
<radialGradient id="halo"><stop offset="0" stop-color="{th.HALO}" stop-opacity=".35"/><stop offset="1" stop-color="{th.HALO}" stop-opacity="0"/></radialGradient>
<filter id="gs" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<style>text{{font-family:system-ui,-apple-system,'SF Pro Text','Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif}}</style></defs>
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#sky)"/>"""]

    for i in range(90):  # stars
        o.append(f'<circle cx="{rnd.randint(0, W)}" cy="{rnd.randint(0, 230)}" r="{rnd.choice([.5, .8, 1.1])}" fill="{th.STAR_BG}" opacity="{rnd.uniform(.2, .8):.2f}">'
                 f'<animate attributeName="opacity" values=".15;.9;.15" dur="{rnd.uniform(2.5, 7):.1f}s" begin="-{rnd.uniform(0, 6):.1f}s" repeatCount="indefinite"/></circle>')
    # shooting stars
    for k, (sx, sy, dly) in enumerate(((120, 70, 3), (560, 40, 11), (320, 100, 16.5))):
        a = dly / DUR
        o.append(f'<line x1="0" y1="0" x2="-34" y2="-12" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round" opacity="0">'
                 f'<animateTransform attributeName="transform" type="translate" values="{sx} {sy};{sx} {sy};{sx + 150} {sy + 52};{sx + 150} {sy + 52}" keyTimes="0;{a:.4f};{a + .035:.4f};1" dur="{DUR}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{a:.4f};{a + .012:.4f};{a + .035:.4f};1" dur="{DUR}s" repeatCount="indefinite"/></line>')

    o.append(f'<text x="30" y="38" font-size="13" fill="{GREEN}">&#9608; CONTRIBUTION SKYLINE</text>')
    o.append(f'<text x="{W - 24}" y="38" font-size="11" fill="{th.TEXT3}" text-anchor="end">'
             f'{len(cells)} days &#183; {total} contributions &#183; peak {peak[2]} on {peak[3]}</text>')

    o.append(f'<g transform="translate({tx:.1f},{ty:.1f}) scale({sc:.4f})">')
    # ground plane
    g = [P(-0.6, -0.6), P(nw + .6, -0.6), P(nw + .6, 7.6), P(-0.6, 7.6)]
    o.append(f'<polygon points="{poly(g)}" fill="{th.GROUND[0]}" stroke="{th.HAIRLINE}" stroke-width="1"/>')
    for r in range(0, 8):
        a, b = P(-0.6, r - .1), P(nw + .6, r - .1)
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{th.GROUND[1]}" stroke-width=".6"/>')
    last = None
    for ci, wk in enumerate(weeks):  # month ticks on the front edge
        d = date.fromisoformat(wk["contributionDays"][0]["date"])
        if d.month != last:
            x, y = P(ci, 7.9)
            o.append(f'<text x="{x:.0f}" y="{y + 10:.0f}" font-size="{9 / sc:.1f}" fill="{th.TEXT3}">{MONTHS[d.month - 1]}</text>')
            last = d.month

    # buildings, far to near (painter's algorithm)
    order = sorted(cells, key=lambda x: (x[0] * U[1] + x[1] * V[1], x[0]))
    glow_for = sorted((x for x in cells if x[2]), key=lambda x: -x[2])[:10]
    for ci, ri, c, dt in glow_for:  # ground glow under the tallest
        x, y = P(ci + F / 2, ri + F / 2)
        o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="20" ry="8" fill="url(#halo)"/>')

    for ci, ri, c, dt in order:
        lv = level(c)
        h = height(c)
        col = BASE[lv]
        if c == 0:
            top, _, _ = faces(ci, ri, h)
            o.append(f'<polygon points="{top}" fill="{col}" opacity=".85"/>')
            continue
        ts = 0.6 + ci * 0.17 + ri * 0.04
        t = [0, ts, ts + .55, ts + .8, HOLD, HOLD + 1.2, DUR]
        kt = ";".join(f"{x / DUR:.4f}" for x in t)
        fac = [0, 0, 1.07, 1, 1, 0, 0]
        seq = [faces(ci, ri, h * f) for f in fac]
        fills = (col, shade(col, .72), shade(col, .48))
        for part, fill in zip(range(3), fills):
            vals = ";".join(s[part] for s in seq)
            o.append(f'<polygon points="{seq[0][part]}" fill="{fill}"><animate attributeName="points" values="{vals}" keyTimes="{kt}" dur="{DUR}s" repeatCount="indefinite"/></polygon>')
        # windows appear once the tower is up
        if h >= 11:
            floors = max(1, min(16, int(h // 6.5)))
            lit_p = .3 + .1 * lv
            wins = []
            for face_i, (p0, e) in enumerate(((P(ci, ri + F), (U[0] * F, U[1] * F)), (P(ci + F, ri), (V[0] * F, V[1] * F)))):
                shade_k = .9 if face_i == 0 else .75
                for fl in range(floors):
                    for k in range(2):
                        if rnd.random() > lit_p:
                            continue
                        s0 = .16 + k * .44
                        z0 = 3.2 + fl * 6.5
                        if z0 + 3.4 > h - 1:
                            continue
                        pts = [(p0[0] + e[0] * s, p0[1] + e[1] * s - z) for s, z in
                               ((s0, z0), (s0 + .26, z0), (s0 + .26, z0 + 3.4), (s0, z0 + 3.4))]
                        tw = ""
                        if rnd.random() < .28:
                            tw = (f'<animate attributeName="opacity" values="1;.15;1" dur="{rnd.uniform(1.8, 5):.1f}s" '
                                  f'begin="-{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/>')
                        wins.append(f'<polygon points="{poly(pts)}" fill="{rnd.choice(["#ffd98a", "#fff1c2", "#ffc76b"])}" opacity="{shade_k}">{tw}</polygon>')
            if wins:
                wk = ";".join(f"{x / DUR:.4f}" for x in (0, ts + .85, ts + 1.2, HOLD, HOLD + .8, DUR))
                o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{wk}" dur="{DUR}s" repeatCount="indefinite"/>{"".join(wins)}</g>')

    # peak beacon + callout
    pc, pr, pcount, pdate = peak
    bx, by = P(pc + F / 2, pr + F / 2, height(pcount))
    pt = 0.6 + pc * 0.17 + pr * 0.04 + .9
    pk = ";".join(f"{x / DUR:.4f}" for x in (0, pt, pt + .3, HOLD, HOLD + .8, DUR))
    o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{pk}" dur="{DUR}s" repeatCount="indefinite"/>'
             f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx:.1f}" y2="{by - 34 / sc:.1f}" stroke="{th.BEACON[0]}" stroke-width="{1 / sc:.2f}"/>'
             f'<circle cx="{bx:.1f}" cy="{by - 2:.1f}" r="{3 / sc:.1f}" fill="{th.BEACON[0]}" filter="url(#gs)"><animate attributeName="opacity" values="1;.1;1" dur="1.2s" repeatCount="indefinite"/></circle>'
             f'<text x="{bx:.1f}" y="{by - 40 / sc:.1f}" font-size="{11 / sc:.1f}" fill="{th.BEACON[1]}" text-anchor="middle">PEAK &#183; {pcount} commits</text>'
             f'<text x="{bx:.1f}" y="{by - 40 / sc + 13 / sc:.1f}" font-size="{9 / sc:.1f}" fill="{th.BEACON[2]}" text-anchor="middle">{pdate}</text></g>')
    # today marker on the last cell
    lc = cells[-1]
    tx2, ty2 = P(lc[0] + F / 2, lc[1] + F / 2, height(lc[2]))
    o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{pk}" dur="{DUR}s" repeatCount="indefinite"/>'
             f'<circle cx="{tx2:.1f}" cy="{ty2 - 6:.1f}" r="{5 / sc:.1f}" fill="none" stroke="{GREEN}" stroke-width="{1.4 / sc:.2f}"><animate attributeName="r" values="{4 / sc:.1f};{12 / sc:.1f};{4 / sc:.1f}" dur="2s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="1;0;1" dur="2s" repeatCount="indefinite"/></circle>'
             f'<text x="{tx2:.1f}" y="{ty2 - 20 / sc:.1f}" font-size="{10 / sc:.1f}" fill="{GREEN}" text-anchor="middle">TODAY</text></g>')
    o.append("</g>")  # end scene transform

    # searchlights sweeping the sky (screen space)
    for bx0, by0, per, amp, begin in ((tx + P(7, 8.4)[0] * sc, ty + P(7, 8.4)[1] * sc, 8.0, 24, 0),
                                       (tx + P(nw - 8, 8.4)[0] * sc, ty + P(nw - 8, 8.4)[1] * sc, 10.5, 28, -3)):
        o.append(f'<g transform="translate({bx0:.1f},{by0:.1f})"><g>'
                 f'<animateTransform attributeName="transform" type="rotate" values="-{amp};{amp};-{amp}" dur="{per}s" begin="{begin}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" keyTimes="0;.5;1"/>'
                 f'<polygon points="0,0 -26,-300 26,-300" fill="url(#beam)"/></g></g>')

    # bottom bar: legend + caption
    o.append(f'<rect x="0" y="{H - 38}" width="{W}" height="38" fill="{th.GROUND[2]}" opacity=".9"/><line x1="0" y1="{H - 38}" x2="{W}" y2="{H - 38}" stroke="{th.HAIRLINE}"/>')
    o.append(f'<text x="30" y="{H - 14}" font-size="10" fill="{th.TEXT3}">quiet</text>')
    for i, cc in enumerate(BASE):
        o.append(f'<rect x="{66 + i * 18}" y="{H - 25}" width="12" height="12" rx="2" fill="{cc}"/>')
    o.append(f'<text x="164" y="{H - 14}" font-size="10" fill="{th.TEXT3}">busy</text>')
    o.append(f'<text x="{W - 24}" y="{H - 14}" font-size="10" fill="{th.TEXT3}" text-anchor="end">'
             f'1 building = 1 day &#183; taller = more commits &#183; lit windows = active &#183; {datetime.now(timezone.utc):%Y-%m-%d} UTC</text>')
    o.append("</g>")
    o.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="url(#bdr)" stroke-width="1.2"/>')
    o.append("</svg>")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print(f"wrote {OUT}: {len(cells)} buildings, {len(counts)} active, scale {sc:.2f}, peak {peak[2]} on {peak[3]}, {sum(len(x) for x in o) // 1024} KB")


if __name__ == "__main__":
    main()
