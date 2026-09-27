"""Sincroniza o acervo da home com o Instagram da igreja."""

from django.core.management.base import BaseCommand

from apps.public.instagram import sync


class Command(BaseCommand):
    help = (
        "Busca as mídias recentes pela API oficial e guarda as imagens localmente. "
        "Falha de rede não é erro fatal: a home continua servindo a galeria curada."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            dest="limit",
            type=int,
            default=None,
            help="Quantas mídias recentes buscar (padrão: até 100, conforme a configuração da home).",
        )

    def handle(self, *args, **options):
        summary = sync(limit=options["limit"])

        if summary["error"]:
            self.stderr.write(self.style.WARNING(f"Sincronização não concluída: {summary['error']}"))

        self.stdout.write(
            "Quadros novos: {created} | atualizados: {updated} | ignorados: {skipped}".format(**summary)
        )
