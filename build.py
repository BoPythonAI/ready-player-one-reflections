"""Build the static reading page and the GitHub README from article.md."""

from html import escape
from pathlib import Path


ROOT = Path(__file__).parent
source = (ROOT / "article.md").read_text(encoding="utf-8")
title_line, *rest = source.strip().split("\n", 1)
title = title_line.removeprefix("# ")
body = rest[0].strip() if rest else ""
paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
letters = "".join(f'<span aria-hidden="true">{escape(char)}</span>' for char in title)
article_html = "\n".join(f"      <p>{escape(part)}</p>" for part in paragraphs)

index = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#08142c">
  <meta name="description" content="{escape(paragraphs[1], quote=True)}">
  <title>{escape(title)} | BoPythonAI</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <figure class="hero">
      <img src="assets/ready-player-one.png" alt="以《头号玩家》为灵感的未来虚拟世界画面" width="1671" height="943" fetchpriority="high">
    </figure>
    <header class="article-header">
      <p class="eyebrow">READY PLAYER ONE · A REFLECTION</p>
      <h1 aria-label="{escape(title, quote=True)}">{letters}</h1>
      <p class="intro">从电影中的 OASIS，想到今天的三维重建、物理仿真与具身智能。</p>
    </header>
    <article class="essay" aria-label="{escape(title, quote=True)}">
{article_html}
    </article>
    <footer>
      <span>BoPythonAI</span>
      <a href="https://github.com/BoPythonAI/ready-player-one-reflections">在 GitHub 阅读</a>
    </footer>
  </main>
</body>
</html>
'''
(ROOT / "index.html").write_text(index, encoding="utf-8")

spacing = 120
start_x = 28
svg_chars = "\n".join(
    f'  <text x="{start_x + i * spacing}" y="128" fill="url(#rainbow)" '
    f'font-family="Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif" '
    f'font-size="112" font-weight="900">{escape(char)}</text>'
    for i, char in enumerate(title)
)
svg_width = start_x * 2 + spacing * len(title)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="164" viewBox="0 0 {svg_width} 164" role="img" aria-label="{escape(title, quote=True)}">
  <defs>
    <linearGradient id="rainbow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f53634"/>
      <stop offset="20%" stop-color="#ff922d"/>
      <stop offset="39%" stop-color="#ffe732"/>
      <stop offset="58%" stop-color="#51e753"/>
      <stop offset="78%" stop-color="#02d8e4"/>
      <stop offset="100%" stop-color="#3654f5"/>
    </linearGradient>
  </defs>
{svg_chars}
</svg>
'''
(ROOT / "assets" / "rainbow-title.svg").write_text(svg, encoding="utf-8")

readme = f'''<p align="center"><img src="assets/rainbow-title.svg" alt="{title}" width="880"></p>

<p align="center"><a href="https://bopythonai.github.io/ready-player-one-reflections/">打开沉浸式阅读页面</a></p>

![以《头号玩家》为灵感的未来虚拟世界画面](assets/ready-player-one.png)

{body}
'''
(ROOT / "README.md").write_text(readme, encoding="utf-8")
print(f"Built index.html, README.md and assets/rainbow-title.svg ({len(paragraphs)} paragraphs).")
