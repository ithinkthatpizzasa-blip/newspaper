import json
import unittest
from datetime import date
from unittest import mock

from paper import gather

RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>BBC News</title>
<item><title>Diesel passes &#163;2 a litre</title><description><![CDATA[<p>Prices hit a record.</p>]]></description>
<link>https://www.bbc.co.uk/news/1</link><pubDate>Fri, 02 Oct 2026 16:00:00 GMT</pubDate></item>
<item><title>Second story</title><description>More news.</description>
<link>https://www.bbc.co.uk/news/2</link><pubDate>Fri, 02 Oct 2026 15:00:00 GMT</pubDate></item>
</channel></rss>"""

DAYS = ["2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"]
METEO = {
    "daily": {
        "time": DAYS,
        "weather_code": [2, 1, 3, 61, 95],
        "temperature_2m_max": [20.6, 21.2, 19.8, 14.1, 13.0],
        "temperature_2m_min": [13.9, 11.0, 10.6, 7.2, 6.0],
        "precipitation_probability_max": [4, 3, 30, 70, 80],
        "sunrise": [f"{d}T07:12" for d in DAYS],
        "sunset": [f"{d}T18:38" for d in DAYS],
        "wind_speed_10m_max": [6.0, 8.0, 12.0, 15.0, 20.0],
        "wind_gusts_10m_max": [14.0, 18.0, 25.0, 34.0, 40.0],
        "uv_index_max": [3.1, 3.0, 2.0, 1.5, 1.0],
    },
    "hourly": {
        "time": [f"2026-10-04T{h:02d}:00" for h in range(24)],
        "temperature_2m": [14 + h * 0.2 for h in range(24)],
        "precipitation_probability": [0] * 24,
        "weather_code": [45] * 9 + [2] * 15,
    },
}

ICS = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//test//EN
BEGIN:VEVENT
UID:1
DTSTART;TZID=Europe/London:20260907T090000
DTEND;TZID=Europe/London:20260907T100000
RRULE:FREQ=WEEKLY;BYDAY=SU
SUMMARY:Football practice
LOCATION:Rec ground
END:VEVENT
BEGIN:VEVENT
UID:2
DTSTART;VALUE=DATE:20261007
DTEND;VALUE=DATE:20261008
SUMMARY:Geography essay due
END:VEVENT
BEGIN:VEVENT
UID:3
DTSTART:20261104T090000Z
SUMMARY:Far future
END:VEVENT
END:VCALENDAR
"""


class Feeds(unittest.TestCase):
    def test_rss_parsing_strips_html(self):
        with mock.patch.object(gather, "_get", return_value=RSS):
            items = gather.feed("https://example.test/rss.xml")
        self.assertEqual(items[0]["title"], "Diesel passes £2 a litre")
        self.assertEqual(items[0]["summary"], "Prices hit a record.")
        self.assertTrue(items[0]["published"].startswith("2026-10-02T16:00"))

    def test_interests_map_to_feeds(self):
        feeds = gather.feeds_for({"interests": ["News", "Technology", "Knitting"],
                                  "location": {"local_feeds": ["https://local.test/rss"]}})
        self.assertIn("News", feeds)
        self.assertIn("Technology", feeds)
        self.assertNotIn("Knitting", feeds)
        self.assertEqual(feeds["Local"], ["https://local.test/rss"])


class Weather(unittest.TestCase):
    def test_open_meteo_mapping(self):
        with mock.patch.object(gather, "_get", return_value=json.dumps(METEO).encode()):
            wx = gather.weather(51.45, -2.59, "Europe/London", date(2026, 10, 4))
        self.assertEqual(wx["today"]["kind"], "partly-cloudy")
        self.assertEqual((wx["today"]["high"], wx["today"]["low"]), (21, 14))
        self.assertEqual(wx["today"]["sunrise"], "07:12")
        self.assertEqual([d["day"] for d in wx["outlook"]], ["Mon", "Tue", "Wed"])
        self.assertEqual(wx["hours"][0]["kind"], "fog")


class Calendar(unittest.TestCase):
    def test_recurring_and_all_day_events(self):
        try:
            import recurring_ical_events  # noqa: F401
        except ImportError:
            self.skipTest("calendar libraries not installed")
        with mock.patch.object(gather, "_get", return_value=ICS):
            cal = gather.calendar("webcal://example.test/cal.ics", "Europe/London", date(2026, 10, 4))
        self.assertEqual(cal["today"], [{"date": "2026-10-04", "time": "09:00", "title": "Football practice",
                                         "where": "Rec ground"}])
        self.assertEqual([(e["when"], e["title"], e["time"]) for e in cal["upcoming"]],
                         [("Wed", "Geography essay due", None)])


class Problems(unittest.TestCase):
    def test_blocked_sources_are_reported_not_fatal(self):
        def blocked(url, timeout=15):
            raise gather.SourceError("feeds.example is blocked by this machine's network policy")
        profile = {"interests": ["News"], "location": {"latitude": 51.5, "longitude": -1.8},
                   "calendar": {"source": "apple", "ics_url_env": "NO_SUCH_ENV_VAR_FOR_TESTS"}}
        with mock.patch.object(gather, "_get", side_effect=blocked):
            data = gather.gather(profile, date(2026, 10, 4))
        self.assertNotIn("weather", data)
        self.assertTrue(any(p.startswith("weather:") for p in data["problems"]))
        self.assertTrue(any("NO_SUCH_ENV_VAR_FOR_TESTS" in p for p in data["problems"]))


if __name__ == "__main__":
    unittest.main()
