"""Subnavegação da área privada: só as seções que o perfil pode abrir."""

from django import template
from django.urls import reverse

from apps.accounts.permissions import Permission, user_has_permission

register = template.Library()

# (rótulo, nome da URL de entrada, prefixos de url_name que marcam a seção ativa)
SECTIONS = (
    ("Início", "home", ("home",)),
    ("Ministérios", "ministry_list", ("ministry_", "schedule_", "assignment_")),
    ("Louvores", "songbook", ("song",)),
    ("Playlists", "playlist_list", ("playlist_",)),
    ("Documentos", "document_library", ("document_",)),
    ("Eventos", "event_calendar", ("event_", "retreat_")),
)


def _can_see_events(user) -> bool:
    return user_has_permission(user, Permission.MANAGE_EVENT_OPERATIONS) or user_has_permission(
        user, Permission.MANAGE_FINANCES
    )


@register.inclusion_tag("private_area/_private_nav.html", takes_context=True)
def private_nav(context):
    request = context["request"]
    current = getattr(request.resolver_match, "url_name", "") or ""
    items = []
    for label, url_name, prefixes in SECTIONS:
        if url_name == "event_calendar" and not _can_see_events(request.user):
            continue
        active = current == "home" if url_name == "home" else current.startswith(prefixes)
        items.append(
            {"label": label, "url": reverse(f"private_area:{url_name}"), "active": active}
        )
    return {"items": items}
