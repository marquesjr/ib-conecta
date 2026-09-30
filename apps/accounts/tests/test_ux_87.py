from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role

User = get_user_model()


class HeaderAccountMenuTests(TestCase):
    """UX #87: com sessão aberta, o cabeçalho troca "Planeje sua visita" por um menu da conta."""

    def test_visitor_sees_plan_visit_and_login(self):
        response = self.client.get(reverse("privacy"))
        self.assertContains(response, 'class="cta nav-visit"')
        self.assertContains(response, reverse("accounts:login"))
        self.assertNotContains(response, "nav-account")

    def test_member_sees_account_menu_instead_of_plan_visit(self):
        user = User.objects.create_user(
            username="maria", password="senha-segura-123", first_name="Maria", last_name="Souza"
        )
        user.profile.role = Role.MEMBER
        user.profile.save()
        self.client.login(username="maria", password="senha-segura-123")

        response = self.client.get(reverse("privacy"))
        self.assertNotContains(response, 'class="cta nav-visit"')
        self.assertContains(response, 'class="nav-group nav-account"')
        self.assertContains(response, '<span class="nav-account-name">Maria</span>')
        self.assertContains(response, "Maria Souza")
        self.assertContains(response, f'href="{reverse("private_area:home")}"', count=1)
        self.assertContains(response, f'href="{reverse("accounts:account_home")}"', count=1)
        self.assertContains(response, f'action="{reverse("accounts:logout")}"')

    def test_account_menu_falls_back_to_username(self):
        User.objects.create_user(username="joao", password="senha-segura-123")
        self.client.login(username="joao", password="senha-segura-123")
        response = self.client.get(reverse("privacy"))
        self.assertContains(response, '<span class="nav-account-name">joao</span>')
