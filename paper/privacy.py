"""Privacy filters for the personal parts of the paper (your day, inbox heads-ups).

By default the paper leaves out money amounts, street addresses, parcel tracking
numbers and medical details. Doctor-type appointments still appear as a time and
a neutral label, and parcels can say what's arriving, just not the tracking number.

News and newsletter content is public, so it isn't filtered (a business story
can still say "a £2bn deal").
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MONEY = re.compile(
    r"(?:[£$€¥₹]\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:k|m|bn|million|billion)\b)?"
    r"|\b(?:GBP|USD|EUR)\s?\d[\d,]*(?:\.\d{1,2})?"
    r"|\b\d[\d,]*(?:\.\d{1,2})?\s?(?:GBP|USD|EUR|pounds?|quid|dollars?|euros?|p)\b)",
    re.IGNORECASE,
)
CARD = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")
UK_POSTCODE = re.compile(r"\b(?:[A-Z]{1,2}\d[A-Z\d]?|GIR)\s*\d[A-Z]{2}\b", re.IGNORECASE)
STREET = re.compile(
    r"\b\d{1,4}[A-Za-z]?,?\s+(?:[A-Z][\w'-]*\s+){1,3}"
    r"(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Close|Drive|Dr|Way|Crescent|Cres|Place|Pl|Court|Ct|"
    r"Gardens|Gdns|Grove|Terrace|Mews|Square|Sq|Hill|Row|Walk|Parade|Boulevard|Blvd|View|Rise)\b\.?"
)
TRACKING = re.compile(
    r"\b(?:1Z[0-9A-Z]{16}|[A-Z]{2}\d{9}[A-Z]{2}|\d{12,22}"
    r"|(?=[A-Z0-9]{10,24}\b)(?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{10,24})\b"
)
MEDICAL = re.compile(
    r"\b(?:doctors?|dr\.?|gp|surgery|dentist|dental|orthodont\w*|hospital|clinic|physio\w*|"
    r"therap\w*|counsell?\w*|psycholog\w*|psychiatr\w*|vaccin\w*|jab|blood test|prescription|"
    r"pharmacy|chemist|optician|eye test|hearing test|scan|x-?ray|nhs|medical|health check|"
    r"diagnos\w*|injection|a&e)\b",
    re.IGNORECASE,
)


@dataclass
class Rules:
    hide_money: bool = True
    hide_addresses: bool = True
    hide_tracking_numbers: bool = True
    hide_medical_details: bool = True

    @classmethod
    def from_profile(cls, profile: dict) -> "Rules":
        p = profile.get("privacy") or {}
        return cls(**{k: bool(p.get(k, True)) for k in cls.__dataclass_fields__})


def is_medical(text: str) -> bool:
    return bool(MEDICAL.search(text or ""))


def scrub_text(text: str, rules: Rules) -> str:
    """Remove money, addresses and tracking numbers from one piece of text."""
    if not text:
        return text
    out = text
    if rules.hide_tracking_numbers:
        out = TRACKING.sub("(tracking no. hidden)", out)
    if rules.hide_money:
        out = CARD.sub("(number hidden)", out)
        out = MONEY.sub("(amount hidden)", out)
    if rules.hide_addresses:
        out = STREET.sub("(address hidden)", out)
        out = UK_POSTCODE.sub("(postcode hidden)", out)
    return re.sub(r"\s{2,}", " ", out).strip()


def scrub_event(event: dict, rules: Rules) -> dict:
    """A calendar entry: medical ones keep only their time and a neutral label."""
    e = dict(event)
    blob = " ".join(str(e.get(k, "")) for k in ("title", "where", "note"))
    if rules.hide_medical_details and is_medical(blob):
        return {k: v for k, v in {"time": e.get("time"), "when": e.get("when"),
                                  "title": "Appointment"}.items() if v}
    for key in ("title", "where", "note"):
        if e.get(key):
            e[key] = scrub_text(str(e[key]), rules)
    if rules.hide_addresses and e.get("where") and ("hidden" in e["where"]):
        e.pop("where")
    return e


def scrub_heads_up(item: dict, rules: Rules) -> dict:
    i = dict(item)
    blob = " ".join(str(i.get(k, "")) for k in ("from", "text"))
    if rules.hide_medical_details and is_medical(blob):
        return {"from": "Appointments", "text": "A health-related email arrived. Details left out of the paper."}
    for key in ("from", "text"):
        if i.get(key):
            i[key] = scrub_text(str(i[key]), rules)
    return i


def scrub_edition(edition: dict, profile: dict) -> dict:
    """Apply the reader's privacy rules to the personal sections of an edition."""
    rules = Rules.from_profile(profile)
    ed = dict(edition)
    day = dict(ed.get("your_day") or {})
    for key in ("events", "upcoming"):
        if day.get(key):
            day[key] = [scrub_event(e, rules) for e in day[key]]
    if day.get("note"):
        day["note"] = scrub_text(day["note"], rules)
    if day:
        ed["your_day"] = day
    inbox = dict(ed.get("inbox") or {})
    if inbox.get("heads_up"):
        inbox["heads_up"] = [scrub_heads_up(i, rules) for i in inbox["heads_up"]]
    if inbox:
        ed["inbox"] = inbox
    return ed
