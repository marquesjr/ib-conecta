from django import forms

from apps.forms import FormLabelsMixin
from apps.public.privacy import consent_label
from apps.public.retreats import event_reference_date, is_minor
from apps.public.spam import HONEYPOT_FIELD


class HoneypotForm(FormLabelsMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[HONEYPOT_FIELD] = forms.CharField(
            required=False,
            label="Site",
            widget=forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "tabindex": "-1",
                    "aria-hidden": "true",
                }
            ),
        )


class PrayerRequestForm(HoneypotForm):
    is_anonymous = forms.BooleanField(
        required=False,
        label="Enviar de forma anônima",
    )
    name = forms.CharField(
        label="Nome",
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="E-mail",
        required=False,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    phone = forms.CharField(
        label="Telefone",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
    )
    body = forms.CharField(
        label="Pedido de oração",
        widget=forms.Textarea(attrs={"rows": 5}),
        min_length=8,
        max_length=4000,
    )
    lgpd_consent = forms.BooleanField(
        required=False,
        label=consent_label("Autorizo o uso dos meus dados para contato pastoral."),
    )

    def clean(self):
        data = super().clean()
        if data.get("is_anonymous"):
            data["name"] = ""
            data["email"] = ""
            data["phone"] = ""
            data["lgpd_consent"] = False
            return data
        if not (data.get("name") or "").strip():
            self.add_error("name", "Informe seu nome ou envie de forma anônima.")
        if not data.get("lgpd_consent"):
            self.add_error(
                "lgpd_consent",
                "É necessário consentir o uso dos dados para contato.",
            )
        return data

    def submission_payload(self) -> dict:
        data = self.cleaned_data
        return {
            "is_anonymous": bool(data.get("is_anonymous")),
            "name": data.get("name") or "",
            "email": data.get("email") or "",
            "phone": data.get("phone") or "",
            "body": data["body"],
            "lgpd_consent": bool(data.get("lgpd_consent")),
        }


class KnowChurchForm(HoneypotForm):
    name = forms.CharField(
        label="Nome",
        max_length=120,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="E-mail",
        required=False,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    phone = forms.CharField(
        label="Telefone",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
    )
    message = forms.CharField(
        label="Mensagem (opcional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        max_length=2000,
    )
    lgpd_consent = forms.BooleanField(
        label=consent_label("Autorizo o uso dos meus dados para contato da igreja."),
    )

    def clean(self):
        data = super().clean()
        if not data.get("email") and not (data.get("phone") or "").strip():
            raise forms.ValidationError("Informe e-mail ou telefone para contato.")
        return data

    def submission_payload(self) -> dict:
        data = self.cleaned_data
        return {
            "name": data["name"],
            "email": data.get("email") or "",
            "phone": data.get("phone") or "",
            "message": data.get("message") or "",
            "lgpd_consent": True,
        }


class EventRegistrationForm(FormLabelsMixin, forms.Form):
    name = forms.CharField(
        label="Nome",
        max_length=120,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    phone = forms.CharField(
        label="Telefone",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
    )


class EventFamilyMemberForm(FormLabelsMixin, forms.Form):
    name = forms.CharField(label="Nome do familiar", max_length=120, required=False)
    birth_date = forms.DateField(
        label="Data de nascimento",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    dietary_restrictions = forms.CharField(
        label="Restrições alimentares",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    medical_notes = forms.CharField(
        label="Informações médicas",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def clean(self):
        data = super().clean()
        name = (data.get("name") or "").strip()
        if name and not data.get("birth_date"):
            self.add_error("birth_date", "Informe a data de nascimento do familiar.")
        if data.get("birth_date") and not name:
            self.add_error("name", "Informe o nome do familiar.")
        data["name"] = name
        return data


FamilyMemberFormSet = forms.formset_factory(EventFamilyMemberForm, extra=2, max_num=10)


class RetreatRegistrationForm(FormLabelsMixin, forms.Form):
    # Obrigatórios quando há menor de 18 anos; "(opcional)" enganaria.
    OPTIONAL_MARK_EXEMPT = ("guardian_name", "guardian_phone", "guardian_relationship")

    name = forms.CharField(
        label="Nome",
        max_length=120,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    phone = forms.CharField(
        label="Telefone",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
    )
    birth_date = forms.DateField(
        label="Data de nascimento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    guardian_name = forms.CharField(
        label="Responsável legal",
        max_length=120,
        required=False,
    )
    guardian_phone = forms.CharField(
        label="Telefone do responsável",
        max_length=30,
        required=False,
    )
    guardian_relationship = forms.CharField(
        label="Parentesco do responsável",
        max_length=80,
        required=False,
    )
    emergency_name = forms.CharField(label="Contato de emergência", max_length=120)
    emergency_phone = forms.CharField(label="Telefone de emergência", max_length=30)
    dietary_restrictions = forms.CharField(
        label="Restrições alimentares",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    medical_notes = forms.CharField(
        label="Informações médicas",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    transport_needed = forms.BooleanField(label="Preciso de transporte", required=False)
    boarding_point = forms.CharField(
        label="Ponto de embarque",
        max_length=120,
        required=False,
    )
    accommodation = forms.CharField(
        label="Acomodação",
        max_length=120,
        required=False,
    )
    lgpd_consent = forms.BooleanField(
        label=consent_label(
            "Autorizo o uso dos dados da inscrição (incluindo menores) só para este retiro."
        ),
    )

    # Seções exibidas como blocos separados no formulário público; os campos
    # fora delas (o consentimento) aparecem no fim, depois dos familiares.
    SECTIONS = (
        ("Você", "", ("name", "email", "phone", "birth_date")),
        (
            "Responsável e emergência",
            "O responsável legal é obrigatório quando houver menores de 18 anos.",
            (
                "guardian_name",
                "guardian_phone",
                "guardian_relationship",
                "emergency_name",
                "emergency_phone",
            ),
        ),
        ("Saúde", "", ("dietary_restrictions", "medical_notes")),
        ("Transporte e hospedagem", "", ("transport_needed", "boarding_point", "accommodation")),
    )

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

    def sections(self):
        return [
            {"title": title, "hint": hint, "fields": [self[name] for name in names]}
            for title, hint, names in self.SECTIONS
        ]

    def closing_fields(self):
        in_sections = {name for _, _, names in self.SECTIONS for name in names}
        return [field for field in self.visible_fields() if field.name not in in_sections]

    def clean(self):
        data = super().clean()
        if not data.get("lgpd_consent"):
            self.add_error(
                "lgpd_consent",
                "É necessário consentir o uso dos dados para a inscrição no retiro.",
            )
        return data

    def require_guardian_if_minors(self, formset, event):
        on_date = event_reference_date(event)
        has_minor = is_minor(self.cleaned_data.get("birth_date"), on_date)
        for child in formset:
            if not child.cleaned_data.get("name"):
                continue
            if is_minor(child.cleaned_data.get("birth_date"), on_date):
                has_minor = True
        if has_minor and not (self.cleaned_data.get("guardian_name") or "").strip():
            self.add_error(
                "guardian_name",
                "Informe o responsável legal pelos menores de idade.",
            )
        if has_minor and not (self.cleaned_data.get("guardian_phone") or "").strip():
            self.add_error(
                "guardian_phone",
                "Informe o telefone do responsável legal.",
            )
