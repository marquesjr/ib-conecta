from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


class PrivateAreaAccessTests(TestCase):
    def test_visitor_is_redirected_from_private_area_to_login(self):
        response = self.client.get(reverse("private_area:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_authenticated_member_can_open_private_area(self):
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("private_area:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Área privada")
        self.assertContains(response, "Biblioteca de documentos")
        self.assertContains(response, "Ministérios")
        self.assertContains(response, "Coletânea de louvores")
