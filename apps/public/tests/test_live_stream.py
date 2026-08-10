from django.test import TestCase
from wagtail.models import Site

from apps.public.models import LiveStreamPage


class LiveStreamPublicTests(TestCase):
    def setUp(self):
        self.root = Site.objects.get(is_default_site=True).root_page

    def test_live_page_embeds_youtube_without_autoplay(self):
        page = LiveStreamPage(
            title="Ao vivo",
            slug="ao-vivo",
            intro="Acompanhe o culto quando estiver no ar.",
            body="<p>Transmissão pela igreja no YouTube.</p>",
            youtube_url="https://www.youtube.com/live/dQw4w9WgXcQ",
        )
        self.root.add_child(instance=page)
        page.save_revision().publish()

        response = self.client.get("/ao-vivo/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ao vivo")
        self.assertContains(response, "Acompanhe o culto quando estiver no ar.")
        self.assertContains(response, "Transmissão pela igreja no YouTube.")
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, "youtube-nocookie.com/embed/dQw4w9WgXcQ")
        self.assertContains(response, 'loading="lazy"')
        self.assertNotContains(response, "autoplay")
        self.assertNotContains(response, 'type="file"')
        self.assertNotContains(response, "enctype=")

    def test_draft_live_page_is_not_public(self):
        page = LiveStreamPage(
            title="Ensaio ao vivo",
            slug="ensaio-ao-vivo",
            youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            live=False,
        )
        self.root.add_child(instance=page)
        page.save_revision()

        self.assertEqual(self.client.get("/ensaio-ao-vivo/").status_code, 404)
