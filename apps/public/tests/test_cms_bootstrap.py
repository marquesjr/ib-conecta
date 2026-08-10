from django.test import TestCase

from apps.public.bootstrap import bootstrap_cms
from apps.public.cms import (
    AGENDA_INDEX_SLUG,
    INSTITUTIONAL_PAGE_SEEDS,
    LIVE_STREAM_SLUG,
    NEWS_INDEX_SLUG,
    SERMON_INDEX_SLUG,
)
from apps.public.models import (
    EventIndexPage,
    InstitutionalPage,
    LiveStreamPage,
    NewsIndexPage,
    SermonIndexPage,
)


class CmsBootstrapTests(TestCase):
    def test_bootstrap_creates_public_news_index_and_institutional_pages(self):
        bootstrap_cms()
        response = self.client.get(f"/{NEWS_INDEX_SLUG}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Notícias")
        self.assertContains(response, f'href="/{NEWS_INDEX_SLUG}/"')
        self.assertEqual(
            NewsIndexPage.objects.live().filter(slug=NEWS_INDEX_SLUG).count(),
            1,
        )

        agenda = self.client.get(f"/{AGENDA_INDEX_SLUG}/")
        self.assertEqual(agenda.status_code, 200)
        self.assertContains(agenda, "Agenda")
        self.assertContains(agenda, f'href="/{AGENDA_INDEX_SLUG}/"')
        self.assertEqual(
            EventIndexPage.objects.live().filter(slug=AGENDA_INDEX_SLUG).count(),
            1,
        )

        sermons = self.client.get(f"/{SERMON_INDEX_SLUG}/")
        self.assertEqual(sermons.status_code, 200)
        self.assertContains(sermons, "Sermões")
        self.assertContains(sermons, f'href="/{SERMON_INDEX_SLUG}/"')
        self.assertEqual(
            SermonIndexPage.objects.live().filter(slug=SERMON_INDEX_SLUG).count(),
            1,
        )

        live = self.client.get(f"/{LIVE_STREAM_SLUG}/")
        self.assertEqual(live.status_code, 200)
        self.assertContains(live, "Ao vivo")
        self.assertContains(live, f'href="/{LIVE_STREAM_SLUG}/"')
        self.assertEqual(
            LiveStreamPage.objects.live().filter(slug=LIVE_STREAM_SLUG).count(),
            1,
        )

        for slug, title, _intro in INSTITUTIONAL_PAGE_SEEDS:
            page_response = self.client.get(f"/{slug}/")
            self.assertEqual(page_response.status_code, 200, slug)
            self.assertContains(page_response, title)

        bootstrap_cms()
        self.assertEqual(NewsIndexPage.objects.filter(slug=NEWS_INDEX_SLUG).count(), 1)
        self.assertEqual(EventIndexPage.objects.filter(slug=AGENDA_INDEX_SLUG).count(), 1)
        self.assertEqual(SermonIndexPage.objects.filter(slug=SERMON_INDEX_SLUG).count(), 1)
        self.assertEqual(LiveStreamPage.objects.filter(slug=LIVE_STREAM_SLUG).count(), 1)
        self.assertEqual(
            InstitutionalPage.objects.filter(
                slug__in=[slug for slug, _, _ in INSTITUTIONAL_PAGE_SEEDS]
            ).count(),
            len(INSTITUTIONAL_PAGE_SEEDS),
        )
