from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.public.demo import DEMO_PASSWORD, seed_demo


class Command(BaseCommand):
    help = (
        "Popula o ambiente local com conteúdo de demonstração para revisar o visual "
        "do portal. Não use em produção: horários, endereço, PIX e textos não são da igreja."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Sobrescreve conteúdos de demonstração já existentes.",
        )
        parser.add_argument(
            "--allow-on-production",
            action="store_true",
            help="Permite rodar mesmo com DEBUG=False. Use só se tiver certeza.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["allow_on_production"]:
            raise CommandError(
                "Recusado: seed_demo exige DEBUG=True "
                "(use --allow-on-production se tiver certeza)."
            )

        stats = seed_demo(force=options["force"])
        self.stdout.write(self.style.SUCCESS("Conteúdo de demonstração pronto."))
        for key, value in stats.items():
            self.stdout.write(f"  {key}: {value}")
        self.stdout.write("")
        self.stdout.write("Contas de preview (senha compartilhada):")
        self.stdout.write(
            "  membro, joao, maria, carla, lider, comunicacao, pastor, tesouraria, comissao"
        )
        self.stdout.write(f"  senha: {DEMO_PASSWORD}")
        self.stdout.write(
            "PIX e WhatsApp deste seed são fictícios — não envie dinheiro nem mensagens."
        )
