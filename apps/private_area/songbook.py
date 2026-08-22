import io

import segno
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse

from apps.accounts.permissions import Permission, user_has_permission
from apps.private_area.models import Song, SongReference, SongStatus

PRINT_LAYOUTS = {"full", "lyrics", "chords", "index"}


def can_manage_songbook(user) -> bool:
    return user_has_permission(user, Permission.MANAGE_MINISTRY_SCHEDULES)


def visible_songs(user) -> QuerySet[Song]:
    songs = Song.objects.prefetch_related("references", "versions")
    if not can_manage_songbook(user):
        songs = songs.filter(status=SongStatus.PUBLISHED)
    return songs


def filter_songs(queryset: QuerySet[Song], *, query: str = "", tag: str = "") -> QuerySet[Song]:
    if query:
        queryset = queryset.filter(title__icontains=query.strip())
    if tag:
        queryset = queryset.filter(tags__icontains=tag.strip())
    return queryset


def resolve_print_layout(value: str | None) -> str:
    if value in PRINT_LAYOUTS:
        return value
    return "full"


def reference_url(request: HttpRequest, reference: SongReference) -> str:
    return request.build_absolute_uri(
        reverse("private_area:song_reference", args=[reference.token])
    )


def qr_svg(data: str) -> str:
    buffer = io.BytesIO()
    segno.make(data, error="m").save(buffer, kind="svg", xmldecl=False, scale=4)
    return buffer.getvalue().decode()


def print_references(request: HttpRequest, song: Song) -> list[dict]:
    items = []
    for reference in song.references.all():
        url = reference_url(request, reference)
        items.append(
            {
                "reference": reference,
                "url": url,
                "qr_svg": qr_svg(url),
            }
        )
    return items
