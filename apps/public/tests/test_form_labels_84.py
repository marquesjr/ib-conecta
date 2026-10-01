from django.test import TestCase

from apps.public.forms import KnowChurchForm, PrayerRequestForm, RetreatRegistrationForm


class FormLabelTests(TestCase):
    def test_labels_have_no_colon_suffix(self):
        html = str(PrayerRequestForm().as_p())
        self.assertNotIn(":</label>", html)

    def test_optional_fields_are_marked_once_and_required_are_not(self):
        form = PrayerRequestForm()
        self.assertEqual(form.fields["phone"].label, "Telefone (opcional)")
        self.assertEqual(form.fields["body"].label, "Pedido de oração")
        self.assertEqual(KnowChurchForm().fields["message"].label, "Mensagem (opcional)")
        # Instanciar de novo não duplica a marca.
        self.assertEqual(PrayerRequestForm().fields["phone"].label, "Telefone (opcional)")

    def test_consent_checkbox_and_conditional_guardian_are_not_marked(self):
        fields = RetreatRegistrationForm().fields
        self.assertNotIn("(opcional)", fields["lgpd_consent"].label)
        self.assertNotIn("(opcional)", fields["transport_needed"].label)
        self.assertEqual(fields["guardian_name"].label, "Responsável legal")
        self.assertEqual(fields["boarding_point"].label, "Ponto de embarque (opcional)")

    def test_privacy_link_appears_once_in_contact_forms(self):
        for url in ("/pedido-de-oracao/", "/quero-conhecer/"):
            with self.subTest(url=url):
                body = self.client.get(url).content.decode()
                self.assertEqual(body.count("política de privacidade"), 1)
