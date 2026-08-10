from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role
from apps.public.cms import ensure_cms_editors_group, sync_cms_access_for_user

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    sync_cms_access_for_user(user)
    user.refresh_from_db()
    return user


class CmsPermissionTests(TestCase):
    def setUp(self):
        ensure_cms_editors_group()

    def test_communication_can_open_wagtail_admin(self):
        make_user("comms", Role.COMMUNICATION)
        self.client.login(username="comms", password="senha-segura-123")
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_member_cannot_open_wagtail_admin(self):
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get("/admin/")
        self.assertIn(response.status_code, (302, 403))
        if response.status_code == 302:
            self.assertIn("/admin/login", response.url)

    def test_communication_can_open_create_institutional_page_form(self):
        make_user("comms", Role.COMMUNICATION)
        self.client.login(username="comms", password="senha-segura-123")
        # Wagtail root page id is 1; create child InstitutionalPage under it.
        url = reverse("wagtailadmin_pages:add", args=("public", "institutionalpage", 1))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Página institucional")
