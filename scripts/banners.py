#!/usr/bin/env python3
"""assets/header.svg + assets/div-*.svg: the Aurora hero and section dividers.

Hero: drifting aurora mesh, a gradient name, rotating role line, live status
chips and a faint wave of your real weekly contribution totals along the base.
"""
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import common
import theme as t

USER = sys.argv[1] if len(sys.argv) > 1 else "Shlok-Parekh09"
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "assets"
W = 830
NAME = "Shlok"
ROLES = ["Building with Agentic AI.", "Exploring AI & Cybersecurity.", "3rd-year B.Tech CSE student."]

DIVIDERS = [  # (file, number, label)
    ("div-dossier", "01", "Operator dossier"),
    ("div-vitals", "02", "Vitals"),
    ("div-skyline", "03", "Contribution skyline"),
    ("div-neural", "04", "Repo neural map"),
    ("div-galaxy", "05", "Contribution galaxy"),
    ("div-ops", "06", "Active ops: flight recorder"),
    ("div-ctf", "07", "Intercepted transmission"),
    ("div-arsenal", "08", "Arsenal"),
]


def smooth(pts):
    """Catmull-Rom spline through pts as cubic bezier path data."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def header(last, streak, weekly):
    H = 330
    mx = max(weekly) or 1
    base, amp = H - 14, 74
    pts = [(i * W / (len(weekly) - 1), base - amp * (v / mx) ** 0.7) for i, v in enumerate(weekly)]
    line = smooth(pts)
    area = f"{line} L{W},{H} L0,{H} Z"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="{escape(USER)}: full-stack developer and AI explorer">',
         f"<title>{escape(USER)}</title>",
         t.defs(f"""
<radialGradient id="bm"><stop offset="0" stop-color="{t.GLOW[0]}" stop-opacity=".58"/><stop offset="1" stop-color="{t.GLOW[0]}" stop-opacity="0"/></radialGradient>
<radialGradient id="bv"><stop offset="0" stop-color="{t.GLOW[1]}" stop-opacity=".46"/><stop offset="1" stop-color="{t.GLOW[1]}" stop-opacity="0"/></radialGradient>
<radialGradient id="bc"><stop offset="0" stop-color="{t.GLOW[2]}" stop-opacity=".40"/><stop offset="1" stop-color="{t.GLOW[2]}" stop-opacity="0"/></radialGradient>
<linearGradient id="wavefill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.A2}" stop-opacity=".34"/><stop offset="1" stop-color="{t.A2}" stop-opacity="0"/></linearGradient>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#ffffff" fill-opacity=".09"/></pattern>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>"""),
         '<g clip-path="url(#card)">',
         f'<rect width="{W}" height="{H}" fill="{t.CANVAS}"/>']
    # drifting aurora blobs
    for cx, cy, r, fill, dx, dy, dur in ((170, 110, 300, "bm", 60, 30, 19), (660, 40, 320, "bv", -70, 40, 23), (470, 300, 280, "bc", 50, -50, 27)):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{fill})"><animateTransform attributeName="transform" type="translate" '
                 f'values="0 0;{dx} {dy};0 0" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/></circle>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')

    # wave of real weekly totals
    o.append(f'<path d="{area}" fill="url(#wavefill)"/>')
    o.append(f'<path d="{line}" fill="none" stroke="url(#aurora)" stroke-width="2.2" stroke-linecap="round" pathLength="1" '
             f'stroke-dasharray="1" stroke-dashoffset="1"><animate attributeName="stroke-dashoffset" values="1;0;0;1" keyTimes="0;.18;.9;1" '
             f'dur="16s" repeatCount="indefinite"/></path>')

    # copy
    o.append(f'<text x="50" y="92" class="mono" font-size="12" letter-spacing="3" fill="{t.A3}">AGENTIC AI  &#183;  CYBERSECURITY  &#183;  INDIA</text>')
    o.append(f'<text x="44" y="186" font-size="104" font-weight="800" letter-spacing="-4" fill="url(#aurora)">{NAME}</text>')
    cyc = 4.2 * len(ROLES)
    for i, r in enumerate(ROLES):
        a, b = i / len(ROLES), (i + 1) / len(ROLES)
        kt = f"0;{a:.3f};{a + .03:.3f};{b - .04:.3f};{b - .01:.3f};1" if i else f"0;0;.03;{b - .04:.3f};{b - .01:.3f};1"
        o.append(f'<text x="50" y="228" font-size="{t.T_TITLE + 2}" fill="{t.TEXT}" opacity="0">{escape(r)}'
                 f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{cyc}s" repeatCount="indefinite"/></text>')

    # glass status chips (right)
    chips = [("STATUS", "Online", t.GREEN), ("LAST PUSH", last, t.A2), ("STREAK", f"{streak} days", t.A3)]
    for i, (k, v, c) in enumerate(chips):
        y = 56 + i * 52
        o.append(f'<g><rect x="560" y="{y}" width="228" height="44" rx="12" fill="{t.RAISED}" fill-opacity=".72" stroke="{t.HAIRLINE}"/>'
                 f'<circle cx="580" cy="{y + 22}" r="4" fill="{c}"><animate attributeName="opacity" values="1;.3;1" dur="{2 + i * .6:.1f}s" repeatCount="indefinite"/></circle>'
                 f'<text x="594" y="{y + 19}" class="label">{k}</text>'
                 f'<text x="594" y="{y + 36}" font-size="14" font-weight="600" fill="{t.TEXT}">{escape(v)}</text></g>')
    o.append("</g>")
    o.append(t.card_border(W, H, 18))
    o.append("</svg>")
    return "\n".join(o)


def divider(num, label):
    H = 44
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(label)}">',
        f"<title>{escape(label)}</title>",
        t.defs('<clipPath id="bar"><rect width="830" height="44" rx="12"/></clipPath>'),
        f'<g clip-path="url(#bar)"><rect width="{W}" height="{H}" fill="{t.SURFACE}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#aurora)" opacity=".07"/>',
        f'<rect width="4" height="{H}" fill="url(#auroraV)"/>',
        f'<rect x="-120" width="120" height="{H}" fill="url(#aurora)" opacity=".16"><animate attributeName="x" values="-120;{W};{W}" keyTimes="0;.55;1" dur="9s" repeatCount="indefinite"/></rect></g>',
        f'<text x="24" y="27" class="mono" font-size="12" fill="{t.A2}">{num}</text>',
        f'<text x="54" y="28" font-size="{t.T_HEAD + 2}" font-weight="600" fill="{t.TEXT}">{escape(label)}</text>',
        t.card_border(W, H, 12),
        "</svg>"])


def main():
    u = common.user_graph(USER)
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    cur, _ = common.streaks(common.days(u))
    rp = sorted(common.repos(USER), key=lambda r: r["pushed_at"], reverse=True)
    now = datetime.now(timezone.utc)
    d = (now - datetime.fromisoformat(rp[0]["pushed_at"].replace("Z", "+00:00"))).days
    last = f'{rp[0]["name"][:20]} ({"today" if d == 0 else f"{d}d ago"})'
    with open(f"{OUTDIR}/header.svg", "w", encoding="utf-8") as f:
        f.write(header(last, cur, weekly))
    for fn, num, label in DIVIDERS:
        with open(f"{OUTDIR}/{fn}.svg", "w", encoding="utf-8") as f:
            f.write(divider(num, label))
    print("wrote header + dividers; last push:", last, "| streak", cur)


if __name__ == "__main__":
    main()
