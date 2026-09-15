from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.accounts.models import AuditLog, Role
from apps.public.models import ChurchSettings, PrayerRequest

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


class PrayerRequestPublicTests(TestCase):
    def setUp(self):
        cache.clear()
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)
        self.settings.whatsapp_number = "5527999999999"
        self.settings.whatsapp_default_message = "Olá, gostaria de conversar com a igreja"
        self.settings.save()

    def test_visitor_can_submit_named_prayer_request_with_consent(self):
        page = self.client.get(reverse("prayer_request"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Pedido de oração")
        self.assertContains(page, "anônima")
        self.assertContains(page, "wa.me/5527999999999")
        self.assertContains(page, "WhatsApp")
        self.assertContains(page, reverse("privacy"))

        response = self.client.post(
            reverse("prayer_request"),
            {
                "name": "Maria Silva",
                "email": "maria@example.com",
                "phone": "27999990000",
                "body": "Orem pela saúde da minha família.",
                "lgpd_consent": "on",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pedido de oração recebido")
        self.assertNotContains(response, "Orem pela saúde da minha família.")
        request = PrayerRequest.objects.get()
        self.assertFalse(request.is_anonymous)
        self.assertEqual(request.name, "Maria Silva")
        self.assertEqual(request.body, "Orem pela saúde da minha família.")
        self.assertEqual(request.status, PrayerRequest.Status.NEW)

    def test_visitor_can_submit_anonymous_prayer_request(self):
        response = self.client.post(
            reverse("prayer_request"),
            {
                "is_anonymous": "on",
                "name": "não deve ser gravado",
                "email": "anon@example.com",
                "body": "Pedido confidencial sem identificação.",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pedido de oração recebido")
        request = PrayerRequest.objects.get()
        self.assertTrue(request.is_anonymous)
        self.assertEqual(request.name, "")
        self.assertEqual(request.email, "")
        self.assertEqual(request.body, "Pedido confidencial sem identificação.")

    def test_named_prayer_request_requires_name_and_consent(self):
        response = self.client.post(
            reverse("prayer_request"),
            {"body": "Preciso de oração."},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PrayerRequest.objects.count(), 0)

    def test_honeypot_submission_is_silently_dropped(self):
        response = self.client.post(
            reverse("prayer_request"),
            {
                "is_anonymous": "on",
                "body": "Sou um robô enviando spam de oração.",
                "website": "https://spam.example",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pedido de oração recebido")
        self.assertEqual(PrayerRequest.objects.count(), 0)

    def test_rate_limit_blocks_repeated_submissions(self):
        payload = {
            "is_anonymous": "on",
            "body": "Pedido repetido para testar limite.",
        }
        for _ in range(5):
            response = self.client.post(reverse("prayer_request"), payload, follow=True)
            self.assertContains(response, "Pedido de oração recebido")
        self.assertEqual(PrayerRequest.objects.count(), 5)

        blocked = self.client.post(reverse("prayer_request"), payload, follow=True)
        self.assertContains(blocked, "Muitas tentativas")
        self.assertEqual(PrayerRequest.objects.count(), 5)

    def test_prayer_body_is_not_exposed_on_public_pages(self):
        PrayerRequest.objects.create(
            is_anonymous=True,
            body="Segredo pastoral jamais público",
        )
        for url in (
            reverse("home"),
            reverse("plan_visit"),
            reverse("prayer_request"),
            reverse("know_church"),
        ):
            response = self.client.get(url)
            self.assertNotContains(response, "Segredo pastoral jamais público")


class PrayerRequestFollowUpTests(TestCase):
    def setUp(self):
        self.item = PrayerRequest.objects.create(
            name="João Pedro",
            email="joao@example.com",
            body="Peço oração pelo emprego.",
            lgpd_consent=True,
        )

    def test_pastor_lists_and_updates_status_without_auditing_body(self):
        make_user("pastor", Role.PASTOR)
        self.client.login(username="pastor", password="senha-segura-123")

        list_url = reverse("accounts:prayer_requests")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Peço oração pelo emprego.")
        self.assertContains(response, "João Pedro")
        self.assertContains(response, "confidencial")

        response = self.client.post(
            reverse("accounts:prayer_request_status", args=[self.item.pk]),
            {"status": PrayerRequest.Status.IN_PROGRESS},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, PrayerRequest.Status.IN_PROGRESS)
        self.assertContains(response, "Em acompanhamento")

        entry = AuditLog.objects.get(action="prayer_request_status_changed")
        self.assertEqual(entry.metadata.get("request_id"), self.item.pk)
        self.assertEqual(entry.metadata.get("new_status"), PrayerRequest.Status.IN_PROGRESS)
        self.assertNotIn("Peço oração pelo emprego.", str(entry.metadata))
        self.assertNotIn("prayer_text", entry.metadata)

    def test_communication_can_follow_up_and_member_cannot(self):
        make_user("comms", Role.COMMUNICATION)
        self.client.login(username="comms", password="senha-segura-123")
        response = self.client.get(reverse("accounts:prayer_requests"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Peço oração pelo emprego.")

        self.client.logout()
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("accounts:prayer_requests"))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_follow_up_redirects_to_login(self):
        response = self.client.get(reverse("accounts:prayer_requests"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/conta/entrar/", response.url)
