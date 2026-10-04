"""Collect the raw ingredients for an edition: weather, headlines and the calendar.

Everything here is best-effort. Each source that fails (no network, a blocked
host, no calendar link) is listed under ``problems`` so Claude can fill the gap
another way, e.g. with web search. Email is read by Claude through the Gmail
connector, not here.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from zoneinfo import ZoneInfo

from . import profile as prof

UA = "MorningNewspaper/1.0 (+https://github.com/ithinkthatpizzasa-blip/newspaper)"

BBC = "https://feeds.bbci.co.uk/news"
DEFAULT_FEEDS = {
    "news": [f"{BBC}/rss.xml"],
    "general news": [f"{BBC}/rss.xml"],
    "uk": [f"{BBC}/uk/rss.xml"],
    "world": [f"{BBC}/world/rss.xml"],
    "politics": [f"{BBC}/politics/rss.xml"],
    "technology": [f"{BBC}/technology/rss.xml"],
    "tech": [f"{BBC}/technology/rss.xml"],
    "business": [f"{BBC}/business/rss.xml"],
    "science": [f"{BBC}/science_and_environment/rss.xml"],
    "health": [f"{BBC}/health/rss.xml"],
    "education": [f"{BBC}/education/rss.xml"],
    "entertainment": [f"{BBC}/entertainment_and_arts/rss.xml"],
    "arts": [f"{BBC}/entertainment_and_arts/rss.xml"],
    "sport": ["https://feeds.bbci.co.uk/sport/rss.xml"],
    "football": ["https://feeds.bbci.co.uk/sport/football/rss.xml"],
}

# Open-Meteo weather codes -> (kind used by the paper's icons/comic, description)
WMO = {
    0: ("clear", "Clear skies"), 1: ("clear", "Mainly clear"), 2: ("partly-cloudy", "Partly cloudy"),
    3: ("cloudy", "Overcast"), 45: ("fog", "Fog"), 48: ("fog", "Freezing fog"),
    51: ("drizzle", "Light drizzle"), 53: ("drizzle", "Drizzle"), 55: ("drizzle", "Heavy drizzle"),
    56: ("drizzle", "Freezing drizzle"), 57: ("drizzle", "Freezing drizzle"),
    61: ("rain", "Light rain"), 63: ("rain", "Rain"), 65: ("heavy-rain", "Heavy rain"),
    66: ("rain", "Freezing rain"), 67: ("heavy-rain", "Heavy freezing rain"),
    71: ("snow", "Light snow"), 73: ("snow", "Snow"), 75: ("snow", "Heavy snow"), 77: ("snow", "Snow grains"),
    80: ("showers", "Light showers"), 81: ("showers", "Showers"), 82: ("heavy-rain", "Violent showers"),
    85: ("snow", "Snow showers"), 86: ("snow", "Heavy snow showers"),
    95: ("thunder", "Thunderstorms"), 96: ("thunder", "Thunderstorms with hail"),
    99: ("thunder", "Thunderstorms with hail"),
}


class SourceError(RuntimeError):
    pass


def _get(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise SourceError(f"{urllib.parse.urlparse(url).netloc} answered HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        host = urllib.parse.urlparse(url).netloc
        reason = str(getattr(exc, "reason", exc))
        if "403" in reason or "Tunnel" in reason or "Forbidden" in reason:
            raise SourceError(f"{host} is blocked by this machine's network policy") from exc
        raise SourceError(f"couldn't reach {host} ({reason})") from exc


# --------------------------------------------------------------------------- weather

def weather(lat: float, lon: float, tz: str, day: date) -> dict:
    params = {
        "latitude": lat, "longitude": lon, "timezone": tz, "forecast_days": 5,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
                 "sunrise,sunset,wind_speed_10m_max,wind_gusts_10m_max,uv_index_max",
        "hourly": "temperature_2m,precipitation_probability,weather_code",
        "wind_speed_unit": "mph",
    }
    data = json.loads(_get("https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)))
    d = data["daily"]
    days = []
    for i, iso in enumerate(d["time"]):
        kind, desc = WMO.get(d["weather_code"][i], ("partly-cloudy", "Mixed"))
        days.append({
            "date": iso,
            "day": date.fromisoformat(iso).strftime("%a"),
            "kind": kind,
            "description": desc,
            "high": round(d["temperature_2m_max"][i]),
            "low": round(d["temperature_2m_min"][i]),
            "rain_chance": d["precipitation_probability_max"][i],
            "wind_mph": round(d["wind_speed_10m_max"][i]),
            "gusts_mph": round(d["wind_gusts_10m_max"][i]),
            "uv": d["uv_index_max"][i],
            "sunrise": d["sunrise"][i][-5:],
            "sunset": d["sunset"][i][-5:],
        })
    today = next((x for x in days if x["date"] == day.isoformat()), days[0])
    h = data["hourly"]
    hours = []
    for i, stamp in enumerate(h["time"]):
        if stamp.startswith(today["date"]) and int(stamp[11:13]) in (7, 9, 12, 15, 18, 21):
            kind, desc = WMO.get(h["weather_code"][i], ("partly-cloudy", "Mixed"))
            hours.append({"time": stamp[11:16], "temp": round(h["temperature_2m"][i]),
                          "rain_chance": h["precipitation_probability"][i], "kind": kind, "description": desc})
    later = [x for x in days if x["date"] > today["date"]][:3]
    return {"source": "Open-Meteo", "today": today, "hours": hours, "outlook": later}


# --------------------------------------------------------------------------- news

def _text(node, tag: str) -> str:
    el = node.find(tag)
    return unescape(re.sub(r"<[^>]+>", "", el.text or "")).strip() if el is not None and el.text else ""


def feed(url: str, limit: int = 12) -> list[dict]:
    root = ET.fromstring(_get(url))
    items = []
    for item in root.iter("item"):
        when = _text(item, "pubDate")
        try:
            stamp = parsedate_to_datetime(when).isoformat() if when else ""
        except (TypeError, ValueError):
            stamp = when
        items.append({"title": _text(item, "title"), "summary": _text(item, "description"),
                      "link": _text(item, "link"), "published": stamp})
        if len(items) >= limit:
            break
    return items


def feeds_for(profile: dict) -> dict[str, list[str]]:
    custom = profile.get("feeds") or {}
    out = {}
    for interest in profile.get("interests") or ["News"]:
        urls = custom.get(interest) or DEFAULT_FEEDS.get(interest.strip().lower())
        if urls:
            out[interest] = urls
    local = (profile.get("location") or {}).get("local_feeds") or []
    if local:
        out["Local"] = local
    return out


def headlines(profile: dict, problems: list[str]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for section, urls in feeds_for(profile).items():
        seen, items = set(), []
        for url in urls:
            try:
                for it in feed(url):
                    if it["title"] not in seen:
                        seen.add(it["title"])
                        items.append(it)
            except (SourceError, ET.ParseError) as exc:
                problems.append(f"{section} headlines: {exc}")
        if items:
            out[section] = items
    return out


# --------------------------------------------------------------------------- calendar

def calendar(url: str, tz: str, day: date, days_ahead: int = 6) -> dict:
    url = re.sub(r"^webcal://", "https://", url.strip())
    raw = _get(url)
    try:
        import icalendar
        import recurring_ical_events
    except ImportError as exc:
        raise SourceError("calendar libraries missing: python3 -m pip install -r requirements.txt") from exc
    zone = ZoneInfo(tz)
    cal = icalendar.Calendar.from_ical(raw)
    start = datetime.combine(day, datetime.min.time(), zone)
    end = start + timedelta(days=days_ahead + 1)
    events = []
    for ev in recurring_ical_events.of(cal).between(start, end):
        begin = ev.get("DTSTART").dt
        all_day = not isinstance(begin, datetime)
        when = datetime.combine(begin, datetime.min.time(), zone) if all_day else begin.astimezone(zone)
        events.append({
            "date": when.date().isoformat(),
            "time": None if all_day else when.strftime("%H:%M"),
            "title": str(ev.get("SUMMARY", "")).strip() or "Busy",
            "where": str(ev.get("LOCATION", "")).strip() or None,
        })
    events.sort(key=lambda e: (e["date"], e["time"] or ""))
    today = [e for e in events if e["date"] == day.isoformat()]
    upcoming = [dict(e, when=date.fromisoformat(e["date"]).strftime("%a")) for e in events
                if e["date"] != day.isoformat()]
    return {"today": today, "upcoming": upcoming}


# --------------------------------------------------------------------------- all together

def gather(profile: dict, day: date | None = None) -> dict:
    loc = profile.get("location") or {}
    tz = loc.get("timezone") or "Europe/London"
    day = day or datetime.now(ZoneInfo(tz)).date()
    problems: list[str] = []
    out: dict = {"date": day.isoformat(), "generated_at": datetime.now(ZoneInfo(tz)).isoformat(timespec="minutes"),
                 "paper": prof.paper_name(profile), "city": prof.city(profile)}

    if loc.get("latitude") is not None and loc.get("longitude") is not None:
        try:
            out["weather"] = weather(loc["latitude"], loc["longitude"], tz, day)
        except (SourceError, KeyError, ValueError) as exc:
            problems.append(f"weather: {exc}")
    else:
        problems.append("weather: no latitude/longitude in profile.json")

    out["headlines"] = headlines(profile, problems)
    if not out["headlines"]:
        problems.append("headlines: none fetched")

    cal = profile.get("calendar") or {}
    env_name = cal.get("ics_url_env") or "NEWSPAPER_CALENDAR_URL"
    ics = os.environ.get(env_name) or cal.get("ics_url")
    if ics:
        try:
            out["calendar"] = calendar(ics, tz, day)
        except (SourceError, ValueError) as exc:
            problems.append(f"calendar: {exc}")
    elif cal.get("source") not in (None, "none"):
        problems.append(f"calendar: set the {env_name} environment variable to the calendar's private link")

    out["problems"] = problems
    return out


def write(profile: dict, day: date | None = None, build_root: Path | None = None) -> Path:
    data = gather(profile, day)
    folder = (build_root or prof.ROOT / "build") / data["date"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "sources.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return path
