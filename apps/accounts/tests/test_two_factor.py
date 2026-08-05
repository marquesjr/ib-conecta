import pyotp
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role

User = get_user_model()


class TwoFactorTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin2fa",
            password="senha-segura-123",
        )
        self.admin.profile.role = Role.ADMIN
        self.admin.profile.save()

        self.member = User.objects.create_user(
            username="membro2fa",
            password="senha-segura-123",
        )
        self.member.profile.role = Role.MEMBER
        self.member.profile.save()

    def test_admin_can_enable_totp_and_must_use_it_on_login(self):
        self.client.login(username="admin2fa", password="senha-segura-123")
        setup = self.client.get(reverse("accounts:two_factor_setup"))
        self.assertEqual(setup.status_code, 200)

        self.admin.profile.refresh_from_db()
        secret = self.admin.profile.totp_secret
        self.assertTrue(secret)

        token = pyotp.TOTP(secret).now()
        enable = self.client.post(
            reverse("accounts:two_factor_setup"),
            {"token": token},
        )
        self.assertEqual(enable.status_code, 302)
        self.admin.profile.refresh_from_db()
        self.assertTrue(self.admin.profile.totp_enabled)

        self.client.logout()
        login = self.client.post(
            reverse("accounts:login"),
            {"username": "admin2fa", "password": "senha-segura-123"},
        )
        self.assertEqual(login.status_code, 302)
        self.assertEqual(login.url, reverse("accounts:two_factor_verify"))

        # Session is not fully authenticated for protected pages yet
        blocked = self.client.get(reverse("accounts:account_home"))
        self.assertEqual(blocked.status_code, 302)

        bad = self.client.post(
            reverse("accounts:two_factor_verify"),
            {"token": "000000"},
        )
        self.assertEqual(bad.status_code, 200)

        good_token = pyotp.TOTP(self.admin.profile.totp_secret).now()
        ok = self.client.post(
            reverse("accounts:two_factor_verify"),
            {"token": good_token},
        )
        self.assertEqual(ok.status_code, 302)
        home = self.client.get(reverse("accounts:account_home"))
        self.assertEqual(home.status_code, 200)

    def test_non_admin_cannot_access_two_factor_setup(self):
        self.client.login(username="membro2fa", password="senha-segura-123")
        response = self.client.get(reverse("accounts:two_factor_setup"))
        self.assertEqual(response.status_code, 403)
