"""Caixas de seleção seguem um padrão só: caixa à esquerda, rótulo clicável ao lado (issue #76)."""

import re
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

CSS_PATH = Path(settings.BASE_DIR) / "static" / "css" / "ib-conecta.css"


class CheckboxPatternTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_consent_checkbox_comes_before_its_label_in_a_check_field(self):
        for name in ("prayer_request", "know_church"):
            html = self.client.get(reverse(name)).content.decode()
            with self.subTest(page=name):
                match = re.search(
                    r'<div class="check-field">\s*<input type="checkbox" name="lgpd_consent"[^>]*>'
                    r'\s*<label for="id_lgpd_consent"',
                    html,
                )
                self.assertIsNotNone(match)

    def test_as_p_checkboxes_are_laid_out_like_check_field(self):
        """form.as_p põe o rótulo antes da caixa; o CSS inverte a ordem visual."""
        css = CSS_PATH.read_text(encoding="utf-8")
        self.assertIn(
            'form p:has(> input[type="checkbox"]) { display: grid; grid-template-columns: 24px minmax(0, 1fr);',
            css,
        )
        self.assertIn(
            'form p:has(> input[type="checkbox"]) > input[type="checkbox"] { grid-column: 1; grid-row: 1;',
            css,
        )
        self.assertIn(
            'form p:has(> input[type="checkbox"]) > label { grid-column: 2; grid-row: 1;',
            css,
        )
