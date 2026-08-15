from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.accounts.models import AuditLog, Role
from apps.public.models import ChurchSettings, KnowChurchContact

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


class KnowChurchPublicTests(TestCase):
    def setUp(self):
        cache.clear()
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)
        self.settings.whatsapp_number = "5527999999999"
        self.settings.whatsapp_default_message = "Olá, gostaria de conversar com a igreja"
        self.settings.save()

    def test_visitor_submits_contact_with_lgpd_consent_and_whatsapp_shortcut(self):
        page = self.client.get(reverse("know_church"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Quero conhecer a igreja")
        self.assertContains(page, "LGPD")
        self.assertContains(page, "wa.me/5527999999999")
        self.assertContains(page, "WhatsApp")

        response = self.client.post(
            reverse("know_church"),
            {
                "name": "Ana Costa",
                "email": "ana@example.com",
                "phone": "27988887777",
                "message": "Gostaria de visitar no domingo.",
                "lgpd_consent": "on",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recebemos seu contato")
        contact = KnowChurchContact.objects.get()
        self.assertEqual(contact.name, "Ana Costa")
        self.assertEqual(contact.email, "ana@example.com")
        self.assertTrue(contact.lgpd_consent)
        self.assertEqual(contact.status, KnowChurchContact.Status.NEW)

    def test_contact_requires_consent_and_email_or_phone(self):
        missing_consent = self.client.post(
            reverse("know_church"),
            {
                "name": "Ana",
                "email": "ana@example.com",
            },
        )
        self.assertEqual(missing_consent.status_code, 200)
        self.assertEqual(KnowChurchContact.objects.count(), 0)

        missing_contact = self.client.post(
            reverse("know_church"),
            {
                "name": "Ana",
                "lgpd_consent": "on",
            },
        )
        self.assertEqual(missing_contact.status_code, 200)
        self.assertEqual(KnowChurchContact.objects.count(), 0)

    def test_honeypot_and_rate_limit_protect_know_church_form(self):
        self.client.post(
            reverse("know_church"),
            {
                "name": "Bot",
                "email": "bot@example.com",
                "lgpd_consent": "on",
                "website": "http://spam.test",
            },
            follow=True,
        )
        self.assertEqual(KnowChurchContact.objects.count(), 0)

        payload = {
            "name": "Visitante",
            "phone": "27999990000",
            "lgpd_consent": "on",
        }
        for _ in range(5):
            self.client.post(reverse("know_church"), payload)
        self.assertEqual(KnowChurchContact.objects.count(), 5)
        blocked = self.client.post(reverse("know_church"), payload, follow=True)
        self.assertContains(blocked, "Muitas tentativas")
        self.assertEqual(KnowChurchContact.objects.count(), 5)


class KnowChurchFollowUpTests(TestCase):
    def setUp(self):
        self.item = KnowChurchContact.objects.create(
            name="Carla Nunes",
            email="carla@example.com",
            message="Quero conhecer a igreja",
            lgpd_consent=True,
        )

    def test_communication_updates_status_and_audit_omits_message(self):
        make_user("comms", Role.COMMUNICATION)
        self.client.login(username="comms", password="senha-segura-123")

        response = self.client.get(reverse("accounts:know_church_contacts"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carla Nunes")
        self.assertContains(response, "carla@example.com")

        response = self.client.post(
            reverse("accounts:know_church_contact_status", args=[self.item.pk]),
            {"status": KnowChurchContact.Status.IN_PROGRESS},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, KnowChurchContact.Status.IN_PROGRESS)

        entry = AuditLog.objects.get(action="know_church_contact_status_changed")
        self.assertEqual(entry.metadata.get("contact_id"), self.item.pk)
        self.assertNotIn("Quero conhecer a igreja", str(entry.metadata))

    def test_pastor_can_access_and_member_cannot(self):
        make_user("pastor", Role.PASTOR)
        self.client.login(username="pastor", password="senha-segura-123")
        self.assertEqual(
            self.client.get(reverse("accounts:know_church_contacts")).status_code,
            200,
        )

        self.client.logout()
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        self.assertEqual(
            self.client.get(reverse("accounts:know_church_contacts")).status_code,
            403,
        )
