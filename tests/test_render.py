import json
import tempfile
import unittest
from pathlib import Path

from paper import profile as prof
from paper.browser import find_executable
from paper.render import render, render_html

ROOT = Path(__file__).resolve().parent.parent
PROFILE = json.loads((ROOT / "profile.example.json").read_text())
SAMPLE = json.loads((ROOT / "paper" / "samples" / "sample-edition.json").read_text())


class Html(unittest.TestCase):
    def test_sample_renders_to_html(self):
        html = render_html(PROFILE, SAMPLE)
        self.assertIn("The Alex Times", html)
        self.assertIn("Monday 5 October 2026", html)
        self.assertEqual(html.count('class="panel'), 4)

    def test_privacy_applies_to_personal_sections(self):
        html = render_html(PROFILE, SAMPLE)
        self.assertNotIn("JD014600003814512345", html)
        self.assertNotIn("£24.99", html)
        self.assertNotIn("Dr Smith", html)

    def test_more_to_read_replaces_an_empty_inbox(self):
        edition = {"date": "2026-10-04", "more": {"items": [{"label": "Science", "headline": "Comet spotted"}]}}
        html = render_html(PROFILE, edition)
        self.assertIn("More to read", html)
        self.assertIn("Comet spotted", html)
        self.assertNotIn("From your inbox", html)
        self.assertIn("From your inbox", render_html(PROFILE, SAMPLE))

    def test_headlines_box_takes_the_first_column(self):
        html = render_html(PROFILE, SAMPLE)
        row = html[html.index('class="sections"'):]
        self.assertEqual(row.count('class="hl-list"'), 1)
        self.assertLess(row.index("BBC headlines"), row.index('data-fit="Technology"'))
        self.assertIn("Source: BBC News", row)

    def test_headlines_box_pushes_out_the_news_section(self):
        story = [{"headline": "H", "body": "b"}]
        edition = {"date": "2026-10-04",
                   "headlines": {"title": "BBC headlines", "items": [{"headline": "One"}, {"headline": "Two"}]},
                   "sections": [{"name": "News", "stories": story}, {"name": "Technology", "stories": story},
                                {"name": "Business", "stories": story}]}
        html = render_html(PROFILE, edition)
        self.assertIn('data-fit="Technology"', html)
        self.assertIn('data-fit="Business"', html)
        self.assertNotIn('data-fit="News"', html)

    def test_minimal_edition(self):
        html = render_html(PROFILE, {"date": "2026-10-04"})
        self.assertIn("The Alex Times", html)

    def test_edition_number(self):
        from datetime import date
        self.assertEqual(prof.edition_number({"started": "2026-10-04"}, date(2026, 10, 4)), 1)
        self.assertEqual(prof.edition_number({"started": "2026-10-04"}, date(2026, 10, 10)), 7)


@unittest.skipUnless(find_executable(), "no Chromium available")
class Pdf(unittest.TestCase):
    def test_sample_is_two_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = render(PROFILE, SAMPLE, out_dir=Path(tmp), build_dir=Path(tmp), previews=False)
            self.assertEqual(result.pages, 2)
            self.assertTrue(result.pdf.exists())


if __name__ == "__main__":
    unittest.main()
