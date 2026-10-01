from django.test import TestCase
from wagtail.models import Site

from apps.public.models import NewsIndexPage, NewsPage


class OtherNewsTests(TestCase):
    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page
        self.index = NewsIndexPage(title="Notícias", slug="noticias")
        root.add_child(instance=self.index)
        self.index.save_revision().publish()

    def make(self, title, slug):
        page = NewsPage(title=title, slug=slug, body="<p>Texto.</p>")
        self.index.add_child(instance=page)
        page.save_revision().publish()
        return page

    def test_news_lists_up_to_three_other_news_without_itself(self):
        current = self.make("Atual", "atual")
        for i in range(4):
            self.make(f"Outra {i}", f"outra-{i}")

        response = self.client.get(current.url)

        self.assertContains(response, "Outras notícias")
        self.assertContains(response, "Todas as notícias")
        self.assertEqual(len(response.context["other_news"]), 3)
        self.assertNotIn(current.pk, [n.pk for n in response.context["other_news"]])

    def test_only_news_has_no_other_news_section(self):
        current = self.make("Única", "unica")
        response = self.client.get(current.url)
        self.assertNotContains(response, "Outras notícias")
