#!/usr/bin/env python3
"""assets/genome.svg: your contribution year as a rotating DNA double helix.

Each of the last 53 weeks is a base pair. The helix spins in pseudo-3D (nodes
swell and brighten at the front, shrink and fade at the back). Rung colour is
that week's intensity; the three biggest weeks are gold "mutations". Under the
helix runs the sequence strip (A quiet -> T -> C -> G busy) and a scanner sweeps
the strand, decoding every week live. Pure SMIL, so it animates inside <img>.
"""
import math
import sys
from datetime import date, datetime, timezone
from xml.sax.saxutils import escape

import common

USER = sys.argv[1] if len(sys.argv) > 1 else "Shlok-Parekh09"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/genome.svg"
W, H = 830, 380
X0, PITCH = 44, 14.2
CY, R = 176, 78
SPIN = 11.0  # seconds per helix rotation
SCAN = 16.0  # seconds per scanner sweep
K = 20  # keyframes per rotation
TURN = 0.43  # radians of twist per week
GREEN, CYAN, GOLD = "#00ff41", "#19f9ff", "#ffd43b"
RUNG = ["#1d3a2b", "#0e8f3f", "#22e062", "#9bffb8", GOLD]
LETTER = "ATCGΩ"
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"


def main():
    u = common.user_graph(USER)
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    nw = len(weeks)
    tot = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    nz = sorted(t for t in tot if t)
    q = [nz[int(len(nz) * p)] for p in (0.3, 0.6)] if nz else [1, 2]
    top3 = set(sorted(range(nw), key=lambda i: tot[i])[-3:]) if any(tot) else set()

    def lvl(i):
        if i in top3:
            return 4
        t = tot[i]
        return 0 if t == 0 else 1 + sum(t > x for x in q)

    levels = [lvl(i) for i in range(nw)]
    xs = [X0 + i * PITCH for i in range(nw)]
    X1 = xs[-1]
    mutations = sum(1 for l in levels if l == 4)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="My last 53 weeks of contributions drawn as a rotating DNA double helix">',
         f"<title>CONTRIBUTION GENOME // {escape(USER)}</title>",
         f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#06100f"/><stop offset="1" stop-color="#0a0d1a"/></linearGradient>
<linearGradient id="scan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset="1" stop-color="{GREEN}" stop-opacity=".28"/></linearGradient>
<filter id="gs" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<style>text{{font-family:{FONT}}}</style></defs>
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#bg)"/>"""]
    # faint lab grid
    for x in range(0, W, 30):
        o.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#0f2a22" stroke-opacity=".5"/>')
    for y in range(0, H, 30):
        o.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#0f2a22" stroke-opacity=".5"/>')

    o.append(f'<text x="{X0}" y="36" font-size="13" fill="{GREEN}">&#9608; GENOME.sequence()</text>')
    o.append(f'<text x="{W - 24}" y="36" font-size="11" fill="#7d8590" text-anchor="end">'
             f'{nw} base pairs &#183; {sum(tot)} contributions &#183; {mutations} mutations</text>')

    # helix backbone guide
    # (rungs first, then nodes, so nodes sit on top)
    def kf(fn):
        return ";".join(f"{fn(2 * math.pi * k / K):.1f}" for k in range(K + 1))

    for sign, col in ((1, GREEN), (-1, CYAN)):  # continuous backbone strands
        frames = []
        for k in range(K + 1):
            a = 2 * math.pi * k / K
            frames.append("M" + " L".join(f"{xs[i]:.1f},{CY + sign * R * math.sin(i * TURN + a):.1f}" for i in range(nw)))
        o.append(f'<path d="{frames[0]}" fill="none" stroke="{col}" stroke-width="2.2" stroke-opacity=".55" stroke-linejoin="round">'
                 f'<animate attributeName="d" values="{";".join(frames)}" dur="{SPIN}s" repeatCount="indefinite"/></path>')

    for i in range(nw):
        ph = i * TURN
        lv = levels[i]
        ya = kf(lambda a, ph=ph: CY + R * math.sin(ph + a))
        yb = kf(lambda a, ph=ph: CY - R * math.sin(ph + a))
        w = 1.2 + lv * 0.7
        o.append(f'<line x1="{xs[i]:.1f}" x2="{xs[i]:.1f}" y1="{CY}" y2="{CY}" stroke="{RUNG[lv]}" stroke-width="{w:.1f}" '
                 f'stroke-linecap="round" stroke-opacity="{0.35 + lv * 0.14:.2f}"{" filter=\"url(#gs)\"" if lv >= 3 else ""}>'
                 f'<animate attributeName="y1" values="{ya}" dur="{SPIN}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y2" values="{yb}" dur="{SPIN}s" repeatCount="indefinite"/></line>')

    for i in range(nw):
        ph = i * TURN
        lv = levels[i]
        base = 2.6 + lv * 0.9
        for strand, sign, col in (("a", 1, GREEN), ("b", -1, CYAN)):
            cy = kf(lambda a, ph=ph, s=sign: CY + s * R * math.sin(ph + a))
            # depth: +1 when the node faces the viewer (cos > 0 for strand a)
            rr = ";".join(f"{base * (1 + .38 * sign * math.cos(ph + 2 * math.pi * k / K)):.2f}" for k in range(K + 1))
            op = ";".join(f"{0.62 + .38 * sign * math.cos(ph + 2 * math.pi * k / K):.2f}" for k in range(K + 1))
            fill = GOLD if lv == 4 else col
            o.append(f'<circle cx="{xs[i]:.1f}" cy="{CY}" r="{base:.1f}" fill="{fill}" filter="url(#gs)">'
                     f'<animate attributeName="cy" values="{cy}" dur="{SPIN}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="r" values="{rr}" dur="{SPIN}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values="{op}" dur="{SPIN}s" repeatCount="indefinite"/></circle>')

    # mutation markers above the helix
    prev = -9
    for i in sorted(top3):
        o.append(f'<path d="M{xs[i]:.1f},{CY - R - 20} l-5,-8 h10 z" fill="{GOLD}"><animate attributeName="opacity" values="1;.3;1" dur="1.4s" repeatCount="indefinite"/></path>')
        if i - prev > 3:
            o.append(f'<text x="{xs[i]:.1f}" y="{CY - R - 34}" font-size="10" fill="{GOLD}" text-anchor="middle">MUTATION</text>')
        prev = i

    # scanner sweep over the helix
    k = "0;1"
    o.append(f'<rect x="{X0 - 40}" y="{CY - R - 16}" width="40" height="{2 * R + 32}" fill="url(#scan)">'
             f'<animate attributeName="x" values="{X0 - 40};{X1 + 10:.0f}" keyTimes="{k}" dur="{SCAN}s" repeatCount="indefinite"/></rect>')
    o.append(f'<rect x="{X0 - 2}" y="{CY - R - 16}" width="2" height="{2 * R + 32}" fill="{GREEN}" filter="url(#gs)">'
             f'<animate attributeName="x" values="{X0 - 2};{X1 + 48:.0f}" keyTimes="{k}" dur="{SCAN}s" repeatCount="indefinite"/></rect>')

    # sequence strip: one letter per week, aligned under its base pair
    sy = 300
    o.append(f'<text x="{X0 - 30}" y="{sy}" font-size="11" fill="#586069">5\'</text>')
    o.append(f'<text x="{X1 + 16:.0f}" y="{sy}" font-size="11" fill="#586069">3\'</text>')
    for i in range(nw):
        lv = levels[i]
        o.append(f'<text x="{xs[i]:.1f}" y="{sy}" font-size="13" font-weight="bold" fill="{RUNG[lv] if lv else "#2c5a43"}" text-anchor="middle">{LETTER[lv]}</text>')
    # reading head that follows the scanner
    o.append(f'<rect x="{X0 - 8}" y="{sy - 16}" width="16" height="22" rx="3" fill="none" stroke="{GREEN}" stroke-width="1.5" filter="url(#gs)">'
             f'<animate attributeName="x" values="{X0 - 8};{X1 - 8:.0f}" keyTimes="{k}" dur="{SCAN}s" repeatCount="indefinite"/></rect>')

    # live decoder: one readout per week shown while the scanner is over it
    for i, w in enumerate(weeks):
        d0 = date.fromisoformat(w["contributionDays"][0]["date"])
        a, b = i / nw, (i + 1) / nw
        kt = f"0;{a:.4f};{b:.4f};1" if i else f"0;0;{b:.4f};1"
        codon = "".join(LETTER[levels[j]] for j in range(max(0, i - 1), min(nw, i + 2)))
        tag = "MUTATION" if levels[i] == 4 else ["silent", "low", "active", "expressed", ""][levels[i]]
        o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0;0" keyTimes="{kt}" dur="{SCAN}s" repeatCount="indefinite" calcMode="discrete"/>'
                 f'<text x="{X0}" y="338" font-size="13" fill="#c9d1d9">WK {i + 1:02d} &#183; {d0.day:02d} {MONTHS[d0.month - 1]} {d0.year}'
                 f' &#183; <tspan fill="{GREEN}">{tot[i]} commits</tspan> &#183; codon <tspan fill="{CYAN}">{escape(codon)}</tspan></text>'
                 f'<text x="{W - 24}" y="338" font-size="13" fill="{GOLD if levels[i] == 4 else "#7d8590"}" text-anchor="end">{tag}</text></g>')
    o.append(f'<text x="{W - 24}" y="{H - 10}" font-size="9" fill="#586069" text-anchor="end">'
             f'A quiet &#183; T low &#183; C active &#183; G expressed &#183; &#937; mutation (top 3 weeks) &#183; {datetime.now(timezone.utc):%Y-%m-%d} UTC</text>')
    o.append("</g>")
    o.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#0f5d2c"/>')
    o.append("</svg>")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print(f"wrote {OUT}: {nw} base pairs, {mutations} mutations, seq={''.join(LETTER[l] for l in levels)}")


if __name__ == "__main__":
    main()
