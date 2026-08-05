from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role
from apps.accounts.permissions import Permission, user_has_permission

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


class PermissionMatrixTests(TestCase):
    def test_member_cannot_manage_users_or_finances(self):
        user = make_user("membro", Role.MEMBER)
        self.assertTrue(user_has_permission(user, Permission.ACCESS_PRIVATE_AREA))
        self.assertFalse(user_has_permission(user, Permission.MANAGE_USERS))
        self.assertFalse(user_has_permission(user, Permission.MANAGE_FINANCES))

    def test_communication_can_manage_content_but_not_finances(self):
        user = make_user("comms", Role.COMMUNICATION)
        self.assertTrue(user_has_permission(user, Permission.MANAGE_CONTENT))
        self.assertFalse(user_has_permission(user, Permission.MANAGE_FINANCES))

    def test_pastor_can_manage_prayer_requests(self):
        user = make_user("pastor", Role.PASTOR)
        self.assertTrue(user_has_permission(user, Permission.MANAGE_PRAYER_REQUESTS))
        self.assertFalse(user_has_permission(user, Permission.MANAGE_USERS))

    def test_treasury_can_manage_finances(self):
        user = make_user("tesouraria", Role.TREASURY)
        self.assertTrue(user_has_permission(user, Permission.MANAGE_FINANCES))
        self.assertFalse(user_has_permission(user, Permission.MANAGE_CONTENT))

    def test_events_commission_can_manage_event_operations(self):
        user = make_user("comissao", Role.EVENTS_COMMISSION)
        self.assertTrue(user_has_permission(user, Permission.MANAGE_EVENT_OPERATIONS))
        self.assertFalse(user_has_permission(user, Permission.MANAGE_USERS))

    def test_ministry_leader_can_manage_ministry_schedules(self):
        user = make_user("lider", Role.MINISTRY_LEADER)
        self.assertTrue(user_has_permission(user, Permission.MANAGE_MINISTRY_SCHEDULES))
        self.assertFalse(user_has_permission(user, Permission.MANAGE_FINANCES))

    def test_admin_has_all_permissions(self):
        user = make_user("admin", Role.ADMIN)
        for permission in Permission:
            self.assertTrue(user_has_permission(user, permission), permission)

    def test_permission_denied_view_for_unauthorized_role(self):
        user = make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("accounts:manage_users_demo"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_manage_users_demo(self):
        make_user("admin", Role.ADMIN)
        self.client.login(username="admin", password="senha-segura-123")
        response = self.client.get(reverse("accounts:manage_users_demo"))
        self.assertEqual(response.status_code, 200)
