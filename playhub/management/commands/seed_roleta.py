from decimal import Decimal

from django.core.management.base import BaseCommand

from playhub.roulette.models import RoletaMesa


class Command(BaseCommand):
    help = "Cria ou atualiza a mesa padrão Roleta Brasil."

    def handle(self, *args, **options):
        mesa, created = RoletaMesa.objects.update_or_create(
            slug="roleta-brasil",
            defaults={
                "nome": "Roleta Brasil",
                "variante": "european",
                "saldo_inicial": Decimal("1000.00"),
                "aposta_minima": Decimal("1.00"),
                "aposta_maxima": Decimal("500.00"),
                "max_apostas_por_giro": 12,
                "ativa": True,
            },
        )
        verb = "criada" if created else "atualizada"
        self.stdout.write(self.style.SUCCESS(f"Mesa {mesa.slug} {verb}."))
