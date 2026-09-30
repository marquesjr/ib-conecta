import re

from django.test import TestCase
from wagtail.models import Site

from apps.public.models import ChurchSettings


class HomeSeeAllLinksTests(TestCase):
    """#71: cada seção da home tem o "ver todos" no mesmo lugar do HTML, depois do conteúdo."""

    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        settings = ChurchSettings.for_site(site)
        settings.instagram_url = "https://www.instagram.com/igrejabatista.santaleopoldina/"
        settings.save()

    def sections(self):
        html = self.client.get("/").content.decode()
        return re.findall(r'<section class="[^"]*\bhome-section\b[^"]*".*?</section>', html, re.S)

    def test_home_sections_share_one_structure(self):
        sections = self.sections()
        self.assertGreaterEqual(len(sections), 4)
        for section in sections:
            self.assertIn('class="section-heading"', section)
            heading = re.search(r'<div class="section-heading">.*?</h2>', section, re.S).group(0)
            self.assertNotIn("section-more", heading)

    def test_see_all_link_comes_after_the_content(self):
        for section in self.sections():
            if "section-more" not in section:
                continue
            more_at = section.index("section-more")
            content_at = max(section.rfind("</ul>"), section.rfind('class="mosaic"'))
            self.assertGreater(more_at, content_at)

    def test_instagram_link_is_a_section_more_link(self):
        html = self.client.get("/").content.decode()
        self.assertEqual(html.count("instagram-link section-more"), 1)
        self.assertNotRegex(html, r'class="text-link instagram-link"')
