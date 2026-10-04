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
