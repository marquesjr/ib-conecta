import os

from django.core.exceptions import ImproperlyConfigured

WEAK_SECRET_KEYS = {
    "unsafe-dev-only-secret-key",
    "change-me-in-local-dev",
    "change-me",
}

OBJECT_STORAGE_ENV = (
    "OCI_S3_ACCESS_KEY",
    "OCI_S3_SECRET_KEY",
    "OCI_S3_BUCKET",
    "OCI_S3_NAMESPACE",
)


def require_env(name: str, env: dict[str, str] | None = None) -> str:
    source = os.environ if env is None else env
    value = (source.get(name) or "").strip()
    if not value:
        raise ImproperlyConfigured(f"{name} is required when using production settings.")
    return value


def production_secret_key(value: str) -> str:
    secret = (value or "").strip()
    if secret in WEAK_SECRET_KEYS or len(secret) < 32:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY is missing or too weak for production."
        )
    return secret


def csv_values(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def with_healthcheck_hosts(allowed_hosts: list[str]) -> list[str]:
    hosts = list(allowed_hosts)
    for host in ("127.0.0.1", "localhost"):
        if host not in hosts:
            hosts.append(host)
    return hosts


def csrf_trusted_origins(allowed_hosts: list[str], configured: list[str]) -> list[str]:
    if configured:
        return configured
    origins = [
        f"https://{host}"
        for host in allowed_hosts
        if host not in {"localhost", "127.0.0.1", "web"}
    ]
    if any(host in {"localhost", "127.0.0.1"} for host in allowed_hosts):
        origins.extend(
            [
                "http://localhost",
                "https://localhost",
                "http://127.0.0.1",
                "https://127.0.0.1",
            ]
        )
    return origins


def object_storage_configured(env: dict[str, str]) -> bool:
    return all((env.get(name) or "").strip() for name in OBJECT_STORAGE_ENV)


def object_storage_endpoint(env: dict[str, str]) -> str:
    explicit = (env.get("OCI_S3_ENDPOINT") or "").strip()
    if explicit:
        return explicit
    namespace = (env.get("OCI_S3_NAMESPACE") or "").strip()
    region = (env.get("OCI_S3_REGION") or "sa-saopaulo-1").strip()
    return f"https://{namespace}.compat.objectstorage.{region}.oraclecloud.com"


def build_storages(*, media_root: str, env: dict[str, str]) -> dict:
    staticfiles = {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    }
    if object_storage_configured(env):
        region = (env.get("OCI_S3_REGION") or "sa-saopaulo-1").strip()
        default = {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "access_key": env["OCI_S3_ACCESS_KEY"].strip(),
                "secret_key": env["OCI_S3_SECRET_KEY"].strip(),
                "bucket_name": env["OCI_S3_BUCKET"].strip(),
                "endpoint_url": object_storage_endpoint(env),
                "region_name": region,
                "addressing_style": "path",
                "signature_version": "s3v4",
                "default_acl": None,
                "querystring_auth": True,
                "querystring_expire": 86400,
                "file_overwrite": False,
                "location": "media",
            },
        }
    else:
        default = {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": str(media_root)},
        }
    return {"default": default, "staticfiles": staticfiles}
