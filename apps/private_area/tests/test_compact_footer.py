from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Site

from apps.accounts.models import Role
from apps.public.models import ChurchSettings

User = get_user_model()


class CompactFooterTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        settings = ChurchSettings.for_site(site)
        settings.address_line = "Rua da Igreja, Centro, Santa Leopoldina - ES"
        settings.whatsapp_number = "5527999999999"
        settings.save()
        user = User.objects.create_user(username="membro", password="senha-segura-123")
        user.profile.role = Role.MEMBER
        user.profile.save()

    def assert_compact_footer(self, response, *, with_logout):
        self.assertContains(response, "site-footer--compact")
        self.assertContains(response, "Igreja Batista em Santa Leopoldina")
        self.assertContains(response, reverse("privacy"))
        self.assertNotContains(response, "footer-map")
        self.assertNotContains(response, "Vamos conversar?")
        self.assertNotContains(response, "Onde estamos")
        if with_logout:
            self.assertContains(response, f'action="{reverse("accounts:logout")}"')
            self.assertContains(response, 'class="footer-logout"')
        else:
            self.assertNotContains(response, 'class="footer-logout"')

    def test_private_area_uses_compact_footer_with_logout(self):
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("private_area:home"))
        self.assert_compact_footer(response, with_logout=True)

    def test_account_page_uses_compact_footer_with_logout(self):
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("accounts:account_home"))
        self.assert_compact_footer(response, with_logout=True)

    def test_login_page_uses_compact_footer_without_logout(self):
        response = self.client.get(reverse("accounts:login"))
        self.assert_compact_footer(response, with_logout=False)

    def test_public_pages_keep_full_footer(self):
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "site-footer--compact")
        self.assertContains(response, "Vamos conversar?")
        self.assertContains(response, "footer-map")

    def test_footer_logout_signs_user_out(self):
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)
