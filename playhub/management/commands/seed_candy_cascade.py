from decimal import Decimal

from django.core.management.base import BaseCommand

from playhub.candy_cascade.config import DEFAULT_SLUG, DISPLAY_NAME
from playhub.candy_cascade.models import CandyCascadeJogo


class Command(BaseCommand):
    help = "Cria ou atualiza o jogo Candy Cascade (card Sweet Bonanza)."

    def handle(self, *args, **options):
        jogo, created = CandyCascadeJogo.objects.update_or_create(
            slug=DEFAULT_SLUG,
            defaults={
                "nome": DISPLAY_NAME,
                "rtp_label": "96.0%",
                "saldo_inicial": Decimal("1000.00"),
                "aposta_minima": Decimal("0.20"),
                "aposta_maxima": Decimal("20.00"),
                "ativo": True,
            },
        )
        verb = "criado" if created else "atualizado"
        self.stdout.write(self.style.SUCCESS(f"Jogo {jogo.slug} ({jogo.nome}) {verb}."))