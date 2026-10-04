"""The reader's profile: who the paper is for and what goes in it.

It lives in ``profile.json`` at the repo root, which is git-ignored because it is
personal. A cloud run can pass it in the ``NEWSPAPER_PROFILE`` environment
variable instead (inline JSON).
"""

from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = ROOT / "profile.json"
EXAMPLE_PATH = ROOT / "profile.example.json"


class ProfileMissing(RuntimeError):
    pass


def load(path: str | Path | None = None) -> dict:
    if path:
        return json.loads(Path(path).read_text())
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text())
    inline = os.environ.get("NEWSPAPER_PROFILE", "").strip()
    if inline:
        return json.loads(inline)
    raise ProfileMissing(
        "No profile.json yet. Run /paper-setup in Claude Code, or copy profile.example.json "
        "to profile.json and edit it."
    )


def save(profile: dict, path: str | Path | None = None) -> Path:
    target = Path(path) if path else PROFILE_PATH
    target.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n")
    return target


def reader(profile: dict) -> str:
    return (profile.get("reader") or {}).get("name") or "Reader"


def paper_name(profile: dict) -> str:
    return profile.get("paper_name") or f"The {reader(profile)} Times"


def city(profile: dict) -> str:
    return (profile.get("location") or {}).get("city") or "Home"


def slug(profile: dict) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", paper_name(profile)).strip("-") or "Paper"


def started(profile: dict, default: date) -> date:
    try:
        return date.fromisoformat(str(profile.get("started")))
    except ValueError:
        return default


def edition_number(profile: dict, day: date) -> int:
    return max(1, (day - started(profile, day)).days + 1)


def volume(profile: dict, day: date) -> str:
    years = max(0, (day - started(profile, day)).days // 365)
    return _roman(years + 1)


def _roman(n: int) -> str:
    out = ""
    for value, numeral in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= value:
            out, n = out + numeral, n - value
    return out
