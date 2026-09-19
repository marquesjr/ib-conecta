from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0010_instagramcredential_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="archiveframe",
            name="credit",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Ex.: Instagram @igrejabatista.santaleopoldina. Quadros da API e da exportação preenchem sozinhos.",
                max_length=120,
                verbose_name="Crédito",
            ),
        ),
    ]
