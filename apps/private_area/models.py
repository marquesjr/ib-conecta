import secrets

from django.conf import settings
from django.db import models
from django.utils.text import slugify

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


WORSHIP_FUNCTIONS = (
    "Dirigente",
    "Vocal",
    "Instrumento",
    "Sonoplastia",
    "Projeção",
)


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


class EventOperation(models.Model):
    public_event = models.OneToOneField(
        "public.EventPage",
        on_delete=models.CASCADE,
        related_name="operation",
        verbose_name="Evento da agenda",
    )
    notes = models.TextField(blank=True, default="", verbose_name="Planejamento")
    final_report = models.TextField(blank=True, default="", verbose_name="Relatório final")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_event_operations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["public_event__starts_at"]
        verbose_name = "Operação de evento"
        verbose_name_plural = "Operações de eventos"

    def __str__(self) -> str:
        return str(self.public_event)


class EventTeam(models.Model):
    operation = models.ForeignKey(
        EventOperation,
        on_delete=models.CASCADE,
        related_name="teams",
    )
    name = models.CharField(max_length=80, verbose_name="Equipe")

    class Meta:
        ordering = ["name"]
        verbose_name = "Equipe do evento"
        verbose_name_plural = "Equipes do evento"

    def __str__(self) -> str:
        return self.name


class EventTeamMember(models.Model):
    team = models.ForeignKey(
        EventTeam,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_team_memberships",
    )

    class Meta:
        ordering = ["user__username"]
        constraints = [
            models.UniqueConstraint(
                fields=["team", "user"],
                name="unique_event_team_member",
            )
        ]
        verbose_name = "Membro da equipe"
        verbose_name_plural = "Membros da equipe"

    def __str__(self) -> str:
        return f"{self.user} — {self.team}"


class EventTask(models.Model):
    operation = models.ForeignKey(
        EventOperation,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=200, verbose_name="Tarefa")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_tasks",
        verbose_name="Responsável",
    )
    done = models.BooleanField(default=False, verbose_name="Concluída")

    class Meta:
        ordering = ["done", "title"]
        verbose_name = "Tarefa do evento"
        verbose_name_plural = "Tarefas do evento"

    def __str__(self) -> str:
        return self.title


class EventChecklistItem(models.Model):
    operation = models.ForeignKey(
        EventOperation,
        on_delete=models.CASCADE,
        related_name="checklist_items",
    )
    label = models.CharField(max_length=200, verbose_name="Item")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_checklist_items",
        verbose_name="Responsável",
    )
    done = models.BooleanField(default=False, verbose_name="Concluído")

    class Meta:
        ordering = ["done", "label"]
        verbose_name = "Item de checklist"
        verbose_name_plural = "Itens de checklist"

    def __str__(self) -> str:
        return self.label


class EventSupplier(models.Model):
    operation = models.ForeignKey(
        EventOperation,
        on_delete=models.CASCADE,
        related_name="suppliers",
    )
    name = models.CharField(max_length=120, verbose_name="Fornecedor")
    contact = models.CharField(max_length=120, blank=True, default="", verbose_name="Contato")
    notes = models.TextField(blank=True, default="", verbose_name="Observações")

    class Meta:
        ordering = ["name"]
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self) -> str:
        return self.name


class EventMaterial(models.Model):
    operation = models.ForeignKey(
        EventOperation,
        on_delete=models.CASCADE,
        related_name="materials",
    )
    name = models.CharField(max_length=120, verbose_name="Material")
    quantity = models.CharField(max_length=40, blank=True, default="", verbose_name="Quantidade")
    notes = models.TextField(blank=True, default="", verbose_name="Observações")

    class Meta:
        ordering = ["name"]
        verbose_name = "Material"
        verbose_name_plural = "Materiais"

    def __str__(self) -> str:
        return self.name


class BudgetLineStatus(models.TextChoices):
    PENDING = "pending", "Pendente"
    APPROVED = "approved", "Aprovado"
    REJECTED = "rejected", "Recusado"


class EventBudgetLine(models.Model):
    operation = models.ForeignKey(
        EventOperation,
        on_delete=models.CASCADE,
        related_name="budget_lines",
    )
    description = models.CharField(max_length=200, verbose_name="Descrição")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    status = models.CharField(
        max_length=16,
        choices=BudgetLineStatus.choices,
        default=BudgetLineStatus.PENDING,
        verbose_name="Situação",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_event_budget_lines",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_event_budget_lines",
    )

    class Meta:
        ordering = ["status", "description"]
        verbose_name = "Linha de orçamento"
        verbose_name_plural = "Linhas de orçamento"

    def __str__(self) -> str:
        return f"{self.description} ({self.amount})"


class EventOperationDocument(models.Model):
    operation = models.ForeignKey(
        EventOperation,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    file = models.FileField(
        upload_to="event-operations/",
        storage=private_document_storage,
        verbose_name="Arquivo",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_event_operation_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Documento da operação"
        verbose_name_plural = "Documentos da operação"

    def __str__(self) -> str:
        return self.title


class SongStatus(models.TextChoices):
    DRAFT = "draft", "Rascunho"
    PUBLISHED = "published", "Publicado"


class Song(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=220, unique=True)
    status = models.CharField(
        max_length=16,
        choices=SongStatus.choices,
        default=SongStatus.DRAFT,
        verbose_name="Situação",
    )
    key = models.CharField(max_length=20, blank=True, default="", verbose_name="Tom")
    tempo = models.CharField(max_length=40, blank=True, default="", verbose_name="Andamento")
    lyrics = models.TextField(blank=True, default="", verbose_name="Letra")
    chords = models.TextField(blank=True, default="", verbose_name="Cifra")
    tags = models.CharField(max_length=200, blank=True, default="", verbose_name="Tags")
    authors = models.CharField(max_length=200, verbose_name="Autoria")
    source = models.CharField(max_length=200, verbose_name="Fonte")
    license = models.TextField(verbose_name="Licença / autorização")
    permitted_uses = models.TextField(verbose_name="Usos permitidos")
    authorized = models.BooleanField(
        default=False,
        verbose_name="Há autorização para armazenar este louvor",
    )
    score = models.FileField(
        upload_to="songbook/",
        storage=private_document_storage,
        blank=True,
        verbose_name="Partitura PDF",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_songs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Louvor"
        verbose_name_plural = "Louvores"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(authorized=True),
                name="song_requires_authorization",
            )
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_song_slug(self)
        super().save(*args, **kwargs)


def _unique_song_slug(song: Song) -> str:
    base = slugify(song.title) or "louvor"
    slug = base
    suffix = 2
    while Song.objects.exclude(pk=song.pk).filter(slug=slug).exists():
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug


class SongReference(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="references")
    label = models.CharField(max_length=80, verbose_name="Rótulo")
    token = models.CharField(max_length=32, unique=True, editable=False)
    target_url = models.URLField(verbose_name="URL externa")

    class Meta:
        ordering = ["id"]
        verbose_name = "Referência externa"
        verbose_name_plural = "Referências externas"

    def __str__(self) -> str:
        return f"{self.label} ({self.song.title})"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(8)
        super().save(*args, **kwargs)


class SongVersion(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="versions")
    name = models.CharField(max_length=80, verbose_name="Versão")
    key = models.CharField(max_length=20, blank=True, default="", verbose_name="Tom")
    lyrics = models.TextField(blank=True, default="", verbose_name="Letra")
    chords = models.TextField(blank=True, default="", verbose_name="Cifra")

    class Meta:
        ordering = ["id"]
        verbose_name = "Versão"
        verbose_name_plural = "Versões"

    def __str__(self) -> str:
        return f"{self.song.title} — {self.name}"


class PlaylistKind(models.TextChoices):
    SERVICE = "service", "Culto"
    REHEARSAL = "rehearsal", "Ensaio"


class WeeklyPlaylist(models.Model):
    ministry = models.ForeignKey(
        Ministry,
        on_delete=models.CASCADE,
        related_name="playlists",
    )
    kind = models.CharField(
        max_length=16,
        choices=PlaylistKind.choices,
        verbose_name="Tipo",
    )
    starts_at = models.DateTimeField(verbose_name="Data e horário")
    notes = models.TextField(blank=True, default="", verbose_name="Observações")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_playlists",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-starts_at"]
        verbose_name = "Playlist semanal"
        verbose_name_plural = "Playlists semanais"

    def __str__(self) -> str:
        return self.label()

    def label(self) -> str:
        return f"{self.get_kind_display()} — {self.starts_at:%d/%m/%Y}"


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(
        WeeklyPlaylist,
        on_delete=models.CASCADE,
        related_name="items",
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="playlist_items",
    )
    version = models.ForeignKey(
        SongVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="playlist_items",
        verbose_name="Versão",
    )
    position = models.PositiveIntegerField(verbose_name="Ordem")
    key = models.CharField(max_length=20, blank=True, default="", verbose_name="Tom")
    notes = models.TextField(blank=True, default="", verbose_name="Observações")

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Item da playlist"
        verbose_name_plural = "Itens da playlist"

    def __str__(self) -> str:
        return f"{self.position}. {self.song}"

    def print_lyrics(self) -> str:
        if self.version and self.version.lyrics:
            return self.version.lyrics
        return self.song.lyrics

    def print_chords(self) -> str:
        if self.version and self.version.chords:
            return self.version.chords
        return self.song.chords

    def display_key(self) -> str:
        if self.key:
            return self.key
        if self.version and self.version.key:
            return self.version.key
        return self.song.key
