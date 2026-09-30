from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="E-mail ou usuário",
        widget=forms.TextInput(
            attrs={"autocomplete": "username", "autocapitalize": "none", "spellcheck": "false"}
        ),
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "E-mail, usuário ou senha incorretos. Confira e tente de novo.",
    }


class OTPTokenForm(forms.Form):
    token = forms.CharField(
        label="Código de autenticação",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"autocomplete": "one-time-code", "inputmode": "numeric"}),
    )
