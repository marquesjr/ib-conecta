from django.test import TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.public.models import ChurchSettings


class HomePageTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)
        self.settings.evangelistic_headline = "Jesus te convida a conhecer a graça de Deus"
        self.settings.evangelistic_message = (
            "A Igreja Batista em Santa Leopoldina celebra a Palavra e acolhe visitantes."
        )
        self.settings.next_service_label = "Culto de celebração"
        self.settings.next_service_when = "Domingo, 19h"
        self.settings.next_service_description = "Venha participar conosco do próximo culto."
        self.settings.address_line = "Rua da Igreja, Centro, Santa Leopoldina - ES"
        self.settings.address_references = "Próximo ao ponto de ônibus da praça"
        self.settings.whatsapp_number = "5527999999999"
        self.settings.whatsapp_default_message = "Olá, gostaria de conversar com a igreja"
        self.settings.whatsapp_welcome_text = (
            "Fale conosco pelo WhatsApp para dúvidas, conversa, desabafo ou pedido de oração. "
            "Responderemos assim que possível — não é um canal de plantão 24 horas."
        )
        self.settings.save()

    def test_home_returns_ok_with_project_name(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "IB Conecta")
        self.assertContains(response, "css/ib-conecta.css")
        self.assertContains(response, "Ir para o conteúdo")

    def test_home_shows_next_service_and_visit_cta_within_two_clicks(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Culto de celebração")
        self.assertContains(response, "Domingo, 19h")
        self.assertContains(response, "Planeje sua visita")
        self.assertContains(response, reverse("plan_visit"))
        self.assertContains(response, "Pedido de oração")
        self.assertContains(response, reverse("prayer_request"))
        self.assertContains(response, "Quero conhecer")
        self.assertContains(response, reverse("know_church"))
        self.assertContains(response, reverse("privacy"))
        self.assertContains(response, "Privacidade")

        # Second click: visit page has address/references and contact.
        visit = self.client.get(reverse("plan_visit"))
        self.assertEqual(visit.status_code, 200)
        self.assertContains(visit, "Rua da Igreja, Centro, Santa Leopoldina - ES")
        self.assertContains(visit, "Próximo ao ponto de ônibus da praça")
        self.assertContains(visit, "wa.me/5527999999999")

    def test_home_has_configurable_whatsapp_and_no_autoplay_video(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "wa.me/5527999999999")
        self.assertContains(response, "Ol%C3%A1%2C%20gostaria%20de%20conversar%20com%20a%20igreja")

        self.assertContains(response, "não é um canal de plantão 24 horas")
        self.assertContains(response, 'href="#nota-whatsapp"')
        self.assertContains(response, 'id="nota-whatsapp"')
        self.assertNotContains(response, "autoplay")
        self.assertNotContains(response, "<video")

    def test_footer_whatsapp_uses_admin_configuration(self):
        self.settings.whatsapp_number = "5527888888888"
        self.settings.whatsapp_default_message = "Mensagem configurada"
        self.settings.save()
        response = self.client.get(reverse("home"))
        self.assertContains(response, "wa.me/5527888888888")
        self.assertContains(response, "Mensagem%20configurada")
        self.assertNotContains(response, "5527999999999")

    def test_home_title_is_the_church_name(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "<title>Igreja Batista em Santa Leopoldina</title>", html=False)

    def test_welcome_reference_is_shown_and_can_be_hidden(self):
        self.settings.evangelistic_reference = "Inspirado em Mateus 11:28 e Atos 2:42-47."
        self.settings.save()
        self.assertContains(self.client.get(reverse("home")), "Inspirado em Mateus 11:28 e Atos 2:42-47.")
        self.settings.evangelistic_reference = ""
        self.settings.save()
        self.assertNotContains(self.client.get(reverse("home")), 'class="welcome-reference"')


class WelcomeTextMigrationTests(TestCase):
    def test_existing_settings_receive_the_new_welcome_text(self):
        settings = ChurchSettings.for_site(Site.objects.get(is_default_site=True))
        self.assertEqual(settings.evangelistic_headline, "Um lugar para viver a fé. Uma família para caminhar com você.")
        self.assertTrue(settings.evangelistic_message.startswith("Em Cristo encontramos esperança"))
        self.assertEqual(settings.evangelistic_reference, "Inspirado em Mateus 11:28 e Atos 2:42-47.")


class PageTitleTests(TestCase):
    def test_inner_pages_end_with_the_church_name(self):
        for name in ("plan_visit", "prayer_request", "contribute", "privacy"):
            body = self.client.get(reverse(name)).content.decode()
            self.assertRegex(body, r"<title>[^<]+ — Igreja Batista em Santa Leopoldina</title>", name)
            self.assertNotIn("— IB Conecta</title>", body)



class FooterLocationTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)
        self.settings.address_line = "Av. Pres. Vargas, 38 - Centro, Santa Leopoldina - ES, 29640-000"
        self.settings.map_url = "https://maps.app.goo.gl/wZdYwYxUpUJpA1DG9"
        self.settings.save()

    def test_footer_shows_full_address_and_lazy_map(self):
        response = self.client.get(reverse("home"))
        self.assertContains(
            response,
            "<address>Av. Pres. Vargas, 38 - Centro, Santa Leopoldina - ES, 29640-000</address>",
            html=True,
        )
        self.assertContains(
            response,
            "https://www.google.com/maps?q=Av.%20Pres.%20Vargas%2C%2038%20-%20Centro%2C"
            "%20Santa%20Leopoldina%20-%20ES%2C%2029640-000&amp;output=embed",
        )
        self.assertContains(response, 'loading="lazy"')
        self.assertContains(response, 'title="Mapa com a localização da Igreja Batista')
        self.assertContains(response, "Abrir no Google Maps")
        self.assertContains(response, "https://maps.app.goo.gl/wZdYwYxUpUJpA1DG9")

    def test_footer_hides_map_without_address(self):
        self.settings.address_line = ""
        self.settings.save()
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "google.com/maps")
