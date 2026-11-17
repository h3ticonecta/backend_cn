"""Sincroniza percentuais casa/usuário entre Game (catálogo) e backends jogáveis."""

from __future__ import annotations

from django.db.models import Q

from playhub.models import Game


def _roleta_games_qs(mesa_slug: str):
    return Game.objects.filter(play_kind=Game.PlayKind.ROLETA).filter(
        Q(play_mesa_slug=mesa_slug) | (Q(play_mesa_slug="") & Q(slug=mesa_slug))
    )


def _slot_games_qs(slot_slug: str):
    return Game.objects.filter(play_kind=Game.PlayKind.SLOT).filter(
        Q(play_mesa_slug=slot_slug) | (Q(play_mesa_slug="") & Q(slug=slot_slug))
    )


def playable_slug(game: Game) -> str | None:
    if game.play_kind not in (Game.PlayKind.ROLETA, Game.PlayKind.SLOT):
        return None
    slug = (game.play_mesa_slug or game.slug).strip()
    return slug or None


def sync_from_game(game: Game) -> dict[str, int]:
    """Propaga chances do catálogo para RoletaMesa / slots vinculados pelo slug."""
    slug = playable_slug(game)
    if not slug:
        return {"roleta": 0, "fortune_gems": 0, "wolf_gold": 0, "candy_cascade": 0, "games": 0}

    casa = game.percentual_casa
    usuario = game.percentual_usuario
    counts = {"roleta": 0, "fortune_gems": 0, "wolf_gold": 0, "candy_cascade": 0, "games": 0}

    if game.play_kind == Game.PlayKind.ROLETA:
        from playhub.roulette.models import RoletaMesa

        counts["roleta"] = RoletaMesa.objects.filter(slug=slug).update(
            percentual_casa=casa,
            percentual_usuario=usuario,
        )

    if game.play_kind == Game.PlayKind.SLOT:
        from playhub.candy_cascade.models import CandyCascadeJogo
        from playhub.fortune_gems.models import FortuneGemsJogo
        from playhub.wolf_gold.models import WolfGoldJogo

        counts["fortune_gems"] = FortuneGemsJogo.objects.filter(slug=slug).update(
            percentual_casa=casa,
            percentual_usuario=usuario,
        )
        counts["wolf_gold"] = WolfGoldJogo.objects.filter(slug=slug).update(
            percentual_casa=casa,
            percentual_usuario=usuario,
        )
        counts["candy_cascade"] = CandyCascadeJogo.objects.filter(slug=slug).update(
            percentual_casa=casa,
            percentual_usuario=usuario,
        )

    return counts


def sync_from_roleta_mesa(mesa) -> int:
    """Atualiza jogos do catálogo ligados a esta mesa."""
    return _roleta_games_qs(mesa.slug).update(
        percentual_casa=mesa.percentual_casa,
        percentual_usuario=mesa.percentual_usuario,
    )


def sync_from_fortune_gems_jogo(jogo) -> int:
    return _slot_games_qs(jogo.slug).update(
        percentual_casa=jogo.percentual_casa,
        percentual_usuario=jogo.percentual_usuario,
    )


def sync_from_wolf_gold_jogo(jogo) -> int:
    return _slot_games_qs(jogo.slug).update(
        percentual_casa=jogo.percentual_casa,
        percentual_usuario=jogo.percentual_usuario,
    )


def sync_from_candy_cascade_jogo(jogo) -> int:
    return _slot_games_qs(jogo.slug).update(
        percentual_casa=jogo.percentual_casa,
        percentual_usuario=jogo.percentual_usuario,
    )


def connect_chance_sync_signals() -> None:
    from django.db.models.signals import post_save

    from playhub.candy_cascade.models import CandyCascadeJogo
    from playhub.fortune_gems.models import FortuneGemsJogo
    from playhub.roulette.models import RoletaMesa
    from playhub.wolf_gold.models import WolfGoldJogo

    def on_game_saved(sender, instance: Game, **kwargs):
        sync_from_game(instance)

    def on_roleta_mesa_saved(sender, instance: RoletaMesa, **kwargs):
        sync_from_roleta_mesa(instance)

    def on_fortune_gems_saved(sender, instance: FortuneGemsJogo, **kwargs):
        sync_from_fortune_gems_jogo(instance)

    def on_wolf_gold_saved(sender, instance: WolfGoldJogo, **kwargs):
        sync_from_wolf_gold_jogo(instance)

    def on_candy_cascade_saved(sender, instance: CandyCascadeJogo, **kwargs):
        sync_from_candy_cascade_jogo(instance)

    uid = "playhub_chance_sync"
    post_save.connect(on_game_saved, sender=Game, dispatch_uid=f"{uid}_game")
    post_save.connect(
        on_roleta_mesa_saved, sender=RoletaMesa, dispatch_uid=f"{uid}_roleta"
    )
    post_save.connect(
        on_fortune_gems_saved, sender=FortuneGemsJogo, dispatch_uid=f"{uid}_fg"
    )
    post_save.connect(
        on_wolf_gold_saved, sender=WolfGoldJogo, dispatch_uid=f"{uid}_wg"
    )
    post_save.connect(
        on_candy_cascade_saved, sender=CandyCascadeJogo, dispatch_uid=f"{uid}_cc"
    )