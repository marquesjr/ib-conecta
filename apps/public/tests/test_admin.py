from django.test import TestCase


class AdminSmokeTests(TestCase):
    def test_wagtail_admin_is_reachable(self):
        response = self.client.get("/admin/")
        self.assertIn(response.status_code, (200, 302))
