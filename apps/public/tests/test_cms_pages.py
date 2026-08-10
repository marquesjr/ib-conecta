from django.test import TestCase
from wagtail.models import Site

from apps.public.models import InstitutionalPage


class InstitutionalPagePublicTests(TestCase):
    def setUp(self):
        self.root = Site.objects.get(is_default_site=True).root_page

    def test_published_institutional_page_is_public_and_readable(self):
        page = InstitutionalPage(
            title="Nossa história",
            slug="historia",
            intro="Como a igreja nasceu em Santa Leopoldina.",
            body="<p>Desde o início anunciamos o evangelho na região.</p>",
        )
        self.root.add_child(instance=page)
        page.save_revision().publish()

        response = self.client.get("/historia/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nossa história")
        self.assertContains(response, "Como a igreja nasceu em Santa Leopoldina.")
        self.assertContains(response, "Desde o início anunciamos o evangelho na região.")
        self.assertContains(response, 'name="viewport"')

    def test_draft_institutional_page_is_not_public(self):
        page = InstitutionalPage(
            title="Crenças (rascunho)",
            slug="crencas",
            intro="Em preparação.",
            body="<p>Texto ainda não revisado.</p>",
            live=False,
        )
        self.root.add_child(instance=page)
        page.save_revision()

        response = self.client.get("/crencas/")
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "Texto ainda não revisado.", status_code=404)

    def test_unpublished_edits_do_not_replace_live_content(self):
        page = InstitutionalPage(
            title="Ministérios",
            slug="ministerios",
            intro="Como servir.",
            body="<p>Conteúdo publicado.</p>",
        )
        self.root.add_child(instance=page)
        page.save_revision().publish()

        page.refresh_from_db()
        page.body = "<p>Rascunho ainda não publicado.</p>"
        page.save_revision()

        response = self.client.get("/ministerios/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conteúdo publicado.")
        self.assertNotContains(response, "Rascunho ainda não publicado.")
