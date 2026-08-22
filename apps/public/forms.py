from django import forms

from apps.public.retreats import event_reference_date, is_minor
from apps.public.spam import HONEYPOT_FIELD


class HoneypotForm(forms.Form):
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
    name = forms.CharField(label="Nome", max_length=120, required=False)
    email = forms.EmailField(label="E-mail", required=False)
    phone = forms.CharField(label="Telefone", max_length=30, required=False)
    body = forms.CharField(
        label="Pedido de oração",
        widget=forms.Textarea(attrs={"rows": 5}),
        min_length=8,
        max_length=4000,
    )
    lgpd_consent = forms.BooleanField(
        required=False,
        label="Autorizo o uso dos meus dados para contato pastoral (LGPD).",
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
    name = forms.CharField(label="Nome", max_length=120)
    email = forms.EmailField(label="E-mail", required=False)
    phone = forms.CharField(label="Telefone", max_length=30, required=False)
    message = forms.CharField(
        label="Mensagem (opcional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        max_length=2000,
    )
    lgpd_consent = forms.BooleanField(
        label="Autorizo o uso dos meus dados para contato da igreja (LGPD).",
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


class EventRegistrationForm(forms.Form):
    name = forms.CharField(label="Nome", max_length=120)
    email = forms.EmailField(label="E-mail")
    phone = forms.CharField(label="Telefone", max_length=30, required=False)


class EventFamilyMemberForm(forms.Form):
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


class RetreatRegistrationForm(forms.Form):
    name = forms.CharField(label="Nome", max_length=120)
    email = forms.EmailField(label="E-mail")
    phone = forms.CharField(label="Telefone", max_length=30, required=False)
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
        label="Autorizo o uso dos dados da inscrição (incluindo menores) só para este retiro (LGPD).",
    )

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

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
