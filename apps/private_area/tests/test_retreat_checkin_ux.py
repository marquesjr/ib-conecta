from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role
from apps.private_area.models import EventOperation
from apps.private_area.tests.test_retreats import enroll_family, make_user, publish_retreat
from apps.public.models import EventFamilyMember, EventRegistration


class RetreatCheckInUxTests(TestCase):
    def setUp(self):
        make_user("coordenador", Role.EVENTS_COMMISSION)
        self.event = publish_retreat()
        self.client.login(username="coordenador", password="senha-segura-123")
        self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": ""},
        )
        self.operation = EventOperation.objects.get()
        self.registration = enroll_family(self.event)
        self.other = EventRegistration.objects.create(
            event=self.event,
            name="Sônia Castro",
            email="sonia@example.com",
            phone="27999990001",
            birth_date="1980-01-01",
            is_minor=False,
            emergency_name="Igor Castro",
            emergency_phone="27988880004",
            lgpd_consent=True,
            status=EventRegistration.Status.CONFIRMED,
        )
        self.url = reverse("private_area:retreat_roster", args=[self.operation.pk])

    def test_counter_shows_present_out_of_expected_people(self):
        self.client.post(reverse("private_area:retreat_check_in", args=[self.registration.pk]))
        page = self.client.get(self.url)
        # Maria + Pedro (familiar) + Sônia = 3 pessoas; só Maria chegou.
        self.assertContains(page, "<strong>1 de 3</strong> presentes", html=False)

    def test_search_filters_by_name_ignoring_accents_and_family_members(self):
        page = self.client.get(self.url, {"q": "sonia"})
        self.assertContains(page, "Sônia Castro")
        self.assertNotContains(page, "Maria Silva")
        self.assertContains(page, "Limpar busca")

        by_family = self.client.get(self.url, {"q": "pedro"})
        self.assertContains(by_family, "Maria Silva")
        self.assertNotContains(by_family, "Sônia Castro")

        nobody = self.client.get(self.url, {"q": "zzz"})
        self.assertContains(nobody, "Ninguém encontrado com esse nome.")
        # O contador continua contando o retiro inteiro.
        self.assertContains(nobody, "<strong>0 de 3</strong>", html=False)

    def test_holder_and_family_share_the_same_button_style(self):
        page = self.client.get(self.url).content.decode()
        self.assertIn('aria-label="Check-in de Maria Silva">Check-in</button>', page)
        self.assertIn('aria-label="Check-in de Pedro Silva">Check-in</button>', page)
        self.assertEqual(
            page.count('<button class="cta secondary" type="submit" aria-label="Check-in de'),
            3,
        )

    def test_sensitive_data_is_collapsed(self):
        page = self.client.get(self.url).content.decode()
        details = page.index('<details class="checkin-sensitive">')
        self.assertLess(details, page.index("asma leve"))
        self.assertLess(details, page.index("Emergência: João Silva"))
        self.assertNotIn('<details class="checkin-sensitive" open', page)

    def test_check_in_keeps_the_search(self):
        member = EventFamilyMember.objects.get(name="Pedro Silva")
        response = self.client.post(
            reverse("private_area:retreat_member_check_in", args=[member.pk]),
            {"q": "silva"},
        )
        self.assertRedirects(response, f"{self.url}?q=silva", fetch_redirect_response=False)
        member.refresh_from_db()
        self.assertIsNotNone(member.checked_in_at)

        plain = self.client.post(reverse("private_area:retreat_check_in", args=[self.other.pk]))
        self.assertRedirects(plain, self.url, fetch_redirect_response=False)
