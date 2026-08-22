from django.core.management.base import BaseCommand

from apps.public.retreats import discard_due_retreat_sensitive_data


class Command(BaseCommand):
    help = "Descarta dados médicos e de menores após o prazo do retiro."

    def handle(self, *args, **options):
        discarded = discard_due_retreat_sensitive_data()
        self.stdout.write(f"{discarded} inscrição(ões) com dados sensíveis descartados.")
