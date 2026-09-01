"""Guarda mecânica do contrato de direção "Arquivo da Congregação".

O contrato está escrito como comentário no topo de ``templates/base.html``. Três das
suas regras são verificáveis por máquina, e são exatamente as que derivam sem ninguém
notar quando alguém copia um trecho de CSS de outro projeto:

- canto reto, sem raio;
- nenhuma sombra;
- toda cor vem da amostragem do comp aprovado, nunca estimada.

Sem este teste a única defesa seria alguém reparar num screenshot.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

CSS_PATH = Path(settings.BASE_DIR) / "static" / "css" / "ib-conecta.css"

# Amostrados de .impeccable/mocks/comp-arquivo-b-folha.png. O registro da amostragem
# está em .impeccable/surfaces/templates-public-home-html.md.
SAMPLED = {
    "#ece8e2",  # papel de arquivo
    "#d4d0ca",  # fio e goteira
    "#f9f9f9",  # chapa de montagem
    "#222527",  # grafite
    "#111313",  # preto de fotografia
    "#74706c",  # cinza de arquivo
    "#8b211a",  # vermelho de nanquim, o único sinal
}
# Derivados de estado, escurecidos a partir dos amostrados.
DERIVED = {"#6f1a14", "#15181a", "#f4f1ec"}
# Papel e tinta puros da impressão.
PRINT_ONLY = {"#fff", "#ffffff", "#000", "#000000"}

ALLOWED = SAMPLED | DERIVED | PRINT_ONLY


def stylesheet():
    return re.sub(r"/\*.*?\*/", "", CSS_PATH.read_text(encoding="utf-8"), flags=re.S)


class DesignContractTests(SimpleTestCase):
    def test_the_stylesheet_exists_where_the_shell_expects_it(self):
        self.assertTrue(CSS_PATH.is_file(), f"{CSS_PATH} não encontrado")

    def test_no_rounded_corners(self):
        """Chapa de canto reto é o contrato; um raio é outro mundo."""
        offenders = [
            value.strip()
            for value in re.findall(r"^\s*border-radius\s*:\s*([^;]+);", stylesheet(), re.M)
            if value.strip() not in {"0", "0px", "none"}
        ]
        self.assertEqual(offenders, [], f"border-radius encontrado: {offenders}")

    def test_no_shadows(self):
        offenders = []
        for prop in ("box-shadow", "text-shadow"):
            offenders += [
                f"{prop}: {value.strip()}"
                for value in re.findall(rf"^\s*{prop}\s*:\s*([^;]+);", stylesheet(), re.M)
                if value.strip() not in {"none", "0"}
            ]
        self.assertEqual(offenders, [], f"sombra encontrada: {offenders}")

    def test_every_colour_was_sampled_and_none_estimated(self):
        used = {value.lower() for value in re.findall(r"#[0-9a-fA-F]{3,8}\b", stylesheet())}
        stray = sorted(used - ALLOWED)
        self.assertEqual(stray, [], f"cor fora da paleta amostrada: {stray}")

    def test_the_ink_red_is_the_only_signal_colour(self):
        """Um segundo vermelho, ou um verde de sucesso, quebra a economia do mundo."""
        used = {value.lower() for value in re.findall(r"#[0-9a-fA-F]{6}\b", stylesheet())}
        reds = {value for value in used if value in {"#8b211a", "#6f1a14"}}
        self.assertLessEqual(len(reds), 2, f"mais de um vermelho de sinal: {sorted(reds)}")

    def test_the_direction_contract_is_recorded_in_the_shell(self):
        """O contrato mora no template que todas as superfícies estendem."""
        base = Path(settings.BASE_DIR) / "templates" / "base.html"
        contract = base.read_text(encoding="utf-8")[:4000]
        for token in ("THESIS", "OWN-WORLD", "FIRST VIEWPORT", "Arquivo da Congregação"):
            self.assertIn(token, contract, f"contrato sem {token}")
