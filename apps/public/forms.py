from django import forms


class EventRegistrationForm(forms.Form):
    name = forms.CharField(label="Nome", max_length=120)
    email = forms.EmailField(label="E-mail")
    phone = forms.CharField(label="Telefone", max_length=30, required=False)
