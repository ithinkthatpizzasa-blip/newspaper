import itertools
import re
import unittest
import xml.etree.ElementTree as ET

from paper import scenes
from paper.avatar import HAIR_STYLES, MOODS, OUTFITS, PROPS, avatar_standalone, resolve_look
from paper.comic import panel_html, strip_html


def parses(svg: str) -> bool:
    ET.fromstring(svg)
    return True


class Avatar(unittest.TestCase):
    def test_every_combination_is_valid_svg(self):
        for style, outfit, mood in itertools.product(HAIR_STYLES, OUTFITS, MOODS):
            look = {"hair_style": style, "outfit": outfit, "glasses": True, "facial_hair": "beard"}
            self.assertTrue(parses(avatar_standalone(look, mood)), (style, outfit, mood))

    def test_every_prop_is_valid_svg(self):
        for prop in PROPS:
            self.assertTrue(parses(avatar_standalone({}, "happy", prop)), prop)

    def test_colour_names_resolve(self):
        look = resolve_look({"hair_color": "Black", "outfit_color": "navy", "skin": "medium"})
        self.assertEqual(look["hair_hex"], "#1c1c1c")
        self.assertEqual(look["outfit_hex"], "#25324d")

    def test_unknown_values_fall_back(self):
        look = resolve_look({"hair_style": "mohawk", "outfit": "spacesuit", "facial_hair": "goatee"})
        self.assertEqual((look["hair_style"], look["outfit"], look["facial_hair"]), ("spiky", "tshirt", "none"))


class Scenes(unittest.TestCase):
    def test_every_scene_and_weather_is_valid_svg(self):
        for name, kind in itertools.product(scenes.SCENES, scenes.WEATHER_KINDS):
            back, front = scenes.draw(name, kind)
            self.assertTrue(parses(f'<svg xmlns="http://www.w3.org/2000/svg">{back}{front}</svg>'), (name, kind))

    def test_weather_words_normalise(self):
        self.assertEqual(scenes.normalise_kind("Sunny spells"), "partly-cloudy")
        self.assertEqual(scenes.normalise_kind("overcast"), "cloudy")
        self.assertEqual(scenes.normalise_kind("blizzard of frogs"), "partly-cloudy")

    def test_aliases(self):
        self.assertEqual(scenes.resolve("school"), "classroom")
        self.assertEqual(scenes.resolve("nowhere"), "plain")


class Comic(unittest.TestCase):
    def test_panel_escapes_text_and_keeps_ids_unique(self):
        panels = [{"scene": "bedroom", "mood": "sleepy", "speech": "<b>hi</b> & bye", "caption": "7am"},
                  {"scene": "bedroom", "mood": "happy", "pose": "left", "sfx": "BEEP!"}]
        html = strip_html({"panels": panels}, {"hair_color": "black"})
        self.assertIn("&lt;b&gt;hi&lt;/b&gt; &amp; bye", html)
        self.assertNotIn("<b>hi</b>", html)
        ids = re.findall(r'\bid="([^"]+)"', html)
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))

    def test_panel_survives_missing_fields(self):
        self.assertIn('class="panel"', panel_html({}, None))


if __name__ == "__main__":
    unittest.main()
