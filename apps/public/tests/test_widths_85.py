import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

CSS = (Path(settings.BASE_DIR) / "static/css/ib-conecta.css").read_text()


class NamedWidthTests(SimpleTestCase):
    def test_two_named_widths_are_defined(self):
        self.assertIn("--width-wide: 90rem", CSS)
        self.assertIn("--width-reading: 76rem", CSS)

    def test_page_containers_share_the_wide_width(self):
        for selector in (".site-header", ".site-footer", ".welcome", ".home-content", ".cms-page"):
            with self.subTest(selector=selector):
                rule = re.search(rf"^{re.escape(selector)} \{{[^}}]*\}}", CSS, re.M)
                self.assertIsNotNone(rule)
                self.assertIn("max-width: var(--width-wide)", rule.group(0))

    def test_inner_page_blocks_use_the_reading_width_aligned_left(self):
        self.assertIn(".cms-page > * { max-width: var(--width-reading); }", CSS)

    def test_no_container_uses_a_loose_page_width(self):
        self.assertNotRegex(CSS, r"max-width: (76|90|96)rem")
