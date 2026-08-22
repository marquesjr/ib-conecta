from django.contrib import messages
from django.db.models import Max
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.audit import AuditAction, log_audit
from apps.accounts.decorators import permission_required
from apps.accounts.permissions import Permission, user_has_permission
from apps.private_area.calendar import build_playlist_ics
from apps.private_area.forms import PlaylistItemForm, WeeklyPlaylistForm
from apps.private_area.models import Ministry, WeeklyPlaylist
from apps.private_area.songbook import resolve_print_layout
from apps.public.whatsapp import build_whatsapp_share_url


def _can_manage_playlists(user) -> bool:
    return user_has_permission(user, Permission.MANAGE_MINISTRY_SCHEDULES)


def _playlist_or_404(pk: int) -> WeeklyPlaylist:
    return get_object_or_404(
        WeeklyPlaylist.objects.select_related("ministry"),
        pk=pk,
    )


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def playlist_list(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "private_area/playlist_list.html",
        {
            "playlists": WeeklyPlaylist.objects.select_related("ministry"),
        },
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["GET", "POST"])
def playlist_create(request: HttpRequest, pk: int) -> HttpResponse:
    ministry = get_object_or_404(Ministry, pk=pk)
    form = WeeklyPlaylistForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        playlist = form.save(commit=False)
        playlist.ministry = ministry
        playlist.created_by = request.user
        playlist.save()
        log_audit(
            actor=request.user,
            action=AuditAction.PLAYLIST_CREATED,
            metadata={
                "playlist_id": playlist.pk,
                "ministry_id": ministry.pk,
                "kind": playlist.kind,
            },
        )
        messages.success(request, "Playlist semanal criada.")
        return redirect("private_area:playlist_detail", pk=playlist.pk)
    return render(
        request,
        "private_area/playlist_form.html",
        {"form": form, "ministry": ministry},
    )


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def playlist_detail(request: HttpRequest, pk: int) -> HttpResponse:
    playlist = _playlist_or_404(pk)
    can_manage = _can_manage_playlists(request.user)
    share_title = f"{playlist.label()} — {playlist.ministry.name}"
    return render(
        request,
        "private_area/playlist_detail.html",
        {
            "playlist": playlist,
            "items": playlist.items.select_related("song", "version"),
            "item_form": PlaylistItemForm() if can_manage else None,
            "can_manage_playlists": can_manage,
            "share_url": build_whatsapp_share_url(
                share_title,
                request.build_absolute_uri(),
            ),
        },
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["POST"])
def playlist_item_add(request: HttpRequest, pk: int) -> HttpResponse:
    playlist = _playlist_or_404(pk)
    form = PlaylistItemForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.playlist = playlist
        if not item.position:
            last = playlist.items.aggregate(Max("position"))["position__max"] or 0
            item.position = last + 1
        item.save()
        log_audit(
            actor=request.user,
            action=AuditAction.PLAYLIST_ITEM_ADDED,
            metadata={
                "playlist_id": playlist.pk,
                "song_id": item.song_id,
                "position": item.position,
            },
        )
        messages.success(request, "Louvor adicionado à playlist.")
    else:
        messages.error(
            request,
            "Não foi possível adicionar. Use um louvor publicado da coletânea.",
        )
    return redirect("private_area:playlist_detail", pk=playlist.pk)


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def playlist_calendar(request: HttpRequest, pk: int) -> HttpResponse:
    playlist = _playlist_or_404(pk)
    content = build_playlist_ics(playlist, request)
    response = HttpResponse(content, content_type="text/calendar; charset=utf-8")
    when = playlist.starts_at.strftime("%Y-%m-%d")
    filename = f"playlist-{playlist.ministry_id}-{when}.ics"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def playlist_print(request: HttpRequest, pk: int) -> HttpResponse:
    playlist = _playlist_or_404(pk)
    layout = resolve_print_layout(request.GET.get("layout"))
    items = playlist.items.select_related("song", "version")
    return render(
        request,
        "private_area/playlist_print.html",
        {
            "playlist": playlist,
            "items": items,
            "layout": layout,
        },
    )
