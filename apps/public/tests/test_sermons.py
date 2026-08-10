from django.test import TestCase
from wagtail.models import Site

from apps.public.models import SermonIndexPage, SermonPage


class SermonPublicTests(TestCase):
    def setUp(self):
        self.root = Site.objects.get(is_default_site=True).root_page
        self.index = SermonIndexPage(
            title="Sermões",
            slug="sermoes",
            intro="Sermões e estudos da Igreja Batista em Santa Leopoldina.",
        )
        self.root.add_child(instance=self.index)
        self.index.save_revision().publish()

    def test_published_sermon_with_embed_appears_on_index_and_detail(self):
        sermon = SermonPage(
            title="A graça que basta",
            slug="a-graca-que-basta",
            intro="Estudo sobre 2 Coríntios 12.",
            body="<p>Texto do estudo para leitura.</p>",
            media_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
        self.index.add_child(instance=sermon)
        sermon.save_revision().publish()

        index_response = self.client.get("/sermoes/")
        self.assertEqual(index_response.status_code, 200)
        self.assertContains(index_response, "Sermões")
        self.assertContains(index_response, "A graça que basta")
        self.assertContains(index_response, "/sermoes/a-graca-que-basta/")

        detail = self.client.get("/sermoes/a-graca-que-basta/")
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "A graça que basta")
        self.assertContains(detail, "Estudo sobre 2 Coríntios 12.")
        self.assertContains(detail, "Texto do estudo para leitura.")
        self.assertContains(detail, 'name="viewport"')
        self.assertContains(detail, "youtube-nocookie.com/embed/dQw4w9WgXcQ")
        self.assertNotContains(detail, "autoplay")
        self.assertNotContains(detail, 'type="file"')

    def test_published_sermon_with_audio_url_embeds_player(self):
        sermon = SermonPage(
            title="Estudo em áudio",
            slug="estudo-em-audio",
            intro="Ouça o estudo.",
            body="<p>Roteiro do estudo.</p>",
            media_url="https://cdn.example.com/estudos/graca.mp3",
        )
        self.index.add_child(instance=sermon)
        sermon.save_revision().publish()

        detail = self.client.get("/sermoes/estudo-em-audio/")
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "<audio")
        self.assertContains(detail, 'preload="none"')
        self.assertContains(detail, "https://cdn.example.com/estudos/graca.mp3")
        self.assertNotContains(detail, "autoplay")

    def test_draft_sermon_is_hidden_from_index_and_detail(self):
        sermon = SermonPage(
            title="Rascunho pastoral",
            slug="rascunho-pastoral",
            intro="Ainda em preparação.",
            body="<p>Não deve aparecer no site.</p>",
            media_url="",
            live=False,
        )
        self.index.add_child(instance=sermon)
        sermon.save_revision()

        index_response = self.client.get("/sermoes/")
        self.assertEqual(index_response.status_code, 200)
        self.assertNotContains(index_response, "Rascunho pastoral")

        self.assertEqual(self.client.get("/sermoes/rascunho-pastoral/").status_code, 404)
