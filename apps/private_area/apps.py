from django.apps import AppConfig


class PrivateAreaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.private_area"
    label = "private_area"
    verbose_name = "Área privada"
