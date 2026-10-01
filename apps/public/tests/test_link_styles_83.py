import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.public.models import ChurchSettings

TEMPLATES = Path(settings.BASE_DIR) / "templates"
PLAIN_BACK_LINK = re.compile(r'<a href="[^"]*">Voltar')


class BackLinkTests(SimpleTestCase):
    def test_no_template_has_a_plain_underlined_back_link(self):
        offenders = [
            str(path.relative_to(TEMPLATES))
            for path in sorted(TEMPLATES.rglob("*.html"))
            if PLAIN_BACK_LINK.search(path.read_text())
        ]
        self.assertEqual(offenders, [], "Use class=\"text-link back-link\" nos links Voltar.")

    def test_design_doc_defines_when_to_use_each_link_style(self):
        design = (Path(settings.BASE_DIR) / "DESIGN.md").read_text()
        self.assertIn("### Links", design)
        for term in ("Link com seta", "Sublinhado", "Botão"):
            self.assertIn(term, design)


class PlanVisitMapLinkTests(TestCase):
    def test_map_link_uses_the_arrow_style(self):
        site = Site.objects.get(is_default_site=True)
        settings_obj = ChurchSettings.for_site(site)
        settings_obj.map_url = "https://maps.example/igreja"
        settings_obj.save()
        body = self.client.get(reverse("plan_visit")).content.decode()
        self.assertRegex(body, r'<a class="text-link" href="https://maps.example/igreja"[^>]*>Abrir mapa\s*<svg class="icon-arrow"')
