"""A folha de contato da home e o cliente da API oficial do Instagram."""

import io
import json
import tempfile
from unittest.mock import MagicMock, patch

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from wagtail.models import Site

from apps.public.archive import SEEDED_FRAMES, archive_frames
from apps.public.instagram import (
    InstagramError,
    _short_caption,
    fetch_media,
    sync,
)
from apps.public.models import ArchiveFrame, ChurchSettings, InstagramCredential

MEDIA_ROOT = tempfile.mkdtemp()


def png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), (20, 20, 20)).save(buffer, "PNG")
    return buffer.getvalue()


def make_frame(**kwargs):
    kwargs.setdefault("caption", "Quadro real")
    kwargs.setdefault("alt_text", "Descrição da cena")
    frame = ArchiveFrame(**kwargs)
    frame.image.save("real.png", ContentFile(png_bytes()), save=False)
    frame.save()
    return frame


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ArchiveFramesTests(TestCase):
    def test_seeded_frames_fill_the_sheet_when_there_is_no_archive(self):
        """A densidade da composição é um compromisso: a folha nunca fica vazia."""
        frames = archive_frames(12)
        self.assertEqual(len(frames), 12)
        self.assertTrue(all(frame["synthetic"] for frame in frames))
        self.assertTrue(all(frame["alt"] for frame in frames))

    def test_real_frames_come_first_and_seeded_ones_top_up(self):
        make_frame(caption="Culto desta semana")
        frames = archive_frames(12)

        self.assertEqual(len(frames), 12)
        self.assertEqual(frames[0]["caption"], "Culto desta semana")
        self.assertFalse(frames[0]["synthetic"])
        self.assertTrue(all(frame["synthetic"] for frame in frames[1:]))

    def test_hidden_frames_are_left_out(self):
        make_frame(caption="Escondido", is_visible=False)
        frames = archive_frames(12)
        self.assertNotIn("Escondido", [frame["caption"] for frame in frames])

    def test_alt_text_falls_back_to_the_caption(self):
        make_frame(caption="Café e comunhão", alt_text="")
        self.assertEqual(archive_frames(1)[0]["alt"], "Café e comunhão")

    def test_count_is_respected(self):
        self.assertEqual(len(archive_frames(4)), 4)

    def test_every_seeded_frame_has_a_scene_description(self):
        for slug, alt, caption in SEEDED_FRAMES:
            self.assertTrue(alt, f"{slug} sem descrição")
            self.assertTrue(caption, f"{slug} sem legenda")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class HomeContactSheetTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)
        self.settings.next_service_when = "Domingo, 19h"
        self.settings.instagram_url = "https://www.instagram.com/igrejabatista.santaleopoldina/"
        self.settings.instagram_handle = "igrejabatista.santaleopoldina"
        self.settings.save()

    def test_home_renders_the_contact_sheet_with_every_region(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'class="contact-sheet"')
        self.assertContains(response, "sheet-mount")
        self.assertContains(response, "sheet-action--primary")
        self.assertContains(response, "sheet-list--agenda")
        self.assertContains(response, "sheet-list--sermons")
        self.assertContains(response, "sheet-list--news")
        self.assertContains(response, "sheet-handle")
        self.assertContains(response, "@igrejabatista.santaleopoldina")

    def test_home_shows_the_configured_number_of_frames(self):
        self.settings.archive_frame_count = 6
        self.settings.save()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.content.decode().count('class="sheet-frame"'), 6)

    def test_seeded_archive_is_disclosed_as_example_imagery(self):
        """Imagem gerada não passa por prova: a página diz que é exemplo."""
        response = self.client.get(reverse("home"))
        self.assertTrue(response.context["archive_is_seeded"])
        self.assertContains(response, "imagens de exemplo")

    def test_real_archive_drops_the_example_notice(self):
        for index in range(12):
            make_frame(caption=f"Quadro {index}")
        response = self.client.get(reverse("home"))
        self.assertFalse(response.context["archive_is_seeded"])
        self.assertNotContains(response, "imagens de exemplo")

    def test_every_frame_carries_alternative_text(self):
        response = self.client.get(reverse("home"))
        body = response.content.decode()
        self.assertEqual(body.count("<img"), body.count("alt="))
        self.assertNotIn('alt=""', body)


class InstagramCaptionTests(TestCase):
    def test_caption_collapses_to_a_single_short_line(self):
        self.assertEqual(
            _short_caption("Culto de domingo\n\nVenha participar!"), "Culto de domingo"
        )

    def test_leading_hashtag_is_dropped(self):
        self.assertEqual(_short_caption("#gratidão pela noite"), "gratidão pela noite")

    def test_empty_caption_stays_empty(self):
        self.assertEqual(_short_caption(""), "")

    def test_long_caption_is_trimmed(self):
        self.assertLessEqual(len(_short_caption("a" * 400)), 119)


def fake_response(payload):
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    response.__enter__ = lambda self: self
    response.__exit__ = lambda *args: False
    return response


class FetchMediaTests(TestCase):
    def test_media_without_a_usable_url_is_skipped(self):
        """A Meta omite media_url em mídia com direito autoral marcado."""
        payload = {
            "data": [
                {"id": "1", "media_type": "IMAGE", "media_url": "https://cdn/1.jpg"},
                {"id": "2", "media_type": "IMAGE"},
            ]
        }
        with patch("apps.public.instagram.urllib.request.urlopen", return_value=fake_response(payload)):
            frames = fetch_media(mode="instagram_login", token="tok")

        self.assertEqual([frame.remote_id for frame in frames], ["1"])

    def test_video_uses_its_thumbnail(self):
        payload = {
            "data": [
                {
                    "id": "9",
                    "media_type": "VIDEO",
                    "media_url": "https://cdn/movie.mp4",
                    "thumbnail_url": "https://cdn/thumb.jpg",
                }
            ]
        }
        with patch("apps.public.instagram.urllib.request.urlopen", return_value=fake_response(payload)):
            frames = fetch_media(mode="instagram_login", token="tok")

        self.assertEqual(frames[0].image_url, "https://cdn/thumb.jpg")

    def test_missing_token_is_rejected_before_any_request(self):
        with self.assertRaises(InstagramError):
            fetch_media(mode="instagram_login", token="")

    def test_facebook_login_requires_the_account_id(self):
        with self.assertRaises(InstagramError):
            fetch_media(mode="facebook_login", token="tok")

    def test_unknown_mode_is_rejected(self):
        with self.assertRaises(InstagramError):
            fetch_media(mode="carrier-pigeon", token="tok")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SyncTests(TestCase):
    """A sincronização nunca levanta: a home precisa sobreviver à Meta fora do ar."""

    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)

    def test_sync_reports_when_the_archive_is_switched_off(self):
        self.settings.instagram_mode = ChurchSettings.InstagramMode.OFF
        self.settings.save()

        summary = sync()

        self.assertIn("desligado", summary["error"])
        self.assertEqual(summary["created"], 0)

    def test_sync_reports_a_missing_credential_instead_of_failing(self):
        self.settings.instagram_mode = ChurchSettings.InstagramMode.INSTAGRAM_LOGIN
        self.settings.save()

        summary = sync()

        self.assertIn("credencial", summary["error"].lower())

    def test_api_failure_is_recorded_on_the_credential_and_not_raised(self):
        self.settings.instagram_mode = ChurchSettings.InstagramMode.INSTAGRAM_LOGIN
        self.settings.save()
        InstagramCredential.objects.create(access_token="tok", expires_at=timezone.now())

        with patch(
            "apps.public.instagram.fetch_media",
            side_effect=InstagramError("HTTP 400 da API"),
        ):
            summary = sync()

        self.assertIn("HTTP 400", summary["error"])
        self.assertIn("HTTP 400", InstagramCredential.current().last_sync_error)

    def test_a_successful_sync_stores_the_image_locally(self):
        """As URLs do CDN da Meta expiram, então a imagem tem de virar arquivo nosso."""
        self.settings.instagram_mode = ChurchSettings.InstagramMode.INSTAGRAM_LOGIN
        self.settings.save()
        InstagramCredential.objects.create(access_token="tok")

        payload = {
            "data": [
                {
                    "id": "abc123",
                    "media_type": "IMAGE",
                    "media_url": "https://cdn.example/photo.jpg",
                    "permalink": "https://www.instagram.com/p/abc123/",
                    "caption": "Culto de domingo",
                    "timestamp": "2026-08-16T22:00:00+0000",
                }
            ]
        }

        with (
            patch(
                "apps.public.instagram.urllib.request.urlopen",
                return_value=fake_response(payload),
            ),
            patch(
                "apps.public.instagram._download",
                return_value=(png_bytes(), ".jpg"),
            ),
        ):
            summary = sync()

        self.assertEqual(summary["created"], 1)
        frame = ArchiveFrame.objects.get(remote_id="abc123")
        self.assertEqual(frame.source, ArchiveFrame.Source.INSTAGRAM)
        self.assertEqual(frame.caption, "Culto de domingo")
        self.assertTrue(frame.image.name.endswith(".jpg"))
        self.assertEqual(InstagramCredential.current().last_sync_error, "")
