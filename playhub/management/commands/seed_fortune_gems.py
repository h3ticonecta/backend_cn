from decimal import Decimal

from django.core.management.base import BaseCommand

from playhub.fortune_gems.models import FortuneGemsJogo


class Command(BaseCommand):
    help = "Cria ou atualiza a config demo do slot Fortune Gems."

    def handle(self, *args, **options):
        jogo, created = FortuneGemsJogo.objects.update_or_create(
            slug="fortune-gems",
            defaults={
                "nome": "Fortune Gems",
                "rtp_label": "96.5%",
                "saldo_inicial": Decimal("25450.00"),
                "aposta_minima": Decimal("10.00"),
                "aposta_maxima": Decimal("1000.00"),
                "jackpot_exibicao": Decimal("1489200.50"),
                "ativo": True,
            },
        )
        verb = "Criado" if created else "Atualizado"
        self.stdout.write(self.style.SUCCESS(f"{verb}: {jogo.nome} ({jogo.slug})"))
