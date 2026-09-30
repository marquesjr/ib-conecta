"""Hero da home no tablet e no celular (issue #69)."""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

CSS_PATH = Path(settings.BASE_DIR) / "static" / "css" / "ib-conecta.css"


def media_block(css, query):
    """Corpo do primeiro bloco @media que contém regras da .welcome para a query."""
    for match in re.finditer(rf"@media \({re.escape(query)}\) \{{(.*?)\n\}}", css, re.S):
        if ".welcome" in match.group(1):
            return match.group(1)
    return ""


class WelcomeHeroLayoutTests(SimpleTestCase):
    def setUp(self):
        self.css = re.sub(r"/\*.*?\*/", "", CSS_PATH.read_text(encoding="utf-8"), flags=re.S)

    def test_tablet_keeps_copy_and_photo_side_by_side(self):
        tablet = media_block(self.css, "max-width: 900px")
        self.assertRegex(tablet, r"\.welcome \{[^}]*grid-template-columns: minmax\(0, 1fr\) minmax\(0, 17rem\)")

    def test_photo_never_jumps_above_the_title(self):
        self.assertNotRegex(self.css, r"\.welcome-photo \{[^}]*order:\s*-1")

    def test_phone_stacks_with_a_short_16_9_photo(self):
        phone = media_block(self.css, "max-width: 600px")
        self.assertRegex(phone, r"\.welcome \{[^}]*grid-template-columns: 1fr")
        self.assertRegex(phone, r"\.welcome-photo img \{[^}]*aspect-ratio: 16 / 9")


class WelcomeHeroMarkupTests(TestCase):
    def test_title_and_visit_cta_come_before_the_photo(self):
        html = self.client.get(reverse("home")).content.decode()
        section = html[html.index('class="welcome"'):]
        self.assertLess(section.index("welcome-title"), section.index("Planeje sua visita"))
        if "welcome-photo" in section:
            self.assertLess(section.index("Planeje sua visita"), section.index("welcome-photo"))
