"""Renders assets/pulse.svg: a year of GitHub contributions drawn as a trace.

    GITHUB_TOKEN=... python scripts/render_pulse.py          # fetch, save data/pulse.json, render
    python scripts/render_pulse.py --offline                 # re-render from data/pulse.json

Standard library only, so it runs on a bare Actions runner. Every number printed
on the instrument comes from the contribution calendar GitHub returns.
"""

import datetime as dt
import json
import math
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, SANS, TEAL, document, esc, f, rng  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "pulse.json")
OUT = os.path.join(ROOT, "assets", "pulse.svg")
LOGIN = os.environ.get("PROFILE_LOGIN", "harshrastogii")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
  }
}
"""


def fetch(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-pulse"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    user = payload["data"]["user"]
    days = [{"date": d["date"], "count": d["contributionCount"]}
            for w in user["contributionsCollection"]["contributionCalendar"]["weeks"]
            for d in w["contributionDays"]]
    sizes = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            sizes[edge["node"]["name"]] = sizes.get(edge["node"]["name"], 0) + edge["size"]
    total = sum(sizes.values()) or 1
    langs = [{"name": n, "share": round(s / total, 4)}
             for n, s in sorted(sizes.items(), key=lambda kv: -kv[1])[:6]]
    return {"login": LOGIN, "generated": dt.date.today().isoformat(),
            "source": "GitHub GraphQL contribution calendar", "days": days, "languages": langs}


def streaks(counts):
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    tail = counts[:-1] if counts and counts[-1] == 0 else counts  # today may not have started
    for c in reversed(tail):
        if not c:
            break
        current += 1
    return current, longest


def render(data):
    days = data["days"][-365:]
    counts = [d["count"] for d in days]
    dates = [dt.date.fromisoformat(d["date"]) for d in days]
    total, peak = sum(counts), max(counts) or 1
    peak_i = counts.index(peak)
    active = sum(1 for c in counts if c)
    current, longest = streaks(counts)

    W, H = 1200, 330
    x0, x1, base, amp = 40, 1160, 150, 84
    step = (x1 - x0) / len(days)
    r = rng(7)

    # each day is a short burst whose amplitude follows sqrt(count)
    pts = [(x0, base)]
    for i, c in enumerate(counts):
        a = 1.2 + (amp - 4) * math.sqrt(c / peak) if c else r.uniform(0.3, 1.0)
        for k, sgn in enumerate((1, -1, 0.65, -0.4)):
            x = x0 + step * (i + (k + 1) / 5)
            pts.append((x, base - sgn * a * r.uniform(0.7, 1.0)))
    pts.append((x1, base))
    trace = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)

    css = f"""
.ttl{{font:600 17px {SANS};fill:{INK[12]}}}
.sub{{font:400 14px {SANS};fill:{INK[9]}}}
.ax{{font:400 12px {SANS};fill:{INK[8]}}}
.note{{font:500 12.5px {SANS};fill:{INK[11]}}}
.sum{{font:400 15px {SANS};fill:{INK[10]}}}
.sum tspan.n{{font-weight:600;fill:{INK[12]}}}
.ink{{stroke-dasharray:1;stroke-dashoffset:1;animation:ink 5s cubic-bezier(.4,0,.2,1) .3s forwards}}
@keyframes ink{{to{{stroke-dashoffset:0}}}}
.late{{opacity:0;animation:late .8s ease 4.6s forwards}}
@keyframes late{{to{{opacity:1}}}}
"""
    body = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="8.5" fill="{INK[1]}" stroke="{INK[4]}"/>',
            f'<text x="{x0}" y="42" class="ttl">Contributions over the last 12 months</text>',
            f'<text x="{x1}" y="42" text-anchor="end" class="sub">to {dates[-1].day} {dates[-1]:%B %Y}</text>',
            f'<line x1="{x0}" y1="{base + .5}" x2="{x1}" y2="{base + .5}" stroke="{INK[4]}"/>']
    for i, d in enumerate(dates):
        if d.day == 1:
            x = x0 + step * i
            body.append(f'<line x1="{f(x)}" y1="{base + amp + 4}" x2="{f(x)}" y2="{base + amp + 10}" stroke="{INK[6]}"/>'
                        f'<text x="{f(x + 4)}" y="{base + amp + 22}" class="ax">{d:%b}</text>')
    body.append(f'<path class="ink" pathLength="1" d="{trace}" fill="none" stroke="{TEAL[8]}" stroke-width="1.3" stroke-linejoin="round"/>')

    px = x0 + step * (peak_i + 0.5)
    anchor = "end" if px > W - 200 else "start"
    tx = px - 8 if anchor == "end" else px + 8
    body.append(f'<g class="late"><line x1="{f(px)}" y1="{base - amp - 6}" x2="{f(px)}" y2="{base - amp + 6}" stroke="{INK[10]}"/>'
                f'<text x="{f(tx)}" y="{base - amp + 4}" text-anchor="{anchor}" class="note">Busiest day: {peak} on {dates[peak_i].day} {dates[peak_i]:%B}</text></g>')

    line = (f'<tspan class="n">{total:,}</tspan> contributions on <tspan class="n">{active}</tspan> days. '
            f'Current streak <tspan class="n">{current}</tspan> {"day" if current == 1 else "days"}, '
            f'longest <tspan class="n">{longest}</tspan>.')
    if data.get("languages"):
        langs = ", ".join(f'{l["name"].replace(" Notebook", "")} {round(l["share"] * 100)}%' for l in data["languages"][:3])
        line += f" Public code: {esc(langs)}."
    body.append(f'<text x="{x0}" y="{H - 26}" class="sum">{line}</text>')

    return document(
        W, H, f"{LOGIN}: contributions over the last 12 months",
        f"{total} contributions over the last 365 days on {active} days. Busiest day {peak} "
        f"on {dates[peak_i]:%d %B %Y}. Current streak {current} days, longest {longest} days.",
        css, "\n".join(body))


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if "--offline" not in sys.argv and token:
        data = fetch(token)
        os.makedirs(os.path.dirname(DATA), exist_ok=True)
        with open(DATA, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=1)
    else:
        with open(DATA, encoding="utf-8") as fh:
            data = json.load(fh)
    svg = render(data)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {os.path.relpath(OUT, ROOT)} from {len(data['days'])} days")


if __name__ == "__main__":
    main()
