from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Role

User = get_user_model()


class AuthFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="membro1",
            email="membro1@example.com",
            password="senha-segura-123",
        )
        self.user.profile.role = Role.MEMBER
        self.user.profile.save()

    def test_login_and_logout(self):
        login_url = reverse("accounts:login")
        response = self.client.post(
            login_url,
            {"username": "membro1", "password": "senha-segura-123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

        follow = self.client.get(reverse("accounts:account_home"))
        self.assertEqual(follow.status_code, 200)
        self.assertContains(follow, "membro1")

        logout_response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(logout_response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
        home = self.client.get(reverse("accounts:account_home"))
        self.assertEqual(home.status_code, 302)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_sends_email_and_allows_new_password(self):
        response = self.client.post(
            reverse("accounts:password_reset"),
            {"email": "membro1@example.com"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        reset_url = None
        for line in mail.outbox[0].body.splitlines():
            if "/conta/redefinir/" in line:
                reset_url = line.strip()
                break
        self.assertIsNotNone(reset_url)

        path = "/" + reset_url.split("/", 3)[-1]
        if not path.startswith("/conta/"):
            path = "/conta/redefinir/" + reset_url.split("/conta/redefinir/")[1]

        # Django stores the token in session and redirects to set-password.
        landed = self.client.get(path)
        self.assertEqual(landed.status_code, 302)
        set_password_url = landed.url

        confirm = self.client.post(
            set_password_url,
            {
                "new_password1": "nova-senha-segura-456",
                "new_password2": "nova-senha-segura-456",
            },
        )
        self.assertEqual(confirm.status_code, 302)
        self.assertTrue(
            self.client.login(username="membro1", password="nova-senha-segura-456")
        )
