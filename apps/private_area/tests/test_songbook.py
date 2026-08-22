from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import AuditLog, Role
from apps.private_area.models import Song, SongStatus

User = get_user_model()


def authorized_song_payload(**overrides):
    payload = {
        "title": "Grande é o Senhor",
        "key": "G",
        "tempo": "80 BPM",
        "lyrics": "Grande é o Senhor\ne mui digno de louvor",
        "chords": "G          D\nGrande é o Senhor",
        "tags": "adoração, clássico",
        "authors": "Desconhecido",
        "source": "Hinário Batista",
        "license": "Uso congregacional autorizado",
        "permitted_uses": "Culto, ensaio e impressão interna",
        "authorized": "on",
        "references-TOTAL_FORMS": "1",
        "references-INITIAL_FORMS": "0",
        "references-MIN_NUM_FORMS": "0",
        "references-MAX_NUM_FORMS": "10",
        "references-0-label": "YouTube",
        "references-0-target_url": "https://www.youtube.com/watch?v=abc123",
        "versions-TOTAL_FORMS": "1",
        "versions-INITIAL_FORMS": "0",
        "versions-MIN_NUM_FORMS": "0",
        "versions-MAX_NUM_FORMS": "10",
        "versions-0-name": "Congregacional",
        "versions-0-key": "G",
        "versions-0-lyrics": "",
        "versions-0-chords": "",
        "score": SimpleUploadedFile(
            "grande.pdf",
            b"%PDF-1.4 partitura",
            content_type="application/pdf",
        ),
    }
    payload.update(overrides)
    return payload


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


class SongbookAccessTests(TestCase):
    def test_visitor_is_redirected_from_the_private_songbook(self):
        listing = self.client.get(reverse("private_area:songbook"))
        self.assertEqual(listing.status_code, 302)
        self.assertIn(reverse("accounts:login"), listing.url)
        create = self.client.get(reverse("private_area:song_create"))
        self.assertEqual(create.status_code, 302)
        self.assertIn(reverse("accounts:login"), create.url)

    def test_member_cannot_create_a_song(self):
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        page = self.client.get(reverse("private_area:song_create"))
        self.assertEqual(page.status_code, 403)
        denied = self.client.post(
            reverse("private_area:song_create"),
            {"title": "Grande é o Senhor"},
        )
        self.assertEqual(denied.status_code, 403)


class SongbookCatalogTests(TestCase):
    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.member = make_user("membro", Role.MEMBER)
        self.client.login(username="lider", password="senha-segura-123")

    def test_leader_creates_a_draft_song_with_authorized_material(self):
        page = self.client.get(reverse("private_area:song_create"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "autoriz")
        response = self.client.post(
            reverse("private_area:song_create"),
            authorized_song_payload(),
        )
        self.assertEqual(response.status_code, 302)
        song = Song.objects.get()
        self.assertEqual(song.title, "Grande é o Senhor")
        self.assertEqual(song.status, SongStatus.DRAFT)
        self.assertEqual(song.key, "G")
        self.assertEqual(song.tempo, "80 BPM")
        self.assertIn("mui digno de louvor", song.lyrics)
        self.assertIn("Grande é o Senhor", song.chords)
        self.assertIn("adoração", song.tags)
        self.assertEqual(song.authors, "Desconhecido")
        self.assertEqual(song.source, "Hinário Batista")
        self.assertEqual(song.license, "Uso congregacional autorizado")
        self.assertEqual(song.permitted_uses, "Culto, ensaio e impressão interna")
        self.assertTrue(song.authorized)
        self.assertTrue(song.score.name.endswith(".pdf"))
        reference = song.references.get()
        self.assertEqual(reference.label, "YouTube")
        self.assertEqual(reference.target_url, "https://www.youtube.com/watch?v=abc123")
        self.assertTrue(reference.token)
        version = song.versions.get()
        self.assertEqual(version.name, "Congregacional")
        listing = self.client.get(reverse("private_area:songbook"))
        self.assertContains(listing, "Grande é o Senhor")
        self.assertContains(listing, "Rascunho")
        entry = AuditLog.objects.filter(action="song_created").latest("created_at")
        self.assertEqual(entry.metadata.get("song_id"), song.pk)

    def test_song_is_not_stored_without_authorization(self):
        payload = authorized_song_payload(authorized="")
        response = self.client.post(reverse("private_area:song_create"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sem autorização")
        self.assertEqual(Song.objects.count(), 0)

    def test_leader_publishes_a_song_and_members_see_only_published(self):
        self.client.post(reverse("private_area:song_create"), authorized_song_payload())
        song = Song.objects.get()
        self.client.logout()
        self.client.login(username="membro", password="senha-segura-123")
        listing = self.client.get(reverse("private_area:songbook"))
        self.assertEqual(listing.status_code, 200)
        self.assertNotContains(listing, "Grande é o Senhor")
        detail = self.client.get(reverse("private_area:song_detail", args=[song.slug]))
        self.assertEqual(detail.status_code, 404)

        self.client.logout()
        self.client.login(username="lider", password="senha-segura-123")
        published = self.client.post(
            reverse("private_area:song_publish", args=[song.slug])
        )
        self.assertEqual(published.status_code, 302)
        song.refresh_from_db()
        self.assertEqual(song.status, SongStatus.PUBLISHED)
        entry = AuditLog.objects.filter(action="song_published").latest("created_at")
        self.assertEqual(entry.metadata.get("song_id"), song.pk)

        self.client.logout()
        self.client.login(username="membro", password="senha-segura-123")
        listing = self.client.get(reverse("private_area:songbook"))
        self.assertContains(listing, "Grande é o Senhor")
        detail = self.client.get(reverse("private_area:song_detail", args=[song.slug]))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Grande é o Senhor")
        self.assertContains(detail, "mui digno de louvor")
        self.assertContains(detail, "Hinário Batista")
        self.assertContains(detail, "Uso congregacional autorizado")

    def test_unpublished_reference_does_not_redirect(self):
        self.client.post(reverse("private_area:song_create"), authorized_song_payload())
        song = Song.objects.get()
        token = song.references.get().token
        self.client.logout()
        response = self.client.get(reverse("private_area:song_reference", args=[token]))
        self.assertEqual(response.status_code, 404)


class SongbookReferenceTests(TestCase):
    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.client.login(username="lider", password="senha-segura-123")
        self.client.post(reverse("private_area:song_create"), authorized_song_payload())
        self.song = Song.objects.get()
        self.client.post(reverse("private_area:song_publish", args=[self.song.slug]))
        self.reference = self.song.references.get()

    def test_leader_reviews_song_and_keeps_stable_reference_url(self):
        page = self.client.get(reverse("private_area:song_edit", args=[self.song.slug]))
        self.assertEqual(page.status_code, 200)
        payload = authorized_song_payload(lyrics="Letra revisada da congregação")
        payload.update(
            {
                "references-TOTAL_FORMS": "1",
                "references-INITIAL_FORMS": "1",
                "references-0-id": str(self.reference.pk),
                "references-0-label": "YouTube",
                "references-0-target_url": "https://www.youtube.com/watch?v=xyz789",
                "versions-TOTAL_FORMS": "1",
                "versions-INITIAL_FORMS": "1",
                "versions-0-id": str(self.song.versions.get().pk),
                "versions-0-name": "Congregacional",
                "versions-0-key": "A",
            }
        )
        payload.pop("score", None)
        response = self.client.post(
            reverse("private_area:song_edit", args=[self.song.slug]),
            payload,
        )
        self.assertEqual(response.status_code, 302)
        self.song.refresh_from_db()
        self.reference.refresh_from_db()
        self.assertEqual(self.song.lyrics, "Letra revisada da congregação")
        self.assertEqual(self.reference.target_url, "https://www.youtube.com/watch?v=xyz789")
        self.assertEqual(self.reference.token, Song.objects.get().references.get().token)

        internal = reverse("private_area:song_reference", args=[self.reference.token])
        self.client.logout()
        redirected = self.client.get(internal)
        self.assertEqual(redirected.status_code, 302)
        self.assertEqual(redirected.url, "https://www.youtube.com/watch?v=xyz789")


class SongbookPrintTests(TestCase):
    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.member = make_user("membro", Role.MEMBER)
        self.client.login(username="lider", password="senha-segura-123")
        self.client.post(reverse("private_area:song_create"), authorized_song_payload())
        self.song = Song.objects.get()
        self.client.post(
            reverse("private_area:song_create"),
            authorized_song_payload(
                title="Noite de paz",
                tags="natal",
                lyrics="Noite de paz, noite de amor",
                chords="C     G\nNoite de paz",
                score=SimpleUploadedFile(
                    "noite.pdf", b"%PDF-1.4 natal", content_type="application/pdf"
                ),
            ),
        )
        self.christmas = Song.objects.get(title="Noite de paz")
        self.client.post(reverse("private_area:song_publish", args=[self.song.slug]))
        self.client.post(reverse("private_area:song_publish", args=[self.christmas.slug]))
        self.client.logout()
        self.client.login(username="membro", password="senha-segura-123")

    def test_print_covers_individual_filtered_lyrics_chords_and_index(self):
        individual = self.client.get(
            reverse("private_area:song_print", args=[self.song.slug])
        )
        self.assertEqual(individual.status_code, 200)
        self.assertContains(individual, "Grande é o Senhor")
        self.assertContains(individual, "mui digno de louvor")
        self.assertContains(individual, "G          D")
        self.assertContains(individual, "@page")
        self.assertContains(individual, "A4")
        token = self.song.references.get().token
        self.assertContains(individual, f"/r/{token}/")
        self.assertContains(individual, "<svg")
        self.assertContains(individual, "Congregacional")
        self.assertContains(individual, "Uso congregacional autorizado")

        lyrics_only = self.client.get(
            reverse("private_area:songbook_print") + "?layout=lyrics&tag=natal"
        )
        self.assertEqual(lyrics_only.status_code, 200)
        self.assertContains(lyrics_only, "Noite de paz, noite de amor")
        self.assertNotContains(lyrics_only, "Grande é o Senhor")
        self.assertNotContains(lyrics_only, "C     G")

        with_chords = self.client.get(
            reverse("private_area:songbook_print") + "?layout=chords&tag=natal"
        )
        self.assertContains(with_chords, "Noite de paz, noite de amor")
        self.assertContains(with_chords, "C     G")

        index = self.client.get(reverse("private_area:songbook_print") + "?layout=index")
        self.assertContains(index, "Grande é o Senhor")
        self.assertContains(index, "Noite de paz")
        self.assertNotContains(index, "mui digno de louvor")
        self.assertNotContains(index, "Noite de paz, noite de amor")

    def test_member_downloads_the_private_score_pdf(self):
        download = self.client.get(
            reverse("private_area:song_score", args=[self.song.slug])
        )
        self.assertEqual(download.status_code, 200)
        self.assertEqual(b"".join(download.streaming_content), b"%PDF-1.4 partitura")
        self.assertFalse(
            Path(self.song.score.path).is_relative_to(Path(settings.MEDIA_ROOT))
        )
