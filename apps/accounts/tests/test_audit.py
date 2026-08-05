from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.audit import log_audit
from apps.accounts.models import AuditLog, Role

User = get_user_model()


class AuditLogTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="auditor",
            password="senha-segura-123",
        )
        self.admin.profile.role = Role.ADMIN
        self.admin.profile.save()

    def test_sensitive_login_is_audited_without_password(self):
        self.client.post(
            reverse("accounts:login"),
            {"username": "auditor", "password": "senha-segura-123"},
        )
        entry = AuditLog.objects.filter(action="login_success").latest("created_at")  # AuditAction.LOGIN_SUCCESS

        self.assertEqual(entry.actor_id, self.admin.id)
        self.assertNotIn("password", entry.metadata)
        self.assertNotIn("senha-segura-123", str(entry.metadata))

    def test_audit_helper_redacts_sensitive_and_pastoral_fields(self):
        log_audit(
            actor=self.admin,
            action="prayer_request_viewed",
            metadata={
                "password": "segredo",
                "token": "abc",
                "prayer_text": "pedido pastoral confidencial",
                "request_id": 42,
            },
        )
        entry = AuditLog.objects.get(action="prayer_request_viewed")
        self.assertEqual(entry.metadata.get("password"), "[redacted]")
        self.assertEqual(entry.metadata.get("token"), "[redacted]")
        self.assertEqual(entry.metadata.get("prayer_text"), "[redacted]")
        self.assertEqual(entry.metadata.get("request_id"), 42)

    def test_role_change_is_audited(self):
        target = User.objects.create_user(username="alvo", password="senha-segura-123")
        self.client.login(username="auditor", password="senha-segura-123")
        response = self.client.post(
            reverse("accounts:manage_users_demo"),
            {"user_id": target.id, "role": Role.COMMUNICATION},
        )
        self.assertEqual(response.status_code, 302)
        target.profile.refresh_from_db()
        self.assertEqual(target.profile.role, Role.COMMUNICATION)
        entry = AuditLog.objects.filter(action="role_changed").latest("created_at")
        self.assertEqual(entry.actor_id, self.admin.id)
        self.assertEqual(entry.metadata.get("target_user_id"), target.id)
        self.assertEqual(entry.metadata.get("new_role"), Role.COMMUNICATION)
