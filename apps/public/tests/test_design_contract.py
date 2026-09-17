"""Guardas do sistema editorial aprovado pelo usuário."""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

CSS_PATH = Path(settings.BASE_DIR) / "static" / "css" / "ib-conecta.css"

ALLOWED = {"#faf9f6", "#f3f0eb", "#ded9d2", "#ffffff", "#262722", "#171916", "#62635d", "#862d36", "#69222b", "#b06e75", "#fff", "#000"}


def stylesheet():
    return re.sub(r"/\*.*?\*/", "", CSS_PATH.read_text(encoding="utf-8"), flags=re.S)


class DesignContractTests(SimpleTestCase):
    def test_the_stylesheet_exists_where_the_shell_expects_it(self):
        self.assertTrue(CSS_PATH.is_file(), f"{CSS_PATH} não encontrado")

    def test_no_shadows(self):
        offenders = []
        for prop in ("box-shadow", "text-shadow"):
            offenders += [
                f"{prop}: {value.strip()}"
                for value in re.findall(rf"^\s*{prop}\s*:\s*([^;]+);", stylesheet(), re.M)
                if value.strip() not in {"none", "0"}
            ]
        self.assertEqual(offenders, [], f"sombra encontrada: {offenders}")

    def test_colours_belong_to_the_editorial_palette(self):
        used = {value.lower() for value in re.findall(r"#[0-9a-fA-F]{3,8}\b", stylesheet())}
        stray = sorted(used - ALLOWED)
        self.assertEqual(stray, [], f"cor fora da paleta editorial: {stray}")

    def test_the_direction_contract_is_recorded_in_the_shell(self):
        """O contrato mora no template que todas as superfícies estendem."""
        base = Path(settings.BASE_DIR) / "templates" / "base.html"
        contract = base.read_text(encoding="utf-8")[:4000]
        for token in ("THESIS", "OWN-WORLD", "FIRST VIEWPORT", "Editorial acolhedor"):
            self.assertIn(token, contract, f"contrato sem {token}")
