import re

from django.test import TestCase
from wagtail.models import Site

from apps.public.bootstrap import ensure_institutional_pages, ensure_news_index
from apps.public.cms import INSTITUTIONAL_PLACEHOLDER
from apps.public.models import InstitutionalPage


def nav_groups(html):
    """Mapa {nome do grupo: HTML do dropdown} da navegação principal."""
    return {
        re.sub(r"<[^>]+>", "", summary).strip(): body
        for summary, body in re.findall(
            r'<details class="nav-group">\s*<summary>(.*?)</summary><div class="nav-dropdown">(.*?)</div></details>',
            html,
            re.S,
        )
    }


class MenuStructureTests(TestCase):
    def setUp(self):
        Site.objects.get(is_default_site=True)
        ensure_news_index()

    def test_participe_groups_the_ways_to_take_part(self):
        groups = nav_groups(self.client.get("/").content.decode())
        participe = groups["Participe"]
        for text in ("Quero conhecer", "Pedido de oração", "Contribuir"):
            self.assertIn(text, participe)

    def test_news_is_in_the_first_level_not_in_a_dropdown(self):
        html = self.client.get("/").content.decode()
        for body in nav_groups(html).values():
            self.assertNotIn(">Notícias<", body)
        self.assertRegex(html, r'(?s)<nav id="primary-nav".*?</details>\s*<a href="/noticias/">Notícias</a>')

    def test_unwritten_institutional_pages_stay_out_of_the_menu(self):
        ensure_institutional_pages()
        self.assertTrue(InstitutionalPage.objects.filter(body__contains=INSTITUTIONAL_PLACEHOLDER).exists())
        groups = nav_groups(self.client.get("/").content.decode())
        self.assertNotIn("Conheça a igreja", groups)

    def test_written_institutional_page_appears_under_conheca_a_igreja(self):
        ensure_institutional_pages()
        page = InstitutionalPage.objects.get(slug="historia")
        page.body = "<p>Fundada em 1999 por famílias da região.</p>"
        page.save_revision().publish()
        groups = nav_groups(self.client.get("/").content.decode())
        self.assertIn("Nossa história", groups["Conheça a igreja"])
        self.assertNotIn("Crenças", groups["Conheça a igreja"])
