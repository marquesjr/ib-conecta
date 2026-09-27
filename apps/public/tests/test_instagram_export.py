"""Importação da exportação oficial de dados do Instagram, sem raspagem."""

import io
import json
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from PIL import Image
from wagtail.models import Site

from apps.public.instagram import archive_credit, normalize_handle
from apps.public.instagram_export import (
    export_remote_id,
    fix_instagram_text,
    import_export,
    parse_export,
)
from apps.public.models import ArchiveFrame, ChurchSettings

MEDIA_ROOT = tempfile.mkdtemp()


def png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), (80, 40, 40)).save(buffer, "PNG")
    return buffer.getvalue()


def write_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_bytes())


class HandleAndCreditTests(TestCase):
    def test_handle_comes_from_url_or_arroba(self):
        self.assertEqual(
            normalize_handle("https://www.instagram.com/igrejabatista.santaleopoldina/"),
            "igrejabatista.santaleopoldina",
        )
        self.assertEqual(normalize_handle("@igrejabatista.santaleopoldina"), "igrejabatista.santaleopoldina")

    def test_credit_names_the_church_account(self):
        self.assertEqual(
            archive_credit("igrejabatista.santaleopoldina"),
            "Instagram @igrejabatista.santaleopoldina",
        )


class InstagramTextTests(TestCase):
    def test_mojibake_from_meta_export_is_repaired(self):
        broken = "Culto de aÃ§Ã£o de graÃ§as"
        self.assertEqual(fix_instagram_text(broken), "Culto de ação de graças")


class ParseExportTests(TestCase):
    def test_reads_posts_json_and_skips_videos(self):
        root = Path(tempfile.mkdtemp())
        photo = root / "your_instagram_activity" / "media" / "posts" / "202401" / "culto.jpg"
        write_png(photo)
        manifest = root / "your_instagram_activity" / "media" / "posts_1.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(
                [
                    {
                        "title": "Culto de domingo",
                        "creation_timestamp": 1704067200,
                        "media": [
                            {
                                "uri": "your_instagram_activity/media/posts/202401/culto.jpg",
                                "creation_timestamp": 1704067200,
                                "title": "Culto de domingo",
                            },
                            {
                                "uri": "your_instagram_activity/media/posts/202401/clipe.mp4",
                                "creation_timestamp": 1704067200,
                                "title": "Vídeo",
                            },
                        ],
                    }
                ]
            ),
            encoding="utf-8",
        )

        items = parse_export(root)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].caption, "Culto de domingo")
        self.assertEqual(items[0].taken_at, datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc))
        self.assertTrue(items[0].path.is_file())

    def test_reads_legacy_media_json_photos_key(self):
        root = Path(tempfile.mkdtemp())
        photo = root / "photos" / "cafe.png"
        write_png(photo)
        (root / "media.json").write_text(
            json.dumps(
                {
                    "photos": [
                        {
                            "caption": "Café e comunhão",
                            "taken_at": "2025-03-02T19:00:00+00:00",
                            "path": "photos/cafe.png",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        items = parse_export(root)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].caption, "Café e comunhão")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ImportExportTests(TestCase):
    def _export_dir(self) -> Path:
        root = Path(tempfile.mkdtemp())
        photo = root / "media" / "posts" / "foto.png"
        write_png(photo)
        (root / "posts_1.json").write_text(
            json.dumps(
                [
                    {
                        "media": [
                            {
                                "uri": "media/posts/foto.png",
                                "creation_timestamp": 1722470400,
                                "title": "Encontro da igreja",
                            }
                        ]
                    }
                ]
            ),
            encoding="utf-8",
        )
        return root

    def test_import_creates_archive_frame_with_credit_and_date(self):
        root = self._export_dir()
        summary = import_export(root, handle="igrejabatista.santaleopoldina")

        self.assertEqual(summary["created"], 1)
        frame = ArchiveFrame.objects.get()
        self.assertEqual(frame.source, ArchiveFrame.Source.INSTAGRAM)
        self.assertEqual(frame.caption, "Encontro da igreja")
        self.assertEqual(frame.credit, "Instagram @igrejabatista.santaleopoldina")
        self.assertEqual(frame.taken_at.year, 2024)
        self.assertTrue(frame.image.name.endswith(".png"))

    def test_import_is_idempotent(self):
        root = self._export_dir()
        import_export(root, handle="igrejabatista.santaleopoldina")
        summary = import_export(root, handle="igrejabatista.santaleopoldina")
        self.assertEqual(summary["created"], 0)
        self.assertEqual(summary["skipped"], 1)
        self.assertEqual(ArchiveFrame.objects.count(), 1)

    def test_import_from_official_zip(self):
        root = self._export_dir()
        zip_path = Path(tempfile.mkdtemp()) / "instagram.zip"
        with zipfile.ZipFile(zip_path, "w") as archive:
            for file in root.rglob("*"):
                if file.is_file():
                    archive.write(file, file.relative_to(root).as_posix())

        summary = import_export(zip_path, handle="igrejabatista.santaleopoldina")
        self.assertEqual(summary["created"], 1)
        self.assertEqual(ArchiveFrame.objects.count(), 1)

    def test_dry_run_does_not_write(self):
        root = self._export_dir()
        summary = import_export(root, dry_run=True)
        self.assertEqual(summary["found"], 1)
        self.assertEqual(ArchiveFrame.objects.count(), 0)

    def test_management_command_imports(self):
        site = Site.objects.get(is_default_site=True)
        settings = ChurchSettings.for_site(site)
        settings.instagram_handle = "igrejabatista.santaleopoldina"
        settings.save()

        root = self._export_dir()
        call_command("import_instagram_export", str(root))
        self.assertEqual(ArchiveFrame.objects.count(), 1)

    def test_management_command_rejects_missing_path(self):
        with self.assertRaises(CommandError):
            call_command("import_instagram_export", "/tmp/does-not-exist-ig-export")


class ExportIdStabilityTests(TestCase):
    def test_same_uri_keeps_the_same_remote_id(self):
        uri = "your_instagram_activity/media/posts/202401/culto.jpg"
        self.assertEqual(export_remote_id(uri), export_remote_id(uri))
        self.assertTrue(export_remote_id(uri).startswith("export:"))
