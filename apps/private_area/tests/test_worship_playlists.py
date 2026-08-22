from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import AuditLog, Role
from apps.private_area.models import AssignmentStatus, Ministry, MonthlySchedule, ScheduleAssignment, Song
from apps.private_area.tests.test_songbook import authorized_song_payload

User = get_user_model()

WORSHIP_FUNCTIONS = (
    "Dirigente",
    "Vocal",
    "Instrumento",
    "Sonoplastia",
    "Projeção",
)


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


def playlist_pk(response) -> int:
    return int(response.url.rstrip("/").rsplit("/", 1)[-1])


class WorshipScheduleTests(TestCase):
    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.joao = make_user("joao", Role.MEMBER)
        self.maria = make_user("maria", Role.MEMBER)
        self.client.login(username="lider", password="senha-segura-123")
        created = self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": "Ministério de louvor"},
        )
        self.assertEqual(created.status_code, 302)
        self.ministry = Ministry.objects.get(name="Louvor")

    def test_leader_builds_monthly_schedule_with_worship_functions(self):
        created = self.client.post(
            reverse("private_area:schedule_create", args=[self.ministry.pk]),
            {"year": 2026, "month": 9, "notes": "Cultos de setembro"},
        )
        self.assertEqual(created.status_code, 302)
        page = self.client.get(created.url)
        self.assertEqual(page.status_code, 200)
        for function in WORSHIP_FUNCTIONS:
            self.assertContains(page, function)

        schedule = MonthlySchedule.objects.get()
        for function in WORSHIP_FUNCTIONS:
            added = self.client.post(
                reverse("private_area:assignment_add", args=[schedule.pk]),
                {
                    "starts_at": "2026-09-06T19:00",
                    "function": function,
                    "participant": self.joao.pk,
                },
            )
            self.assertEqual(added.status_code, 302)

        detail = self.client.get(created.url)
        for function in WORSHIP_FUNCTIONS:
            self.assertContains(detail, function)
        self.assertContains(detail, "joao")

    def test_participant_confirms_and_leader_records_substitution(self):
        created = self.client.post(
            reverse("private_area:schedule_create", args=[self.ministry.pk]),
            {"year": 2026, "month": 9, "notes": ""},
        )
        schedule = MonthlySchedule.objects.get()
        self.client.post(
            reverse("private_area:assignment_add", args=[schedule.pk]),
            {
                "starts_at": "2026-09-06T19:00",
                "function": "Sonoplastia",
                "participant": self.joao.pk,
            },
        )
        assignment = ScheduleAssignment.objects.get()

        self.client.logout()
        self.client.login(username="joao", password="senha-segura-123")
        confirmed = self.client.post(
            reverse("private_area:assignment_respond", args=[assignment.pk]),
            {"action": "confirm"},
        )
        self.assertEqual(confirmed.status_code, 302)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, AssignmentStatus.CONFIRMED)

        self.client.logout()
        self.client.login(username="lider", password="senha-segura-123")
        substituted = self.client.post(
            reverse("private_area:assignment_substitute", args=[assignment.pk]),
            {"substitute": self.maria.pk},
        )
        self.assertEqual(substituted.status_code, 302)
        assignment.refresh_from_db()
        self.assertEqual(assignment.participant_id, self.maria.pk)
        self.assertEqual(assignment.status, AssignmentStatus.PENDING)
        history = self.client.get(created.url)
        self.assertContains(history, "Substituição")
        self.assertContains(history, "joao")
        self.assertContains(history, "maria")


class WeeklyPlaylistAccessTests(TestCase):
    def test_visitor_is_redirected_from_playlists(self):
        listing = self.client.get(reverse("private_area:playlist_list"))
        self.assertEqual(listing.status_code, 302)
        self.assertIn(reverse("accounts:login"), listing.url)

    def test_member_cannot_create_a_playlist(self):
        make_user("membro", Role.MEMBER)
        make_user("lider", Role.MINISTRY_LEADER)
        self.client.login(username="lider", password="senha-segura-123")
        self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": ""},
        )
        ministry = Ministry.objects.get()
        self.client.logout()
        self.client.login(username="membro", password="senha-segura-123")
        denied = self.client.post(
            reverse("private_area:playlist_create", args=[ministry.pk]),
            {
                "kind": "service",
                "starts_at": "2026-09-06T19:00",
                "notes": "",
            },
        )
        self.assertEqual(denied.status_code, 403)


class WeeklyPlaylistTests(TestCase):
    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.member = make_user("membro", Role.MEMBER)
        self.client.login(username="lider", password="senha-segura-123")
        self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": ""},
        )
        self.ministry = Ministry.objects.get()
        self.client.post(reverse("private_area:song_create"), authorized_song_payload())
        self.song = Song.objects.get(title="Grande é o Senhor")
        self.client.post(reverse("private_area:song_publish", args=[self.song.slug]))
        self.client.post(
            reverse("private_area:song_create"),
            authorized_song_payload(
                title="Noite de paz",
                lyrics="Noite de paz, noite de amor",
                chords="C     G\nNoite de paz",
                tags="natal",
            ),
        )
        self.christmas = Song.objects.get(title="Noite de paz")
        self.client.post(reverse("private_area:song_publish", args=[self.christmas.slug]))
        self.version = self.song.versions.get()

    def test_leader_creates_weekly_playlist_from_the_songbook(self):
        page = self.client.get(
            reverse("private_area:playlist_create", args=[self.ministry.pk])
        )
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Culto")
        self.assertContains(page, "Ensaio")

        created = self.client.post(
            reverse("private_area:playlist_create", args=[self.ministry.pk]),
            {
                "kind": "service",
                "starts_at": "2026-09-06T19:00",
                "notes": "Abertura do culto",
            },
        )
        self.assertEqual(created.status_code, 302)
        detail = self.client.get(created.url)
        self.assertContains(detail, "Culto")
        self.assertContains(detail, "Louvor")
        self.assertContains(detail, "Abertura do culto")
        self.assertContains(detail, "Grande é o Senhor")

        pk = playlist_pk(created)
        first = self.client.post(
            reverse("private_area:playlist_item_add", args=[pk]),
            {
                "song": self.song.pk,
                "version": self.version.pk,
                "key": "A",
                "notes": "Começar mais baixo",
                "position": "1",
            },
        )
        self.assertEqual(first.status_code, 302)
        second = self.client.post(
            reverse("private_area:playlist_item_add", args=[pk]),
            {
                "song": self.christmas.pk,
                "version": "",
                "key": "C",
                "notes": "Encerramento",
                "position": "2",
            },
        )
        self.assertEqual(second.status_code, 302)

        playlist = self.client.get(created.url)
        self.assertContains(playlist, "Grande é o Senhor")
        self.assertContains(playlist, "Noite de paz")
        self.assertContains(playlist, "Tom A")
        self.assertContains(playlist, "Tom C")
        self.assertContains(playlist, "Congregacional")
        self.assertContains(playlist, "Começar mais baixo")
        self.assertContains(playlist, "Encerramento")
        body = playlist.content.decode()
        self.assertLess(body.index("Grande é o Senhor"), body.index("Noite de paz"))
        entry = AuditLog.objects.filter(action="playlist_created").latest("created_at")
        self.assertEqual(entry.metadata.get("ministry_id"), self.ministry.pk)

        listing = self.client.get(reverse("private_area:playlist_list"))
        self.assertContains(listing, "Culto")
        self.assertContains(listing, "Louvor")

    def test_unpublished_song_cannot_enter_the_playlist(self):
        self.client.post(
            reverse("private_area:song_create"),
            authorized_song_payload(title="Rascunho interno"),
        )
        draft = Song.objects.get(title="Rascunho interno")
        created = self.client.post(
            reverse("private_area:playlist_create", args=[self.ministry.pk]),
            {
                "kind": "rehearsal",
                "starts_at": "2026-09-05T19:00",
                "notes": "",
            },
        )
        self.assertEqual(created.status_code, 302)
        pk = playlist_pk(created)
        denied = self.client.post(
            reverse("private_area:playlist_item_add", args=[pk]),
            {
                "song": draft.pk,
                "version": "",
                "key": "G",
                "notes": "",
                "position": "1",
            },
        )
        self.assertEqual(denied.status_code, 302)
        detail = self.client.get(created.url)
        self.assertNotContains(detail, "Rascunho interno")
        self.assertContains(detail, "publicado")

    def test_member_consults_and_prints_playlist_material(self):
        created = self.client.post(
            reverse("private_area:playlist_create", args=[self.ministry.pk]),
            {
                "kind": "service",
                "starts_at": "2026-09-06T19:00",
                "notes": "",
            },
        )
        pk = playlist_pk(created)
        self.client.post(
            reverse("private_area:playlist_item_add", args=[pk]),
            {
                "song": self.song.pk,
                "version": self.version.pk,
                "key": "G",
                "notes": "",
                "position": "1",
            },
        )
        self.client.logout()
        self.client.login(username="membro", password="senha-segura-123")

        listing = self.client.get(reverse("private_area:playlist_list"))
        self.assertEqual(listing.status_code, 200)
        self.assertContains(listing, "Culto")
        detail = self.client.get(reverse("private_area:playlist_detail", args=[pk]))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Grande é o Senhor")
        self.assertNotContains(detail, "Adicionar louvor")

        printable = self.client.get(
            reverse("private_area:playlist_print", args=[pk])
        )
        self.assertEqual(printable.status_code, 200)
        self.assertContains(printable, "Salvar como PDF")
        self.assertContains(printable, "Grande é o Senhor")
        self.assertContains(printable, "mui digno de louvor")
        self.assertContains(printable, "G          D")
        self.assertContains(printable, "Congregacional")

        lyrics_only = self.client.get(
            reverse("private_area:playlist_print", args=[pk]) + "?layout=lyrics"
        )
        self.assertContains(lyrics_only, "mui digno de louvor")
        self.assertNotContains(lyrics_only, "G          D")

    def test_playlist_exports_calendar_and_authorized_whatsapp_share(self):
        created = self.client.post(
            reverse("private_area:playlist_create", args=[self.ministry.pk]),
            {
                "kind": "service",
                "starts_at": "2026-09-06T19:00",
                "notes": "",
            },
        )
        pk = playlist_pk(created)
        self.client.post(
            reverse("private_area:playlist_item_add", args=[pk]),
            {
                "song": self.song.pk,
                "version": "",
                "key": "G",
                "notes": "",
                "position": "1",
            },
        )
        self.client.logout()
        self.client.login(username="membro", password="senha-segura-123")

        calendar = self.client.get(
            reverse("private_area:playlist_calendar", args=[pk])
        )
        self.assertEqual(calendar.status_code, 200)
        self.assertIn("text/calendar", calendar["Content-Type"])
        body = calendar.content.decode()
        self.assertIn("BEGIN:VCALENDAR", body)
        self.assertIn("BEGIN:VEVENT", body)
        self.assertIn("SUMMARY:Louvor — Culto", body)
        self.assertIn("Grande é o Senhor", body)

        detail = self.client.get(
            reverse("private_area:playlist_detail", args=[pk])
        )
        self.assertContains(detail, "wa.me")
        self.assertContains(detail, "Compartilhar no WhatsApp")

        home = self.client.get(reverse("private_area:home"))
        self.assertContains(home, "Playlist")
        self.assertContains(home, "Culto")
        self.assertContains(home, "Louvor")
