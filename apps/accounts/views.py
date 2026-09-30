import pyotp
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db.models import Case, Count, IntegerField, Value, When
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods

from apps.accounts.audit import AuditAction, log_audit
from apps.accounts.decorators import permission_required
from apps.accounts.forms import (
    AccountDetailsForm,
    AccountPasswordChangeForm,
    LoginForm,
    OTPTokenForm,
)
from apps.accounts.models import Role
from apps.accounts.permissions import Permission, user_has_permission

User = get_user_model()

OTP_SESSION_KEY = "otp_user_id"


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("accounts:account_home")

    form = LoginForm(request=request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            if user.profile.totp_enabled:
                request.session[OTP_SESSION_KEY] = user.id
                log_audit(
                    actor=user,
                    action=AuditAction.LOGIN_PASSWORD_ACCEPTED_AWAITING_2FA,
                    metadata={"username": user.username},
                )
                return redirect("accounts:two_factor_verify")
            login(request, user)
            log_audit(
                actor=user,
                action=AuditAction.LOGIN_SUCCESS,
                metadata={"username": user.username},
            )
            return redirect("accounts:account_home")
        log_audit(
            actor=None,
            action=AuditAction.LOGIN_FAILED,
            metadata={"username": request.POST.get("username", "")},
        )
    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        log_audit(
            actor=request.user,
            action=AuditAction.LOGOUT,
            metadata={"username": request.user.username},
        )
    logout(request)
    return redirect("home")


@login_required
@require_http_methods(["GET", "POST"])
def account_home(request: HttpRequest) -> HttpResponse:
    user = request.user
    details_form = AccountDetailsForm(request.POST or None, instance=user)
    if request.method == "POST" and details_form.is_valid():
        details_form.save()
        log_audit(
            actor=user,
            action=AuditAction.ACCOUNT_DETAILS_UPDATED,
            metadata={"username": user.username, "fields": details_form.changed_data},
        )
        messages.success(request, "Seus dados foram atualizados.")
        return redirect("accounts:account_home")

    can_manage_event_registrations = user_has_permission(
        user, Permission.MANAGE_EVENT_OPERATIONS
    ) or user_has_permission(user, Permission.MANAGE_CONTENT)
    can_manage_prayer_requests = user_has_permission(user, Permission.MANAGE_PRAYER_REQUESTS)
    can_manage_content = user_has_permission(user, Permission.MANAGE_CONTENT)
    return render(
        request,
        "accounts/account_home.html",
        {
            "profile": user.profile,
            "details_form": details_form,
            "can_manage_2fa": user_has_permission(user, Permission.MANAGE_TWO_FACTOR),
            "can_manage_event_registrations": can_manage_event_registrations,
            "can_manage_prayer_requests": can_manage_prayer_requests,
            "can_manage_content": can_manage_content,
        },
    )


class AccountPasswordChangeView(PasswordChangeView):
    form_class = AccountPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:account_home")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_audit(
            actor=self.request.user,
            action=AuditAction.PASSWORD_CHANGED,
            metadata={"username": self.request.user.username},
        )
        messages.success(self.request, "Senha alterada.")
        return response


@require_http_methods(["GET", "POST"])
def two_factor_verify(request: HttpRequest) -> HttpResponse:
    user_id = request.session.get(OTP_SESSION_KEY)
    if not user_id:
        return redirect("accounts:login")

    user = get_object_or_404(User, pk=user_id)
    form = OTPTokenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if user.profile.verify_totp(form.cleaned_data["token"]):
            login(request, user, backend="apps.accounts.backends.EmailOrUsernameBackend")
            request.session.pop(OTP_SESSION_KEY, None)
            log_audit(
                actor=user,
                action=AuditAction.LOGIN_SUCCESS,
                metadata={"username": user.username, "two_factor": True},
            )
            return redirect("accounts:account_home")
        form.add_error("token", "Código inválido.")
        log_audit(
            actor=user,
            action=AuditAction.LOGIN_2FA_FAILED,
            metadata={"username": user.username},
        )
    return render(request, "accounts/two_factor_verify.html", {"form": form})


@login_required
@permission_required(Permission.MANAGE_TWO_FACTOR)
@require_http_methods(["GET", "POST"])
def two_factor_setup(request: HttpRequest) -> HttpResponse:
    profile = request.user.profile
    if not profile.totp_enabled:
        profile.ensure_totp_secret()

    form = OTPTokenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if profile.verify_totp(form.cleaned_data["token"]):
            profile.enable_totp()
            log_audit(
                actor=request.user,
                action=AuditAction.TWO_FACTOR_ENABLED,
                metadata={"username": request.user.username},
            )
            messages.success(request, "Autenticação em dois fatores ativada.")
            return redirect("accounts:account_home")
        form.add_error("token", "Código inválido. Confira o app autenticador.")

    provisioning_uri = pyotp.TOTP(profile.totp_secret).provisioning_uri(
        name=request.user.username,
        issuer_name="IB Conecta",
    )
    return render(
        request,
        "accounts/two_factor_setup.html",
        {
            "form": form,
            "secret": profile.totp_secret,
            "provisioning_uri": provisioning_uri,
            "enabled": profile.totp_enabled,
        },
    )


@permission_required(Permission.MANAGE_EVENT_OPERATIONS, Permission.MANAGE_CONTENT)
def event_registrations(request: HttpRequest) -> HttpResponse:
    from apps.public.models import EventRegistration

    registrations = EventRegistration.objects.select_related("event").order_by(
        "event__starts_at", "event_id", "name"
    )
    events = []
    for registration in registrations:
        if not events or events[-1]["event"].pk != registration.event_id:
            events.append({"event": registration.event, "registrations": []})
        events[-1]["registrations"].append(registration)

    selected_event = request.GET.get("evento", "")
    shown = [group for group in events if str(group["event"].pk) == selected_event] or events
    if len(shown) == len(events):
        selected_event = ""

    # Ativas primeiro; canceladas descem para o fim do grupo.
    status_order = {
        EventRegistration.Status.CONFIRMED: 0,
        EventRegistration.Status.WAITLISTED: 1,
        EventRegistration.Status.CANCELLED: 2,
    }
    for group in shown:
        items = group["registrations"]
        items.sort(key=lambda item: status_order.get(item.status, 1))
        group["confirmed_count"] = sum(item.status == "confirmed" for item in items)
        group["waitlisted_count"] = sum(item.status == "waitlisted" for item in items)
        group["cancelled_count"] = sum(item.status == "cancelled" for item in items)

    return render(
        request,
        "public/event_registrations.html",
        {
            "events": events,
            "groups": shown,
            "selected_event": selected_event,
        },
    )


@permission_required(Permission.MANAGE_EVENT_OPERATIONS, Permission.MANAGE_CONTENT)
@require_http_methods(["POST"])
def event_registration_cancel(request: HttpRequest, pk: int) -> HttpResponse:
    from apps.public.models import EventRegistration

    registration = get_object_or_404(EventRegistration, pk=pk)
    registration.status = EventRegistration.Status.CANCELLED
    registration.save(update_fields=["status"])
    messages.success(request, f"Inscrição de {registration.name} cancelada.")
    url = reverse("accounts:event_registrations")
    selected_event = request.POST.get("evento", "")
    if selected_event.isdigit():
        url = f"{url}?evento={selected_event}"
    return redirect(url)


@permission_required(Permission.MANAGE_PRAYER_REQUESTS)
def prayer_requests(request: HttpRequest) -> HttpResponse:
    from apps.public.models import PrayerRequest

    Status = PrayerRequest.Status
    selected = request.GET.get("situacao", "")
    if selected not in Status.values:
        selected = ""
    counts = {
        row["status"]: row["total"] for row in PrayerRequest.objects.values("status").annotate(total=Count("pk"))
    }
    # Novos primeiro, depois em acompanhamento e concluídos; mais recentes dentro de cada grupo.
    status_order = Case(
        *(When(status=value, then=Value(index)) for index, value in enumerate(Status.values)),
        default=Value(len(Status.values)),
        output_field=IntegerField(),
    )
    items = PrayerRequest.objects.annotate(status_order=status_order).order_by("status_order", "-created_at")
    if selected:
        items = items.filter(status=selected)
    filters = [("", "Todos", sum(counts.values()))] + [
        (value, label, counts.get(value, 0)) for value, label in Status.choices
    ]
    return render(
        request,
        "public/prayer_requests.html",
        {
            "requests": items,
            "statuses": Status.choices,
            "filters": filters,
            "selected_status": selected,
        },
    )


@permission_required(Permission.MANAGE_PRAYER_REQUESTS)
@require_http_methods(["POST"])
def prayer_request_status(request: HttpRequest, pk: int) -> HttpResponse:
    from apps.public.models import PrayerRequest

    item = get_object_or_404(PrayerRequest, pk=pk)
    new_status = request.POST.get("status", "")
    if new_status in PrayerRequest.Status.values:
        old_status = item.status
        item.status = new_status
        item.save(update_fields=["status"])
        log_audit(
            actor=request.user,
            action=AuditAction.PRAYER_REQUEST_STATUS_CHANGED,
            metadata={
                "request_id": item.pk,
                "old_status": old_status,
                "new_status": new_status,
            },
        )
        messages.success(request, "Situação do pedido atualizada.")
    url = reverse("accounts:prayer_requests")
    selected = request.POST.get("situacao", "")
    if selected in PrayerRequest.Status.values:
        url = f"{url}?situacao={selected}"
    return redirect(url)


@permission_required(Permission.MANAGE_PRAYER_REQUESTS)
def know_church_contacts(request: HttpRequest) -> HttpResponse:
    from apps.public.models import KnowChurchContact

    return render(
        request,
        "public/know_church_contacts.html",
        {
            "contacts": KnowChurchContact.objects.all(),
            "statuses": KnowChurchContact.Status.choices,
        },
    )


@permission_required(Permission.MANAGE_PRAYER_REQUESTS)
@require_http_methods(["POST"])
def know_church_contact_status(request: HttpRequest, pk: int) -> HttpResponse:
    from apps.public.models import KnowChurchContact

    item = get_object_or_404(KnowChurchContact, pk=pk)
    new_status = request.POST.get("status", "")
    if new_status in KnowChurchContact.Status.values:
        old_status = item.status
        item.status = new_status
        item.save(update_fields=["status"])
        log_audit(
            actor=request.user,
            action=AuditAction.KNOW_CHURCH_CONTACT_STATUS_CHANGED,
            metadata={
                "contact_id": item.pk,
                "old_status": old_status,
                "new_status": new_status,
            },
        )
        messages.success(request, "Situação do contato atualizada.")
    return redirect("accounts:know_church_contacts")


@permission_required(Permission.MANAGE_USERS)
@require_http_methods(["GET", "POST"])
def manage_users_demo(request: HttpRequest) -> HttpResponse:
    """Demo seam for role management until the full admin UX arrives."""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        new_role = request.POST.get("role")
        if user_id and new_role in Role.values:
            target = get_object_or_404(User, pk=user_id)
            old_role = target.profile.role
            target.profile.role = new_role
            target.profile.save(update_fields=["role"])
            log_audit(
                actor=request.user,
                action=AuditAction.ROLE_CHANGED,
                metadata={
                    "target_user_id": target.id,
                    "old_role": old_role,
                    "new_role": target.profile.role,
                },
            )
            messages.success(request, f"Perfil de {target.username} atualizado.")
            return redirect("accounts:manage_users_demo")

    users = User.objects.select_related("profile").order_by("username")
    return render(
        request,
        "accounts/manage_users_demo.html",
        {"users": users, "roles": Role.choices},
    )


class EmailPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset_form.html"
    email_template_name = "accounts/password_reset_email.txt"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_audit(
            actor=self.request.user if self.request.user.is_authenticated else None,
            action=AuditAction.PASSWORD_RESET_REQUESTED,
            metadata={"email": form.cleaned_data.get("email", "")},
        )
        return response


class EmailPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class EmailPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_audit(
            actor=self.user,
            action=AuditAction.PASSWORD_RESET_COMPLETED,
            metadata={"username": getattr(self.user, "username", "")},
        )
        return response


class EmailPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
