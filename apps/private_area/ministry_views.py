from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
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
    AssignmentStatus,
    Ministry,
    MonthlySchedule,
    ScheduleAssignment,
    Substitution,
)
from apps.public.whatsapp import build_whatsapp_share_url


def _can_manage_schedules(user) -> bool:
    return user_has_permission(user, Permission.MANAGE_MINISTRY_SCHEDULES)


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


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def schedule_detail(request: HttpRequest, pk: int) -> HttpResponse:
    schedule = get_object_or_404(
        MonthlySchedule.objects.select_related("ministry"),
        pk=pk,
    )
    can_manage = _can_manage_schedules(request.user)
    share_title = f"Escala de {schedule.label()} — {schedule.ministry.name}"
    return render(
        request,
        "private_area/schedule_detail.html",
        {
            "schedule": schedule,
            "assignments": schedule.assignments.select_related("participant").prefetch_related(
                "substitutions__replaced",
                "substitutions__substitute",
            ),
            "assignment_form": AssignmentForm() if can_manage else None,
            "can_manage_schedules": can_manage,
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
            "assignments": schedule.assignments.select_related("participant"),
        },
    )
