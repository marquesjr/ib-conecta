from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from apps.public.models import EventFamilyMember, EventIndexPage, EventPage, EventRegistration


def publish_retreat(**overrides) -> EventPage:
    root = Site.objects.get(is_default_site=True).root_page
    index = EventIndexPage.objects.filter(slug="agenda").first()
    if index is None:
        index = EventIndexPage(title="Agenda", slug="agenda", intro="")
        root.add_child(instance=index)
        index.save_revision().publish()
    defaults = {
        "title": "Retiro de famílias",
        "slug": "retiro-familias",
        "starts_at": timezone.now() + timedelta(days=20),
        "ends_at": timezone.now() + timedelta(days=22),
        "location": "Sítio da igreja",
        "body": "<p>Retiro com inscrição familiar.</p>",
        "requires_registration": True,
        "is_retreat": True,
        "capacity": 4,
        "sensitive_retain_days": 30,
    }
    defaults.update(overrides)
    event = EventPage(**defaults)
    index.add_child(instance=event)
    event.save_revision().publish()
    return event


def family_form_payload(extra=None):
    payload = {
        "name": "Maria Silva",
        "email": "maria@example.com",
        "phone": "27999990000",
        "birth_date": "1985-05-10",
        "guardian_name": "Maria Silva",
        "guardian_phone": "27999990000",
        "guardian_relationship": "mãe",
        "emergency_name": "João Silva",
        "emergency_phone": "27988887777",
        "dietary_restrictions": "sem glúten",
        "medical_notes": "asma leve",
        "transport_needed": "on",
        "boarding_point": "Praça central",
        "accommodation": "quarto família",
        "lgpd_consent": "on",
        "family-TOTAL_FORMS": "2",
        "family-INITIAL_FORMS": "0",
        "family-MIN_NUM_FORMS": "0",
        "family-MAX_NUM_FORMS": "10",
        "family-0-name": "Pedro Silva",
        "family-0-birth_date": "2015-03-01",
        "family-0-dietary_restrictions": "sem lactose",
        "family-0-medical_notes": "",
        "family-1-name": "",
        "family-1-birth_date": "",
        "family-1-dietary_restrictions": "",
        "family-1-medical_notes": "",
    }
    if extra:
        payload.update(extra)
    return payload


class RetreatPublicAgendaTests(TestCase):
    def test_retreat_appears_on_public_agenda_with_family_registration(self):
        publish_retreat()

        agenda = self.client.get("/agenda/")
        self.assertEqual(agenda.status_code, 200)
        self.assertContains(agenda, "Retiro de famílias")
        self.assertContains(agenda, "Retiro")
        self.assertContains(agenda, "/agenda/retiro-familias/")

        detail = self.client.get("/agenda/retiro-familias/")
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Inscrição individual ou familiar")
        self.assertContains(detail, 'name="guardian_name"')
        self.assertContains(detail, 'name="emergency_name"')
        self.assertContains(detail, 'name="dietary_restrictions"')
        self.assertContains(detail, 'name="medical_notes"')
        self.assertContains(detail, 'name="boarding_point"')
        self.assertContains(detail, 'name="accommodation"')
        self.assertNotContains(detail, 'name="bank_account"')
        self.assertNotContains(detail, 'name="agencia"')
        self.assertContains(detail, "PIX")

        response = self.client.post(
            "/agenda/retiro-familias/inscrever/",
            family_form_payload(),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inscrição confirmada")
        registration = EventRegistration.objects.get(email="maria@example.com")
        self.assertEqual(registration.status, EventRegistration.Status.CONFIRMED)
        self.assertEqual(registration.guardian_name, "Maria Silva")
        self.assertEqual(registration.emergency_name, "João Silva")
        self.assertEqual(registration.dietary_restrictions, "sem glúten")
        self.assertEqual(registration.medical_notes, "asma leve")
        self.assertEqual(registration.boarding_point, "Praça central")
        self.assertEqual(registration.pix_status, EventRegistration.PixStatus.PENDING)
        self.assertTrue(
            EventFamilyMember.objects.filter(
                registration=registration,
                name="Pedro Silva",
            ).exists()
        )


class RetreatWaitlistTests(TestCase):
    def test_full_retreat_goes_to_waitlist_without_bank_data(self):
        publish_retreat(capacity=2)
        first = self.client.post(
            "/agenda/retiro-familias/inscrever/",
            family_form_payload(),
        )
        self.assertEqual(first.status_code, 302)
        second = self.client.post(
            "/agenda/retiro-familias/inscrever/",
            family_form_payload(
                {
                    "name": "Ana Costa",
                    "email": "ana@example.com",
                    "phone": "27977776666",
                    "family-0-name": "",
                    "family-0-birth_date": "",
                    "family-0-dietary_restrictions": "",
                    "family-0-medical_notes": "",
                }
            ),
            follow=True,
        )
        self.assertContains(second, "lista de espera")
        waitlisted = EventRegistration.objects.get(email="ana@example.com")
        self.assertEqual(waitlisted.status, EventRegistration.Status.WAITLISTED)
        self.assertEqual(waitlisted.pix_status, EventRegistration.PixStatus.PENDING)
        self.assertFalse(hasattr(waitlisted, "bank_account"))
        detail = self.client.get("/agenda/retiro-familias/")
        self.assertContains(detail, "dados bancários")
