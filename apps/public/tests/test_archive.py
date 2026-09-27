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

from apps.public.archive import MOSAIC_PHOTOS, SEEDED_FRAMES, archive_frames, home_archive
from apps.public.instagram import (
    InstagramError,
    _short_caption,
    fetch_media,
    sync,
)
from apps.public.models import ArchiveFrame, ChurchSettings, InstagramCredential
from apps.public.templatetags.public_tags import hour_label

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
    def setUp(self):
        # Parte do vazio: a migração 0012 já cadastra fotos reais do Instagram.
        ArchiveFrame.objects.all().delete()

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

    def test_frame_date_uses_portuguese_month(self):
        make_frame(taken_at=timezone.make_aware(timezone.datetime(2025, 8, 15, 12)))
        self.assertEqual(archive_frames(1)[0]["date"], "ago 2025")

    def test_count_is_respected(self):
        self.assertEqual(len(archive_frames(4)), 4)

    def test_every_seeded_frame_has_a_scene_description(self):
        for slug, alt, caption in SEEDED_FRAMES:
            self.assertTrue(alt, f"{slug} sem descrição")
            self.assertTrue(caption, f"{slug} sem legenda")


def days_ago(days):
    return timezone.now() - timezone.timedelta(days=days)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class HomeArchiveTests(TestCase):
    """Encontro 2: fotografia abre e compõe o mosaico; arte vai inteira para o mural."""

    def setUp(self):
        ArchiveFrame.objects.all().delete()

    def test_a_poster_never_opens_the_page(self):
        make_frame(caption="Cartaz novo", kind=ArchiveFrame.Kind.ART, taken_at=days_ago(1))
        make_frame(caption="Foto antiga", taken_at=days_ago(30))
        archive = home_archive(12)
        self.assertEqual(archive["hero"]["caption"], "Foto antiga")
        self.assertEqual([frame["caption"] for frame in archive["posters"]], ["Cartaz novo"])
        self.assertEqual(archive["photos"], [])

    def test_featured_photo_opens_the_page_even_when_older(self):
        make_frame(caption="Recente", taken_at=days_ago(1))
        make_frame(caption="Escolhida", featured=True, taken_at=days_ago(400))
        archive = home_archive(2)
        self.assertEqual(archive["hero"]["caption"], "Escolhida")
        self.assertEqual([frame["caption"] for frame in archive["photos"]], ["Recente"])

    def test_featured_poster_does_not_open_the_page(self):
        make_frame(caption="Cartaz", kind=ArchiveFrame.Kind.ART, featured=True, taken_at=days_ago(1))
        make_frame(caption="Foto", taken_at=days_ago(5))
        self.assertEqual(home_archive(12)["hero"]["caption"], "Foto")

    def test_photos_get_their_turn_before_recent_posters(self):
        for index in range(6):
            make_frame(caption=f"Cartaz {index}", kind=ArchiveFrame.Kind.ART, taken_at=days_ago(index))
        make_frame(caption="Foto antiga", taken_at=days_ago(90))
        archive = home_archive(4)
        self.assertEqual(archive["hero"]["caption"], "Foto antiga")
        self.assertEqual(len(archive["posters"]), 3)

    def test_without_real_photos_the_illustrations_are_not_mixed_with_posters(self):
        make_frame(caption="Cartaz", kind=ArchiveFrame.Kind.ART)
        archive = home_archive(12)
        self.assertTrue(archive["is_seeded"])
        self.assertTrue(archive["hero"]["synthetic"])
        self.assertTrue(all(frame["synthetic"] for frame in archive["photos"]))
        self.assertEqual([frame["caption"] for frame in archive["posters"]], ["Cartaz"])

    def test_real_photos_are_never_topped_up_with_illustrations(self):
        make_frame(caption="Foto 1")
        make_frame(caption="Foto 2")
        archive = home_archive(12)
        self.assertFalse(archive["is_seeded"])
        self.assertFalse(any(frame["synthetic"] for frame in archive["photos"]))

    def test_invite_closes_a_short_mosaic(self):
        make_frame(caption="Foto 1")
        make_frame(caption="Foto 2")
        archive = home_archive(12)
        self.assertTrue(archive["invite"])
        self.assertEqual(archive["mosaic_size"], 2)

    def test_full_mosaic_has_no_invite(self):
        for index in range(1 + MOSAIC_PHOTOS + 2):
            make_frame(caption=f"Foto {index}")
        archive = home_archive(12)
        self.assertEqual(len(archive["photos"]), MOSAIC_PHOTOS)
        self.assertFalse(archive["invite"])

    def test_instagram_credit_is_not_repeated_under_each_frame(self):
        make_frame(caption="Foto", credit="Instagram @igrejabatista.santaleopoldina")
        make_frame(caption="Outra", credit="Foto: Maria Silva")
        frames = {frame["caption"]: frame for frame in archive_frames(2)}
        self.assertEqual(frames["Foto"]["byline"], "")
        self.assertEqual(frames["Outra"]["byline"], "Foto: Maria Silva")


class HourLabelTests(TestCase):
    def test_whole_hour(self):
        self.assertEqual(hour_label(timezone.datetime(2026, 9, 27, 19, 0)), "19h")

    def test_half_hour(self):
        self.assertEqual(hour_label(timezone.datetime(2026, 9, 27, 19, 30)), "19h30")

    def test_empty(self):
        self.assertEqual(hour_label(None), "")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ImportedInstagramFramesTests(TestCase):
    def test_migration_registers_the_most_liked_posts(self):
        """As fotos do perfil entram curadas, visíveis, com imagem e descrição."""
        frames = ArchiveFrame.objects.filter(permalink__startswith="https://www.instagram.com/p/")
        self.assertEqual(frames.count(), 9)
        for frame in frames:
            self.assertEqual(frame.source, ArchiveFrame.Source.CURATED)
            self.assertTrue(frame.is_visible)
            self.assertTrue(frame.image.name.startswith("archive/ig-"))
            self.assertTrue(frame.alt_text)
            self.assertLessEqual(len(frame.caption), 120)

        sheet = archive_frames(12)
        self.assertEqual(sum(not frame["synthetic"] for frame in sheet), 9)
        self.assertEqual(sheet[0]["caption"], "27 anos de Igreja Batista em Santa Leopoldina")

    def test_posters_are_marked_as_art_and_a_photo_opens_the_home(self):
        """Os cinco cartazes vão para o mural; a abertura é uma fotografia."""
        arts = ArchiveFrame.objects.filter(kind=ArchiveFrame.Kind.ART)
        self.assertEqual(arts.count(), 5)
        self.assertIn("27 anos de Igreja Batista em Santa Leopoldina", arts.values_list("caption", flat=True))

        archive = home_archive(12)
        self.assertEqual(archive["hero"]["caption"], "Consagração da pequena Anne")
        self.assertEqual(len(archive["posters"]), 5)
        self.assertFalse(archive["is_seeded"])


class HomeEditorialTests(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.settings = ChurchSettings.for_site(site)
        self.settings.next_service_when = "Domingo, 19h"
        self.settings.instagram_url = "https://www.instagram.com/igrejabatista.santaleopoldina/"
        self.settings.instagram_handle = "igrejabatista.santaleopoldina"
        self.settings.save()

    def test_home_keeps_visitor_actions_and_content_sections(self):
        response = self.client.get(reverse("home"))
        for title in ("Próximos encontros", "Palavra para a vida", "Notícias da igreja", "A vida em comunidade", "Mural da igreja"):
            self.assertContains(response, title)
        self.assertContains(response, reverse("plan_visit"))
        self.assertContains(response, reverse("prayer_request"))
        self.assertContains(response, "Domingo, 19h")
        self.assertContains(response, "@igrejabatista.santaleopoldina")

    def test_home_shows_the_configured_number_of_frames(self):
        self.settings.archive_frame_count = 6
        self.settings.save()
        body = self.client.get(reverse("home")).content.decode()
        shown = sum(body.count(f'class="{name}"') for name in ("welcome-photo", "community-photo", "poster"))
        self.assertEqual(shown, 6)

    def test_visit_band_links_to_the_map_when_configured(self):
        self.settings.map_url = "https://maps.example.com/igreja"
        self.settings.save()
        response = self.client.get(reverse("home"))
        self.assertContains(response, "https://maps.example.com/igreja")
        self.assertContains(response, "Abrir no mapa")

    def test_seeded_archive_is_disclosed_as_example_imagery(self):
        """Imagem gerada não passa por prova: a página diz que é exemplo."""
        ArchiveFrame.objects.filter(kind=ArchiveFrame.Kind.PHOTO).delete()
        response = self.client.get(reverse("home"))
        self.assertTrue(response.context["archive_is_seeded"])
        self.assertContains(response, "imagens de exemplo")

    def test_real_archive_drops_the_example_notice(self):
        for index in range(12):
            make_frame(caption=f"Quadro {index}")
        response = self.client.get(reverse("home"))
        self.assertFalse(response.context["archive_is_seeded"])
        self.assertNotContains(response, "imagens de exemplo")

    def test_real_frame_shows_credit_and_caption(self):
        make_frame(caption="Culto de domingo", credit="Foto: Maria Silva", featured=True)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Culto de domingo")
        self.assertContains(response, "Foto: Maria Silva")

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

    def test_fetch_follows_official_pagination(self):
        page1 = {
            "data": [{"id": "1", "media_type": "IMAGE", "media_url": "https://cdn/1.jpg"}],
            "paging": {"next": "https://graph.instagram.com/me/media?after=abc&access_token=tok"},
        }
        page2 = {
            "data": [{"id": "2", "media_type": "IMAGE", "media_url": "https://cdn/2.jpg"}],
        }
        with patch(
            "apps.public.instagram.urllib.request.urlopen",
            side_effect=[fake_response(page1), fake_response(page2)],
        ):
            frames = fetch_media(mode="instagram_login", token="tok", limit=10)

        self.assertEqual([frame.remote_id for frame in frames], ["1", "2"])


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
        self.assertEqual(frame.credit, "Instagram @igrejabatista.santaleopoldina")
        self.assertTrue(frame.image.name.endswith(".jpg"))
        self.assertEqual(InstagramCredential.current().last_sync_error, "")
