"""Sincroniza o acervo da home com o Instagram da igreja."""

from django.core.management.base import BaseCommand

from apps.public.instagram import sync


class Command(BaseCommand):
    help = (
        "Busca as mídias recentes pela API oficial e guarda as imagens localmente. "
        "Falha de rede não é erro fatal: a home continua servindo a galeria curada."
    )

    def handle(self, *args, **options):
        summary = sync()

        if summary["error"]:
            self.stderr.write(self.style.WARNING(f"Sincronização não concluída: {summary['error']}"))

        self.stdout.write(
            "Quadros novos: {created} | atualizados: {updated} | ignorados: {skipped}".format(**summary)
        )
