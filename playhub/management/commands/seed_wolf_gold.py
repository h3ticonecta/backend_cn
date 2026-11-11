from decimal import Decimal

from django.core.management.base import BaseCommand

from playhub.wolf_gold.models import WolfGoldJogo


class Command(BaseCommand):
    help = "Cria ou atualiza o slot demo Wolf Gold."

    def handle(self, *args, **options):
        jogo, created = WolfGoldJogo.objects.update_or_create(
            slug="wolf-gold",
            defaults={
                "nome": "Wolf Gold",
                "rtp_label": "96.0%",
                "saldo_inicial": Decimal("10000.00"),
                "aposta_minima": Decimal("0.25"),
                "aposta_maxima": Decimal("125.00"),
                "ativo": True,
            },
        )
        verb = "Criado" if created else "Atualizado"
        self.stdout.write(self.style.SUCCESS(f"{verb}: {jogo.nome}"))
