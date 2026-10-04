"""The reader's cartoon avatar, drawn as SVG line art.

The same character is redrawn in every comic panel from the profile's ``avatar``
settings, so the reader looks the same every day. Coordinates live in a
200 x 220 box with the face centred on x=100 and the chin at y~148.
"""

from __future__ import annotations

INK = "#141414"
W, H = 200, 220

COLOURS = {
    "black": "#1c1c1c",
    "dark brown": "#3b2a1e",
    "brown": "#6b4a32",
    "light brown": "#a07a55",
    "auburn": "#8a3b1f",
    "ginger": "#c0602a",
    "red": "#b23a2a",
    "blonde": "#ead9a3",
    "light": "#f3ead2",
    "grey": "#9b9b9b",
    "gray": "#9b9b9b",
    "silver": "#cfcfcf",
    "white": "#ffffff",
    "navy": "#25324d",
    "blue": "#3d6bb3",
    "light blue": "#9cc3e6",
    "green": "#3e7a4f",
    "maroon": "#6d1f2c",
    "pink": "#e7a3b8",
    "purple": "#6a4c93",
    "yellow": "#f2d24b",
    "orange": "#e58a2e",
    "beige": "#e8dcc4",
    "charcoal": "#3c3c3c",
}

SKIN_TONES = {
    "none": "#ffffff",
    "light": "#fbe9dc",
    "medium-light": "#eccbab",
    "medium": "#d7a77f",
    "medium-dark": "#a8714c",
    "dark": "#6e4630",
}

HAIR_STYLES = ("spiky", "side-part", "curly", "bob", "long", "buzz", "bald")
OUTFITS = ("tshirt", "hoodie", "shirt", "blazer", "jumper")
FACIAL_HAIR = ("none", "stubble", "moustache", "beard")
PROPS = (
    "mug", "phone", "book", "newspaper", "football", "umbrella", "laptop",
    "headphones", "backpack", "scarf", "beanie",
)

MOODS = {
    "happy": dict(eyes="dot", brows="normal", mouth="smile", blush=True),
    "excited": dict(eyes="sparkle", brows="raised", mouth="open", blush=True, extra="sparkles"),
    "laughing": dict(eyes="laugh", brows="raised", mouth="open", blush=True),
    "proud": dict(eyes="laugh", brows="normal", mouth="smile", blush=True, extra="sparkles"),
    "sleepy": dict(eyes="closed", brows="low", mouth="yawn", extra="zzz"),
    "surprised": dict(eyes="wide", brows="raised", mouth="o", extra="shock"),
    "thinking": dict(eyes="up", brows="quizzical", mouth="smirk", extra="question"),
    "worried": dict(eyes="dot", brows="worried", mouth="wavy", extra="sweat"),
    "determined": dict(eyes="dot", brows="angry", mouth="grin"),
    "grumpy": dict(eyes="lidded", brows="angry", mouth="frown", extra="scribble"),
    "smug": dict(eyes="lidded", brows="quizzical", mouth="smirk"),
    "neutral": dict(eyes="dot", brows="normal", mouth="flat"),
}

DEFAULT_LOOK = {
    "hair_style": "spiky",
    "hair_color": "black",
    "skin": "none",
    "glasses": False,
    "facial_hair": "none",
    "outfit": "tshirt",
    "outfit_color": "white",
    "freckles": False,
}


def colour(value, default: str) -> str:
    """Turn a colour name ("black", "navy") or hex string into a hex string."""
    if not value:
        return default
    text = str(value).strip().lower()
    if text.startswith("#"):
        return text
    return COLOURS.get(text, default)


def is_dark(hex_colour: str) -> bool:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return True
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.45


def resolve_look(look: dict | None) -> dict:
    """Fill in defaults and normalise colours for a profile's avatar settings."""
    merged = {**DEFAULT_LOOK, **(look or {})}
    style = str(merged["hair_style"]).lower().replace(" ", "-")
    merged["hair_style"] = style if style in HAIR_STYLES else "spiky"
    merged["hair_hex"] = colour(merged["hair_color"], COLOURS["black"])
    skin = str(merged.get("skin") or "none").lower()
    merged["skin_hex"] = SKIN_TONES.get(skin, colour(skin, "#ffffff"))
    merged["outfit"] = merged["outfit"] if merged["outfit"] in OUTFITS else "tshirt"
    merged["outfit_hex"] = colour(merged["outfit_color"], "#ffffff")
    fh = str(merged.get("facial_hair") or "none").lower()
    merged["facial_hair"] = fh if fh in FACIAL_HAIR else "none"
    return merged


# --------------------------------------------------------------------------- hair

def _hair(style: str, fill: str) -> tuple[str, str]:
    """Return (back, front) SVG for a hairstyle. Back hair sits behind the head."""
    edge = f'stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"'
    hl = "#ffffff" if is_dark(fill) else INK
    hl_op = "0.55" if is_dark(fill) else "0.35"
    shine = (
        f'<path d="M78 40 Q92 33 108 36" fill="none" stroke="{hl}" stroke-width="2.4" '
        f'stroke-linecap="round" opacity="{hl_op}"/>'
    )
    if style == "spiky":
        front = (
            f'<path d="M51 100 C42 72 48 44 70 31 L68 16 L83 24 L90 9 L101 21 L112 8 L118 23 '
            f'L133 15 L131 31 C152 43 158 72 149 100 L144 100 C145 88 142 78 137 72 L132 81 '
            f'L126 66 L118 79 L110 63 L102 77 L94 62 L86 78 L78 65 L71 80 L64 70 C59 79 57 89 '
            f'56 100 Z" fill="{fill}" {edge}/>'
            + shine
        )
        return "", front
    if style == "side-part":
        front = (
            f'<path d="M51 100 C42 64 60 27 101 26 C142 27 159 64 149 100 L144 100 C146 80 140 '
            f'66 130 59 C112 74 84 76 60 70 C57 80 56 90 56 100 Z" fill="{fill}" {edge}/>'
            f'<path d="M118 31 C112 44 104 56 92 66" fill="none" stroke="{hl}" stroke-width="2" '
            f'stroke-linecap="round" opacity="{hl_op}"/>'
        )
        return "", front
    if style == "curly":
        blobs = [
            (55, 86, 13), (52, 68, 14), (60, 50, 15), (74, 36, 15), (91, 28, 15), (109, 28, 15),
            (126, 36, 15), (140, 50, 15), (148, 68, 14), (145, 86, 13), (100, 40, 22),
        ]
        fringe = [(64, 66, 11), (80, 60, 12), (98, 58, 12), (116, 60, 12), (134, 66, 11)]
        circles = "".join(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>' for x, y, r in blobs + fringe
        )
        curls = "".join(
            f'<path d="M{x - 5} {y + 2} q5 -8 10 0" fill="none" stroke="{hl}" '
            f'stroke-width="1.6" opacity="{hl_op}"/>'
            for x, y, _ in [(74, 40, 0), (100, 32, 0), (126, 40, 0), (88, 60, 0), (116, 62, 0)]
        )
        return "", f"<g>{circles}{curls}</g>"
    if style == "bob":
        back = (
            f'<path d="M38 142 C30 82 48 20 100 20 C152 20 170 82 162 142 Q150 148 138 142 '
            f'L62 142 Q50 148 38 142 Z" fill="{fill}" {edge}/>'
        )
        front = (
            f'<path d="M42 140 C36 80 56 26 100 26 C144 26 164 80 158 140 Q151 144 144 140 '
            f'C146 112 146 92 143 76 Q100 82 57 76 C54 92 54 112 56 140 Q49 144 42 140 Z" '
            f'fill="{fill}" {edge}/>'
            + shine
        )
        return back, front
    if style == "long":
        back = (
            f'<path d="M36 206 C26 130 34 22 100 20 C166 22 174 130 164 206 Q150 214 136 206 '
            f'L64 206 Q50 214 36 206 Z" fill="{fill}" {edge}/>'
        )
        front = (
            f'<path d="M45 156 C36 84 54 26 100 25 C146 26 164 84 155 156 L146 156 C150 114 146 '
            f'82 132 64 C118 58 106 50 100 38 C94 50 82 58 68 64 C54 82 50 114 54 156 Z" '
            f'fill="{fill}" {edge}/>'
            f'<path d="M100 38 L100 26" stroke="{hl}" stroke-width="1.6" opacity="{hl_op}"/>'
        )
        return back, front
    if style == "buzz":
        front = (
            f'<path d="M52 90 C51 48 76 27 100 27 C124 27 149 48 148 90 C143 72 128 58 100 56 '
            f'C72 58 57 72 52 90 Z" fill="{fill}" opacity="0.9" {edge}/>'
        )
        return "", front
    return "", ""  # bald


# --------------------------------------------------------------------------- face

def _eyes(kind: str) -> str:
    out = []
    for x in (82, 118):
        y = 101
        if kind == "closed":
            out.append(f'<path d="M{x - 7} {y} Q{x} {y + 6} {x + 7} {y}" fill="none" stroke="{INK}" '
                       'stroke-width="3" stroke-linecap="round"/>')
        elif kind == "laugh":
            out.append(f'<path d="M{x - 7} {y + 3} Q{x} {y - 7} {x + 7} {y + 3}" fill="none" '
                       f'stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
        elif kind == "lidded":
            out.append(f'<path d="M{x - 5.5} {y - 1} L{x + 5.5} {y - 1} A5.5 6.5 0 0 1 {x - 5.5} '
                       f'{y - 1} Z" fill="{INK}"/>')
            out.append(f'<path d="M{x - 8} {y - 1.5} L{x + 8} {y - 1.5}" stroke="{INK}" '
                       'stroke-width="2.6" stroke-linecap="round"/>')
        elif kind == "wide":
            out.append(f'<ellipse cx="{x}" cy="{y}" rx="5.8" ry="7.8" fill="{INK}"/>')
            out.append(f'<circle cx="{x + 1.8}" cy="{y - 2.6}" r="2" fill="#fff"/>')
        elif kind == "up":
            out.append(f'<ellipse cx="{x - 1.5}" cy="{y - 2.5}" rx="4.6" ry="6.2" fill="{INK}"/>')
            out.append(f'<circle cx="{x - 0.2}" cy="{y - 5}" r="1.5" fill="#fff"/>')
        elif kind == "sparkle":
            out.append(f'<ellipse cx="{x}" cy="{y}" rx="5" ry="6.8" fill="{INK}"/>')
            out.append(f'<circle cx="{x + 1.6}" cy="{y - 2.4}" r="2.2" fill="#fff"/>')
            out.append(f'<circle cx="{x - 1.8}" cy="{y + 2.6}" r="1" fill="#fff"/>')
        else:  # dot
            out.append(f'<ellipse cx="{x}" cy="{y}" rx="4.6" ry="6.2" fill="{INK}"/>')
            out.append(f'<circle cx="{x + 1.6}" cy="{y - 2.2}" r="1.6" fill="#fff"/>')
    return "".join(out)


def _brows(kind: str) -> str:
    shapes = {
        "normal": ("M72 86 Q82 81 92 85", "M108 85 Q118 81 128 86"),
        "raised": ("M72 80 Q82 74 92 79", "M108 79 Q118 74 128 80"),
        "low": ("M73 89 Q82 86 91 89", "M109 89 Q118 86 127 89"),
        "worried": ("M72 87 Q82 85 92 79", "M108 79 Q118 85 128 87"),
        "angry": ("M72 80 Q82 82 92 88", "M108 88 Q118 82 128 80"),
        "quizzical": ("M72 87 Q82 84 92 86", "M108 80 Q118 73 128 79"),
    }
    left, right = shapes.get(kind, shapes["normal"])
    return "".join(
        f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>'
        for d in (left, right)
    )


def _mouth(kind: str) -> str:
    stroke = f'fill="none" stroke="{INK}" stroke-width="2.8" stroke-linecap="round"'
    if kind == "open":
        return (f'<path d="M85 123 Q100 127 115 123 Q113 143 100 144 Q87 143 85 123 Z" fill="{INK}"/>'
                '<path d="M92 138 Q100 132 108 138 Q104 143 100 143 Q96 143 92 138 Z" fill="#9a9a9a"/>')
    if kind == "o":
        return f'<ellipse cx="100" cy="130" rx="5" ry="6.5" fill="{INK}"/>'
    if kind == "yawn":
        return f'<ellipse cx="100" cy="131" rx="6.5" ry="8.5" fill="{INK}"/>'
    if kind == "flat":
        return f'<path d="M92 129 L108 129" {stroke}/>'
    if kind == "frown":
        return f'<path d="M89 132 Q100 123 111 132" {stroke}/>'
    if kind == "wavy":
        return f'<path d="M87 130 Q93.5 125 100 130 Q106.5 135 113 130" {stroke}/>'
    if kind == "smirk":
        return f'<path d="M90 129 Q104 132 112 123" {stroke}/>'
    if kind == "grin":
        return f'<path d="M88 127 Q100 133 112 127" {stroke}/>'
    return f'<path d="M87 125 Q100 137 113 125" {stroke}/>'  # smile


def _extra(kind: str | None) -> str:
    if kind == "sparkles":
        def star(x, y, s):
            return (f'<path d="M{x} {y - s} Q{x} {y} {x + s} {y} Q{x} {y} {x} {y + s} Q{x} {y} '
                    f'{x - s} {y} Q{x} {y} {x} {y - s} Z" fill="{INK}"/>')
        return star(34, 44, 9) + star(168, 52, 8) + star(160, 18, 6)
    if kind == "zzz":
        return (f'<g font-family="Patrick Hand, sans-serif" fill="{INK}" font-weight="700">'
                '<text x="150" y="44" font-size="16">z</text>'
                '<text x="163" y="27" font-size="21">z</text>'
                '<text x="178" y="6" font-size="27">Z</text></g>')
    if kind == "shock":
        return (f'<g stroke="{INK}" stroke-width="3" stroke-linecap="round">'
                '<path d="M152 30 L165 16"/><path d="M160 46 L178 42"/><path d="M140 20 L145 4"/>'
                '<path d="M48 30 L35 16"/><path d="M40 46 L22 42"/></g>')
    if kind == "question":
        return (f'<text x="156" y="38" font-family="Patrick Hand, sans-serif" font-size="34" '
                f'font-weight="700" fill="{INK}">?</text>')
    if kind == "sweat":
        return (f'<path d="M151 60 Q143 73 151 78 Q159 73 151 60 Z" fill="#dff0ff" stroke="{INK}" '
                'stroke-width="2"/>')
    if kind == "scribble":
        return (f'<path d="M150 22 q6 -10 12 0 q6 -10 12 0 q-2 10 -12 6 q-8 8 -12 -6 Z" fill="none" '
                f'stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>')
    return ""


def _facial_hair(kind: str, fill: str) -> str:
    if kind == "stubble":
        dots = []
        for i, (x, y) in enumerate([
            (70, 128), (76, 136), (82, 142), (90, 146), (100, 147), (110, 146), (118, 142),
            (124, 136), (130, 128), (66, 120), (134, 120), (86, 139), (114, 139), (95, 141),
            (105, 141), (78, 128), (122, 128), (100, 140),
        ]):
            dots.append(f'<circle cx="{x}" cy="{y}" r="{1.1 if i % 2 else 0.9}" fill="{INK}" opacity="0.55"/>')
        return "".join(dots)
    if kind == "moustache":
        return (f'<path d="M86 120 C90 112 98 114 100 118 C102 114 110 112 114 120 C107 122 103 120 '
                f'100 120 C97 120 93 122 86 120 Z" fill="{fill}" stroke="{INK}" stroke-width="1.5"/>')
    if kind == "beard":
        return (f'<path d="M55 102 C57 132 76 156 100 156 C124 156 143 132 145 102 C140 118 129 123 '
                f'119 122 C118 143 82 143 81 122 C71 123 60 118 55 102 Z" fill="{fill}" '
                f'stroke="{INK}" stroke-width="2"/>')
    return ""


def _glasses() -> str:
    return (f'<g fill="none" stroke="{INK}" stroke-width="2.6">'
            '<rect x="68" y="89" width="28" height="23" rx="9" fill="#fff" fill-opacity="0.25"/>'
            '<rect x="104" y="89" width="28" height="23" rx="9" fill="#fff" fill-opacity="0.25"/>'
            '<path d="M96 99 Q100 95 104 99"/><path d="M68 97 L55 94"/><path d="M132 97 L145 94"/></g>')


# --------------------------------------------------------------------------- body

def _outfit(kind: str, fill: str, skin: str) -> tuple[str, str]:
    """Return (behind_body, body) SVG for the outfit."""
    seam = "#ffffff" if is_dark(fill) else INK
    seam_op = "0.5" if is_dark(fill) else "0.8"
    sleeves = (f'<path d="M60 172 C66 188 66 206 62 222 M140 172 C134 188 134 206 138 222" '
               f'fill="none" stroke="{seam}" stroke-width="2" opacity="{seam_op}"/>')
    def torso(neckline: str) -> str:
        """Body outline; ``neckline`` runs from the left collar (86,158) to the right (114,158)."""
        return f"M22 222 C24 192 36 174 62 166 L86 158 {neckline} L138 166 C164 174 176 192 178 222 Z"

    if kind == "hoodie":
        behind = (f'<path d="M56 176 C52 146 72 138 100 140 C128 138 148 146 144 176 Z" fill="{fill}" '
                  f'stroke="{INK}" stroke-width="2.6"/>')
        body = (f'<path d="{torso("Q100 168 114 158")}" fill="{fill}" stroke="{INK}" stroke-width="2.8"/>'
                f'<path d="M92 166 L90 198 M108 166 L110 198" stroke="{seam}" stroke-width="2.2" opacity="{seam_op}"/>'
                f'<circle cx="90" cy="200" r="2.6" fill="{seam}"/><circle cx="110" cy="200" r="2.6" fill="{seam}"/>'
                + sleeves)
        return behind, body
    if kind == "shirt":
        body = (f'<path d="{torso("L100 178 L114 158")}" fill="{fill}" stroke="{INK}" stroke-width="2.8"/>'
                f'<path d="M86 158 L78 174 L96 172 Z M114 158 L122 174 L104 172 Z" fill="#fff" '
                f'stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
                f'<path d="M100 178 L100 222" stroke="{seam}" stroke-width="1.6" opacity="{seam_op}"/>'
                f'<circle cx="100" cy="192" r="2" fill="{seam}"/><circle cx="100" cy="208" r="2" fill="{seam}"/>'
                + sleeves)
        return "", body
    if kind == "blazer":
        body = (f'<path d="{torso("L100 178 L114 158")}" fill="#fff" stroke="{INK}" stroke-width="2.8"/>'
                f'<path d="M95 170 L105 170 L108 204 L100 214 L92 204 Z" fill="{INK}"/>'
                f'<path d="M22 222 C24 192 36 174 62 166 L86 158 L94 176 L104 222 Z" fill="{fill}" '
                f'stroke="{INK}" stroke-width="2.8" stroke-linejoin="round"/>'
                f'<path d="M178 222 C176 192 164 174 138 166 L114 158 L106 176 L96 222 Z" fill="{fill}" '
                f'stroke="{INK}" stroke-width="2.8" stroke-linejoin="round"/>'
                f'<path d="M86 158 L78 176 L92 184 M114 158 L122 176 L108 184" fill="none" stroke="{seam}" '
                f'stroke-width="2" opacity="{seam_op}"/>')
        return "", body
    if kind == "jumper":
        body = (f'<path d="{torso("L100 186 L114 158")}" fill="{fill}" stroke="{INK}" stroke-width="2.8"/>'
                f'<path d="M88 160 L100 186 L112 160 L100 172 Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'
                f'<path d="M86 158 L80 172 L96 168 Z M114 158 L120 172 L104 168 Z" fill="#fff" '
                f'stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                + sleeves)
        return "", body
    body = (f'<path d="{torso("Q100 172 114 158")}" fill="{fill}" stroke="{INK}" stroke-width="2.8"/>'
            f'<path d="M83 160 Q100 181 117 160" fill="none" stroke="{seam}" stroke-width="2.2" '
            f'opacity="{seam_op}"/>' + sleeves)
    return "", body


def _hand(x: float, y: float, skin: str) -> str:
    return (f'<rect x="{x - 10}" y="{y - 11}" width="20" height="22" rx="9" fill="{skin}" '
            f'stroke="{INK}" stroke-width="2.4"/>'
            f'<path d="M{x - 6} {y - 2} L{x + 4} {y - 2}" stroke="{INK}" stroke-width="1.6" '
            'stroke-linecap="round" opacity="0.7"/>')


def _prop(name: str | None, skin: str) -> tuple[str, str]:
    """Return (under_head, over_everything) SVG for something the character holds or wears."""
    s = f'stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"'
    if name == "mug":
        return "", (f'<path d="M82 176 L82 208 Q82 216 90 216 L106 216 Q114 216 114 208 L114 176 Z" '
                    f'fill="#fff" {s}/>'
                    f'<path d="M114 184 Q127 184 127 195 Q127 206 114 206" fill="none" {s}/>'
                    f'<path d="M90 170 Q85 163 91 156 M99 170 Q94 161 100 152 M108 170 Q103 163 109 156" '
                    f'fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" opacity="0.6"/>'
                    + _hand(80, 200, skin))
    if name == "phone":
        return "", (f'<rect x="112" y="158" width="30" height="52" rx="6" fill="#fff" {s}/>'
                    f'<rect x="116.5" y="164" width="21" height="36" rx="2" fill="#d8d8d8"/>'
                    + _hand(126, 204, skin))
    if name == "book":
        return "", (f'<path d="M56 214 L56 180 Q78 172 100 182 Q122 172 144 180 L144 214 Q122 206 100 216 '
                    f'Q78 206 56 214 Z" fill="#fff" {s}/>'
                    f'<path d="M100 182 L100 216" {s}/>'
                    f'<path d="M64 188 L92 192 M64 196 L92 199 M108 192 L136 188 M108 199 L136 196" '
                    f'stroke="{INK}" stroke-width="1.4" opacity="0.5"/>'
                    + _hand(54, 202, skin) + _hand(146, 202, skin))
    if name == "newspaper":
        return "", (f'<rect x="50" y="168" width="100" height="58" fill="#fff" {s}/>'
                    f'<text x="100" y="185" text-anchor="middle" font-family="UnifrakturMaguntia, serif" '
                    f'font-size="15" fill="{INK}">Times</text>'
                    f'<path d="M58 191 L142 191" stroke="{INK}" stroke-width="1.6"/>'
                    f'<path d="M58 198 L96 198 M58 204 L96 204 M58 210 L96 210 M104 198 L142 198 '
                    f'M104 204 L142 204 M104 210 L142 210" stroke="{INK}" stroke-width="1.2" opacity="0.5"/>'
                    + _hand(48, 200, skin) + _hand(152, 200, skin))
    if name == "football":
        return "", (f'<circle cx="156" cy="198" r="22" fill="#fff" {s}/>'
                    f'<path d="M156 188 L165 195 L161 206 L151 206 L147 195 Z" fill="{INK}"/>'
                    f'<path d="M156 188 L156 177 M165 195 L176 191 M161 206 L168 216 M151 206 L144 216 '
                    f'M147 195 L136 191" stroke="{INK}" stroke-width="2"/>')
    if name == "umbrella":
        return "", (f'<path d="M152 6 L152 204 Q152 215 143 215 Q135 215 135 207" fill="none" '
                    f'stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>'
                    f'<path d="M64 8 Q152 -84 240 8 Q229 0 218 8 Q207 0 196 8 Q185 0 174 8 Q163 0 152 8 '
                    f'Q141 0 130 8 Q119 0 108 8 Q97 0 86 8 Q75 0 64 8 Z" fill="#e8e3d6" {s}/>'
                    f'<path d="M152 -38 L152 -48" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
                    f'<path d="M108 8 Q120 -40 152 -38 M196 8 Q184 -40 152 -38" fill="none" '
                    f'stroke="{INK}" stroke-width="1.6" opacity="0.6"/>'
                    + _hand(152, 192, skin))
    if name == "laptop":
        return "", (f'<path d="M52 224 L58 176 L142 176 L148 224 Z" fill="#e4e4e4" {s}/>'
                    f'<circle cx="100" cy="198" r="7" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
    if name == "headphones":
        return "", (f'<path d="M50 98 C44 22 156 22 150 98" fill="none" stroke="{INK}" stroke-width="7"/>'
                    f'<rect x="39" y="84" width="19" height="30" rx="8" fill="#3c3c3c" {s}/>'
                    f'<rect x="142" y="84" width="19" height="30" rx="8" fill="#3c3c3c" {s}/>')
    if name == "backpack":
        return "", (f'<path d="M70 163 C65 180 63 200 66 222 M130 163 C135 180 137 200 134 222" fill="none" '
                    f'stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
                    f'<path d="M70 163 C65 180 63 200 66 222 M130 163 C135 180 137 200 134 222" fill="none" '
                    f'stroke="#6b6b6b" stroke-width="5" stroke-linecap="round"/>')
    if name == "scarf":
        return "", (f'<path d="M76 150 Q100 168 124 150 L127 165 Q100 184 73 165 Z" fill="#b23a2a" {s}/>'
                    f'<path d="M106 168 L114 212 L100 214 L96 172 Z" fill="#b23a2a" {s}/>'
                    f'<path d="M100 196 L113 194 M99 204 L114 202" stroke="#fff" stroke-width="2.4"/>')
    if name == "beanie":
        return "", (f'<path d="M46 80 C34 -24 166 -24 154 80 Z" fill="#3d6bb3" {s}/>'
                    f'<path d="M43 66 Q100 54 157 66 L158 85 Q100 73 42 85 Z" fill="#2f5591" {s}/>'
                    f'<circle cx="100" cy="2" r="11" fill="#fff" {s}/>')
    return "", ""


def prop_svg(look: dict | None, prop: str | None) -> str:
    """Just the held/worn prop, for drawing in front of scenery (desks, blankets)."""
    return _prop(prop, resolve_look(look)["skin_hex"])[1]


def avatar_svg(look: dict | None, mood: str = "happy", prop: str | None = None) -> str:
    """SVG group content for the avatar (200 x 220 box), ready to be placed in a panel.

    Pass ``prop=None`` and draw :func:`prop_svg` separately to put the prop in front of scenery.
    """
    lk = resolve_look(look)
    m = MOODS.get(mood, MOODS["happy"])
    skin, hair = lk["skin_hex"], lk["hair_hex"]
    hair_back, hair_front = _hair(lk["hair_style"], hair)
    behind_body, body = _outfit(lk["outfit"], lk["outfit_hex"], skin)
    _, prop_svg = _prop(prop, skin)

    head = ("M52 90 C52 50 76 30 100 30 C124 30 148 50 148 90 C148 124 128 148 100 148 "
            "C72 148 52 124 52 90 Z")
    ears = (f'<path d="M56 82 C38 76 36 108 57 108 Z" fill="{skin}" stroke="{INK}" stroke-width="2.8"/>'
            f'<path d="M144 82 C162 76 164 108 143 108 Z" fill="{skin}" stroke="{INK}" stroke-width="2.8"/>'
            f'<path d="M51 89 C45 90 45 99 52 100 M149 89 C155 90 155 99 148 100" fill="none" '
            f'stroke="{INK}" stroke-width="1.6" opacity="0.6"/>')
    if lk["hair_style"] in ("bob", "long"):
        ears = ""
    neck = f'<path d="M87 132 L87 164 L113 164 L113 132 Z" fill="{skin}" stroke="{INK}" stroke-width="2.8"/>'
    blush = ""
    if m.get("blush"):
        blush = ('<ellipse cx="72" cy="118" rx="7.5" ry="4" fill="#e58a8a" opacity="0.35"/>'
                 '<ellipse cx="128" cy="118" rx="7.5" ry="4" fill="#e58a8a" opacity="0.35"/>')
    freckles = ""
    if lk.get("freckles"):
        freckles = "".join(f'<circle cx="{x}" cy="{y}" r="1.1" fill="{INK}" opacity="0.5"/>'
                           for x, y in [(70, 112), (75, 115), (68, 117), (130, 112), (125, 115), (132, 117)])
    nose = (f'<path d="M100 106 Q105 114 99 116" fill="none" stroke="{INK}" stroke-width="2.2" '
            'stroke-linecap="round"/>')

    parts = [
        hair_back,
        behind_body,
        neck,
        body,
        ears,
        f'<path d="{head}" fill="{skin}" stroke="{INK}" stroke-width="3"/>',
        blush,
        freckles,
        _facial_hair(lk["facial_hair"], hair),
        _eyes(m["eyes"]),
        _brows(m["brows"]),
        nose,
        _mouth(m["mouth"]),
        hair_front,
        _glasses() if lk.get("glasses") else "",
        prop_svg,
        _extra(m.get("extra")),
    ]
    return "".join(p for p in parts if p)


def avatar_standalone(look: dict | None, mood: str = "happy", prop: str | None = None,
                      size: int = 200) -> str:
    """A complete <svg> element, for previews and the avatar picker."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -20 220 240" width="{size}" '
            f'height="{round(size * 240 / 220)}">{avatar_svg(look, mood, prop)}</svg>')
