from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.accounts.audit import AuditAction, log_audit
from apps.accounts.decorators import permission_required
from apps.accounts.permissions import Permission, user_has_permission
from apps.private_area.models import EventOperation, EventTeamMember
from apps.public.models import EventFamilyMember, EventRegistration
from apps.public.retreats import discard_due_retreat_sensitive_data


def user_can_access_event_staff_area(user, operation: EventOperation) -> bool:
    if user_has_permission(user, Permission.MANAGE_EVENT_OPERATIONS):
        return True
    if not operation.public_event.is_retreat:
        return False
    return EventTeamMember.objects.filter(team__operation=operation, user=user).exists()


def require_retreat_staff(user, operation: EventOperation) -> None:
    if not user_can_access_event_staff_area(user, operation):
        raise PermissionDenied


@permission_required(Permission.ACCESS_PRIVATE_AREA)
def retreat_roster(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(
        EventOperation.objects.select_related("public_event"),
        pk=pk,
    )
    require_retreat_staff(request.user, operation)
    discard_due_retreat_sensitive_data()
    registrations = (
        EventRegistration.objects.filter(event=operation.public_event)
        .prefetch_related("family_members")
        .order_by("status", "name")
    )
    confirmed = [item for item in registrations if item.status == EventRegistration.Status.CONFIRMED]
    waitlisted = [item for item in registrations if item.status == EventRegistration.Status.WAITLISTED]
    return render(
        request,
        "private_area/retreat_roster.html",
        {
            "operation": operation,
            "confirmed": confirmed,
            "waitlisted": waitlisted,
            "pix_choices": EventRegistration.PixStatus.choices,
            "can_manage_pix": user_has_permission(
                request.user, Permission.MANAGE_EVENT_OPERATIONS
            ),
            "documents": operation.documents.all(),
        },
    )


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def retreat_pix_status(request: HttpRequest, pk: int) -> HttpResponse:
    registration = get_object_or_404(
        EventRegistration.objects.select_related("event__operation"),
        pk=pk,
    )
    operation = registration.event.operation
    status = request.POST.get("pix_status")
    if status in EventRegistration.PixStatus.values:
        registration.pix_status = status
        registration.save(update_fields=["pix_status"])
        log_audit(
            actor=request.user,
            action=AuditAction.RETREAT_PIX_STATUS_CHANGED,
            metadata={
                "registration_id": registration.pk,
                "pix_status": status,
            },
        )
    return redirect("private_area:retreat_roster", pk=operation.pk)


@permission_required(Permission.ACCESS_PRIVATE_AREA)
@require_http_methods(["POST"])
def retreat_check_in(request: HttpRequest, pk: int) -> HttpResponse:
    registration = get_object_or_404(
        EventRegistration.objects.select_related("event__operation"),
        pk=pk,
    )
    operation = registration.event.operation
    require_retreat_staff(request.user, operation)
    if registration.checked_in_at is None:
        registration.checked_in_at = timezone.now()
        registration.save(update_fields=["checked_in_at"])
        log_audit(
            actor=request.user,
            action=AuditAction.RETREAT_CHECKED_IN,
            metadata={"registration_id": registration.pk},
        )
    return redirect("private_area:retreat_roster", pk=operation.pk)


@permission_required(Permission.ACCESS_PRIVATE_AREA)
@require_http_methods(["POST"])
def retreat_member_check_in(request: HttpRequest, pk: int) -> HttpResponse:
    member = get_object_or_404(
        EventFamilyMember.objects.select_related("registration__event__operation"),
        pk=pk,
    )
    operation = member.registration.event.operation
    require_retreat_staff(request.user, operation)
    if member.checked_in_at is None:
        member.checked_in_at = timezone.now()
        member.save(update_fields=["checked_in_at"])
        log_audit(
            actor=request.user,
            action=AuditAction.RETREAT_CHECKED_IN,
            metadata={"family_member_id": member.pk},
        )
    return redirect("private_area:retreat_roster", pk=operation.pk)
