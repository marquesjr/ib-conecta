from django.test import TestCase


class HomePageTests(TestCase):
    def test_home_returns_ok_with_project_name(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "IB Conecta")
