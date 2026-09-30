import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from wagtail.models import Site

from apps.public.models import NewsIndexPage, NewsPage

DETAIL_TEMPLATES = [
    "news_page.html",
    "sermon_page.html",
    "event_page.html",
    "live_stream_page.html",
    "institutional_page.html",
]


class ShareAreaTemplateTests(SimpleTestCase):
    def test_detail_templates_keep_share_area_wrapper(self):
        templates_dir = Path(settings.BASE_DIR) / "templates" / "public"
        for name in DETAIL_TEMPLATES:
            with self.subTest(template=name):
                source = (templates_dir / name).read_text(encoding="utf-8")
                block = re.search(r"{% block share %}(.*?){% endblock %}", source, re.S)
                self.assertIsNotNone(block)
                self.assertIn('<div class="share-area">', block.group(1))


class ShareAreaRenderTests(TestCase):
    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page
        index = NewsIndexPage(title="Notícias", slug="noticias", intro="")
        root.add_child(instance=index)
        index.save_revision().publish()
        news = NewsPage(
            title="Culto especial",
            slug="culto-especial",
            intro="Venha.",
            body="<p>Culto às 19h.</p>",
        )
        index.add_child(instance=news)
        news.save_revision().publish()

    def test_news_share_button_is_inside_share_area(self):
        response = self.client.get("/noticias/culto-especial/")
        self.assertRegex(
            response.content.decode(),
            r'(?s)<div class="share-area">\s*(?:(?!</div>).)*Compartilhar no WhatsApp',
        )
