from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.public.models import ChurchSettings, NewsIndexPage, NewsPage
from apps.public.whatsapp import build_whatsapp_share_url, build_whatsapp_url


class WhatsAppUrlTests(SimpleTestCase):
    def test_builds_wa_me_url_with_encoded_message(self):
        url = build_whatsapp_url("55 (27) 99999-9999", "Olá, igreja")
        self.assertEqual(url, "https://wa.me/5527999999999?text=Ol%C3%A1%2C%20igreja")

    def test_empty_number_returns_empty_url(self):
        self.assertEqual(build_whatsapp_url("", "Oi"), "")

    def test_share_url_has_no_church_number_and_encodes_page(self):
        url = build_whatsapp_share_url(
            "Culto especial",
            "http://testserver/noticias/culto-especial/",
        )
        self.assertEqual(
            url,
            "https://wa.me/?text=Culto%20especial%0Ahttp%3A//testserver/noticias/culto-especial/",
        )
        self.assertNotIn("wa.me/55", url)


class WhatsAppSharePageTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        settings = ChurchSettings.for_site(site)
        settings.whatsapp_number = "5527999999999"
        settings.save()
        root = site.root_page
        self.index = NewsIndexPage(title="Notícias", slug="noticias", intro="")
        root.add_child(instance=self.index)
        self.index.save_revision().publish()
        news = NewsPage(
            title="Culto especial no domingo",
            slug="culto-especial",
            intro="Venha celebrar.",
            body="<p>Culto às 19h.</p>",
        )
        self.index.add_child(instance=news)
        news.save_revision().publish()

    def test_public_pages_can_be_shared_via_whatsapp(self):
        home = self.client.get(reverse("home"))
        self.assertContains(home, "Compartilhar no WhatsApp")
        self.assertContains(home, "wa.me/?text=")

        news = self.client.get("/noticias/culto-especial/")
        self.assertContains(news, "Compartilhar no WhatsApp")
        self.assertContains(news, "wa.me/?text=")
        self.assertContains(news, "noticias/culto-especial")
        self.assertContains(news, "Culto%20especial%20no%20domingo")
