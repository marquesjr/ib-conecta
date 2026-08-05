from django.test import TestCase
from wagtail.models import Site

from apps.public.models import NewsIndexPage, NewsPage


class NewsPublicTests(TestCase):
    def setUp(self):
        self.root = Site.objects.get(is_default_site=True).root_page
        self.index = NewsIndexPage(
            title="Notícias",
            slug="noticias",
            intro="Comunicados da Igreja Batista em Santa Leopoldina.",
        )
        self.root.add_child(instance=self.index)
        self.index.save_revision().publish()

    def test_published_news_appears_on_index_and_detail(self):
        news = NewsPage(
            title="Culto especial no domingo",
            slug="culto-especial",
            intro="Venha celebrar conosco.",
            body="<p>Haverá culto especial às 19h.</p>",
        )
        self.index.add_child(instance=news)
        news.save_revision().publish()

        index_response = self.client.get("/noticias/")
        self.assertEqual(index_response.status_code, 200)
        self.assertContains(index_response, "Notícias")
        self.assertContains(index_response, "Culto especial no domingo")
        self.assertContains(index_response, "/noticias/culto-especial/")

        detail = self.client.get("/noticias/culto-especial/")
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Culto especial no domingo")
        self.assertContains(detail, "Venha celebrar conosco.")
        self.assertContains(detail, "Haverá culto especial às 19h.")
        self.assertContains(detail, 'name="viewport"')
        self.assertNotContains(detail, "autoplay")

    def test_draft_news_is_hidden_from_index_and_detail(self):
        news = NewsPage(
            title="Comunicado interno",
            slug="comunicado-interno",
            intro="Ainda em rascunho.",
            body="<p>Não deve aparecer no site.</p>",
            live=False,
        )
        self.index.add_child(instance=news)
        news.save_revision()

        index_response = self.client.get("/noticias/")
        self.assertEqual(index_response.status_code, 200)
        self.assertNotContains(index_response, "Comunicado interno")
        self.assertNotContains(index_response, "Não deve aparecer no site.")

        detail = self.client.get("/noticias/comunicado-interno/")
        self.assertEqual(detail.status_code, 404)
