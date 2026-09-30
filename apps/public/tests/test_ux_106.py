from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role
from apps.public.models import PrayerRequest

User = get_user_model()


class PrayerRequestFilterTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="pastor", password="senha-segura-123")
        user.profile.role = Role.PASTOR
        user.profile.save()
        self.client.login(username="pastor", password="senha-segura-123")
        now = timezone.now()
        self.done = self._create("Pedido concluído", PrayerRequest.Status.DONE, now)
        self.progress = self._create("Pedido em acompanhamento", PrayerRequest.Status.IN_PROGRESS, now)
        self.old_new = self._create("Pedido novo antigo", PrayerRequest.Status.NEW, now - timedelta(days=2))
        self.new = self._create("Pedido novo recente", PrayerRequest.Status.NEW, now - timedelta(days=1))

    def _create(self, body, status, created_at):
        item = PrayerRequest.objects.create(body=body, is_anonymous=True, status=status)
        PrayerRequest.objects.filter(pk=item.pk).update(created_at=created_at)
        return item

    def test_lists_new_requests_first(self):
        response = self.client.get(reverse("accounts:prayer_requests"))
        bodies = [item.body for item in response.context["requests"]]
        self.assertEqual(
            bodies,
            ["Pedido novo recente", "Pedido novo antigo", "Pedido em acompanhamento", "Pedido concluído"],
        )

    def test_filters_by_status_with_counts(self):
        url = reverse("accounts:prayer_requests")
        response = self.client.get(url, {"situacao": "new"})
        self.assertEqual({item.pk for item in response.context["requests"]}, {self.new.pk, self.old_new.pk})
        self.assertNotContains(response, "Pedido concluído")
        self.assertContains(response, f'href="{url}?situacao=new" aria-current="page"')
        self.assertEqual(
            response.context["filters"],
            [("", "Todos", 4), ("new", "Novo", 2), ("in_progress", "Em acompanhamento", 1), ("done", "Concluído", 1)],
        )

    def test_invalid_filter_shows_all(self):
        response = self.client.get(reverse("accounts:prayer_requests"), {"situacao": "xyz"})
        self.assertEqual(len(response.context["requests"]), 4)
        self.assertEqual(response.context["selected_status"], "")

    def test_empty_filter_message(self):
        PrayerRequest.objects.filter(status=PrayerRequest.Status.DONE).delete()
        response = self.client.get(reverse("accounts:prayer_requests"), {"situacao": "done"})
        self.assertContains(response, "Nenhum pedido nesta situação.")

    def test_status_is_not_repeated_in_meta_line_and_form_saves_on_change(self):
        response = self.client.get(reverse("accounts:prayer_requests"), {"situacao": "done"})
        html = response.content.decode()
        meta = html.split('class="news-meta"', 1)[1].split("</p>", 1)[0]
        self.assertNotIn("Concluído", meta)
        self.assertIn("data-auto-submit", html)
        self.assertIn("js/auto-submit.js", html)
        self.assertNotIn("Atualizar situação", html)

    def test_update_keeps_current_filter(self):
        response = self.client.post(
            reverse("accounts:prayer_request_status", args=[self.new.pk]),
            {"status": PrayerRequest.Status.IN_PROGRESS, "situacao": "new"},
        )
        self.assertRedirects(response, reverse("accounts:prayer_requests") + "?situacao=new")
        self.new.refresh_from_db()
        self.assertEqual(self.new.status, PrayerRequest.Status.IN_PROGRESS)

    def test_update_without_filter_returns_to_full_list(self):
        response = self.client.post(
            reverse("accounts:prayer_request_status", args=[self.new.pk]),
            {"status": PrayerRequest.Status.DONE, "situacao": "../evil"},
        )
        self.assertRedirects(response, reverse("accounts:prayer_requests"))
