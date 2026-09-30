from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LoginWithEmailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="membro1",
            email="Membro1@Example.com",
            password="senha-segura-123",
        )
        self.login_url = reverse("accounts:login")

    def post(self, username, password="senha-segura-123"):
        return self.client.post(self.login_url, {"username": username, "password": password})

    def test_login_with_username_still_works(self):
        response = self.post("membro1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["_auth_user_id"], str(self.user.pk))

    def test_login_with_email_ignores_case_and_spaces(self):
        response = self.post("  membro1@example.COM ")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["_auth_user_id"], str(self.user.pk))

    def test_login_with_email_and_wrong_password_fails(self):
        response = self.post("membro1@example.com", password="errada")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(response, "E-mail, usuário ou senha incorretos")

    def test_email_shared_by_two_accounts_is_refused(self):
        User.objects.create_user(
            username="membro2", email="membro1@example.com", password="senha-segura-123"
        )
        response = self.post("membro1@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_inactive_user_cannot_login_by_email(self):
        self.user.is_active = False
        self.user.save()
        self.post("membro1@example.com")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_page_labels_toggle_and_spacing(self):
        response = self.client.get(self.login_url)
        self.assertContains(response, "E-mail ou usuário")
        self.assertContains(response, 'autocomplete="username"')
        self.assertContains(response, 'autocomplete="current-password"')
        self.assertContains(response, 'class="password-toggle"')
        self.assertContains(response, 'aria-controls="id_password"')
        self.assertContains(response, "js/login.js")
        self.assertContains(response, 'class="login-actions"')
        self.assertContains(response, "Esqueci minha senha")
