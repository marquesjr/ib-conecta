from django.test import TestCase
from wagtail.models import Site

from apps.public.models import InstitutionalPage


class CmsRevisionTests(TestCase):
    def setUp(self):
        self.root = Site.objects.get(is_default_site=True).root_page

    def test_publish_keeps_revision_history_and_can_revert(self):
        page = InstitutionalPage(
            title="Liderança",
            slug="lideranca",
            intro="Equipe pastoral.",
            body="<p>Versão publicada original.</p>",
        )
        self.root.add_child(instance=page)
        first_revision = page.save_revision()
        first_revision.publish()

        page.refresh_from_db()
        page.body = "<p>Versão alterada por engano.</p>"
        page.save_revision().publish()

        public = self.client.get("/lideranca/")
        self.assertContains(public, "Versão alterada por engano.")

        revisions = list(page.revisions.order_by("created_at"))
        self.assertGreaterEqual(len(revisions), 2)

        revisions[0].publish()

        reverted = self.client.get("/lideranca/")
        self.assertContains(reverted, "Versão publicada original.")
        self.assertNotContains(reverted, "Versão alterada por engano.")
