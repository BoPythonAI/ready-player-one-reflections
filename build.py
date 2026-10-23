"""Build the static reading page and the GitHub README from article.md."""

from html import escape
from hashlib import sha256
from pathlib import Path
import re


ROOT = Path(__file__).parent
TERMS = (
    "Humanoid / Creature Control", "环境理解与自主决策", "仿真与机器人学习环境",
    "生成式内容创作", "生成式人工智能", "三维场景表示", "角色运动与控制",
    "Reinforcement Learning", "Gaussian Splatting", "Hyperscape Capture",
    "Diffusion Models", "NVIDIA Isaac Sim", "Meta VR Glasses", "Horizon Worlds",
    "Motion Tracking", "Task Planning", "计算机图形学", "物理世界建模",
    "强化学习框架", "计算机视觉", "Meta Quest", "Orion AR", "Isaac Lab",
    "SAM 3D", "V-JEPA", "三维重建", "物理仿真", "运动控制", "具身智能",
    "三维理解", "强化学习", "人工智能", "生成模型", "物理引擎", "人体运动",
    "数字人", "元宇宙", "机器人学", "三维环境", "虚拟社交平台",
    "PhysX", "MuJoCo", "Mesh", "3DGS", "NeRF", "VLM", "VLA", "GPT",
    "3D建模", "3D角色", "推荐算法",
)
TERM_PATTERN = re.compile("|".join(re.escape(term) for term in sorted(TERMS, key=len, reverse=True)))
TERMS_DIR = ROOT / "assets" / "terms"
TERMS_DIR.mkdir(parents=True, exist_ok=True)


def term_asset(term: str) -> str:
    """Create a readable lavender SVG for GitHub's restricted Markdown renderer."""
    name = sha256(term.encode("utf-8")).hexdigest()[:12] + ".svg"
    path = TERMS_DIR / name
    def char_width(char: str) -> int:
        if ord(char) > 0x2E80:
            return 22
        if char == " ":
            return 7
        if char in "ilI1/.-":
            return 7
        if char in "MWmw":
            return 18
        return 12

    width = sum(char_width(char) for char in term) + (
        17 if any(char.isascii() and char.isalpha() for char in term) else 6
    )
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="27" '
        f'viewBox="0 0 {width} 27" role="img" aria-label="{escape(term, quote=True)}">'
        '<style>text{fill:#895cb8}@media(prefers-color-scheme:dark){text{fill:#d4b5f8}}</style>'
        f'<text x="2" y="21" font-family="Arial, Microsoft YaHei, PingFang SC, '
        f'Noto Sans CJK SC, sans-serif" font-size="21" font-weight="600">{escape(term)}</text>'
        '</svg>\n',
        encoding="utf-8",
    )
    return f"assets/terms/{name}"


def highlight(text: str, for_readme: bool = False) -> str:
    chunks = []
    last = 0
    for match in TERM_PATTERN.finditer(text):
        chunks.append(escape(text[last:match.start()]))
        term = match.group()
        if for_readme:
            chunks.append(
                f'<img src="{term_asset(term)}" alt="{escape(term, quote=True)}" height="21">'
            )
        else:
            chunks.append(f'<span class="technical-term">{escape(term)}</span>')
        last = match.end()
    chunks.append(escape(text[last:]))
    return "".join(chunks)


source = (ROOT / "article.md").read_text(encoding="utf-8")
title_line, *rest = source.strip().split("\n", 1)
title = title_line.removeprefix("# ")
body = rest[0].strip() if rest else ""
paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
letters = "".join(f'<span aria-hidden="true">{escape(char)}</span>' for char in title)
article_html = "\n".join(f"      <p>{highlight(part)}</p>" for part in paragraphs)

index = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#08142c">
  <meta name="description" content="{escape(paragraphs[1], quote=True)}">
  <title>{escape(title)} | BoPythonAI</title>
  <link rel="stylesheet" href="style.css">
  <link rel="preload" href="assets/decorative-plush-horse-poster.webp" as="image" type="image/webp">
  <link rel="preload" href="assets/monkey-king-poster.webp" as="image" type="image/webp">
  <link rel="preload" href="assets/tang-sanzang-poster.webp" as="image" type="image/webp">
  <link rel="preload" href="assets/decorative-plush-horse-optimized.glb" as="fetch" type="model/gltf-binary" crossorigin>
  <link rel="preload" href="assets/monkey-king-home.glb" as="fetch" type="model/gltf-binary" crossorigin>
  <link rel="preload" href="assets/tang-sanzang-home.glb" as="fetch" type="model/gltf-binary" crossorigin>
  <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.4.0/model-viewer.min.js"></script>
</head>
<body>
  <main>
    <figure class="hero">
      <img src="assets/ready-player-one.png" alt="以《头号玩家》为灵感的未来虚拟世界画面" width="1671" height="943" loading="lazy">
    </figure>
    <header class="article-header">
      <p class="eyebrow">READY PLAYER ONE · A REFLECTION</p>
      <h1 aria-label="{escape(title, quote=True)}">{letters}</h1>
      <p class="intro">从电影中的 OASIS，想到今天的<span class="technical-term">三维重建</span>、<span class="technical-term">物理仿真</span>与<span class="technical-term">具身智能</span>。</p>
    </header>
    <section id="model" class="model-gallery" aria-label="可交互的 3D 模型">
      <figure class="model-card">
        <model-viewer src="assets/decorative-plush-horse-optimized.glb" poster="assets/decorative-plush-horse-poster.webp" alt="可旋转的彩色毛绒马三维模型" loading="eager" camera-controls camera-orbit="30deg 75deg auto" interaction-prompt="none" touch-action="pan-y" shadow-intensity="0.8" exposure="1.1"></model-viewer>
        <figcaption><strong>毛绒马</strong><span>拖动旋转 · 滚轮缩放</span><a href="normal-view.html">查看法线视图</a></figcaption>
      </figure>
      <figure class="model-card">
        <model-viewer src="assets/monkey-king-home.glb" poster="assets/monkey-king-poster.webp" alt="可旋转的彩色孙悟空三维模型" loading="eager" camera-controls camera-orbit="25deg 75deg auto" interaction-prompt="none" touch-action="pan-y" shadow-intensity="0.8" exposure="1.1"></model-viewer>
        <figcaption><strong>孙悟空</strong><span>拖动旋转 · 滚轮缩放</span><a href="monkey-king.html">原版与法线视图</a></figcaption>
      </figure>
      <figure class="model-card">
        <model-viewer src="assets/tang-sanzang-home.glb" poster="assets/tang-sanzang-poster.webp" alt="可旋转的彩色唐三藏三维模型" loading="eager" camera-controls camera-orbit="25deg 75deg auto" interaction-prompt="none" touch-action="pan-y" shadow-intensity="0.8" exposure="1.1"></model-viewer>
        <figcaption><strong>唐三藏</strong><span>拖动旋转 · 滚轮缩放</span><a href="tang-sanzang.html">原版与法线视图</a></figcaption>
      </figure>
    </section>
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

readme_body = "\n\n".join(highlight(part, for_readme=True) for part in paragraphs)
readme = f'''<p align="center"><img src="assets/rainbow-title.svg" alt="{title}" width="880"></p>

<p align="center"><a href="https://bopythonai.github.io/ready-player-one-reflections/">打开沉浸式阅读页面</a></p>

![以《头号玩家》为灵感的未来虚拟世界画面](assets/ready-player-one.png)

<p align="center"><a href="https://bopythonai.github.io/ready-player-one-reflections/3d-assets.html">3D资产</a></p>

{readme_body}
'''
(ROOT / "README.md").write_text(readme, encoding="utf-8")
print(f"Built index.html, README.md and assets/rainbow-title.svg ({len(paragraphs)} paragraphs).")
