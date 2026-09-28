from django.db import migrations

ADDRESS = "Av. Pres. Vargas, 38 - Centro, Santa Leopoldina - ES, 29640-000"
MAP_URL = "https://maps.app.goo.gl/wZdYwYxUpUJpA1DG9"


def use_church_address(apps, schema_editor):
    """Endereço e mapa informados pelo usuário em 28/09/2026; seguem editáveis no CMS."""
    ChurchSettings = apps.get_model("public", "ChurchSettings")
    ChurchSettings.objects.update(address_line=ADDRESS, map_url=MAP_URL)


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0015_home_welcome_text"),
    ]

    operations = [
        migrations.RunPython(use_church_address, migrations.RunPython.noop),
    ]
