"""Cadastra no acervo as fotos mais curtidas do Instagram da igreja (set/2026).

As imagens foram baixadas do perfil público @igrejabatista.santaleopoldina e
acompanham o repositório em ``apps/public/data/instagram_2026_09``. Entram como
quadros curados — não como ``instagram`` — porque não vieram da API oficial e não
têm o ID numérico da Meta; assim uma sincronização futura não colide com elas.

A migração é idempotente pelo link do post: rodar de novo não duplica quadros.
"""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from django.core.files.base import ContentFile
from django.db import migrations

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "instagram_2026_09"
TZ = ZoneInfo("America/Sao_Paulo")

# (arquivo, shortcode, data do post, legenda, texto alternativo)
FRAMES = (
    (
        "20250810_DNMF0BZSELs_01.jpg",
        "DNMF0BZSELs",
        (2025, 8, 10),
        "Feliz Dia dos Pais",
        "Interior do templo durante o culto, com o banner “Jesus é o caminho” na parede "
        "e a frase “Feliz Dia dos Pais” escrita sobre a imagem",
    ),
    (
        "20250830_DN-mZu2gEom_01.jpg",
        "DN-mZu2gEom",
        (2025, 8, 30),
        "Subindo a Pedra Malha",
        "Jovens sentados em um banco rústico no alto da Pedra Malha, um menino em primeiro "
        "plano e montanhas cobertas de mata ao fundo",
    ),
    (
        "20250915_DOopIIDEcLO_01.jpg",
        "DOopIIDEcLO",
        (2025, 9, 15),
        "Encerramento da Campanha de Missões",
        "Membros de pé à frente do púlpito no culto de domingo: um menino de camiseta verde, "
        "uma senhora de casaco vinho e dois homens ao lado",
    ),
    (
        "20260322_DWMWocQkddj_01.jpg",
        "DWMWocQkddj",
        (2026, 3, 22),
        "Mutirão de limpeza do Rio Santa Maria da Vitória",
        "Cartaz do mutirão de limpeza das margens do Rio Santa Maria da Vitória sobre uma "
        "foto do casario do centro de Santa Leopoldina",
    ),
    (
        "20260323_DWOqTXrgGYP_01.jpg",
        "DWOqTXrgGYP",
        (2026, 3, 23),
        "Encontro de casais: “As quatro estações do amor”",
        "Arte do Encontro de Casais: um coração formado por árvores nas cores das quatro "
        "estações, com o tema “As quatro estações do amor”",
    ),
    (
        "20260403_DWqwTNTEVQD_01.jpg",
        "DWqwTNTEVQD",
        (2026, 4, 3),
        "Sexta-feira Santa",
        "Arte da Sexta-feira Santa com a frase “A cruz não foi o fim. Foi o plano eterno "
        "de Deus” sobre um céu claro",
    ),
    (
        "20260417_DXPItN0gEiA_01.jpg",
        "DXPItN0gEiA",
        (2026, 4, 17),
        "Parabéns, Santa Leopoldina, pelos 139 anos",
        "Vista aérea de Santa Leopoldina com uma igreja branca na encosta e montanhas de "
        "mata, com a mensagem de parabéns pelos 139 anos da cidade",
    ),
    (
        "20260809_Db1rSblxKLn_01.jpg",
        "Db1rSblxKLn",
        (2026, 8, 9),
        "Consagração da pequena Anne",
        "Homem de camisa branca segura no colo uma bebê de vestido branco diante da "
        "congregação, com o telão e os instrumentos ao fundo",
    ),
    (
        "20260905_Dc7A0_YxMoH_01.jpg",
        "Dc7A0_YxMoH",
        (2026, 9, 5),
        "27 anos de Igreja Batista em Santa Leopoldina",
        "Arte comemorativa com a fachada amarela do templo da Igreja Batista em Santa "
        "Leopoldina e a palavra “Aniversário”",
    ),
)


def permalink(shortcode):
    return f"https://www.instagram.com/p/{shortcode}/"


def add_frames(apps, schema_editor):
    ArchiveFrame = apps.get_model("public", "ArchiveFrame")
    for filename, shortcode, (year, month, day), caption, alt_text in FRAMES:
        link = permalink(shortcode)
        if ArchiveFrame.objects.filter(permalink=link).exists():
            continue
        frame = ArchiveFrame(
            source="curated",
            caption=caption,
            alt_text=alt_text,
            permalink=link,
            taken_at=datetime(year, month, day, 12, 0, tzinfo=TZ),
            is_visible=True,
        )
        data = (DATA_DIR / filename).read_bytes()
        frame.image.save(f"ig-{shortcode}.jpg", ContentFile(data), save=False)
        frame.save()


def remove_frames(apps, schema_editor):
    ArchiveFrame = apps.get_model("public", "ArchiveFrame")
    links = [permalink(shortcode) for _, shortcode, *_ in FRAMES]
    for frame in ArchiveFrame.objects.filter(source="curated", permalink__in=links):
        frame.image.delete(save=False)
        frame.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0010_instagramcredential_and_more"),
    ]

    operations = [
        migrations.RunPython(add_frames, remove_frames),
    ]
