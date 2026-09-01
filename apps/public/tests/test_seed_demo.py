from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.models import Site

from apps.accounts.models import Role
from apps.private_area.models import PrivateDocument, Song, SongStatus
from apps.public.bootstrap import bootstrap_cms
from apps.public.cms import NEWS_INDEX_SLUG
from apps.public.demo import DEMO_PASSWORD, DEMO_PIX_KEY, seed_demo
from apps.public.models import ChurchSettings, EventPage, NewsPage, SermonPage

User = get_user_model()


class SeedDemoTests(TestCase):
    def test_seed_demo_fills_empty_public_catalogs_and_visit_facts(self):
        bootstrap_cms()
        seed_demo()

        news = self.client.get(f"/{NEWS_INDEX_SLUG}/")
        self.assertEqual(news.status_code, 200)
        self.assertContains(news, "Mutirão de limpeza do templo")
        self.assertNotContains(news, "Nenhuma notícia publicada no momento.")

        agenda = self.client.get("/agenda/")
        self.assertEqual(agenda.status_code, 200)
        self.assertContains(agenda, "Culto de celebração")
        self.assertContains(agenda, "Retiro")
        self.assertNotContains(agenda, "Nenhum evento publicado no momento.")

        sermons = self.client.get("/sermoes/")
        self.assertEqual(sermons.status_code, 200)
        self.assertContains(sermons, "A graça que nos alcança")
        self.assertNotContains(sermons, "Nenhum sermão publicado no momento.")

        live = self.client.get("/ao-vivo/")
        self.assertEqual(live.status_code, 200)
        self.assertContains(live, "youtube-nocookie.com/embed/")

        visit = self.client.get(reverse("plan_visit"))
        self.assertContains(visit, "Rua do Comércio")
        self.assertContains(visit, "wa.me/5527999999999")
        self.assertContains(visit, "zona rural")

        contribute = self.client.get(reverse("contribute"))
        self.assertContains(contribute, DEMO_PIX_KEY)
        self.assertNotContains(
            contribute,
            "A chave PIX será publicada aqui quando a administração configurar.",
        )

        history = self.client.get("/historia/")
        self.assertEqual(history.status_code, 200)
        self.assertNotContains(
            history,
            "Edite este conteúdo no CMS Wagtail quando estiver pronto para publicar a versão final.",
        )

    def test_seed_demo_is_idempotent(self):
        bootstrap_cms()
        seed_demo()
        seed_demo()

        self.assertEqual(NewsPage.objects.filter(slug="mutirao-limpeza-templo").count(), 1)
        self.assertEqual(EventPage.objects.filter(slug="culto-celebracao").count(), 1)
        self.assertEqual(SermonPage.objects.filter(slug="a-graca-que-nos-alcanca").count(), 1)
        self.assertEqual(User.objects.filter(username="membro").count(), 1)

    def test_seed_demo_does_not_overwrite_custom_church_settings(self):
        bootstrap_cms()
        site = Site.objects.get(is_default_site=True)
        settings = ChurchSettings.for_site(site)
        settings.whatsapp_number = "5527111111111"
        settings.pix_key = "chave-ja-configurada@igreja.example"
        settings.save()

        seed_demo()

        settings.refresh_from_db()
        self.assertEqual(settings.whatsapp_number, "5527111111111")
        self.assertEqual(settings.pix_key, "chave-ja-configurada@igreja.example")

    def test_seed_demo_creates_private_preview_accounts(self):
        bootstrap_cms()
        seed_demo()

        user = User.objects.get(username="membro")
        self.assertEqual(user.profile.role, Role.MEMBER)
        self.assertTrue(self.client.login(username="membro", password=DEMO_PASSWORD))

        library = self.client.get(reverse("private_area:document_library"))
        self.assertEqual(library.status_code, 200)
        self.assertContains(library, "Comunicado aos membros")
        self.assertTrue(PrivateDocument.objects.filter(title="Comunicado aos membros").exists())

        self.client.logout()
        self.assertTrue(self.client.login(username="lider", password=DEMO_PASSWORD))
        songbook = self.client.get(reverse("private_area:songbook"))
        self.assertEqual(songbook.status_code, 200)
        self.assertContains(songbook, "Graça à beira do rio")
        song = Song.objects.get(title="Graça à beira do rio")
        self.assertEqual(song.status, SongStatus.PUBLISHED)
        self.assertTrue(song.authorized)

    @override_settings(DEBUG=False)
    def test_management_command_refuses_when_debug_is_off(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo")
