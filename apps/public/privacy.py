"""Constantes da política de privacidade, alinhadas ao que o portal coleta."""

from django.utils.html import format_html

PRIVACY_SLUG = "privacidade"

# Precisa coincidir com EventPage.sensitive_retain_days (default do modelo).
DEFAULT_RETREAT_SENSITIVE_RETAIN_DAYS = 30
INBOX_RETENTION_MONTHS = 12
EVENT_REGISTRATION_RETENTION_DAYS = 90


def consent_label(prefix: str):
    return format_html(
        '{} Li a <a href="/privacidade/">política de privacidade</a> (LGPD).',
        prefix,
    )
