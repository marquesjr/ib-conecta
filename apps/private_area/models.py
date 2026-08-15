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
