"""Renders assets/pulse.svg: a year of GitHub contributions drawn as a seismograph.

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
from svgkit import AMBER, GREEN, INK, MONO, SANS, TEAL, document, esc, f, rng  # noqa: E402

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

    W, H = 1200, 360
    x0, x1, base, amp = 70, 1150, 158, 92
    step = (x1 - x0) / len(days)
    r = rng(7)

    # the trace: each day is a short burst whose amplitude follows sqrt(count)
    pts = [(x0, base)]
    for i, c in enumerate(counts):
        a = 1.2 + (amp - 4) * math.sqrt(c / peak) if c else r.uniform(0.4, 1.6)
        for k, sgn in enumerate((1, -1, 0.65, -0.4)):
            x = x0 + step * (i + (k + 1) / 5)
            pts.append((x, base - sgn * a * r.uniform(0.7, 1.0)))
    pts.append((x1, base))
    trace = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)

    cycle = 14
    css = f"""
.hd{{font:500 12px {MONO};fill:{INK[10]};letter-spacing:.2em}}
.ax{{font:500 11px {MONO};fill:{INK[9]};letter-spacing:.1em}}
.val{{font:700 30px {SANS};fill:{INK[12]};letter-spacing:-.02em}}
.lab{{font:500 10.5px {MONO};fill:{INK[10]};letter-spacing:.14em}}
.note{{font:500 11px {MONO};fill:{AMBER};letter-spacing:.08em}}
.ink{{stroke-dasharray:1;stroke-dashoffset:1;animation:ink {cycle}s linear infinite}}
@keyframes ink{{0%{{stroke-dashoffset:1;opacity:1}}62%{{stroke-dashoffset:0;opacity:1}}93%{{stroke-dashoffset:0;opacity:1}}100%{{stroke-dashoffset:0;opacity:0}}}}
.ghost{{opacity:.14}}
.pen{{animation:pen .18s linear infinite alternate}}
@keyframes pen{{from{{transform:translateY(-3px)}}to{{transform:translateY(3px)}}}}
.rec{{animation:rec 1.2s ease-in-out infinite}}
@keyframes rec{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
.mark{{opacity:0;animation:mark {cycle}s linear infinite}}
@keyframes mark{{0%,{peak_i / len(days) * 62:.1f}%{{opacity:0}}{peak_i / len(days) * 62 + 2:.1f}%,93%{{opacity:1}}100%{{opacity:0}}}}
"""
    rec = "REC · " + dates[-1].strftime("%d %b %Y").upper()
    body = [f"""<defs>
<linearGradient id="tr" x1="0" x2="1"><stop offset="0" stop-color="{TEAL[7]}"/><stop offset=".6" stop-color="{TEAL[8]}"/><stop offset="1" stop-color="{GREEN[8]}"/></linearGradient>
<pattern id="paper" width="{f(step * 7)}" height="23" patternUnits="userSpaceOnUse" x="{x0}" y="{base}">
 <path d="M{f(step * 7)},0 H0 V23" fill="none" stroke="{INK[3]}" stroke-width="1"/></pattern>
<filter id="gl" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>
<clipPath id="fr"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>""",
            f'<g clip-path="url(#fr)"><rect width="{W}" height="{H}" fill="{INK[1]}"/>',
            f'<rect x="{x0}" y="{base - amp - 4}" width="{x1 - x0}" height="{2 * amp + 8}" fill="url(#paper)"/>',
            f'<line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{INK[5]}"/>',
            f'<text x="{x0}" y="36" class="hd">FIELD SIGNAL · {esc(LOGIN.upper())} · CONTRIBUTIONS, LAST 365 DAYS</text>',
            f'<circle class="rec" cx="{f(x1 - len(rec) * 9.6 - 10)}" cy="32" r="4.5" fill="#ef4444"/>',
            f'<text x="{x1}" y="36" text-anchor="end" class="hd">{esc(rec)}</text>']

    # month ticks
    for i, d in enumerate(dates):
        if d.day == 1:
            x = x0 + step * i
            body.append(f'<line x1="{f(x)}" y1="{base + amp + 6}" x2="{f(x)}" y2="{base + amp + 14}" stroke="{INK[7]}"/>'
                        f'<text x="{f(x + 4)}" y="{base + amp + 26}" class="ax">{d.strftime("%b").upper()}</text>')

    body.append(f'<path class="ghost" d="{trace}" fill="none" stroke="{TEAL[8]}" stroke-width="1"/>')
    body.append(f'<path class="ink" pathLength="1" d="{trace}" fill="none" stroke="{TEAL[8]}" stroke-width="3" opacity=".22" filter="url(#gl)"/>')
    body.append(f'<path class="ink" id="trace" pathLength="1" d="{trace}" fill="none" stroke="url(#tr)" stroke-width="1.4" stroke-linejoin="round"/>')
    body.append(f'<g><animateMotion dur="{cycle}s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;0.62;1" calcMode="linear">'
                f'<mpath href="#trace"/></animateMotion><g class="pen"><circle r="7" fill="{GREEN[8]}" opacity=".25"/>'
                f'<circle r="3" fill="#ecfeff"/></g></g>')

    # annotate the biggest day
    px = x0 + step * (peak_i + 0.5)
    body.append(f'<g class="mark"><line x1="{f(px)}" y1="{base - amp - 10}" x2="{f(px)}" y2="{base + amp}" stroke="{AMBER}" stroke-dasharray="3 3"/>'
                f'<text x="{f(px - 8)}" y="{base - amp - 14}" text-anchor="end" class="note">PEAK · {peak} ON {esc(dates[peak_i].strftime("%d %b").upper())}</text></g>')

    # readouts
    stats = [(f"{total:,}", "CONTRIBUTIONS"), (str(active), "ACTIVE DAYS"), (str(peak), "BEST DAY"),
             (f"{current}d", "CURRENT STREAK"), (f"{longest}d", "LONGEST STREAK")]
    colw = (x1 - x0) / (len(stats) + (1 if data.get("languages") else 0))
    for i, (v, lab) in enumerate(stats):
        x = x0 + i * colw
        body.append(f'<line x1="{f(x)}" y1="{H - 72}" x2="{f(x)}" y2="{H - 22}" stroke="{INK[4]}"/>'
                    f'<text x="{f(x + 14)}" y="{H - 40}" class="val">{esc(v)}</text>'
                    f'<text x="{f(x + 14)}" y="{H - 22}" class="lab">{lab}</text>')
    if data.get("languages"):
        x = x0 + len(stats) * colw
        body.append(f'<line x1="{f(x)}" y1="{H - 72}" x2="{f(x)}" y2="{H - 22}" stroke="{INK[4]}"/>'
                    f'<text x="{f(x + 14)}" y="{H - 22}" class="lab">PUBLIC CODE</text>')
        for k, lang in enumerate(data["languages"][:3]):
            y = H - 62 + k * 13
            share = round(lang["share"] * 100)
            body.append(f'<rect x="{f(x + 14)}" y="{y - 8}" width="{f(max(2, share * 0.5))}" height="8" rx="2" fill="{(TEAL[8], GREEN[8], AMBER)[k]}"/>'
                        f'<text x="{f(x + 70)}" y="{y}" style="font:500 11.5px {MONO};fill:{INK[11]}">{esc(lang["name"].replace(" Notebook", ""))} {share}%</text>')
    body.append("</g>")

    return document(
        W, H, f"{LOGIN}: a year of contributions as a seismograph",
        f"{total} contributions over the last 365 days, {active} active days, best day {peak} "
        f"on {dates[peak_i]:%d %B %Y}, current streak {current} days, longest streak {longest} days.",
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
