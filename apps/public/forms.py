from django import forms

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
