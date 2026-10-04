import unittest

from paper.privacy import Rules, scrub_edition, scrub_event, scrub_heads_up, scrub_text


class ScrubText(unittest.TestCase):
    def setUp(self):
        self.rules = Rules()

    def test_money(self):
        self.assertEqual(scrub_text("Receipt for £18.00 from Anthropic", self.rules),
                         "Receipt for (amount hidden) from Anthropic")
        self.assertNotIn("20", scrub_text("Paid $20 and 15 GBP", self.rules))

    def test_tracking_numbers(self):
        for text in ("Parcel JD014600003814512345 arrives", "Royal Mail AB123456789GB", "UPS 1Z999AA10123456784"):
            self.assertIn("(tracking no. hidden)", scrub_text(text, self.rules), text)

    def test_addresses_and_postcodes(self):
        out = scrub_text("Party at 12 Station Road, Bristol BS1 4DJ", self.rules)
        self.assertNotIn("Station Road", out)
        self.assertNotIn("BS1", out)

    def test_card_numbers_keep_spacing(self):
        self.assertEqual(scrub_text("Card 4111 1111 1111 1111 charged", self.rules), "Card (number hidden) charged")

    def test_ordinary_text_untouched(self):
        for text in ("Claude Opus 5.5 is here", "Meeting at 5pm about Year 12", "BBC iPlayer: Traitors returns",
                     "Order #2041-8482-1675 shipped"):
            self.assertEqual(scrub_text(text, self.rules), text)

    def test_rules_can_be_switched_off(self):
        rules = Rules(hide_money=False)
        self.assertEqual(scrub_text("Costs £5", rules), "Costs £5")


class ScrubPersonalSections(unittest.TestCase):
    def test_medical_event_becomes_neutral(self):
        e = scrub_event({"time": "15:30", "title": "Dentist - Dr Patel", "where": "5 High Street"}, Rules())
        self.assertEqual(e, {"time": "15:30", "title": "Appointment"})

    def test_normal_event_kept(self):
        e = scrub_event({"time": "09:00", "title": "Geography", "where": "Room 4"}, Rules())
        self.assertEqual(e["title"], "Geography")
        self.assertEqual(e["where"], "Room 4")

    def test_medical_email_hidden(self):
        h = scrub_heads_up({"from": "NHS", "text": "Your vaccination booking"}, Rules())
        self.assertNotIn("vaccination", h["text"])

    def test_edition_news_is_not_scrubbed(self):
        ed = {"date": "2026-10-04",
              "sections": [{"name": "Business", "stories": [{"headline": "£2bn deal", "body": "Worth £2bn."}]}],
              "inbox": {"heads_up": [{"from": "Shop", "text": "Refund of £12.50 sent"}]}}
        out = scrub_edition(ed, {})
        self.assertEqual(out["sections"][0]["stories"][0]["body"], "Worth £2bn.")
        self.assertIn("(amount hidden)", out["inbox"]["heads_up"][0]["text"])


if __name__ == "__main__":
    unittest.main()
