import os
import html
import requests
from pathlib import Path

USERNAME = "batualkoc"
ROOT = Path(__file__).resolve().parent
ASCII_FILE = ROOT / "ascii-art.txt"

TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

PROFILE = {
    "header": "batualkoc@github",
    "os": "Linux · Windows Server · Cloud",
    "role": "Infrastructure & Security Engineer",
    "focus": "Cloud · Network · Automation",
    "stack": "VMware · FortiGate · AWS · Azure",
    "infrastructure": "VMware, Windows Server, Linux",
    "network": "FortiGate, DNS, DHCP, VPN",
    "cloud": "AWS, Azure",
    "automation": "Python, n8n, REST APIs",
    "security": "Firewall, IAM, Hardening",
}

THEMES = {
    "dark": {
        "background": "#0d1117",
        "border": "#30363d",
        "portrait": "#c9d1d9",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "label": "#ffa657",
        "value": "#79c0ff",
        "positive": "#7ee787",
    },
    "light": {
        "background": "#ffffff",
        "border": "#d0d7de",
        "portrait": "#24292f",
        "text": "#24292f",
        "muted": "#57606a",
        "label": "#bc4c00",
        "value": "#0969da",
        "positive": "#1a7f37",
    },
}

def github_get(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r

def get_user():
    return github_get(f"https://api.github.com/users/{USERNAME}").json()

def get_repos():
    repos = []
    page = 1
    while True:
        data = github_get(
            f"https://api.github.com/users/{USERNAME}/repos",
            params={
                "per_page": 100,
                "page": page,
                "type": "owner",
                "sort": "updated",
            },
        ).json()
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos

def get_commit_count(repos):
    total = 0
    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue
        try:
            r = github_get(
                f"https://api.github.com/repos/{USERNAME}/{repo['name']}/commits",
                params={"author": USERNAME, "per_page": 1},
            )
            link = r.headers.get("Link", "")
            if 'rel="last"' in link:
                last = [p for p in link.split(",") if 'rel="last"' in p][0]
                page = last.split("page=")[-1].split(">")[0].split("&")[0]
                total += int(page)
            else:
                total += len(r.json())
        except requests.RequestException:
            pass
    return total

def calculate_stats():
    user = get_user()
    repos = get_repos()
    owned = [r for r in repos if not r.get("fork")]
    return {
        "repos": len(owned),
        "stars": sum(r.get("stargazers_count", 0) for r in owned),
        "followers": user.get("followers", 0),
        "commits": get_commit_count(owned),
    }

def esc(value):
    return html.escape(str(value), quote=False)

def font_family():
    return "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, Courier New, monospace"

def txt(x, y, value, color, size=14, weight="normal"):
    return (
        f'<text x="{x}" y="{y}" fill="{color}" '
        f'font-family="{font_family()}" font-size="{size}" '
        f'font-weight="{weight}" xml:space="preserve">{esc(value)}</text>'
    )

def kv(x, y, label, value, theme, size=14):
    return (
        f'<text x="{x}" y="{y}" font-family="{font_family()}" '
        f'font-size="{size}" xml:space="preserve">'
        f'<tspan fill="{theme["label"]}">{esc(label)}</tspan>'
        f'<tspan fill="{theme["value"]}">{esc(value)}</tspan>'
        f'</text>'
    )

def build_svg(mode, stats):
    theme = THEMES[mode]
    art = ASCII_FILE.read_text(encoding="utf-8").splitlines()

    width, height = 1280, 590
    art_x, art_y = 18, 24
    art_font, art_line = 8.7, 9.5

    info_x = 650
    y = 42
    line = 22

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="14" '
        f'fill="{theme["background"]}" stroke="{theme["border"]}" stroke-width="2"/>',
    ]

    # Left: uploaded ASCII exactly as-is
    for i, row in enumerate(art):
        out.append(txt(art_x, art_y + i * art_line, row, theme["portrait"], art_font))

    # Right: fastfetch-style information
    out.append(
        f'<text x="{info_x}" y="{y}" font-family="{font_family()}" font-size="15" xml:space="preserve">'
        f'<tspan fill="{theme["text"]}" font-weight="700">{esc(PROFILE["header"])}</tspan>'
        f'<tspan fill="{theme["muted"]}"> --------------------------------------</tspan>'
        f'</text>'
    )

    for label, key in [
        ("OS: ", "os"),
        ("Role: ", "role"),
        ("Focus: ", "focus"),
        ("Stack: ", "stack"),
    ]:
        y += line
        out.append(kv(info_x, y, label, PROFILE[key], theme))

    y += 30
    out.append(txt(info_x, y, "- Skills -----------------------------------------------", theme["muted"], 14))

    for label, key in [
        ("Infrastructure: ", "infrastructure"),
        ("Network: ", "network"),
        ("Cloud: ", "cloud"),
        ("Automation: ", "automation"),
        ("Security: ", "security"),
    ]:
        y += line
        out.append(kv(info_x, y, label, PROFILE[key], theme))

    y += 30
    out.append(txt(info_x, y, "- GitHub Stats ------------------------------------------", theme["muted"], 14))

    y += line
    out.append(
        f'<text x="{info_x}" y="{y}" font-family="{font_family()}" font-size="14" xml:space="preserve">'
        f'<tspan fill="{theme["label"]}">Repositories: </tspan>'
        f'<tspan fill="{theme["value"]}">{stats["repos"]}</tspan>'
        f'<tspan fill="{theme["muted"]}">     Stars: </tspan>'
        f'<tspan fill="{theme["value"]}">{stats["stars"]}</tspan>'
        f'</text>'
    )

    y += line
    out.append(
        f'<text x="{info_x}" y="{y}" font-family="{font_family()}" font-size="14" xml:space="preserve">'
        f'<tspan fill="{theme["label"]}">Followers: </tspan>'
        f'<tspan fill="{theme["value"]}">{stats["followers"]}</tspan>'
        f'<tspan fill="{theme["muted"]}">        Commits: </tspan>'
        f'<tspan fill="{theme["positive"]}">{stats["commits"]}</tspan>'
        f'</text>'
    )

    y += 34
    out.append(txt(
        info_x, y,
        "Infrastructure should be automated, observable and secure by default.",
        theme["muted"], 12.5
    ))

    out.append("</svg>")
    return "\n".join(out)

def main():
    stats = calculate_stats()
    print("Profile stats:", stats)
    (ROOT / "dark_mode.svg").write_text(build_svg("dark", stats), encoding="utf-8")
    (ROOT / "light_mode.svg").write_text(build_svg("light", stats), encoding="utf-8")

if __name__ == "__main__":
    main()
