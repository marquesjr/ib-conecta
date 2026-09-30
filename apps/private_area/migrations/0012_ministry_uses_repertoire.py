from django.db import migrations, models


def mark_worship_ministries(apps, schema_editor):
    Ministry = apps.get_model("private_area", "Ministry")
    Ministry.objects.filter(
        models.Q(name__iexact="louvor") | models.Q(playlists__isnull=False)
    ).update(uses_repertoire=True)


class Migration(migrations.Migration):

    dependencies = [
        ("private_area", "0011_worship_playlist"),
    ]

    operations = [
        migrations.AddField(
            model_name="ministry",
            name="uses_repertoire",
            field=models.BooleanField(
                default=False,
                help_text="Marque para ministérios que montam playlist semanal de louvores.",
                verbose_name="Usa repertório",
            ),
        ),
        migrations.RunPython(mark_worship_ministries, migrations.RunPython.noop),
    ]
