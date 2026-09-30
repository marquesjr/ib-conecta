from importlib import import_module

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role
from apps.private_area.models import Ministry, WeeklyPlaylist

User = get_user_model()

PLAYLIST_BUTTON = "Montar playlist semanal"


def make_leader():
    user = User.objects.create_user(username="lider", password="senha-segura-123")
    user.profile.role = Role.MINISTRY_LEADER
    user.profile.save()
    return user


class MinistryRepertoireTests(TestCase):
    def setUp(self):
        self.leader = make_leader()
        self.client.login(username="lider", password="senha-segura-123")

    def test_playlist_button_is_hidden_for_ministry_without_repertoire(self):
        diaconia = Ministry.objects.create(name="Diaconia")
        page = self.client.get(reverse("private_area:ministry_detail", args=[diaconia.pk]))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Montar escala mensal")
        self.assertNotContains(page, PLAYLIST_BUTTON)

    def test_playlist_button_is_shown_for_ministry_with_repertoire(self):
        louvor = Ministry.objects.create(name="Louvor", uses_repertoire=True)
        page = self.client.get(reverse("private_area:ministry_detail", args=[louvor.pk]))
        self.assertContains(page, PLAYLIST_BUTTON)
        self.assertContains(
            page, reverse("private_area:playlist_create", args=[louvor.pk])
        )

    def test_leader_marks_repertoire_when_creating_a_ministry(self):
        form = self.client.get(reverse("private_area:ministry_create"))
        self.assertContains(form, "Usa repertório")
        self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": "", "uses_repertoire": "on"},
        )
        self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Recepção", "description": ""},
        )
        self.assertTrue(Ministry.objects.get(name="Louvor").uses_repertoire)
        self.assertFalse(Ministry.objects.get(name="Recepção").uses_repertoire)


class MarkWorshipMinistriesMigrationTests(TestCase):
    def test_marks_louvor_and_ministries_that_already_have_playlists(self):
        migration = import_module(
            "apps.private_area.migrations.0012_ministry_uses_repertoire"
        )
        louvor = Ministry.objects.create(name="louvor")
        coral = Ministry.objects.create(name="Coral")
        diaconia = Ministry.objects.create(name="Diaconia")
        WeeklyPlaylist.objects.create(
            ministry=coral, kind="rehearsal", starts_at="2026-09-06T19:00-03:00"
        )

        migration.mark_worship_ministries(django_apps, None)

        louvor.refresh_from_db()
        coral.refresh_from_db()
        diaconia.refresh_from_db()
        self.assertTrue(louvor.uses_repertoire)
        self.assertTrue(coral.uses_repertoire)
        self.assertFalse(diaconia.uses_repertoire)
