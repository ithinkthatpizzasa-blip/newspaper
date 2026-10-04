"""The daily comic strip: turns a short panel script into HTML panels starring the reader.

A panel script looks like::

    {"scene": "bedroom", "mood": "sleepy", "pose": "center", "prop": "phone",
     "caption": "7:02am", "speech": "Five more minutes...", "thought": false, "sfx": "BEEP!"}

Only ``scene`` and ``mood`` matter for the drawing; everything else is optional.
"""

from __future__ import annotations

import re
from html import escape

from . import scenes
from .avatar import MOODS, PROPS, avatar_svg, prop_svg

POSES = {"left": 6, "center": 57, "right": 108}
AVATAR_Y, AVATAR_SCALE = 86, 0.93
TAIL = ('<svg class="tail" viewBox="0 -3 24 21" aria-hidden="true">'
        '<path d="M2 -3 L15 -3 L22 17 Z" fill="#fff"/>'
        '<path d="M2 -0.5 L22 17 L15 -0.5" fill="none" stroke="#141414" stroke-width="1.7" '
        'stroke-linejoin="round"/></svg>')
THOUGHT_TAIL = ('<svg class="tail thought-tail" viewBox="0 0 24 22" aria-hidden="true">'
                '<circle cx="8" cy="6" r="4.5" fill="#fff" stroke="#141414" stroke-width="1.6"/>'
                '<circle cx="17" cy="16" r="3" fill="#fff" stroke="#141414" stroke-width="1.6"/></svg>')


def _unique_ids(svg: str, suffix: str) -> str:
    """Several panels share one HTML page, so make clipPath/pattern ids unique per panel."""
    ids = set(re.findall(r'id="([^"]+)"', svg))
    for i in ids:
        svg = svg.replace(f'id="{i}"', f'id="{i}-{suffix}"').replace(f"url(#{i})", f"url(#{i}-{suffix})")
    return svg


def _sfx(text: str, pose: str) -> str:
    text = text.strip()[:14]
    if not text:
        return ""
    x, y = (242, 188) if pose == "left" else (56, 190)
    size = max(15, min(30, 190 / max(len(text), 1)))
    return (f'<text x="{x}" y="{y}" text-anchor="middle" transform="rotate(-10 {x} {y})" '
            f'font-family="Oswald, sans-serif" font-weight="600" font-size="{size:.1f}" letter-spacing="1" '
            f'fill="#ffd84d" stroke="#141414" stroke-width="2.2" paint-order="stroke" '
            f'stroke-linejoin="round">{escape(text)}</text>')


def panel_html(panel: dict, look: dict | None, weather: str = "partly-cloudy", index: int = 0) -> str:
    pose = panel.get("pose") if panel.get("pose") in POSES else "center"
    mood = panel.get("mood") if panel.get("mood") in MOODS else "happy"
    prop = panel.get("prop") if panel.get("prop") in PROPS else None
    back, front = scenes.draw(panel.get("scene", "plain"), panel.get("weather") or weather)
    if pose == "left":
        back = f'<g transform="matrix(-1 0 0 1 300 0)">{back}</g>'
        front = f'<g transform="matrix(-1 0 0 1 300 0)">{front}</g>' if front else ""
    place = f'translate({POSES[pose]} {AVATAR_Y}) scale({AVATAR_SCALE})'
    figure = f'<g transform="{place}">{avatar_svg(look, mood)}</g>'
    held = f'<g transform="{place}">{prop_svg(look, prop)}</g>' if prop else ""
    art = _unique_ids(
        f'<svg class="art" viewBox="0 0 300 300" preserveAspectRatio="xMidYMid slice" '
        f'xmlns="http://www.w3.org/2000/svg">{back}{figure}{front}{held}'
        f'{_sfx(panel.get("sfx", ""), pose)}</svg>',
        f"p{index}",
    )

    caption = (panel.get("caption") or "").strip()
    speech = (panel.get("speech") or "").strip()
    side = "right" if pose == "left" else "left"
    classes = ["panel"]
    html = [art]
    if caption:
        classes.append("has-caption")
        html.append(f'<div class="caption">{escape(caption)}</div>')
    if speech:
        kind = "thought" if panel.get("thought") else "speech"
        tail = THOUGHT_TAIL if kind == "thought" else TAIL
        html.append(f'<div class="bubble {kind} {side}">{escape(speech)}{tail}</div>')
    return f'<div class="{" ".join(classes)}">{"".join(html)}</div>'


def strip_html(comic: dict, look: dict | None, weather: str = "partly-cloudy") -> str:
    panels = comic.get("panels") or []
    return "".join(panel_html(p, look, weather, i) for i, p in enumerate(panels[:4]))
