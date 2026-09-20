import os, json, html, random, urllib.request
from datetime import date, datetime, timezone
from PIL import Image, ImageOps

# ---------- edit this block ----------
USERNAME = "krithik-n25"
START = date(2024, 8, 1)          # uptime start, pick any date
PHOTO = "photo.png"               # crop tight on your face
INVERT = False                    # set True if your photo background is light
CITY, TZ = "Ahmedabad", "UTC+5:30"
INFO = [
    ("Subject", "Krithik Naidu"),
    ("Role", "CSE Student"),
    ("Location", "Ahmedabad, Gujarat"),
    ("Education", "B.Tech CSE"),
    ("Language", "Python, JavaScript"),
]
FOCUS = "ML . Backend . Applied AI . Agentic AI"
CONTACT = [
    ("Mail", "nadiukrithik37@gmail.com"),
    ("LinkedIn", "/in/krithik-naidu-579400350"),
    ("GitHub", USERNAME),
]
# --------------------------------------

W, H = 900, 560
BG, PANEL, LINE = "#0b1220", "#0d1526", "#1c2940"
CYAN, DIMT, WHITE, AMBER, GREEN, RED = "#22d3ee", "#6b7a90", "#f1f5f9", "#fbbf24", "#34d399", "#ff5f57"
DOT = "#a5e8f7"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
TOKEN = os.environ.get("GITHUB_TOKEN")
NOW = datetime.now(timezone.utc)

COLS, ROWS, PITCH = 100, 115, 3   # dot grid, 300 x 345 px

def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-card"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def get_stats():
    try:
        user = api(f"/users/{USERNAME}")
        stars, page = 0, 1
        while True:
            repos = api(f"/users/{USERNAME}/repos?per_page=100&type=owner&page={page}")
            stars += sum(r["stargazers_count"] for r in repos)
            if len(repos) < 100:
                break
            page += 1
        commits = api(f"/search/commits?q=author:{USERNAME}&per_page=1")["total_count"]
        return dict(Repos=user["public_repos"], Stars=stars, Commits=commits, Followers=user["followers"])
    except Exception as e:
        print("stats failed:", e)
        return dict(Repos="n/a", Stars="n/a", Commits="n/a", Followers="n/a")

def uptime():
    t = date.today()
    y, m, d = t.year - START.year, t.month - START.month, t.day - START.day
    if d < 0:
        m -= 1
        d += 30
    if m < 0:
        y -= 1
        m += 12
    s = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return f"{s(y, 'year')}, {s(m, 'month')}, {s(d, 'day')}"

def dither_points(seed):
    """Floyd-Steinberg dithering with serpentine scan. Bright pixels become dots.
    A small random threshold jitter, seeded per run, makes every regeneration differ."""
    img = Image.open(PHOTO).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    w, h = img.size
    target = ROWS / COLS
    ch = min(h, int(w * target))
    cw = int(ch / target)
    left, top = (w - cw) // 2, max(0, (h - ch) // 4)
    img = img.crop((left, top, left + cw, top + ch)).resize((COLS, ROWS), Image.LANCZOS)
    px = [[float(img.getpixel((x, y))) for x in range(COLS)] for y in range(ROWS)]
    if INVERT:
        px = [[255.0 - v for v in row] for row in px]
    rng = random.Random(seed)
    pts = []
    for y in range(ROWS):
        forward = y % 2 == 0
        d = 1 if forward else -1
        for x in (range(COLS) if forward else range(COLS - 1, -1, -1)):
            old = px[y][x]
            new = 255.0 if old > 127.5 + rng.uniform(-25, 25) else 0.0
            err = old - new
            if new:
                pts.append((x, y))
            for dx, dy, f in ((d, 0, 7 / 16), (-d, 1, 3 / 16), (0, 1, 5 / 16), (d, 1, 1 / 16)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < COLS and 0 <= yy < ROWS:
                    px[yy][xx] += err * f
    return pts, rng

def esc(s):
    return html.escape(str(s), quote=False)

def build():
    stats = get_stats()
    seed = int(NOW.strftime("%Y%m%d%H"))
    pts, rng = dither_points(seed)
    o = []
    a = o.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">')
    a(f'''<style>
.g0,.g1,.g2,.g3{{animation:tw 3.4s ease-in-out infinite}}
.g1{{animation-delay:.85s}}.g2{{animation-delay:1.7s}}.g3{{animation-delay:2.55s}}
@keyframes tw{{0%,100%{{opacity:.95}}50%{{opacity:.22}}}}
.live{{animation:blink 1.3s ease-in-out infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.15}}}}
.sweep{{animation:sweep 5s linear infinite}}
@keyframes sweep{{0%{{transform:translateY(-16px);opacity:0}}12%{{opacity:1}}88%{{opacity:1}}100%{{transform:translateY({ROWS * PITCH}px);opacity:0}}}}
</style>''')
    a('<defs><linearGradient id="trail" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0.28"/>'
      '</linearGradient></defs>')
    a(f'<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="#1e2a3f"/>')

    # title bar
    for cx, c in ((28, "#ff5f57"), (48, "#febc2e"), (68, "#28c840")):
        a(f'<circle cx="{cx}" cy="26" r="6" fill="{c}"/>')
    a(f'<text x="{W // 2}" y="30" font-size="11" fill="{DIMT}" text-anchor="middle">profile.sh --live</text>')

    # ---------- left panel: VISUAL.MAP ----------
    lx, ly, lw, lh = 24, 56, 320, 480
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="4" fill="{PANEL}" stroke="{LINE}"/>')
    a(f'<text x="{lx + 12}" y="{ly + 22}" font-size="11" font-weight="700" fill="{CYAN}" letter-spacing="1">VISUAL.MAP</text>')
    a(f'<text x="{lx + lw - 12}" y="{ly + 22}" font-size="9" fill="{DIMT}" text-anchor="end">{COLS * PITCH}x{ROWS * PITCH} / 1-BIT</text>')
    a(f'<line x1="{lx}" y1="{ly + 34}" x2="{lx + lw}" y2="{ly + 34}" stroke="{LINE}"/>')

    ax0, ay0, ax1, ay1 = lx + 10, ly + 44, lx + lw - 10, ly + lh - 30
    dx0 = ax0
    dy0 = ay0 + ((ay1 - ay0) - ROWS * PITCH) // 2
    groups = [[], [], [], []]
    for x, y in pts:
        groups[rng.randrange(4)].append(f"M{dx0 + x * PITCH} {dy0 + y * PITCH}h1.8v1.8h-1.8z")
    for i, g in enumerate(groups):
        a(f'<path class="g{i}" fill="{DOT}" d="{"".join(g)}"/>')
    a(f'<clipPath id="clip"><rect x="{ax0}" y="{dy0}" width="{COLS * PITCH}" height="{ROWS * PITCH}"/></clipPath>')
    a(f'<g clip-path="url(#clip)"><g class="sweep">'
      f'<rect x="{ax0}" y="{dy0 - 14}" width="{COLS * PITCH}" height="14" fill="url(#trail)"/>'
      f'<rect x="{ax0}" y="{dy0}" width="{COLS * PITCH}" height="1.5" fill="{CYAN}" opacity="0.8"/>'
      f'</g></g>')
    for cx, cy, sx, sy in ((ax0, ay0, 1, 1), (ax1, ay0, -1, 1), (ax0, ay1, 1, -1), (ax1, ay1, -1, -1)):
        a(f'<path d="M{cx + 12 * sx} {cy}L{cx} {cy}L{cx} {cy + 12 * sy}" stroke="{CYAN}" stroke-opacity="0.6" fill="none"/>')
    a(f'<text x="{lx + 12}" y="{ly + lh - 12}" font-size="9" fill="{DIMT}">PTS {len(pts)} · FS/SERPENTINE</text>')

    # ---------- right panel: SYSTEM.INFO ----------
    rx, ry, rw, rh = 360, 56, 516, 480
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="4" fill="{PANEL}" stroke="{LINE}"/>')
    a(f'<text x="{rx + 12}" y="{ry + 22}" font-size="11" font-weight="700" fill="{CYAN}" letter-spacing="1">SYSTEM.INFO</text>')
    pill_w = 12 + 8 * (len(USERNAME) + 1)
    px0 = rx + rw - 12 - pill_w
    a(f'<rect x="{px0}" y="{ry + 8}" width="{pill_w}" height="22" rx="11" fill="#12304a"/>')
    a(f'<text x="{px0 + pill_w / 2}" y="{ry + 23}" font-size="11" font-weight="700" fill="{CYAN}" text-anchor="middle">@{esc(USERNAME)}</text>')
    a(f'<text x="{px0 - 12}" y="{ry + 23}" font-size="9" font-weight="700" fill="{RED}" text-anchor="end">LIVE</text>')
    a(f'<circle class="live" cx="{px0 - 46}" cy="{ry + 19.5}" r="3" fill="{RED}"/>')
    a(f'<line x1="{rx}" y1="{ry + 34}" x2="{rx + rw}" y2="{ry + 34}" stroke="{LINE}"/>')

    kx, vx = rx + 14, rx + rw - 14
    cw = 7.9
    y = ry + 62

    def row(key, val, color=WHITE):
        nonlocal y
        val = str(val)
        a(f'<text x="{kx}" y="{y}" font-size="12" fill="{DIMT}">{esc(key)}</text>')
        a(f'<text x="{vx}" y="{y}" font-size="12" font-weight="700" fill="{color}" text-anchor="end">{esc(val)}</text>')
        ds, de = kx + len(key) * cw + 10, vx - len(val) * cw - 10
        if de > ds:
            a(f'<line x1="{ds:.0f}" y1="{y - 3}" x2="{de:.0f}" y2="{y - 3}" stroke="#2a3a55" stroke-dasharray="1 4" stroke-linecap="round"/>')
        y += 25

    row("Uptime", uptime(), AMBER)
    for k, v in INFO:
        row(k, v)
    row("Focus", FOCUS)
    y += 10
    for k, v in CONTACT:
        row(f"Grid.{k}", v)
    y += 10
    for k in ("Repos", "Stars", "Commits", "Followers"):
        row(f"Git.{k}", stats[k], AMBER)

    fy = ry + rh - 30
    a(f'<line x1="{rx + 12}" y1="{fy}" x2="{rx + rw - 12}" y2="{fy}" stroke="{LINE}"/>')
    a(f'<circle class="live" cx="{kx + 3}" cy="{fy + 15}" r="2.5" fill="{GREEN}"/>')
    a(f'<text x="{kx + 12}" y="{fy + 18}" font-size="9" fill="{GREEN}">ALL SYSTEMS NOMINAL</text>')
    a(f'<text x="{vx}" y="{fy + 18}" font-size="9" fill="{DIMT}" text-anchor="end">SYNC {NOW:%d %b %H:%M} UTC · {esc(TZ)} · {esc(CITY.upper())} NODE</text>')

    a('</svg>')
    with open("card.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print("wrote card.svg,", len(pts), "points")

if __name__ == "__main__":
    build()
