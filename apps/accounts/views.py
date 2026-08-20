import pyotp
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from apps.accounts.audit import AuditAction, log_audit
from apps.accounts.decorators import permission_required
from apps.accounts.forms import LoginForm, OTPTokenForm
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
def account_home(request: HttpRequest) -> HttpResponse:
    can_manage_event_registrations = user_has_permission(
        request.user, Permission.MANAGE_EVENT_OPERATIONS
    ) or user_has_permission(request.user, Permission.MANAGE_CONTENT)
    can_manage_prayer_requests = user_has_permission(
        request.user, Permission.MANAGE_PRAYER_REQUESTS
    )
    can_access_event_operations = user_has_permission(
        request.user, Permission.MANAGE_EVENT_OPERATIONS
    ) or user_has_permission(request.user, Permission.MANAGE_FINANCES)
    return render(
        request,
        "accounts/account_home.html",
        {
            "profile": request.user.profile,
            "can_manage_2fa": user_has_permission(request.user, Permission.MANAGE_TWO_FACTOR),
            "can_manage_event_registrations": can_manage_event_registrations,
            "can_manage_prayer_requests": can_manage_prayer_requests,
            "can_access_event_operations": can_access_event_operations,
        },
    )


@require_http_methods(["GET", "POST"])
def two_factor_verify(request: HttpRequest) -> HttpResponse:
    user_id = request.session.get(OTP_SESSION_KEY)
    if not user_id:
        return redirect("accounts:login")

    user = get_object_or_404(User, pk=user_id)
    form = OTPTokenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if user.profile.verify_totp(form.cleaned_data["token"]):
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
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

    registrations = EventRegistration.objects.select_related("event").all()
    return render(
        request,
        "public/event_registrations.html",
        {"registrations": registrations},
    )


@permission_required(Permission.MANAGE_EVENT_OPERATIONS, Permission.MANAGE_CONTENT)
@require_http_methods(["POST"])
def event_registration_cancel(request: HttpRequest, pk: int) -> HttpResponse:
    from apps.public.models import EventRegistration

    registration = get_object_or_404(EventRegistration, pk=pk)
    registration.status = EventRegistration.Status.CANCELLED
    registration.save(update_fields=["status"])
    messages.success(request, f"Inscrição de {registration.name} cancelada.")
    return redirect("accounts:event_registrations")


@permission_required(Permission.MANAGE_PRAYER_REQUESTS)
def prayer_requests(request: HttpRequest) -> HttpResponse:
    from apps.public.models import PrayerRequest

    return render(
        request,
        "public/prayer_requests.html",
        {
            "requests": PrayerRequest.objects.all(),
            "statuses": PrayerRequest.Status.choices,
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
    return redirect("accounts:prayer_requests")


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
