import re

from django.test import TestCase

from apps.public.forms import RetreatRegistrationForm
from apps.public.tests.test_retreats import family_form_payload, publish_retreat


def fieldset_legends(html: str) -> list[str]:
    return re.findall(r"<legend>([^<]+)</legend>", html)


class RetreatFormSectionsTests(TestCase):
    def test_form_is_split_into_named_sections(self):
        publish_retreat()
        response = self.client.get("/agenda/retiro-familias/")
        html = response.content.decode()

        legends = fieldset_legends(html)
        for title in ("Você", "Responsável e emergência", "Saúde", "Transporte e hospedagem", "Familiares"):
            self.assertIn(title, legends)
        self.assertLess(html.index("<legend>Você</legend>"), html.index("<legend>Familiares</legend>"))
        self.assertLess(html.index("<legend>Familiares</legend>"), html.index('name="lgpd_consent"'))
        self.assertContains(response, 'class="form-grid"')
        self.assertContains(response, "js/retreat-form.js")

    def test_every_field_belongs_to_one_section_or_the_closing_block(self):
        form = RetreatRegistrationForm()
        in_sections = [field.name for section in form.sections() for field in section["fields"]]
        closing = [field.name for field in form.closing_fields()]

        self.assertEqual(len(in_sections), len(set(in_sections)))
        self.assertEqual(closing, ["lgpd_consent"])
        self.assertEqual(sorted(in_sections + closing), sorted(form.fields))

    def test_empty_family_blocks_are_marked_and_add_button_is_offered(self):
        publish_retreat()
        response = self.client.get("/agenda/retiro-familias/")

        self.assertNotContains(response, "Familiar 1 (opcional)")
        self.assertEqual(response.content.decode().count('class="family-member" data-empty'), 2)
        self.assertContains(response, "data-add-family")
        self.assertContains(response, "Adicionar familiar")
        self.assertContains(response, "<template data-family-template>")
        self.assertContains(response, 'name="family-__prefix__-name"')

    def test_filled_family_block_stays_visible_after_validation_error(self):
        publish_retreat()
        response = self.client.post(
            "/agenda/retiro-familias/inscrever/",
            family_form_payload({"emergency_name": ""}),
        )

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertEqual(html.count('class="family-member" data-empty'), 1)
        self.assertIn('value="Pedro Silva"', html)
