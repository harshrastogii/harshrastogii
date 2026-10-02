"""Builds the hand-made animated SVGs in ../assets.

    python scripts/build_assets.py

Deterministic: the same code always writes the same files. The data-driven
contribution seismograph is built separately by render_pulse.py.
"""

import math
import os

from svgkit import (AMBER, BLUE, EMBER, GREEN, INK, MONO, RED, SANS, TEAL, chip, document,
                    esc, f, mono_width, periodic_noise, rng, smooth_path)
import nt_geo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")


def write(name, svg):
    path = os.path.join(ASSETS, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote assets/{name} ({len(svg) / 1024:.1f} KB)")


# ---------------------------------------------------------------------------
# Hero: the Territory at night
# ---------------------------------------------------------------------------

def typing_ticker(phrases, x, y, size, cycle, prefix_id):
    """Mono phrases that type, hold and erase in turn (SMIL, discrete steps)."""
    cw = size * 0.6
    slot = cycle / len(phrases)
    out = []
    for i, text in enumerate(phrases):
        n = len(text)
        start, type_end = i * slot, i * slot + slot * 0.38
        hold_end, erase_end = i * slot + slot * 0.86, i * slot + slot * 0.96
        times, widths = [0.0], [0.0]
        for k in range(n + 1):
            times.append(start + (type_end - start) * k / n)
            widths.append(k * cw)
        times.append(hold_end)
        widths.append(n * cw)
        steps = 8
        for k in range(1, steps + 1):
            times.append(hold_end + (erase_end - hold_end) * k / steps)
            widths.append(n * cw * (1 - k / steps))
        times.append(cycle)
        widths.append(0.0)
        # keyTimes must be strictly non-decreasing within [0, 1]
        kt = ";".join(f"{t / cycle:.4f}" for t in times)
        wv = ";".join(f(w) for w in widths)
        xv = ";".join(f(x + w) for w in widths)
        cid = f"{prefix_id}{i}"
        out.append(
            f'<clipPath id="{cid}"><rect x="{x}" y="{y - size}" width="0" height="{size * 1.5}">'
            f'<animate attributeName="width" dur="{cycle}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{kt}" values="{wv}"/></rect></clipPath>'
            f'<text clip-path="url(#{cid})" x="{x}" y="{y}" class="tick">{esc(text)}</text>'
            f'<rect x="{x}" y="{y - size * 0.82}" width="{f(cw * 0.9)}" height="{f(size * 1.02)}" '
            f'fill="{TEAL[8]}" opacity="0">'
            f'<animate attributeName="x" dur="{cycle}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{kt}" values="{xv}"/>'
            f'<animate attributeName="opacity" dur="{cycle}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="0;{start / cycle:.4f};{erase_end / cycle:.4f}" '
            f'values="0;0.85;0"/></rect>'
        )
    return "".join(out)


def build_hero():
    W, H = 1200, 460
    K, X0, Y0, LON0, LAT0 = 26.5, 852, 22, 128.8, -10.9

    def P(lon, lat):
        return (X0 + (lon - LON0) * K, Y0 + (LAT0 - lat) * K)

    r = rng(11)
    css = f"""
.tw{{animation:tw 5s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
.outline{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 3.2s cubic-bezier(.6,0,.2,1) .2s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.fill{{opacity:0;animation:fade 2s ease 2.2s forwards}}
@keyframes fade{{to{{opacity:1}}}}
.light{{animation:glow 4s ease-in-out infinite}}
@keyframes glow{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
.ripple{{transform-box:fill-box;transform-origin:center;animation:ripple 6s cubic-bezier(.2,.6,.3,1) infinite;opacity:0}}
@keyframes ripple{{0%{{transform:scale(.1);opacity:.75}}100%{{transform:scale(1);opacity:0}}}}
.sweep{{animation:sweep 9s linear infinite}}
@keyframes sweep{{0%{{transform:translateY(-40px)}}100%{{transform:translateY({H}px)}}}}
.links{{opacity:0;animation:fade 1.6s ease 2.6s forwards}}
.name{{font:800 74px {SANS};letter-spacing:-.02em}}
.kicker{{font:500 15px {MONO};fill:{TEAL[8]};letter-spacing:.22em}}
.lead{{font:600 29px {SANS};fill:{INK[12]};letter-spacing:-.01em}}
.tick{{font:500 19px {MONO};fill:{INK[11]}}}
.tag{{font:500 12px {MONO};fill:{INK[10]};letter-spacing:.14em}}
.lbl{{font:500 10.5px {MONO};fill:{INK[10]};letter-spacing:.08em}}
.reveal{{animation:reveal 1.4s cubic-bezier(.7,0,.2,1) .3s both}}
@keyframes reveal{{from{{transform:translateX(-620px)}}to{{transform:translateX(0)}}}}
.rise{{animation:rise 1s ease both}}
@keyframes rise{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
.live{{animation:live 1.6s ease-in-out infinite}}
@keyframes live{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
"""
    defs = f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#0b1418"/><stop offset=".6" stop-color="{INK[1]}"/><stop offset="1" stop-color="#0c0d0e"/>
</linearGradient>
<radialGradient id="halo" cx="0.81" cy="0.45" r="0.42">
 <stop offset="0" stop-color="{TEAL[5]}" stop-opacity=".28"/><stop offset="1" stop-color="{TEAL[5]}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="lamp"><stop offset="0" stop-color="#fff7d6"/><stop offset=".25" stop-color="{AMBER}" stop-opacity=".9"/>
 <stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
<radialGradient id="lampT"><stop offset="0" stop-color="#ecfeff"/><stop offset=".3" stop-color="{TEAL[8]}" stop-opacity=".8"/>
 <stop offset="1" stop-color="{TEAL[8]}" stop-opacity="0"/></radialGradient>
<linearGradient id="nameg" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="{INK[12]}"/><stop offset=".55" stop-color="{TEAL[9]}"/><stop offset="1" stop-color="{GREEN[9]}"/>
</linearGradient>
<linearGradient id="sweepg" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="{TEAL[8]}" stop-opacity="0"/><stop offset="1" stop-color="{TEAL[8]}" stop-opacity=".16"/>
</linearGradient>
<linearGradient id="landg" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="{TEAL[3]}" stop-opacity=".55"/><stop offset="1" stop-color="{TEAL[3]}" stop-opacity=".18"/>
</linearGradient>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
<clipPath id="namec"><rect x="56" y="100" width="760" height="100"/></clipPath>
</defs>"""

    body = [defs, f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
            f'<rect width="{W}" height="{H}" fill="url(#halo)"/>']

    # star field, kept off the text column's busiest area
    stars = []
    for _ in range(120):
        x, y = r.uniform(0, W), r.uniform(0, H)
        rad = r.choice([0.6, 0.8, 0.8, 1.1, 1.4])
        cls = ' class="tw"' if r.random() < 0.45 else ""
        dl = f' style="animation-delay:-{r.uniform(0, 5):.2f}s"' if cls else ""
        stars.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{rad}" fill="{INK[11]}" opacity=".35"{cls}{dl}/>')
    body.append("<g>" + "".join(stars) + "</g>")

    # graticule around the map
    grat = []
    for lon in range(130, 139, 2):
        x, _ = P(lon, 0)
        grat.append(f'<line x1="{f(x)}" y1="14" x2="{f(x)}" y2="{H - 14}"/>')
        grat.append(f'<text x="{f(x)}" y="{H - 8}" text-anchor="middle" class="lbl" stroke="none">{lon}°E</text>')
    for lat in range(-12, -27, -4):
        _, y = P(0, lat)
        grat.append(f'<line x1="{X0 - 40}" y1="{f(y)}" x2="{W - 30}" y2="{f(y)}"/>')
        grat.append(f'<text x="{W - 26}" y="{f(y + 3.5)}" class="lbl" stroke="none">{-lat}°S</text>')
    body.append(f'<g stroke="{INK[5]}" stroke-width=".6" stroke-dasharray="2 5" opacity=".7">{"".join(grat)}</g>')

    # the Territory
    coast = [P(*p) for p in nt_geo.COAST]
    border = [P(*p) for p in nt_geo.BORDER]
    d = smooth_path(coast) + "".join(f"L{f(x)},{f(y)}" for x, y in border) + "Z"
    islands = "".join(smooth_path([P(*p) for p in isl], closed=True) for isl in nt_geo.ISLANDS)
    body.append(f'<path class="fill" d="{d}{islands}" fill="url(#landg)"/>')
    body.append(f'<path d="{d}{islands}" fill="none" stroke="{TEAL[7]}" stroke-width="5" opacity=".25" filter="url(#soft)" class="fill"/>')
    body.append(f'<path class="outline" pathLength="1" d="{d}" fill="none" stroke="{TEAL[8]}" stroke-width="1.4" stroke-linejoin="round"/>')
    body.append(f'<path class="fill" d="{islands}" fill="none" stroke="{TEAL[8]}" stroke-width="1.2"/>')

    # scanning band
    body.append(f'<g clip-path="url(#mapclip)"><g class="sweep"><rect x="{X0 - 10}" y="0" width="{W - X0}" height="40" fill="url(#sweepg)"/><rect x="{X0 - 10}" y="39" width="{W - X0}" height="1" fill="{TEAL[8]}" opacity=".35"/></g></g>')
    body.append(f'<clipPath id="mapclip"><path d="{d}"/></clipPath>')

    # relay network: spine solid, spurs dashed, packets riding the spurs
    links = []
    spine = [P(*nt_geo.town(n)[1:3]) for n in nt_geo.BACKBONE]
    links.append(f'<path d="M{" L".join(f"{f(x)},{f(y)}" for x, y in spine)}" fill="none" stroke="{TEAL[8]}" stroke-width="1.3" opacity=".55"/>')
    packets = []
    for i, spur in enumerate(nt_geo.SPURS):
        pts = [P(*nt_geo.town(n)[1:3]) for n in spur]
        pd = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
        links.append(f'<path id="sp{i}" d="{pd}" fill="none" stroke="{TEAL[9]}" stroke-width=".9" stroke-dasharray="3 3" opacity=".45"/>')
        dur = 2.6 + len(spur) * 0.7
        packets.append(f'<circle r="2.1" fill="#ecfeff"><animateMotion dur="{dur:.1f}s" begin="{3 + r.uniform(0, 2):.2f}s" repeatCount="indefinite"><mpath href="#sp{i}"/></animateMotion></circle>')
    spine_d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in spine)
    links.append(f'<path id="spine" d="{spine_d}" fill="none"/>')
    for k in range(3):
        packets.append(f'<circle r="2.4" fill="{GREEN[9]}"><animateMotion dur="9s" begin="{3 + k * 3}s" repeatCount="indefinite"><mpath href="#spine"/></animateMotion></circle>')
    body.append(f'<g class="links">{"".join(links)}{"".join(packets)}</g>')

    # town lights
    lights = []
    for name, lon, lat, size in nt_geo.TOWNS:
        x, y = P(lon, lat)
        glow = {3: 16, 2: 11, 1: 7}[size]
        grad = "lamp" if size == 3 else "lampT"
        lights.append(
            f'<g class="light" style="animation-delay:-{r.uniform(0, 4):.2f}s">'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{glow}" fill="url(#{grad})"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{1.1 + size * 0.45:.2f}" fill="#fffbeb"/></g>')
    body.append(f'<g class="fill">{"".join(lights)}</g>')
    for name, dx, anchor in [("Darwin", -12, "end"), ("Katherine", 12, "start"),
                             ("Tennant Creek", 12, "start"), ("Alice Springs", 12, "start")]:
        _, lon, lat, _ = nt_geo.town(name)
        x, y = P(lon, lat)
        body.append(f'<text class="lbl fill" x="{f(x + dx)}" y="{f(y + 3.5)}" text-anchor="{anchor}" style="fill:{INK[11]}">{name.upper()}</text>')

    # ripples from Darwin
    dx, dy = P(130.84, -12.46)
    for k in range(3):
        body.append(f'<circle class="ripple" cx="{f(dx)}" cy="{f(dy)}" r="150" fill="none" stroke="{TEAL[8]}" stroke-width="1.2" style="animation-delay:{k * 2}s"/>')

    # text column
    body.append(f'<text x="64" y="92" class="kicker rise">DATA SCIENTIST · DARWIN, NORTHERN TERRITORY</text>')
    body.append(f'<g clip-path="url(#namec)"><g class="reveal"><text x="60" y="174" class="name" fill="url(#nameg)">Harsh Rastogi</text></g></g>')
    body.append(f'<g class="rise" style="animation-delay:1s">'
                f'<text x="64" y="232" class="lead">I turn Territory data into <tspan fill="{TEAL[8]}">decisions</tspan>,</text>'
                f'<text x="64" y="270" class="lead">not just dashboards.</text></g>')
    body.append(f'<text x="64" y="322" class="tick" style="fill:{GREEN[8]}">&gt;</text>')
    body.append(typing_ticker([
        "environmental intelligence",
        "spatial analysis & geostatistics",
        "machine learning that ships",
        "civic tech for remote communities",
        "open data → tools people use",
    ], 88, 322, 19, 20, "ty"))

    chips_y = 360
    x = 64
    for text, fg, bg, st in [
        ("MASTER OF DATA SCIENCE · CDU", INK[11], INK[2], INK[5]),
        ("GOVHACK · NT LEAD", INK[11], INK[2], INK[5]),
    ]:
        svg, w = chip(x, chips_y, text, 12, fg, bg, st, pad=12, h=28)
        body.append(f'<g class="rise" style="animation-delay:1.4s">{svg}</g>')
        x += w + 10
    aw = mono_width("AVAILABLE FOR WORK", 12) + 42
    body.append(f'<g class="rise" style="animation-delay:1.4s">'
                f'<rect x="{f(x)}" y="{chips_y}" width="{f(aw)}" height="28" rx="14" fill="#062213" stroke="{GREEN[5]}"/>'
                f'<circle class="live" cx="{f(x + 17)}" cy="{chips_y + 14}" r="4" fill="{GREEN[8]}"/>'
                f'<text x="{f(x + 30)}" y="{chips_y + 18.2}" style="font:500 12px {MONO};fill:{GREEN[9]}">AVAILABLE FOR WORK</text></g>')

    body.append(f'<text x="64" y="428" class="tag">12.4637°S  130.8444°E  ·  TWELVE SHIPPED PROJECTS ACROSS THE NT</text>')

    return document(W, H, "Harsh Rastogi — data scientist, Northern Territory",
                    "An animated night-lights map of the Northern Territory: town lights glow, "
                    "signals travel a relay network along the Stuart Highway, and the tagline reads "
                    "'I turn Territory data into decisions, not just dashboards.'",
                    css, "\n".join(body))


# ---------------------------------------------------------------------------
# Project cards: one field instrument per project
# ---------------------------------------------------------------------------

CW, CH, VH = 560, 330, 172  # card width, height, visualisation band height

CARD_CSS = f"""
.code{{font:500 11.5px {MONO};fill:{TEAL[8]};letter-spacing:.16em}}
.ttl{{font:700 27px {SANS};fill:{INK[12]};letter-spacing:-.01em}}
.txt{{font:400 15.5px {SANS};fill:{INK[10]}}}
.stk{{font:400 11.5px {MONO};fill:{INK[9]}}}
.big{{font:700 30px {SANS};fill:{INK[12]};letter-spacing:-.02em}}
.cap{{font:500 10.5px {MONO};fill:{INK[10]};letter-spacing:.06em}}
.mini{{font:500 9.5px {MONO};fill:{INK[9]};letter-spacing:.08em}}
.pill{{font:600 10px {MONO};letter-spacing:.12em}}
.blink{{animation:blink 1.6s ease-in-out infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
"""


def card(slug, *, code, title, lines, stack, stat, stat_cap, status, viz, viz_css, desc, readout_right=False):
    status_svg = ""
    if status:
        color = {"LIVE": GREEN[8], "RESEARCH": BLUE[8], "CODE FAIR": AMBER}.get(status, TEAL[8])
        w = len(status) * 7.2 + 30
        status_svg = (
            f'<g transform="translate({f(CW - 20 - w)},{VH + 16})">'
            f'<rect width="{f(w)}" height="22" rx="11" fill="{INK[1]}" stroke="{color}" stroke-opacity=".55"/>'
            f'<circle class="blink" cx="12" cy="11" r="3.5" fill="{color}"/>'
            f'<text x="22" y="15" class="pill" fill="{color}">{status}</text></g>')
    text_lines = "".join(
        f'<text x="24" y="{VH + 92 + i * 22}" class="txt">{esc(l)}</text>' for i, l in enumerate(lines))
    rw = max(len(stat_cap) * 10.5 * 0.66 + 22, 150)
    rx = CW - 16 - rw if readout_right else 16
    readout = (
        f'<g transform="translate({f(rx)},14)"><rect width="{f(rw)}" '
        f'height="58" rx="8" fill="{INK[1]}" fill-opacity=".82" stroke="{INK[4]}"/>'
        f'<text x="11" y="31" class="big">{esc(stat)}</text>'
        f'<text x="11" y="48" class="cap">{esc(stat_cap)}</text></g>')
    body = f"""<defs>
<clipPath id="band"><path d="M1,{VH} V14 a13,13 0 0 1 13,-13 H{CW - 14} a13,13 0 0 1 13,13 V{VH} Z"/></clipPath>
<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20,0 H0 V20" fill="none" stroke="{INK[3]}" stroke-width="1"/></pattern>
<linearGradient id="cardg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK[2]}"/><stop offset="1" stop-color="#141517"/></linearGradient>
</defs>
<rect x=".5" y=".5" width="{CW - 1}" height="{CH - 1}" rx="14" fill="url(#cardg)" stroke="{INK[4]}"/>
<g clip-path="url(#band)"><rect width="{CW}" height="{VH}" fill="#0c0d0e"/><rect width="{CW}" height="{VH}" fill="url(#grid)" opacity=".7"/>
{viz}
{readout}
</g>
<line x1="1" y1="{VH}" x2="{CW - 1}" y2="{VH}" stroke="{INK[4]}"/>
<text x="24" y="{VH + 32}" class="code">{esc(code)}</text>
{status_svg}
<text x="24" y="{VH + 64}" class="ttl">{esc(title)}</text>
{text_lines}
<text x="24" y="{CH - 16}" class="stk">{esc(stack)}</text>"""
    write(f"projects/{slug}.svg", document(CW, CH, title, desc, CARD_CSS + viz_css, body))


def viz_underlink():
    nodes = [(70, 128), (150, 104), (232, 132), (314, 98), (398, 130), (470, 102), (526, 128)]
    seg = " L".join(f"{x},{y}" for x, y in nodes)
    fail = 4  # index of the single-path relay
    up = " L".join(f"{x},{y}" for x, y in nodes[:fail + 1])
    down = " L".join(f"{x},{y}" for x, y in nodes[fail:])
    css = f"""
.down{{animation:down 8s ease-in-out infinite}}
@keyframes down{{0%,52%,84%,100%{{opacity:1}}58%,78%{{opacity:.18}}}}
.flt{{animation:flt 8s ease-in-out infinite}}
@keyframes flt{{0%,50%,86%,100%{{fill:{TEAL[8]};stroke:{TEAL[8]}}}54%,80%{{fill:{RED};stroke:{RED}}}}}
.ring{{transform-box:fill-box;transform-origin:center;animation:ring 8s ease-out infinite;opacity:0}}
@keyframes ring{{0%,52%{{opacity:0;transform:scale(.3)}}56%{{opacity:.9}}74%{{opacity:0;transform:scale(2.4)}}100%{{opacity:0}}}}
.warn{{animation:warn 8s ease-in-out infinite;opacity:0}}
@keyframes warn{{0%,53%,82%,100%{{opacity:0}}57%,78%{{opacity:1}}}}
.pk{{animation:pk 8s linear infinite}}
@keyframes pk{{0%,52%,82%,100%{{opacity:1}}55%,79%{{opacity:0}}}}
"""

    def tower(x, y, extra=""):
        return (f'<g transform="translate({x},{y})"{extra}><path d="M0,-14 L-7,6 M0,-14 L7,6 M-4.5,-2 H4.5" '
                f'fill="none" stroke-width="1.6" stroke-linecap="round"/><circle cy="-15" r="2.6" stroke="none"/></g>')

    out = [f'<path d="M{nodes[1][0]},{nodes[1][1]} Q{nodes[2][0]},{nodes[2][1] + 52} {nodes[3][0]},{nodes[3][1]}" fill="none" stroke="{INK[7]}" stroke-dasharray="3 4"/>',
           f'<text x="{nodes[2][0]}" y="{nodes[2][1] + 30}" text-anchor="middle" class="mini">ALT PATH</text>',
           f'<path d="M{up}" fill="none" stroke="{TEAL[7]}" stroke-width="1.6"/>',
           f'<path class="down" d="M{down}" fill="none" stroke="{TEAL[7]}" stroke-width="1.6"/>',
           f'<path id="chain" d="M{seg}" fill="none"/>']
    for i in range(1, len(nodes)):
        mx = (nodes[i - 1][0] + nodes[i][0]) / 2
        my = (nodes[i - 1][1] + nodes[i][1]) / 2 + 18
        out.append(f'<text x="{f(mx)}" y="{f(my)}" text-anchor="middle" class="mini" opacity=".7">{i}</text>')
    fx, fy = nodes[0]
    out.append(f'<rect x="{fx - 22}" y="{fy - 12}" width="44" height="24" rx="5" fill="{TEAL[3]}" stroke="{TEAL[8]}"/>'
               f'<text x="{fx}" y="{fy + 4}" text-anchor="middle" class="mini" style="fill:{TEAL[9]}">FIBRE</text>')
    for i, (x, y) in enumerate(nodes[1:-1], start=1):
        if i == fail:
            out.append(f'<circle class="ring" cx="{x}" cy="{y - 6}" r="16" fill="none" stroke="{RED}" stroke-width="1.5"/>')
            out.append(tower(x, y, ' class="flt"'))
        else:
            g = f'<g fill="{TEAL[8]}" stroke="{TEAL[8]}">' + tower(x, y) + "</g>"
            out.append(f'<g class="down">{g}</g>' if i > fail else g)
    cx, cy = nodes[-1]
    out.append(f'<g class="down"><path d="M{cx - 11},{cy + 9} V{cy - 2} L{cx},{cy - 11} L{cx + 11},{cy - 2} V{cy + 9} Z" '
               f'fill="{GREEN[3]}" stroke="{GREEN[8]}" stroke-width="1.5"/></g>')
    out.append(f'<text x="{cx}" y="{cy + 26}" text-anchor="middle" class="mini">COMMUNITY</text>')
    for k in range(3):
        out.append(f'<g class="pk"><circle r="3" fill="#ecfeff"><animateMotion dur="4s" begin="{k * 1.33:.2f}s" repeatCount="indefinite"><mpath href="#chain"/></animateMotion></circle></g>')
    wx, wy = nodes[fail]
    out.append(f'<g class="warn"><rect x="{wx - 66}" y="{wy - 52}" width="132" height="20" rx="4" fill="#2a0d0d" stroke="{RED}"/>'
               f'<text x="{wx}" y="{wy - 38}" text-anchor="middle" class="mini" style="fill:#fecaca">SINGLE-PATH RELAY</text></g>')
    out.append(f'<g class="warn"><text x="{cx}" y="{cy - 22}" text-anchor="middle" class="mini" style="fill:#fecaca">NO SIGNAL</text></g>')
    return "\n".join(out), css


def viz_pyrantis():
    r = rng(5)
    cols, rows, size, gap = 34, 5, 12, 2.5
    x0, y0 = 22, 76
    css = f"""
.u{{fill:#123222;animation:u 12s ease-in-out infinite}}
@keyframes u{{0%,70%{{fill:#1a3a23}}85%,100%{{fill:#123222}}}}
.e{{animation:e 12s linear infinite}}
@keyframes e{{0%,30%{{fill:#1a3a23}}33%{{fill:{AMBER}}}38%{{fill:#5a3d12}}88%{{fill:#4a3412}}96%,100%{{fill:#1a3a23}}}}
.l{{animation:l 12s linear infinite}}
@keyframes l{{0%,62%{{fill:#1a3a23}}65%{{fill:#fff1e6}}67%{{fill:{EMBER}}}72%{{fill:#4a1712}}96%{{fill:#3b1410}}99%,100%{{fill:#1a3a23}}}}
.scrub{{animation:scrub 12s linear infinite}}
@keyframes scrub{{from{{transform:translateX(0)}}to{{transform:translateX({cols * (size + gap) - gap}px)}}}}
"""
    out = []
    for cy in range(rows):
        for cx in range(cols):
            x, y = x0 + cx * (size + gap), y0 + cy * (size + gap)
            roll = r.random()
            north = 1 - cy / rows
            if roll < 0.14 + 0.08 * north:
                out.append(f'<rect class="e" x="{f(x)}" y="{f(y)}" width="{size}" height="{size}" rx="2" style="animation-delay:-{r.uniform(0, 2.8):.2f}s"/>')
            elif roll < 0.33 + 0.06 * (1 - north):
                out.append(f'<rect class="l" x="{f(x)}" y="{f(y)}" width="{size}" height="{size}" rx="2" style="animation-delay:-{r.uniform(0, 3.6):.2f}s"/>')
            else:
                out.append(f'<rect class="u" x="{f(x)}" y="{f(y)}" width="{size}" height="{size}" rx="2"/>')
    span = cols * (size + gap) - gap
    ty = y0 + rows * (size + gap) + 6
    months = ["APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR"]
    for i, m in enumerate(months):
        out.append(f'<text x="{f(x0 + span * (i + 0.5) / 12)}" y="{ty + 10}" text-anchor="middle" class="mini">{m}</text>')
    cut = x0 + span * 4 / 12
    out.append(f'<line x1="{f(cut)}" y1="{y0 - 8}" x2="{f(cut)}" y2="{ty + 2}" stroke="{AMBER}" stroke-dasharray="3 3" opacity=".8"/>')
    out.append(f'<text x="{f(cut + 5)}" y="{y0 - 10}" class="mini" style="fill:{AMBER}">31 JUL</text>')
    out.append(f'<g class="scrub"><line x1="{x0}" y1="{y0 - 6}" x2="{x0}" y2="{ty + 2}" stroke="#fff" stroke-opacity=".55"/></g>')
    lx = 22
    for i, (label, col) in enumerate([("UNBURNT", "#2f6a40"), ("EARLY", AMBER), ("LATE", EMBER)]):
        out.append(f'<rect x="{lx + i * 66}" y="27" width="9" height="9" rx="2" fill="{col}"/>'
                   f'<text x="{lx + 14 + i * 66}" y="35" class="mini">{label}</text>')
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
    air_spikes = [(130, 30), (395, 26)]
    sea_spikes = [(250, 24), (480, 28)]
    air = trace(periodic_noise(r, P, 6), P, 100, 12, spikes=air_spikes)
    sea = trace(periodic_noise(r, P, 6), P, 144, 9, spikes=sea_spikes)
    css = scroll_css("scr", P, 14) + f"""
.now{{animation:now 2s ease-in-out infinite}}@keyframes now{{0%,100%{{opacity:.35}}50%{{opacity:.9}}}}"""
    flags = []
    for off in (0, P):
        for sx, _ in air_spikes:
            flags.append(f'<g transform="translate({sx + off},74)"><line y1="4" y2="84" stroke="{TEAL[8]}" stroke-dasharray="2 3" opacity=".5"/>'
                         f'<path d="M0,-6 L5,0 L0,6 L-5,0 Z" fill="{TEAL[8]}"/><text x="8" y="4" class="mini" style="fill:{TEAL[9]}">AIR FLAG</text></g>')
        for sx, _ in sea_spikes:
            flags.append(f'<g transform="translate({sx + off},160)"><line y1="-4" y2="-78" stroke="{BLUE[8]}" stroke-dasharray="2 3" opacity=".5"/>'
                         f'<path d="M0,-6 L5,0 L0,6 L-5,0 Z" fill="{BLUE[8]}"/><text x="8" y="4" class="mini" style="fill:{BLUE[9]}">SEA FLAG</text></g>')
    out = [f'<g class="scr"><path d="{air}" fill="none" stroke="{TEAL[8]}" stroke-width="1.6"/>'
           f'<path d="{sea}" fill="none" stroke="{BLUE[8]}" stroke-width="1.6"/>{"".join(flags)}</g>',
           f'<defs><linearGradient id="gut" x1="0" x2="1"><stop offset=".7" stop-color="#0c0d0e"/><stop offset="1" stop-color="#0c0d0e" stop-opacity="0"/></linearGradient></defs>',
           f'<rect x="0" y="74" width="84" height="98" fill="url(#gut)"/>',
           f'<text x="16" y="104" class="mini" style="fill:{TEAL[9]}">AIR</text>',
           f'<text x="16" y="148" class="mini" style="fill:{BLUE[9]}">SEA</text>',
           f'<line class="now" x1="500" y1="20" x2="500" y2="170" stroke="#fff" stroke-width="1"/>',
           f'<text x="494" y="32" text-anchor="end" class="mini">NOW · EVERY 3 H</text>']
    return "\n".join(out), css


def viz_terraiq():
    r = rng(21)
    P, bw = 560, 7
    css = scroll_css("tape", P, 18) + f"""
.st{{animation:st 3s ease-in-out infinite}}@keyframes st{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}"""
    bars_top, bars_bot = [], []
    vals = []
    for i in range(P // (bw + 3)):
        v = r.random() ** 2.2
        if r.random() < 0.35:
            v = 0.03
        vals.append(v)
    for off in (0, P):
        for i, v in enumerate(vals):
            x = off + i * (bw + 3)
            h1, h2 = 3 + v * 28, 4 + v * 40
            bars_top.append(f'<rect x="{x}" y="{f(112 - h1)}" width="{bw}" height="{f(h1)}" rx="1.5"/>')
            bars_bot.append(f'<rect x="{x}" y="{f(160 - h2)}" width="{bw}" height="{f(h2)}" rx="1.5"/>')
    out = [f'<defs><linearGradient id="win" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
           f'<stop offset=".55" stop-color="#fff" stop-opacity="0"/><stop offset=".7" stop-color="#fff" stop-opacity="1"/></linearGradient>'
           f'<mask id="feed"><rect width="560" height="172" fill="url(#win)"/></mask></defs>',
           f'<g mask="url(#feed)"><g class="tape" fill="{BLUE[8]}">{"".join(bars_top)}</g></g>',
           f'<g class="tape" fill="{TEAL[7]}" opacity=".9">{"".join(bars_bot)}</g>',
           f'<line x1="392" y1="64" x2="392" y2="112" stroke="{AMBER}" stroke-dasharray="3 3"/>',
           f'<text x="386" y="72" text-anchor="end" class="mini" style="fill:{AMBER}">DROPPED AFTER 72 H</text>',
           f'<text x="548" y="72" text-anchor="end" class="mini" style="fill:{BLUE[9]}">BOM PUBLIC FEED</text>',
           f'<rect x="0" y="116" width="560" height="1" fill="{INK[5]}"/>',
           f'<rect x="14" y="121" width="160" height="17" rx="3" fill="#0c0d0e" opacity=".9"/>',
           f'<text x="22" y="133" class="mini" style="fill:{TEAL[9]}">TERRAIQ MEMORY · KEPT</text>']
    dots = []
    for i in range(44):
        dots.append(f'<circle class="st" cx="{f(330 + (i % 22) * 9.5)}" cy="{24 + (i // 22) * 10}" r="2.3" fill="{TEAL[8]}" style="animation-delay:-{r.uniform(0, 3):.2f}s"/>')
    out.append("".join(dots))
    out.append(f'<text x="330" y="54" class="mini">44 STATIONS REPORTING</text>')
    return "\n".join(out), css


def viz_avian():
    r = rng(3)
    P = 560
    css = scroll_css("spec", P, 16) + f"""
.ph{{animation:ph 1.4s ease-in-out infinite}}@keyframes ph{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}"""
    noise, calls = [], []
    for off in (0, P):
        for i in range(0, P, 10):
            for j in range(78, 166, 11):
                a = r.random() * 0.22 * (1 - (j - 78) / 120)
                if a > 0.05:
                    noise.append(f'<rect x="{off + i}" y="{j}" width="10" height="11" fill="{TEAL[6]}" opacity="{a:.2f}"/>')
    rc = rng(17)
    call_x = [40, 150, 270, 360, 470]
    shapes = []
    for k, cx in enumerate(call_x):
        kind = k % 3
        y = rc.uniform(96, 128)
        if kind == 0:   # descending whistle
            d = f"M{cx},{f(y)} q14,-12 30,8 t26,14"
        elif kind == 1:  # trill
            d = f"M{cx},{f(y)} " + " ".join(f"l5,{-8 if i % 2 else 8}" for i in range(10))
        else:           # rising sweep with harmonic
            d = f"M{cx},{f(y + 16)} c12,-4 24,-20 46,-26"
        shapes.append((cx, y, d, kind))
    cx3, _, _, kind3 = shapes[3]
    shapes[3] = (cx3, 104, f"M{cx3},104 " + " ".join(f"l5,{-8 if i % 2 else 8}" for i in range(10)), kind3)
    for off in (0, P):
        for cx, y, d, kind in shapes:
            calls.append(f'<path transform="translate({off},0)" d="{d}" fill="none" stroke="{GREEN[9]}" stroke-width="3" stroke-linecap="round" opacity=".95"/>')
            calls.append(f'<path transform="translate({off},-22)" d="{d}" fill="none" stroke="{GREEN[8]}" stroke-width="1.6" stroke-linecap="round" opacity=".45"/>')
        bx, by = shapes[3][0], shapes[3][1]
        calls.append(f'<g transform="translate({off},0)"><rect x="{bx - 10}" y="{f(by - 36)}" width="72" height="58" rx="3" fill="none" stroke="{GREEN[8]}" stroke-dasharray="4 3"/>'
                     f'<text x="{bx - 10}" y="{f(by + 36)}" class="mini" style="fill:#fca5a5">BICKNELL\'S THRUSH</text>'
                     f'<line x1="{bx - 12}" y1="{f(by + 32.5)}" x2="{bx + 104}" y2="{f(by + 32.5)}" stroke="#f87171" stroke-width="1.4"/>'
                     f'<text x="{bx - 10}" y="{f(by + 50)}" class="mini" style="fill:{GREEN[9]}">REGIONAL MODEL ✓</text></g>')
    out = [f'<g class="spec">{"".join(noise)}{"".join(calls)}</g>',
           f'<rect x="0" y="70" width="40" height="102" fill="#0c0d0e" opacity=".9"/>']
    for k, lab in enumerate(["8k", "4k", "2k"]):
        out.append(f'<text x="10" y="{92 + k * 32}" class="mini">{lab}</text>')
    out.append(f'<line class="ph" x1="420" y1="72" x2="420" y2="170" stroke="#fff" stroke-width="1.2"/>')
    out.append(f'<text x="548" y="34" text-anchor="end" class="mini" style="fill:{GREEN[9]}">NT AUDIO · LIVE SPECTROGRAM</text>')
    return "\n".join(out), css


def viz_bushmetrics():
    r = rng(9)
    K, X0, Y0 = 10.2, 396, 6

    def P(lon, lat):
        return X0 + (lon - 128.8) * K, Y0 + (-10.9 - lat) * K
    css = f"""
.hx{{animation:hx 6s ease-in-out infinite}}
@keyframes hx{{0%,100%{{opacity:.75}}8%{{opacity:1}}}}
.cold{{animation:cold 2.4s ease-in-out infinite}}
@keyframes cold{{0%,100%{{opacity:.6}}50%{{opacity:1}}}}
.scan{{animation:scan 6s linear infinite}}
@keyframes scan{{from{{transform:translateY(0)}}to{{transform:translateY(160px)}}}}
"""
    s = 3.3
    hexes = []
    dx, dy = s * math.sqrt(3) + 0.9, s * 1.5 + 0.8
    row = 0
    y = Y0 + 2
    while y < Y0 + 15.2 * K:
        x = X0 + (dx / 2 if row % 2 else 0)
        while x < X0 + 9.3 * K:
            lon, lat = 128.8 + (x - X0) / K, -10.9 - (y - Y0) / K
            if nt_geo.inside(lon, lat):
                tanami = 129.2 <= lon <= 132.3 and -21.8 <= lat <= -18.4
                north = (-lat - 11) / 15
                if tanami:
                    col, cls = BLUE[8], "cold"
                elif r.random() < 0.55 - 0.5 * north:
                    col, cls = GREEN[8], "hx"
                else:
                    col, cls = INK[6], "hx"
                pts = " ".join(f"{f(x + s * math.cos(math.radians(60 * k + 30)))},{f(y + s * math.sin(math.radians(60 * k + 30)))}" for k in range(6))
                hexes.append(f'<polygon class="{cls}" points="{pts}" fill="{col}" style="animation-delay:{(y - Y0) / 160 * 6:.2f}s"/>')
            x += dx
        y += dy
        row += 1
    tx, ty = P(130.6, -20.1)
    out = ["".join(hexes),
           f'<rect class="scan" x="{X0 - 4}" y="0" width="100" height="2" fill="{TEAL[8]}" opacity=".6"/>',
           f'<line x1="{f(tx - 8)}" y1="{f(ty)}" x2="300" y2="{f(ty)}" stroke="{BLUE[8]}" stroke-dasharray="2 3"/>',
           f'<text x="294" y="{f(ty - 6)}" text-anchor="end" class="mini" style="fill:{BLUE[9]}">TANAMI · COLD SPOT</text>',
           f'<text x="294" y="{f(ty + 8)}" text-anchor="end" class="mini">~538,000 KM² BIOREGION</text>',
           f'<rect x="20" y="124" width="9" height="9" rx="2" fill="{GREEN[8]}"/><text x="35" y="132" class="mini">PROTECTED LAND</text>',
           f'<rect x="20" y="141" width="9" height="9" rx="2" fill="{BLUE[8]}"/><text x="35" y="149" class="mini">SIGNIFICANT COLD SPOT</text>',
           f'<rect x="20" y="158" width="9" height="9" rx="2" fill="{INK[6]}"/><text x="35" y="166" class="mini">UNPROTECTED</text>']
    return "\n".join(out), css


def viz_rainsignal():
    r = rng(12)
    css = f"""
.rain{{animation:rain .9s linear infinite}}
@keyframes rain{{from{{transform:translate(0,-60px)}}to{{transform:translate(-18px,60px)}}}}
.br{{transform-box:fill-box;transform-origin:50% 100%;animation:br 5s ease-in-out infinite}}
@keyframes br{{0%,100%{{transform:scaleY(.55)}}50%{{transform:scaleY(1)}}}}
"""
    drops = []
    for _ in range(70):
        x, y = r.uniform(0, 600), r.uniform(0, 172)
        drops.append(f'<line x1="{f(x)}" y1="{f(y)}" x2="{f(x - 4)}" y2="{f(y + 12)}"/>')
    out = [f'<g class="rain" stroke="{BLUE[9]}" stroke-width="1" opacity=".28">{"".join(drops)}</g>',
           f'<g class="rain" stroke="{BLUE[9]}" stroke-width="1" opacity=".28" style="animation-delay:-.45s">{"".join(drops)}</g>']
    bars = []
    n, x0, span = 49, 20, 520
    w = span / n
    for i in range(n):
        p = r.random() ** 1.3
        obs = r.random() ** 3
        x = x0 + i * w
        h = 10 + p * 62
        bars.append(f'<rect class="br" x="{f(x + 1)}" y="{f(160 - h)}" width="{f(w - 3.5)}" height="{f(h)}" fill="none" '
                    f'stroke="{TEAL[8]}" stroke-dasharray="2 2" style="animation-delay:-{r.uniform(0, 5):.2f}s"/>')
        if obs > 0.05:
            oh = 4 + obs * 40
            bars.append(f'<rect x="{f(x + 2.5)}" y="{f(160 - oh)}" width="{f(w - 6.5)}" height="{f(oh)}" fill="{BLUE[8]}"/>')
    out.append("".join(bars))
    out.append(f'<line x1="20" y1="160.5" x2="540" y2="160.5" stroke="{INK[6]}"/>')
    out.append(f'<rect x="352" y="22" width="12" height="9" fill="{BLUE[8]}"/><text x="370" y="30" class="mini">OBSERVED · BOM</text>')
    out.append(f'<rect x="352" y="40" width="12" height="9" fill="none" stroke="{TEAL[8]}" stroke-dasharray="2 2"/><text x="370" y="48" class="mini">MODEL ESTIMATE</text>')
    return "\n".join(out), css


def viz_fairfix():
    r = rng(4)
    lanes = [("URGENT", RED, 92), ("HIGH", AMBER, 122), ("ROUTINE", TEAL[8], 152)]
    css = """
.sh{animation:sh 9s cubic-bezier(.6,0,.3,1) infinite}
.try{animation:try 9s cubic-bezier(.5,0,.3,1) infinite}
@keyframes try{0%,58%,82%,100%{transform:translateY(0)}66%{transform:translateY(-13px)}70%{transform:translateY(-9px)}74%{transform:translateY(0)}}
.bar{animation:bar 9s ease infinite}
@keyframes bar{0%,62%,80%,100%{stroke-opacity:.35}66%,72%{stroke-opacity:1;stroke:#ef4444}}
.lock{animation:lock 9s ease infinite;opacity:0}
@keyframes lock{0%,62%,82%,100%{opacity:0}66%,78%{opacity:1}}
"""
    out = []
    xs = [100, 172, 244, 316, 388, 460]
    kf = []
    for li, (name, col, y) in enumerate(lanes):
        out.append(f'<text x="22" y="{y + 4}" class="mini" style="fill:{col}">{name}</text>')
        if li:
            out.append(f'<line class="bar" x1="100" y1="{y - 15}" x2="546" y2="{y - 15}" stroke="{INK[9]}" stroke-dasharray="5 4"/>')
        p1, p2 = list(range(6)), list(range(6))
        r.shuffle(p1)
        r.shuffle(p2)
        for j in range(5):
            a = xs[p1.index(j)] - xs[j]
            b = xs[p2.index(j)] - xs[j]
            name_k = f"m{li}{j}"
            kf.append(f"@keyframes {name_k}{{0%,20%,100%{{transform:translateX(0)}}25%,50%{{transform:translateX({a}px)}}55%,93%{{transform:translateX({b}px)}}}}")
            label = f"J-{r.randint(10, 99)}"
            cost = r.choice(["$", "$$", "$$$"])
            inner = (f'<rect x="{xs[j]}" y="{y - 9}" width="68" height="18" rx="9" fill="{INK[1]}" stroke="{col}" stroke-opacity=".8"/>'
                     f'<text x="{xs[j] + 9}" y="{y + 3.5}" class="mini" style="fill:{INK[11]}">{label}</text>'
                     f'<text x="{xs[j] + 60}" y="{y + 3.5}" text-anchor="end" class="mini" style="fill:{INK[8]}">{cost}</text>')
            anim = f"animation:{name_k} 9s cubic-bezier(.6,0,.3,1) infinite"
            if li == 2 and j == 0:
                out.append(f'<g style="{anim}"><g class="try">{inner}</g></g>')
            else:
                out.append(f'<g style="{anim}">{inner}</g>')
    out.append(f'<g class="lock"><rect x="296" y="20" width="246" height="22" rx="4" fill="#2a0d0d" stroke="{RED}"/>'
               f'<text x="419" y="35" text-anchor="middle" class="mini" style="fill:#fecaca">BLOCKED · CAN\'T CROSS A NEED BAND</text></g>')
    out.append(f'<text x="542" y="62" text-anchor="end" class="mini">$ = COST TO SERVE · NEVER MERGED WITH NEED</text>')
    return "\n".join(out), css + "".join(kf)


def build_cards():
    projects = [
        ("underlink", viz_underlink, dict(
            code="CONNECTIVITY · CDU CODE FAIR 2026", title="Underlink", status="LIVE",
            lines=["Finds the radio relays remote NT communities can't",
                   "route around, from the public ACMA licence register."],
            stack="Python · graph analysis · Panel · vanilla JS",
            stat="18 / 23", stat_cap="RADIO-CHAIN PLACES ON A SINGLE PATH",
            desc="Underlink: a relay chain from fibre to a remote community; one single-path relay fails and the community loses signal. 18 of 23 radio-chain places depend on such a relay.")),
        ("pyrantis", viz_pyrantis, dict(
            code="FIRE ECOLOGY · MACHINE LEARNING", title="PYRANTIS", status="LIVE",
            lines=["Classifies every 5 km cell of the Territory as unburnt,",
                   "early- or late-season fire (2000–2025), then forecasts 2026."],
            stack="Python · gradient boosting · LSTM · NAFI · SILO · MODIS",
            stat="0.684", stat_cap="MACRO-F1 · HELD-OUT 2023–25",
            desc="PYRANTIS: a grid of 5 km cells burning through the dry season, early fires in amber before 31 July and late fires in red after it. Macro-F1 0.684 on held-out years.")),
        ("conflux", viz_conflux, dict(
            code="ANOMALY DETECTION · SERVERLESS", title="Conflux", status="LIVE",
            lines=["Air and sea, compared directly every three hours — two",
                   "detectors that shared their inputs and still disagreed."],
            stack="scikit-learn · PyTorch · Next.js · Cloudflare Workers",
            stat="~8,000", stat_cap="ANOMALY SCORES PER RUN",
            desc="Conflux: two scrolling signal traces, air and sea, each flagging anomalies at different moments.")),
        ("terraiq", viz_terraiq, dict(
            code="CLIMATE · TIME SERIES", title="TerraIQ", status="LIVE",
            lines=["A Territory-wide weather memory built from 44 BOM",
                   "stations, holding what the public feed drops after 72 h."],
            stack="Python · SQLite · GitHub Actions · MapLibre GL",
            stat="44", stat_cap="BOM STATIONS · NOTHING DROPPED",
            desc="TerraIQ: the public weather feed forgets observations after 72 hours while the TerraIQ memory tape keeps them all.")),
        ("avian-observatory", viz_avian, dict(
            code="BIOACOUSTICS · RESEARCH", title="Avian Observatory", status="LIVE",
            lines=["On Territory audio, BirdNET confidently answers a North",
                   "American thrush. A regional model gets it right."],
            stack="Python · FastAPI · Next.js · TensorFlow · BirdNET",
            stat="0.88", stat_cap="ACCURACY ON UNSEEN RECORDINGS",
            desc="Avian Observatory: a scrolling bird-call spectrogram where the generic model's 'Bicknell's Thrush' is struck out and the regional model's detection is confirmed.")),
        ("bushmetrics", viz_bushmetrics, dict(
            code="CONSERVATION · SPATIAL STATISTICS", title="BushMetrics", status="LIVE",
            lines=["Do NT parks protect a fair cross-section of the land?",
                   "They favour the rugged north and skip the arid interior."],
            stack="GeoPandas · hot-spot analysis · FastAPI · React · Leaflet",
            stat="0.6%", stat_cap="OF THE TANAMI IS PROTECTED",
            desc="BushMetrics: a hexagon map of the Northern Territory with protected land in the north and the Tanami pulsing as a statistically significant cold spot at 0.6% coverage.")),
        ("rainsignal", viz_rainsignal, dict(
            code="FORECASTING · LIVE DATA", title="RainSignal AU", status="LIVE",
            lines=["Live Bureau of Meteorology observations run through",
                   "frozen, evaluated rainfall models for 49 towns."],
            stack="Python · scikit-learn · BoM feeds · Cloudflare Pages",
            stat="49", stat_cap="TOWNS · OBSERVED ≠ ESTIMATED",
            desc="RainSignal AU: rain falls over 49 town gauges; observed rainfall is drawn solid and model estimates dashed, never conflated.")),
        ("fairfix", viz_fairfix, dict(
            code="RESPONSIBLE AI · CDU CODE FAIR 2026", title="FairFix NT", status="CODE FAIR",
            lines=["Explainable triage for remote housing repairs: logistics",
                   "may reorder jobs within a need band, never across one."],
            stack="Python · Streamlit · fairness test suite · 200 tests",
            stat="2 scores", stat_cap="NEED AND COST, NEVER MERGED",
            desc="FairFix NT: repair jobs shuffle within urgent, high and routine need bands; a job that tries to cross a band is blocked.")),
    ]
    for slug, viz_fn, meta in projects:
        viz, css = viz_fn()
        card(slug, viz=viz, viz_css=css, readout_right=(slug == "pyrantis"), **meta)


# ---------------------------------------------------------------------------
# Toolkit as geological strata, with a drill core passing through
# ---------------------------------------------------------------------------

def build_strata():
    W, H = 1200, 380
    layers = [
        ("SHIP", "the tool people actually open", TEAL[8],
         ["Next.js", "React", "TypeScript", "FastAPI", "Streamlit", "Panel", "Cloudflare Workers", "Vercel"]),
        ("MAP", "where it happens matters", GREEN[8],
         ["GeoPandas", "MapLibre GL", "Leaflet", "Earth Engine", "hot-spot stats", "equal-area projections"]),
        ("MODEL", "and say what it can't tell you", BLUE[8],
         ["scikit-learn", "gradient boosting", "PyTorch", "TensorFlow", "LSTM", "BirdNET", "fairness tests"]),
        ("DATA", "start with the question", AMBER,
         ["Python", "SQL", "PostgreSQL", "SQLite", "pandas", "Jupyter", "Plotly", "Power BI"]),
        ("AUTOMATE", "keeps running without me", "#c084fc",
         ["GitHub Actions", "scheduled pipelines", "pytest", "Docker", "reproducible research"]),
    ]
    top, lh = 40, 64
    r = rng(2)
    drill_x = 1120
    dur = 10
    css = f"""
.nm{{font:700 16px {MONO};letter-spacing:.2em}}
.sub{{font:400 14px {SANS};fill:{INK[10]};font-style:italic}}
.drill{{animation:drill {dur}s cubic-bezier(.45,0,.55,1) infinite}}
@keyframes drill{{0%{{transform:translateY(0)}}88%{{transform:translateY({len(layers) * lh}px)}}100%{{transform:translateY(0)}}}}
.core{{transform-box:fill-box;transform-origin:top;animation:core {dur}s cubic-bezier(.45,0,.55,1) infinite}}
@keyframes core{{0%{{transform:scaleY(0)}}88%{{transform:scaleY(1)}}100%{{transform:scaleY(0)}}}}
.hd{{font:500 12px {MONO};fill:{INK[10]};letter-spacing:.2em}}
"""
    body = [f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
            f'<rect width="{W}" height="{H}" rx="16" fill="{INK[1]}"/><g clip-path="url(#frame)">',
            f'<text x="40" y="26" class="hd">CORE SAMPLE · THE STACK, SURFACE TO BEDROCK</text>']
    prev = [(x, top) for x in range(0, W + 1, 40)]
    fill_tops = []
    for i, (name, sub, col, tools) in enumerate(layers):
        yb = top + (i + 1) * lh
        noise = periodic_noise(r, W, 4)
        if i < len(layers) - 1:
            bottom = [(x, yb + noise(x) * 7) for x in range(0, W + 1, 40)]
        else:
            bottom = [(x, yb) for x in range(0, W + 1, 40)]
        path = smooth_path(prev) + smooth_path(list(reversed(bottom))).replace("M", "L", 1) + "Z"
        delay = (i + 0.5) / len(layers) * 0.88 * dur
        kf = (f"@keyframes lyr{i}{{0%,{max(0, (delay - 0.6) / dur * 100):.1f}%{{opacity:.55}}"
              f"{delay / dur * 100:.1f}%,{min(99, (delay + 1.6) / dur * 100):.1f}%{{opacity:1}}100%{{opacity:.55}}}}")
        css += kf
        fill_tops.append(
            f'<g style="animation:lyr{i} {dur}s ease-in-out infinite">'
            f'<path d="{path}" fill="{col}" fill-opacity="{0.05 + 0.025 * i:.3f}"/>'
            f'<path d="{smooth_path(bottom)}" fill="none" stroke="{col}" stroke-opacity=".35"/>'
            f'<text x="40" y="{top + i * lh + 30}" class="nm" fill="{col}">{name}</text>'
            f'<text x="40" y="{top + i * lh + 49}" class="sub">{esc(sub)}</text>')
        x = 250
        for t in tools:
            svg, w = chip(x, top + i * lh + 19, t, 14, INK[12], INK[2], col, pad=11, h=28)
            fill_tops.append(svg)
            x += w + 9
        fill_tops.append("</g>")
        prev = bottom
    body.extend(fill_tops)
    body.append(f'<rect class="core" x="{drill_x - 5}" y="{top}" width="10" height="{len(layers) * lh}" fill="{INK[11]}" opacity=".18"/>')
    body.append(f'<g class="drill"><line x1="{drill_x}" y1="-400" x2="{drill_x}" y2="{top - 6}" stroke="{INK[8]}" stroke-width="2"/>'
                f'<path d="M{drill_x - 8},{top - 6} L{drill_x + 8},{top - 6} L{drill_x},{top + 10} Z" fill="{TEAL[8]}"/>'
                f'<circle cx="{drill_x}" cy="{top + 2}" r="14" fill="{TEAL[8]}" opacity=".18"/></g></g>')
    return document(W, H, "Toolkit, as a core sample",
                    "The stack drawn as geological strata, surface to bedrock: SHIP (Next.js, React, TypeScript, FastAPI, Streamlit, Panel, Cloudflare Workers, Vercel); "
                    "MAP (GeoPandas, MapLibre GL, Leaflet, Earth Engine, hot-spot statistics); MODEL (scikit-learn, gradient boosting, PyTorch, TensorFlow, LSTM, BirdNET, fairness tests); "
                    "DATA (Python, SQL, PostgreSQL, SQLite, pandas, Jupyter, Plotly, Power BI); AUTOMATE (GitHub Actions, scheduled pipelines, pytest, Docker, reproducible research).",
                    css, "\n".join(body))


# ---------------------------------------------------------------------------
# Footer: Darwin tide line
# ---------------------------------------------------------------------------

def build_footer():
    W, H = 1200, 190
    r = rng(30)
    css = f"""
.w1{{animation:w 16s linear infinite}}.w2{{animation:w 11s linear infinite reverse}}.w3{{animation:w 7s linear infinite}}
@keyframes w{{from{{transform:translateX(0)}}to{{transform:translateX(-{W}px)}}}}
.q{{font:600 26px {SANS};fill:{INK[12]};letter-spacing:-.01em}}
.m{{font:500 12.5px {MONO};fill:{INK[10]};letter-spacing:.16em}}
.sun{{animation:sun 8s ease-in-out infinite}}@keyframes sun{{0%,100%{{opacity:.55}}50%{{opacity:.9}}}}
"""

    def wave(base, amp, k, phase):
        pts = []
        for x in range(0, 2 * W + 1, 20):
            pts.append((x, base + amp * math.sin(math.tau * k * x / W + phase)))
        return smooth_path(pts) + f"L{2 * W},{H} L0,{H} Z"

    body = [f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK[1]}"/>'
            f'<stop offset="1" stop-color="#1a1410"/></linearGradient>'
            f'<radialGradient id="sunr" cx=".5" cy="1" r=".6"><stop offset="0" stop-color="{EMBER}" stop-opacity=".55"/>'
            f'<stop offset=".5" stop-color="{AMBER}" stop-opacity=".12"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient></defs>',
            f'<rect width="{W}" height="{H}" rx="16" fill="url(#sky)"/>',
            f'<ellipse class="sun" cx="600" cy="150" rx="420" ry="120" fill="url(#sunr)"/>',
            f'<text x="600" y="62" text-anchor="middle" class="q">Got Territory data that isn\'t doing anything yet?</text>',
            f'<text x="600" y="92" text-anchor="middle" class="m">BUILT AND DEPLOYED FROM DARWIN · 12.4637°S 130.8444°E</text>',
            f'<g class="w1"><path d="{wave(140, 6, 3, 0)}" fill="{TEAL[5]}" opacity=".25"/></g>',
            f'<g class="w2"><path d="{wave(152, 5, 4, 1)}" fill="{BLUE[5]}" opacity=".3"/></g>',
            f'<g class="w3"><path d="{wave(164, 4, 5, 2)}" fill="{TEAL[3]}" opacity=".9"/></g>']
    sparkle = []
    for _ in range(26):
        x, y = r.uniform(80, 1120), r.uniform(144, 180)
        sparkle.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="1" fill="#fde68a"><animate attributeName="opacity" values="0;.9;0" dur="{r.uniform(2, 4):.1f}s" begin="{r.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>')
    body.append("".join(sparkle))
    clip = f'<clipPath id="fc"><rect width="{W}" height="{H}" rx="16"/></clipPath>'
    svg = document(W, H, "Got Territory data that isn't doing anything yet?",
                   "A Darwin harbour sunset with a moving tide line. Built and deployed from Darwin, 12.4637 S, 130.8444 E.",
                   css, f'{clip}<g clip-path="url(#fc)">{"".join(body)}</g>')
    return svg


if __name__ == "__main__":
    write("hero.svg", build_hero())
    build_cards()
    write("strata.svg", build_strata())
    write("footer.svg", build_footer())
