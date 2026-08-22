from pathlib import Path

from django.contrib import messages
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.accounts.audit import AuditAction, log_audit
from apps.accounts.decorators import permission_required
from apps.accounts.permissions import Permission
from apps.private_area.forms import SongForm, SongReferenceFormSet, SongVersionFormSet
from apps.private_area.models import Song, SongReference, SongStatus
from apps.private_area.songbook import (
    can_manage_songbook,
    filter_songs,
    print_references,
    resolve_print_layout,
    visible_songs,
)


def _song_for_user(user, slug: str) -> Song:
    return get_object_or_404(visible_songs(user), slug=slug)


def _song_forms(request: HttpRequest, song: Song):
    form = SongForm(request.POST or None, request.FILES or None, instance=song)
    references = SongReferenceFormSet(
        request.POST or None, instance=song, prefix="references"
    )
    versions = SongVersionFormSet(request.POST or None, instance=song, prefix="versions")
    return form, references, versions


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def songbook(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "")
    tag = request.GET.get("tag", "")
    songs = filter_songs(visible_songs(request.user), query=query, tag=tag)
    return render(
        request,
        "private_area/songbook.html",
        {
            "songs": songs,
            "query": query,
            "tag": tag,
            "can_manage_songbook": can_manage_songbook(request.user),
        },
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["GET", "POST"])
def song_create(request: HttpRequest) -> HttpResponse:
    song = Song()
    form, references, versions = _song_forms(request, song)
    if request.method == "POST" and form.is_valid() and references.is_valid() and versions.is_valid():
        song = form.save(commit=False)
        song.created_by = request.user
        song.status = SongStatus.DRAFT
        song.save()
        references.instance = song
        references.save()
        versions.instance = song
        versions.save()
        log_audit(
            actor=request.user,
            action=AuditAction.SONG_CREATED,
            metadata={"song_id": song.pk, "title": song.title},
        )
        messages.success(request, "Louvor salvo como rascunho.")
        return redirect("private_area:song_detail", slug=song.slug)
    return render(
        request,
        "private_area/song_form.html",
        {
            "form": form,
            "references": references,
            "versions": versions,
            "editing": False,
        },
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["GET", "POST"])
def song_edit(request: HttpRequest, slug: str) -> HttpResponse:
    song = get_object_or_404(Song, slug=slug)
    form, references, versions = _song_forms(request, song)
    if request.method == "POST" and form.is_valid() and references.is_valid() and versions.is_valid():
        song = form.save()
        references.save()
        versions.save()
        log_audit(
            actor=request.user,
            action=AuditAction.SONG_UPDATED,
            metadata={"song_id": song.pk, "title": song.title},
        )
        messages.success(request, "Louvor revisado.")
        return redirect("private_area:song_detail", slug=song.slug)
    return render(
        request,
        "private_area/song_form.html",
        {
            "form": form,
            "references": references,
            "versions": versions,
            "editing": True,
            "song": song,
        },
    )


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def song_detail(request: HttpRequest, slug: str) -> HttpResponse:
    song = _song_for_user(request.user, slug)
    return render(
        request,
        "private_area/song_detail.html",
        {
            "song": song,
            "can_manage_songbook": can_manage_songbook(request.user),
        },
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_POST
def song_publish(request: HttpRequest, slug: str) -> HttpResponse:
    song = get_object_or_404(Song, slug=slug)
    song.status = SongStatus.PUBLISHED
    song.published_at = timezone.now()
    song.save(update_fields=["status", "published_at", "updated_at"])
    log_audit(
        actor=request.user,
        action=AuditAction.SONG_PUBLISHED,
        metadata={"song_id": song.pk, "title": song.title},
    )
    messages.success(request, "Louvor publicado na coletânea privada.")
    return redirect("private_area:song_detail", slug=song.slug)


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def song_print(request: HttpRequest, slug: str) -> HttpResponse:
    song = _song_for_user(request.user, slug)
    layout = resolve_print_layout(request.GET.get("layout"))
    if layout == "index":
        layout = "full"
    return render(
        request,
        "private_area/song_print.html",
        {
            "songs": [song],
            "layout": layout,
            "print_items": [_print_item(request, song)],
        },
    )


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def songbook_print(request: HttpRequest) -> HttpResponse:
    layout = resolve_print_layout(request.GET.get("layout"))
    songs = filter_songs(
        visible_songs(request.user),
        query=request.GET.get("q", ""),
        tag=request.GET.get("tag", ""),
    )
    return render(
        request,
        "private_area/song_print.html",
        {
            "songs": songs,
            "layout": layout,
            "print_items": [_print_item(request, song) for song in songs],
            "tag": request.GET.get("tag", ""),
            "query": request.GET.get("q", ""),
        },
    )


def _print_item(request: HttpRequest, song: Song) -> dict:
    return {
        "song": song,
        "references": print_references(request, song),
    }


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def song_score(request: HttpRequest, slug: str) -> HttpResponse:
    song = _song_for_user(request.user, slug)
    if not song.score:
        raise Http404
    return FileResponse(
        song.score.open("rb"),
        as_attachment=True,
        filename=Path(song.score.name).name,
    )


@require_GET
def song_reference(request: HttpRequest, token: str) -> HttpResponse:
    reference = get_object_or_404(
        SongReference.objects.select_related("song"),
        token=token,
        song__status=SongStatus.PUBLISHED,
    )
    return redirect(reference.target_url)
