from pathlib import Path

from django.conf import settings
from django.test import TestCase
from wagtail.models import Site

from apps.public.models import SermonIndexPage, SermonPage


class ListRowAffordanceTests(TestCase):
    def test_sermon_rows_end_with_an_arrow(self):
        root = Site.objects.get(is_default_site=True).root_page
        index = SermonIndexPage(title="Sermões", slug="sermoes")
        root.add_child(instance=index)
        index.save_revision().publish()
        sermon = SermonPage(title="Graça", slug="graca", intro="Estudo.", body="<p>x</p>")
        index.add_child(instance=sermon)
        sermon.save_revision().publish()

        response = self.client.get("/sermoes/")

        self.assertContains(response, 'class="icon-arrow"')

    def test_row_has_straight_single_divider(self):
        css = (Path(settings.BASE_DIR) / "static/css/ib-conecta.css").read_text()
        self.assertIn(".register-entry { border-radius: 0;", css)
        self.assertNotIn(".register-entry { border-radius: 10px", css)
