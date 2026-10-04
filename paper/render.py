"""Turn a day's ``edition.json`` into the printed paper: HTML, then PDF, plus PNG previews."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from . import profile as prof
from .avatar import avatar_svg
from .browser import chromium
from .comic import strip_html
from .privacy import scrub_edition
from .scenes import normalise_kind, weather_icon

PKG = Path(__file__).resolve().parent
TEMPLATES = PKG / "templates"
FONTS = PKG / "fonts"
BUILD = prof.ROOT / "build"
EDITIONS = prof.ROOT / "editions"

FONT_FACES = [
    ("UnifrakturMaguntia", 400, "normal", "UnifrakturMaguntia-400.ttf"),
    ("Playfair Display", 700, "normal", "PlayfairDisplay-700.ttf"),
    ("Playfair Display", 900, "normal", "PlayfairDisplay-900.ttf"),
    ("Playfair Display", 700, "italic", "PlayfairDisplay-700i.ttf"),
    ("Source Serif 4", 400, "normal", "SourceSerif4-400.ttf"),
    ("Source Serif 4", 400, "italic", "SourceSerif4-400i.ttf"),
    ("Source Serif 4", 600, "normal", "SourceSerif4-600.ttf"),
    ("Source Serif 4", 700, "normal", "SourceSerif4-700.ttf"),
    ("Oswald", 500, "normal", "Oswald-500.ttf"),
    ("Oswald", 600, "normal", "Oswald-600.ttf"),
    ("Patrick Hand", 400, "normal", "PatrickHand-400.ttf"),
]

# Finds text boxes that overflow (too long) or are mostly empty (too short).
FIT_JS = """
() => Array.from(document.querySelectorAll('[data-fit]')).map(el => {
  const words = (el.innerText || '').trim().split(/\\s+/).filter(Boolean).length;
  const dy = el.scrollHeight - el.clientHeight, dx = el.scrollWidth - el.clientWidth;
  if (dy > 2 || dx > 2) {
    const frac = Math.max(dy > 2 ? dy / el.scrollHeight : 0, dx > 2 ? dx / el.scrollWidth : 0);
    return {box: el.dataset.fit, problem: 'too long', words, change: Math.max(5, Math.ceil(words * frac * 1.15))};
  }
  const cols = parseInt(getComputedStyle(el).columnCount) || 1;
  const grows = cols > 1 || el.classList.contains('grow');
  if (!grows) return null;
  let used = 0;
  for (const child of el.children) for (const r of child.getClientRects()) used += r.height;
  const fill = used / (el.clientHeight * cols);
  if (fill < 0.8 && words > 0) {
    return {box: el.dataset.fit, problem: 'too short', words, change: Math.ceil(words * (1 / Math.max(fill, .2) - 1) * 0.8)};
  }
  return null;
}).filter(Boolean)
"""


@dataclass
class Result:
    pdf: Path
    html: Path
    previews: list[Path] = field(default_factory=list)
    fit: list[dict] = field(default_factory=list)
    pages: int = 0

    @property
    def overflow(self) -> list[dict]:
        return [f for f in self.fit if f["problem"] == "too long"]


def fonts_css(embed: bool = False) -> str:
    rules = []
    for family, weight, style, file in FONT_FACES:
        path = FONTS / file
        if embed:
            src = "data:font/ttf;base64," + base64.b64encode(path.read_bytes()).decode()
        else:
            src = path.as_uri()
        rules.append(f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
                     f"src:url('{src}') format('truetype');font-display:block}}")
    return "\n".join(rules)


def _temp(value) -> str:
    if value is None or value == "":
        return "–"
    if isinstance(value, (int, float)):
        return f"{round(value)}°"
    text = str(value).strip()
    return text if text.endswith("°") or "°" in text else f"{text}°"


def _paras(body) -> list[str]:
    if not body:
        return []
    if isinstance(body, str):
        return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    return [str(p).strip() for p in body if str(p).strip()]


def _icon(kind) -> Markup:
    return Markup(weather_icon(normalise_kind(kind)))


def _weather(raw: dict | None) -> dict | None:
    if not raw:
        return None
    wx = dict(raw)
    wx["kind"] = normalise_kind(wx.get("kind"))
    wx.setdefault("rain_chance", None)
    wx["outlook"] = [dict(o, kind=normalise_kind(o.get("kind"))) for o in wx.get("outlook") or []]
    return wx


def build_context(profile: dict, edition: dict, embed_fonts: bool = False) -> dict:
    ed = scrub_edition(edition, profile)
    day = date.fromisoformat(ed["date"])
    name, reader, city = prof.paper_name(profile), prof.reader(profile), prof.city(profile)
    wx = _weather(ed.get("weather"))
    comic = ed.get("comic") or {}
    panels = comic.get("panels") or []
    look = profile.get("avatar") or {}
    inbox = ed.get("inbox") or {}
    local = (ed.get("local") or {}).get("items") or []
    extras = {k: v for k, v in (ed.get("extras") or {}).items() if v}
    sections = [s for s in ed.get("sections") or [] if s.get("stories")][:3]

    if panels:
        ear_right = f"{comic.get('title') or 'Today’s comic'}, starring you. Page 2."
    else:
        ear_right = "Your newsletters, local news and more on page 2."

    sun_line = f"{city} · {day.strftime('%A')}"
    if wx and wx.get("sunrise") and wx.get("sunset"):
        sun_line = f"Sunrise {wx['sunrise']} · Sunset {wx['sunset']}"

    sources = ed.get("sources")
    if not sources:
        seen = []
        for s in sections:
            for st in s["stories"]:
                if st.get("source") and st["source"] not in seen:
                    seen.append(st["source"])
        sources = seen
    if isinstance(sources, list):
        sources = ", ".join(sources)

    names = [n.get("from") for n in inbox.get("newsletters") or [] if n.get("from")]
    face = (f'<svg viewBox="26 -6 148 176" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            f'{avatar_svg(look, "happy")}</svg>')

    return {
        "fonts_css": Markup(fonts_css(embed_fonts)),
        "css": Markup((TEMPLATES / "paper.css").read_text()),
        "paper_name": name,
        "reader": reader,
        "city": city,
        "tagline": profile.get("tagline") or f"Printed fresh for {reader} every morning",
        "date_long": f"{day.strftime('%A')} {day.day} {day.strftime('%B %Y')}",
        "day_name": day.strftime("%A"),
        "edition_no": prof.edition_number(profile, day),
        "volume": prof.volume(profile, day),
        "topics": " · ".join(s["name"] for s in sections) or "Your daily paper",
        "sun_line": sun_line,
        "wx": wx,
        "lead": ed.get("lead") or {"headline": "Good morning"},
        "day": ed.get("your_day") or {},
        "sections": sections,
        "inbox": inbox,
        "newsletter_names": ", ".join(names),
        "local": local,
        "more_title": (ed.get("more") or {}).get("title") or "More to read",
        "more_items": (ed.get("more") or {}).get("items") or [],
        "comic": comic,
        "comic_html": Markup(strip_html(comic, look, wx["kind"] if wx else "partly-cloudy")) if panels else "",
        "n_panels": min(len(panels), 4),
        "extras": extras,
        "sources": sources,
        "ear_right": ear_right,
        "face": Markup(face),
        "icon": _icon,
        "temp": _temp,
        "paras": _paras,
    }


def render_html(profile: dict, edition: dict, embed_fonts: bool = False) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["j2", "html"]))
    return env.get_template("paper.html.j2").render(**build_context(profile, edition, embed_fonts))


def render(profile: dict, edition: dict, *, out_dir: Path | None = None, build_dir: Path | None = None,
           previews: bool = True) -> Result:
    day = edition["date"]
    build_dir = Path(build_dir or BUILD / day).resolve()
    out_dir = Path(out_dir or EDITIONS).resolve()
    build_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    html_path = build_dir / "paper.html"
    html_path.write_text(render_html(profile, edition))
    pdf_path = out_dir / f"{prof.slug(profile)}-{day}.pdf"
    result = Result(pdf=pdf_path, html=html_path)

    with chromium() as browser:
        page = browser.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=1.6)
        page.goto(html_path.as_uri(), wait_until="load")
        page.wait_for_function("document.body.dataset.ready === '1'", timeout=20000)
        result.fit = page.evaluate(FIT_JS)
        page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
        if previews:
            for i, sheet in enumerate(page.locator(".page").all(), start=1):
                png = build_dir / f"page-{i}.png"
                sheet.screenshot(path=str(png))
                result.previews.append(png)

    result.pages = len(re.findall(rb"/Type\s*/Page(?!s)", pdf_path.read_bytes()))
    return result
