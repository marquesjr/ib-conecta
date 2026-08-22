from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model

from apps.private_area.models import (
    MONTH_LABELS,
    EventBudgetLine,
    EventChecklistItem,
    EventMaterial,
    EventOperation,
    EventOperationDocument,
    EventSupplier,
    EventTask,
    EventTeam,
    EventTeamMember,
    Ministry,
    MonthlySchedule,
    PrivateDocument,
    ScheduleAssignment,
    Song,
    SongReference,
    SongVersion,
)

User = get_user_model()


ALLOWED_EXTENSIONS = {
    ".csv",
    ".docx",
    ".key",
    ".odt",
    ".pdf",
    ".pptx",
    ".rtf",
    ".txt",
    ".xlsx",
    ".zip",
}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


class PrivateDocumentForm(forms.ModelForm):
    class Meta:
        model = PrivateDocument
        fields = ("title", "description", "audience", "file")

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        suffix = Path(uploaded.name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Tipo de arquivo não permitido.")
        if uploaded.size > MAX_UPLOAD_BYTES:
            raise forms.ValidationError("O arquivo deve ter no máximo 20 MB.")
        return uploaded


class MinistryForm(forms.ModelForm):
    class Meta:
        model = Ministry
        fields = ("name", "description")


class MonthlyScheduleForm(forms.ModelForm):
    month = forms.TypedChoiceField(
        label="Mês",
        coerce=int,
        choices=[(number, label.capitalize()) for number, label in MONTH_LABELS.items()],
    )

    class Meta:
        model = MonthlySchedule
        fields = ("year", "month", "notes")


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = ScheduleAssignment
        fields = ("starts_at", "function", "participant")
        widgets = {
            "starts_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["starts_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"]
        self.fields["participant"].queryset = User.objects.filter(is_active=True).order_by(
            "username"
        )
        self.fields["function"].help_text = "Ex.: dirigente, vocal, instrumento"


class SubstitutionForm(forms.Form):
    substitute = forms.ModelChoiceField(queryset=User.objects.none(), label="Substituto")

    def __init__(self, *args, assignment=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = User.objects.filter(is_active=True).order_by("username")
        if assignment is not None:
            queryset = queryset.exclude(pk=assignment.participant_id)
        self.fields["substitute"].queryset = queryset


class EventOperationForm(forms.ModelForm):
    title = forms.CharField(max_length=200, required=False, label="Título")
    starts_at = forms.DateTimeField(
        required=False,
        label="Início",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"],
    )
    ends_at = forms.DateTimeField(
        required=False,
        label="Término",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"],
    )
    location = forms.CharField(max_length=255, required=False, label="Local")
    body = forms.CharField(
        required=False,
        label="Descrição pública",
        widget=forms.Textarea,
    )
    requires_registration = forms.BooleanField(
        required=False,
        label="Exige inscrição",
    )
    is_retreat = forms.BooleanField(
        required=False,
        label="É retiro",
        help_text="Inscrição familiar, transporte, PIX e check-in na área privada.",
    )
    capacity = forms.IntegerField(
        required=False,
        min_value=1,
        label="Vagas",
        help_text="Pessoas (titular + familiares). Em branco, sem lista de espera.",
    )
    sensitive_retain_days = forms.IntegerField(
        required=False,
        min_value=1,
        initial=30,
        label="Dias para descarte de dados sensíveis",
    )

    class Meta:
        model = EventOperation
        fields = ("public_event", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.public.models import EventPage

        queryset = EventPage.objects.filter(operation__isnull=True).order_by("starts_at")
        if self.instance.pk:
            queryset = EventPage.objects.filter(pk=self.instance.public_event_id) | queryset
        self.fields["public_event"].queryset = queryset
        self.fields["public_event"].required = False
        self.fields["public_event"].label_from_instance = lambda event: event.title
        self.fields["public_event"].help_text = (
            "Escolha um evento já publicado ou deixe em branco para criar um novo na agenda."
        )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("public_event"):
            return cleaned
        if not cleaned.get("title") or not cleaned.get("starts_at"):
            raise forms.ValidationError(
                "Selecione um evento da agenda ou informe título e início para criar um novo."
            )
        return cleaned


class EventPlanningForm(forms.ModelForm):
    class Meta:
        model = EventOperation
        fields = ("notes",)


class EventTeamForm(forms.ModelForm):
    class Meta:
        model = EventTeam
        fields = ("name",)


class EventTeamMemberForm(forms.ModelForm):
    class Meta:
        model = EventTeamMember
        fields = ("user",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.filter(is_active=True).order_by(
            "username"
        )


class EventTaskForm(forms.ModelForm):
    class Meta:
        model = EventTask
        fields = ("title", "assignee")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignee"].queryset = User.objects.filter(is_active=True).order_by(
            "username"
        )


class EventChecklistForm(forms.ModelForm):
    class Meta:
        model = EventChecklistItem
        fields = ("label", "assignee")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignee"].queryset = User.objects.filter(is_active=True).order_by(
            "username"
        )


class EventSupplierForm(forms.ModelForm):
    class Meta:
        model = EventSupplier
        fields = ("name", "contact", "notes")


class EventMaterialForm(forms.ModelForm):
    class Meta:
        model = EventMaterial
        fields = ("name", "quantity", "notes")


class EventBudgetLineForm(forms.ModelForm):
    class Meta:
        model = EventBudgetLine
        fields = ("description", "amount")


class EventRegistrantMessageForm(forms.Form):
    subject = forms.CharField(max_length=200, label="Assunto")
    body = forms.CharField(widget=forms.Textarea, label="Mensagem")


class EventFinalReportForm(forms.ModelForm):
    class Meta:
        model = EventOperation
        fields = ("final_report",)


class EventOperationDocumentForm(forms.ModelForm):
    class Meta:
        model = EventOperationDocument
        fields = ("title", "file")

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        suffix = Path(uploaded.name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Tipo de arquivo não permitido.")
        if uploaded.size > MAX_UPLOAD_BYTES:
            raise forms.ValidationError("O arquivo deve ter no máximo 20 MB.")
        return uploaded


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = (
            "title",
            "key",
            "tempo",
            "lyrics",
            "chords",
            "tags",
            "score",
            "authors",
            "source",
            "license",
            "permitted_uses",
            "authorized",
        )

    def clean_score(self):
        uploaded = self.cleaned_data.get("score")
        if not uploaded:
            return uploaded
        suffix = Path(uploaded.name).suffix.lower()
        if suffix != ".pdf":
            raise forms.ValidationError("A partitura deve ser um PDF.")
        if uploaded.size > MAX_UPLOAD_BYTES:
            raise forms.ValidationError("O arquivo deve ter no máximo 20 MB.")
        return uploaded

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("authorized"):
            raise forms.ValidationError(
                "Não é permitido armazenar louvor sem autorização de uso."
            )
        return cleaned


class SongReferenceForm(forms.ModelForm):
    class Meta:
        model = SongReference
        fields = ("label", "target_url")


class SongVersionForm(forms.ModelForm):
    class Meta:
        model = SongVersion
        fields = ("name", "key", "lyrics", "chords")


SongReferenceFormSet = forms.inlineformset_factory(
    Song,
    SongReference,
    form=SongReferenceForm,
    extra=1,
    can_delete=False,
)

SongVersionFormSet = forms.inlineformset_factory(
    Song,
    SongVersion,
    form=SongVersionForm,
    extra=1,
    can_delete=False,
)
