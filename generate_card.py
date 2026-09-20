import os, json, html, urllib.request
from datetime import date
from PIL import Image, ImageOps

# ---------- edit this block ----------
USERNAME = "krithik-n25"
START = date(2024, 8, 1)          # your "uptime" start, pick any date
PHOTO = "photo.png"               # crop tight on your face
INFO = [
    ("Role", "CSE Student"),
    ("Education", "B.Tech CSE"),
    ("Location", "Ahmedabad/Gujarat"),
    ("Language", "Python","javascript"),
]
FOCUS = "Machine Learning, Backend Engg , Applied AI, Agentic AI"
CONTACT = [
    ("GitHub", f"github.com/{USERNAME}"),
    ("LinkedIn", "https://www.linkedin.com/in/krithik-naidu-579400350/"),
    ("Email", "nadiukrithik37@gmail.com"),
]
# --------------------------------------

W, H = 900, 540
CYAN, ORANGE, TEXT, DIM = "#4fd1c5", "#f0883e", "#c9d1d9", "#8b949e"
TOKEN = os.environ.get("GITHUB_TOKEN")

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
        return dict(Repos=user["public_repos"], Stars=stars,
                    Commits=commits, Followers=user["followers"])
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
    return f"{y} year{'s' if y != 1 else ''}, {m} month{'s' if m != 1 else ''}, {d} day{'s' if d != 1 else ''}"

def ascii_art(cols=64):
    img = Image.open(PHOTO).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    ratio = 1.15  # height / width of the crop
    w, h = img.size
    ch = min(h, int(w * ratio))
    cw = int(ch / ratio)
    left, top = (w - cw) // 2, max(0, (h - ch) // 3)
    img = img.crop((left, top, left + cw, top + ch))
    rows = int(cols * ratio * 0.5)
    img = img.resize((cols, rows))
    ramp = " .:-=+*#%@"
    return ["".join(ramp[img.getpixel((x, y)) * len(ramp) // 256] for x in range(cols))
            for y in range(rows)]

def esc(s):
    return html.escape(s, quote=False)

def build():
    stats = get_stats()
    art = ascii_art()
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">')
    a('<defs><linearGradient id="glow" x1="0" x2="1"><stop offset="0" stop-color="#4fd1c5" stop-opacity="0"/>'
      '<stop offset="0.5" stop-color="#4fd1c5"/><stop offset="1" stop-color="#4fd1c5" stop-opacity="0"/>'
      '</linearGradient></defs>')
    a(f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>')

    # left panel: portrait
    px, py, pw, ph = 40, 40, 350, 460
    a(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#0a0e13" stroke="#1f2a33"/>')
    cell_w = (pw - 20) / len(art[0])
    line_h = cell_w * 2
    top = py + (ph - line_h * len(art)) / 2 + line_h
    for i, line in enumerate(art):
        y = top + i * line_h
        a(f'<text x="{px + 10}" y="{y:.1f}" font-size="{cell_w / 0.6:.2f}" fill="{DIM}" '
          f'textLength="{pw - 20}" lengthAdjust="spacing" xml:space="preserve">{esc(line)}</text>')
    scan = py + ph * 0.82
    a(f'<rect x="{px}" y="{scan:.0f}" width="{pw}" height="2" fill="{CYAN}" opacity="0.7"/>')
    for cx, cy, dx, dy in [(px, py, 1, 1), (px + pw, py, -1, 1), (px, py + ph, 1, -1), (px + pw, py + ph, -1, -1)]:
        a(f'<path d="M{cx + 12 * dx} {cy} L{cx} {cy} L{cx} {cy + 12 * dy}" stroke="{CYAN}" fill="none"/>')

    # right panel
    rx0, rx1 = 430, W - 40
    a(f'<rect x="{rx0 - 15}" y="{py}" width="{rx1 - rx0 + 30}" height="{ph}" rx="8" fill="none" stroke="#21262d"/>')
    y = py + 34
    fs, cw_char = 15, 9.0

    def header(title):
        nonlocal y
        a(f'<text x="{rx0}" y="{y}" font-size="{fs}" fill="{CYAN}">{esc(title)}</text>')
        lx = rx0 + (len(title) + 1) * cw_char
        a(f'<line x1="{lx}" y1="{y - 5}" x2="{rx1}" y2="{y - 5}" stroke="{CYAN}" stroke-width="1"/>')
        y += 26

    def row(key, val, color=TEXT):
        nonlocal y
        a(f'<text x="{rx0}" y="{y}" font-size="{fs}" fill="{TEXT}">{esc(key)}</text>')
        a(f'<text x="{rx1}" y="{y}" font-size="{fs}" fill="{color}" text-anchor="end">{esc(str(val))}</text>')
        ds = rx0 + (len(key) + 1) * cw_char
        de = rx1 - (len(str(val)) + 2) * cw_char
        if de > ds:
            a(f'<line x1="{ds:.0f}" y1="{y - 3}" x2="{de:.0f}" y2="{y - 3}" stroke="{DIM}" '
              f'stroke-dasharray="1 5" stroke-linecap="round" stroke-width="1.5"/>')
        y += 22

    header(f"{USERNAME}@github")
    row("Uptime", uptime(), ORANGE)
    for k, v in INFO:
        row(k, v)
    y += 8
    header("Focus")
    a(f'<text x="{rx0}" y="{y}" font-size="{fs}" fill="{TEXT}">{esc(FOCUS)}</text>')
    y += 32
    header("Contact")
    for k, v in CONTACT:
        row(k, v)
    y += 8
    header("GitHub Stats")
    row("Repos", stats["Repos"], ORANGE)
    row("Stars", stats["Stars"], ORANGE)
    row("Commits", stats["Commits"], ORANGE)
    row("Followers", stats["Followers"], ORANGE)

    a(f'<rect x="40" y="{H - 24}" width="{W - 80}" height="2" fill="url(#glow)"/>')
    a('</svg>')
    with open("card.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("wrote card.svg")

if __name__ == "__main__":
    build()
