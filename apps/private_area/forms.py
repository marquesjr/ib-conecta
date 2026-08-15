from pathlib import Path

from django import forms

from apps.private_area.models import PrivateDocument

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
