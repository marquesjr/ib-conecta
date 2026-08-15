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


class MemberListPrivacyTests(TestCase):
    def setUp(self):
        make_user("ana.silva", Role.MEMBER)
        make_user("bruno.souza", Role.MEMBER)
        make_user("carla.nunes", Role.COMMUNICATION)

    def test_member_does_not_see_other_members_on_private_pages(self):
        self.client.login(username="ana.silva", password="senha-segura-123")
        for url_name in ("private_area:home", "private_area:document_library"):
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200, url_name)
            self.assertNotContains(response, "bruno.souza")
            self.assertNotContains(response, "carla.nunes")

    def test_member_cannot_open_the_full_member_list(self):
        self.client.login(username="ana.silva", password="senha-segura-123")
        response = self.client.get(reverse("accounts:manage_users_demo"))
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "bruno.souza", status_code=403)
        self.assertNotContains(response, "carla.nunes", status_code=403)
