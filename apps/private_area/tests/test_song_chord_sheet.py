from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role
from apps.private_area.models import Song, SongStatus

User = get_user_model()


class SongChordSheetTests(TestCase):
    """A cifra rola só dentro do próprio bloco, sem empurrar a página no celular."""

    def setUp(self):
        member = User.objects.create_user(username="membro", password="senha-segura-123")
        member.profile.role = Role.MEMBER
        member.profile.save()
        self.song = Song.objects.create(
            title="Rascunho de ensaio",
            slug="rascunho-de-ensaio",
            status=SongStatus.PUBLISHED,
            lyrics="Uma linha de letra",
            chords="G            D/F#          Em7          C9          G/B    Am7    D4  D\nUma linha de cifra bem comprida",
            authors="Desconhecido",
            source="Hinário Batista",
            license="Uso congregacional autorizado",
            permitted_uses="Culto e ensaio",
            authorized=True,
        )
        self.client.login(username="membro", password="senha-segura-123")

    def test_chords_render_in_a_scrollable_sheet_with_size_controls(self):
        response = self.client.get(reverse("private_area:song_detail", args=[self.song.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<pre class="chord-sheet" tabindex="0"')
        self.assertContains(response, '<pre class="song-lyrics">')
        self.assertContains(response, 'class="chord-size"')
        self.assertContains(response, 'data-chord-step="-1"')
        self.assertContains(response, 'data-chord-step="1"')
        self.assertContains(response, "js/chord-sheet.js")

    def test_page_without_chords_has_no_size_controls(self):
        self.song.chords = ""
        self.song.save()
        response = self.client.get(reverse("private_area:song_detail", args=[self.song.slug]))
        self.assertNotContains(response, 'class="chord-size"')

    def test_css_keeps_chord_lines_intact_and_scrolls_only_the_sheet(self):
        css = (Path(settings.BASE_DIR) / "static/css/ib-conecta.css").read_text()
        rule = css.split(".chord-sheet {", 1)[1].split("}", 1)[0]
        self.assertIn("overflow-x: auto", rule)
        self.assertIn("max-width: 100%", rule)
        self.assertIn("overflow-wrap: normal", rule)
        self.assertNotIn("pre-wrap", rule)
