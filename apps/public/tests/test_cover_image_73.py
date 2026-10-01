from django.test import TestCase
from django.utils import timezone
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

from apps.public.models import (
    EventIndexPage,
    EventPage,
    NewsIndexPage,
    NewsPage,
    SermonIndexPage,
    SermonPage,
)


class CoverImageTests(TestCase):
    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page
        self.image = Image.objects.create(title="Capa de teste", file=get_test_image_file())
        self.news_index = NewsIndexPage(title="Notícias", slug="noticias")
        self.sermon_index = SermonIndexPage(title="Sermões", slug="sermoes")
        self.event_index = EventIndexPage(title="Agenda", slug="agenda")
        for index in (self.news_index, self.sermon_index, self.event_index):
            root.add_child(instance=index)
            index.save_revision().publish()

    def publish(self, parent, page):
        parent.add_child(instance=page)
        page.save_revision().publish()
        return page

    def pages(self, with_image):
        cover = self.image if with_image else None
        news = self.publish(
            self.news_index, NewsPage(title="Notícia", slug="noticia", body="<p>x</p>", cover_image=cover)
        )
        sermon = self.publish(
            self.sermon_index, SermonPage(title="Sermão", slug="sermao", body="<p>x</p>", cover_image=cover)
        )
        event = self.publish(
            self.event_index,
            EventPage(title="Culto", slug="culto", starts_at=timezone.now() + timezone.timedelta(days=3), cover_image=cover),
        )
        return news, sermon, event

    def test_lists_show_a_thumbnail_and_details_show_the_cover(self):
        pages = self.pages(with_image=True)
        for url in ("/noticias/", "/sermoes/", "/agenda/"):
            with self.subTest(list=url):
                self.assertContains(self.client.get(url), 'class="register-thumb"')
        for page in pages:
            with self.subTest(detail=page.slug):
                self.assertContains(self.client.get(page.url), 'class="cover-image"')

    def test_pages_without_image_look_as_before(self):
        pages = self.pages(with_image=False)
        for url in ("/noticias/", "/sermoes/", "/agenda/"):
            self.assertNotContains(self.client.get(url), "register-thumb")
        for page in pages:
            self.assertNotContains(self.client.get(page.url), "cover-image")

    def test_image_is_optional_in_the_cms_form(self):
        field = NewsPage._meta.get_field("cover_image")
        self.assertTrue(field.null and field.blank)
