"""Marca como arte os cartazes entre as fotos do Instagram cadastradas em 0012.

Cartaz recortado na abertura ou no mosaico perde o texto; como arte, ele vai
inteiro para o Mural. Só toca quadros ainda marcados como fotografia, para não
desfazer uma revisão feita no CMS.
"""

from django.db import migrations

ART_SHORTCODES = (
    "DWMWocQkddj",  # Mutirão de limpeza
    "DWOqTXrgGYP",  # Encontro de casais
    "DWqwTNTEVQD",  # Sexta-feira Santa
    "DXPItN0gEiA",  # 139 anos de Santa Leopoldina
    "Dc7A0_YxMoH",  # 27 anos da igreja
)


def links():
    return [f"https://www.instagram.com/p/{code}/" for code in ART_SHORTCODES]


def mark_art(apps, schema_editor):
    ArchiveFrame = apps.get_model("public", "ArchiveFrame")
    ArchiveFrame.objects.filter(permalink__in=links(), kind="photo").update(kind="art")


def unmark_art(apps, schema_editor):
    ArchiveFrame = apps.get_model("public", "ArchiveFrame")
    ArchiveFrame.objects.filter(permalink__in=links(), kind="art").update(kind="photo")


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0013_archiveframe_kind_featured"),
    ]

    operations = [
        migrations.RunPython(mark_art, unmark_art),
    ]
