from django.conf import settings
from django.db import models

from apps.accounts.permissions import Permission, user_has_permission
from apps.private_area.storage import private_document_storage


class DocumentAudience(models.TextChoices):
    MEMBERS = "members", "Todos os membros"
    CONTENT = "content", "Comunicação e pastor"
    FINANCES = "finances", "Tesouraria"
    ADMIN = "admin", "Administração"


AUDIENCE_PERMISSION = {
    DocumentAudience.MEMBERS: Permission.ACCESS_PRIVATE_AREA,
    DocumentAudience.CONTENT: Permission.MANAGE_CONTENT,
    DocumentAudience.FINANCES: Permission.MANAGE_FINANCES,
    DocumentAudience.ADMIN: Permission.MANAGE_USERS,
}


class PrivateDocumentQuerySet(models.QuerySet):
    def visible_to(self, user):
        audiences = [
            audience
            for audience, permission in AUDIENCE_PERMISSION.items()
            if user_has_permission(user, permission)
        ]
        return self.filter(audience__in=audiences)


class PrivateDocument(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, default="", verbose_name="Descrição")
    audience = models.CharField(
        max_length=32,
        choices=DocumentAudience.choices,
        default=DocumentAudience.MEMBERS,
        verbose_name="Quem pode ver",
    )
    file = models.FileField(
        upload_to="documents/",
        storage=private_document_storage,
        verbose_name="Arquivo",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_private_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PrivateDocumentQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Documento privado"
        verbose_name_plural = "Documentos privados"

    def __str__(self) -> str:
        return self.title

    def is_visible_to(self, user) -> bool:
        permission = AUDIENCE_PERMISSION.get(self.audience)
        return bool(permission and user_has_permission(user, permission))


class Ministry(models.Model):
    name = models.CharField(max_length=120, verbose_name="Nome")
    description = models.TextField(blank=True, default="", verbose_name="Descrição")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_ministries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Ministério"
        verbose_name_plural = "Ministérios"

    def __str__(self) -> str:
        return self.name


MONTH_LABELS = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}


class AssignmentStatus(models.TextChoices):
    PENDING = "pending", "Pendente"
    CONFIRMED = "confirmed", "Confirmado"
    DECLINED = "declined", "Recusado"


class MonthlySchedule(models.Model):
    ministry = models.ForeignKey(
        Ministry,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    year = models.PositiveIntegerField(verbose_name="Ano")
    month = models.PositiveSmallIntegerField(verbose_name="Mês")
    notes = models.TextField(blank=True, default="", verbose_name="Observações")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_schedules",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["ministry", "year", "month"],
                name="unique_ministry_month_schedule",
            )
        ]
        verbose_name = "Escala mensal"
        verbose_name_plural = "Escalas mensais"

    def __str__(self) -> str:
        return self.label()

    def label(self) -> str:
        month = MONTH_LABELS.get(self.month, str(self.month))
        return f"{month} de {self.year}"


class ScheduleAssignment(models.Model):
    schedule = models.ForeignKey(
        MonthlySchedule,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    starts_at = models.DateTimeField(verbose_name="Data e horário")
    function = models.CharField(max_length=80, verbose_name="Função")
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="schedule_assignments",
    )
    status = models.CharField(
        max_length=16,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.PENDING,
        verbose_name="Situação",
    )

    class Meta:
        ordering = ["starts_at", "function"]
        verbose_name = "Convocação"
        verbose_name_plural = "Convocações"

    def __str__(self) -> str:
        return f"{self.function} — {self.participant}"


class Substitution(models.Model):
    assignment = models.ForeignKey(
        ScheduleAssignment,
        on_delete=models.CASCADE,
        related_name="substitutions",
    )
    replaced = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="replaced_on_assignments",
    )
    substitute = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="substituting_on_assignments",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_substitutions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Substituição"
        verbose_name_plural = "Substituições"

    def __str__(self) -> str:
        return f"{self.replaced} → {self.substitute}"
