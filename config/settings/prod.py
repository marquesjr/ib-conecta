import os

from .base import *  # noqa: F401,F403
from .prod_helpers import (
    build_storages,
    csv_values,
    csrf_trusted_origins,
    object_storage_configured,
    production_secret_key,
    require_env,
    with_healthcheck_hosts,
)

DEBUG = False

SECRET_KEY = production_secret_key(os.environ.get("DJANGO_SECRET_KEY", ""))
_public_hosts = csv_values(require_env("DJANGO_ALLOWED_HOSTS"))
CSRF_TRUSTED_ORIGINS = csrf_trusted_origins(
    _public_hosts,
    csv_values(os.environ.get("CSRF_TRUSTED_ORIGINS", "")),
)
ALLOWED_HOSTS = with_healthcheck_hosts(_public_hosts)

MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))
PRIVATE_MEDIA_ROOT = Path(
    os.environ.get("PRIVATE_MEDIA_ROOT", BASE_DIR / "private_media")
)
STORAGES = build_storages(media_root=str(MEDIA_ROOT), env=dict(os.environ))

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
# Caddy terminates TLS and redirects HTTP → HTTPS.
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

_admin_url = os.environ.get("WAGTAILADMIN_BASE_URL", "").strip()
if _admin_url:
    WAGTAILADMIN_BASE_URL = _admin_url
elif CSRF_TRUSTED_ORIGINS:
    WAGTAILADMIN_BASE_URL = CSRF_TRUSTED_ORIGINS[0]

if object_storage_configured(dict(os.environ)) and "storages" not in INSTALLED_APPS:
    INSTALLED_APPS = [*INSTALLED_APPS, "storages"]

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)
