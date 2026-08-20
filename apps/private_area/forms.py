from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model

from apps.private_area.models import (
    MONTH_LABELS,
    Ministry,
    MonthlySchedule,
    PrivateDocument,
    ScheduleAssignment,
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
