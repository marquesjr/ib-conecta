from django.test import TestCase

from apps.public.bootstrap import bootstrap_cms
from apps.public.cms import INSTITUTIONAL_PAGE_SEEDS, NEWS_INDEX_SLUG
from apps.public.models import InstitutionalPage, NewsIndexPage


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

        for slug, title, _intro in INSTITUTIONAL_PAGE_SEEDS:
            page_response = self.client.get(f"/{slug}/")
            self.assertEqual(page_response.status_code, 200, slug)
            self.assertContains(page_response, title)

        bootstrap_cms()
        self.assertEqual(NewsIndexPage.objects.filter(slug=NEWS_INDEX_SLUG).count(), 1)
        self.assertEqual(
            InstitutionalPage.objects.filter(
                slug__in=[slug for slug, _, _ in INSTITUTIONAL_PAGE_SEEDS]
            ).count(),
            len(INSTITUTIONAL_PAGE_SEEDS),
        )
