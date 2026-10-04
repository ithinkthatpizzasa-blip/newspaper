"""Comic panel backgrounds and weather, drawn as SVG on a 300 x 300 canvas.

Each scene returns ``(back, front)``: ``back`` is drawn behind the avatar and
``front`` in front of it (blankets, desks, counters). Scenes are drawn with
their window or sky feature on the right; ``comic.py`` mirrors them when the
avatar stands on the left. Scenes contain no text so mirroring is safe.
"""

from __future__ import annotations

import math
import random

LINE = "#4a4a4a"
WALL = "#f4f1ea"
LIGHT = "#e7e2d8"
MID = "#cfc8bb"
DARK = "#3b3b3b"
SKY_NIGHT = "#2f3445"

WEATHER_KINDS = (
    "clear", "partly-cloudy", "cloudy", "fog", "drizzle", "rain", "showers",
    "heavy-rain", "thunder", "snow", "windy", "night",
)


def _l(extra: str = "", width: float = 2, colour: str = LINE) -> str:
    return f'fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round" {extra}'


# --------------------------------------------------------------------------- weather bits

def sun(cx: float, cy: float, r: float) -> str:
    rays = []
    for i in range(10):
        a = i * math.pi / 5
        x1, y1 = cx + math.cos(a) * (r + 5), cy + math.sin(a) * (r + 5)
        x2, y2 = cx + math.cos(a) * (r + 13), cy + math.sin(a) * (r + 13)
        rays.append(f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}")
    return (f'<path d="{" ".join(rays)}" stroke="#d9a400" stroke-width="3" stroke-linecap="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffd84d" stroke="#b58900" stroke-width="2.4"/>')


def cloud(x: float, y: float, s: float = 1, fill: str = "#ffffff", stroke: str = LINE) -> str:
    """A cloud whose flat base starts at (x, y) and is ~80*s wide."""
    d = (f"M{x} {y} C{x - 14 * s} {y} {x - 14 * s} {y - 22 * s} {x + 4 * s} {y - 20 * s} "
         f"C{x + 6 * s} {y - 38 * s} {x + 34 * s} {y - 40 * s} {x + 40 * s} {y - 24 * s} "
         f"C{x + 48 * s} {y - 34 * s} {x + 72 * s} {y - 30 * s} {x + 70 * s} {y - 14 * s} "
         f"C{x + 86 * s} {y - 12 * s} {x + 86 * s} {y} {x + 70 * s} {y} Z")
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="2.4" stroke-linejoin="round"/>'


def rain(x: float, y: float, w: float, h: float, heavy: bool = False, seed: int = 3) -> str:
    rnd = random.Random(seed)
    n = int(w * h / (260 if heavy else 520))
    drops = []
    for _ in range(max(n, 4)):
        px, py = x + rnd.random() * w, y + rnd.random() * h
        drops.append(f"M{px:.1f} {py:.1f} l-4 {11 if heavy else 8}")
    return f'<path d="{" ".join(drops)}" stroke="#5b8fc9" stroke-width="{2.4 if heavy else 2}" stroke-linecap="round"/>'


def snow(x: float, y: float, w: float, h: float, seed: int = 5) -> str:
    rnd = random.Random(seed)
    flakes = []
    for _ in range(max(int(w * h / 600), 4)):
        px, py = x + rnd.random() * w, y + rnd.random() * h
        flakes.append(f"M{px - 4:.1f} {py:.1f} l8 0 M{px:.1f} {py - 4:.1f} l0 8 "
                      f"M{px - 3:.1f} {py - 3:.1f} l6 6 M{px + 3:.1f} {py - 3:.1f} l-6 6")
    return f'<path d="{" ".join(flakes)}" stroke="#7aa6d6" stroke-width="1.6" stroke-linecap="round"/>'


def bolt(x: float, y: float, s: float = 1) -> str:
    d = (f"M{x} {y} L{x - 10 * s} {y + 22 * s} L{x - 2 * s} {y + 22 * s} L{x - 8 * s} {y + 42 * s} "
         f"L{x + 10 * s} {y + 14 * s} L{x + 2 * s} {y + 14 * s} L{x + 8 * s} {y} Z")
    return f'<path d="{d}" fill="#ffd84d" stroke="#8a6d00" stroke-width="2" stroke-linejoin="round"/>'


def moon(cx: float, cy: float, r: float) -> str:
    return (f'<path d="M{cx + r * 0.2} {cy - r} A{r} {r} 0 1 0 {cx + r * 0.2} {cy + r} '
            f'A{r * 0.78} {r * 0.78} 0 1 1 {cx + r * 0.2} {cy - r} Z" fill="#fff6c9" '
            f'stroke="#b8a65a" stroke-width="2"/>')


def stars(x: float, y: float, w: float, h: float, n: int = 7, seed: int = 9) -> str:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        px, py, s = x + rnd.random() * w, y + rnd.random() * h, 2.5 + rnd.random() * 3
        out.append(f"M{px:.1f} {py - s:.1f} L{px + s * 0.3:.1f} {py:.1f} L{px:.1f} {py + s:.1f} "
                   f"L{px - s * 0.3:.1f} {py:.1f} Z M{px - s:.1f} {py:.1f} L{px:.1f} {py - s * 0.3:.1f} "
                   f"L{px + s:.1f} {py:.1f} L{px:.1f} {py + s * 0.3:.1f} Z")
    return f'<path d="{" ".join(out)}" fill="#fff6c9"/>'


def fog(x: float, y: float, w: float, h: float) -> str:
    lines = []
    for i in range(4):
        yy = y + h * (0.2 + i * 0.2)
        lines.append(f"M{x + (i % 2) * 10} {yy:.1f} q{w / 8:.1f} -6 {w / 4:.1f} 0 t{w / 4:.1f} 0 t{w / 4:.1f} 0")
    return f'<path d="{" ".join(lines)}" {_l(width=3)} opacity="0.55"/>'


def wind(x: float, y: float, w: float) -> str:
    return (f'<path d="M{x} {y} L{x + w * 0.7} {y} q14 0 14 -10 q0 -9 -9 -9 q-8 0 -8 8 '
            f'M{x + 10} {y + 14} L{x + w} {y + 14} q12 0 12 9 q0 8 -8 8 '
            f'M{x - 6} {y + 28} L{x + w * 0.55} {y + 28}" {_l(width=2.6)}/>')


def weather_art(kind: str, x: float, y: float, w: float, h: float) -> str:
    """Weather drawn into a sky box (x, y, w, h)."""
    s = min(w, h) / 100
    cx, cy = x + w * 0.62, y + h * 0.36
    if kind == "clear":
        return sun(cx, cy, 15 * s + 4)
    if kind == "partly-cloudy":
        return sun(cx + 10 * s, cy - 6 * s, 13 * s + 3) + cloud(x + w * 0.18, y + h * 0.7, s * 0.95)
    if kind == "cloudy":
        return cloud(x + w * 0.42, y + h * 0.42, s * 0.8, "#f0f0f0") + cloud(x + w * 0.12, y + h * 0.72, s)
    if kind == "fog":
        return cloud(x + w * 0.3, y + h * 0.45, s * 0.8, "#f0f0f0") + fog(x, y + h * 0.4, w, h * 0.6)
    if kind in ("drizzle", "rain", "showers"):
        sky = sun(cx + 16 * s, cy - 10 * s, 11 * s + 2) if kind == "showers" else ""
        return sky + cloud(x + w * 0.15, y + h * 0.5, s, "#e9edf2") + rain(
            x + w * 0.1, y + h * 0.55, w * 0.8, h * 0.45, seed=int(x + y))
    if kind in ("heavy-rain", "thunder"):
        out = cloud(x + w * 0.15, y + h * 0.5, s, "#b9bec7", "#3d4350")
        out += rain(x + w * 0.05, y + h * 0.52, w * 0.9, h * 0.48, heavy=True, seed=int(x + y))
        if kind == "thunder":
            out += bolt(x + w * 0.55, y + h * 0.42, s * 0.9)
        return out
    if kind == "snow":
        return cloud(x + w * 0.15, y + h * 0.5, s, "#f4f6f9") + snow(x + w * 0.05, y + h * 0.55, w * 0.9, h * 0.45)
    if kind == "windy":
        return cloud(x + w * 0.4, y + h * 0.35, s * 0.7) + wind(x + w * 0.1, y + h * 0.55, w * 0.6)
    if kind == "night":
        return moon(cx, cy, 13 * s + 3) + stars(x + 4, y + 4, w - 8, h - 8)
    return ""


def window(x: float, y: float, w: float, h: float, weather: str, night: bool = False,
           curtains: bool = True) -> str:
    sky = SKY_NIGHT if night or weather == "night" else "#eaf3fb"
    art = weather_art("night" if night else weather, x + 4, y + 4, w - 8, h - 8)
    clip = f"win{int(x)}{int(y)}"
    out = (f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{sky}"/>'
           f'<g clip-path="url(#{clip})">{art}</g>'
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {_l(width=4, colour="#6b6458")}/>'
           f'<path d="M{x + w / 2} {y} L{x + w / 2} {y + h} M{x} {y + h / 2} L{x + w} {y + h / 2}" '
           f'stroke="#6b6458" stroke-width="3"/>'
           f'<rect x="{x - 6}" y="{y + h}" width="{w + 12}" height="6" fill="{LIGHT}" stroke="#6b6458" stroke-width="2"/>')
    if curtains:
        out += (f'<path d="M{x - 10} {y - 8} L{x + 10} {y - 8} Q{x + 4} {y + h * 0.5} {x + 12} {y + h + 4} '
                f'L{x - 10} {y + h + 4} Z" fill="#d8cdb5" stroke="{LINE}" stroke-width="1.6"/>'
                f'<path d="M{x + w + 10} {y - 8} L{x + w - 10} {y - 8} Q{x + w - 4} {y + h * 0.5} '
                f'{x + w - 12} {y + h + 4} L{x + w + 10} {y + h + 4} Z" fill="#d8cdb5" stroke="{LINE}" '
                f'stroke-width="1.6"/>'
                f'<path d="M{x - 14} {y - 9} L{x + w + 14} {y - 9}" stroke="#6b6458" stroke-width="3"/>')
    return out


def weather_icon(kind: str) -> str:
    """A square weather symbol for the paper's forecast boxes (100 x 100 viewBox)."""
    if kind == "clear":
        art = sun(50, 50, 21)
    elif kind == "partly-cloudy":
        art = sun(62, 38, 17) + cloud(14, 82, 0.95)
    elif kind == "cloudy":
        art = cloud(36, 56, 0.72, "#f0f0f0") + cloud(14, 84, 0.95)
    elif kind == "fog":
        art = cloud(20, 52, 0.85, "#f0f0f0") + fog(4, 52, 92, 48)
    elif kind in ("drizzle", "rain", "showers"):
        art = (sun(70, 26, 14) if kind == "showers" else "") + cloud(14, 62, 0.95, "#e9edf2") + rain(
            14, 66, 70, 30, seed=7)
    elif kind in ("heavy-rain", "thunder"):
        art = cloud(14, 60, 0.95, "#b9bec7", "#3d4350") + rain(8, 62, 84, 34, heavy=True, seed=7)
        if kind == "thunder":
            art += bolt(52, 52, 0.85)
    elif kind == "snow":
        art = cloud(14, 62, 0.95, "#f4f6f9") + snow(12, 66, 76, 30)
    elif kind == "windy":
        art = cloud(36, 40, 0.6) + wind(14, 58, 60)
    elif kind == "night":
        art = moon(48, 50, 22) + stars(6, 6, 88, 88, n=5)
    else:
        art = cloud(14, 70, 0.95)
    return f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{art}</svg>'


KIND_ALIASES = {
    "sunny": "clear", "sun": "clear", "fine": "clear", "clear-sky": "clear", "mostly-sunny": "clear",
    "partly-sunny": "partly-cloudy", "sunny-intervals": "partly-cloudy", "sunny-spells": "partly-cloudy",
    "bright-spells": "partly-cloudy", "mostly-cloudy": "cloudy", "overcast": "cloudy", "grey": "cloudy",
    "mist": "fog", "misty": "fog", "foggy": "fog", "light-rain": "drizzle", "rainy": "rain",
    "shower": "showers", "light-showers": "showers", "heavy-showers": "heavy-rain", "downpour": "heavy-rain",
    "storm": "thunder", "stormy": "thunder", "thunderstorm": "thunder", "thunderstorms": "thunder",
    "sleet": "snow", "snowy": "snow", "hail": "heavy-rain", "wind": "windy", "breezy": "windy",
    "gales": "windy", "clear-night": "night",
}


def normalise_kind(kind: str | None) -> str:
    key = str(kind or "partly-cloudy").strip().lower().replace(" ", "-").replace("_", "-")
    key = KIND_ALIASES.get(key, key)
    return key if key in WEATHER_KINDS else "partly-cloudy"


def sky_box(weather: str) -> str:
    night = weather == "night"
    bg = SKY_NIGHT if night else ("#dfe3e8" if weather in ("heavy-rain", "thunder", "fog") else "#eef6fc")
    return f'<rect x="0" y="0" width="300" height="300" fill="{bg}"/>' + weather_art(weather, 168, 8, 124, 108)


# --------------------------------------------------------------------------- scenes

def bedroom(weather: str, night: bool = False):
    back = (f'<rect width="300" height="300" fill="{WALL}"/>'
            f'<rect y="236" width="300" height="64" fill="{LIGHT}"/>'
            + window(196, 22, 82, 80, weather, night)
            + f'<rect x="28" y="160" width="244" height="110" rx="26" fill="#d9cdb6" stroke="{LINE}" stroke-width="2.4"/>'
            f'<rect x="44" y="176" width="212" height="80" rx="18" fill="none" stroke="{LINE}" stroke-width="1.4" opacity="0.6"/>'
            f'<rect x="64" y="200" width="172" height="44" rx="18" fill="#fff" stroke="{LINE}" stroke-width="2"/>')
    front = (f'<path d="M0 300 L0 262 C40 248 84 256 124 248 C170 240 222 254 300 244 L300 300 Z" fill="#fbfbfb" '
             f'stroke="{LINE}" stroke-width="2.4"/>'
             f'<path d="M0 274 C50 262 90 270 130 262 C176 254 228 268 300 258" {_l(width=1.4)} opacity="0.5"/>'
             f'<path d="M30 300 L44 266 M90 300 L98 262 M160 300 L164 256 M230 300 L232 258" {_l(width=1.2)} opacity="0.35"/>'
             f'<rect x="258" y="206" width="42" height="94" fill="#c9b99a" stroke="{LINE}" stroke-width="2"/>'
             f'<circle cx="279" cy="190" r="14" fill="#fff" stroke="{LINE}" stroke-width="2.4"/>'
             f'<path d="M279 182 L279 190 L285 194" {_l(width=2)}/>'
             f'<path d="M267 178 l-5 -5 M291 178 l5 -5" {_l(width=3)}/>')
    if night:
        front += '<rect width="300" height="300" fill="#1d2233" opacity="0.18"/>'
    return back, front


def night(weather: str):
    return bedroom("night", night=True)


def kitchen(weather: str):
    tiles = "".join(f"M0 {y} L300 {y}" for y in range(190, 262, 18)) + "".join(
        f"M{x} 172 L{x} 262" for x in range(0, 300, 26))
    back = (f'<rect width="300" height="300" fill="{WALL}"/>'
            f'<rect y="172" width="300" height="90" fill="#ece7dc"/>'
            f'<path d="{tiles}" {_l(width=1)} opacity="0.35"/>'
            f'<rect x="8" y="8" width="70" height="76" fill="{LIGHT}" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="84" y="8" width="70" height="76" fill="{LIGHT}" stroke="{LINE}" stroke-width="2"/>'
            f'<path d="M66 40 L66 54 M96 40 L96 54" {_l(width=3)}/>'
            + window(196, 26, 82, 76, weather, curtains=False))
    front = (f'<rect x="232" y="214" width="50" height="48" rx="10" fill="#dfe6ec" stroke="{LINE}" stroke-width="2.2"/>'
             f'<path d="M282 226 q14 2 12 18 q-2 10 -12 12" {_l(width=3)}/>'
             f'<path d="M246 214 L246 204 L268 204 L268 214" {_l(width=2.4)}/>'
             f'<ellipse cx="44" cy="260" rx="34" ry="6" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
             f'<path d="M26 258 L28 236 Q44 228 60 236 L62 258 Z" fill="#e9c98f" stroke="{LINE}" stroke-width="2"/>'
             f'<rect y="262" width="300" height="38" fill="#c8b48f" stroke="{LINE}" stroke-width="2.4"/>'
             f'<path d="M0 270 L300 270" {_l(width=1.2)} opacity="0.4"/>')
    return back, front


def desk(weather: str):
    books = []
    x = 196
    rnd = random.Random(11)
    for i in range(8):
        w, h = 9 + rnd.random() * 6, 24 + rnd.random() * 14
        fill = ["#c86b5a", "#5a7fc8", "#e0b54d", "#6ea37a", "#a07ab8", "#d98c4a", "#7a8a99", "#c95f84"][i]
        books.append(f'<rect x="{x:.1f}" y="{90 - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
                     f'stroke="{LINE}" stroke-width="1.4"/>')
        x += w + 1.5
    back = (f'<rect width="300" height="300" fill="{WALL}"/>'
            + "".join(books)
            + f'<rect x="188" y="90" width="108" height="6" fill="#b89c72" stroke="{LINE}" stroke-width="1.6"/>'
            f'<rect x="200" y="120" width="70" height="52" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
            f'<path d="M206 162 L222 140 L234 154 L244 144 L264 162 Z" fill="{LIGHT}" stroke="{LINE}" stroke-width="1.4"/>'
            f'<circle cx="252" cy="134" r="5" fill="#ffd84d" stroke="{LINE}" stroke-width="1.2"/>')
    front = (f'<rect y="262" width="300" height="38" fill="#c8a97a" stroke="{LINE}" stroke-width="2.4"/>'
             f'<path d="M30 262 L30 236 Q30 228 38 228 L52 228 Q60 228 60 236 L60 262" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
             f'<path d="M60 238 q10 0 10 9 q0 8 -10 8" {_l(width=2)}/>'
             f'<rect x="226" y="246" width="62" height="8" fill="#5a7fc8" stroke="{LINE}" stroke-width="1.4"/>'
             f'<rect x="230" y="238" width="56" height="8" fill="#e0b54d" stroke="{LINE}" stroke-width="1.4"/>'
             f'<rect x="224" y="254" width="66" height="8" fill="#c86b5a" stroke="{LINE}" stroke-width="1.4"/>')
    return back, front


def classroom(weather: str):
    scribble = (f'<path d="M168 40 L216 40 M168 54 L204 54 M168 68 L224 68 M232 92 q14 -44 28 -44 q14 0 24 44" '
                f'stroke="#3d6bb3" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
                f'<path d="M228 96 L288 96 M232 100 L232 40" stroke="#555" stroke-width="1.6"/>'
                f'<path d="M170 88 l10 -10 l10 10 l10 -10" stroke="#c0392b" stroke-width="2.2" fill="none"/>')
    back = (f'<rect width="300" height="300" fill="#efeadf"/>'
            f'<rect x="156" y="20" width="136" height="96" fill="#fff" stroke="#8a8a8a" stroke-width="5"/>'
            + scribble
            + f'<rect x="200" y="116" width="60" height="5" fill="#9a9a9a"/>'
            f'<rect y="238" width="300" height="62" fill="{LIGHT}"/>')
    front = (f'<rect y="270" width="300" height="30" fill="#c8a97a" stroke="{LINE}" stroke-width="2.4"/>'
             f'<path d="M30 266 L96 262 L98 270 L32 274 Z" fill="#fff" stroke="{LINE}" stroke-width="1.4"/>'
             f'<path d="M232 268 L286 252" stroke="#e0b54d" stroke-width="6" stroke-linecap="round"/>'
             f'<path d="M232 268 L286 252" stroke="{LINE}" stroke-width="1.2"/>')
    return back, front


def _houses() -> str:
    out = []
    for i, x in enumerate((-10, 92, 194)):
        fill = ["#e9dcc9", "#dcd3c4", "#e6d7cf"][i]
        out.append(f'<path d="M{x} 236 L{x} 150 L{x + 52} 118 L{x + 104} 150 L{x + 104} 236 Z" fill="{fill}" '
                   f'stroke="{LINE}" stroke-width="2"/>'
                   f'<path d="M{x - 4} 152 L{x + 52} 116 L{x + 108} 152" {_l(width=4, colour="#7a5a48")}/>'
                   f'<rect x="{x + 14}" y="164" width="22" height="22" fill="#eaf3fb" stroke="{LINE}" stroke-width="1.8"/>'
                   f'<rect x="{x + 66}" y="164" width="22" height="22" fill="#eaf3fb" stroke="{LINE}" stroke-width="1.8"/>'
                   f'<rect x="{x + 40}" y="196" width="24" height="40" fill="#8a5a44" stroke="{LINE}" stroke-width="1.8"/>')
    return "".join(out)


def street(weather: str):
    back = (sky_box(weather) + _houses()
            + f'<rect y="236" width="300" height="64" fill="#d6d2ca"/>'
            f'<path d="M0 248 L300 248" {_l(width=2)}/>'
            f'<path d="M270 236 L270 120 M270 120 q0 -8 -10 -8 L250 112" {_l(width=4, colour="#555")}/>'
            f'<path d="M240 112 L262 112 L258 122 L244 122 Z" fill="#fff3b0" stroke="#555" stroke-width="2"/>')
    front = ""
    if weather in ("rain", "showers", "heavy-rain", "thunder", "drizzle"):
        front = (f'<ellipse cx="40" cy="284" rx="34" ry="6" fill="#bcd3ea" stroke="{LINE}" stroke-width="1.4"/>'
                 f'<ellipse cx="262" cy="290" rx="28" ry="5" fill="#bcd3ea" stroke="{LINE}" stroke-width="1.4"/>')
    return back, front


def town(weather: str):
    awning = "".join(f'<path d="M{x} 150 l14 0 l-4 18 l-14 0 Z" fill="{c}"/>'
                     for x, c in zip(range(8, 290, 14), ["#c0392b", "#fff"] * 11))
    back = (sky_box(weather)
            + f'<rect x="0" y="120" width="140" height="116" fill="#e6dccb" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="150" y="104" width="150" height="132" fill="#dcd6cc" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="16" y="128" width="108" height="16" fill="#fff" stroke="{LINE}" stroke-width="1.6"/>'
            f'<rect x="166" y="112" width="118" height="18" fill="#fff" stroke="{LINE}" stroke-width="1.6"/>'
            + awning
            + f'<rect x="14" y="176" width="70" height="60" fill="#eaf3fb" stroke="{LINE}" stroke-width="1.8"/>'
            f'<rect x="196" y="176" width="70" height="60" fill="#eaf3fb" stroke="{LINE}" stroke-width="1.8"/>'
            f'<rect y="236" width="300" height="64" fill="#d6d2ca"/>'
            f'<path d="M0 248 L300 248" {_l(width=2)}/>')
    return back, ""


def bus(weather: str):
    outside = weather_art(weather, 168, 30, 116, 100)
    back = (f'<rect width="300" height="300" fill="#e3e8ee"/>'
            f'<clipPath id="buswin"><rect x="12" y="26" width="276" height="120" rx="14"/></clipPath>'
            f'<rect x="12" y="26" width="276" height="120" rx="14" fill="#eef6fc"/>'
            f'<g clip-path="url(#buswin)">{outside}'
            f'<path d="M12 146 L12 112 L40 112 L40 96 L70 96 L70 118 L110 118 L110 104 L150 104 L150 146 Z" '
            f'fill="#d6dbe2" stroke="{LINE}" stroke-width="1.4"/>'
            f'<path d="M30 70 L80 70 M20 84 L60 84" {_l(width=2)} opacity="0.45"/></g>'
            f'<rect x="12" y="26" width="276" height="120" rx="14" fill="none" stroke="#6b7480" stroke-width="5"/>'
            f'<path d="M150 26 L150 146" stroke="#6b7480" stroke-width="5"/>'
            f'<path d="M0 12 L300 12" stroke="#9aa3ad" stroke-width="6"/>'
            f'<path d="M286 0 L286 300" stroke="#e0b54d" stroke-width="8"/>'
            f'<rect x="60" y="170" width="180" height="140" rx="22" fill="#4f6d8f" stroke="{LINE}" stroke-width="2.4"/>'
            f'<rect x="76" y="182" width="148" height="20" rx="8" fill="#3f5a77"/>')
    front = (f'<rect x="-10" y="282" width="320" height="30" rx="10" fill="#4f6d8f" stroke="{LINE}" stroke-width="2.4"/>')
    return back, front


def train(weather: str):
    hills = (f'<path d="M14 120 Q60 90 110 112 T210 104 T296 110 L296 160 L14 160 Z" fill="#b8d3a6" stroke="{LINE}" stroke-width="1.6"/>'
             f'<path d="M30 140 L110 140 M150 132 L260 132 M60 152 L200 152" {_l(width=2)} opacity="0.5"/>')
    back = (f'<rect width="300" height="300" fill="#e9e6df"/>'
            f'<clipPath id="trainwin"><rect x="14" y="20" width="272" height="140" rx="20"/></clipPath>'
            f'<rect x="14" y="20" width="272" height="140" rx="20" fill="#eef6fc"/>'
            f'<g clip-path="url(#trainwin)">{weather_art(weather, 168, 24, 116, 90)}{hills}</g>'
            f'<rect x="14" y="20" width="272" height="140" rx="20" fill="none" stroke="#7a7a7a" stroke-width="6"/>'
            f'<rect x="56" y="150" width="188" height="160" rx="26" fill="#8a3b3b" stroke="{LINE}" stroke-width="2.4"/>'
            f'<rect x="84" y="160" width="132" height="34" rx="10" fill="#f2efe8" stroke="{LINE}" stroke-width="1.6"/>')
    return back, ""


def park(weather: str):
    back = (sky_box(weather)
            + f'<rect y="214" width="300" height="86" fill="#b9d6a0"/>'
            f'<path d="M0 214 L300 214" {_l(width=2)}/>'
            f'<rect x="30" y="140" width="14" height="80" fill="#8a6a4a" stroke="{LINE}" stroke-width="2"/>'
            f'<circle cx="37" cy="122" r="42" fill="#8fbf7a" stroke="{LINE}" stroke-width="2.2"/>'
            f'<circle cx="12" cy="140" r="26" fill="#8fbf7a" stroke="{LINE}" stroke-width="2.2"/>'
            f'<circle cx="64" cy="142" r="24" fill="#8fbf7a" stroke="{LINE}" stroke-width="2.2"/>'
            f'<rect x="276" y="168" width="10" height="50" fill="#8a6a4a" stroke="{LINE}" stroke-width="2"/>'
            f'<circle cx="281" cy="160" r="22" fill="#a3c98d" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="40" y="200" width="220" height="12" rx="3" fill="#b07a4a" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="40" y="218" width="220" height="12" rx="3" fill="#b07a4a" stroke="{LINE}" stroke-width="2"/>'
            f'<path d="M60 230 L60 272 M240 230 L240 272" {_l(width=5, colour="#555")}/>')
    tufts = "".join(f"M{x} 290 l4 -10 l4 10 " for x in (20, 120, 210, 268))
    return back, f'<path d="{tufts}" {_l(width=2, colour="#4f7a3a")}/>'


def sofa(weather: str):
    back = (f'<rect width="300" height="300" fill="#efe6dc"/>'
            f'<rect x="196" y="28" width="86" height="64" fill="#fff" stroke="{LINE}" stroke-width="3"/>'
            f'<path d="M204 84 L228 52 L244 70 L256 58 L274 84 Z" fill="#a9c7e6" stroke="{LINE}" stroke-width="1.4"/>'
            f'<path d="M30 0 L30 60" {_l(width=2)}/>'
            f'<path d="M14 60 L46 60 L54 84 L6 84 Z" fill="#fff3b0" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="18" y="168" width="264" height="110" rx="30" fill="#7c9a8a" stroke="{LINE}" stroke-width="2.6"/>'
            f'<path d="M150 176 L150 262" {_l(width=1.6)} opacity="0.5"/>'
            f'<rect x="-10" y="210" width="44" height="100" rx="18" fill="#6c8a7a" stroke="{LINE}" stroke-width="2.6"/>'
            f'<rect x="266" y="210" width="44" height="100" rx="18" fill="#6c8a7a" stroke="{LINE}" stroke-width="2.6"/>')
    return back, ""


def pitch(weather: str):
    net = "".join(f"M{x} 112 L{x - 20} 228 " for x in range(64, 260, 16)) + "".join(
        f"M42 {y} L258 {y} " for y in range(130, 228, 16))
    back = (sky_box(weather)
            + "".join(f'<rect y="{y}" width="300" height="18" fill="{c}"/>'
                      for y, c in zip(range(212, 300, 18), ["#9cc77f", "#8fbd72"] * 3))
            + f'<path d="{net}" stroke="#9a9a9a" stroke-width="1" opacity="0.6"/>'
            f'<path d="M40 228 L40 108 L260 108 L260 228" fill="none" stroke="#fff" stroke-width="8"/>'
            f'<path d="M40 228 L40 108 L260 108 L260 228" fill="none" stroke="{LINE}" stroke-width="1.6"/>')
    return back, ""


def cafe(weather: str):
    menu = "".join(f'<path d="M{198} {y} L{256 - (y % 3) * 6} {y}" stroke="#fff" stroke-width="2.2" '
                   f'stroke-linecap="round" opacity="0.85"/>' for y in range(38, 96, 12))
    back = (f'<rect width="300" height="300" fill="#efe3d3"/>'
            f'<rect x="186" y="18" width="104" height="90" rx="4" fill="#2f3b33" stroke="#8a6a4a" stroke-width="5"/>'
            + menu
            + f'<path d="M40 0 L40 30 M100 0 L100 22" {_l(width=1.6)}/>'
            f'<path d="M26 30 L54 30 L48 46 L32 46 Z M86 22 L114 22 L108 38 L92 38 Z" fill="#e0b54d" stroke="{LINE}" stroke-width="1.6"/>'
            f'<rect y="236" width="300" height="64" fill="#d9c7ad"/>')
    front = (f'<rect y="268" width="300" height="32" fill="#a07a55" stroke="{LINE}" stroke-width="2.4"/>'
             f'<ellipse cx="250" cy="266" rx="26" ry="5" fill="#fff" stroke="{LINE}" stroke-width="1.8"/>'
             f'<path d="M234 264 L236 242 L264 242 L266 264 Z" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
             f'<path d="M266 248 q10 0 10 7 q0 7 -10 7" {_l(width=2)}/>'
             f'<path d="M244 236 q-4 -6 1 -12 M254 236 q-4 -6 1 -12" {_l(width=1.6)} opacity="0.6"/>')
    return back, front


def library(weather: str):
    rnd = random.Random(21)
    colours = ["#c86b5a", "#5a7fc8", "#e0b54d", "#6ea37a", "#a07ab8", "#d98c4a", "#7a8a99", "#c95f84"]
    books = []
    for shelf_y in (60, 130, 200):
        x = 4.0
        while x < 296:
            w, h = 8 + rnd.random() * 8, 34 + rnd.random() * 18
            books.append(f'<rect x="{x:.1f}" y="{shelf_y - h:.1f}" width="{w:.1f}" height="{h:.1f}" '
                         f'fill="{rnd.choice(colours)}" stroke="{LINE}" stroke-width="1.2"/>')
            x += w + 1
        books.append(f'<rect x="0" y="{shelf_y}" width="300" height="8" fill="#9a7a55" stroke="{LINE}" stroke-width="1.4"/>')
    back = f'<rect width="300" height="300" fill="#e8dcc8"/>' + "".join(books)
    front = (f'<rect y="270" width="300" height="30" fill="#a07a55" stroke="{LINE}" stroke-width="2.4"/>'
             f'<path d="M28 268 L28 252 L76 248 L76 266 Z" fill="#5a7fc8" stroke="{LINE}" stroke-width="1.6"/>')
    return back, front


def burst(weather: str):
    rays = []
    cx, cy = 150, 180
    for i in range(24):
        a1, a2 = i * 2 * math.pi / 24, (i + 0.5) * 2 * math.pi / 24
        rays.append(f"M{cx} {cy} L{cx + math.cos(a1) * 400:.0f} {cy + math.sin(a1) * 400:.0f} "
                    f"L{cx + math.cos(a2) * 400:.0f} {cy + math.sin(a2) * 400:.0f} Z")
    return (f'<rect width="300" height="300" fill="#fff7d6"/><path d="{" ".join(rays)}" fill="#ffe7a0"/>', "")


def plain(weather: str):
    return (f'<pattern id="dots" width="10" height="10" patternUnits="userSpaceOnUse">'
            f'<circle cx="5" cy="5" r="1.4" fill="#d8d2c4"/></pattern>'
            f'<rect width="300" height="300" fill="#faf8f2"/><rect width="300" height="300" fill="url(#dots)"/>', "")


SCENES = {
    "bedroom": bedroom, "night": night, "kitchen": kitchen, "desk": desk, "classroom": classroom,
    "street": street, "town": town, "bus": bus, "train": train, "park": park, "sofa": sofa,
    "pitch": pitch, "cafe": cafe, "library": library, "burst": burst, "plain": plain,
}

ALIASES = {
    "bed": "bedroom", "home": "sofa", "living-room": "sofa", "lounge": "sofa", "tv": "sofa",
    "breakfast": "kitchen", "dinner": "kitchen", "office": "desk", "homework": "desk", "study": "desk",
    "computer": "desk", "school": "classroom", "lesson": "classroom", "exam": "classroom",
    "outside": "street", "walk": "street", "commute": "bus", "football": "pitch", "sport": "pitch",
    "coffee": "cafe", "shops": "town", "shopping": "town", "city": "town", "bedtime": "night",
    "excited": "burst", "celebration": "burst", "blank": "plain",
}


def resolve(name: str | None) -> str:
    key = str(name or "plain").strip().lower().replace(" ", "-")
    key = ALIASES.get(key, key)
    return key if key in SCENES else "plain"


def draw(scene: str, weather: str) -> tuple[str, str]:
    return SCENES[resolve(scene)](normalise_kind(weather))
