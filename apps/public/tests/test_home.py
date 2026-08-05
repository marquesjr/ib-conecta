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

    def test_home_shows_next_service_and_visit_cta_within_two_clicks(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Culto de celebração")
        self.assertContains(response, "Domingo, 19h")
        self.assertContains(response, "Planeje sua visita")
        self.assertContains(response, reverse("plan_visit"))

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
