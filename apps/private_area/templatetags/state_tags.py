"""O selo de estado da área privada.

A área privada é modo Operar: quem abre "Minhas convocações" precisa ver de relance
qual linha ainda espera resposta dela. Antes deste selo o estado era texto cinza atrás
de um ponto médio, e "CONFIRMADO" e "PENDENTE" tinham exatamente o mesmo peso.

Os três tons se distinguem pela forma da marca, não só pela cor, porque estas telas são
impressas em preto e branco (escala de ministério, coletânea) e porque cor sozinha não
chega a quem não a distingue:

- ``open``    caixa vazada — ainda espera alguém
- ``settled`` caixa cheia — resolvido
- ``closed``  caixa cortada — resolvido pelo não
"""

from django import template

register = template.Library()

OPEN = "open"
SETTLED = "settled"
CLOSED = "closed"

# Chave de estado para tom. Reúne os vocabulários de AssignmentStatus,
# BudgetLineStatus, SongStatus, EventRegistration.Status e PixStatus.
TONES = {
    "pending": OPEN,
    "draft": OPEN,
    "new": OPEN,
    "in_progress": OPEN,
    "waitlisted": OPEN,
    "confirmed": SETTLED,
    "approved": SETTLED,
    "published": SETTLED,
    "paid": SETTLED,
    "done": SETTLED,
    "checked_in": SETTLED,
    "declined": CLOSED,
    "rejected": CLOSED,
    "cancelled": CLOSED,
    "waived": CLOSED,
}

# Descrição do tom para leitor de tela, já que a marca é decorativa.
TONE_MEANING = {
    OPEN: "aguardando",
    SETTLED: "resolvido",
    CLOSED: "encerrado",
}


@register.inclusion_tag("private_area/_state.html")
def state(key, label=""):
    """Desenha o selo de estado para ``key``, rotulado com ``label``.

    Chave desconhecida cai em ``open``: um estado que o desenho não previu é
    justamente o que a liderança precisa notar, não esconder.
    """
    tone = TONES.get(str(key or "").strip().lower(), OPEN)
    return {
        "tone": tone,
        "label": label or key,
        "meaning": TONE_MEANING[tone],
    }
