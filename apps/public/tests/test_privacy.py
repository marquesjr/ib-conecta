from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.public.models import ChurchSettings, EventPage
from apps.public.privacy import (
    DEFAULT_RETREAT_SENSITIVE_RETAIN_DAYS,
    EVENT_REGISTRATION_RETENTION_DAYS,
    INBOX_RETENTION_MONTHS,
)
from apps.public.tests.test_retreats import publish_retreat


PRIVACY_DOC = Path(settings.BASE_DIR) / "docs" / "privacidade.md"
ADR_DOC = Path(settings.BASE_DIR) / "docs" / "adr" / "0011-lgpd-privacy-retention.md"
BACKUP_SCRIPT = Path(settings.BASE_DIR) / "scripts" / "backup.sh"
ENTRYPOINT = Path(settings.BASE_DIR) / "scripts" / "entrypoint.py"
DISCARD_SCRIPT = Path(settings.BASE_DIR) / "scripts" / "discard-sensitive-data.sh"

POLICY_PHRASES = (
    "Lei 13.709/2018",
    "Pedido de oração",
    "Quero conhecer",
    "Proteção de menores",
    "responsável legal",
    "discard_retreat_sensitive_data",
    "cookies",
    "youtube-nocookie.com",
)

OPS_PHRASES = (
    "discard_retreat_sensitive_data",
    "12 meses",
    "90 dias",
    "30 dias",
    "Pastor e comunicação",
    "Comissão de eventos",
    "BACKUP_SKIP_DISCARD",
    "scripts/discard-sensitive-data.sh",
)


class PrivacyPageTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        settings_obj = ChurchSettings.for_site(site)
        settings_obj.whatsapp_number = "5527999999999"
        settings_obj.whatsapp_default_message = "Olá, gostaria de conversar com a igreja"
        settings_obj.save()

    def test_privacy_page_is_public_and_covers_lgpd_topics(self):
        response = self.client.get(reverse("privacy"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Política de privacidade")
        self.assertContains(response, "Igreja Batista em Santa Leopoldina")
        self.assertContains(response, f"{DEFAULT_RETREAT_SENSITIVE_RETAIN_DAYS} dias")
        self.assertContains(response, f"{INBOX_RETENTION_MONTHS} meses")
        self.assertContains(response, f"{EVENT_REGISTRATION_RETENTION_DAYS} dias")
        self.assertContains(response, "wa.me/5527999999999")
        for phrase in POLICY_PHRASES:
            self.assertContains(response, phrase)

    def test_footer_and_sensitive_forms_link_to_privacy(self):
        home = self.client.get(reverse("home"))
        self.assertContains(home, reverse("privacy"))
        self.assertContains(home, "Privacidade")

        prayer = self.client.get(reverse("prayer_request"))
        self.assertContains(prayer, reverse("privacy"))
        self.assertContains(prayer, "política de privacidade")
        self.assertContains(prayer, "LGPD")

        know = self.client.get(reverse("know_church"))
        self.assertContains(know, reverse("privacy"))
        self.assertContains(know, "política de privacidade")
        self.assertContains(know, "LGPD")

        event = publish_retreat()
        retreat = self.client.get(event.url)
        self.assertContains(retreat, reverse("privacy"))
        self.assertContains(retreat, "Proteção de menores")
        self.assertContains(retreat, "responsável legal")
        self.assertContains(retreat, "política de privacidade")
        self.assertContains(retreat, "LGPD")


class PrivacyPolicyDocumentsTests(SimpleTestCase):
    def test_retention_constants_match_the_event_model(self):
        field = EventPage._meta.get_field("sensitive_retain_days")
        self.assertEqual(field.default, DEFAULT_RETREAT_SENSITIVE_RETAIN_DAYS)

    def test_ops_docs_and_adr_record_the_same_decisions(self):
        self.assertTrue(PRIVACY_DOC.is_file(), PRIVACY_DOC)
        self.assertTrue(ADR_DOC.is_file(), ADR_DOC)
        ops = PRIVACY_DOC.read_text(encoding="utf-8")
        adr = ADR_DOC.read_text(encoding="utf-8")
        for phrase in OPS_PHRASES:
            self.assertIn(phrase, ops, phrase)
        self.assertIn("/privacidade/", adr)
        self.assertIn("discard_retreat_sensitive_data", adr)
        self.assertIn("CMS", adr)

    def test_discard_runs_on_boot_and_before_backup(self):
        backup = BACKUP_SCRIPT.read_text(encoding="utf-8")
        entry = ENTRYPOINT.read_text(encoding="utf-8")
        self.assertIn("discard_retreat_sensitive_data", backup)
        self.assertIn("BACKUP_SKIP_DISCARD", backup)
        self.assertIn("discard_due_sensitive_data", entry)
        self.assertTrue(DISCARD_SCRIPT.is_file(), DISCARD_SCRIPT)
        self.assertIn("discard_retreat_sensitive_data", DISCARD_SCRIPT.read_text())
