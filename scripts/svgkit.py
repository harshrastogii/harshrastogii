"""Shared helpers for the hand-built profile SVGs.

Every asset in ../assets is plain SVG with CSS keyframes and SMIL, so it animates
when GitHub serves it through an <img> tag (no scripts, no external fonts).
Colours follow the design tokens of harshrastogi.au.
"""

import math
import random
from xml.sax.saxutils import escape

INK = {1: "#101112", 2: "#17181a", 3: "#1f2023", 4: "#26282c", 5: "#303237",
       6: "#3d4046", 7: "#4e5158", 8: "#63666e", 9: "#7d8189", 10: "#9ca0a8",
       11: "#c0c3c9", 12: "#e6e8ec"}
TEAL = {3: "#06353f", 5: "#036679", 6: "#0090ab", 7: "#06b6d4", 8: "#35d3ee",
        9: "#8be9f7", 10: "#aef0fa"}
GREEN = {3: "#08361d", 5: "#0d6b35", 7: "#16a34a", 8: "#31d46c", 9: "#86eaa9"}
BLUE = {3: "#121f47", 5: "#1e3a91", 7: "#2563eb", 8: "#5b8bf5", 9: "#a8c3fb"}
AMBER = "#fbbf24"
EMBER = "#f97316"
RED = "#ef4444"

SANS = "'Plus Jakarta Sans','Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"

# Reduced motion: skip straight to each animation's end state rather than
# switching animations off, so fade-ins still finish visible.
REDUCED = ("@media (prefers-reduced-motion: reduce){*{animation-duration:0s!important;"
           "animation-delay:0s!important;animation-iteration-count:1!important}}")


def esc(text):
    return escape(text, {'"': "&quot;"})


def f(v):
    """Compact number formatting for coordinates."""
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def document(width, height, title, desc, css, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">\n'
        f'<title id="t">{esc(title)}</title>\n<desc id="d">{esc(desc)}</desc>\n'
        f"<style>{css}{REDUCED}</style>\n{body}\n</svg>\n"
    )


def smooth_path(points, closed=False):
    """Catmull-Rom spline through points, emitted as cubic Béziers."""
    pts = list(points)
    if closed:
        pts = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        pts = [pts[0]] + pts + [pts[-1]]
    d = [f"M{f(pts[1][0])},{f(pts[1][1])}"]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}")
    if closed:
        d.append("Z")
    return "".join(d)


def periodic_noise(rng, period, harmonics=5):
    """A smooth function that repeats exactly every `period` units."""
    terms = [(k, rng.uniform(0, math.tau), rng.uniform(0.3, 1.0) / k)
             for k in range(1, harmonics + 1)]
    norm = sum(a for _, _, a in terms)

    def fn(x):
        return sum(a * math.sin(math.tau * k * x / period + p) for k, p, a in terms) / norm
    return fn


def rng(seed):
    return random.Random(seed)
