"""Builds the animated SVGs in ../assets.

    python scripts/build_assets.py

Deterministic: the same code always writes the same files. The contribution
chart is built separately by render_pulse.py.

Design rules, kept on purpose:
- one motion per image, and only where it explains the project
- labels in sentence case and in text colours; data colours are for marks only
- each card states its finding in a sentence instead of a stat box
"""

import math
import os

from svgkit import (AMBER, BLUE, EMBER, GREEN, INK, RED, SANS, TEAL, document, esc, f,
                    periodic_noise, rng, smooth_path)
import nt_geo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

SURFACE = INK[1]
HAIR = INK[4]


def write(name, svg):
    path = os.path.join(ASSETS, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote assets/{name} ({len(svg) / 1024:.1f} KB)")


# ---------------------------------------------------------------------------
# Hero: the Territory at night. One sequence on load: the coast draws, the
# towns light up from north to south, then traffic runs down the highway.
# ---------------------------------------------------------------------------

def build_hero():
    W, H = 1200, 440
    K, X0, Y0, LON0, LAT0 = 25.5, 880, 26, 128.8, -10.9

    def P(lon, lat):
        return (X0 + (lon - LON0) * K, Y0 + (LAT0 - lat) * K)

    css = f"""
.coast{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.6s cubic-bezier(.55,0,.25,1) .2s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.in{{opacity:0;animation:in 1.2s ease forwards}}
@keyframes in{{to{{opacity:1}}}}
.name{{font:700 64px {SANS};fill:{INK[12]};letter-spacing:-.025em}}
.lead{{font:400 27px {SANS};fill:{INK[11]};letter-spacing:-.01em}}
.meta{{font:400 16px {SANS};fill:{INK[9]}}}
.place{{font:500 12.5px {SANS};fill:{INK[10]}}}
.tick{{font:400 11px {SANS};fill:{INK[8]}}}
"""
    body = [f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>']

    grat = []
    for lon in (130, 134, 138):
        x, _ = P(lon, 0)
        grat.append(f'<line x1="{f(x)}" y1="16" x2="{f(x)}" y2="{H - 30}"/>')
        grat.append(f'<text x="{f(x)}" y="{H - 14}" text-anchor="middle" class="tick" stroke="none">{lon}°E</text>')
    for lat in (-14, -20, -26):
        _, y = P(0, lat)
        grat.append(f'<line x1="{X0 - 30}" y1="{f(y)}" x2="{W - 50}" y2="{f(y)}"/>')
        grat.append(f'<text x="{W - 44}" y="{f(y + 4)}" class="tick" stroke="none">{-lat}°S</text>')
    body.append(f'<g stroke="{INK[3]}" stroke-width="1">{"".join(grat)}</g>')

    coast = [P(*p) for p in nt_geo.COAST]
    border = [P(*p) for p in nt_geo.BORDER]
    d = smooth_path(coast) + "".join(f"L{f(x)},{f(y)}" for x, y in border) + "Z"
    islands = "".join(smooth_path([P(*p) for p in isl], closed=True) for isl in nt_geo.ISLANDS)
    body.append(f'<path class="in" style="animation-delay:1.6s" d="{d}{islands}" fill="{TEAL[3]}" fill-opacity=".35"/>')
    body.append(f'<path class="coast" pathLength="1" d="{d}" fill="none" stroke="{TEAL[7]}" stroke-width="1.3" stroke-linejoin="round"/>')
    body.append(f'<path class="in" style="animation-delay:1.8s" d="{islands}" fill="none" stroke="{TEAL[7]}" stroke-width="1.1"/>')

    # roads: the Stuart Highway in teal, the rest thin and quiet
    spine = [P(*nt_geo.town(n)[1:3]) for n in nt_geo.BACKBONE]
    spine_d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in spine)
    spurs = "".join("M" + " L".join(f"{f(x)},{f(y)}" for x, y in (P(*nt_geo.town(n)[1:3]) for n in s))
                    for s in nt_geo.SPURS)
    body.append(f'<g class="in" style="animation-delay:2.6s">'
                f'<path d="{spurs}" fill="none" stroke="{INK[6]}" stroke-width=".9"/>'
                f'<path id="hwy" d="{spine_d}" fill="none" stroke="{TEAL[6]}" stroke-width="1.3"/></g>')

    # towns light up north to south, then hold
    lights = []
    for name, lon, lat, size in nt_geo.TOWNS:
        x, y = P(lon, lat)
        delay = 2.0 + (-11 - lat) / 15 * 1.6
        r_glow, r_core = {3: (11, 2.6), 2: (7, 2.0), 1: (4.5, 1.4)}[size]
        lights.append(f'<g class="in" style="animation-delay:{delay:.2f}s">'
                      f'<circle cx="{f(x)}" cy="{f(y)}" r="{r_glow}" fill="{AMBER}" opacity=".16"/>'
                      f'<circle cx="{f(x)}" cy="{f(y)}" r="{r_core}" fill="#fde9b8"/></g>')
    body.append("".join(lights))
    for name, dx, anchor in [("Darwin", -12, "end"), ("Katherine", 12, "start"),
                             ("Tennant Creek", 12, "start"), ("Alice Springs", 12, "start")]:
        _, lon, lat, _ = nt_geo.town(name)
        x, y = P(lon, lat)
        body.append(f'<text class="place in" style="animation-delay:3.4s" x="{f(x + dx)}" y="{f(y + 4)}" text-anchor="{anchor}">{name}</text>')

    # the one continuous motion: traffic on the highway
    for k in range(2):
        start = 4 + k * 7
        body.append(f'<circle r="2.4" fill="{TEAL[9]}" opacity="0"><set attributeName="opacity" to="1" begin="{start}s"/>'
                    f'<animateMotion dur="14s" begin="{start}s" repeatCount="indefinite"><mpath href="#hwy"/></animateMotion></circle>')

    body.append(f'<g class="in" style="animation-delay:.3s">'
                f'<text x="64" y="176" class="name">Harsh Rastogi</text>'
                f'<text x="66" y="230" class="lead">I turn Territory data into decisions,</text>'
                f'<text x="66" y="266" class="lead">not just dashboards.</text></g>')
    body.append(f'<g class="in" style="animation-delay:.9s">'
                f'<text x="66" y="324" class="meta">Data scientist in Darwin, Northern Territory.</text>'
                f'<text x="66" y="348" class="meta">Master of Data Science, Charles Darwin University.</text></g>')

    return document(W, H, "Harsh Rastogi, data scientist in Darwin",
                    "A map of the Northern Territory at night. The coastline draws in, town lights come on "
                    "from north to south, and traffic moves along the Stuart Highway. Text: Harsh Rastogi. "
                    "I turn Territory data into decisions, not just dashboards.",
                    css, "\n".join(body))


# ---------------------------------------------------------------------------
# Project cards. The top band is a small working model of the project; the
# text underneath says what it found.
# ---------------------------------------------------------------------------

CW, CH, VH = 560, 296, 176

CARD_CSS = f"""
.ttl{{font:600 23px {SANS};fill:{INK[12]};letter-spacing:-.01em}}
.txt{{font:400 15px {SANS};fill:{INK[10]}}}
.stk{{font:400 12.5px {SANS};fill:{INK[8]}}}
.lbl{{font:400 11.5px {SANS};fill:{INK[10]}}}
.lbl2{{font:500 11.5px {SANS};fill:{INK[12]}}}
"""


def card(slug, *, title, lines, tools, viz, viz_css, desc):
    text = "".join(f'<text x="22" y="{VH + 62 + i * 21}" class="txt">{esc(l)}</text>' for i, l in enumerate(lines))
    body = f"""<defs><clipPath id="band"><path d="M1,{VH} V9 a8,8 0 0 1 8,-8 H{CW - 9} a8,8 0 0 1 8,8 V{VH} Z"/></clipPath></defs>
<rect x=".5" y=".5" width="{CW - 1}" height="{CH - 1}" rx="8.5" fill="{SURFACE}" stroke="{HAIR}"/>
<g clip-path="url(#band)">
{viz}
</g>
<line x1="1" y1="{VH + .5}" x2="{CW - 1}" y2="{VH + .5}" stroke="{HAIR}"/>
<text x="22" y="{VH + 34}" class="ttl">{esc(title)}</text>
{text}
<text x="22" y="{CH - 16}" class="stk">{esc(tools)}</text>"""
    write(f"projects/{slug}.svg", document(CW, CH, title, desc, CARD_CSS + viz_css, body))


def viz_underlink():
    nodes = [(56, 112), (140, 88), (224, 116), (308, 84), (392, 114), (470, 88), (520, 112)]
    fail = 4
    seg = " L".join(f"{x},{y}" for x, y in nodes)
    up = " L".join(f"{x},{y}" for x, y in nodes[:fail + 1])
    down = " L".join(f"{x},{y}" for x, y in nodes[fail:])
    css = f"""
.down{{animation:down 10s ease-in-out infinite}}
@keyframes down{{0%,50%,86%,100%{{opacity:1}}56%,80%{{opacity:.15}}}}
.flt{{animation:flt 10s ease-in-out infinite}}
@keyframes flt{{0%,48%,88%,100%{{stroke:{TEAL[8]}}}52%,82%{{stroke:{RED}}}}}
.warn{{opacity:0;animation:warn 10s ease-in-out infinite}}
@keyframes warn{{0%,51%,84%,100%{{opacity:0}}56%,80%{{opacity:1}}}}
.pk{{animation:pk 10s linear infinite}}
@keyframes pk{{0%,50%,84%,100%{{opacity:1}}53%,81%{{opacity:0}}}}
"""

    def tower(x, y, cls=""):
        c = f' class="{cls}"' if cls else ""
        return (f'<g transform="translate({x},{y})"{c} stroke="{TEAL[8]}" fill="none" stroke-width="1.5" stroke-linecap="round">'
                f'<path d="M0,-13 L-6,6 M0,-13 L6,6 M-3.8,-2 H3.8"/></g>')

    out = [f'<path d="M{nodes[1][0]},{nodes[1][1]} Q{nodes[2][0]},{nodes[2][1] + 48} {nodes[3][0]},{nodes[3][1]}" fill="none" stroke="{INK[6]}"/>',
           f'<text x="{nodes[2][0]}" y="{nodes[2][1] + 42}" text-anchor="middle" class="lbl">alternative path</text>',
           f'<path d="M{up}" fill="none" stroke="{TEAL[7]}" stroke-width="1.5"/>',
           f'<path class="down" d="M{down}" fill="none" stroke="{TEAL[7]}" stroke-width="1.5"/>',
           f'<path id="chain" d="M{seg}" fill="none"/>']
    fx, fy = nodes[0]
    out.append(f'<rect x="{fx - 20}" y="{fy - 11}" width="40" height="22" rx="4" fill="{SURFACE}" stroke="{TEAL[7]}"/>'
               f'<text x="{fx}" y="{fy + 4}" text-anchor="middle" class="lbl2">Fibre</text>')
    for i, (x, y) in enumerate(nodes[1:-1], start=1):
        if i == fail:
            out.append(tower(x, y, "flt"))
        elif i > fail:
            out.append(f'<g class="down">{tower(x, y)}</g>')
        else:
            out.append(tower(x, y))
    cx, cy = nodes[-1]
    out.append(f'<g class="down"><path d="M{cx - 10},{cy + 8} V{cy - 2} L{cx},{cy - 10} L{cx + 10},{cy - 2} V{cy + 8} Z" '
               f'fill="{GREEN[3]}" stroke="{GREEN[8]}" stroke-width="1.4"/></g>')
    out.append(f'<text x="{cx + 12}" y="{cy + 26}" text-anchor="end" class="lbl">Community</text>')
    for k in range(2):
        out.append(f'<g class="pk"><circle r="2.6" fill="#e6fbff"><animateMotion dur="5s" begin="{k * 2.5}s" repeatCount="indefinite"><mpath href="#chain"/></animateMotion></circle></g>')
    wx, wy = nodes[fail]
    out.append(f'<g class="warn"><text x="{wx}" y="{wy - 26}" text-anchor="middle" class="lbl2">Single-path relay fails</text>'
               f'<text x="{cx + 12}" y="{cy - 20}" text-anchor="end" class="lbl2">No signal</text></g>')
    out.append(f'<text x="22" y="32" class="lbl">One radio chain from fibre to a remote community, up to six hops</text>')
    return "\n".join(out), css


def viz_pyrantis():
    r = rng(5)
    cols, rows, size, gap = 34, 5, 12, 2.5
    x0, y0 = 22, 58
    cyc = 14
    css = f"""
.e{{fill:#1d3524;animation:e {cyc}s linear infinite}}
@keyframes e{{0%,30%{{fill:#1d3524}}33%{{fill:{AMBER}}}40%,88%{{fill:#5b4318}}96%,100%{{fill:#1d3524}}}}
.l{{fill:#1d3524;animation:l {cyc}s linear infinite}}
@keyframes l{{0%,62%{{fill:#1d3524}}66%{{fill:{EMBER}}}74%,96%{{fill:#5a2117}}99%,100%{{fill:#1d3524}}}}
.scrub{{animation:scrub {cyc}s linear infinite}}
@keyframes scrub{{from{{transform:translateX(0)}}to{{transform:translateX({cols * (size + gap) - gap}px)}}}}
"""
    out = []
    for cy in range(rows):
        for cx in range(cols):
            x, y = x0 + cx * (size + gap), y0 + cy * (size + gap)
            roll, north = r.random(), 1 - cy / rows
            if roll < 0.14 + 0.08 * north:
                out.append(f'<rect class="e" x="{f(x)}" y="{f(y)}" width="{size}" height="{size}" rx="2" style="animation-delay:-{r.uniform(0, 3.2):.2f}s"/>')
            elif roll < 0.33 + 0.06 * (1 - north):
                out.append(f'<rect class="l" x="{f(x)}" y="{f(y)}" width="{size}" height="{size}" rx="2" style="animation-delay:-{r.uniform(0, 4.2):.2f}s"/>')
            else:
                out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{size}" height="{size}" rx="2" fill="#1d3524"/>')
    span = cols * (size + gap) - gap
    ty = y0 + rows * (size + gap) + 4
    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    for i, m in enumerate(months):
        out.append(f'<text x="{f(x0 + span * (i + 0.5) / 12)}" y="{ty + 14}" text-anchor="middle" class="lbl">{m}</text>')
    cut = x0 + span * 4 / 12
    out.append(f'<line x1="{f(cut)}" y1="{y0 - 6}" x2="{f(cut)}" y2="{ty}" stroke="{INK[11]}" stroke-width="1"/>')
    out.append(f'<text x="{f(cut + 6)}" y="{y0 - 10}" class="lbl2">31 July</text>')
    out.append(f'<g class="scrub"><line x1="{x0}" y1="{y0 - 3}" x2="{x0}" y2="{ty - 2}" stroke="#fff" stroke-opacity=".5"/></g>')
    lx = 22
    for label, col in [("Unburnt", "#2f5a3a"), ("Early fire", AMBER), ("Late fire", EMBER)]:
        out.append(f'<rect x="{lx}" y="24" width="10" height="10" rx="2" fill="{col}"/><text x="{lx + 15}" y="33" class="lbl">{label}</text>')
        lx += 15 + len(label) * 6.2 + 18
    return "\n".join(out), css


def scroll_css(name, dist, dur):
    return (f".{name}{{animation:{name} {dur}s linear infinite}}"
            f"@keyframes {name}{{from{{transform:translateX(0)}}to{{transform:translateX(-{dist}px)}}}}")


def trace(fn, period, base, amp, step=4, spikes=()):
    pts = []
    for x in range(0, period * 2 + 1, step):
        y = base + fn(x) * amp
        for sx, sa in spikes:
            dxs = min(abs(x - sx), abs(x - sx - period))
            if dxs < 14:
                y -= sa * (1 - dxs / 14) * (1 if (x // step) % 2 else -0.6)
        pts.append((x, y))
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)


def viz_conflux():
    r = rng(8)
    P = 560
    air_spikes = [(130, 28), (395, 24)]
    sea_spikes = [(250, 22), (480, 26)]
    air = trace(periodic_noise(r, P, 6), P, 82, 11, spikes=air_spikes)
    sea = trace(periodic_noise(r, P, 6), P, 134, 8, spikes=sea_spikes)
    css = scroll_css("scr", P, 18)
    marks = []
    for off in (0, P):
        for sx, _ in air_spikes:
            marks.append(f'<circle cx="{sx + off}" cy="44" r="3.5" fill="{TEAL[8]}"/>')
        for sx, _ in sea_spikes:
            marks.append(f'<circle cx="{sx + off}" cy="166" r="3.5" fill="{BLUE[8]}"/>')
    out = [f'<g class="scr"><path d="{air}" fill="none" stroke="{TEAL[8]}" stroke-width="1.5"/>'
           f'<path d="{sea}" fill="none" stroke="{BLUE[8]}" stroke-width="1.5"/>{"".join(marks)}</g>',
           f'<rect x="0" y="0" width="74" height="176" fill="{SURFACE}"/>',
           f'<text x="22" y="86" class="lbl2">Air</text>',
           f'<text x="22" y="138" class="lbl2">Sea</text>',
           f'<text x="22" y="48" class="lbl">flags</text>',
           f'<text x="22" y="170" class="lbl">flags</text>',
           f'<line x1="74.5" y1="0" x2="74.5" y2="176" stroke="{HAIR}"/>']
    return "\n".join(out), css


def viz_terraiq():
    r = rng(21)
    P, bw = 560, 7
    css = scroll_css("tape", P, 22)
    vals = []
    for _ in range(P // (bw + 3)):
        v = r.random() ** 2.2
        vals.append(0.03 if r.random() < 0.35 else v)
    top, bot = [], []
    for off in (0, P):
        for i, v in enumerate(vals):
            x = off + i * (bw + 3)
            h1, h2 = 3 + v * 26, 3 + v * 34
            top.append(f'<rect x="{x}" y="{f(96 - h1)}" width="{bw}" height="{f(h1)}" rx="1.5"/>')
            bot.append(f'<rect x="{x}" y="{f(150 - h2)}" width="{bw}" height="{f(h2)}" rx="1.5"/>')
    out = [f'<defs><linearGradient id="win" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
           f'<stop offset=".64" stop-color="#fff" stop-opacity="0"/><stop offset=".7" stop-color="#fff"/></linearGradient>'
           f'<mask id="feed"><rect width="560" height="176" fill="url(#win)"/></mask></defs>',
           f'<g mask="url(#feed)"><g class="tape" fill="{BLUE[8]}">{"".join(top)}</g></g>',
           f'<g class="tape" fill="{TEAL[7]}">{"".join(bot)}</g>',
           f'<line x1="22" y1="104.5" x2="538" y2="104.5" stroke="{HAIR}"/>',
           f'<line x1="392.5" y1="56" x2="392.5" y2="98" stroke="{INK[9]}"/>',
           f'<text x="22" y="32" class="lbl">Rainfall readings move right to left</text>',
           f'<text x="538" y="50" text-anchor="end" class="lbl2">Public feed</text>',
           f'<text x="386" y="70" text-anchor="end" class="lbl">gone after 72 hours</text>',
           f'<rect x="16" y="112" width="118" height="20" fill="{SURFACE}"/>',
           f'<text x="22" y="126" class="lbl2">TerraIQ keeps all</text>']
    return "\n".join(out), css


def viz_avian():
    r = rng(3)
    P = 560
    css = scroll_css("spec", P, 18)
    noise, calls = [], []
    for off in (0, P):
        for i in range(0, P, 10):
            for j in range(56, 150, 11):
                a = r.random() * 0.2 * (1 - (j - 56) / 120)
                if a > 0.05:
                    noise.append(f'<rect x="{off + i}" y="{j}" width="10" height="11" fill="{TEAL[6]}" opacity="{a:.2f}"/>')
    rc = rng(17)
    shapes = []
    for k, cx in enumerate([40, 150, 270, 360, 470]):
        y = rc.uniform(80, 108)
        if k == 3:
            y = 84
        kind = k % 3
        if kind == 0:
            d = f"M{cx},{f(y)} q14,-12 30,8 t26,14"
        elif kind == 1 or k == 3:
            d = f"M{cx},{f(y)} " + " ".join(f"l5,{-8 if i % 2 else 8}" for i in range(10))
        else:
            d = f"M{cx},{f(y + 16)} c12,-4 24,-20 46,-26"
        shapes.append((cx, y, d))
    for off in (0, P):
        for cx, y, d in shapes:
            calls.append(f'<path transform="translate({off},0)" d="{d}" fill="none" stroke="{GREEN[9]}" stroke-width="2.6" stroke-linecap="round"/>')
        bx, by = shapes[3][0], shapes[3][1]
        calls.append(f'<g transform="translate({off},0)"><rect x="{bx - 10}" y="{f(by - 22)}" width="72" height="44" rx="3" fill="none" stroke="{INK[11]}"/>'
                     f'<text x="{bx - 10}" y="{f(by + 40)}" class="lbl">BirdNET: Bicknell\'s Thrush</text>'
                     f'<line x1="{bx - 11}" y1="{f(by + 36)}" x2="{bx + 128}" y2="{f(by + 36)}" stroke="{INK[10]}"/>'
                     f'<text x="{bx - 10}" y="{f(by + 57)}" class="lbl2">Regional model: correct</text></g>')
    out = [f'<g class="spec">{"".join(noise)}{"".join(calls)}</g>',
           f'<rect x="0" y="48" width="50" height="128" fill="{SURFACE}"/>',
           f'<line x1="50.5" y1="48" x2="50.5" y2="176" stroke="{HAIR}"/>',
           f'<text x="22" y="32" class="lbl">Bird calls in Territory field audio</text>']
    for k, lab in enumerate(["8 kHz", "4 kHz", "2 kHz"]):
        out.append(f'<text x="12" y="{70 + k * 34}" class="lbl">{lab}</text>')
    return "\n".join(out), css


def viz_bushmetrics():
    r = rng(9)
    K, X0, Y0 = 10.2, 404, 8

    def P(lon, lat):
        return X0 + (lon - 128.8) * K, Y0 + (-10.9 - lat) * K
    css = """
.cold{animation:cold 4s ease-in-out infinite}
@keyframes cold{0%,100%{opacity:.55}50%{opacity:1}}
"""
    s = 3.3
    dx, dy = s * math.sqrt(3) + 0.9, s * 1.5 + 0.8
    hexes, cold = [], []
    row, y = 0, Y0 + 2
    while y < Y0 + 15.2 * K:
        x = X0 + (dx / 2 if row % 2 else 0)
        while x < X0 + 9.3 * K:
            lon, lat = 128.8 + (x - X0) / K, -10.9 - (y - Y0) / K
            if nt_geo.inside(lon, lat):
                pts = " ".join(f"{f(x + s * math.cos(math.radians(60 * k + 30)))},{f(y + s * math.sin(math.radians(60 * k + 30)))}" for k in range(6))
                if 129.2 <= lon <= 132.3 and -21.8 <= lat <= -18.4:
                    cold.append(f'<polygon points="{pts}"/>')
                else:
                    north = (-lat - 11) / 15
                    col = GREEN[7] if r.random() < 0.55 - 0.5 * north else INK[5]
                    hexes.append(f'<polygon points="{pts}" fill="{col}"/>')
            x += dx
        y += dy
        row += 1
    tx, ty = P(129.2, -20.1)
    out = ["".join(hexes),
           f'<g class="cold" fill="{BLUE[8]}">{"".join(cold)}</g>',
           f'<line x1="{f(tx - 4)}" y1="{f(ty)}" x2="300" y2="{f(ty)}" stroke="{INK[8]}"/>',
           f'<text x="294" y="{f(ty - 6)}" text-anchor="end" class="lbl2">Tanami: 0.6% protected</text>',
           f'<text x="294" y="{f(ty + 10)}" text-anchor="end" class="lbl">a significant cold spot</text>',
           f'<rect x="22" y="24" width="10" height="10" rx="2" fill="{GREEN[7]}"/><text x="37" y="33" class="lbl">Protected land</text>',
           f'<rect x="135" y="24" width="10" height="10" rx="2" fill="{INK[5]}"/><text x="150" y="33" class="lbl">Not protected</text>']
    return "\n".join(out), css


def viz_rainsignal():
    r = rng(12)
    css = """
.rain{animation:rain 1.6s linear infinite}
@keyframes rain{from{transform:translate(0,-60px)}to{transform:translate(-14px,60px)}}
"""
    drops = "".join(f'<line x1="{f(x)}" y1="{f(y)}" x2="{f(x - 3)}" y2="{f(y + 9)}"/>'
                    for x, y in ((r.uniform(0, 600), r.uniform(0, 176)) for _ in range(45)))
    out = [f'<g class="rain" stroke="{BLUE[9]}" stroke-width="1" opacity=".18">{drops}</g>']
    bars = []
    n, x0, span = 49, 22, 516
    w = span / n
    for i in range(n):
        p, obs = r.random() ** 1.3, r.random() ** 3
        x = x0 + i * w
        h = 8 + p * 64
        bars.append(f'<rect x="{f(x + 1)}" y="{f(158 - h)}" width="{f(w - 3)}" height="{f(h)}" fill="none" stroke="{TEAL[7]}" stroke-width="1"/>')
        if obs > 0.05:
            oh = 3 + obs * 40
            bars.append(f'<rect x="{f(x + 2.5)}" y="{f(158 - oh)}" width="{f(w - 6)}" height="{f(oh)}" fill="{BLUE[8]}"/>')
    out.append("".join(bars))
    out.append(f'<line x1="22" y1="158.5" x2="538" y2="158.5" stroke="{INK[6]}"/>')
    out.append(f'<text x="22" y="172" class="lbl">49 towns</text>')
    out.append(f'<rect x="22" y="24" width="10" height="10" fill="{BLUE[8]}"/><text x="37" y="33" class="lbl">Observed by BoM</text>')
    out.append(f'<rect x="150.5" y="24.5" width="9" height="9" fill="none" stroke="{TEAL[7]}"/><text x="165" y="33" class="lbl">Model estimate, kept separate</text>')
    return "\n".join(out), css


def viz_roadstate():
    cyc = 14
    months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    x0, span, split, ry = 22, 516, 236, 96
    css = f"""
.city{{animation:city 2.4s linear infinite}}
@keyframes city{{from{{transform:translateX(-26px)}}to{{transform:translateX(0)}}}}
.far{{animation:far {cyc}s linear infinite}}
@keyframes far{{from{{transform:translateX(0)}}to{{transform:translateX(312px)}}}}
.dry{{animation:dry {cyc}s ease-in-out infinite}}
@keyframes dry{{0%,34%,84%,100%{{opacity:1}}38%,80%{{opacity:0}}}}
.wet{{opacity:0;animation:wet {cyc}s ease-in-out infinite}}
@keyframes wet{{0%,33%,84%,100%{{opacity:0}}38%,80%{{opacity:1}}}}
.scrub{{animation:scrub {cyc}s linear infinite}}
@keyframes scrub{{from{{transform:translateX(0)}}to{{transform:translateX({span}px)}}}}
"""
    out = [f'<clipPath id="cityc"><rect x="{x0}" y="{ry - 12}" width="{split - x0}" height="24"/></clipPath>',
           f'<clipPath id="farc"><rect x="{split}" y="{ry - 12}" width="{x0 + span - split}" height="24"/></clipPath>',
           f'<rect x="{x0}" y="{ry - 10}" width="{span}" height="20" rx="3" fill="{INK[3]}"/>',
           f'<line x1="{split + .5}" y1="{ry - 18}" x2="{split + .5}" y2="{ry + 14}" stroke="{INK[7]}"/>',
           f'<text x="{x0}" y="{ry - 22}" class="lbl2">Darwin, 78% of traffic</text>',
           f'<text x="{split + 8}" y="{ry - 22}" class="lbl">Remote roads</text>']
    cars = "".join(f'<rect x="{x0 - 26 + k * 26}" y="{ry - 6 + (k % 2) * 7}" width="13" height="5" rx="1.5" fill="#fde9b8"/>' for k in range(10))
    out.append(f'<g clip-path="url(#cityc)"><g class="city">{cars}</g></g>')
    far = "".join(f'<rect x="{split - 20 + k * 156}" y="{ry - 6 + (k % 2) * 7}" width="13" height="5" rx="1.5" fill="#fde9b8"/>' for k in range(-1, 2))
    out.append(f'<g clip-path="url(#farc)"><g class="dry"><g class="far">{far}</g></g></g>')
    bars = "".join(f'<rect x="{bx - 12}" y="{ry - 5}" width="24" height="10" rx="1.5" fill="{RED}"/>' for bx in (318, 432, 512))
    out.append(f'<g class="wet">{bars}<text x="538" y="{ry + 30}" text-anchor="end" class="lbl2">Closed in the wet</text></g>')
    my = 150
    cw = span / 12
    for i, m in enumerate(months):
        wet = 4 <= i <= 9
        out.append(f'<rect x="{f(x0 + i * cw + 1)}" y="{my - 10}" width="{f(cw - 2)}" height="3" rx="1.5" fill="{BLUE[8] if wet else INK[5]}"/>'
                   f'<text x="{f(x0 + (i + 0.5) * cw)}" y="{my + 6}" text-anchor="middle" class="lbl">{m}</text>')
    out.append(f'<g class="scrub"><line x1="{x0}" y1="{my - 15}" x2="{x0}" y2="{my - 4}" stroke="#fff" stroke-opacity=".7" stroke-width="1.5"/></g>')
    out.append(f'<text x="22" y="32" class="lbl">One year on NT roads</text>')
    return "\n".join(out), css


PROJECTS = [
    ("underlink", viz_underlink, dict(
        title="Underlink",
        lines=["18 of 23 remote places that reach fibre by radio rely",
               "on a relay with no other licensed path."],
        tools="Python, graph analysis, Panel. Built for the CDU Code Fair 2026.",
        desc="A radio relay chain from fibre to a remote community. When a single-path relay fails, "
             "the community loses signal. 18 of 23 radio-chain places depend on such a relay.")),
    ("pyrantis", viz_pyrantis, dict(
        title="PYRANTIS",
        lines=["Classifies 25 years of Territory fire seasons by 5 km",
               "cell. Gradient boosting scores 0.684 macro-F1 on 2023–25."],
        tools="Python, gradient boosting, LSTM. Data from NAFI, SILO and MODIS.",
        desc="A grid of 5 km cells through a fire year: early fires before 31 July in amber, "
             "late fires after it in orange.")),
    ("conflux", viz_conflux, dict(
        title="Conflux",
        lines=["Two anomaly detectors read the same air and sea data",
               "every three hours, and still disagree."],
        tools="scikit-learn, PyTorch, Next.js, Cloudflare Workers.",
        desc="Air and sea signal traces scroll past, each flagging anomalies at different moments.")),
    ("terraiq", viz_terraiq, dict(
        title="TerraIQ",
        lines=["Keeps the readings from 44 BOM stations that the",
               "public feed drops after 72 hours."],
        tools="Python, SQLite, GitHub Actions, MapLibre GL.",
        desc="Rainfall readings scroll left. The public feed loses them after 72 hours; TerraIQ keeps them all.")),
    ("avian-observatory", viz_avian, dict(
        title="Avian Observatory",
        lines=["BirdNET calls Territory birds a North American thrush.",
               "A regional model reaches 0.88 on unseen recordings."],
        tools="Python, TensorFlow, BirdNET, FastAPI, Next.js.",
        desc="A scrolling spectrogram of bird calls. BirdNET's label, Bicknell's Thrush, is struck out; "
             "the regional model's label is correct.")),
    ("bushmetrics", viz_bushmetrics, dict(
        title="BushMetrics",
        lines=["NT parks favour the rugged north. The Tanami, the",
               "largest bioregion, is only 0.6% protected."],
        tools="GeoPandas, hot-spot statistics, FastAPI, React, Leaflet.",
        desc="A hexagon map of the Northern Territory. Protected land clusters in the north; "
             "the Tanami is a significant cold spot at 0.6% protection.")),
    ("rainsignal", viz_rainsignal, dict(
        title="RainSignal AU",
        lines=["Runs live Bureau of Meteorology observations through",
               "frozen, evaluated rainfall models for 49 towns."],
        tools="Python, scikit-learn, BoM feeds, Cloudflare Pages.",
        desc="Rain over 49 town gauges. Observed rainfall is drawn solid and model estimates as outlines, never mixed.")),
    ("roadstate", viz_roadstate, dict(
        title="RoadState",
        lines=["78% of NT traffic is in Darwin, and 66% of closures",
               "start in the wet. Access is the problem, not congestion."],
        tools="Next.js, TypeScript, Visx, Python. Open NT Government data.",
        desc="A year on NT roads: Darwin traffic keeps moving while remote roads close through the wet season.")),
]


def build_cards():
    for slug, viz_fn, meta in PROJECTS:
        viz, css = viz_fn()
        card(slug, viz=viz, viz_css=css, **meta)


if __name__ == "__main__":
    write("hero.svg", build_hero())
    build_cards()
