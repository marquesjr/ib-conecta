from pathlib import Path

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.audit import AuditAction, log_audit
from apps.accounts.decorators import permission_required
from apps.accounts.permissions import Permission, user_has_permission
from apps.private_area.forms import PrivateDocumentForm
from apps.private_area.models import (
    EventChecklistItem,
    EventOperation,
    EventTask,
    PrivateDocument,
    ScheduleAssignment,
    WeeklyPlaylist,
)


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def home(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "private_area/home.html",
        {
            "can_manage_documents": user_has_permission(
                request.user, Permission.MANAGE_CONTENT
            ),
            "can_manage_schedules": user_has_permission(
                request.user, Permission.MANAGE_MINISTRY_SCHEDULES
            ),
            "can_access_event_operations": user_has_permission(
                request.user, Permission.MANAGE_EVENT_OPERATIONS
            )
            or user_has_permission(request.user, Permission.MANAGE_FINANCES),
            "my_assignments": ScheduleAssignment.objects.filter(
                participant=request.user
            )
            .select_related("schedule__ministry")
            .order_by("starts_at")[:12],
            "upcoming_playlists": WeeklyPlaylist.objects.select_related("ministry").order_by(
                "starts_at"
            )[:8],
            "my_event_tasks": EventTask.objects.filter(assignee=request.user)
            .select_related("operation__public_event")
            .order_by("done", "title")[:12],
            "my_event_checklist": EventChecklistItem.objects.filter(assignee=request.user)
            .select_related("operation__public_event")
            .order_by("done", "label")[:12],
            "my_retreats": EventOperation.objects.filter(
                public_event__is_retreat=True,
                teams__members__user=request.user,
            )
            .select_related("public_event")
            .distinct(),
        },
    )


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def document_library(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "private_area/document_library.html",
        {
            "documents": PrivateDocument.objects.visible_to(request.user),
            "can_manage_documents": user_has_permission(
                request.user, Permission.MANAGE_CONTENT
            ),
        },
    )


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def document_download(request: HttpRequest, pk: int) -> HttpResponse:
    document = get_object_or_404(PrivateDocument, pk=pk)
    if not document.is_visible_to(request.user):
        raise PermissionDenied
    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=Path(document.file.name).name,
    )


@permission_required(Permission.MANAGE_CONTENT)
@require_http_methods(["GET", "POST"])
def document_upload(request: HttpRequest) -> HttpResponse:
    form = PrivateDocumentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.created_by = request.user
        document.save()
        log_audit(
            actor=request.user,
            action=AuditAction.DOCUMENT_UPLOADED,
            metadata={"document_id": document.pk, "title": document.title},
        )
        messages.success(request, "Documento enviado para a biblioteca privada.")
        return redirect("private_area:document_library")
    return render(request, "private_area/document_upload.html", {"form": form})
