import pyotp
from django.conf import settings
from django.db import models


class Role(models.TextChoices):
    MEMBER = "member", "Membro"
    MINISTRY_LEADER = "ministry_leader", "Líder de ministério"
    COMMUNICATION = "communication", "Comunicação"
    PASTOR = "pastor", "Pastor"
    TREASURY = "treasury", "Tesouraria"
    EVENTS_COMMISSION = "events_commission", "Comissão de eventos"
    ADMIN = "admin", "Administrador"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    totp_secret = models.CharField(max_length=64, blank=True, default="")
    totp_enabled = models.BooleanField(default=False)

    def ensure_totp_secret(self) -> str:
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
            self.save(update_fields=["totp_secret"])
        return self.totp_secret

    def verify_totp(self, token: str) -> bool:
        if not self.totp_secret:
            return False
        return pyotp.TOTP(self.totp_secret).verify(token, valid_window=1)

    def enable_totp(self) -> None:
        self.totp_enabled = True
        self.save(update_fields=["totp_enabled"])

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_role_display()})"



class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        actor = self.actor_id or "system"
        return f"{self.created_at:%Y-%m-%d %H:%M} {actor} {self.action}"
