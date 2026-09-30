"""Ponto de foco no acervo e quadros do Instagram de set/2026 na proporção original.

As imagens cadastradas em 0012 tinham vindo da grade do perfil, já recortadas em
quadrado: o Mural mostrava “Parabén… Leopoldina 139 a” e a Sexta-feira Santa sem
as bordas. Os arquivos em ``apps/public/data/instagram_2026_09`` agora são o
quadro inteiro de cada post, e esta migração troca a imagem dos quadros que ainda
usam o arquivo semeado por 0012. Quadro cuja imagem foi trocada no CMS fica como
está.

“Feliz Dia dos Pais” é fotografia com texto no alto; o ponto de foco no topo
mantém a frase visível quando o mosaico recorta o quadro.
"""

from pathlib import Path

from django.core.files.base import ContentFile
from django.db import migrations, models

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "instagram_2026_09"

# (arquivo, shortcode) — os mesmos quadros de 0012.
FRAMES = (
    ("20250810_DNMF0BZSELs_01.jpg", "DNMF0BZSELs"),
    ("20250830_DN-mZu2gEom_01.jpg", "DN-mZu2gEom"),
    ("20250915_DOopIIDEcLO_01.jpg", "DOopIIDEcLO"),
    ("20260322_DWMWocQkddj_01.jpg", "DWMWocQkddj"),
    ("20260323_DWOqTXrgGYP_01.jpg", "DWOqTXrgGYP"),
    ("20260403_DWqwTNTEVQD_01.jpg", "DWqwTNTEVQD"),
    ("20260417_DXPItN0gEiA_01.jpg", "DXPItN0gEiA"),
    ("20260809_Db1rSblxKLn_01.jpg", "Db1rSblxKLn"),
    ("20260905_Dc7A0_YxMoH_01.jpg", "Dc7A0_YxMoH"),
)

TOP_FOCUS = ("DNMF0BZSELs",)  # Feliz Dia dos Pais


def permalink(shortcode):
    return f"https://www.instagram.com/p/{shortcode}/"


def _stored_bytes(image):
    try:
        with image.open("rb") as handle:
            return handle.read()
    except (FileNotFoundError, OSError):
        return None


def use_full_frames(apps, schema_editor):
    ArchiveFrame = apps.get_model("public", "ArchiveFrame")
    for filename, shortcode in FRAMES:
        # Só a imagem semeada por 0012 (``archive/ig-<shortcode>…``) é trocada.
        prefix = f"archive/ig-{shortcode}"
        for frame in ArchiveFrame.objects.filter(source="curated", permalink=permalink(shortcode)):
            if not frame.image.name.startswith(prefix):
                continue
            data = (DATA_DIR / filename).read_bytes()
            if _stored_bytes(frame.image) == data:
                continue
            old_name = frame.image.name
            # Nome novo para o navegador não reaproveitar a versão recortada do cache.
            frame.image.save(f"ig-{shortcode}-full.jpg", ContentFile(data), save=False)
            frame.save(update_fields=["image"])
            frame.image.storage.delete(old_name)

    ArchiveFrame.objects.filter(
        permalink__in=[permalink(code) for code in TOP_FOCUS], focal_point="center"
    ).update(focal_point="top")


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0016_church_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="archiveframe",
            name="focal_point",
            field=models.CharField(
                choices=[
                    ("center", "Centro"),
                    ("top", "Topo"),
                    ("bottom", "Base"),
                    ("left", "Esquerda"),
                    ("right", "Direita"),
                    ("top-left", "Topo à esquerda"),
                    ("top-right", "Topo à direita"),
                    ("bottom-left", "Base à esquerda"),
                    ("bottom-right", "Base à direita"),
                ],
                default="center",
                help_text="Parte da fotografia que não pode sumir quando o quadro é recortado no mosaico. Artes vão inteiras para o Mural e não são recortadas.",
                max_length=12,
                verbose_name="Ponto de foco",
            ),
        ),
        migrations.RunPython(use_full_frames, migrations.RunPython.noop),
    ]
