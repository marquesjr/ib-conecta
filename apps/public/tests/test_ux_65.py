import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from wagtail.models import Site

from apps.public.models import SermonIndexPage, SermonPage

TEMPLATES_DIR = Path(settings.BASE_DIR) / "templates"
# `{# #}` só vale numa linha; aberto sem fechar na mesma linha, vai para a página.
UNCLOSED_COMMENT = re.compile(r"\{#(?!.*#\})")


class TemplateCommentTests(SimpleTestCase):
    def test_no_template_has_multiline_short_comment(self):
        offenders = [
            f"{path.relative_to(TEMPLATES_DIR)}:{number}"
            for path in sorted(TEMPLATES_DIR.rglob("*.html"))
            for number, line in enumerate(path.read_text().splitlines(), start=1)
            if UNCLOSED_COMMENT.search(line)
        ]
        self.assertEqual(offenders, [], "Use {% comment %} para comentários em várias linhas.")


class SermonIndexCommentTests(TestCase):
    def test_sermon_list_does_not_leak_template_comment(self):
        root = Site.objects.get(is_default_site=True).root_page
        index = SermonIndexPage(title="Sermões", slug="sermoes")
        root.add_child(instance=index)
        index.save_revision().publish()
        sermon = SermonPage(
            title="Somente leitura",
            slug="somente-leitura",
            intro="Estudo escrito.",
            body="<p>Texto.</p>",
            media_url="",
        )
        index.add_child(instance=sermon)
        sermon.save_revision().publish()

        response = self.client.get("/sermoes/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Somente texto")
        self.assertNotContains(response, "{#")
        self.assertNotContains(response, "Marcar a exceção")
