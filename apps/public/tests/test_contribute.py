from django.test import TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.public.models import ChurchSettings


class ContributePageTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)
        self.settings.pix_key = "pix@ibsantaleopoldina.com.br"
        self.settings.pix_key_type = ChurchSettings.PixKeyType.EMAIL
        self.settings.pix_beneficiary_name = "Igreja Batista em Santa Leopoldina"
        self.settings.pix_city = "Santa Leopoldina"
        self.settings.pix_instructions = "Dízimos e ofertas voluntárias pelo PIX da igreja."
        self.settings.instagram_url = "https://instagram.com/ibsantaleopoldina"
        self.settings.facebook_url = "https://facebook.com/ibsantaleopoldina"
        self.settings.youtube_url = "https://youtube.com/@ibsantaleopoldina"
        self.settings.save()

    def test_visitor_sees_admin_configured_pix_without_card_or_bank_capture(self):
        response = self.client.get(reverse("contribute"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contribuições")
        self.assertContains(response, "pix@ibsantaleopoldina.com.br")
        self.assertContains(response, "Igreja Batista em Santa Leopoldina")
        self.assertContains(response, "Santa Leopoldina")
        self.assertContains(response, "Dízimos e ofertas voluntárias")
        self.assertContains(response, "não processa pagamentos")
        self.assertNotContains(response, "cartão")
        self.assertNotContains(response, "cvv")
        self.assertNotContains(response, 'name="card"')
        self.assertNotContains(response, "<form")

    def test_home_and_nav_link_to_contributions(self):
        home = self.client.get(reverse("home"))
        self.assertContains(home, reverse("contribute"))
        self.assertContains(home, "Contribuir")

    def test_footer_shows_configured_social_links_consistently(self):
        home = self.client.get(reverse("home"))
        contribute = self.client.get(reverse("contribute"))
        for response in (home, contribute):
            self.assertContains(response, "https://instagram.com/ibsantaleopoldina")
            self.assertContains(response, "https://facebook.com/ibsantaleopoldina")
            self.assertContains(response, "https://youtube.com/@ibsantaleopoldina")
            self.assertContains(response, "Instagram")
            self.assertContains(response, "Facebook")
            self.assertContains(response, "YouTube")

    def test_empty_social_and_pix_are_omitted(self):
        self.settings.pix_key = ""
        self.settings.instagram_url = ""
        self.settings.facebook_url = ""
        self.settings.youtube_url = ""
        self.settings.save()
        response = self.client.get(reverse("contribute"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "pix@ibsantaleopoldina.com.br")
        self.assertNotContains(response, "instagram.com")
        self.assertNotContains(response, "facebook.com")
        self.assertContains(response, "chave PIX")
