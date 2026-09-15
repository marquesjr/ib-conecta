from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from wagtail.test.utils.form_data import nested_form_data, rich_text

from apps.accounts.models import Role
from apps.public.bootstrap import bootstrap_cms
from apps.public.models import NewsIndexPage, NewsPage
from apps.public.tests.test_cms_permissions import make_user

GUIDE_PATH = Path(settings.BASE_DIR) / "docs" / "treinamento-administracao.md"

REQUIRED_HEADINGS = (
    "Roteiro de treinamento da administração",
    "Entrar no CMS",
    "Notícias",
    "Páginas institucionais",
    "Agenda e eventos",
    "Sermões",
    "Ao vivo",
    "Publicar, revisar e despublicar",
    "Checklist de publicação",
    "Erros comuns",
    "Quem acionar",
)

REQUIRED_PHRASES = (
    "Salvar rascunho",
    "Publicar",
    "Despublicar",
    "Pré-visualizar",
    "Adicionar subpágina",
    "Título",
    "texto alternativo",
    "Imagem",
    "Data",
    "visibilidade",
    "Pastor",
    "TI / administração",
    "/admin/",
    "/noticias/",
    "/agenda/",
    "/sermoes/",
    "/ao-vivo/",
)


class TrainingGuideDocumentTests(SimpleTestCase):
    def test_guide_covers_login_editorial_surfaces_and_support(self):
        self.assertTrue(GUIDE_PATH.is_file(), GUIDE_PATH)
        text = GUIDE_PATH.read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, text, heading)
        for phrase in REQUIRED_PHRASES:
            self.assertIn(phrase, text, phrase)


class CmsEditorTrainingFlowTests(TestCase):
    """Full publish → review → unpublish cycle from the Wagtail admin (issue #39)."""

    def setUp(self):
        bootstrap_cms()
        self.editor = make_user("comms", Role.COMMUNICATION)
        self.client.login(username="comms", password="senha-segura-123")
        self.news_index = NewsIndexPage.objects.get(slug="noticias")

    def test_communication_account_home_links_to_cms(self):
        home = self.client.get(reverse("accounts:account_home"))
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, "Publicar conteúdo (CMS)")
        self.assertContains(home, reverse("wagtailadmin_home"))

    def test_communication_draft_publish_unpublish_news_via_admin(self):
        add_url = reverse(
            "wagtailadmin_pages:add",
            args=("public", "newspage", self.news_index.id),
        )
        form = self.client.get(add_url)
        self.assertEqual(form.status_code, 200)
        self.assertContains(form, "Notícia")

        draft_payload = nested_form_data(
            {
                "title": "Comunicado de treinamento",
                "slug": "comunicado-de-treinamento",
                "intro": "Aviso para a congregação.",
                "body": rich_text("<p>Culto no horário habitual.</p>"),
                "action-save-draft": "action-save-draft",
            }
        )
        created = self.client.post(add_url, draft_payload)
        self.assertEqual(created.status_code, 302, created.content[:500])

        news = NewsPage.objects.get(slug="comunicado-de-treinamento")
        self.assertFalse(news.live)
        public_url = "/noticias/comunicado-de-treinamento/"
        self.assertEqual(self.client.get(public_url).status_code, 404)

        edit_url = reverse("wagtailadmin_pages:edit", args=(news.id,))
        preview = self.client.get(edit_url)
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, "Comunicado de treinamento")

        publish_payload = nested_form_data(
            {
                "title": "Comunicado de treinamento",
                "slug": "comunicado-de-treinamento",
                "intro": "Aviso para a congregação.",
                "body": rich_text("<p>Culto no horário habitual.</p>"),
                "action-publish": "action-publish",
            }
        )
        published = self.client.post(edit_url, publish_payload)
        self.assertEqual(published.status_code, 302, published.content[:500])

        news.refresh_from_db()
        self.assertTrue(news.live)
        live = self.client.get(public_url)
        self.assertEqual(live.status_code, 200)
        self.assertContains(live, "Comunicado de treinamento")
        self.assertContains(live, "Culto no horário habitual.")

        unpublish_url = reverse("wagtailadmin_pages:unpublish", args=(news.id,))
        confirm = self.client.get(unpublish_url)
        self.assertEqual(confirm.status_code, 200)
        unpublished = self.client.post(unpublish_url)
        self.assertEqual(unpublished.status_code, 302)

        news.refresh_from_db()
        self.assertFalse(news.live)
        self.assertEqual(self.client.get(public_url).status_code, 404)

    def test_member_does_not_get_cms_link_or_publish_access(self):
        self.client.logout()
        member = make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        home = self.client.get(reverse("accounts:account_home"))
        self.assertNotContains(home, "Publicar conteúdo (CMS)")
        add_url = reverse(
            "wagtailadmin_pages:add",
            args=("public", "newspage", self.news_index.id),
        )
        denied = self.client.get(add_url)
        self.assertIn(denied.status_code, (302, 403))
