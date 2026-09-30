from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role
from apps.private_area.models import Song, SongStatus
from apps.private_area.songbook import song_tags

User = get_user_model()


def make_song(title: str, slug: str, tags: str, status: str = SongStatus.PUBLISHED) -> Song:
    return Song.objects.create(
        title=title,
        slug=slug,
        tags=tags,
        status=status,
        authors="Autoria",
        source="Fonte",
        license="Licença",
        permitted_uses="Culto",
        authorized=True,
    )


class SongbookChipsTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="membro", password="senha-segura-123")
        user.profile.role = Role.MEMBER
        user.profile.save()
        self.client.login(username="membro", password="senha-segura-123")
        self.grande = make_song("Grande é o Senhor", "grande", "adoração, Clássico")
        self.noite = make_song("Noite de paz", "noite", "natal, clássico")
        make_song("Rascunho secreto", "rascunho", "oculta", status=SongStatus.DRAFT)

    def test_song_tags_are_distinct_sorted_and_case_insensitive(self):
        self.assertEqual(
            song_tags(Song.objects.filter(status=SongStatus.PUBLISHED)),
            ["adoração", "Clássico", "natal"],
        )

    def test_tags_render_as_chips_without_hidden_songs_tags(self):
        response = self.client.get(reverse("private_area:songbook"))
        self.assertContains(response, 'class="tag-chip" href="?q="')
        self.assertContains(response, ">natal</a>")
        self.assertNotContains(response, "oculta")
        self.assertNotContains(response, 'id="id_tag"')

    def test_active_tag_chip_is_marked_and_filters_the_list(self):
        response = self.client.get(reverse("private_area:songbook"), {"tag": "natal"})
        self.assertContains(
            response, 'href="?tag=natal&amp;q=" aria-current="true">natal</a>', html=False
        )
        self.assertContains(response, "Noite de paz")
        self.assertNotContains(response, "Grande é o Senhor")
        self.assertContains(response, 'type="hidden" name="tag" value="natal"')

    def test_title_links_to_song_and_print_options_live_in_a_menu(self):
        response = self.client.get(reverse("private_area:songbook"))
        detail = reverse("private_area:song_detail", args=[self.grande.slug])
        self.assertContains(response, f'<a class="song-title" href="{detail}">Grande é o Senhor</a>')
        self.assertNotContains(response, "Abrir louvor")
        self.assertContains(response, '<summary class="cta secondary">Imprimir</summary>')
        self.assertContains(response, "data-print-link", count=4)
        self.assertContains(response, "js/songbook.js")
