from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import AuditLog, Role
from apps.private_area.models import Ministry, PlaylistItem, Song, WeeklyPlaylist
from apps.private_area.tests.test_songbook import authorized_song_payload
from apps.private_area.tests.test_worship_playlists import make_user, playlist_pk

TITLES = ("Grande é o Senhor", "Noite de paz", "Castelo forte")


class PlaylistReorderTests(TestCase):
    def setUp(self):
        make_user("lider", Role.MINISTRY_LEADER)
        make_user("membro", Role.MEMBER)
        self.client.login(username="lider", password="senha-segura-123")
        self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": ""},
        )
        ministry = Ministry.objects.get()
        for title in TITLES:
            self.client.post(
                reverse("private_area:song_create"),
                authorized_song_payload(title=title),
            )
            song = Song.objects.get(title=title)
            self.client.post(reverse("private_area:song_publish", args=[song.slug]))
        created = self.client.post(
            reverse("private_area:playlist_create", args=[ministry.pk]),
            {"kind": "service", "starts_at": "2026-09-06T19:00", "notes": ""},
        )
        self.pk = playlist_pk(created)
        self.detail_url = reverse("private_area:playlist_detail", args=[self.pk])
        for title in TITLES:
            self.client.post(
                reverse("private_area:playlist_item_add", args=[self.pk]),
                {"song": Song.objects.get(title=title).pk, "version": "", "key": "", "notes": ""},
            )
        self.playlist = WeeklyPlaylist.objects.get(pk=self.pk)

    def order(self):
        return list(self.playlist.items.values_list("song__title", flat=True))

    def item(self, title):
        return PlaylistItem.objects.get(playlist=self.playlist, song__title=title)

    def test_songs_are_appended_without_an_order_field(self):
        self.assertEqual(self.order(), list(TITLES))
        self.assertEqual(
            list(self.playlist.items.values_list("position", flat=True)), [1, 2, 3]
        )
        page = self.client.get(self.detail_url)
        self.assertNotContains(page, 'name="position"')
        self.assertContains(page, '<details class="panel playlist-add">')
        self.assertContains(page, 'rows="2"')

    def test_add_panel_starts_open_when_playlist_is_empty(self):
        self.playlist.items.all().delete()
        page = self.client.get(self.detail_url)
        self.assertContains(page, '<details class="panel playlist-add" open>')

    def test_arrows_move_a_song_up_and_down(self):
        middle = self.item("Noite de paz")
        url = reverse("private_area:playlist_item_move", args=[self.pk, middle.pk])
        moved = self.client.post(url, {"direction": "up"})
        self.assertRedirects(moved, f"{self.detail_url}#item-{middle.pk}")
        self.assertEqual(self.order(), ["Noite de paz", "Grande é o Senhor", "Castelo forte"])

        self.client.post(url, {"direction": "up"})
        self.assertEqual(self.order()[0], "Noite de paz")

        self.client.post(url, {"direction": "down"})
        self.client.post(url, {"direction": "down"})
        self.assertEqual(self.order(), ["Grande é o Senhor", "Castelo forte", "Noite de paz"])
        self.assertTrue(AuditLog.objects.filter(action="playlist_reordered").exists())

    def test_first_and_last_arrows_are_disabled(self):
        page = self.client.get(self.detail_url).content.decode()
        self.assertIn('aria-label="Subir Grande é o Senhor" disabled', page)
        self.assertIn('aria-label="Descer Castelo forte" disabled', page)
        self.assertNotIn('aria-label="Descer Grande é o Senhor" disabled', page)

    def test_drag_saves_full_order(self):
        ids = [self.item(t).pk for t in ("Castelo forte", "Grande é o Senhor", "Noite de paz")]
        response = self.client.post(
            reverse("private_area:playlist_reorder", args=[self.pk]),
            {"item": ids},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})
        self.assertEqual(self.order(), ["Castelo forte", "Grande é o Senhor", "Noite de paz"])
        page = self.client.get(self.detail_url).content.decode()
        self.assertLess(page.index("Castelo forte"), page.index("Noite de paz"))

    def test_reorder_rejects_incomplete_or_foreign_items(self):
        url = reverse("private_area:playlist_reorder", args=[self.pk])
        partial = [self.item("Noite de paz").pk]
        response = self.client.post(url, {"item": partial}, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 400)
        response = self.client.post(url, {"item": ["x"]})
        self.assertRedirects(response, self.detail_url)
        self.assertEqual(self.order(), list(TITLES))

    def test_remove_song_and_renumber(self):
        first = self.item("Grande é o Senhor")
        removed = self.client.post(
            reverse("private_area:playlist_item_remove", args=[self.pk, first.pk])
        )
        self.assertRedirects(removed, self.detail_url)
        self.assertEqual(self.order(), ["Noite de paz", "Castelo forte"])
        self.assertEqual(
            list(self.playlist.items.values_list("position", flat=True)), [1, 2]
        )
        self.assertTrue(AuditLog.objects.filter(action="playlist_item_removed").exists())

    def test_item_from_another_playlist_is_not_found(self):
        other = WeeklyPlaylist.objects.create(
            ministry=self.playlist.ministry, kind="rehearsal", starts_at=self.playlist.starts_at
        )
        item = self.item("Noite de paz")
        for name in ("playlist_item_move", "playlist_item_remove"):
            response = self.client.post(reverse(f"private_area:{name}", args=[other.pk, item.pk]))
            self.assertEqual(response.status_code, 404)

    def test_member_sees_no_controls_and_cannot_change_order(self):
        self.client.logout()
        self.client.login(username="membro", password="senha-segura-123")
        page = self.client.get(self.detail_url)
        self.assertNotContains(page, "playlist-actions")
        self.assertNotContains(page, "playlist.js")
        item = self.item("Noite de paz")
        for name in ("playlist_item_move", "playlist_item_remove"):
            response = self.client.post(
                reverse(f"private_area:{name}", args=[self.pk, item.pk]), {"direction": "up"}
            )
            self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse("private_area:playlist_reorder", args=[self.pk]), {"item": []}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.order(), list(TITLES))
