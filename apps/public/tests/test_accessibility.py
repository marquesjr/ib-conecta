"""Guardas do checklist WCAG 2.2 AA das páginas públicas (issue #38)."""

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse


class PublicAccessibilityTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_contact_fields_identify_their_purpose(self):
        """WCAG 1.3.5: nome, e-mail e telefone aceitam preenchimento automático."""
        for name in ("prayer_request", "know_church"):
            html = self.client.get(reverse(name)).content.decode()
            with self.subTest(page=name):
                self.assertInHTML(
                    '<input type="text" name="name" autocomplete="name" maxlength="120" id="id_name"'
                    + (" required" if name == "know_church" else "")
                    + ">",
                    html,
                )
                self.assertIn('autocomplete="email"', html)
                self.assertIn('type="tel" name="phone" autocomplete="tel"', html)

    def test_honeypot_is_hidden_from_assistive_technology(self):
        html = self.client.get(reverse("prayer_request")).content.decode()
        self.assertIn('<p class="hp" aria-hidden="true">', html)

    def test_non_field_errors_are_announced_without_nested_lists(self):
        response = self.client.post(
            reverse("know_church"),
            {"name": "Ana", "lgpd_consent": "on"},
        )
        html = response.content.decode()
        self.assertIn('<div class="form-errors" role="alert">', html)
        self.assertNotIn('<ul class="form-errors">', html)

    def test_retention_table_scrolls_inside_a_focusable_region(self):
        """axe scrollable-region-focusable: a tabela larga rola pelo teclado."""
        html = self.client.get(reverse("privacy")).content.decode()
        self.assertIn(
            '<div class="table-scroll" role="region" aria-label="Prazos de retenção e descarte" tabindex="0">',
            html,
        )

    def test_pages_have_a_meta_description(self):
        html = self.client.get(reverse("plan_visit")).content.decode()
        self.assertRegex(html, r'<meta name="description" content="[^"]{40,}"')
