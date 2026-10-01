from pathlib import Path

from django.conf import settings
from django.test import TestCase


class FooterPrivacyLinkTests(TestCase):
    def test_full_footer_privacy_link_has_touch_height(self):
        response = self.client.get("/")
        self.assertContains(response, 'class="footer-privacy"')
        css = (Path(settings.BASE_DIR) / "static/css/ib-conecta.css").read_text()
        self.assertRegex(css, r"\.footer-privacy \{[^}]*min-height: 24px")
