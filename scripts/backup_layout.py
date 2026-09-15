"""S3 key layout for encrypted IB Conecta backups (issue #33)."""

from __future__ import annotations

from datetime import datetime, timezone

DAILY_PREFIX = "daily/"
MONTHLY_PREFIX = "monthly/"
DAILY_RETENTION_DAYS = 30
MONTHLY_RETENTION_DAYS = 366


def artifact_filename(stamp: datetime) -> str:
    utc = stamp.astimezone(timezone.utc)
    return f"ib-conecta-{utc.strftime('%Y%m%dT%H%M%SZ')}.tar.age"


def daily_key(stamp: datetime, filename: str | None = None) -> str:
    utc = stamp.astimezone(timezone.utc)
    name = filename or artifact_filename(utc)
    return f"{DAILY_PREFIX}{utc.strftime('%Y-%m-%d')}/{name}"


def monthly_prefix(stamp: datetime) -> str:
    utc = stamp.astimezone(timezone.utc)
    return f"{MONTHLY_PREFIX}{utc.strftime('%Y-%m')}/"


def monthly_key(stamp: datetime, filename: str | None = None) -> str:
    utc = stamp.astimezone(timezone.utc)
    name = filename or artifact_filename(utc)
    return f"{monthly_prefix(utc)}{name}"
