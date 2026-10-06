from datetime import datetime, time

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from apps.public.models import EventIndexPage, EventPage, RecurringEvent


def local(*args):
    return timezone.make_aware(datetime(*args))


class RecurringEventOccurrenceTests(TestCase):
    def setUp(self):
        self.ebd = RecurringEvent.objects.get(title="Escola Bíblica Dominical")

    def test_migration_seeds_sunday_events(self):
        culto = RecurringEvent.objects.get(title="Culto de Adoração ao Senhor")
        self.assertEqual(self.ebd.weekday, RecurringEvent.Weekday.SUNDAY)
        self.assertEqual(self.ebd.starts_at, time(9, 0))
        self.assertEqual(culto.weekday, RecurringEvent.Weekday.SUNDAY)
        self.assertEqual(culto.starts_at, time(19, 0))

    def test_next_occurrence_is_the_coming_sunday(self):
        # 2026-10-07 é uma quarta-feira.
        self.assertEqual(self.ebd.next_occurrence(local(2026, 10, 7, 12)), local(2026, 10, 11, 9))

    def test_same_day_counts_until_it_starts(self):
        self.assertEqual(self.ebd.next_occurrence(local(2026, 10, 11, 8, 30)), local(2026, 10, 11, 9))
        self.assertEqual(self.ebd.next_occurrence(local(2026, 10, 11, 9, 1)), local(2026, 10, 18, 9))

    def test_repeats_label(self):
        self.assertEqual(self.ebd.repeats_label, "Todo domingo")
        self.ebd.weekday = RecurringEvent.Weekday.WEDNESDAY
        self.assertEqual(self.ebd.repeats_label, "Toda quarta")


class RecurringEventAgendaTests(TestCase):
    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page
        self.index = EventIndexPage(title="Agenda", slug="agenda", intro="")
        root.add_child(instance=self.index)
        self.index.save_revision().publish()

    def test_agenda_lists_weekly_events(self):
        response = self.client.get("/agenda/")
        self.assertContains(response, "Escola Bíblica Dominical")
        self.assertContains(response, "Culto de Adoração ao Senhor")
        self.assertContains(response, "Todo domingo", count=2)
        self.assertNotContains(response, "Nenhum evento publicado no momento.")

    def test_inactive_weekly_event_is_hidden(self):
        RecurringEvent.objects.filter(title="Escola Bíblica Dominical").update(is_active=False)
        response = self.client.get("/agenda/")
        self.assertNotContains(response, "Escola Bíblica Dominical")
        self.assertContains(response, "Culto de Adoração ao Senhor")

    def test_dated_page_at_same_time_replaces_weekly_entry(self):
        culto = RecurringEvent.objects.get(title="Culto de Adoração ao Senhor")
        special = EventPage(
            title="Culto de aniversário da igreja",
            slug="aniversario",
            starts_at=culto.next_occurrence(),
        )
        self.index.add_child(instance=special)
        special.save_revision().publish()

        response = self.client.get("/agenda/")
        self.assertContains(response, "Culto de aniversário da igreja")
        self.assertNotContains(response, "Culto de Adoração ao Senhor")

    def test_home_shows_weekly_events_linking_to_agenda(self):
        response = self.client.get("/")
        self.assertContains(response, "Escola Bíblica Dominical")
        self.assertContains(response, "Todo domingo · 9h")
        self.assertContains(response, "Todo domingo · 19h")
