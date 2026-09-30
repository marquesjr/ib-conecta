from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    """Aceita o nome de usuário ou o e-mail cadastrado no campo de login."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user is not None or not username or "@" not in username:
            return user

        user_model = get_user_model()
        matches = list(user_model._default_manager.filter(email__iexact=username.strip())[:2])
        if len(matches) != 1:
            # E-mail desconhecido ou repetido em mais de uma conta: não adivinha qual.
            user_model().set_password(password)
            return None
        candidate = matches[0]
        if candidate.check_password(password) and self.user_can_authenticate(candidate):
            return candidate
        return None
