"""#68: artes do Mural inteiras e ponto de foco nas fotos da comunidade."""

import importlib
import io
import re
import tempfile
from pathlib import Path

from django.apps import apps as django_apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.public.archive import home_archive
from apps.public.models import ArchiveFrame

MEDIA_ROOT = tempfile.mkdtemp()
DATA_DIR = Path(settings.BASE_DIR) / "apps" / "public" / "data" / "instagram_2026_09"
migration = importlib.import_module("apps.public.migrations.0017_archiveframe_focal_point_full_frames")


def jpeg_bytes(size=(4, 4)):
    buffer = io.BytesIO()
    Image.new("RGB", size, (20, 20, 20)).save(buffer, "JPEG")
    return buffer.getvalue()


def make_frame(name="real.jpg", **kwargs):
    kwargs.setdefault("caption", "Quadro real")
    kwargs.setdefault("alt_text", "Descrição da cena")
    frame = ArchiveFrame(**kwargs)
    frame.image.save(name, ContentFile(jpeg_bytes()), save=False)
    frame.save()
    return frame


class BundledFramesTests(TestCase):
    def test_bundled_instagram_frames_keep_the_original_proportion(self):
        """As artes chegam inteiras: nada de quadrado recortado da grade do perfil."""
        sizes = {path.name: Image.open(path).size for path in DATA_DIR.glob("*.jpg")}
        self.assertEqual(len(sizes), 9)
        width, height = sizes["20260417_DXPItN0gEiA_01.jpg"]  # 139 anos, paisagem
        self.assertGreater(width, height)
        width, height = sizes["20260323_DWOqTXrgGYP_01.jpg"]  # Encontro de casais, retrato
        self.assertGreater(height, width)
        self.assertTrue(all(width >= 640 for width, _ in sizes.values()))

    def test_fathers_day_photo_keeps_its_text_in_the_mosaic(self):
        frame = ArchiveFrame.objects.get(permalink="https://www.instagram.com/p/DNMF0BZSELs/")
        self.assertEqual(frame.focal_point, ArchiveFrame.FocalPoint.TOP)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class FullFrameMigrationTests(TestCase):
    link = "https://www.instagram.com/p/DXPItN0gEiA/"

    def setUp(self):
        ArchiveFrame.objects.all().delete()

    def test_seeded_square_is_replaced_by_the_full_frame(self):
        frame = make_frame("ig-DXPItN0gEiA.jpg", source="curated", permalink=self.link, kind="art")
        old_name = frame.image.name

        migration.use_full_frames(django_apps, None)

        frame.refresh_from_db()
        self.assertNotEqual(frame.image.name, old_name)
        self.assertFalse(frame.image.storage.exists(old_name))
        with frame.image.open("rb") as handle:
            self.assertEqual(handle.read(), (DATA_DIR / "20260417_DXPItN0gEiA_01.jpg").read_bytes())

    def test_image_changed_in_the_cms_is_kept(self):
        frame = make_frame("nova-arte.jpg", source="curated", permalink=self.link, kind="art")
        name = frame.image.name

        migration.use_full_frames(django_apps, None)

        frame.refresh_from_db()
        self.assertEqual(frame.image.name, name)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class FocalPointTests(TestCase):
    def setUp(self):
        ArchiveFrame.objects.all().delete()

    def test_focal_point_becomes_object_position(self):
        make_frame(caption="Foto com foco", focal_point="bottom-left")
        make_frame(caption="Foto centrada")
        archive = home_archive(12)
        focus = {frame["caption"]: frame["focus"] for frame in [archive["hero"], *archive["photos"]]}
        self.assertEqual(focus["Foto com foco"], "0% 100%")
        self.assertEqual(focus["Foto centrada"], "")

    def test_mosaic_photo_uses_the_focal_point(self):
        make_frame(caption="Abertura", featured=True)
        make_frame(caption="Mosaico", focal_point="top")
        body = self.client.get(reverse("home")).content.decode()
        mosaic = body[body.index('class="mosaic"'):]
        self.assertIn('style="object-position: 50% 0%"', mosaic)
        self.assertEqual(mosaic.count("object-position"), 1)


class PosterProportionTests(TestCase):
    def test_posters_are_shown_whole_in_instagram_portrait(self):
        css = (Path(settings.BASE_DIR) / "static" / "css" / "ib-conecta.css").read_text()
        rule = re.search(r"\.poster img \{([^}]*)\}", css).group(1)
        self.assertIn("aspect-ratio: 4 / 5", rule)
        self.assertIn("object-fit: contain", rule)

    def test_poster_markup_reserves_a_portrait_box(self):
        body = self.client.get(reverse("home")).content.decode()
        poster = body[body.index('class="poster"'):]
        self.assertRegex(poster[:400], r'width="640" height="800"')
