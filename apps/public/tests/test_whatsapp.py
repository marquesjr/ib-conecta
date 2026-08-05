from django.test import SimpleTestCase

from apps.public.whatsapp import build_whatsapp_url


class WhatsAppUrlTests(SimpleTestCase):
    def test_builds_wa_me_url_with_encoded_message(self):
        url = build_whatsapp_url("55 (27) 99999-9999", "Olá, igreja")
        self.assertEqual(url, "https://wa.me/5527999999999?text=Ol%C3%A1%2C%20igreja")

    def test_empty_number_returns_empty_url(self):
        self.assertEqual(build_whatsapp_url("", "Oi"), "")
