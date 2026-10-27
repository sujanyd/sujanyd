"""Render the arcade "fidget" charts for the profile README.

Fetches the public contribution calendar and repo languages for a GitHub user
and writes animated SVGs into assets/. Stdlib only, so the workflow needs no
pip install.

    python scripts/build_charts.py --user sujanyd --out assets
    python scripts/build_charts.py --data snapshot.json --out assets   # offline
"""
import argparse
import datetime as dt
import json
import math
import os
import random
import re
import urllib.request

BG = "#0d1117"
PANEL = "#161b22"
SCREEN = "#0a0c10"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
PURPLE = "#a371f7"
GREEN = "#7ee787"
CYAN = "#79c0ff"
PINK = "#ff7b72"
AMBER = "#f2cc60"
MONO = "ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace"
LEVEL = ["#21262d", "#3b2a66", "#5b3fa0", "#7c55d6", "#a371f7"]
LANG_COLORS = {"HTML": "#e34c26", "JavaScript": "#f1e05a", "Python": "#3572a5", "TypeScript": "#3178c6",
               "CSS": "#663399", "Java": "#b07219", "Jupyter Notebook": "#da5b0b", "Shell": "#89e051"}
WEEKDAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

# ─────────────────────────────── DATA ───────────────────────────────


def _get(url, token=None):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-charts"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def fetch_days(user):
    html = _get(f"https://github.com/users/{user}/contributions")
    tips = {}
    for for_id, label in re.findall(r'<tool-tip[^>]*?\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"\s*(\d+|No) contribution", label)
        if m:
            tips[for_id] = 0 if m.group(1) == "No" else int(m.group(1))
    days = []
    for tag in re.findall(r"<td\b[^>]*ContributionCalendar-day[^>]*>", html):
        date = re.search(r'data-date="([\d-]+)"', tag)
        level = re.search(r'data-level="(\d)"', tag)
        cell = re.search(r'\bid="([^"]+)"', tag)
        if date and level:
            days.append([date.group(1), int(level.group(1)), tips.get(cell.group(1) if cell else "", 0)])
    if not days:
        raise SystemExit("no contribution cells found; GitHub markup may have changed")
    return sorted(days)


def fetch_langs(user, token=None):
    repos = json.loads(_get(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner", token))
    langs = {}
    for repo in repos:
        if not repo.get("fork") and repo.get("language"):
            langs[repo["language"]] = langs.get(repo["language"], 0) + 1
    return langs


def summarize(days):
    counts = [c for _, _, c in days]
    best = max(days, key=lambda d: d[2])
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    for c in reversed(tail):
        if not c:
            break
        current += 1
    weekday = [0] * 7
    months = {}
    for date, _, c in days:
        d = dt.date.fromisoformat(date)
        weekday[(d.weekday() + 1) % 7] += c
        key = date[:7]
        months[key] = months.get(key, 0) + c
    return {
        "total": sum(counts),
        "active": sum(1 for c in counts if c),
        "best": best,
        "longest": longest,
        "current": current,
        "weekday": weekday,
        "months": list(months.items())[-12:],
    }


# ─────────────────────────────── HELPERS ───────────────────────────────


def frame(w, h, title, sub, accent):
    """Draw a desktop-app window: title bar with traffic lights, dark screen below."""
    return (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="{SCREEN}" stroke="{BORDER}" stroke-width="2"/>'
            f'<path d="M1 13a12 12 0 0 1 12-12h{w - 26}a12 12 0 0 1 12 12v17H1Z" fill="{PANEL}"/>'
            f'<path d="M1 30H{w - 1}" stroke="{BORDER}" stroke-width="2"/>'
            f'<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/>'
            f'<circle cx="50" cy="16" r="5" fill="#27c93f"/>'
            f'<text x="68" y="20" font-size="11.5" font-weight="700" fill="{accent}">{title}</text>'
            f'<text x="{w - 16}" y="20" text-anchor="end" font-size="10.5" fill="{MUTED}">{sub}</text>')


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<g font-family="{MONO}">{body}</g></svg>\n')


def short_date(iso):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%b ") + str(d.day)


# ─────────────────────────────── ODOMETER COUNTERS ───────────────────────────────


def counters(s):
    tiles = [("TOTAL", s["total"], "contributions", PURPLE), ("ACTIVE DAYS", s["active"], "out of 365", CYAN),
             ("LONGEST STREAK", s["longest"], "days in a row", GREEN),
             ("BEST DAY", s["best"][2], short_date(s["best"][0]), AMBER)]
    out = []
    for i, (label, value, sub, col) in enumerate(tiles):
        x = 12 + i * 222
        out.append(f'<rect x="{x}" y="12" width="210" height="106" rx="12" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5"/>'
                   f'<text x="{x + 16}" y="36" font-size="11" letter-spacing="2" fill="{MUTED}">{label}</text>'
                   f'<text x="{x + 16}" y="104" font-size="11" fill="{MUTED}">{sub}</text>')
        digits = str(value)
        for j, ch in enumerate(digits):
            dx = x + 16 + j * 28
            final = int(ch)
            strip = "".join(f'<text x="{dx + 12}" y="{78 + k * 40}" text-anchor="middle" font-size="34" font-weight="800" fill="{col}">{k % 10}</text>'
                            for k in range(10 + final + 1))
            dur = 1.2 + j * 0.3 + i * 0.15
            out.append(f'<clipPath id="c{i}{j}"><rect x="{dx}" y="46" width="26" height="42"/></clipPath>'
                       f'<g clip-path="url(#c{i}{j})"><g transform="translate(0,{-(10 + final) * 40})">'
                       f'<animateTransform attributeName="transform" type="translate" from="0,0" to="0,{-(10 + final) * 40}" '
                       f'dur="{dur:.2f}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>{strip}</g></g>')
    head = frame(900, 160, "~/fidgets/sysmon", "live from github.com/sujanyd", GREEN)
    return svg(900, 160, head + f'<g transform="translate(0,30)">{"".join(out)}</g>')


# ─────────────────────────────── CONTRIBUTION CITY ───────────────────────────────


def city(days):
    rng = random.Random(7)
    first = dt.date.fromisoformat(days[0][0])
    start_col = (first.weekday() + 1) % 7
    cw, dx, dy = 14, 8, 7
    k = 170 / (max(c for *_, c in days) or 1)
    ox, oy = 40, 318
    cells = []
    for i, (date, level, count) in enumerate(days):
        idx = i + start_col
        cells.append((idx // 7, idx % 7, level, count, date))
    out = [frame(900, 384, "~/fidgets/city.exe", "every block is a day · height = contributions", PURPLE)]
    body, windows = [], []
    for d in range(7):
        for w, wd, level, count, date in sorted(c for c in cells if c[1] == d):
            back = 6 - wd
            x0, y0 = ox + w * cw + back * dx, oy - back * dy
            h = count * k
            top = ["#1c2128", "#4b3585", "#6a4cc0", "#8b66e8", "#b892ff"][level]
            front = LEVEL[level]
            side = ["#161b22", "#2c1f52", "#46337f", "#5f45ad", "#7c59d6"][level]
            if h:
                body.append(f'<path d="M{x0} {y0}h{cw}v{-h}h{-cw}Z" fill="{front}"/>'
                            f'<path d="M{x0 + cw} {y0}l{dx} {-dy}v{-h}l{-dx} {dy}Z" fill="{side}"/>')
                if count >= 3:
                    for wy in range(int(h // 10)):
                        if rng.random() < 0.6:
                            begin = rng.random() * 4
                            windows.append(f'<rect x="{x0 + 4}" y="{y0 - 8 - wy * 10}" width="6" height="4" fill="{AMBER}" opacity="0.2">'
                                           f'<animate attributeName="opacity" values="0.2;0.95;0.2" dur="{rng.choice([2, 3, 4])}s" begin="{begin:.1f}s" repeatCount="indefinite"/></rect>')
            body.append(f'<path d="M{x0} {y0 - h}h{cw}l{dx} {-dy}h{-cw}Z" fill="{top}" stroke="{SCREEN}" stroke-width="0.4"><title>{date}: {count}</title></path>')
    label_y = oy + 56
    seen = set()
    for w, wd, *_rest, date in cells:
        m = date[:7]
        if wd == 0 and m not in seen and date[8:] <= "07":
            seen.add(m)
            out.append(f'<text x="{ox + w * cw + 6 * dx}" y="{label_y}" font-size="10" fill="{MUTED}">{dt.date.fromisoformat(date).strftime("%b").upper()}</text>')
    out.append(f'<clipPath id="reveal"><rect x="0" y="0" width="0" height="384"><animate attributeName="width" from="0" to="900" dur="2.5s" fill="freeze"/></rect></clipPath>')
    out.append(f'<g clip-path="url(#reveal)">{"".join(body)}{"".join(windows)}</g>')
    out.append(road(oy + 8))
    return svg(900, 384, "".join(out))


CAR = ["...XXXXXX.....", "..XWWXWWWX....", ".XXXXXXXXXXXXH", "XXXXXXXXXXXXXH", ".OO.......OO.."]


def car_sprite(body, s=2):
    pal = {"X": body, "W": CYAN, "H": AMBER, "O": "#05060a"}
    out = []
    for y, row in enumerate(CAR):
        for x, c in enumerate(row):
            if c in pal:
                out.append(f'<rect x="{x * s}" y="{y * s}" width="{s}" height="{s}" fill="{pal[c]}"/>')
    beam = f'<path d="M{14 * s} {2 * s}l46 -5v{4 * s + 10}Z" fill="{AMBER}" opacity="0.18"/>'
    return beam + "".join(out)


def road(y):
    """Two-lane street in front of the city with cars driving both ways."""
    lane = 15
    return (f'<rect x="20" y="{y}" width="860" height="{2 * lane}" fill="#07080c"/>'
            f'<path d="M20 {y}H880M20 {y + 2 * lane}H880" stroke="{BORDER}"/>'
            f'<path d="M20 {y + lane}H880" stroke="#484f58" stroke-dasharray="10 8">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="-36" dur="1s" repeatCount="indefinite"/></path>'
            f'<clipPath id="street"><rect x="20" y="{y - 12}" width="860" height="{2 * lane + 14}"/></clipPath>'
            f'<g clip-path="url(#street)">'
            f'<g><animateTransform attributeName="transform" type="translate" from="-80,{y + lane + 2}" to="920,{y + lane + 2}" dur="7s" repeatCount="indefinite"/>{car_sprite(PINK)}</g>'
            f'<g><animateTransform attributeName="transform" type="translate" from="980,{y + 2}" to="-20,{y + 2}" dur="9s" begin="1.5s" repeatCount="indefinite"/>'
            f'<g transform="scale(-1,1)">{car_sprite(GREEN)}</g></g>'
            f'</g>')


# ─────────────────────────────── FIDGET SPINNER (languages) ───────────────────────────────


def spinner(langs):
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:3]
    while len(top) < 3:
        top.append(("—", 0))
    total = sum(langs.values()) or 1
    cx, cy = 150, 172
    arms, lobes = [], []
    for i, (name, n) in enumerate(top):
        a = math.radians(-90 + i * 120)
        lx, ly = cx + 70 * math.cos(a), cy + 70 * math.sin(a)
        col = LANG_COLORS.get(name, PURPLE)
        arms.append(f'<line x1="{cx}" y1="{cy}" x2="{lx:.1f}" y2="{ly:.1f}" stroke="{PANEL}" stroke-width="46" stroke-linecap="round"/>')
        lobes.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="34" fill="{PANEL}" stroke="{col}" stroke-width="4"/>'
                     f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="20" fill="{col}" fill-opacity="0.25" stroke="{col}" stroke-width="1.5"/>'
                     f'<text x="{lx:.1f}" y="{ly + 5:.1f}" text-anchor="middle" font-size="14" font-weight="800" fill="{TEXT}">{n}</text>')
    legend = []
    for i, (name, n) in enumerate(sorted(langs.items(), key=lambda kv: -kv[1])[:5]):
        y = 92 + i * 36
        col = LANG_COLORS.get(name, PURPLE)
        w = 120 * n / max(langs.values())
        legend.append(f'<text x="290" y="{y}" font-size="12" fill="{TEXT}">{name}</text>'
                      f'<text x="416" y="{y}" text-anchor="end" font-size="11" fill="{MUTED}">{round(100 * n / total)}%</text>'
                      f'<rect x="290" y="{y + 7}" width="126" height="6" rx="3" fill="{PANEL}"/>'
                      f'<rect x="290" y="{y + 7}" width="0" height="6" rx="3" fill="{col}">'
                      f'<animate attributeName="width" from="0" to="{w:.1f}" dur="1.2s" begin="{0.2 * i:.1f}s" fill="freeze"/></rect>')
    body = (frame(440, 300, "~/fidgets/spinner.exe", "repos by language", CYAN)
            + f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="6s" repeatCount="indefinite"/>'
            + "".join(arms) + "".join(lobes)
            + f'<circle cx="{cx}" cy="{cy}" r="22" fill="{BORDER}"/><circle cx="{cx}" cy="{cy}" r="12" fill="{CYAN}"/>'
            + f'<circle cx="{cx}" cy="{cy}" r="4" fill="{SCREEN}"/></g>'
            + "".join(legend)
            + f'<text x="24" y="284" font-size="10" fill="{MUTED}">top 3 on the spinner · numbers = repos</text>')
    return svg(440, 300, body)


# ─────────────────────────────── LED EQUALIZER (months) ───────────────────────────────


def equalizer(s):
    months = s["months"]
    peak = max((v for _, v in months), default=1) or 1
    segs, out = 12, []
    for i, (key, v) in enumerate(months):
        x = 40 + i * 31
        lit = max(1, round(segs * v / peak)) if v else 0
        for j in range(segs):
            y = 240 - j * 14
            col = GREEN if j < 7 else (AMBER if j < 10 else PINK)
            if j < lit:
                begin = 0.05 * i + 0.04 * j
                out.append(f'<rect x="{x}" y="{y}" width="24" height="10" rx="2" fill="{col}" opacity="0.15">'
                           f'<animate attributeName="opacity" from="0.15" to="1" dur="0.15s" begin="{begin:.2f}s" fill="freeze"/></rect>')
            else:
                out.append(f'<rect x="{x}" y="{y}" width="24" height="10" rx="2" fill="{PANEL}"/>')
        cap_lo, cap_hi = 240 - lit * 14, 240 - min(segs - 1, lit + 1) * 14
        out.append(f'<rect x="{x}" y="{cap_lo}" width="24" height="3" fill="{TEXT}" opacity="0.8">'
                   f'<animate attributeName="y" values="{cap_lo};{cap_hi};{cap_lo}" dur="{0.9 + (i % 4) * 0.2:.1f}s" repeatCount="indefinite"/></rect>')
        out.append(f'<text x="{x + 12}" y="270" text-anchor="middle" font-size="10" fill="{MUTED}">{dt.date.fromisoformat(key + "-01").strftime("%b")[0]}</text>'
                   f'<text x="{x + 12}" y="{226 - segs * 14}" text-anchor="middle" font-size="10" fill="{TEXT}">{v}</text>')
    return svg(440, 300, frame(440, 300, "~/fidgets/equalizer.exe", "contributions / month", GREEN) + "".join(out))


# ─────────────────────────────── WEEKDAY RADAR ───────────────────────────────


def radar(s):
    cx, cy, rmax = 150, 168, 104
    wk = s["weekday"]
    peak = max(wk) or 1
    out = [frame(440, 300, "~/fidgets/radar.exe", "when he ships", PINK)]
    for r in (35, 70, 104):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BORDER}" stroke-dasharray="3 5"/>')
    pts = []
    for i, v in enumerate(wk):
        a = math.radians(-90 + i * 360 / 7)
        r = 12 + (rmax - 12) * v / peak
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
        lx, ly = cx + (rmax + 16) * math.cos(a), cy + (rmax + 16) * math.sin(a)
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + rmax * math.cos(a):.1f}" y2="{cy + rmax * math.sin(a):.1f}" stroke="{BORDER}"/>'
                   f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle" font-size="10" fill="{MUTED}">{WEEKDAYS[i]}</text>')
    out.append(f'<defs><radialGradient id="sweep" cx="0" cy="0" r="1"><stop offset="0" stop-color="{PINK}" stop-opacity="0.5"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient></defs>')
    out.append(f'<path d="M{cx} {cy}L{cx} {cy - rmax}A{rmax} {rmax} 0 0 1 {cx + rmax * math.sin(math.radians(40)):.1f} {cy - rmax * math.cos(math.radians(40)):.1f}Z" fill="{PINK}" fill-opacity="0.18">'
               f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="4s" repeatCount="indefinite"/></path>')
    out.append(f'<polygon points="{" ".join(pts)}" fill="{PINK}" fill-opacity="0.25" stroke="{PINK}" stroke-width="2"/>')
    for p in pts:
        x, y = p.split(",")
        out.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{PINK}"/>')
    order = sorted(range(7), key=lambda i: -wk[i])
    for j, i in enumerate(order[:4]):
        y = 92 + j * 40
        out.append(f'<text x="300" y="{y}" font-size="12" fill="{TEXT}">{WEEKDAYS[i]}</text>'
                   f'<text x="416" y="{y}" text-anchor="end" font-size="16" font-weight="800" fill="{PINK if j == 0 else TEXT}">{wk[i]}</text>'
                   f'<path d="M300 {y + 10}H416" stroke="{BORDER}"/>')
    return svg(440, 300, "".join(out))


# ─────────────────────────────── YEAR RING ───────────────────────────────


def year_ring(days, s):
    cx, cy, r0 = 150, 166, 62
    n = len(days)
    peak = max(c for *_, c in days) or 1
    out = [frame(440, 300, "~/fidgets/year_ring.exe", "365 days, one loop", AMBER)]
    for i, (date, level, count) in enumerate(days):
        a = math.radians(-90 + 360 * i / n)
        l = 4 + 46 * math.sqrt(count / peak)
        col = LEVEL[level] if count else BORDER
        out.append(f'<line x1="{cx + r0 * math.cos(a):.1f}" y1="{cy + r0 * math.sin(a):.1f}" '
                   f'x2="{cx + (r0 + l) * math.cos(a):.1f}" y2="{cy + (r0 + l) * math.sin(a):.1f}" stroke="{AMBER if level == 4 else col}" stroke-width="2"/>')
    out.append(f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="10s" repeatCount="indefinite"/>'
               f'<circle cx="{cx}" cy="{cy - r0 + 10}" r="5" fill="{AMBER}"/></g>')
    out.append(f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="26" font-weight="800" fill="{TEXT}">{s["total"]}</text>'
               f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="10" fill="{MUTED}">this year</text>')
    rows = [("current streak", f'{s["current"]}d'), ("longest streak", f'{s["longest"]}d'),
            ("active days", str(s["active"])), ("best day", f'{s["best"][2]} · {short_date(s["best"][0])}')]
    for j, (k, v) in enumerate(rows):
        y = 92 + j * 40
        out.append(f'<text x="290" y="{y}" font-size="11" fill="{MUTED}">{k}</text>'
                   f'<text x="290" y="{y + 18}" font-size="15" font-weight="800" fill="{AMBER if j == 0 else TEXT}">{v}</text>')
    return svg(440, 300, "".join(out))


# ─────────────────────────────── NEON SNAKE ───────────────────────────────


def snake(days):
    first = dt.date.fromisoformat(days[0][0])
    start_col = (first.weekday() + 1) % 7
    grid = {}
    for i, (_, level, count) in enumerate(days):
        idx = i + start_col
        grid[(idx // 7, idx % 7)] = (level, count)
    cols = max(c for c, _ in grid) + 1
    ox, oy, cs = 32, 66, 15

    def center(c, r):
        return ox + c * cs + 6, oy + r * cs + 6

    # Greedy tour: always chase the nearest uneaten contribution, moving along the grid.
    food = {pos for pos, (_, n) in grid.items() if n}
    pos, steps, eat_at = (0, 0), [(0, 0)], {}
    while food:
        target = min(food, key=lambda p: (abs(p[0] - pos[0]) + abs(p[1] - pos[1]), p))
        while pos != target:
            if pos[0] != target[0]:
                pos = (pos[0] + (1 if target[0] > pos[0] else -1), pos[1])
            else:
                pos = (pos[0], pos[1] + (1 if target[1] > pos[1] else -1))
            steps.append(pos)
        eat_at[target] = len(steps) - 1
        food.discard(target)
    home = len(steps) - 1
    while pos != (0, 0):
        pos = (pos[0] - 1, pos[1]) if pos[0] else (pos[0], pos[1] - 1)
        steps.append(pos)
    n_steps = max(1, len(steps) - 1)
    step = min(0.09, 32 / n_steps)
    dur = n_steps * step

    corners = [steps[0]] + [p for a, p, b in zip(steps, steps[1:], steps[2:])
                            if (p[0] - a[0], p[1] - a[1]) != (b[0] - p[0], b[1] - p[1])] + [steps[-1]]
    path = "M" + " L".join("{} {}".format(*center(*p)) for p in corners)

    def kt(t):
        return f"{min(max(t / dur, 0), 1):.4f}"

    out = [frame(900, 230, "~/fidgets/snake.exe", "eating the contribution graph, one commit at a time", GREEN),
           '<filter id="neon" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/>'
           '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>']
    cells, bursts = [], []
    for (c, r), (level, count) in sorted(grid.items()):
        x, y = ox + c * cs, oy + r * cs
        if not count:
            cells.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{PANEL}"/>')
            continue
        t = eat_at[(c, r)] * step
        cells.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{LEVEL[level]}" stroke="{PURPLE}" stroke-opacity="0.6">'
                     f'<animate attributeName="opacity" values="1;0.15;1" keyTimes="0;{kt(t)};0.999" dur="{dur:.2f}s" calcMode="discrete" repeatCount="indefinite"/></rect>')
        cx, cy = center(c, r)
        bursts.append(f'<circle cx="{cx}" cy="{cy}" r="2" fill="none" stroke="{AMBER}" stroke-width="2" opacity="0">'
                      f'<animate attributeName="r" values="2;2;16;16" keyTimes="0;{kt(t)};{kt(t + 0.45)};1" dur="{dur:.2f}s" repeatCount="indefinite"/>'
                      f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{kt(t)};{kt(t + 0.01)};{kt(t + 0.45)};1" dur="{dur:.2f}s" repeatCount="indefinite"/></circle>')
    out += cells + bursts

    palette = [CYAN, "#8fa8ff", PURPLE, "#c86fe0", PINK, AMBER, GREEN]
    segs = 16
    body = []
    for k in range(segs, 0, -1):
        col = palette[min(len(palette) - 1, k * len(palette) // (segs + 1))]
        r = 6.5 - 3.5 * k / segs
        body.append(f'<circle r="{r:.1f}" fill="{col}" opacity="0"><set attributeName="opacity" to="1" begin="{k * step:.2f}s"/>'
                    f'<animateMotion path="{path}" dur="{dur:.2f}s" begin="{k * step:.2f}s" repeatCount="indefinite"/></circle>')
    head = (f'<g><animateMotion path="{path}" dur="{dur:.2f}s" repeatCount="indefinite" rotate="auto"/>'
            f'<circle r="8" fill="{CYAN}"/><circle cx="3" cy="-3.5" r="2" fill="{SCREEN}"/><circle cx="3" cy="3.5" r="2" fill="{SCREEN}"/>'
            f'<path d="M8 0h5M13 0l3 -2M13 0l3 2" stroke="{PINK}" stroke-width="1.5"><animate attributeName="opacity" values="1;0;1" dur="0.4s" repeatCount="indefinite"/></path></g>')
    out.append(f'<g filter="url(#neon)">{"".join(body)}{head}</g>')

    # Score ticks up as each contribution is eaten.
    eats = sorted((eat_at[p] * step, grid[p][1]) for p in eat_at)
    total, scores = 0, []
    marks = [(0.0, 0)]
    for t, n in eats:
        total += n
        marks.append((t, total))
    for i, (t, value) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else dur * 0.999
        scores.append(f'<text x="{900 - 24}" y="56" text-anchor="end" font-size="13" font-weight="800" fill="{TEXT}" opacity="{1 if i == 0 else 0}">{value:04d}'
                      f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{kt(t)};{kt(end)}" dur="{dur:.2f}s" calcMode="discrete" repeatCount="indefinite"/></text>'
                      if i else
                      f'<text x="{900 - 24}" y="56" text-anchor="end" font-size="13" font-weight="800" fill="{TEXT}">{value:04d}'
                      f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;{kt(end)};0.999" dur="{dur:.2f}s" calcMode="discrete" repeatCount="indefinite"/></text>')
    out += scores
    out.append(f'<text x="{900 - 76}" y="56" text-anchor="end" font-size="11" letter-spacing="2" fill="{MUTED}">SCORE</text>'
               f'<text x="24" y="56" font-size="11" letter-spacing="2" fill="{MUTED}">LEN <tspan fill="{CYAN}">{segs + 1}</tspan>'
               f'  ·  FOOD <tspan fill="{PURPLE}">{len(eat_at)}</tspan></text>')
    out.append(f'<text x="450" y="210" text-anchor="middle" font-size="13" font-weight="800" letter-spacing="4" fill="{GREEN}" opacity="0">'
               f'GRAPH CLEARED · RESPAWNING'
               f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{kt(home * step)};0.999" dur="{dur:.2f}s" calcMode="discrete" repeatCount="indefinite"/></text>')
    return svg(900, 230, "".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="sujanyd")
    ap.add_argument("--out", default="assets")
    ap.add_argument("--data", help="render from a saved JSON snapshot instead of fetching")
    ap.add_argument("--save", help="write the fetched data to this JSON file")
    args = ap.parse_args()
    if args.data:
        with open(args.data) as f:
            data = json.load(f)
    else:
        data = {"days": fetch_days(args.user), "langs": fetch_langs(args.user, os.environ.get("GITHUB_TOKEN"))}
        if args.save:
            with open(args.save, "w") as f:
                json.dump(data, f)
    days, langs = data["days"][-365:], data["langs"]
    s = summarize(days)
    os.makedirs(args.out, exist_ok=True)
    for name, content in [("fx-counters.svg", counters(s)), ("fx-city.svg", city(days)),
                          ("fx-spinner.svg", spinner(langs)), ("fx-equalizer.svg", equalizer(s)),
                          ("fx-radar.svg", radar(s)), ("fx-ring.svg", year_ring(days, s)),
                          ("fx-snake.svg", snake(days))]:
        with open(os.path.join(args.out, name), "w") as f:
            f.write(content)
    print(f"rendered 7 charts · {s['total']} contributions · {len(langs)} languages")


if __name__ == "__main__":
    main()
