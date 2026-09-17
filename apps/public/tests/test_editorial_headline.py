from django.test import SimpleTestCase, override_settings
from django.utils.html import strip_tags

from apps.public.templatetags.public_tags import editorial_headline, is_demo_preview


class EditorialHeadlineTests(SimpleTestCase):
    def test_cms_words_are_preserved_with_emphasis(self):
        text = "Jesus te convida a conhecer a graça de Deus"
        rendered = editorial_headline(text)
        self.assertEqual(strip_tags(rendered), text)
        self.assertIn("<em>graça de Deus</em>", rendered)

    def test_cms_html_is_escaped(self):
        rendered = editorial_headline('<script>alert("x")</script> Deus acolhe')
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    @override_settings(DEBUG=False, EDITORIAL_DEMO_PREVIEW=True)
    def test_demo_notice_cannot_be_enabled_in_production(self):
        self.assertFalse(is_demo_preview())

    @override_settings(DEBUG=True, EDITORIAL_DEMO_PREVIEW=True)
    def test_isolated_demo_preview_is_labelled(self):
        self.assertTrue(is_demo_preview())
