from django.core.management.base import BaseCommand

from playhub.game_chance_sync import (
    sync_from_fortune_gems_jogo,
    sync_from_game,
    sync_from_roleta_mesa,
    sync_from_wolf_gold_jogo,
)
from playhub.fortune_gems.models import FortuneGemsJogo
from playhub.models import Game
from playhub.roulette.models import RoletaMesa
from playhub.wolf_gold.models import WolfGoldJogo


class Command(BaseCommand):
    help = "Alinha percentuais casa/usuário entre catálogo (Game) e backends jogáveis."

    def add_arguments(self, parser):
        parser.add_argument(
            "--from-catalog",
            action="store_true",
            help="Propaga Game → mesa/slot (padrão).",
        )
        parser.add_argument(
            "--from-backend",
            action="store_true",
            help="Propaga mesa/slot → Game.",
        )

    def handle(self, *args, **options):
        from_backend = options["from_backend"]
        from_catalog = options["from_catalog"] or not from_backend

        if from_catalog:
            n = 0
            for game in Game.objects.filter(
                play_kind__in=[Game.PlayKind.ROLETA, Game.PlayKind.SLOT]
            ):
                sync_from_game(game)
                n += 1
            self.stdout.write(self.style.SUCCESS(f"Catálogo → backend: {n} jogos processados."))

        if from_backend:
            r = sum(sync_from_roleta_mesa(m) for m in RoletaMesa.objects.all())
            f = sum(sync_from_fortune_gems_jogo(j) for j in FortuneGemsJogo.objects.all())
            w = sum(sync_from_wolf_gold_jogo(j) for j in WolfGoldJogo.objects.all())
            self.stdout.write(
                self.style.SUCCESS(
                    f"Backend → catálogo: mesas={r}, fortune_gems={f}, wolf_gold={w} registros."
                )
            )