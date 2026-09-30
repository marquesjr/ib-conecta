from dataclasses import dataclass, field
from datetime import datetime
from itertools import groupby

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.accounts.audit import AuditAction, log_audit
from apps.accounts.decorators import permission_required
from apps.accounts.permissions import Permission, user_has_permission
from apps.private_area.calendar import build_schedule_ics
from apps.private_area.forms import (
    AssignmentForm,
    MinistryForm,
    MonthlyScheduleForm,
    SubstitutionForm,
)
from apps.private_area.models import (
    WORSHIP_FUNCTIONS,
    AssignmentStatus,
    Ministry,
    MonthlySchedule,
    ScheduleAssignment,
    Substitution,
)
from apps.public.whatsapp import build_whatsapp_share_url


def _can_manage_schedules(user) -> bool:
    return user_has_permission(user, Permission.MANAGE_MINISTRY_SCHEDULES)


@dataclass
class ServiceGroup:
    """Convocações de um mesmo culto (mesma data e horário) dentro da escala."""

    starts_at: datetime
    assignments: list = field(default_factory=list)
    is_past: bool = False

    @property
    def confirmed_count(self) -> int:
        return sum(1 for a in self.assignments if a.status == AssignmentStatus.CONFIRMED)


def _group_by_service(assignments, now) -> list[ServiceGroup]:
    return [
        ServiceGroup(starts_at=starts_at, assignments=list(items), is_past=starts_at < now)
        for starts_at, items in groupby(assignments, key=lambda a: a.starts_at)
    ]


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def ministry_list(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "private_area/ministry_list.html",
        {
            "ministries": Ministry.objects.all(),
            "can_manage_schedules": _can_manage_schedules(request.user),
        },
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["GET", "POST"])
def ministry_create(request: HttpRequest) -> HttpResponse:
    form = MinistryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ministry = form.save(commit=False)
        ministry.created_by = request.user
        ministry.save()
        log_audit(
            actor=request.user,
            action=AuditAction.MINISTRY_CREATED,
            metadata={"ministry_id": ministry.pk, "name": ministry.name},
        )
        messages.success(request, "Ministério cadastrado.")
        return redirect("private_area:ministry_detail", pk=ministry.pk)
    return render(request, "private_area/ministry_form.html", {"form": form})


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def ministry_detail(request: HttpRequest, pk: int) -> HttpResponse:
    ministry = get_object_or_404(Ministry, pk=pk)
    return render(
        request,
        "private_area/ministry_detail.html",
        {
            "ministry": ministry,
            "schedules": ministry.schedules.all(),
            "playlists": ministry.playlists.all()[:12],
            "can_manage_schedules": _can_manage_schedules(request.user),
        },
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["GET", "POST"])
def schedule_create(request: HttpRequest, pk: int) -> HttpResponse:
    ministry = get_object_or_404(Ministry, pk=pk)
    today = timezone.localdate()
    form = MonthlyScheduleForm(
        request.POST or None,
        initial={"year": today.year, "month": today.month},
    )
    if request.method == "POST" and form.is_valid():
        schedule = form.save(commit=False)
        schedule.ministry = ministry
        schedule.created_by = request.user
        try:
            schedule.save()
        except IntegrityError:
            form.add_error(None, "Já existe uma escala para este mês.")
        else:
            log_audit(
                actor=request.user,
                action=AuditAction.SCHEDULE_CREATED,
                metadata={
                    "schedule_id": schedule.pk,
                    "ministry_id": ministry.pk,
                    "year": schedule.year,
                    "month": schedule.month,
                },
            )
            messages.success(request, "Escala mensal criada.")
            return redirect("private_area:schedule_detail", pk=schedule.pk)
    return render(
        request,
        "private_area/schedule_form.html",
        {"form": form, "ministry": ministry},
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["GET", "POST"])
def schedule_edit(request: HttpRequest, pk: int) -> HttpResponse:
    schedule = get_object_or_404(
        MonthlySchedule.objects.select_related("ministry"),
        pk=pk,
    )
    form = MonthlyScheduleForm(request.POST or None, instance=schedule)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error(None, "Já existe uma escala para este mês.")
        else:
            log_audit(
                actor=request.user,
                action=AuditAction.SCHEDULE_UPDATED,
                metadata={
                    "schedule_id": schedule.pk,
                    "ministry_id": schedule.ministry_id,
                    "year": schedule.year,
                    "month": schedule.month,
                    "changed": form.changed_data,
                },
            )
            messages.success(request, "Escala atualizada.")
            return redirect("private_area:schedule_detail", pk=schedule.pk)
    return render(
        request,
        "private_area/schedule_form.html",
        {"form": form, "ministry": schedule.ministry, "schedule": schedule},
    )


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def schedule_detail(request: HttpRequest, pk: int) -> HttpResponse:
    schedule = get_object_or_404(
        MonthlySchedule.objects.select_related("ministry"),
        pk=pk,
    )
    can_manage = _can_manage_schedules(request.user)
    share_title = f"Escala de {schedule.label()} — {schedule.ministry.name}"
    assignments = list(
        schedule.assignments.select_related("participant").prefetch_related(
            "substitutions__replaced",
            "substitutions__substitute",
        )
    )
    now = timezone.now()
    services = _group_by_service(assignments, now)
    upcoming_services = [s for s in services if not s.is_past]
    # Os totais do topo falam dos próximos cultos; os já realizados ficam
    # recolhidos e só entram na conta quando não há mais nenhum pela frente.
    summary_assignments = (
        [a for s in upcoming_services for a in s.assignments] if upcoming_services else assignments
    )
    status_counts = {status: 0 for status in AssignmentStatus.values}
    for assignment in summary_assignments:
        status_counts[assignment.status] += 1
    return render(
        request,
        "private_area/schedule_detail.html",
        {
            "schedule": schedule,
            "assignments": assignments,
            "upcoming_services": upcoming_services,
            "past_services": [s for s in services if s.is_past],
            "my_pending": [
                a
                for a in assignments
                if a.participant_id == request.user.pk
                and a.status == AssignmentStatus.PENDING
                and a.starts_at >= now
            ],
            "summary_total": len(summary_assignments),
            "confirmed_count": status_counts[AssignmentStatus.CONFIRMED],
            "pending_count": status_counts[AssignmentStatus.PENDING],
            "declined_count": status_counts[AssignmentStatus.DECLINED],
            "assignment_form": AssignmentForm() if can_manage else None,
            "can_manage_schedules": can_manage,
            "worship_functions": WORSHIP_FUNCTIONS,
            "share_url": build_whatsapp_share_url(
                share_title,
                request.build_absolute_uri(),
            ),
        },
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["POST"])
def assignment_add(request: HttpRequest, pk: int) -> HttpResponse:
    schedule = get_object_or_404(MonthlySchedule, pk=pk)
    form = AssignmentForm(request.POST)
    if form.is_valid():
        assignment = form.save(commit=False)
        assignment.schedule = schedule
        assignment.save()
        messages.success(request, "Participante convocado.")
    else:
        messages.error(
            request,
            "Não foi possível convocar. Confira data, função e participante.",
        )
    return redirect("private_area:schedule_detail", pk=schedule.pk)


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["GET", "POST"])
def assignment_edit(request: HttpRequest, pk: int) -> HttpResponse:
    assignment = get_object_or_404(
        ScheduleAssignment.objects.select_related("schedule__ministry", "participant"),
        pk=pk,
    )
    form = AssignmentForm(request.POST or None, instance=assignment)
    if request.method == "POST" and form.is_valid():
        assignment = form.save(commit=False)
        # A new person or a new date needs a fresh confirmation.
        if {"participant", "starts_at"} & set(form.changed_data):
            assignment.status = AssignmentStatus.PENDING
        assignment.save()
        log_audit(
            actor=request.user,
            action=AuditAction.ASSIGNMENT_UPDATED,
            metadata={"assignment_id": assignment.pk, "changed": form.changed_data},
        )
        messages.success(request, "Convocação atualizada.")
        return redirect("private_area:schedule_detail", pk=assignment.schedule_id)
    return render(
        request,
        "private_area/assignment_form.html",
        {
            "form": form,
            "assignment": assignment,
            "worship_functions": WORSHIP_FUNCTIONS,
        },
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["POST"])
def assignment_remove(request: HttpRequest, pk: int) -> HttpResponse:
    assignment = get_object_or_404(ScheduleAssignment, pk=pk)
    schedule_id = assignment.schedule_id
    log_audit(
        actor=request.user,
        action=AuditAction.ASSIGNMENT_REMOVED,
        metadata={
            "assignment_id": assignment.pk,
            "schedule_id": schedule_id,
            "participant_id": assignment.participant_id,
            "function": assignment.function,
        },
    )
    assignment.delete()
    messages.success(request, "Convocação removida da escala.")
    return redirect("private_area:schedule_detail", pk=schedule_id)


@permission_required(Permission.ACCESS_PRIVATE_AREA)
@require_http_methods(["GET", "POST"])
def assignment_respond(request: HttpRequest, pk: int) -> HttpResponse:
    assignment = get_object_or_404(
        ScheduleAssignment.objects.select_related("schedule__ministry", "participant"),
        pk=pk,
    )
    if assignment.participant_id != request.user.pk:
        raise PermissionDenied
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "confirm":
            assignment.status = AssignmentStatus.CONFIRMED
            assignment.save(update_fields=["status"])
            log_audit(
                actor=request.user,
                action=AuditAction.ASSIGNMENT_CONFIRMED,
                metadata={"assignment_id": assignment.pk},
            )
            messages.success(request, "Presença confirmada.")
        elif action == "decline":
            assignment.status = AssignmentStatus.DECLINED
            assignment.save(update_fields=["status"])
            log_audit(
                actor=request.user,
                action=AuditAction.ASSIGNMENT_DECLINED,
                metadata={"assignment_id": assignment.pk},
            )
            messages.success(request, "Convocação recusada.")
        return redirect("private_area:assignment_respond", pk=assignment.pk)
    return render(
        request,
        "private_area/assignment_respond.html",
        {"assignment": assignment},
    )


@permission_required(Permission.MANAGE_MINISTRY_SCHEDULES)
@require_http_methods(["GET", "POST"])
def assignment_substitute(request: HttpRequest, pk: int) -> HttpResponse:
    assignment = get_object_or_404(
        ScheduleAssignment.objects.select_related("schedule__ministry", "participant"),
        pk=pk,
    )
    form = SubstitutionForm(request.POST or None, assignment=assignment)
    if request.method == "POST" and form.is_valid():
        substitute = form.cleaned_data["substitute"]
        replaced = assignment.participant
        Substitution.objects.create(
            assignment=assignment,
            replaced=replaced,
            substitute=substitute,
            created_by=request.user,
        )
        assignment.participant = substitute
        assignment.status = AssignmentStatus.PENDING
        assignment.save(update_fields=["participant", "status"])
        log_audit(
            actor=request.user,
            action=AuditAction.ASSIGNMENT_SUBSTITUTED,
            metadata={
                "assignment_id": assignment.pk,
                "replaced_user_id": replaced.pk,
                "substitute_user_id": substitute.pk,
            },
        )
        messages.success(request, "Substituição registrada.")
        return redirect("private_area:schedule_detail", pk=assignment.schedule_id)
    return render(
        request,
        "private_area/assignment_substitute.html",
        {"form": form, "assignment": assignment},
    )


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def schedule_calendar(request: HttpRequest, pk: int) -> HttpResponse:
    schedule = get_object_or_404(
        MonthlySchedule.objects.select_related("ministry"),
        pk=pk,
    )
    content = build_schedule_ics(schedule, request)
    response = HttpResponse(content, content_type="text/calendar; charset=utf-8")
    filename = f"escala-{schedule.ministry_id}-{schedule.year}-{schedule.month:02d}.ics"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def schedule_print(request: HttpRequest, pk: int) -> HttpResponse:
    schedule = get_object_or_404(
        MonthlySchedule.objects.select_related("ministry"),
        pk=pk,
    )
    return render(
        request,
        "private_area/schedule_print.html",
        {
            "schedule": schedule,
            "services": _group_by_service(
                schedule.assignments.select_related("participant"),
                timezone.now(),
            ),
        },
    )
