from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.public.models import ChurchSettings
from apps.public.pix import crc16, normalize_key, pix_payload


class PixPayloadTests(SimpleTestCase):
    def test_crc16_matches_ccitt_false_reference(self):
        self.assertEqual(crc16("123456789"), "29B1")

    def test_payload_follows_br_code_layout(self):
        payload = pix_payload(
            "pix@ibsantaleopoldina.com.br",
            "Igreja Batista em Santa Leopoldina",
            "Santa Leopoldina",
            "email",
        )
        self.assertTrue(payload.startswith("000201"))
        self.assertIn("0014br.gov.bcb.pix0128pix@ibsantaleopoldina.com.br", payload)
        self.assertIn("52040000530398658", payload)
        self.assertIn("5925Igreja Batista em Santa L", payload)
        self.assertIn("6015Santa Leopoldin", payload)
        self.assertIn("62070503***", payload)
        self.assertEqual(payload[-8:-4], "6304")
        self.assertEqual(payload[-4:], crc16(payload[:-4]))

    def test_accents_are_removed_from_name_and_city(self):
        payload = pix_payload("abc", "Congregação", "Vitória", "random")
        self.assertIn("5911Congregacao", payload)
        self.assertIn("6007Vitoria", payload)

    def test_keys_are_normalized_by_type(self):
        self.assertEqual(normalize_key("(27) 99999-0000", "phone"), "+5527999990000")
        self.assertEqual(normalize_key("+55 27 99999-0000", "phone"), "+5527999990000")
        self.assertEqual(normalize_key("123.456.789-09", "cpf"), "12345678909")
        self.assertEqual(normalize_key("12.345.678/0001-95", "cnpj"), "12345678000195")
        self.assertEqual(normalize_key(" Pix@Igreja.org ", "email"), "pix@igreja.org")

    def test_missing_name_or_city_gives_no_payload(self):
        self.assertEqual(pix_payload("abc", "", "Cidade"), "")
        self.assertEqual(pix_payload("abc", "Nome", ""), "")
        self.assertEqual(pix_payload("", "Nome", "Cidade"), "")


class ContributePixCopyAndQrTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)
        self.settings.pix_key = "pix@ibsantaleopoldina.com.br"
        self.settings.pix_key_type = ChurchSettings.PixKeyType.EMAIL
        self.settings.pix_beneficiary_name = "Igreja Batista em Santa Leopoldina"
        self.settings.pix_city = "Santa Leopoldina"
        self.settings.save()

    def test_page_offers_copy_button_qr_code_and_copia_e_cola(self):
        response = self.client.get(reverse("contribute"))
        self.assertContains(response, 'data-copy-target="pix-key"')
        self.assertContains(response, "Copiar chave")
        self.assertContains(response, 'data-copy-done="Chave copiada!"')
        self.assertContains(response, 'role="status"')
        self.assertContains(response, "js/pix.js")
        self.assertContains(response, '<div class="pix-qr-code"><svg')
        self.assertContains(response, "QR Code PIX")
        self.assertContains(response, "PIX copia e cola")
        self.assertContains(response, "0014br.gov.bcb.pix")

    def test_qr_is_omitted_without_beneficiary_or_city(self):
        self.settings.pix_city = ""
        self.settings.save()
        response = self.client.get(reverse("contribute"))
        self.assertContains(response, "Copiar chave")
        self.assertNotContains(response, "pix-qr-code")
        self.assertNotContains(response, "PIX copia e cola")
