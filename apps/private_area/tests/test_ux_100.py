from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role
from apps.private_area.tests.test_songbook import authorized_song_payload, make_user


class SongFormSectionsTests(TestCase):
    """UX #100: cadastro de louvor agrupado em seções, com salvar fixo no rodapé."""

    def setUp(self):
        make_user("lider", Role.MINISTRY_LEADER)
        self.client.login(username="lider", password="senha-segura-123")

    def test_form_is_grouped_in_sections_in_order(self):
        page = self.client.get(reverse("private_area:song_create"))
        html = page.content.decode()
        legends = [
            "<legend>Dados</legend>",
            "<legend>Letra e cifra</legend>",
            "<legend>Licença</legend>",
            "<legend>Referências externas</legend>",
            "<legend>Versões</legend>",
        ]
        positions = [html.index(legend) for legend in legends]
        self.assertEqual(positions, sorted(positions))
        # Cada campo aparece dentro da sua seção.
        self.assertLess(html.index('name="title"'), positions[1])
        self.assertTrue(positions[1] < html.index('name="lyrics"') < positions[2])
        self.assertTrue(positions[2] < html.index('name="authorized"') < positions[3])
        self.assertTrue(positions[3] < html.index('name="references-0-target_url"') < positions[4])
        self.assertGreater(html.index('name="versions-0-name"'), positions[4])

    def test_save_button_lives_in_sticky_footer_and_textareas_grow(self):
        page = self.client.get(reverse("private_area:song_create"))
        self.assertContains(page, 'class="form-sticky-actions"')
        self.assertContains(page, "Salvar rascunho")
        self.assertContains(page, "js/song-form.js")

    def test_non_field_error_is_shown_at_the_top(self):
        response = self.client.post(
            reverse("private_area:song_create"),
            authorized_song_payload(authorized=""),
        )
        html = response.content.decode()
        self.assertIn("Não é permitido armazenar louvor sem autorização de uso.", html)
        self.assertLess(
            html.index("Não é permitido armazenar"), html.index("<legend>Dados</legend>")
        )
