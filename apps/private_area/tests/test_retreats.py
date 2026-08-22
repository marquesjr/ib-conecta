from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Site

from apps.accounts.models import Role
from apps.private_area.models import EventOperation, EventOperationDocument, EventTeam, EventTeamMember
from apps.public.models import EventFamilyMember, EventIndexPage, EventPage, EventRegistration

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


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
        "body": "<p>Retiro</p>",
        "requires_registration": True,
        "is_retreat": True,
        "capacity": 20,
        "sensitive_retain_days": 30,
    }
    defaults.update(overrides)
    event = EventPage(**defaults)
    index.add_child(instance=event)
    event.save_revision().publish()
    return event


def enroll_family(event: EventPage) -> EventRegistration:
    registration = EventRegistration.objects.create(
        event=event,
        name="Maria Silva",
        email="maria@example.com",
        phone="27999990000",
        birth_date="1985-05-10",
        is_minor=False,
        guardian_name="Maria Silva",
        guardian_phone="27999990000",
        guardian_relationship="mãe",
        emergency_name="João Silva",
        emergency_phone="27988887777",
        dietary_restrictions="sem glúten",
        medical_notes="asma leve",
        transport_needed=True,
        boarding_point="Praça central",
        accommodation="quarto família",
        pix_status=EventRegistration.PixStatus.PENDING,
        lgpd_consent=True,
        status=EventRegistration.Status.CONFIRMED,
    )
    EventFamilyMember.objects.create(
        registration=registration,
        name="Pedro Silva",
        birth_date="2015-03-01",
        is_minor=True,
        dietary_restrictions="sem lactose",
        medical_notes="alergia a dipirona",
    )
    return registration


class RetreatRosterAccessTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.ana = make_user("ana", Role.MEMBER)
        self.tesoureiro = make_user("tesoureiro", Role.TREASURY)
        self.event = publish_retreat()
        self.client.login(username="coordenador", password="senha-segura-123")
        created = self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": "Programação: culto às 20h."},
        )
        self.assertEqual(created.status_code, 302)
        self.operation = EventOperation.objects.get()
        self.registration = enroll_family(self.event)
        self.roster_url = reverse("private_area:retreat_roster", args=[self.operation.pk])

    def test_commission_sees_restricted_retreat_roster_and_pix_status(self):
        page = self.client.get(self.roster_url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Maria Silva")
        self.assertContains(page, "Pedro Silva")
        self.assertContains(page, "asma leve")
        self.assertContains(page, "sem glúten")
        self.assertContains(page, "alergia a dipirona")
        self.assertContains(page, "Praça central")
        self.assertContains(page, "PIX pendente")
        self.assertContains(page, "Lista de espera")
        self.assertNotContains(page, "agencia")
        self.assertNotContains(page, "conta bancária")

        pix = self.client.post(
            reverse("private_area:retreat_pix_status", args=[self.registration.pk]),
            {"pix_status": EventRegistration.PixStatus.PAID},
        )
        self.assertEqual(pix.status_code, 302)
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.pix_status, EventRegistration.PixStatus.PAID)
        roster = self.client.get(self.roster_url)
        self.assertContains(roster, "PIX pago")

    def test_member_without_team_cannot_see_sensitive_retreat_data(self):
        self.client.logout()
        self.client.login(username="ana", password="senha-segura-123")
        response = self.client.get(self.roster_url)
        self.assertEqual(response.status_code, 403)

    def test_treasury_cannot_see_medical_or_minor_data(self):
        self.client.logout()
        self.client.login(username="tesoureiro", password="senha-segura-123")
        response = self.client.get(self.roster_url)
        self.assertEqual(response.status_code, 403)


class RetreatCheckInTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.ana = make_user("ana", Role.MEMBER)
        self.bruno = make_user("bruno", Role.MEMBER)
        self.event = publish_retreat()
        self.client.login(username="coordenador", password="senha-segura-123")
        self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": "Programação: culto às 20h."},
        )
        self.operation = EventOperation.objects.get()
        self.registration = enroll_family(self.event)
        self.client.post(
            reverse("private_area:event_team_add", args=[self.operation.pk]),
            {"name": "Recepção"},
        )
        team = EventTeam.objects.get()
        self.client.post(
            reverse("private_area:event_team_member_add", args=[team.pk]),
            {"user": self.ana.pk},
        )
        uploaded = self.client.post(
            reverse("private_area:event_document_upload", args=[self.operation.pk]),
            {
                "title": "Programação do retiro",
                "file": SimpleUploadedFile(
                    "programacao.pdf",
                    b"%PDF-1.4 programacao-privada",
                    content_type="application/pdf",
                ),
            },
        )
        self.assertEqual(uploaded.status_code, 302)
        self.document = EventOperationDocument.objects.get()

    def test_team_checks_in_and_reads_private_program(self):
        self.client.logout()
        self.client.login(username="ana", password="senha-segura-123")
        roster = self.client.get(
            reverse("private_area:retreat_roster", args=[self.operation.pk])
        )
        self.assertEqual(roster.status_code, 200)
        self.assertContains(roster, "Maria Silva")
        self.assertContains(roster, "Programação: culto às 20h.")
        self.assertContains(roster, "Programação do retiro")
        self.assertContains(roster, "Lista de presença")

        checkin = self.client.post(
            reverse("private_area:retreat_check_in", args=[self.registration.pk]),
        )
        self.assertEqual(checkin.status_code, 302)
        self.registration.refresh_from_db()
        self.assertIsNotNone(self.registration.checked_in_at)

        member = EventFamilyMember.objects.get(name="Pedro Silva")
        child_checkin = self.client.post(
            reverse("private_area:retreat_member_check_in", args=[member.pk]),
        )
        self.assertEqual(child_checkin.status_code, 302)
        member.refresh_from_db()
        self.assertIsNotNone(member.checked_in_at)

        download = self.client.get(
            reverse("private_area:event_document_download", args=[self.document.pk])
        )
        self.assertEqual(download.status_code, 200)

        home = self.client.get(reverse("private_area:home"))
        self.assertContains(home, "Retiro de famílias")

    def test_other_member_cannot_check_in(self):
        self.client.logout()
        self.client.login(username="bruno", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:retreat_check_in", args=[self.registration.pk]),
        )
        self.assertEqual(response.status_code, 403)
        download = self.client.get(
            reverse("private_area:event_document_download", args=[self.document.pk])
        )
        self.assertEqual(download.status_code, 403)


class RetreatSensitiveDiscardTests(TestCase):
    def test_medical_and_minor_data_are_discarded_after_retention(self):
        past_end = timezone.now() - timedelta(days=40)
        event = publish_retreat(
            starts_at=past_end - timedelta(days=2),
            ends_at=past_end,
            sensitive_retain_days=30,
        )
        coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        EventOperation.objects.create(public_event=event, created_by=coordinator)
        registration = enroll_family(event)

        call_command("discard_retreat_sensitive_data")
        registration.refresh_from_db()
        self.assertEqual(registration.medical_notes, "")
        self.assertEqual(registration.dietary_restrictions, "")
        self.assertEqual(registration.guardian_name, "")
        self.assertIsNotNone(registration.sensitive_discarded_at)
        child = EventFamilyMember.objects.get(name="Pedro Silva")
        self.assertEqual(child.medical_notes, "")
        self.assertEqual(child.dietary_restrictions, "")
        self.assertIsNone(child.birth_date)
        self.assertEqual(registration.name, "Maria Silva")
        self.assertEqual(child.name, "Pedro Silva")


class RetreatCreateFromCommissionTests(TestCase):
    def test_coordinator_publishes_retreat_with_family_registration(self):
        make_user("coordenador", Role.EVENTS_COMMISSION)
        root = Site.objects.get(is_default_site=True).root_page
        index = EventIndexPage(title="Agenda", slug="agenda", intro="")
        root.add_child(instance=index)
        index.save_revision().publish()
        self.client.login(username="coordenador", password="senha-segura-123")
        starts = timezone.now() + timedelta(days=25)
        response = self.client.post(
            reverse("private_area:event_operation_create"),
            {
                "title": "Retiro de casais",
                "starts_at": starts.strftime("%Y-%m-%dT%H:%M"),
                "location": "Sítio da igreja",
                "body": "Inscrições abertas",
                "requires_registration": "on",
                "is_retreat": "on",
                "capacity": "40",
                "notes": "Equipe de apoio",
            },
        )
        self.assertEqual(response.status_code, 302)
        event = EventPage.objects.get(title="Retiro de casais")
        self.assertTrue(event.is_retreat)
        self.assertEqual(event.capacity, 40)
        public = self.client.get(event.url)
        self.assertContains(public, "Inscrição individual ou familiar")
        self.assertContains(public, 'name="guardian_name"')


class RetreatAttachExistingTests(TestCase):
    def test_coordinator_marks_existing_agenda_event_as_retreat(self):
        make_user("coordenador", Role.EVENTS_COMMISSION)
        event = publish_retreat(title="Acampamento", slug="acampamento", is_retreat=False, capacity=None)
        self.client.login(username="coordenador", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:event_operation_create"),
            {
                "public_event": event.pk,
                "is_retreat": "on",
                "capacity": "12",
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        event.refresh_from_db()
        self.assertTrue(event.is_retreat)
        self.assertTrue(event.requires_registration)
        self.assertEqual(event.capacity, 12)
        public = self.client.get(event.url)
        self.assertContains(public, "Inscrição individual ou familiar")
