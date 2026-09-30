from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.audit import AuditAction
from apps.accounts.models import AuditLog, Role

User = get_user_model()


class AccountProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="lider",
            email="lider@example.com",
            password="senha-segura-123",
        )
        self.user.profile.role = Role.MINISTRY_LEADER
        self.user.profile.save()
        self.client.force_login(self.user)
        self.url = reverse("accounts:account_home")

    def test_greets_by_first_name(self):
        self.user.first_name = "Ana"
        self.user.save()
        response = self.client.get(self.url)
        self.assertContains(response, "<h1>Olá, Ana</h1>", html=True)

    def test_greeting_falls_back_to_username(self):
        response = self.client.get(self.url)
        self.assertContains(response, "<h1>Olá, lider</h1>", html=True)

    def test_does_not_repeat_private_area_links(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "Biblioteca de documentos")
        self.assertNotContains(response, "Ministérios e escalas")

    def test_shows_security_actions(self):
        self.user.profile.role = Role.ADMIN
        self.user.profile.save()
        response = self.client.get(self.url)
        self.assertContains(response, reverse("accounts:password_change"))
        self.assertContains(response, reverse("accounts:two_factor_setup"))
        self.assertContains(response, reverse("accounts:logout"))

    def test_role_without_2fa_permission_does_not_see_2fa(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, reverse("accounts:two_factor_setup"))

    def test_updates_details(self):
        response = self.client.post(
            self.url,
            {"first_name": "Ana", "last_name": "Souza", "email": "ana@example.com"},
        )
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Ana")
        self.assertEqual(self.user.last_name, "Souza")
        self.assertEqual(self.user.email, "ana@example.com")
        self.assertTrue(
            AuditLog.objects.filter(action=AuditAction.ACCOUNT_DETAILS_UPDATED).exists()
        )

    def test_rejects_email_used_by_another_account(self):
        User.objects.create_user(username="outro", email="outro@example.com", password="x")
        response = self.client.post(
            self.url,
            {"first_name": "Ana", "last_name": "", "email": "OUTRO@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este e-mail já está em uso por outra conta.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "lider@example.com")

    def test_changes_password_and_keeps_session(self):
        response = self.client.post(
            reverse("accounts:password_change"),
            {
                "old_password": "senha-segura-123",
                "new_password1": "nova-senha-forte-456",
                "new_password2": "nova-senha-forte-456",
            },
        )
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("nova-senha-forte-456"))
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertTrue(AuditLog.objects.filter(action=AuditAction.PASSWORD_CHANGED).exists())

    def test_password_change_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("accounts:password_change"))
        self.assertEqual(response.status_code, 302)
