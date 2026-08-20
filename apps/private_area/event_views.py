from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods

from apps.accounts.audit import AuditAction, log_audit
from apps.accounts.decorators import permission_required
from apps.accounts.permissions import Permission, user_has_permission
from apps.private_area.forms import (
    EventBudgetLineForm,
    EventChecklistForm,
    EventFinalReportForm,
    EventMaterialForm,
    EventOperationDocumentForm,
    EventOperationForm,
    EventPlanningForm,
    EventRegistrantMessageForm,
    EventSupplierForm,
    EventTaskForm,
    EventTeamForm,
    EventTeamMemberForm,
)
from apps.private_area.models import (
    BudgetLineStatus,
    EventBudgetLine,
    EventChecklistItem,
    EventOperation,
    EventOperationDocument,
    EventTask,
    EventTeam,
)
from apps.public.cms import AGENDA_INDEX_SLUG
from apps.public.models import EventIndexPage, EventPage, EventRegistration


def _publish_event_page(data: dict) -> EventPage:
    index = EventIndexPage.objects.filter(slug=AGENDA_INDEX_SLUG).first()
    if index is None:
        raise ValueError("A agenda pública ainda não foi criada.")
    base = slugify(data["title"]) or "evento"
    slug = base
    suffix = 2
    while EventPage.objects.filter(slug=slug).exists():
        slug = f"{base}-{suffix}"
        suffix += 1
    event = EventPage(
        title=data["title"],
        slug=slug,
        starts_at=data["starts_at"],
        ends_at=data.get("ends_at"),
        location=data.get("location") or "",
        body=data.get("body") or "",
        requires_registration=bool(data.get("requires_registration")),
    )
    index.add_child(instance=event)
    event.save_revision().publish()
    return event


@permission_required(Permission.MANAGE_EVENT_OPERATIONS, Permission.MANAGE_FINANCES)
def event_calendar(request: HttpRequest) -> HttpResponse:
    today_year = timezone.localdate().year
    try:
        year = int(request.GET.get("year", today_year))
    except (TypeError, ValueError):
        year = today_year
    operations = (
        EventOperation.objects.select_related("public_event")
        .filter(public_event__starts_at__year=year)
        .order_by("public_event__starts_at")
    )
    return render(
        request,
        "private_area/event_calendar.html",
        {
            "operations": operations,
            "year": year,
            "previous_year": year - 1,
            "next_year": year + 1,
            "can_manage_operations": user_has_permission(
                request.user, Permission.MANAGE_EVENT_OPERATIONS
            ),
        },
    )


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["GET", "POST"])
def event_operation_create(request: HttpRequest) -> HttpResponse:
    form = EventOperationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        operation = form.save(commit=False)
        if not operation.public_event_id:
            operation.public_event = _publish_event_page(form.cleaned_data)
        operation.created_by = request.user
        operation.save()
        log_audit(
            actor=request.user,
            action=AuditAction.EVENT_OPERATION_CREATED,
            metadata={
                "operation_id": operation.pk,
                "event_id": operation.public_event_id,
            },
        )
        messages.success(request, "Operação vinculada ao evento da agenda.")
        return redirect("private_area:event_operation_detail", pk=operation.pk)
    return render(request, "private_area/event_operation_form.html", {"form": form})


@permission_required(Permission.MANAGE_EVENT_OPERATIONS, Permission.MANAGE_FINANCES)
def event_operation_detail(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(
        EventOperation.objects.select_related("public_event"),
        pk=pk,
    )
    can_manage = user_has_permission(request.user, Permission.MANAGE_EVENT_OPERATIONS)
    can_review_finances = user_has_permission(request.user, Permission.MANAGE_FINANCES)
    return render(
        request,
        "private_area/event_operation_detail.html",
        {
            "operation": operation,
            "registrations": EventRegistration.objects.filter(event=operation.public_event),
            "teams": operation.teams.prefetch_related("members__user"),
            "team_form": EventTeamForm() if can_manage else None,
            "team_member_form": EventTeamMemberForm() if can_manage else None,
            "tasks": operation.tasks.select_related("assignee"),
            "task_form": EventTaskForm() if can_manage else None,
            "checklist_items": operation.checklist_items.select_related("assignee"),
            "checklist_form": EventChecklistForm() if can_manage else None,
            "suppliers": operation.suppliers.all(),
            "supplier_form": EventSupplierForm() if can_manage else None,
            "materials": operation.materials.all(),
            "material_form": EventMaterialForm() if can_manage else None,
            "budget_lines": operation.budget_lines.all(),
            "budget_form": EventBudgetLineForm() if can_manage else None,
            "planning_form": EventPlanningForm(instance=operation) if can_manage else None,
            "message_form": EventRegistrantMessageForm() if can_manage else None,
            "report_form": EventFinalReportForm(instance=operation) if can_manage else None,
            "document_form": EventOperationDocumentForm() if can_manage else None,
            "documents": operation.documents.all() if can_manage else [],
            "can_manage_operations": can_manage,
            "can_review_finances": can_review_finances,
        },
    )


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_team_add(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(EventOperation, pk=pk)
    form = EventTeamForm(request.POST)
    if form.is_valid():
        team = form.save(commit=False)
        team.operation = operation
        team.save()
        messages.success(request, "Equipe adicionada.")
    else:
        messages.error(request, "Não foi possível adicionar a equipe.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_team_member_add(request: HttpRequest, pk: int) -> HttpResponse:
    team = get_object_or_404(EventTeam.objects.select_related("operation"), pk=pk)
    form = EventTeamMemberForm(request.POST)
    if form.is_valid():
        membership = form.save(commit=False)
        membership.team = team
        membership.save()
        messages.success(request, "Membro incluído na equipe.")
    else:
        messages.error(request, "Não foi possível incluir o membro.")
    return redirect("private_area:event_operation_detail", pk=team.operation_id)


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_planning_update(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(EventOperation, pk=pk)
    form = EventPlanningForm(request.POST, instance=operation)
    if form.is_valid():
        form.save()
        messages.success(request, "Planejamento atualizado.")
    else:
        messages.error(request, "Não foi possível atualizar o planejamento.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)



@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_task_add(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(EventOperation, pk=pk)
    form = EventTaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.operation = operation
        task.save()
        messages.success(request, "Tarefa atribuída.")
    else:
        messages.error(request, "Não foi possível atribuir a tarefa.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)


@permission_required(Permission.ACCESS_PRIVATE_AREA)
@require_http_methods(["GET", "POST"])
def event_task_update(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(
        EventTask.objects.select_related("operation__public_event", "assignee"),
        pk=pk,
    )
    if task.assignee_id != request.user.pk:
        raise PermissionDenied
    if request.method == "POST" and request.POST.get("action") == "complete":
        task.done = True
        task.save(update_fields=["done"])
        messages.success(request, "Tarefa concluída.")
        return redirect("private_area:event_task_update", pk=task.pk)
    return render(request, "private_area/event_task_update.html", {"task": task})


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_checklist_add(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(EventOperation, pk=pk)
    form = EventChecklistForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.operation = operation
        item.save()
        messages.success(request, "Item de checklist atribuído.")
    else:
        messages.error(request, "Não foi possível atribuir o item.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)


@permission_required(Permission.ACCESS_PRIVATE_AREA)
@require_http_methods(["GET", "POST"])
def event_checklist_update(request: HttpRequest, pk: int) -> HttpResponse:
    item = get_object_or_404(
        EventChecklistItem.objects.select_related("operation__public_event", "assignee"),
        pk=pk,
    )
    if item.assignee_id != request.user.pk:
        raise PermissionDenied
    if request.method == "POST" and request.POST.get("action") == "complete":
        item.done = True
        item.save(update_fields=["done"])
        messages.success(request, "Item de checklist concluído.")
        return redirect("private_area:event_checklist_update", pk=item.pk)
    return render(request, "private_area/event_checklist_update.html", {"item": item})


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_supplier_add(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(EventOperation, pk=pk)
    form = EventSupplierForm(request.POST)
    if form.is_valid():
        supplier = form.save(commit=False)
        supplier.operation = operation
        supplier.save()
        messages.success(request, "Fornecedor registrado.")
    else:
        messages.error(request, "Não foi possível registrar o fornecedor.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_material_add(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(EventOperation, pk=pk)
    form = EventMaterialForm(request.POST)
    if form.is_valid():
        material = form.save(commit=False)
        material.operation = operation
        material.save()
        messages.success(request, "Material registrado.")
    else:
        messages.error(request, "Não foi possível registrar o material.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_budget_add(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(EventOperation, pk=pk)
    form = EventBudgetLineForm(request.POST)
    if form.is_valid():
        line = form.save(commit=False)
        line.operation = operation
        line.created_by = request.user
        line.save()
        messages.success(request, "Linha de orçamento enviada para aprovação.")
    else:
        messages.error(request, "Não foi possível registrar o orçamento.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)


@permission_required(Permission.MANAGE_FINANCES)
@require_http_methods(["POST"])
def event_budget_review(request: HttpRequest, pk: int) -> HttpResponse:
    line = get_object_or_404(
        EventBudgetLine.objects.select_related("operation"),
        pk=pk,
    )
    action = request.POST.get("action")
    if action == "approve":
        line.status = BudgetLineStatus.APPROVED
        line.reviewed_by = request.user
        line.save(update_fields=["status", "reviewed_by"])
        log_audit(
            actor=request.user,
            action=AuditAction.EVENT_BUDGET_APPROVED,
            metadata={"budget_line_id": line.pk, "operation_id": line.operation_id},
        )
        messages.success(request, "Linha de orçamento aprovada.")
    elif action == "reject":
        line.status = BudgetLineStatus.REJECTED
        line.reviewed_by = request.user
        line.save(update_fields=["status", "reviewed_by"])
        log_audit(
            actor=request.user,
            action=AuditAction.EVENT_BUDGET_REJECTED,
            metadata={"budget_line_id": line.pk, "operation_id": line.operation_id},
        )
        messages.success(request, "Linha de orçamento recusada.")
    return redirect("private_area:event_operation_detail", pk=line.operation_id)


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_registrant_message(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(
        EventOperation.objects.select_related("public_event"),
        pk=pk,
    )
    form = EventRegistrantMessageForm(request.POST)
    if form.is_valid():
        emails = list(
            EventRegistration.objects.filter(
                event=operation.public_event,
                status=EventRegistration.Status.CONFIRMED,
            )
            .exclude(email="")
            .values_list("email", flat=True)
        )
        for email in emails:
            send_mail(
                form.cleaned_data["subject"],
                form.cleaned_data["body"],
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
        log_audit(
            actor=request.user,
            action=AuditAction.EVENT_REGISTRANTS_MESSAGED,
            metadata={
                "operation_id": operation.pk,
                "event_id": operation.public_event_id,
                "recipient_count": len(emails),
            },
        )
        messages.success(request, "Mensagem enviada aos inscritos confirmados.")
    else:
        messages.error(request, "Não foi possível enviar a mensagem.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_final_report(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(EventOperation, pk=pk)
    form = EventFinalReportForm(request.POST, instance=operation)
    if form.is_valid():
        form.save()
        log_audit(
            actor=request.user,
            action=AuditAction.EVENT_FINAL_REPORT_SAVED,
            metadata={"operation_id": operation.pk},
        )
        messages.success(request, "Relatório final salvo.")
    else:
        messages.error(request, "Não foi possível salvar o relatório.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
@require_http_methods(["POST"])
def event_document_upload(request: HttpRequest, pk: int) -> HttpResponse:
    operation = get_object_or_404(EventOperation, pk=pk)
    form = EventOperationDocumentForm(request.POST, request.FILES)
    if form.is_valid():
        document = form.save(commit=False)
        document.operation = operation
        document.created_by = request.user
        document.save()
        log_audit(
            actor=request.user,
            action=AuditAction.EVENT_OPERATION_DOCUMENT_UPLOADED,
            metadata={"document_id": document.pk, "operation_id": operation.pk},
        )
        messages.success(request, "Documento privado anexado à operação.")
    else:
        messages.error(request, "Não foi possível enviar o documento.")
    return redirect("private_area:event_operation_detail", pk=operation.pk)


@permission_required(Permission.MANAGE_EVENT_OPERATIONS)
def event_document_download(request: HttpRequest, pk: int) -> HttpResponse:
    document = get_object_or_404(EventOperationDocument, pk=pk)
    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=Path(document.file.name).name,
    )
