from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.urls import reverse

from config.settings.prod_helpers import (
    build_storages,
    csrf_trusted_origins,
    object_storage_configured,
    object_storage_endpoint,
    production_secret_key,
    with_healthcheck_hosts,
)


class HealthzTests(TestCase):
    def test_healthz_returns_ok_without_auth(self):
        response = self.client.get(reverse("healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class ProductionHelpersTests(TestCase):
    def test_healthcheck_hosts_include_loopback(self):
        hosts = with_healthcheck_hosts(["www.ibsantaleopoldina.com.br"])
        self.assertEqual(
            hosts,
            ["www.ibsantaleopoldina.com.br", "127.0.0.1", "localhost"],
        )

    def test_rejects_weak_or_short_secret_key(self):
        with self.assertRaises(ImproperlyConfigured):
            production_secret_key("change-me-in-local-dev")
        with self.assertRaises(ImproperlyConfigured):
            production_secret_key("short")
        self.assertEqual(production_secret_key("a" * 32), "a" * 32)

    def test_csrf_origins_default_to_https_hosts(self):
        origins = csrf_trusted_origins(
            ["www.ibsantaleopoldina.com.br", "localhost"],
            [],
        )
        self.assertIn("https://www.ibsantaleopoldina.com.br", origins)
        self.assertIn("https://localhost", origins)

    def test_filesystem_storage_when_object_storage_env_missing(self):
        storages = build_storages(media_root="/app/media", env={})
        self.assertEqual(
            storages["default"]["BACKEND"],
            "django.core.files.storage.FileSystemStorage",
        )
        self.assertEqual(
            storages["staticfiles"]["BACKEND"],
            "whitenoise.storage.CompressedStaticFilesStorage",
        )
        self.assertFalse(object_storage_configured({}))

    def test_s3_storage_when_oci_object_storage_is_configured(self):
        env = {
            "OCI_S3_ACCESS_KEY": "key",
            "OCI_S3_SECRET_KEY": "secret",
            "OCI_S3_BUCKET": "ib-conecta-prod-storage",
            "OCI_S3_NAMESPACE": "examplens",
            "OCI_S3_REGION": "sa-saopaulo-1",
        }
        self.assertTrue(object_storage_configured(env))
        self.assertEqual(
            object_storage_endpoint(env),
            "https://examplens.compat.objectstorage.sa-saopaulo-1.oraclecloud.com",
        )
        storages = build_storages(media_root="/app/media", env=env)
        options = storages["default"]["OPTIONS"]
        self.assertEqual(
            storages["default"]["BACKEND"],
            "storages.backends.s3boto3.S3Boto3Storage",
        )
        self.assertEqual(options["bucket_name"], "ib-conecta-prod-storage")
        self.assertEqual(options["addressing_style"], "path")
        self.assertTrue(options["querystring_auth"])
