"""One design system for every generated asset, with swappable palettes.

Every generator reads named colour ROLES from here (never hex literals), so a new
palette is one block of values in PALETTES. Pick with the PROFILE_THEME env var;
the default is DEFAULT below.

  royal      electric blue + gold on deep navy
  nightfall  violet -> pink -> orange sunset on indigo

Colour rules (HIG): one colour, one meaning. Green = live/ok only. Language
colours are reserved for languages. The accent gradient is brand + intensity.
Text roles are all >= 4.5:1 on SURFACE. Cards are self-contained dark surfaces,
so they read the same on GitHub's light and dark page themes.
"""
import os

DEFAULT = "royal"

PALETTES = {
    "royal": dict(
        CANVAS="#040918", SURFACE="#08112b", RAISED="#111d40", HAIRLINE="#243566",
        TEXT="#eef4ff", TEXT2="#b4c4e8", TEXT3="#8b9dca",
        A1="#4f86ff", A2="#8fc7ff", A3="#ffc233",                  # primary / secondary / highlight
        GRAD=("#4f86ff", "#f2f7ff", "#ffc233"),                    # name/line sweep; near-white middle avoids a muddy blue->gold blend
        RAMP=["#0f1c42", "#2358d8", "#59a2ff", "#ffc233", "#fff4cf"],      # quiet -> busy
        GLOW=("#2f66ff", "#7ab6ff", "#ffb62e"),                    # hero light blobs
        RINGS=("#ffc233", "#4f86ff", "#38d4f5"),                   # streak / consistency / momentum
        CLOCK=("#7f8cff", "#ffc233", "#38d4f5", "#ff8a3d"),        # night / morning / day / evening
        LANG=dict(Python="#34d399", TypeScript="#38bdf8", JavaScript="#ffd23f", Java="#fb7185",
                  HTML="#ff8a3d", C="#8b9bff"),
        SKY_GRAD=("#030714", "#0a1740", "#16307a"), GROUND=("#0a1431", "#1b2c5e", "#050b1e"),
        BEAM="#dbe9ff", HALO="#ffb62e", STAR_BG="#bcd0ff",
        STARS=[(70, 110, 255), (110, 170, 255), (190, 220, 255), (255, 205, 90), (255, 245, 214)],
        GALAXY_HALO=("#2f5bff", "#4f3cff"), DUST="#26356a", RING_LINE="#243566",
        DUOTONE=[(0.00, (8, 16, 44)), (0.30, (31, 80, 205)), (0.55, (89, 162, 255)), (0.80, (255, 194, 51)), (1.00, (255, 246, 214))],
    ),
    "nightfall": dict(
        CANVAS="#07050f", SURFACE="#0f0b21", RAISED="#1a1436", HAIRLINE="#2c2455",
        TEXT="#f3efff", TEXT2="#bdb4de", TEXT3="#948ac0",
        A1="#9d7bff", A2="#ff4fa3", A3="#ff9a3c",
        RAMP=["#1c1740", "#5b34c9", "#c43fa0", "#ff7a3d", "#fff1d6"],
        GLOW=("#9d7bff", "#ff4fa3", "#ff9a3c"),
        RINGS=("#ff9a3c", "#ff4fa3", "#9d7bff"),
        CLOCK=("#9d7bff", "#ffc247", "#38bdf8", "#ff4fa3"),
        LANG=dict(Python="#34d399", TypeScript="#38bdf8", JavaScript="#ffc247", Java="#fb7185",
                  HTML="#ff9a3c", C="#9d7bff"),
        SKY_GRAD=("#06040d", "#150a30", "#3a1458"), GROUND=("#120a26", "#2a1d52", "#0a0618"),
        BEAM="#ffe1f0", HALO="#ff7a3d", STAR_BG="#d8c8ff",
        STARS=[(98, 82, 235), (176, 96, 240), (255, 100, 185), (255, 165, 85), (255, 244, 214)],
        GALAXY_HALO=("#6b3cff", "#8b3cff"), DUST="#3a3270", RING_LINE="#3a2f6e",
        DUOTONE=[(0.00, (22, 14, 48)), (0.30, (96, 52, 200)), (0.55, (212, 66, 160)), (0.80, (255, 150, 78)), (1.00, (255, 241, 214))],
    ),
}

NAME = os.environ.get("PROFILE_THEME", DEFAULT)
if NAME not in PALETTES:
    raise SystemExit(f"unknown PROFILE_THEME {NAME!r}; choose from {sorted(PALETTES)}")
_P = PALETTES[NAME]

# --- expose every role as a module attribute ---
globals().update({k: v for k, v in _P.items() if k != "LANG"})

# --- palette-independent semantics ---
GREEN = "#34d399"   # live / ok only
SKY = "#38bdf8"     # generic cool colour
ROSE = "#fb7185"
AMBER = "#ffc247"
BEACON = ("#ff5c6c", "#ffd0d8", "#ff8da1")                       # peak-day marker, same in every palette
VISITOR = {"cyan": "#38bdf8", "pink": "#ff5fa8", "gold": "#ffc247", "green": "#34d399", "violet": "#9d7bff"}

LANG = dict(_P["LANG"], Other=_P["TEXT3"])

# --- type: system stacks so it renders in the viewer's native font (HIG: SF Pro / SF Mono) ---
SANS = "system-ui,-apple-system,'SF Pro Text','Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
# scale: title 20 / headline 14 / body 13 / caption 11 / label 10 (caps, tracked)
T_TITLE, T_HEAD, T_BODY, T_CAP, T_LABEL = 20, 14, 13, 11, 10

GRAD = globals().get("GRAD", (A1, A2, A3))
GRADIENT_STOPS = ((0, GRAD[0]), (50, GRAD[1]), (100, GRAD[2]))

# gradient hairline <linearGradient> (self-contained: paste into any <defs>)
BDR = (f'<linearGradient id="bdr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{A1}" stop-opacity=".6"/>'
       f'<stop offset=".5" stop-color="{A2}" stop-opacity=".3"/><stop offset="1" stop-color="{A3}" stop-opacity=".6"/></linearGradient>')


def lang_color(name):
    return LANG.get(name, LANG["Other"])


def defs(extra=""):
    """Shared <defs>: gradients, glow, fonts. Include once per SVG."""
    stops = "".join(f'<stop offset="{o}%" stop-color="{c}"/>' for o, c in GRADIENT_STOPS)
    return f"""<defs>
<linearGradient id="aurora" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>
<linearGradient id="auroraV" x1="0" y1="1" x2="0" y2="0">{stops}</linearGradient>
{BDR}
<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<style>
text{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
.label{{font-family:{MONO};font-size:{T_LABEL}px;letter-spacing:.14em;text-transform:uppercase;fill:{TEXT3}}}
</style>{extra}</defs>"""


def card_open(w, h, title, meta="", r=16):
    """Standard card chrome: surface, header row with a live (green) dot."""
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="{SURFACE}"/>'
            f'<circle cx="28" cy="30" r="3.5" fill="{GREEN}"><animate attributeName="opacity" values="1;.25;1" dur="2.4s" repeatCount="indefinite"/></circle>'
            f'<text x="40" y="34" class="label" style="fill:{TEXT2}">{title}</text>'
            + (f'<text x="{w - 28}" y="34" class="label" text-anchor="end">{meta}</text>' if meta else "")
            + f'<line x1="28" y1="48" x2="{w - 28}" y2="48" stroke="{HAIRLINE}"/>')


def card_border(w, h, r=16):
    """Gradient hairline so cards separate from the page."""
    return f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="none" stroke="url(#bdr)" stroke-width="1.2"/>'
