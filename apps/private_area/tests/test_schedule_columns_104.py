from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class RosterColumnsTests(SimpleTestCase):
    def test_roster_rows_share_the_list_columns(self):
        css = (Path(settings.BASE_DIR) / "static/css/ib-conecta.css").read_text()
        self.assertIn(".service-roster li { grid-column: 1 / -1; grid-template-columns: subgrid; }", css)
        self.assertRegex(css, r"\.service-roster \{ display: grid; grid-template-columns: 9rem minmax\(0, 1fr\) auto auto; \}")
