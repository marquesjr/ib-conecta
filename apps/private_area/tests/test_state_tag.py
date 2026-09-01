"""O selo de estado da área privada."""

from django.template import Context, Template
from django.test import TestCase

from apps.private_area.models import (
    AssignmentStatus,
    BudgetLineStatus,
    SongStatus,
)
from apps.private_area.templatetags.state_tags import TONES
from apps.public.models import EventRegistration


def render(key, label=""):
    template = Template("{% load state_tags %}{% state key label %}")
    return template.render(Context({"key": key, "label": label}))


class StateSealTests(TestCase):
    def test_pending_is_open_and_carries_an_empty_mark(self):
        html = render("pending", "Pendente")
        self.assertIn("state--open", html)
        self.assertIn("state-mark", html)
        self.assertIn("Pendente", html)

    def test_confirmed_is_settled(self):
        self.assertIn("state--settled", render("confirmed", "Confirmado"))

    def test_declined_is_closed(self):
        self.assertIn("state--closed", render("declined", "Recusado"))

    def test_unknown_status_falls_back_to_open(self):
        """Estado imprevisto é o que a liderança precisa notar, não esconder."""
        self.assertIn("state--open", render("teleported", "Teletransportado"))

    def test_the_mark_is_hidden_from_screen_readers(self):
        """A marca é forma, não conteúdo: quem ouve recebe o rótulo e o significado."""
        html = render("pending", "Pendente")
        self.assertIn('aria-hidden="true"', html)
        self.assertIn("aguardando", html)

    def test_the_label_falls_back_to_the_key(self):
        self.assertIn("pending", render("pending"))

    def test_every_status_in_the_codebase_has_an_explicit_tone(self):
        """Um status novo sem tom cairia em ``open`` calado; este teste obriga a decisão."""
        known = (
            set(AssignmentStatus.values)
            | set(BudgetLineStatus.values)
            | set(SongStatus.values)
            | set(EventRegistration.Status.values)
            | set(EventRegistration.PixStatus.values)
        )
        missing = sorted(status for status in known if status not in TONES)
        self.assertEqual(missing, [], f"Status sem tom declarado: {missing}")

    def test_the_three_tones_are_visually_distinct_classes(self):
        tones = {render(key).split("state--")[1].split('"')[0] for key in TONES}
        self.assertEqual(tones, {"open", "settled", "closed"})
