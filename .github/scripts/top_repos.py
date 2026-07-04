#!/usr/bin/env python3
"""自动生成「top repos by star」榜，写进 README.md 的 <!--TOP:START--> / <!--TOP:END--> 之间。
排除 fork、archived、profile 仓库本身，以及 DENYLIST（永久隐藏，如研究/私密项目）。"""
import os, re, json, urllib.request

USER = "Chasingwind-Z"
TOP_N = 3
DENYLIST = {"Pictures"}  # 永久不展示的仓库名（Pictures=图床基础设施；研究/私密项目也放这里）

tok = os.environ.get("GH_TOKEN", "")
req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&sort=updated",
    headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"},
)
repos = json.load(urllib.request.urlopen(req))

repos = [
    r for r in repos
    if not r["fork"] and not r["archived"]
    and r["name"] not in DENYLIST
    and r["name"].lower() != USER.lower()
]
repos.sort(key=lambda r: (r["stargazers_count"], r["updated_at"]), reverse=True)

lines = []
for r in repos[:TOP_N]:
    desc = (r["description"] or "").strip()
    star = r["stargazers_count"]
    lang = r["language"] or ""
    tail = f" — {desc}" if desc else ""
    meta = f" `{lang}`" if lang else ""
    lines.append(f'- **[{r["name"]}]({r["html_url"]})** · ⭐ {star}{meta}{tail}')
block = "\n".join(lines) if lines else "_（暂无公开仓库）_"

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
new = re.sub(
    r"<!--TOP:START-->.*?<!--TOP:END-->",
    "<!--TOP:START-->\n" + block + "\n<!--TOP:END-->",
    readme,
    flags=re.S,
)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(new)
print("top repos updated:\n" + block)
