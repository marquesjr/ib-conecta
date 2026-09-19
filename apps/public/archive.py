"""Fotografias da home: acervo real com reserva ilustrativa quando necessário.

Ordem de preferência, e ela é deliberada:

1. Quadros do Instagram sincronizados pela API oficial.
2. Quadros curados no CMS pela comunicação.
3. Quadros semeados sintéticos que acompanham o repositório.

Os quadros semeados são gerados, não fotografia da igreja, e vão marcados como tal:
eles sustentam o desenho até a conta profissional do Instagram ser conectada. Eles
nunca afirmam fato nenhum — não carregam data nem nome de pessoa.
"""

from __future__ import annotations

from django.templatetags.static import static

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
                "date": "",
                "permalink": "",
                "synthetic": True,
            }
        )
    return frames


def archive_frames(count=12):
    """Devolve até ``count`` fotos, priorizando o acervo publicado.

    A primeira abre a homepage; as restantes compõem a galeria editorial.
    Imagens de reserva são marcadas como sintéticas para identificação na página.
    """
    from apps.public.models import ArchiveFrame

    frames = []
    try:
        records = list(ArchiveFrame.objects.filter(is_visible=True)[:count])
    except Exception:  # noqa: BLE001 - banco indisponível não deve derrubar a home
        records = []

    for record in records:
        if not record.image:
            continue
        frames.append(
            {
                "url": record.image.url,
                "alt": record.alt_text or record.caption,
                "caption": record.caption,
                "credit": record.credit,
                "date": record.taken_at.strftime("%b %Y").lower() if record.taken_at else "",
                "permalink": record.permalink,
                "synthetic": False,
            }
        )

    if len(frames) < count:
        seeded = _seeded(count - len(frames))
        frames.extend(seeded)

    return frames[:count]
