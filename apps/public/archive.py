"""Fotografias da home: acervo real com reserva ilustrativa quando necessário.

Ordem de preferência, e ela é deliberada:

1. Quadros do Instagram sincronizados pela API oficial.
2. Quadros curados no CMS pela comunicação.
3. Quadros semeados sintéticos que acompanham o repositório.

Os quadros semeados são gerados, não fotografia da igreja, e vão marcados como tal:
eles sustentam o desenho só enquanto não houver nenhuma fotografia real. Eles
nunca afirmam fato nenhum — não carregam data nem nome de pessoa.

A home separa fotografia de arte: a abertura e o mosaico usam só fotografias
(cortar um cartaz apaga o texto dele); artes e cartazes vão inteiros para o Mural.
"""

from __future__ import annotations

from django.templatetags.static import static
from django.utils import timezone
from django.utils.dateformat import format as date_format

# Cena de cada quadro semeado. A descrição é o texto alternativo real da imagem
# gerada; a legenda é a anotação curta que aparece sob o quadro.
SEEDED_FRAMES = (
    ("seed-01", "Congregação reunida em um templo simples, vista do fundo da sala", "Culto de domingo"),
    ("seed-02", "Bíblia aberta sobre uma mesa de madeira, luz de janela", "Palavra que edifica"),
    ("seed-03", "Rua de casario colonial com telhados de telha em cidade serrana", "Casario da cidade"),
    ("seed-04", "Pessoas conversando em pequenos grupos depois do culto", "Depois do culto"),
    ("seed-05", "Café sendo servido em xícaras pequenas sobre uma mesa simples", "Café e comunhão"),
    ("seed-06", "Vale de montanha verde com neblina da manhã e telhados ao fundo", "Manhã na serra"),
    ("seed-07", "Mãos apoiadas sobre um hinário fechado no colo", "Hinos de sempre"),
    ("seed-08", "Passarela de madeira atravessando um rio raso entre margens verdes", "Caminho do rio"),
    ("seed-09", "Fachada de uma pequena capela branca de roça com frontão de sino", "Nossa casa"),
    ("seed-10", "Interior vazio de templo simples com bancos de madeira e janelas altas", "Antes de abrir"),
    ("seed-11", "Cidade serrana vista de cima, telhados junto ao rio e encostas de mata", "Santa Leopoldina"),
    ("seed-12", "Duas pessoas conversando sentadas no degrau de pedra de um prédio simples", "Conversa no degrau"),
)


def _seeded(count):
    frames = []
    for slug, alt, caption in SEEDED_FRAMES[:count]:
        frames.append(
            {
                "url": static(f"img/archive/{slug}.jpg"),
                "alt": alt,
                "caption": caption,
                "credit": "",
                "byline": "",
                "date": "",
                "permalink": "",
                "kind": "photo",
                "featured": False,
                "synthetic": True,
            }
        )
    return frames


def _month_year(value):
    """Mês e ano no idioma do site (``ago 2026``); ``strftime`` sairia em inglês."""
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return date_format(value, "b Y")


def _byline(credit):
    """Crédito que vale mostrar sob o quadro.

    O crédito padrão do Instagram se repetiria em todos os quadros; a seção já
    leva o link do perfil. Crédito de fotógrafo ou outra fonte continua visível.
    """
    if credit.strip().lower().startswith("instagram"):
        return ""
    return credit


def _as_frame(record):
    return {
        "url": record.image.url,
        "alt": record.alt_text or record.caption,
        "caption": record.caption,
        "credit": record.credit,
        "byline": _byline(record.credit),
        "date": _month_year(record.taken_at),
        "permalink": record.permalink,
        "kind": record.kind,
        "featured": record.featured,
        "synthetic": False,
    }


def _published(count, kind=None):
    """Até ``count`` quadros publicados, do mais recente ao mais antigo.

    A fotografia marcada como destaque entra mesmo que seja mais antiga que o corte.
    """
    from apps.public.models import ArchiveFrame

    if count <= 0:
        return []
    try:
        visible = ArchiveFrame.objects.filter(is_visible=True).exclude(image="")
        if kind:
            visible = visible.filter(kind=kind)
        records = list(visible[:count])
        featured = visible.filter(kind=ArchiveFrame.Kind.PHOTO, featured=True).first()
    except Exception:  # noqa: BLE001 - banco indisponível não deve derrubar a home
        return []

    if featured and featured not in records:
        records = [featured] + records[: count - 1]
    return [_as_frame(record) for record in records]


def archive_frames(count=12):
    """Devolve até ``count`` quadros, priorizando o acervo publicado.

    Imagens de reserva completam a lista e são marcadas como sintéticas.
    """
    frames = _published(count)
    if len(frames) < count:
        frames.extend(_seeded(count - len(frames)))
    return frames[:count]


# Fotografias do mosaico “A vida em comunidade”, além da que abre a página.
MOSAIC_PHOTOS = 4


def home_archive(count=12):
    """Divide o acervo da home em abertura, mosaico de fotografias e mural de artes.

    Sem nenhuma fotografia real, abertura e mosaico usam as imagens ilustrativas —
    nunca misturadas a fotos reais. O mural só mostra artes publicadas.
    ``count`` é o total de quadros publicados na home (abertura, mosaico e mural).
    """
    # O limite configurado vale para o total; fotografias têm a vez primeiro,
    # para uma sequência de cartazes recentes não esvaziar abertura e mosaico.
    photos = _published(min(count, 1 + MOSAIC_PHOTOS), kind="photo")
    posters = _published(count - len(photos), kind="art")

    is_seeded = not photos
    if is_seeded:
        photos = _seeded(1 + MOSAIC_PHOTOS)

    hero = next((frame for frame in photos if frame["featured"]), photos[0])
    mosaic = [frame for frame in photos if frame is not hero][:MOSAIC_PHOTOS]
    # Com poucas fotos, um convite para enviar fotos fecha o mosaico sem buracos.
    invite = len(mosaic) < MOSAIC_PHOTOS
    return {
        "hero": hero,
        "photos": mosaic,
        "posters": posters,
        "invite": invite,
        "mosaic_size": len(mosaic) + int(invite),
        "is_seeded": is_seeded,
    }
