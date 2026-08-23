from django.test import TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.public.models import ChurchSettings


class PlanVisitPageTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)
        self.settings.service_times = "Domingo 09h (escola bíblica) e 19h (culto)"
        self.settings.address_line = "Rua da Igreja, Centro"
        self.settings.address_references = "Em frente ao mercado municipal"
        self.settings.map_url = "https://maps.example.com/ibsl"
        self.settings.accessibility_info = "Acesso por rampa na entrada lateral"
        self.settings.transport_info = (
            "Há caronas saindo da zona rural — fale no WhatsApp para combinar."
        )
        self.settings.whatsapp_number = "5527999999999"
        self.settings.whatsapp_default_message = "Olá, quero planejar minha visita"
        self.settings.whatsapp_welcome_text = (
            "Use o WhatsApp para dúvidas, conversa ou oração. "
            "Atendimento conforme disponibilidade da equipe, sem plantão 24h."
        )
        self.settings.save()

    def test_plan_visit_covers_schedule_location_access_and_transport(self):
        response = self.client.get(reverse("plan_visit"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Planeje sua visita")
        self.assertContains(response, "Domingo 09h")
        self.assertContains(response, "Rua da Igreja, Centro")
        self.assertContains(response, "Em frente ao mercado municipal")
        self.assertContains(response, "https://maps.example.com/ibsl")
        self.assertContains(response, "Acesso por rampa na entrada lateral")
        self.assertContains(response, "zona rural")
        self.assertContains(response, "wa.me/5527999999999")
        self.assertContains(response, "sem plantão 24h")
        self.assertContains(response, 'href="#nota-whatsapp"')
        self.assertContains(response, 'id="nota-whatsapp"')
        self.assertNotContains(response, "autoplay")
