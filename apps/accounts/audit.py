from typing import Any

from apps.accounts.models import AuditLog


class AuditAction:
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGIN_PASSWORD_ACCEPTED_AWAITING_2FA = "login_password_accepted_awaiting_2fa"
    LOGIN_2FA_FAILED = "login_2fa_failed"
    LOGOUT = "logout"
    TWO_FACTOR_ENABLED = "two_factor_enabled"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"
    ROLE_CHANGED = "role_changed"
    PRAYER_REQUEST_STATUS_CHANGED = "prayer_request_status_changed"
    KNOW_CHURCH_CONTACT_STATUS_CHANGED = "know_church_contact_status_changed"
    DOCUMENT_UPLOADED = "document_uploaded"
    MINISTRY_CREATED = "ministry_created"
    SCHEDULE_CREATED = "schedule_created"
    ASSIGNMENT_CONFIRMED = "assignment_confirmed"
    ASSIGNMENT_DECLINED = "assignment_declined"
    ASSIGNMENT_SUBSTITUTED = "assignment_substituted"
    EVENT_OPERATION_CREATED = "event_operation_created"
    EVENT_BUDGET_APPROVED = "event_budget_approved"
    EVENT_BUDGET_REJECTED = "event_budget_rejected"
    EVENT_REGISTRANTS_MESSAGED = "event_registrants_messaged"
    EVENT_FINAL_REPORT_SAVED = "event_final_report_saved"
    EVENT_OPERATION_DOCUMENT_UPLOADED = "event_operation_document_uploaded"


REDACT_KEYS = {
    "password",
    "password1",
    "password2",
    "new_password1",
    "new_password2",
    "token",
    "otp",
    "secret",
    "totp_secret",
    "prayer_text",
    "prayer_body",
    "pastoral_notes",
    "authorization",
}


def _redact(value: Any, key: str | None = None) -> Any:
    if key is not None and key.lower() in REDACT_KEYS:
        return "[redacted]"
    if isinstance(value, dict):
        return {k: _redact(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def log_audit(*, actor=None, action: str, metadata: dict | None = None) -> AuditLog:
    return AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        metadata=_redact(metadata or {}),
    )
