"""Destaque de "Quando" e "Onde" na página de evento."""

from urllib.parse import urlencode

from django.utils import timezone
from django.utils.formats import date_format

from apps.public.templatetags.public_tags import hour_label


def _local(value):
    return timezone.localtime(value) if timezone.is_aware(value) else value


def when_label(starts_at, ends_at=None) -> str:
    """``Sábado, 24 de outubro de 2026 · 17h às 19h`` ou o intervalo entre dias."""
    start = _local(starts_at)
    start_day = date_format(start, r"l, j \d\e F \d\e Y").capitalize()
    if not ends_at:
        return f"{start_day} · {hour_label(start)}"
    end = _local(ends_at)
    if end.date() == start.date():
        return f"{start_day} · {hour_label(start)} às {hour_label(end)}"
    end_day = date_format(end, r"l, j \d\e F \d\e Y").lower()
    return f"{start_day}, {hour_label(start)}, até {end_day}, {hour_label(end)}"


def directions_url(location: str) -> str:
    if not location:
        return ""
    return "https://www.google.com/maps/search/?" + urlencode({"api": 1, "query": location})


def spots_left(event) -> int | None:
    """Vagas restantes; só retiros controlam lotação (os demais não têm lista de espera)."""
    if not (event.requires_registration and event.is_retreat and event.capacity is not None):
        return None
    from apps.public.retreats import occupancy

    return max(event.capacity - occupancy(event), 0)
